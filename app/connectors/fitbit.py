"""Fitbit через Google Health API (health.googleapis.com/v4) — сон, HRV, пульс покоя.

Старый Fitbit Web API закрывается осенью 2026, регистрация новых приложений в нём
прекращена. Настройка (один раз):
  1. console.cloud.google.com → новый проект → APIs & Services → Library → «Google Health API» → Enable.
  2. OAuth consent screen: тип External, добавьте свой Google-аккаунт в Test users.
  3. Credentials → Create credentials → OAuth client ID → Web application,
     Authorized redirect URI = GOOGLE_HEALTH_REDIRECT_URI (по умолчанию http://localhost:8000/api/fitbit/callback).
  4. Client ID / Secret → .env, затем «Подключить» во вкладке «Источники».
"""
import json
import secrets
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

import httpx

from .. import config, db
from ..metrics import normalize_sport

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://health.googleapis.com/v4/users/me/dataTypes"
SCOPES = " ".join("https://www.googleapis.com/auth/googlehealth." + s for s in (
    "sleep.readonly", "health_metrics_and_measurements.readonly", "activity_and_fitness.readonly"))

_pending: set[str] = set()


def auth_url() -> str:
    if not config.GOOGLE_HEALTH_CLIENT_ID:
        raise RuntimeError("GOOGLE_HEALTH_CLIENT_ID не задан в .env")
    state = secrets.token_urlsafe(16)
    _pending.add(state)
    return AUTH_URL + "?" + urlencode({
        "client_id": config.GOOGLE_HEALTH_CLIENT_ID, "response_type": "code", "scope": SCOPES,
        "redirect_uri": config.GOOGLE_HEALTH_REDIRECT_URI, "state": state,
        "access_type": "offline", "prompt": "consent",
    })


def _token_request(data: dict) -> dict:
    r = httpx.post(TOKEN_URL, data={"client_id": config.GOOGLE_HEALTH_CLIENT_ID,
                                    "client_secret": config.GOOGLE_HEALTH_CLIENT_SECRET, **data}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Google OAuth: {r.text[:200]}")
    tok = r.json()
    old = json.loads(config.FITBIT_TOKEN_FILE.read_text()) if config.FITBIT_TOKEN_FILE.exists() else {}
    tok.setdefault("refresh_token", old.get("refresh_token"))  # при обновлении Google его не присылает
    tok["expires_at"] = time.time() + tok.get("expires_in", 3600) - 60
    config.FITBIT_TOKEN_FILE.write_text(json.dumps(tok))
    config.FITBIT_TOKEN_FILE.chmod(0o600)
    return tok


def handle_callback(code: str, state: str):
    if state not in _pending:
        raise RuntimeError("Неизвестный state — начните подключение заново")
    _pending.discard(state)
    _token_request({"grant_type": "authorization_code", "code": code,
                    "redirect_uri": config.GOOGLE_HEALTH_REDIRECT_URI})


def connected() -> bool:
    return config.FITBIT_TOKEN_FILE.exists()


def _token() -> str:
    if not connected():
        raise RuntimeError("Fitbit не подключён — нажмите «Подключить» во вкладке «Источники»")
    tok = json.loads(config.FITBIT_TOKEN_FILE.read_text())
    if time.time() > tok.get("expires_at", 0):
        if not tok.get("refresh_token"):
            raise RuntimeError("Сессия Google истекла — подключите Fitbit заново")
        tok = _token_request({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
    return tok["access_token"]


def _list(data_type: str, flt: str, page_size: int = 1000) -> list[dict]:
    out, page = [], None
    while True:
        params = {"filter": flt, "pageSize": 25 if data_type == "sleep" else page_size}
        if page:
            params["pageToken"] = page
        for attempt in range(4):  # Google иногда отвечает 500/503/429 — повторяем с паузой
            r = httpx.get(f"{API}/{data_type}/dataPoints", params=params,
                          headers={"Authorization": f"Bearer {_token()}"}, timeout=60)
            if r.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(2 * (attempt + 1))
        if r.status_code != 200:
            raise RuntimeError(f"{data_type}: HTTP {r.status_code} {r.text[:200]}")
        body = r.json()
        out += body.get("dataPoints", [])
        page = body.get("nextPageToken")
        if not page:
            return out


def _d(obj: dict | None) -> str | None:
    if not obj:
        return None
    return f"{obj['year']:04d}-{obj['month']:02d}-{obj['day']:02d}"


def _wake_date(iv: dict) -> str | None:
    """Дата пробуждения по местному времени: civilEndTime, а если его нет — endTime + endUtcOffset."""
    civil = _d((iv.get("civilEndTime") or {}).get("date"))
    if civil or not iv.get("endTime"):
        return civil
    end = datetime.fromisoformat(iv["endTime"].replace("Z", "+00:00"))
    offset = float(str(iv.get("endUtcOffset", "0s")).rstrip("s") or 0)
    return (end + timedelta(seconds=offset)).date().isoformat()


def _msk(ts: str | None) -> str | None:
    """UTC-время → 'YYYY-MM-DD HH:MM' в поясе режима (по умолчанию Москва)."""
    if not ts:
        return None
    t = datetime.fromisoformat(ts.replace("Z", "+00:00")) + timedelta(hours=config.BEDTIME_TZ)
    return t.strftime("%Y-%m-%d %H:%M")


def _num(v):
    return float(v) if v not in (None, "") else None


def sync(days_back: int) -> str:
    start = (date.today() - timedelta(days=days_back)).isoformat()
    end = (date.today() + timedelta(days=1)).isoformat()
    rows: dict[str, dict] = {}

    def row(d):
        return rows.setdefault(d, {"date": d, "source": "fitbit"})

    for p in _list("sleep", f'sleep.interval.civil_end_time >= "{start}" AND sleep.interval.civil_end_time < "{end}"'):
        if (p.get("dataSource") or {}).get("platform") == "HEALTH_CONNECT":
            continue  # копии ночей из других приложений (Garmin через Health Connect) — Garmin берём напрямую
        s = p.get("sleep") or {}
        summ = s.get("summary") or {}
        iv = s.get("interval") or {}
        d = _wake_date(iv)
        asleep = _num(summ.get("minutesAsleep"))
        if not d or not asleep:
            continue
        r = row(d)
        if asleep * 60 <= (r.get("sleep_s") or 0):  # берём основной (самый длинный) сон за ночь
            continue
        stages = {st.get("type", ""): _num(st.get("minutes")) or 0 for st in summ.get("stagesSummary", [])}
        in_period = _num(summ.get("minutesInSleepPeriod"))
        r.update(bed_time=_msk(iv.get("startTime")), wake_time=_msk(iv.get("endTime")),
                 sleep_s=asleep * 60,
                 deep_s=(stages.get("DEEP") or 0) * 60 or None,
                 rem_s=(stages.get("REM") or 0) * 60 or None,
                 sleep_score=round(asleep / in_period * 100) if in_period else None)  # эффективность сна

    for p in _list("daily-heart-rate-variability", f'daily_heart_rate_variability.date >= "{start}"'):
        h = p.get("dailyHeartRateVariability") or {}
        if _d(h.get("date")):
            row(_d(h["date"]))["hrv"] = _num(h.get("averageHeartRateVariabilityMilliseconds")) \
                or _num(h.get("deepSleepRootMeanSquareOfSuccessiveDifferencesMilliseconds"))

    for p in _list("daily-resting-heart-rate", f'daily_resting_heart_rate.date >= "{start}"'):
        h = p.get("dailyRestingHeartRate") or {}
        if _d(h.get("date")):
            row(_d(h["date"]))["resting_hr"] = _num(h.get("beatsPerMinute"))

    with db.session() as c:
        for r in rows.values():
            db.upsert_health(c, r)
    n = workout_heart_rate(days_back)
    try:
        hrd = sync_day_minutes()
    except Exception as e:  # пульс за день — не критично для остального
        hrd = f"ошибка {type(e).__name__}"
    try:
        ex = sync_exercises(days_back)
    except RuntimeError as e:
        if "MISSING_OAUTH_SCOPE" not in str(e) and "403" not in str(e):
            raise
        ex = "нет доступа к тренировкам — переподключите Fitbit"
    return f"Fitbit (Google Health): здоровье за {len(rows)} дн., пульс на {n} тренировках, тренировки: {ex}, пульс за день: {hrd}"


def fetch_day_minutes(day: str) -> list:
    """Поминутный пульс за местные сутки (1440 значений, None — нет данных)."""
    d0 = datetime.fromisoformat(day) - timedelta(hours=config.BEDTIME_TZ)
    d1 = d0 + timedelta(days=1)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    pts = _list("heart-rate", f'heart_rate.sample_time.physical_time >= "{d0.strftime(fmt)}" AND '
                              f'heart_rate.sample_time.physical_time < "{d1.strftime(fmt)}"', page_size=10000)
    sums, cnt = [0.0] * 1440, [0] * 1440
    for p in pts:
        hr = p.get("heartRate") or {}
        t = datetime.fromisoformat(hr["sampleTime"]["physicalTime"].replace("Z", "")) + timedelta(hours=config.BEDTIME_TZ)
        if t.date().isoformat() != day:
            continue
        i = t.hour * 60 + t.minute
        sums[i] += float(hr["beatsPerMinute"])
        cnt[i] += 1
    return [round(sums[i] / cnt[i]) if cnt[i] else None for i in range(1440)]


def sync_day_minutes(backfill_days: int = 30, max_days: int = 4) -> str:
    """Сегодня — всегда; прошлые незавершённые дни — до max_days за раз (история догружается постепенно)."""
    from .. import recovery
    today = date.today().isoformat()
    todo = [d for d in recovery.days_needing_fetch(backfill_days) if d != today]
    todo = sorted(todo, reverse=True)[:max_days] + [today]
    done, failed = 0, 0
    for d in todo:
        try:
            m = fetch_day_minutes(d)
        except Exception:
            failed += 1
            continue
        # день полный, если прошёл и пульс есть хотя бы за 60 % минут (иначе браслет ещё не всё передал)
        cover = sum(1 for v in m if v) / 1440
        age = (date.today() - date.fromisoformat(d)).days
        recovery.store_day(d, m, "fitbit", complete=d < today and (cover >= 0.6 or age >= 3))
        done += 1
    return f"{done} дн." + (f", сбой {failed}" if failed else "")


EXERCISE_RU = {"HOCKEY": "Хоккей", "FOOTBALL": "Футбол", "SOCCER": "Футбол", "TREADMILL": "Беговая дорожка",
               "EXERCISE_BIKE": "Велотренажёр", "AEROBICS": "Аэробика", "AEROBIC_WORKOUT": "Аэробика", "ICE_SKATING": "Коньки", "WALKING": "Ходьба", "RUNNING": "Бег",
               "BIKING": "Велосипед", "SWIMMING": "Плавание", "WEIGHTLIFTING": "Силовая", "YOGA": "Йога",
               "HIKING": "Поход", "SPORT": "Спорт"}


def _secs(v) -> float | None:
    return float(str(v).rstrip("s")) if v not in (None, "") else None


def sync_exercises(days_back: int) -> int:
    """Тренировки, записанные Fitbit (в т.ч. автоопределённые) — хоккей, ходьба и т.п."""
    start = (date.today() - timedelta(days=days_back)).isoformat()
    pts = _list("exercise", f'exercise.interval.civil_start_time >= "{start}"')
    with db.session() as c:
        for p in pts:
            e = p.get("exercise") or {}
            iv = e.get("interval") or {}
            if not iv.get("startTime"):
                continue
            t0 = datetime.fromisoformat(iv["startTime"].replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(iv["endTime"].replace("Z", "+00:00"))
            off = timedelta(seconds=_secs(iv.get("startUtcOffset")) or 0)
            local = (t0 + off).replace(tzinfo=None)
            m = e.get("metricsSummary") or {}
            z = m.get("heartRateZoneDurations") or {}
            etype = e.get("exerciseType", "")
            dur = _secs(e.get("activeDuration")) or (t1 - t0).total_seconds()
            db.upsert(c, "activities", {
                "source": "fitbit", "source_id": p.get("name", "").rsplit("/", 1)[-1] or iv["startTime"],
                "date": local.date().isoformat(), "start_time": local.strftime("%Y-%m-%d %H:%M:%S"),
                "start_gmt": t0.strftime("%Y-%m-%d %H:%M:%S"),
                "sport": normalize_sport(etype) if etype not in ("WALKING", "HIKING") else "other",
                "title": EXERCISE_RU.get(etype) or e.get("displayName") or etype.title(),
                "duration_s": dur,
                "distance_m": (_num(m.get("distanceMillimeters")) or 0) / 1000 or None,
                "elevation_m": (_num(m.get("elevationGainMillimeters")) or 0) / 1000 or None,
                "avg_hr": _num(m.get("averageHeartRateBeatsPerMinute")),
                "calories": _num(m.get("caloriesKcal")),
                "athlete_comments": e.get("notes"),
                "analysis": json.dumps({
                    "fitbit_zones": [_secs(z.get(k)) or 0 for k in ("lightTime", "moderateTime", "vigorousTime", "peakTime")],
                    "azm": _num(m.get("activeZoneMinutes")),
                    "exercise_type": etype,
                }),
            })
    return len(pts)


def workout_heart_rate(days_back: int) -> int:
    """Средний/максимальный пульс Fitbit на время каждой тренировки Garmin."""
    since = (date.today() - timedelta(days=days_back)).isoformat()
    with db.session() as c:
        acts = [dict(r) for r in c.execute(
            "SELECT source_id, start_gmt, duration_s FROM activities WHERE source='garmin' AND date >= ? "
            "AND start_gmt IS NOT NULL AND duration_s > 0 AND fitbit_avg_hr IS NULL", (since,))]
    done = 0
    for a in acts:
        start = datetime.fromisoformat(a["start_gmt"].replace(" ", "T")).replace(tzinfo=None)
        end = start + timedelta(seconds=a["duration_s"])
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        pts = _list("heart-rate", f'heart_rate.sample_time.physical_time >= "{start.strftime(fmt)}" AND '
                                  f'heart_rate.sample_time.physical_time < "{end.strftime(fmt)}"', page_size=10000)
        bpm = [float(p["heartRate"]["beatsPerMinute"]) for p in pts if p.get("heartRate")]
        # нужны данные хотя бы за половину тренировки (≈ 1 замер на 5 с)
        if len(bpm) < a["duration_s"] / 10:
            continue
        with db.session() as c:
            c.execute("UPDATE activities SET fitbit_avg_hr=?, fitbit_max_hr=? WHERE source='garmin' AND source_id=?",
                      (round(sum(bpm) / len(bpm)), max(bpm), a["source_id"]))
        done += 1
    return done
