"""Цели на Ironman и витрины по дисциплинам: текущие показатели против цели."""
import json
from collections import defaultdict
from datetime import date, timedelta

from . import db, service

RACE = {"swim": 3800, "bike": 180000, "run": 42195}

# Раскладка на 10:00 (секунды). Плавание — темп 2:00/100 м, как в примере спортсмена.
DEFAULT_GOALS = {"swim": 4560, "t1": 360, "bike": 18900, "t2": 180, "run": 12000}

# Отсечка «мусорных» записей: слишком короткие или со странным темпом
MIN_DIST = {"swim": 400, "bike": 5000, "run": 1500}
PACE_OK = {  # сек на единицу: swim — на 100 м, run — на км, bike — на км (для фильтра)
    "swim": (60, 240), "run": (180, 600), "bike": (60, 300),
}
# Для прогноза — только содержательные сессии; коэффициент усталости Ригеля по видам
PROJ_MIN_DIST = {"swim": 400, "bike": 15000, "run": 3000}
RIEGEL_K = {"swim": 1.06, "bike": 1.03, "run": 1.06}

# Ключевые тренировки перед стартом: самая длинная сессия должна дорасти до этих объёмов
LONG_TARGET = {"swim": 4000, "bike": 160000, "run": 30000}
# Пиковый недельный объём базовой подготовки к Ironman (ориентир)
WEEK_TARGET = {"swim": 10000, "bike": 250000, "run": 50000}
# В Ironman марафон после 180 км медленнее «свежего» примерно на 10–15 %
IM_RUN_FADE = 1.12


def _settings_get(key: str, default):
    with db.session() as c:
        c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


def get_goals() -> dict:
    return {**DEFAULT_GOALS, **_settings_get("goals", {})}


def set_goals(g: dict) -> dict:
    clean = {k: int(g[k]) for k in DEFAULT_GOALS if k in g and 0 < int(g[k]) < 86400}
    with db.session() as c:
        c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('goals', ?)", (json.dumps(clean),))
    return get_goals()


def unit(sport: str) -> float:
    return 100 if sport == "swim" else 1000


def _moving(a: dict) -> float:
    return a.get("moving_s") or a.get("duration_s") or 0


def sessions(sport: str, days: int = 365) -> list[dict]:
    """Сессии вида спорта с темпом по чистому времени движения, без мусора."""
    start = (date.today() - timedelta(days=days)).isoformat()
    from .extras import excluded_set
    excl = excluded_set()
    out = []
    for a in service.activities(start, date.today().isoformat()):
        if (a["source"], a["source_id"]) in excl:
            continue
        if a["sport"] != sport or not a.get("distance_m") or a["distance_m"] < MIN_DIST[sport]:
            continue
        mv = _moving(a)
        if not mv:
            continue
        pace = mv / (a["distance_m"] / unit(sport))
        lo, hi = PACE_OK[sport]
        if not lo <= pace <= hi:
            continue
        out.append({"date": a["date"], "title": a.get("title"), "source": a["source"], "source_id": a["source_id"],
                    "has_gps": bool(a.get("has_gps")), "start_time": a.get("start_time"),
                    "distance_m": round(a["distance_m"]), "moving_s": round(mv), "pace": round(pace, 1),
                    "speed_kmh": round(a["distance_m"] / mv * 3.6, 1),
                    "avg_hr": a.get("avg_hr"), "avg_power": a.get("avg_power"), "np": a.get("np"),
                    "tss": a.get("tss")})
    out.sort(key=lambda s: s["date"])
    return out


def _riegel(t: float, d1: float, d2: float, k: float = 1.06) -> float:
    """Прогноз времени на дистанцию d2 по результату t на d1 (формула Ригеля)."""
    return t * (d2 / d1) ** k


def _project(sport: str, ss: list[dict], garmin_status: dict | None) -> dict:
    """Прогноз на дистанцию Ironman по лучшим недавним сессиям."""
    ss = [s for s in ss if s["distance_m"] >= PROJ_MIN_DIST[sport]]
    recent = [s for s in ss if s["date"] >= (date.today() - timedelta(days=120)).isoformat()]
    if sport == "run" and garmin_status and (garmin_status.get("race") or {}).get("timeMarathon"):
        m = garmin_status["race"]["timeMarathon"]
        return {"time": round(m * IM_RUN_FADE), "basis": f"прогноз Garmin на марафон {_hms(m)} × {IM_RUN_FADE} (усталость после вело)"}
    if len(recent) < 4:  # мало свежих данных — смотрим за год
        recent = ss
    if not recent:
        return {"time": None, "basis": "нет данных"}
    # верхняя четверть: что спортсмен показывает, когда реально тренируется. Не абсолютный рекорд
    # (там бывают ошибки — неверная длина бассейна, GPS) и не прогулки по городу
    k = RIEGEL_K[sport]
    proj = sorted(((_riegel(s["moving_s"], s["distance_m"], RACE[sport], k), s) for s in recent), key=lambda x: x[0])
    t, mid = proj[len(proj) // 4]
    if sport == "run":
        t *= IM_RUN_FADE
    rough = " · мало данных, оценка грубая" if len(recent) < 6 else ""
    return {"time": round(t), "basis": f"по лучшей четверти из {len(recent)} трен.: {mid['date']}, "
                                       f"{mid['distance_m'] / 1000:.1f} км за {_hms(mid['moving_s'])}{rough}"}


def _hms(s) -> str:
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def discipline(sport: str) -> dict:
    goals = get_goals()
    gs = service.garmin_status()
    ss = sessions(sport)
    today = date.today()
    d28 = (today - timedelta(days=28)).isoformat()
    d90 = (today - timedelta(days=90)).isoformat()
    last28 = [s for s in ss if s["date"] >= d28]
    last90 = [s for s in ss if s["date"] >= d90]

    target_time = goals[sport]
    target_pace = target_time / (RACE[sport] / unit(sport))
    proj = _project(sport, ss, gs)

    # недельные объёмы за 16 недель
    monday = today - timedelta(days=today.weekday())
    weeks = defaultdict(float)
    for s in ss:
        d = date.fromisoformat(s["date"])
        weeks[(d - timedelta(days=d.weekday())).isoformat()] += s["distance_m"]
    week_series = [{"week": (monday - timedelta(weeks=i)).isoformat(),
                    "distance_m": round(weeks.get((monday - timedelta(weeks=i)).isoformat(), 0))} for i in range(15, -1, -1)]

    def wavg(lst, key):
        tot = sum(s["distance_m"] for s in lst)
        return round(sum(s[key] * s["distance_m"] for s in lst) / tot, 1) if tot else None

    pace28 = wavg(last28, "pace") or wavg(last90, "pace")
    best = min((s["pace"] for s in last90), default=None)
    longest90 = max((s["distance_m"] for s in last90), default=0)
    longest_all = max((s["distance_m"] for s in ss), default=0)
    hr_vals = [s["avg_hr"] for s in last90 if s["avg_hr"]]
    out = {
        "sport": sport, "race_distance": RACE[sport],
        "goal": {"time": target_time, "pace": round(target_pace, 1),
                 "speed_kmh": round(RACE[sport] / target_time * 3.6, 1)},
        "current": {
            "pace_28": pace28, "pace_basis": "28 дней" if last28 else "90 дней",
            "best_pace_90": best,
            "speed_28": round(3600 / (pace28 * 1000 / unit(sport)) * 1, 1) if pace28 else None,
            "longest_90": longest90, "longest_all": longest_all,
            "sessions_28": len(last28), "distance_28": sum(s["distance_m"] for s in last28),
            "avg_week_28": round(sum(s["distance_m"] for s in last28) / 4),
            "avg_hr_90": round(sum(hr_vals) / len(hr_vals)) if hr_vals else None,
        },
        "projection": proj,
        "gap_s": proj["time"] - target_time if proj["time"] else None,
        "pace_gap_pct": round((pace28 / target_pace - 1) * 100) if pace28 else None,
        "milestones": {"long": {"target": LONG_TARGET[sport], "done": longest90},
                       "week": {"target": WEEK_TARGET[sport], "done": max((w["distance_m"] for w in week_series[-4:]), default=0)}},
        "weeks": week_series,
        "sessions": ss[-40:],
    }
    if sport == "run" and gs:
        out["garmin"] = {"vo2max": gs.get("vo2max"), "race": gs.get("race")}
    if sport == "bike":
        pw = [s for s in last90 if s.get("np") or s.get("avg_power")]
        out["current"]["power_90"] = round(sum((s["np"] or s["avg_power"]) for s in pw) / len(pw)) if pw else None
    return out


def summary() -> dict:
    goals = get_goals()
    rows = {s: discipline(s) for s in ("swim", "bike", "run")}
    proj_total = sum(r["projection"]["time"] or 0 for r in rows.values()) + goals["t1"] + goals["t2"]
    complete = all(r["projection"]["time"] for r in rows.values())
    races = _races()
    return {
        "goals": goals,
        "goal_total": sum(goals.values()),
        "projection_total": proj_total if complete else None,
        "disciplines": {s: {k: r[k] for k in ("goal", "current", "projection", "gap_s", "pace_gap_pct", "milestones")}
                        for s, r in rows.items()},
        "races": races,
    }


def _races() -> list[dict]:
    """Прошедшие старты: дни, когда в TP есть переходы (Transition) или мультиспорт в Garmin."""
    with db.session() as c:
        days = [r["date"] for r in c.execute(
            "SELECT DISTINCT date FROM activities WHERE lower(title) LIKE '%transition%' OR lower(title) LIKE '%multisport%' "
            "ORDER BY date DESC LIMIT 5")]
    out = []
    for d in days:
        legs = [a for a in service.activities(d, d) if a["sport"] in ("swim", "bike", "run")]
        if legs:
            out.append({"date": d, "legs": [{"sport": a["sport"], "distance_m": a["distance_m"],
                                             "time_s": _moving(a), "avg_hr": a["avg_hr"]} for a in legs]})
    return out
