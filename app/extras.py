"""Расширения панели: путь к старту, рекорды, аэробная эффективность, сон ↔ восстановление,
комментарии, недельный отчёт, выбор старта, вес, снаряжение, исключение сбойных тренировок."""
import json
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import mean

from . import config, db, goals, service, thresholds

SCHEMA = """
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL, date TEXT NOT NULL,
    author TEXT NOT NULL, author_name TEXT, role TEXT, text TEXT NOT NULL,
    created TEXT DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS comments_date ON comments(date);
CREATE TABLE IF NOT EXISTS weights (date TEXT PRIMARY KEY, kg REAL NOT NULL, source TEXT);
CREATE TABLE IF NOT EXISTS excluded (source TEXT, source_id TEXT, PRIMARY KEY (source, source_id));
"""


def init():
    with db.session() as c:
        c.executescript(SCHEMA)


def _setting(key, default=None):
    with db.session() as c:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


def _set_setting(key, value):
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))


# ---------------- старт ----------------
def race() -> dict:
    r = _setting("race") or {}
    return {"name": r.get("name") or config.RACE_NAME, "date": r.get("date") or config.RACE_DATE,
            "location": r.get("location", ""), "id": r.get("id")}


def set_race(r: dict) -> dict:
    date.fromisoformat(r["date"])
    _set_setting("race", {k: r.get(k) for k in ("name", "date", "location", "id")})
    return race()


# ---------------- исключённые тренировки ----------------
def excluded_set() -> set[tuple[str, str]]:
    with db.session() as c:
        return {(r["source"], r["source_id"]) for r in c.execute("SELECT source, source_id FROM excluded")}


def set_excluded(source: str, source_id: str, on: bool):
    with db.session() as c:
        if on:
            c.execute("INSERT OR IGNORE INTO excluded VALUES (?, ?)", (source, source_id))
        else:
            c.execute("DELETE FROM excluded WHERE source=? AND source_id=?", (source, source_id))


# ---------------- путь к старту: фазы и траектория CTL ----------------
# (название, недель до старта: начало → конец, CTL в начале → в конце, часы в неделю, фокус)
PHASES = [
    ("Общая база", 104, 80, None, 45, "6–9 ч", "техника плавания, аэробный бег и велосипед в Z2, силовая 2 раза в неделю, режим сна"),
    ("Подготовка к 70.3", 80, 56, 45, 70, "8–12 ч", "длинные заезды до 90 км, бег до 21 км, контрольный старт Ironman 70.3"),
    ("Межсезонье", 56, 48, 70, 55, "5–8 ч", "восстановление после 70.3, сила, техника, работа над слабыми местами"),
    ("База 2", 48, 28, 55, 85, "10–13 ч", "объём в Z2, длинные заезды 120–150 км, бег до 25 км"),
    ("Развитие", 28, 10, 85, 115, "12–16 ч", "темп гонки, бессмены вело + бег, заезды до 180 км, бег до 30–32 км"),
    ("Специальная", 10, 3, 115, 125, "14–18 ч", "репетиции гонки: питание, экипировка, темп; ключевые длинные тренировки"),
    ("Подводка", 3, 0, 125, 110, "сокращение объёма", "снижение объёма при сохранении интенсивности, свежесть TSB +15…+25 к старту"),
]


def path() -> dict:
    r = race()
    rd = date.fromisoformat(r["date"])
    today = date.today()
    fit = {s["date"]: s for s in service.fitness(days=max(1, (today - (rd - timedelta(weeks=104))).days), forward=0)}
    cur_ctl = fit.get(today.isoformat(), {}).get("ctl") or 0
    phases, target = [], []
    first_start = rd - timedelta(weeks=PHASES[0][1])
    for i, (name, w0, w1, c0, c1, hours, focus) in enumerate(PHASES):
        p0, p1 = rd - timedelta(weeks=w0), rd - timedelta(weeks=w1)
        c0 = c0 if c0 is not None else min(cur_ctl, 20)
        phases.append({"name": name, "start": p0.isoformat(), "end": p1.isoformat(), "ctl_start": c0, "ctl_end": c1,
                       "hours": hours, "focus": focus, "current": p0 <= today < p1})
        d = p0
        while d <= p1:
            frac = (d - p0).days / max(1, (p1 - p0).days)
            target.append({"date": d.isoformat(), "ctl": round(c0 + (c1 - c0) * frac, 1)})
            d += timedelta(days=7)
    cur = next((p for p in phases if p["current"]), phases[0] if today < first_start else phases[-1])
    tgt_today = next((t["ctl"] for t in target if t["date"] >= today.isoformat()), None)
    actual = [{"date": k, "ctl": v["ctl"]} for k, v in sorted(fit.items()) if k >= first_start.isoformat()][::3]
    # вехи: самые длинные тренировки против ключевых объёмов
    longest = {s: max((x["distance_m"] for x in goals.sessions(s, 730)), default=0) for s in ("swim", "bike", "run")}
    milestones = [
        ("Проплыть 2 км без остановки", "swim", 2000), ("Проплыть 3,8 км", "swim", 3800),
        ("Заезд 90 км", "bike", 90000), ("Заезд 150 км", "bike", 150000), ("Заезд 180 км", "bike", 180000),
        ("Пробежать 21,1 км", "run", 21100), ("Пробежать 30 км", "run", 30000),
    ]
    return {
        "race": r, "weeks_left": (rd - today).days // 7, "phases": phases, "current": cur,
        "ctl": round(cur_ctl, 1), "ctl_target_today": tgt_today, "target": target, "actual": actual,
        "milestones": [{"label": l, "sport": s, "target": t, "best": longest[s], "done": longest[s] >= t * 0.98}
                       for l, s, t in milestones],
    }


# ---------------- личные рекорды ----------------
PR_DIST = {"run": [1000, 5000, 10000, 21097], "bike": [20000, 40000, 90000, 180000], "swim": [400, 1000, 1500, 3800]}


def records() -> dict:
    out = {}
    for sport, dists in PR_DIST.items():
        ss = [s for s in goals.sessions(sport, 3650)]
        rows = []
        for d in dists:
            cand = [s for s in ss if s["distance_m"] >= d]
            if not cand:
                rows.append({"distance": d, "best": None})
                continue
            best = min(cand, key=lambda s: s["pace"])
            # прогресс: каждый раз, когда лучший темп на этой дистанции обновлялся
            prog, cur = [], None
            for s in sorted(cand, key=lambda s: s["date"]):
                if cur is None or s["pace"] < cur:
                    cur = s["pace"]
                    prog.append({"date": s["date"], "pace": s["pace"]})
            u = goals.unit(sport)
            rows.append({"distance": d, "best": {"date": best["date"], "pace": best["pace"], "title": best["title"],
                                                 "time": round(best["pace"] * d / u), "session_distance": best["distance_m"]},
                         "progress": prog})
        longest = max(ss, key=lambda s: s["distance_m"], default=None)
        out[sport] = {"rows": rows, "longest": longest and {"date": longest["date"], "distance": longest["distance_m"],
                                                            "title": longest["title"]}, "sessions": len(ss)}
    return out


# ---------------- аэробная эффективность ----------------
def efficiency(sport: str) -> dict:
    """Скорость на удар сердца в аэробных тренировках. Растёт — база строится."""
    t = thresholds.get()
    z4 = (t["zones_bike"] if sport == "bike" else t["zones_run"])[3]
    pts = []
    for s in goals.sessions(sport, 365):
        if not s["avg_hr"] or s["avg_hr"] >= z4:
            continue
        speed = s["distance_m"] / s["moving_s"] * 60  # м/мин
        pts.append({"date": s["date"], "ef": round(speed / s["avg_hr"], 3), "hr": s["avg_hr"], "pace": s["pace"],
                    "distance_m": s["distance_m"]})
    trend = None
    if len(pts) >= 3:
        x0 = date.fromisoformat(pts[0]["date"])
        xs = [(date.fromisoformat(p["date"]) - x0).days for p in pts]
        ys = [p["ef"] for p in pts]
        mx, my = mean(xs), mean(ys)
        den = sum((x - mx) ** 2 for x in xs)
        if den:
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
            trend = round(slope * 90 / my * 100, 1)  # % за 90 дней
    return {"points": pts, "trend_90d_pct": trend, "z4_floor": z4}


# ---------------- сон и восстановление ----------------
def sleep_impact() -> dict:
    reg = service.regime(120)
    health = {d["date"]: d for d in service.health(120)}
    rs = config.RECOVERY_SOURCE
    rows = []
    for n in reg["nights"]:
        h = (health.get(n["wake_date"]) or {}).get(rs) or (health.get(n["wake_date"]) or {}).get("garmin") or {}
        rows.append({"night": n["night_of"], "bed": n["bed_time"], "bed_min": n["bed_min"], "sleep_h": n["sleep_h"],
                     "hrv": h.get("hrv"), "rhr": h.get("resting_hr")})
    target = reg["target_min"]
    groups = [("до " + reg["target"], lambda m: m <= target), ("до 00:30", lambda m: target < m <= 390),
              ("00:30–01:30", lambda m: 390 < m <= 450), ("позже 01:30", lambda m: m > 450)]
    out = []
    for label, f in groups:
        g = [r for r in rows if f(r["bed_min"])]
        hv = [r["hrv"] for r in g if r["hrv"]]
        rh = [r["rhr"] for r in g if r["rhr"]]
        sl = [r["sleep_h"] for r in g if r["sleep_h"]]
        out.append({"label": label, "nights": len(g), "hrv": round(mean(hv), 1) if hv else None,
                    "rhr": round(mean(rh), 1) if rh else None, "sleep": round(mean(sl), 1) if sl else None})
    return {"nights": rows, "groups": out}


# ---------------- комментарии ----------------
def comments(start: str, end: str) -> list[dict]:
    with db.session() as c:
        return [dict(r) for r in c.execute("SELECT * FROM comments WHERE date BETWEEN ? AND ? ORDER BY id", (start, end))]


def recent_comments(limit: int = 8) -> list[dict]:
    with db.session() as c:
        return [dict(r) for r in c.execute("SELECT * FROM comments ORDER BY id DESC LIMIT ?", (limit,))]


def add_comment(user: dict, key: str, day: str, text: str) -> dict:
    text = text.strip()[:2000]
    if not text:
        raise ValueError("Пустой комментарий")
    date.fromisoformat(day)
    with db.session() as c:
        cid = c.execute("INSERT INTO comments (key, date, author, author_name, role, text) VALUES (?,?,?,?,?,?)",
                        (key, day, user["login"], user.get("name") or user["login"], user["role"], text)).lastrowid
        return dict(c.execute("SELECT * FROM comments WHERE id=?", (cid,)).fetchone())


def delete_comment(user: dict, cid: int) -> bool:
    with db.session() as c:
        return c.execute("DELETE FROM comments WHERE id=? AND author=?", (cid, user["login"])).rowcount > 0


# ---------------- недельный отчёт ----------------
def report(week: str) -> dict:
    mon = date.fromisoformat(week)
    mon -= timedelta(days=mon.weekday())
    sun = mon + timedelta(days=6)
    days = service.calendar(mon.isoformat(), sun.isoformat())
    items = [i for d in days for i in d["items"]]
    by = defaultdict(lambda: {"plan_s": 0, "fact_s": 0, "plan_m": 0, "fact_m": 0, "plan_tss": 0, "fact_tss": 0})
    for i in items:
        b = by[i["sport"]]
        for side, pre in (("planned", "plan"), ("actual", "fact")):
            w = i.get(side) or {}
            b[pre + "_s"] += w.get("duration_s") or 0
            b[pre + "_m"] += w.get("distance_m") or 0
            b[pre + "_tss"] += w.get("tss") or 0
    planned = [i for i in items if i["planned"] and i["sport"] != "rest"]
    done = [i for i in planned if i["status"] in ("done", "partial", "off")]
    health = [d for d in service.health(21) if mon.isoformat() <= d["date"] <= sun.isoformat()]
    rs = config.RECOVERY_SOURCE

    def avg(k):
        v = [(d.get(rs) or {}).get(k) for d in health]
        v = [x for x in v if x]
        return round(mean(v), 1) if v else None

    reg = [n for n in service.regime(21)["nights"] if mon.isoformat() <= n["night_of"] <= sun.isoformat()]
    fit = {s["date"]: s for s in service.fitness(days=(date.today() - mon).days + 1, forward=0)}
    return {
        "week": mon.isoformat(), "end": sun.isoformat(), "race": race(), "days": days,
        "by_sport": {k: {kk: round(vv) for kk, vv in v.items()} for k, v in by.items()},
        "planned": len(planned), "done": len(done),
        "missed": [{"date": i["date"], "title": (i["planned"] or {}).get("title"), "sport": i["sport"]} for i in planned if i["status"] == "missed"],
        "unplanned": [{"date": i["date"], "title": (i["actual"] or {}).get("title"), "sport": i["sport"]} for i in items if i["status"] == "unplanned"],
        "health": {"sleep_h": round(avg("sleep_s") / 3600, 1) if avg("sleep_s") else None, "hrv": avg("hrv"), "rhr": avg("resting_hr")},
        "regime": {"nights": len(reg), "on_time": sum(n["on_time"] for n in reg),
                   "avg_bed": (lambda m: f"{(18 * 60 + m) // 60 % 24:02d}:{(18 * 60 + m) % 60:02d}")(round(mean([n["bed_min"] for n in reg]))) if reg else None},
        "ctl": {"start": (fit.get(mon.isoformat()) or {}).get("ctl"), "end": (fit.get(min(sun, date.today()).isoformat()) or {}).get("ctl")},
        "comments": comments(mon.isoformat(), sun.isoformat()),
    }


# ---------------- вес ----------------
def weights(days: int = 365) -> dict:
    start = (date.today() - timedelta(days=days)).isoformat()
    with db.session() as c:
        rows = [dict(r) for r in c.execute("SELECT * FROM weights WHERE date >= ? ORDER BY date", (start,))]
    return {"rows": rows, "profile": thresholds.get()["weight"]}


def add_weight(day: str, kg: float):
    date.fromisoformat(day)
    if not 30 <= kg <= 200:
        raise ValueError("Вес вне диапазона")
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO weights (date, kg, source) VALUES (?, ?, 'manual')", (day, round(kg, 1)))


# ---------------- снаряжение (Garmin Gear) ----------------
def update_gear(g) -> int:
    try:
        items = g.get_gear(g.garth.profile["profileId"]) or []
    except Exception:
        return 0
    out = []
    for it in items:
        try:
            st = g.get_gear_stats(it["uuid"]) or {}
        except Exception:
            st = {}
        out.append({"uuid": it["uuid"], "name": it.get("displayName") or it.get("customMakeModel") or
                    f"{it.get('gearMakeName', '')} {it.get('gearModelName', '')}".strip(),
                    "type": it.get("gearTypeName"), "status": it.get("gearStatusName"),
                    "since": (it.get("dateBegin") or "")[:10], "max_m": it.get("maximumMeters"),
                    "distance_m": st.get("totalDistance"), "activities": st.get("totalActivities")})
    _set_setting("gear", {"updated": time.strftime("%Y-%m-%d %H:%M"), "items": out})
    return len(out)


GEAR_SPORT = {"Shoes": "run", "Bike": "bike"}


def gear() -> dict:
    """Снаряжение из Garmin. Если в Garmin оно не привязано к тренировкам — считаем пробег сами:
    кроссовки — все пробежки, велосипед — все заезды с даты добавления."""
    g = _setting("gear", {"items": [], "updated": None})
    for it in g["items"]:
        sport = GEAR_SPORT.get(it.get("type"))
        if sport and not it.get("distance_m"):
            ss = goals.sessions(sport, 3650)
            since = it.get("since") or "2000-01-01"
            it["distance_m"] = sum(s["distance_m"] for s in ss if s["date"] >= since)
            it["activities"] = sum(1 for s in ss if s["date"] >= since)
            it["estimated"] = True
    return g
