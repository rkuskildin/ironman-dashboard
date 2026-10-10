"""Восстановление и нагрузка дня по образцу WHOOP.

Восстановление (0–100 %) — утром, по ночи относительно личной нормы за 30 дней:
  HRV (главный вес), пульс покоя, сон против потребности, поздний отбой.
Нагрузка дня (0–21, логарифмическая) — из поминутного пульса Fitbit за весь день:
  TRIMP по Банистеру на резерве пульса, только минуты с заметной активностью.
Оптимальная нагрузка на день зависит от восстановления; остаток переводится в минуты Z2 / Z4.
"""
import json
import math
from datetime import date, datetime, timedelta
from statistics import mean, pstdev

from . import config, db, service, thresholds

SCHEMA = "CREATE TABLE IF NOT EXISTS hr_minutes (date TEXT, source TEXT, data TEXT, complete INTEGER, PRIMARY KEY (date, source));"

# Шкала нагрузки: strain = 21 · ln(1 + TRIMP/A) / ln(1 + TMAX/A)
A, TMAX = 15.0, 700.0
ACTIVE_HRR = 0.25          # ниже 25 % резерва пульса — обычная жизнь, в нагрузку не идёт
SLEEP_NEED_BASE = 8.0      # базовая потребность во сне, ч


def init():
    with db.session() as c:
        c.execute(SCHEMA)


# ---------------- поминутный пульс ----------------
def store_day(day: str, minutes: list, source: str, complete: bool):
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO hr_minutes VALUES (?,?,?,?)", (day, source, json.dumps(minutes), int(complete)))


def day_minutes(day: str) -> list | None:
    """Пульс по минутам: Fitbit основной, пропуски заполняются пульсом часов Garmin."""
    with db.session() as c:
        rows = {r["source"]: json.loads(r["data"]) for r in c.execute("SELECT source, data FROM hr_minutes WHERE date=?", (day,))}
    fb, gm = rows.get("fitbit"), rows.get("garmin")
    if not fb and not gm:
        return None
    if not fb:
        return gm
    if not gm:
        return fb
    return [f if f else g for f, g in zip(fb, gm)]


def garmin_day_minutes(g, day: str) -> list:
    """Пульс часов Garmin за день (замер раз в ~2 мин) → по минутам."""
    hr = g.get_heart_rates(day) or {}
    out = [None] * 1440
    for ts, bpm in hr.get("heartRateValues") or []:
        if not bpm:
            continue
        t = datetime.utcfromtimestamp(ts / 1000) + timedelta(hours=config.BEDTIME_TZ)
        if t.date().isoformat() != day:
            continue
        i = t.hour * 60 + t.minute
        out[i] = bpm
        if i + 1 < 1440 and out[i + 1] is None:  # Garmin пишет раз в 2 минуты — заполняем соседнюю
            out[i + 1] = bpm
    return out


def days_needing_fetch(days: int) -> list[str]:
    today = date.today()
    with db.session() as c:
        have = {r["date"]: r["complete"] for r in c.execute("SELECT date, complete FROM hr_minutes WHERE source='fitbit'")}
    out = []
    for i in range(days, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        if not have.get(d):
            out.append(d)
    return out


# ---------------- нагрузка ----------------
def _hr_params() -> tuple[float, float]:
    t = thresholds.get()
    rest = None
    h = service.health(10)
    vals = [(x.get(config.RECOVERY_SOURCE) or {}).get("resting_hr") for x in h]
    vals = [v for v in vals if v]
    rest = mean(vals[-7:]) if vals else t["rest_hr"]
    return float(rest), float(t["max_hr"])


def _trimp_minute(hr: float, rest: float, mx: float) -> float:
    hrr = (hr - rest) / (mx - rest)
    if hrr < ACTIVE_HRR:
        return 0.0
    return hrr * 0.64 * math.exp(1.92 * hrr)


def strain_from_trimp(trimp: float) -> float:
    return round(min(21.0, 21 * math.log1p(trimp / A) / math.log1p(TMAX / A)), 1)


def trimp_for_strain(strain: float) -> float:
    return A * (math.exp(strain * math.log1p(TMAX / A) / 21) - 1)


def day_strain(day: str) -> dict | None:
    m = day_minutes(day)
    if not m:
        return None
    rest, mx = _hr_params()
    trimp, cum, zones = 0.0, [], [0] * 5
    zr = thresholds.get()["zones_run"]
    for hr in m:
        if hr:
            trimp += _trimp_minute(hr, rest, mx)
            if (hr - rest) / (mx - rest) >= ACTIVE_HRR:
                zones[thresholds.zone_of(hr, zr)] += 1
        cum.append(round(strain_from_trimp(trimp), 2))
    return {"trimp": round(trimp, 1), "strain": strain_from_trimp(trimp), "cumulative": cum,
            "active_zone_min": zones, "rest": rest, "max": mx}


# ---------------- восстановление ----------------
def _z(v, hist):
    if v is None or len(hist) < 5:
        return None
    sd = pstdev(hist) or 1e-6
    return (v - mean(hist)) / sd


def recovery(day: str | None = None) -> dict:
    day = day or date.today().isoformat()
    rs = config.RECOVERY_SOURCE
    hist = service.health(45)
    by = {h["date"]: (h.get(rs) or {}) for h in hist}
    cur = by.get(day) or {}
    prev = [by[d] for d in sorted(by) if d < day][-30:]

    hrv_hist = [math.log(x["hrv"]) for x in prev if x.get("hrv")]
    rhr_hist = [x["resting_hr"] for x in prev if x.get("resting_hr")]
    hz = _z(math.log(cur["hrv"]) if cur.get("hrv") else None, hrv_hist)
    rz = _z(cur.get("resting_hr"), rhr_hist)

    # потребность во сне: база + добавка за вчерашнюю нагрузку
    y = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
    ys = day_strain(y)
    need = SLEEP_NEED_BASE + max(0.0, ((ys or {}).get("strain") or 0) - 10) * 0.12
    sleep_h = (cur.get("sleep_s") or 0) / 3600
    sleep_perf = min(1.0, sleep_h / need) if sleep_h else None

    reg = service.regime(3)
    night = next((n for n in reg["nights"] if n["wake_date"] == day), None)

    parts, weights = [], []
    if hz is not None:
        parts.append(max(0, min(100, 58 + 22 * hz))); weights.append(0.55)
    if rz is not None:
        parts.append(max(0, min(100, 58 - 20 * rz))); weights.append(0.20)
    if sleep_perf is not None:
        parts.append(max(0, min(100, (sleep_perf - 0.55) / 0.45 * 100))); weights.append(0.25)
    score = None
    if parts:
        score = sum(p * w for p, w in zip(parts, weights)) / sum(weights)
        if night and not night["on_time"]:
            score -= min(8, night["late_min"] / 20)   # поздний отбой: до −8 пунктов
        score = round(max(1, min(99, score)))
    zone = None if score is None else "green" if score >= 67 else "yellow" if score >= 34 else "red"
    return {
        "date": day, "score": zone and score, "zone": zone,
        "baseline_days": len(hrv_hist),
        "hrv": cur.get("hrv"), "hrv_base": round(math.exp(mean(hrv_hist)), 1) if hrv_hist else None, "hrv_z": hz and round(hz, 2),
        "rhr": cur.get("resting_hr"), "rhr_base": round(mean(rhr_hist), 1) if rhr_hist else None, "rhr_z": rz and round(rz, 2),
        "sleep_h": round(sleep_h, 1) if sleep_h else None, "sleep_need": round(need, 1),
        "sleep_perf": sleep_perf and round(sleep_perf * 100),
        "bed_time": night and night["bed_time"], "late_min": night and night["late_min"],
        "yesterday_strain": ys and ys["strain"],
    }


# ---------------- оптимальная нагрузка и остаток ----------------
def target_band(score: int | None) -> tuple[float, float]:
    if score is None:
        return 10.0, 14.0
    center = 6 + score * 0.12                     # 1 % → 6, 50 % → 12, 99 % → 18
    return round(max(4, center - 2), 1), round(min(20, center + 2), 1)


def today() -> dict:
    d = date.today().isoformat()
    rec = recovery(d)
    st = day_strain(d) or {"trimp": 0, "strain": 0.0, "cumulative": [], "active_zone_min": [0] * 5, "rest": None, "max": None}
    lo, hi = target_band(rec["score"])
    rest, mx = _hr_params()

    def minutes_at(hrr: float, strain_goal: float) -> int:
        need = trimp_for_strain(strain_goal) - st["trimp"]
        per = hrr * 0.64 * math.exp(1.92 * hrr)
        return max(0, round(need / per))

    t = thresholds.get()
    z2_hr = (t["zones_run"][1] + t["zones_run"][2]) / 2
    z4_hr = (t["zones_run"][3] + t["zones_run"][4]) / 2
    z2, z4 = (z2_hr - rest) / (mx - rest), (z4_hr - rest) / (mx - rest)
    remaining = round(max(0.0, (lo + hi) / 2 - st["strain"]), 1)

    # нагрузка запланированной тренировки: для спокойных тренировок TRIMP ≈ TSS
    o = service.calendar(d, d)[0]["items"]
    planned = [i for i in o if i.get("planned") and i["sport"] != "rest" and not i.get("actual")]
    p_tss = sum((i["planned"].get("tss") or 0) for i in planned)
    planned_strain = strain_from_trimp(st["trimp"] + 1.0 * p_tss) if p_tss else None

    m = day_minutes(d) or []
    last_min = max((i for i, v in enumerate(m) if v), default=None)
    now = datetime.now()
    now_min = now.hour * 60 + now.minute
    stale_min = now_min - last_min if last_min is not None else now_min
    return {
        "date": d, "recovery": rec, "strain": st["strain"], "trimp": st["trimp"],
        "target": [lo, hi], "remaining": remaining,
        "remaining_z2_min": minutes_at(max(z2, 0.3), (lo + hi) / 2),
        "remaining_z4_min": minutes_at(max(z4, 0.5), (lo + hi) / 2),
        "planned": [{"title": i["planned"].get("title"), "sport": i["sport"], "tss": i["planned"].get("tss")} for i in planned],
        "planned_strain": planned_strain,
        "over_plan": planned_strain is not None and planned_strain > hi + 1,
        "hr_updated": f"{last_min // 60:02d}:{last_min % 60:02d}" if last_min is not None else None,
        "hr_stale_min": stale_min, "now_min": now_min,
        "curve": {"hr": m, "strain": st["cumulative"]}, "active_zone_min": st["active_zone_min"],
        "z2_hr": round(z2_hr), "z4_hr": round(z4_hr), "z2_floor": t["zones_run"][1], "z4_floor": t["zones_run"][3],
    }


def history(days: int = 30) -> list[dict]:
    out = []
    for i in range(days, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        r = recovery(d)
        s = day_strain(d)
        out.append({"date": d, "recovery": r["score"], "zone": r["zone"], "strain": s and s["strain"]})
    return out
