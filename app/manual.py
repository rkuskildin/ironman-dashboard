"""Тренировки, которые не записывались ни на Garmin, ни в Fitbit (хоккей и т.п.).

Пользователь указывает дату, время и вид спорта — пульс берём из непрерывного
пульса Fitbit за этот отрезок, по нему считаем зоны и TSS.
"""
import json
from datetime import datetime, timedelta

from . import config, db, thresholds
from .connectors import fitbit

def _zone(bpm: float) -> int:
    """Пульсовая зона по зонам спортсмена из Garmin (или по ПАНО, если их нет)."""
    return thresholds.zone_of(bpm, thresholds.get()["zones_run"])


def heart_rate(day: str, start: str, end: str) -> tuple[list[tuple[datetime, float]], datetime, datetime]:
    """Пульс Fitbit по местному времени Fitbit (берём civilTime замеров, чтобы не зависеть от пояса Mac)."""
    t0 = datetime.fromisoformat(f"{day}T{start}")
    t1 = datetime.fromisoformat(f"{day}T{end}")
    if t1 <= t0:
        t1 += timedelta(days=1)  # тренировка через полночь
    # запас ±14 ч покрывает любой часовой пояс; точный отбор — по civilTime
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    pts = fitbit._list("heart-rate", f'heart_rate.sample_time.physical_time >= "{(t0 - timedelta(hours=14)).strftime(fmt)}" '
                                     f'AND heart_rate.sample_time.physical_time < "{(t1 + timedelta(hours=14)).strftime(fmt)}"',
                       page_size=10000)
    samples = []
    for p in pts:
        st = p["heartRate"]["sampleTime"]
        c = st["civilTime"]
        tm = c.get("time", {})
        local = datetime(c["date"]["year"], c["date"]["month"], c["date"]["day"],
                         tm.get("hours", 0), tm.get("minutes", 0), tm.get("seconds", 0))
        if t0 <= local < t1:
            samples.append((local, float(p["heartRate"]["beatsPerMinute"]), st.get("physicalTime")))
    samples.sort()
    return samples, t0, t1


def add(day: str, start: str, end: str, sport: str, title: str = "", note: str = "") -> dict:
    samples, t0, t1 = heart_rate(day, start, end)
    duration = (t1 - t0).total_seconds()
    bpm = [s[1] for s in samples]
    zones = [0.0] * 5
    for i, (t, b, _) in enumerate(samples):
        nxt = samples[i + 1][0] if i + 1 < len(samples) else t1
        zones[_zone(b)] += min((nxt - t).total_seconds(), 30)  # пропуски в данных не засчитываем
    avg = round(sum(bpm) / len(bpm)) if bpm else None
    gmt = samples[0][2] if samples else None
    row = {
        "source": "manual", "source_id": f"{day}T{start}", "date": day,
        "start_time": t0.strftime("%Y-%m-%d %H:%M:%S"),
        "start_gmt": datetime.fromisoformat(gmt.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S") if gmt else None,
        "sport": sport, "title": title or None, "duration_s": duration,
        "avg_hr": avg, "max_hr": max(bpm) if bpm else None,
        "tss": _hr_tss(samples, t1),
        "athlete_comments": note or None,
        "analysis": json.dumps({"hr_zones": zones, "manual": True, "hr_samples": len(bpm),
                                "hr_curve": _curve(samples)}),
    }
    with db.session() as c:
        db.upsert(c, "activities", row)
    db.log("manual", True, f"{title or sport} {day} {start}–{end}: пульс {avg}/{row['max_hr']}, TSS {row['tss']}")
    return row


def _hr_tss(samples, t1) -> float | None:
    """hrTSS по каждому замеру — точнее, чем по среднему пульсу для игровых видов с рваным темпом."""
    if not samples:
        return None
    total = 0.0
    for i, (t, b, _) in enumerate(samples):
        nxt = samples[i + 1][0] if i + 1 < len(samples) else t1
        dt = min((nxt - t).total_seconds(), 30)
        total += dt / 3600 * (b / thresholds.get()["lthr_run"]) ** 2 * 100
    return round(total, 1)


def _curve(samples, step_s: int = 60) -> list:
    """Поминутная кривая пульса для графика."""
    out, bucket, cur = [], [], None
    for t, b, _ in samples:
        k = t.replace(second=0)
        if cur is not None and k != cur:
            out.append([cur.strftime("%H:%M"), round(sum(bucket) / len(bucket))])
            bucket = []
        cur = k
        bucket.append(b)
    if bucket:
        out.append([cur.strftime("%H:%M"), round(sum(bucket) / len(bucket))])
    return out


def delete(source_id: str):
    with db.session() as c:
        c.execute("DELETE FROM activities WHERE source='manual' AND source_id=?", (source_id,))


def recompute(analysis: dict) -> tuple[float | None, list[float]]:
    """TSS и зоны по сохранённой поминутной кривой — с текущими порогами (после их смены)."""
    curve = analysis.get("hr_curve") or []
    if not curve:
        return None, analysis.get("hr_zones") or []
    lthr, zones = thresholds.get()["lthr_run"], [0.0] * 5
    tss = 0.0
    for _, b in curve:
        tss += 1 / 60 * (b / lthr) ** 2 * 100
        zones[_zone(b)] += 60
    return round(tss, 1), zones
