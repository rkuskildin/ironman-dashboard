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


# Гребков на отрезок по умолчанию: «длина:стиль». Кроль 50 м — по тренировкам, где часы посчитали верно;
# брасс 50 м — со слов спортсмена. Правятся в карточке плавания.
SPL_DEFAULT = {"50:FREESTYLE": 30, "50:BREASTSTROKE": 36.5}


def spl_defaults() -> dict:
    with db.session() as c:
        row = c.execute("SELECT value FROM settings WHERE key='swim_spl'").fetchone()
    saved = json.loads(row["value"]) if row else {}
    out = dict(SPL_DEFAULT)
    for k, v in saved.items():
        out[k if ":" in k else f"{k}:BREASTSTROKE"] = v   # старый формат {"50": 36.5} был про брасс
    return out


def set_spl(pool_m: float, style: str, spl: float):
    d = spl_defaults()
    d[f"{int(pool_m)}:{style}"] = spl
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('swim_spl', ?)", (json.dumps(d),))


def set_fix(source: str, source_id: str, keep_garmin: bool = False, distance_m: float | None = None, clear: bool = False):
    f = fixes()
    key = f"{source}:{source_id}"
    if clear:
        f.pop(key, None)
    else:
        f[key] = {"keep_garmin": keep_garmin, "distance_m": distance_m}
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('swim_fix', ?)", (json.dumps(f),))


def analyze(sw: dict, fix: dict | None = None, spl_map: dict | None = None) -> dict:
    """Отрезки и гребки. Часы чаще ошибаются в разворотах, чем в гребках, поэтому реальное число отрезков
    считаем по сумме гребков каждого стиля / «своих» гребков на отрезок этим стилем."""
    fix = fix or {}
    spl_map = spl_map if spl_map is not None else spl_defaults()
    lengths = sw.get("lengths") or []
    pool = sw.get("pool_m") or 25
    stroked = [l for l in lengths if l.get("strokes")]
    total = sum(l["strokes"] for l in stroked) or sw.get("strokes") or 0
    med_s = median([l["strokes"] for l in stroked]) if stroked else None
    est, covered, rows = 0.0, 0, []
    for l in lengths:
        flag = None
        spl = spl_map.get(f"{int(pool)}:{l.get('style')}")
        if not l.get("strokes"):
            flag = "пауза — в дистанцию не входит"
        elif spl:
            est += l["strokes"] / spl
            covered += 1
            if l["strokes"] <= 0.6 * spl:
                flag = f"лишний разворот: {l['strokes']} гребков вместо ~{spl:g}"
            elif l["strokes"] >= 1.5 * spl:
                flag = f"пропущен разворот: похоже на {round(l['strokes'] / spl)} отрезка"
        else:
            est += 1  # стиль без известных гребков — верим часам
        rows.append({**l, "style_ru": STYLE.get(l.get("style") or "", ""), "flag": flag})
    styles = {}
    for l in stroked:
        st = STYLE.get(l.get("style") or "", "другое")
        styles[st] = styles.get(st, 0) + 1
    active = len(stroked)
    garmin_dist = active * pool
    reliable = stroked and covered >= 0.8 * active
    est_lengths = round(est) if reliable else None
    est_dist = est_lengths * pool if est_lengths else None
    auto = bool(est_dist and abs(est_dist - garmin_dist) / max(garmin_dist, 1) > 0.15)
    if fix.get("distance_m"):
        final, how = fix["distance_m"], "вручную"
    elif fix.get("keep_garmin"):
        final, how = None, "как в Garmin"
    elif auto:
        final, how = est_dist, "по гребкам"
    else:
        final, how = None, None
    moving = sum(l["t"] for l in stroked)
    n = est_lengths or active
    spl_avg = total / n if n else None
    hint = None
    if not reliable and med_s and med_s < (30 if pool >= 50 else 15) * 0.6:
        hint = f"Часы насчитали в среднем {med_s:g} гребков на отрезок {pool:g} м — похоже на лишние развороты. Укажите свои гребки на отрезок."
    return {
        "pool_m": sw.get("pool_m"), "pool_used": pool, "garmin_lengths": active, "garmin_distance": garmin_dist,
        "est_lengths": est_lengths, "est_distance": est_dist, "fixed_distance": final, "fix_how": how,
        "strokes": total, "avg_strokes": round(med_s) if med_s else None, "spl_real": round(spl_avg, 1) if spl_avg else None,
        "spl_map": {k.split(":")[1]: v for k, v in spl_map.items() if k.startswith(f"{int(pool)}:")},
        "intervals": sw.get("intervals"), "swolf": sw.get("swolf"),
        "swolf_real": round(moving / n + spl_avg) if n and spl_avg else None,
        "styles": styles, "rest_counted": sum(1 for r in rows if not r.get("strokes")),
        "suspicious": sum(1 for r in rows if r["flag"] and r.get("strokes")), "pool_hint": hint, "lengths": rows, "fix": fix or None,
    }
