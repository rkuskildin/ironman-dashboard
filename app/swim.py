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


def spl_defaults() -> dict:
    """Гребков на отрезок, которые знает сам спортсмен, по длине бассейна: {"50": 36, "25": 17}."""
    with db.session() as c:
        row = c.execute("SELECT value FROM settings WHERE key='swim_spl'").fetchone()
    return json.loads(row["value"]) if row else {}


def set_fix(source: str, source_id: str, pool_m: float | None, distance_m: float | None, spl: float | None = None):
    f = fixes()
    key = f"{source}:{source_id}"
    if pool_m is None and distance_m is None and spl is None:
        f.pop(key, None)
    else:
        f[key] = {"pool_m": pool_m, "distance_m": distance_m, "spl": spl}
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('swim_fix', ?)", (json.dumps(f),))
        if spl and pool_m:  # запоминаем «свои» гребки на отрезок для этой длины бассейна
            d = spl_defaults()
            d[str(int(pool_m))] = spl
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('swim_spl', ?)", (json.dumps(d),))


def analyze(sw: dict, fix: dict | None = None) -> dict:
    """Отрезки и гребки. Если известно, сколько гребков у спортсмена на отрезок, — реальное число отрезков
    считаем по сумме гребков: часы чаще всего ошибаются в разворотах, а гребки считают надёжнее."""
    fix = fix or {}
    lengths = sw.get("lengths") or []
    pool = fix.get("pool_m") or sw.get("pool_m") or 25
    spl = fix.get("spl") or spl_defaults().get(str(int(pool)))
    stroked = [l for l in lengths if l.get("strokes")]
    total = sum(l["strokes"] for l in stroked) or sw.get("strokes") or 0
    med_s = median([l["strokes"] for l in stroked]) if stroked else None
    rows = []
    for l in lengths:
        flag = None
        if not l.get("strokes"):
            flag = "пауза — в дистанцию не входит"
        elif spl and l["strokes"] <= 0.6 * spl:
            flag = f"лишний разворот: {l['strokes']} гребков вместо ~{spl:g} — кусок отрезка"
        elif spl and l["strokes"] >= 1.5 * spl:
            flag = f"пропущен разворот: похоже на {round(l['strokes'] / spl)} отрезка"
        rows.append({**l, "style_ru": STYLE.get(l.get("style") or "", ""), "flag": flag})
    styles = {}
    for l in stroked:
        st = STYLE.get(l.get("style") or "", "другое")
        styles[st] = styles.get(st, 0) + 1
    active = len(stroked)
    garmin_dist = active * (sw.get("pool_m") or pool)
    est_lengths = round(total / spl) if spl and total else None
    est_dist = est_lengths * pool if est_lengths else None
    # подсказка: у Garmin гребков на отрезок заметно меньше, чем бывает на такой дистанции — значит, лишние развороты
    hint = None
    if med_s and not spl:
        expected = 30 if pool >= 50 else 15
        if med_s < expected * 0.6:
            hint = (f"Часы насчитали в среднем {med_s:g} гребков на отрезок {pool:g} м — это мало, обычно так бывает, когда часы "
                    f"ставят лишние развороты посреди дорожки. Укажите, сколько у вас гребков на {pool:g} м, — пересчитаю дистанцию.")
    final = fix.get("distance_m") or (est_dist if (fix.get("spl") or fix.get("pool_m")) else None)
    moving = sum(l["t"] for l in stroked)
    swolf_real = round(moving / est_lengths + spl) if est_lengths and spl else None
    return {
        "pool_m": sw.get("pool_m"), "pool_used": pool, "spl": spl, "garmin_lengths": active, "garmin_distance": garmin_dist,
        "est_lengths": est_lengths, "est_distance": est_dist, "fixed_distance": final,
        "strokes": total, "avg_strokes": round(med_s) if med_s else None, "intervals": sw.get("intervals"),
        "swolf": sw.get("swolf"), "swolf_real": swolf_real,
        "styles": styles, "rest_counted": sum(1 for r in rows if not r.get("strokes")),
        "suspicious": sum(1 for r in rows if r["flag"] and r.get("strokes")), "pool_hint": hint, "lengths": rows, "fix": fix or None,
    }
