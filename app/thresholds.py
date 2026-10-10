"""Пороги спортсмена: из Garmin (автоматически) → правка вручную → значения по умолчанию из .env.

Хранятся в таблице settings: 'thresholds_garmin' (обновляется при синхронизации) и
'thresholds_manual' (правка в панели). Ручное значение всегда главнее.
"""
import json
import time

from . import config, db

FIELDS = {
    # ключ: (подпись, единица, значение по умолчанию)
    "lthr_run": ("Пульс ПАНО · бег", "уд/мин", lambda: config.LTHR),
    "lthr_bike": ("Пульс ПАНО · велосипед", "уд/мин", lambda: config.LTHR),
    "max_hr": ("Максимальный пульс", "уд/мин", lambda: 190),
    "rest_hr": ("Пульс покоя", "уд/мин", lambda: 55),
    "run_pace": ("Пороговый темп бега", "сек/км", lambda: config.RUN_THRESHOLD_PACE),
    "swim_css": ("Пороговый темп плавания (CSS)", "сек/100 м", lambda: config.SWIM_CSS),
    "ftp": ("FTP · велосипед", "Вт", lambda: config.FTP),
    "weight": ("Вес", "кг", lambda: 70),
}
_cache: dict = {"t": 0, "v": None}


def _load(key: str) -> dict:
    with db.session() as c:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return json.loads(row["value"]) if row else {}


def _save(key: str, value: dict):
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    _cache["t"] = 0


def get(detailed: bool = False) -> dict:
    """Действующие пороги. detailed=True — с источником каждого значения."""
    if not detailed and _cache["v"] and time.time() - _cache["t"] < 30:
        return _cache["v"]
    garmin, manual = _load("thresholds_garmin"), _load("thresholds_manual")
    out, info = {}, {}
    for k, (label, unit, default) in FIELDS.items():
        if manual.get(k) is not None:
            v, src = manual[k], "вручную"
        elif garmin.get(k) is not None:
            v, src = garmin[k], "Garmin"
        else:
            v, src = default(), "по умолчанию"
        out[k] = v
        info[k] = {"value": v, "source": src, "label": label, "unit": unit, "garmin": garmin.get(k)}
    out["zones_run"] = garmin.get("zones_run") or _zones_from_lthr(out["lthr_run"])
    out["zones_bike"] = garmin.get("zones_bike") or _zones_from_lthr(out["lthr_bike"])
    if manual.get("lthr_run") is not None:  # ручной ПАНО — зоны от него
        out["zones_run"] = _zones_from_lthr(out["lthr_run"])
    if manual.get("lthr_bike") is not None:
        out["zones_bike"] = _zones_from_lthr(out["lthr_bike"])
    if detailed:
        return {"values": info, "zones_run": out["zones_run"], "zones_bike": out["zones_bike"],
                "garmin_updated": garmin.get("updated")}
    _cache.update(t=time.time(), v=out)
    return out


def _zones_from_lthr(lthr: float) -> list[int]:
    """Нижние границы Z1..Z5 по Фрилу: 0 · 85 % · 90 % · 95 % · 100 % ПАНО."""
    return [0, round(lthr * .85), round(lthr * .90), round(lthr * .95), round(lthr)]


def zone_of(hr: float, zones: list[int]) -> int:
    z = 0
    for i, floor in enumerate(zones):
        if hr >= floor:
            z = i
    return z


def lthr_for(sport: str) -> float:
    t = get()
    return t["lthr_bike"] if sport == "bike" else t["lthr_run"]


def set_manual(values: dict) -> dict:
    cur = _load("thresholds_manual")
    for k, v in values.items():
        if k not in FIELDS:
            continue
        cur[k] = None if v in (None, "") else float(v)
    _save("thresholds_manual", {k: v for k, v in cur.items() if v is not None})
    return get(detailed=True)


def update_from_garmin(g) -> dict:
    """Забрать пороги и зоны из настроек Garmin Connect."""
    out = {"updated": time.strftime("%Y-%m-%d %H:%M")}
    try:
        ud = (g.garth.connectapi("/userprofile-service/userprofile/user-settings") or {}).get("userData") or {}
        if ud.get("lactateThresholdHeartRate"):
            out["lthr_run"] = ud["lactateThresholdHeartRate"]
        if ud.get("lactateThresholdSpeed"):  # Garmin хранит в дециметрах/с·10 → м/с ×10
            ms = ud["lactateThresholdSpeed"] * 10
            out["run_pace"] = round(1000 / ms)
        if ud.get("functionalThresholdPower"):
            out["ftp"] = ud["functionalThresholdPower"]
        if ud.get("weight"):
            out["weight"] = round(ud["weight"] / 1000, 1)
    except Exception:
        pass
    try:
        for z in g.garth.connectapi("/biometric-service/heartRateZones") or []:
            floors = [0, z["zone2Floor"], z["zone3Floor"], z["zone4Floor"], z["zone5Floor"]]
            if z.get("sport") == "CYCLING":
                out["zones_bike"] = floors
                out["lthr_bike"] = z.get("lactateThresholdHeartRateUsed")
            elif z.get("sport") in ("DEFAULT", "RUNNING"):
                out["zones_run"] = floors
                out["max_hr"] = z.get("maxHeartRateUsed")
                out["rest_hr"] = z.get("restingHeartRateUsed")
                out.setdefault("lthr_run", z.get("lactateThresholdHeartRateUsed"))
    except Exception:
        pass
    _save("thresholds_garmin", {k: v for k, v in out.items() if v is not None})
    return out
