"""Разбор плавания в бассейне: отрезки, гребки, SWOLF и проверка того, что насчитали часы.

Часы в бассейне считают отрезки по разворотам. Ошибаются они предсказуемо:
  * отдых без паузы засчитывается как отрезок (0 гребков);
  * пропущенный разворот — два отрезка сливаются в один (вдвое больше гребков и времени);
  * лишний разворот — отрезок с аномально малым числом гребков.
По медиане гребков на отрезок оцениваем, сколько отрезков было на самом деле.
"""
import json
from statistics import median

from . import db

STYLE = {"FREESTYLE": "кроль", "BREASTSTROKE": "брасс", "BACKSTROKE": "на спине", "BUTTERFLY": "баттерфляй",
         "DRILL": "упражнения", "MIXED": "смешанный"}


def fixes() -> dict:
    with db.session() as c:
        row = c.execute("SELECT value FROM settings WHERE key='swim_fix'").fetchone()
    return json.loads(row["value"]) if row else {}


def set_fix(source: str, source_id: str, pool_m: float | None, distance_m: float | None):
    f = fixes()
    key = f"{source}:{source_id}"
    if pool_m is None and distance_m is None:
        f.pop(key, None)
    else:
        f[key] = {"pool_m": pool_m, "distance_m": distance_m}
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('swim_fix', ?)", (json.dumps(f),))


def analyze(sw: dict, fix: dict | None = None) -> dict:
    lengths = sw.get("lengths") or []
    pool = (fix or {}).get("pool_m") or sw.get("pool_m") or 25
    stroked = [l for l in lengths if l.get("strokes")]
    med_s = median([l["strokes"] for l in stroked]) if stroked else None
    med_t = median([l["t"] for l in stroked]) if stroked else None
    rows, est = [], 0
    for l in lengths:
        flag, k = None, 1
        if not l.get("strokes"):
            flag, k = "отдых засчитан как отрезок", 0
        elif med_s and l["strokes"] >= 1.6 * med_s and l["t"] >= 1.5 * med_t:
            k = max(2, round(l["strokes"] / med_s))
            flag = f"пропущен разворот: похоже на {k} отрезка"
        elif med_s and l["strokes"] <= 0.45 * med_s and l["t"] <= 0.6 * med_t:
            flag, k = "лишний разворот: слишком мало гребков", 0
        est += k
        rows.append({**l, "style_ru": STYLE.get(l.get("style") or "", ""), "flag": flag, "counted": k})
    styles = {}
    for l in stroked:
        st = STYLE.get(l.get("style") or "", "другое")
        styles[st] = styles.get(st, 0) + 1
    # подсказка про длину бассейна: на 25 м обычно 8–14 гребков (циклов), на 50 м — 18–28
    pool_hint = None
    if med_s and (sw.get("pool_m") or 0) >= 50 and med_s <= 16:
        pool_hint = f"В среднем {med_s:g} гребков на отрезок — это похоже на бассейн 25 м, а в часах стоит 50 м"
    elif med_s and (sw.get("pool_m") or 0) and sw["pool_m"] <= 25 and med_s >= 20:
        pool_hint = f"В среднем {med_s:g} гребков на отрезок — это похоже на бассейн 50 м, а в часах стоит 25 м"
    garmin_dist = len(lengths) * (sw.get("pool_m") or pool)
    est_dist = est * pool
    final = (fix or {}).get("distance_m") or (est_dist if fix else None)
    swolfs = [l["swolf"] for l in stroked if l.get("swolf") and not any(r["i"] == l["i"] and r["flag"] for r in rows)]
    return {
        "pool_m": sw.get("pool_m"), "pool_used": pool, "garmin_lengths": len(lengths), "garmin_distance": garmin_dist,
        "est_lengths": est, "est_distance": est_dist, "fixed_distance": final,
        "strokes": sw.get("strokes"), "avg_strokes": round(med_s) if med_s else None,
        "swolf": sw.get("swolf"), "swolf_clean": round(median(swolfs)) if swolfs else None,
        "styles": styles, "rest_counted": sum(1 for r in rows if not r.get("strokes")),
        "suspicious": sum(1 for r in rows if r["flag"]), "pool_hint": pool_hint, "lengths": rows, "fix": fix,
    }
