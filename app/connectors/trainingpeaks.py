"""TrainingPeaks: план тренера (iCal) и полные данные через веб-API по cookie сессии.

Официальный API TrainingPeaks открыт только для партнёров, поэтому:
  * iCal — стабильный, но содержит только план (название, описание, иногда длительность/TSS);
  * веб-API (tpapi.trainingpeaks.com) — то же, что использует сайт TP: план, факт,
    комментарии тренера, TSS, CTL/ATL/TSB. Неофициальный, может сломаться.
"""
import re
from datetime import date, datetime, timedelta

import httpx
from icalendar import Calendar

from .. import config, db
from ..metrics import TP_SPORT, normalize_sport

TP_API = "https://tpapi.trainingpeaks.com"


# ---------- iCal ----------

def _parse_duration(text: str) -> float | None:
    m = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?", text)
    if m:
        h, mi, s = int(m[1]), int(m[2]), int(m[3] or 0)
        return h * 3600 + mi * 60 + s
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(h|ч|hr|hours?)\b", text, re.I)
    if m:
        return float(m[1].replace(",", ".")) * 3600
    m = re.search(r"(\d+)\s*(min|мин)", text, re.I)
    return int(m[1]) * 60 if m else None


def sync_ical(url: str = "") -> str:
    url = url or config.TP_ICAL_URL
    if not url:
        raise RuntimeError("TP_ICAL_URL не задан в .env")
    url = url.replace("webcal://", "https://")
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    cal = Calendar.from_ical(resp.content)
    n = 0
    with db.session() as c:
        for ev in cal.walk("VEVENT"):
            start = ev.decoded("DTSTART")
            d = start.date() if isinstance(start, datetime) else start
            summary = str(ev.get("SUMMARY", ""))
            desc = str(ev.get("DESCRIPTION", ""))
            sport_part = summary.split(":", 1)[0] if ":" in summary else summary
            tss = re.search(r"TSS[^\d]{0,5}(\d+(?:\.\d+)?)", desc, re.I)
            dist = re.search(r"(\d+(?:[.,]\d+)?)\s*(km|км)\b", desc, re.I)
            db.upsert(c, "planned_workouts", {
                "source": "tp_ical",
                "source_id": str(ev.get("UID", f"{d}-{summary}")),
                "date": d.isoformat(),
                "sport": normalize_sport(sport_part) if ":" in summary else normalize_sport(summary),
                "title": summary.split(":", 1)[-1].strip() or summary,
                "description": desc,
                "coach_comments": None,
                "duration_s": _parse_duration(desc),
                "distance_m": float(dist[1].replace(",", ".")) * 1000 if dist else None,
                "tss": float(tss[1]) if tss else None,
            })
            n += 1
    return f"iCal: {n} плановых тренировок"


# ---------- веб-API ----------

class TPClient:
    def __init__(self, auth_cookie: str):
        self.http = httpx.Client(base_url=TP_API, timeout=30)
        r = self.http.get("/users/v3/token", cookies={"Production_tpAuth": auth_cookie})
        if r.status_code != 200:
            raise RuntimeError("TrainingPeaks не принял cookie — войдите на сайт заново и обновите TP_AUTH_COOKIE")
        token = r.json()["token"]["access_token"]
        self.http.headers["Authorization"] = f"Bearer {token}"
        self.athlete_id = self.http.get("/users/v3/user").json()["user"]["userId"]

    def workouts(self, start: date, end: date) -> list[dict]:
        out, a = [], start
        while a <= end:  # TP отдаёт ограниченный диапазон — идём окнами по 60 дней
            b = min(a + timedelta(days=59), end)
            r = self.http.get(f"/fitness/v6/athletes/{self.athlete_id}/workouts/{a}/{b}")
            r.raise_for_status()
            out += r.json()
            a = b + timedelta(days=1)
        return out

    def performance(self, start: date, end: date) -> list[dict]:
        body = {"atlConstant": 7, "atlStart": 0, "ctlConstant": 42, "ctlStart": 0, "workoutTypes": []}
        r = self.http.post(f"/fitness/v1/athletes/{self.athlete_id}/reporting/performancedata/{start}/{end}",
                           json=body)
        r.raise_for_status()
        return r.json()


def _h(v):
    return v * 3600 if v else None


def sync_api(days_back: int, days_forward: int) -> str:
    if not config.TP_AUTH_COOKIE:
        raise RuntimeError("TP_AUTH_COOKIE не задан в .env")
    tp = TPClient(config.TP_AUTH_COOKIE)
    start = date.today() - timedelta(days=days_back)
    end = date.today() + timedelta(days=days_forward)
    plans = acts = 0
    with db.session() as c:
        for w in tp.workouts(start, end):
            d = (w.get("workoutDay") or "")[:10]
            sport = TP_SPORT.get(w.get("workoutTypeValueId"), "other")
            wid = str(w["workoutId"])
            if w.get("totalTimePlanned") or w.get("tssPlanned") or w.get("distancePlanned") or sport == "rest":
                db.upsert(c, "planned_workouts", {
                    "source": "tp", "source_id": wid, "date": d, "sport": sport,
                    "title": w.get("title"), "description": w.get("description"),
                    "coach_comments": w.get("coachComments"),
                    "duration_s": _h(w.get("totalTimePlanned")),
                    "distance_m": w.get("distancePlanned"), "tss": w.get("tssPlanned"),
                })
                plans += 1
            if w.get("totalTime"):
                db.upsert(c, "activities", {
                    "source": "tp", "source_id": wid, "date": d,
                    "start_time": w.get("startTime"), "sport": sport, "title": w.get("title"),
                    "duration_s": _h(w.get("totalTime")), "distance_m": w.get("distance"),
                    "elevation_m": w.get("elevationGain"), "avg_hr": w.get("heartRateAverage"),
                    "max_hr": w.get("heartRateMaximum"), "avg_power": w.get("powerAverage"),
                    "np": w.get("normalizedPowerActual"), "tss": w.get("tssActual"),
                    "calories": w.get("calories"), "athlete_comments": w.get("athleteComments"),
                })
                acts += 1
        msg = f"TP API: план {plans}, факт {acts}"
        try:
            perf = tp.performance(date.today() - timedelta(days=365), date.today() + timedelta(days=days_forward))
            for p in perf:
                db.upsert(c, "fitness_daily", {"date": p["workoutDay"][:10], "ctl": p.get("ctl"),
                                               "atl": p.get("atl"), "tsb": p.get("tsb")})
            msg += f", форма {len(perf)} дн."
        except Exception as e:  # отчёт по форме необязателен — считаем сами
            msg += f" (форму посчитаем локально: {e.__class__.__name__})"
    return msg
