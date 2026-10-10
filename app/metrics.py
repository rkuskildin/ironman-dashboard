"""Расчёты: TSS, CTL/ATL/TSB, сопоставление плана и факта."""
import math
from datetime import date, timedelta

from . import config, thresholds

SPORTS = ("swim", "bike", "run", "strength", "hockey", "football", "other", "rest")

# workoutTypeValueId в TrainingPeaks
TP_SPORT = {1: "swim", 2: "bike", 3: "run", 4: "other", 7: "rest", 8: "bike", 9: "strength",
            10: "other", 11: "other", 12: "other", 13: "run", 100: "other"}


def normalize_sport(raw: str | None) -> str:
    s = (raw or "").lower()
    if any(k in s for k in ("swim", "плав", "pool", "open_water")):
        return "swim"
    if any(k in s for k in ("bike", "cycl", "ride", "вело", "biking", "virtual_ride", "mtb")):
        return "bike"
    if "hockey" in s or "хоккей" in s:
        return "hockey"
    if any(k in s for k in ("football", "soccer", "футбол")):
        return "football"
    if any(k in s for k in ("walk", "hik", "ходьб")):
        return "other"
    if any(k in s for k in ("run", "бег", "treadmill", "trail")):
        return "run"
    if any(k in s for k in ("strength", "силов", "gym", "yoga", "pilates")):
        return "strength"
    if any(k in s for k in ("day off", "rest", "отдых")):
        return "rest"
    return "other"


def estimate_duration(sport: str, distance_m: float | None) -> float | None:
    """Длительность плановой тренировки по дистанции — в спокойном (Z2) темпе."""
    if not distance_m:
        return None
    if sport == "run":
        return distance_m / 1000 * thresholds.get()["run_pace"] * 1.25
    if sport == "swim":
        return distance_m / 100 * thresholds.get()["swim_css"] * 1.15
    if sport == "bike":
        return distance_m / 1000 / 27 * 3600  # ~27 км/ч
    return None


def estimate_tss(sport: str, duration_s: float | None, avg_hr=None, np=None, distance_m=None) -> float | None:
    """Оценка TSS, если источник его не прислал. Порядок: мощность → пульс → темп."""
    if not duration_s and distance_m and not avg_hr:
        # план задан только дистанцией: спокойная тренировка, IF ≈ 0.75
        duration_s = estimate_duration(sport, distance_m)
        return round(duration_s / 3600 * 0.75 ** 2 * 100, 1) if duration_s else None
    if not duration_s:
        return None
    hours = duration_s / 3600
    t = thresholds.get()
    if sport == "bike" and np and t["ftp"]:
        intensity = np / t["ftp"]
        return round(hours * intensity ** 2 * 100, 1)
    if avg_hr:
        intensity = avg_hr / thresholds.lthr_for(sport)
        return round(hours * intensity ** 2 * 100, 1)
    if sport == "run" and distance_m:
        pace = duration_s / (distance_m / 1000)
        intensity = t["run_pace"] / pace
        return round(hours * intensity ** 2 * 100, 1)
    if sport == "swim" and distance_m:
        pace = duration_s / (distance_m / 100)
        intensity = t["swim_css"] / pace
        return round(hours * intensity ** 3 * 100, 1)
    return round(hours * 50, 1)  # умеренная нагрузка по умолчанию


def fitness_series(daily_tss: dict[str, float], start: date, end: date) -> list[dict]:
    """Классическая модель Банистера: CTL — 42 дня, ATL — 7 дней, TSB = CTL − ATL вчерашнего дня."""
    k_ctl, k_atl = 1 - math.exp(-1 / 42), 1 - math.exp(-1 / 7)
    ctl = atl = 0.0
    out = []
    d = start
    while d <= end:
        tsb = ctl - atl
        tss = daily_tss.get(d.isoformat(), 0.0)
        ctl += (tss - ctl) * k_ctl
        atl += (tss - atl) * k_atl
        out.append({"date": d.isoformat(), "tss": round(tss, 1), "ctl": round(ctl, 1),
                    "atl": round(atl, 1), "tsb": round(tsb, 1)})
        d += timedelta(days=1)
    return out


def match_plan(planned: list[dict], actual: list[dict]) -> list[dict]:
    """Сопоставляет плановые тренировки с фактическими по дате и виду спорта.

    Возвращает строки {date, sport, planned, actual, status, compliance}.
    """
    used = set()
    rows = []
    plans = sorted(planned, key=lambda r: (r["date"], r["sport"]))
    found: dict[int, dict] = {}

    def size(r):
        return r.get("distance_m") or r.get("duration_s") or 0

    # Проход 1 — тот же день; проход 2 — соседний день (тренировку перенесли на ±1 день)
    for shift in (0, 1):
        for p in plans:
            if p["sport"] == "rest" or id(p) in found:
                continue
            pd = date.fromisoformat(p["date"])
            days = {p["date"]} if shift == 0 else {(pd + timedelta(days=d)).isoformat() for d in (-1, 1)}
            candidates = [a for a in actual if a["date"] in days and a["sport"] == p["sport"]
                          and id(a) not in used]
            if candidates:
                best = min(candidates, key=lambda a: abs(size(a) - size(p)))
                used.add(id(best))
                found[id(p)] = best

    for p in plans:
        if p["sport"] == "rest":
            rows.append({"date": p["date"], "sport": "rest", "planned": p, "actual": None,
                         "status": "rest", "compliance": None})
            continue
        best = found.get(id(p))
        rows.append({"date": p["date"], "sport": p["sport"], "planned": p, "actual": best,
                     "moved_to": best["date"] if best and best["date"] != p["date"] else None,
                     **_status(p, best)})
    for a in actual:
        if id(a) not in used:
            rows.append({"date": a["date"], "sport": a["sport"], "planned": None, "actual": a,
                         "status": "unplanned", "compliance": None})
    rows.sort(key=lambda r: (r["date"], r["sport"]))
    return rows


def _status(p: dict, a: dict | None) -> dict:
    today = date.today().isoformat()
    if a is None:
        if p["date"] > today:
            return {"status": "upcoming", "compliance": None}
        if p["date"] == today:
            return {"status": "today", "compliance": None}
        return {"status": "missed", "compliance": 0}
    ratio = None
    for key in ("distance_m", "duration_s", "tss"):
        if p.get(key) and a.get(key):
            ratio = a[key] / p[key]
            break
    if ratio is None:
        return {"status": "done", "compliance": None}
    pct = round(ratio * 100)
    # Цвета как в TrainingPeaks: 80–120 % зелёный, 50–80/120–150 жёлтый, иначе оранжевый
    if 80 <= pct <= 120:
        status = "done"
    elif 50 <= pct <= 150:
        status = "partial"
    else:
        status = "off"
    return {"status": status, "compliance": pct}
