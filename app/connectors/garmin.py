"""Garmin Connect через библиотеку garminconnect (неофициальная).

Первый вход: `python -m app.sync garmin-login` — спросит код MFA, если он включён,
и сохранит токены в data/garmin_tokens. Дальше пароль не нужен.
"""
import json
from datetime import date, datetime, timedelta, timezone

from garminconnect import Garmin

from .. import config, db
from ..metrics import normalize_sport


def login(interactive: bool = False) -> Garmin:
    tokens = config.GARMIN_TOKEN_DIR
    if tokens.exists():
        g = Garmin()
        g.login(str(tokens))
        return g
    if not (config.GARMIN_EMAIL and config.GARMIN_PASSWORD):
        raise RuntimeError("Нет токенов Garmin: заполните GARMIN_EMAIL/GARMIN_PASSWORD и выполните "
                           "`python -m app.sync garmin-login`")
    prompt = (lambda: input("Код MFA Garmin: ")) if interactive else None
    g = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD, prompt_mfa=prompt)
    g.login()
    g.garth.dump(str(tokens))
    return g


def _ms_to_local(ms) -> str | None:
    if not ms:
        return None
    t = datetime.fromtimestamp(ms / 1000, timezone.utc) + timedelta(hours=config.BEDTIME_TZ)
    return t.strftime("%Y-%m-%d %H:%M")


def _safe(fn, *a):
    try:
        return fn(*a) or {}
    except Exception:
        return {}


def _analysis(a: dict) -> dict:
    """Разбор тренировки от Garmin: Training Effect, нагрузка, зоны, VO2 max."""
    return {
        "aerobic_te": a.get("aerobicTrainingEffect"),
        "anaerobic_te": a.get("anaerobicTrainingEffect"),
        "te_label": a.get("trainingEffectLabel"),
        "aerobic_msg": a.get("aerobicTrainingEffectMessage"),
        "anaerobic_msg": a.get("anaerobicTrainingEffectMessage"),
        "training_load": a.get("activityTrainingLoad"),
        "vo2max": a.get("vO2MaxValue"),
        "body_battery_diff": a.get("differenceBodyBattery"),
        "moderate_min": a.get("moderateIntensityMinutes"),
        "vigorous_min": a.get("vigorousIntensityMinutes"),
        "hr_zones": [a.get(f"hrTimeInZone_{i}") or 0 for i in range(1, 6)],
        "power_zones": [a.get(f"powerTimeInZone_{i}") or 0 for i in range(1, 6)] if a.get("powerTimeInZone_1") is not None else None,
    }


def _status_snapshot(g, ds: str) -> dict:
    """Общая тренированность на дату: статус, баланс нагрузки, VO2 max, выносливость, прогнозы."""
    out = {}
    ts = _safe(g.get_training_status, ds)
    devs = ((ts.get("mostRecentTrainingStatus") or {}).get("latestTrainingStatusData") or {})
    st = next(iter(devs.values()), {}) if devs else {}
    acwr = st.get("acuteTrainingLoadDTO") or {}
    out["status_phrase"] = st.get("trainingStatusFeedbackPhrase")
    out["acute_load"] = acwr.get("dailyTrainingLoadAcute")
    out["chronic_load"] = acwr.get("dailyTrainingLoadChronic")
    out["chronic_min"], out["chronic_max"] = acwr.get("minTrainingLoadChronic"), acwr.get("maxTrainingLoadChronic")
    out["acwr"] = acwr.get("dailyAcuteChronicWorkloadRatio")
    out["acwr_status"] = acwr.get("acwrStatus")
    bal = ((ts.get("mostRecentTrainingLoadBalance") or {}).get("metricsTrainingLoadBalanceDTOMap") or {})
    b = next(iter(bal.values()), {}) if bal else {}
    out["balance"] = {k: [b.get(f"monthlyLoad{k}"), b.get(f"monthlyLoad{k}TargetMin"), b.get(f"monthlyLoad{k}TargetMax")]
                      for k in ("AerobicLow", "AerobicHigh", "Anaerobic")} if b else None
    out["balance_phrase"] = b.get("trainingBalanceFeedbackPhrase")
    vo2 = ts.get("mostRecentVO2Max") or {}
    out["vo2max"] = (vo2.get("generic") or {}).get("vo2MaxPreciseValue")
    out["vo2max_cycling"] = (vo2.get("cycling") or {}).get("vo2MaxPreciseValue")
    heat = vo2.get("heatAltitudeAcclimation") or {}
    out["heat_acclimation"] = heat.get("heatAcclimationPercentage")
    end = _safe(g.get_endurance_score, ds)
    out["endurance_score"], out["endurance_class"] = end.get("overallScore"), end.get("classification")
    rp = _safe(g.get_race_predictions)
    out["race"] = {k: rp.get(k) for k in ("time5K", "time10K", "timeHalfMarathon", "timeMarathon")} if rp else None
    return out


def sync_activities(g, start: date) -> int:
    acts = g.get_activities_by_date(start.isoformat(), date.today().isoformat())
    with db.session() as c:
        for a in acts:
            st = a.get("startTimeLocal") or ""
            sid = str(a["activityId"])
            prev = c.execute("SELECT fitbit_avg_hr, fitbit_max_hr, kind FROM activities WHERE source='garmin' AND source_id=?",
                             (sid,)).fetchone()
            db.upsert(c, "activities", {
                "source": "garmin", "source_id": sid, "date": st[:10],
                "start_time": st, "start_gmt": a.get("startTimeGMT"),
                "fitbit_avg_hr": prev["fitbit_avg_hr"] if prev else None,
                "fitbit_max_hr": prev["fitbit_max_hr"] if prev else None,
                "sport": normalize_sport((a.get("activityType") or {}).get("typeKey")),
                "title": a.get("activityName"), "duration_s": a.get("duration"),
                "moving_s": a.get("movingDuration"),
                "has_gps": 1 if a.get("hasPolyline") else 0,
                "distance_m": a.get("distance"), "elevation_m": a.get("elevationGain"),
                "avg_hr": a.get("averageHR"), "max_hr": a.get("maxHR"),
                "avg_power": a.get("avgPower"), "np": a.get("normPower"),
                "tss": a.get("trainingStressScore"), "calories": a.get("calories"),
                "athlete_comments": a.get("description"),
                "analysis": json.dumps(_analysis(a)),
                "kind": prev["kind"] if prev else None,
            })
    # мультиспорт (триатлон): забираем этапы — плавание, переходы, вело, бег
    for a in acts:
        if (a.get("activityType") or {}).get("typeKey") in ("multi_sport", "multisport") or a.get("parent"):
            try:
                _sync_children(g, a)
            except Exception:
                pass
    return len(acts)


def _sync_children(g, parent: dict):
    pid = str(parent["activityId"])
    with db.session() as c:
        c.execute("UPDATE activities SET kind='multisport_parent' WHERE source='garmin' AND source_id=?", (pid,))
        have = {r[0] for r in c.execute("SELECT source_id FROM activities WHERE source='garmin' AND parent_id=?", (pid,))}
    md = (g.get_activity(pid) or {}).get("metadataDTO") or {}
    for cid in md.get("childIds") or []:
        cid = str(cid)
        if cid in have:
            continue
        d = g.get_activity(cid) or {}
        sm = d.get("summaryDTO") or {}
        key = (d.get("activityTypeDTO") or {}).get("typeKey") or ""
        sport = normalize_sport(key)
        st = (sm.get("startTimeLocal") or "").replace("T", " ")[:19]
        an = {
            "aerobic_te": sm.get("trainingEffect"), "anaerobic_te": sm.get("anaerobicTrainingEffect"),
            "te_label": sm.get("trainingEffectLabel"), "aerobic_msg": sm.get("aerobicTrainingEffectMessage"),
            "anaerobic_msg": sm.get("anaerobicTrainingEffectMessage"), "training_load": sm.get("activityTrainingLoad"),
            "body_battery_diff": sm.get("differenceBodyBattery"),
        }
        with db.session() as c:
            db.upsert(c, "activities", {
                "source": "garmin", "source_id": cid, "date": st[:10], "start_time": st,
                "start_gmt": (sm.get("startTimeGMT") or "").replace("T", " ")[:19] or None,
                "sport": sport, "title": d.get("activityName") or parent.get("activityName"),
                "duration_s": sm.get("duration"), "moving_s": sm.get("movingDuration"),
                "distance_m": sm.get("distance"), "elevation_m": sm.get("elevationGain"),
                "avg_hr": sm.get("averageHR"), "max_hr": sm.get("maxHR"),
                "avg_power": sm.get("averagePower"), "np": sm.get("normalizedPower"),
                "tss": sm.get("trainingStressScore"), "calories": sm.get("calories"),
                "has_gps": 1 if parent.get("hasPolyline") and sport in ("swim", "bike", "run") else 0,
                "parent_id": pid, "kind": "leg", "analysis": json.dumps(an),
            })


def sync(days_back: int) -> str:
    g = login()
    start = date.today() - timedelta(days=days_back)
    n = sync_activities(g, start)
    with db.session() as c:

        d = start
        while d <= date.today():
            ds = d.isoformat()
            stats = _safe(g.get_stats, ds)
            sleep = _safe(g.get_sleep_data, ds).get("dailySleepDTO") or {}
            hrv = _safe(g.get_hrv_data, ds).get("hrvSummary") or {}
            ready = _safe(g.get_training_readiness, ds)
            if isinstance(ready, list):
                ready = ready[0] if ready else {}
            db.upsert_health(c, {
                "date": ds, "source": "garmin",
                "resting_hr": stats.get("restingHeartRate"),
                "steps": stats.get("totalSteps"),
                "body_battery": stats.get("bodyBatteryHighestValue"),
                "stress": stats.get("averageStressLevel"),
                "bed_time": _ms_to_local(sleep.get("sleepStartTimestampGMT")),
                "wake_time": _ms_to_local(sleep.get("sleepEndTimestampGMT")),
                "sleep_s": sleep.get("sleepTimeSeconds"),
                "deep_s": sleep.get("deepSleepSeconds"),
                "rem_s": sleep.get("remSleepSeconds"),
                "sleep_score": ((sleep.get("sleepScores") or {}).get("overall") or {}).get("value"),
                "hrv": hrv.get("lastNightAvg"),
                "readiness": ready.get("score"),
            })
            d += timedelta(days=1)
        # статус за сегодня Garmin считает в течение дня — если пусто, берём вчерашний
        for back in (0, 1):
            ds = (date.today() - timedelta(days=back)).isoformat()
            snap = _status_snapshot(g, ds)
            if snap.get("vo2max") or snap.get("acute_load"):
                c.execute("INSERT OR REPLACE INTO garmin_status (date, data) VALUES (?, ?)", (ds, json.dumps(snap)))
                break
    from .. import recovery, thresholds
    for back in (0, 1):  # пульс часов за сегодня и вчера — запасной источник для нагрузки дня
        dd = (date.today() - timedelta(days=back)).isoformat()
        try:
            recovery.store_day(dd, recovery.garmin_day_minutes(g, dd), "garmin", complete=back > 0)
        except Exception:
            pass
    thresholds.update_from_garmin(g)
    from .. import extras
    extras.update_gear(g)
    t = cache_tracks(g)
    return f"Garmin: {n} активностей, здоровье за {days_back + 1} дн., тренированность" + (f", карт: {t}" if t else "")


def cache_tracks(g=None) -> int:
    """Скачать заранее GPS-треки всех тренировок, которых ещё нет в кэше — чтобы карты открывались сразу."""
    with db.session() as c:
        ids = [r[0] for r in c.execute(
            "SELECT a.source_id FROM activities a LEFT JOIN tracks t ON t.source='garmin' AND t.source_id=a.source_id "
            "WHERE a.source='garmin' AND a.has_gps=1 AND t.source_id IS NULL")]
    if not ids:
        return 0
    g = g or login()
    n = 0
    for aid in ids:
        try:
            data = track(aid, g=g)
        except Exception:
            continue
        with db.session() as c:
            c.execute("INSERT OR REPLACE INTO tracks (source, source_id, data) VALUES ('garmin', ?, ?)", (aid, json.dumps(data)))
        n += 1
    return n


def track(activity_id: str, max_points: int = 900, g=None) -> dict:
    """GPS-трек тренировки: [lat, lon, пульс, скорость м/с, высота, дистанция м], прореженный до max_points."""
    g = g or login()
    d = g.get_activity_details(activity_id, maxchart=4000, maxpoly=4000)
    keys = [m["key"] for m in sorted(d.get("metricDescriptors") or [], key=lambda m: m["metricsIndex"])]
    idx = {k: i for i, k in enumerate(keys)}

    def col(row, k):
        i = idx.get(k)
        return row[i] if i is not None and i < len(row) else None

    pts = []
    for r in d.get("activityDetailMetrics") or []:
        m = r.get("metrics") or []
        lat, lon = col(m, "directLatitude"), col(m, "directLongitude")
        if lat is None or lon is None:
            continue
        pts.append([round(lat, 6), round(lon, 6), col(m, "directHeartRate"), col(m, "directSpeed"),
                    col(m, "directElevation"), col(m, "sumDistance")])
    if not pts:  # у некоторых записей координаты только в полилинии
        for q in (d.get("geoPolylineDTO") or {}).get("polyline") or []:
            if q.get("lat") is not None:
                pts.append([round(q["lat"], 6), round(q["lon"], 6), None, q.get("speed"), q.get("altitude"), None])
    step = max(1, len(pts) // max_points)
    pts = pts[::step]
    return {"points": pts}
