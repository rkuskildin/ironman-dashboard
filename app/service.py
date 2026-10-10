"""Сведение данных из всех источников в единую картину для панели."""
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import mean

from . import config, db
from .metrics import estimate_duration, estimate_tss, fitness_series, match_plan


def _rows(sql, *args):
    with db.session() as c:
        return [dict(r) for r in c.execute(sql, args)]


def planned(start: str, end: str) -> list[dict]:
    rows = _rows("SELECT * FROM planned_workouts WHERE date BETWEEN ? AND ?", start, end)
    # Если работает веб-API TP, дубли из iCal не нужны
    if any(r["source"] == "tp" for r in rows):
        rows = [r for r in rows if r["source"] != "tp_ical"]
    # Тренер часто ставит только дистанцию — оцениваем время и TSS для итогов и прогноза
    for r in rows:
        if not r["duration_s"] and r["distance_m"]:
            r["duration_s"] = estimate_duration(r["sport"], r["distance_m"])
            r["duration_estimated"] = True
        if not r["tss"] and r["sport"] != "rest":
            r["tss"] = estimate_tss(r["sport"], r["duration_s"] if not r.get("duration_estimated") else None,
                                    distance_m=r["distance_m"])
            r["tss_estimated"] = True
    return rows


def _same_session(a: dict, b: dict) -> bool:
    """Одна и та же тренировка из двух источников. Дистанция надёжнее времени:
    Garmin считает общее время с паузами, TP — чистое (в бассейне разница бывает вдвое)."""
    if a["distance_m"] and b["distance_m"]:
        return abs(a["distance_m"] - b["distance_m"]) <= 0.05 * b["distance_m"] + 50
    return abs((a["duration_s"] or 0) - (b["duration_s"] or 0)) <= 0.15 * (b["duration_s"] or 1)


def _span(r):
    t = datetime.fromisoformat(r["start_gmt"])
    return t, t + timedelta(seconds=r["duration_s"] or 0)


def _overlaps_recorded(fb: dict, rows: list[dict]) -> bool:
    """Авто-тренировка Fitbit — дубль, если на то же время есть запись Garmin или добавленная вручную."""
    if not fb.get("start_gmt"):
        return False
    a0, a1 = _span(fb)
    for r in rows:
        if r["source"] in ("garmin", "manual") and r.get("start_gmt"):
            b0, b1 = _span(r)
            if (min(a1, b1) - max(a0, b0)).total_seconds() > 0.5 * min((a1 - a0).total_seconds(), (b1 - b0).total_seconds() or 1):
                return True
        if r["source"] == "tp" and r["date"] == fb["date"] and r["sport"] == fb["sport"] and fb["sport"] != "other":
            return True
    return False


def _attach_analysis(rows: list[dict]):
    """Разбор Garmin + изменение VO2 max относительно прошлой тренировки того же вида."""
    with db.session() as c:
        for r in rows:
            r["analysis"] = json.loads(r["analysis"]) if r.get("analysis") else None
            vo2 = (r["analysis"] or {}).get("vo2max")
            if vo2 and r.get("start_time"):
                prev = c.execute(
                    "SELECT analysis FROM activities WHERE source='garmin' AND sport=? AND start_time < ? "
                    "AND json_extract(analysis, '$.vo2max') IS NOT NULL ORDER BY start_time DESC LIMIT 1",
                    (r["sport"], r["start_time"])).fetchone()
                if prev:
                    r["analysis"]["vo2max_prev"] = json.loads(prev["analysis"])["vo2max"]


def garmin_status() -> dict | None:
    with db.session() as c:
        row = c.execute("SELECT date, data FROM garmin_status ORDER BY date DESC LIMIT 1").fetchone()
        week = c.execute("SELECT data FROM garmin_status WHERE date <= date(?, '-7 day') ORDER BY date DESC LIMIT 1",
                         (row["date"],)).fetchone() if row else None
    if not row:
        return None
    out = {"date": row["date"], **json.loads(row["data"])}
    if week:
        out["vo2max_week_ago"] = json.loads(week["data"]).get("vo2max")
    return out


def activities(start: str, end: str) -> list[dict]:
    """Garmin — первичный источник факта; из TP берём TSS и комментарии, дубли сливаем."""
    rows = _rows("SELECT * FROM activities WHERE date BETWEEN ? AND ? ORDER BY start_time", start, end)
    rows = [r for r in rows if r["source"] != "fitbit" or not _overlaps_recorded(r, rows)]
    primary = [r for r in rows if r["source"] != "tp"]
    for tp in (r for r in rows if r["source"] == "tp"):
        twin = next((p for p in primary if p["date"] == tp["date"] and p["sport"] == tp["sport"]
                     and _same_session(p, tp) and not p.get("_merged")), None)
        if twin:
            twin["_merged"] = True
            twin["tss"] = tp["tss"] or twin["tss"]
            twin["athlete_comments"] = tp["athlete_comments"] or twin["athlete_comments"]
        else:
            primary.append(tp)
    _attach_analysis(primary)
    from . import manual
    from .extras import excluded_set
    excl = excluded_set()
    for r in primary:
        r["excluded"] = (r["source"], r["source_id"]) in excl
    for r in primary:
        if r["source"] == "manual" and r.get("analysis"):  # пересчёт по текущим порогам
            r["tss"], r["analysis"]["hr_zones"] = manual.recompute(r["analysis"])
        r.pop("_merged", None)
        if r.get("fitbit_avg_hr"):  # пульс на тренировках — с Fitbit, Garmin оставляем для сравнения
            r["garmin_avg_hr"], r["garmin_max_hr"] = r["avg_hr"], r["max_hr"]
            r["avg_hr"], r["max_hr"], r["hr_source"] = r["fitbit_avg_hr"], r["fitbit_max_hr"], "fitbit"
        if not r["tss"]:
            r["tss"] = estimate_tss(r["sport"], r["duration_s"], r["avg_hr"], r["np"], r["distance_m"])
            r["tss_estimated"] = True
    return primary


def calendar(start: str, end: str) -> list[dict]:
    rows = match_plan(planned(start, end), activities(start, end))
    days = defaultdict(list)
    for r in rows:
        days[r["date"]].append(r)
    out, d, last = [], date.fromisoformat(start), date.fromisoformat(end)
    while d <= last:
        ds = d.isoformat()
        out.append({"date": ds, "items": days.get(ds, [])})
        d += timedelta(days=1)
    return out


def fitness(days: int = 180, forward: int = 21) -> list[dict]:
    today = date.today()
    start = today - timedelta(days=days)
    end = today + timedelta(days=forward)
    tp = {r["date"]: r for r in _rows("SELECT * FROM fitness_daily WHERE date BETWEEN ? AND ?",
                                      start.isoformat(), end.isoformat())}
    # Считаем с запасом в 120 дней, чтобы CTL успел «разогреться»
    warm = start - timedelta(days=365)
    daily = defaultdict(float)
    for a in activities(warm.isoformat(), today.isoformat()):
        daily[a["date"]] += a["tss"] or 0
    for p in planned((today + timedelta(days=1)).isoformat(), end.isoformat()):
        daily[p["date"]] += p["tss"] or 0
    series = [s for s in fitness_series(daily, warm, end) if s["date"] >= start.isoformat()]
    for s in series:
        s["future"] = s["date"] > today.isoformat()
        # для сравнения — CTL из TrainingPeaks (он не видит хоккей и тренировки вне TP)
        if s["date"] in tp and tp[s["date"]]["ctl"] is not None:
            s["tp_ctl"] = tp[s["date"]]["ctl"]
    return series


def volume(weeks: int = 16) -> list[dict]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    start = monday - timedelta(weeks=weeks - 1)
    end = monday + timedelta(days=6)
    out = {}
    for i in range(weeks):
        wk = (start + timedelta(weeks=i)).isoformat()
        out[wk] = {"week": wk, "plan": defaultdict(float), "actual": defaultdict(float),
                   "plan_tss": 0.0, "actual_tss": 0.0}

    def week_of(ds):
        d = date.fromisoformat(ds)
        return (d - timedelta(days=d.weekday())).isoformat()

    for p in planned(start.isoformat(), end.isoformat()):
        w = out[week_of(p["date"])]
        w["plan"][p["sport"]] += (p["duration_s"] or 0) / 3600
        w["plan_tss"] += p["tss"] or 0
    for a in activities(start.isoformat(), end.isoformat()):
        w = out[week_of(a["date"])]
        w["actual"][a["sport"]] += (a["duration_s"] or 0) / 3600
        w["actual_tss"] += a["tss"] or 0
    return [{**w, "plan": dict(w["plan"]), "actual": dict(w["actual"])} for w in out.values()]


def health(days: int = 60) -> list[dict]:
    start = (date.today() - timedelta(days=days)).isoformat()
    by_date = defaultdict(dict)
    for r in _rows("SELECT * FROM daily_health WHERE date >= ? ORDER BY date", start):
        by_date[r["date"]][r["source"]] = r
    return [{"date": d, **v} for d, v in sorted(by_date.items())]


def _baseline(series: list[dict], source: str, key: str, n: int = 28):
    vals = [d[source][key] for d in series[-n - 1:-1] if source in d and d[source].get(key)]
    return round(mean(vals), 1) if len(vals) >= 5 else None


def _bed_minutes(bed: str) -> int:
    """Минуты от 18:00 «вечера этой ночи»: 23:00 → 300, 00:30 → 390 (чтобы ночь не рвалась на полуночи)."""
    t = datetime.strptime(bed, "%Y-%m-%d %H:%M")
    m = t.hour * 60 + t.minute - 18 * 60
    return m + 24 * 60 if m < 0 else m


def regime(days: int = 30) -> dict:
    """Режим: время отбоя за каждую ночь против цели."""
    start = (date.today() - timedelta(days=days)).isoformat()
    target = _bed_minutes("2000-01-01 " + config.BEDTIME_TARGET)
    order = [config.RECOVERY_SOURCE] + [s for s in ("fitbit", "garmin") if s != config.RECOVERY_SOURCE]
    by_date: dict[str, dict] = {}
    for r in _rows("SELECT date, source, bed_time, wake_time, sleep_s FROM daily_health "
                   "WHERE date >= ? AND bed_time IS NOT NULL ORDER BY date", start):
        cur = by_date.get(r["date"])
        if cur is None or order.index(r["source"]) < order.index(cur["source"]):
            by_date[r["date"]] = r
    nights = []
    for d, r in sorted(by_date.items()):
        m = _bed_minutes(r["bed_time"])
        night_of = (date.fromisoformat(d) - timedelta(days=1)).isoformat()  # вечер, когда ложился
        nights.append({"night_of": night_of, "wake_date": d, "bed_time": r["bed_time"][11:], "wake_time": (r["wake_time"] or "")[11:],
                       "bed_min": m, "late_min": max(0, m - target), "on_time": m <= target,
                       "sleep_h": round((r["sleep_s"] or 0) / 3600, 1), "source": r["source"]})
    streak = 0
    for n in reversed(nights):
        if not n["on_time"]:
            break
        streak += 1
    last14 = nights[-14:]
    avg = round(sum(n["bed_min"] for n in last14) / len(last14)) if last14 else None
    return {
        "target": config.BEDTIME_TARGET, "target_min": target, "nights": nights,
        "streak": streak,
        "on_time_14": sum(n["on_time"] for n in last14), "count_14": len(last14),
        "avg_bed_14": _fmt_min(avg) if avg is not None else None,
        "avg_late_14": round(sum(n["late_min"] for n in last14) / len(last14)) if last14 else None,
        "last": nights[-1] if nights else None,
    }


def _fmt_min(m: int) -> str:
    t = (18 * 60 + m) % (24 * 60)
    return f"{t // 60:02d}:{t % 60:02d}"


def overview() -> dict:
    today = date.today()
    from .extras import race as _race
    rc = _race()
    race = date.fromisoformat(rc["date"])
    monday = today - timedelta(days=today.weekday())
    week = calendar(monday.isoformat(), (monday + timedelta(days=6)).isoformat())
    items = [i for d in week for i in d["items"]]
    done = [i for i in items if i["status"] in ("done", "partial", "off") and i["planned"]]
    due = [i for i in items if i["planned"] and i["sport"] != "rest" and i["date"] <= today.isoformat()]
    fit = fitness(60, 0)
    hl = health(35)
    latest = {}
    for src in ("garmin", "fitbit"):
        # по каждому показателю — последнее известное значение за 3 дня (сегодняшний сон/HRV приходят с задержкой)
        recent = [d[src] for d in hl[-3:] if src in d]
        if src != config.RECOVERY_SOURCE:
            # дневные показатели (Body Battery, шаги, стресс) — за последний полный день
            full = [d[src] for d in hl if src in d and d["date"] < today.isoformat()]
            recent = full[-1:]
        rec, night = {}, None
        for r in recent:
            rec.update({k: v for k, v in r.items() if v is not None})
            if r.get("sleep_s") or r.get("hrv"):
                night = r["date"]
        if night:
            rec["date"] = night  # дата — по последней записанной ночи, а не по пустому «сегодня»
        if any(rec.get(k) for k in ("hrv", "resting_hr", "sleep_s")):
            latest[src] = {**rec,
                           "hrv_baseline": _baseline(hl, src, "hrv"),
                           "rhr_baseline": _baseline(hl, src, "resting_hr")}

    alerts = []
    # Сон, HRV и пульс покоя — из Fitbit (основной источник восстановления), если он есть
    recovery_src = config.RECOVERY_SOURCE if config.RECOVERY_SOURCE in latest else next(iter(latest), None)
    for src, rec in latest.items():
        if src != recovery_src:
            continue
        if rec.get("hrv") and rec.get("hrv_baseline") and rec["hrv"] < rec["hrv_baseline"] * 0.85:
            alerts.append(f"HRV ({src}) на {round(100 - rec['hrv'] / rec['hrv_baseline'] * 100)}% ниже нормы — "
                          "возможно, стоит обсудить с тренером облегчение")
        if rec.get("resting_hr") and rec.get("rhr_baseline") and rec["resting_hr"] > rec["rhr_baseline"] + 5:
            alerts.append(f"Пульс покоя ({src}) выше нормы на {round(rec['resting_hr'] - rec['rhr_baseline'])} уд/мин")
        if rec.get("sleep_s") and rec["sleep_s"] < 6 * 3600:
            alerts.append(f"Мало сна ({src}): {rec['sleep_s'] / 3600:.1f} ч")
    reg = regime(30)
    if reg["last"] and not reg["last"]["on_time"]:
        lm = reg["last"]["late_min"]
        late = f"{lm // 60} ч {lm % 60} мин" if lm >= 60 else f"{lm} мин"
        alerts.append(f"Режим: лёг в {reg['last']['bed_time']} — на {late} позже {reg['target']}")
    if fit and fit[-1]["tsb"] < -30:
        alerts.append(f"Высокая усталость: TSB {fit[-1]['tsb']}")
    missed = [i for i in items if i["status"] == "missed"]
    if missed:
        alerts.append(f"Пропущено на этой неделе: {len(missed)}")

    with db.session() as c:
        last_sync = [dict(r) for r in c.execute(
            "SELECT source, ok, message, max(ts) ts FROM sync_log GROUP BY source")]
    return {
        "race": {"name": rc["name"], "date": rc["date"], "days_left": (race - today).days},
        "today": today.isoformat(),
        "today_items": next((d["items"] for d in week if d["date"] == today.isoformat()), []),
        "week": week,
        "week_stats": {
            "planned": len([i for i in items if i["planned"] and i["sport"] != "rest"]),
            "done": len(done),
            "compliance": round(100 * len(done) / len(due)) if due else None,
            "plan_hours": round(sum((i["planned"] or {}).get("duration_s") or 0 for i in items) / 3600, 1),
            "actual_hours": round(sum((i["actual"] or {}).get("duration_s") or 0 for i in items) / 3600, 1),
            "plan_tss": round(sum((i["planned"] or {}).get("tss") or 0 for i in items)),
            "actual_tss": round(sum((i["actual"] or {}).get("tss") or 0 for i in items)),
        },
        "form": fit[-1] if fit else None,
        "form_week_ago": fit[-8] if len(fit) >= 8 else None,
        "health": latest,
        "recovery_source": recovery_src,
        "garmin_status": garmin_status(),
        "regime": reg,
        "alerts": alerts,
        "last_sync": last_sync,
    }
