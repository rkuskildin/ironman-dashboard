"""Веб-сервер: REST API + статическая PWA-панель.

    .venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 8000
"""
import asyncio
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import auth, config, db, extras, goals, manual, race_calendar, recovery, service, sync, thresholds
from .connectors import fitbit

WEB = config.ROOT / "web"


_races_running = False


async def _refresh_races():
    global _races_running
    if _races_running:
        return
    _races_running = True
    try:
        await asyncio.to_thread(race_calendar.refresh)
    finally:
        _races_running = False


async def _background_sync():
    while True:
        await asyncio.sleep(config.SYNC_INTERVAL_MIN * 60)
        await asyncio.to_thread(sync.run)
        if race_calendar.due():  # календарь стартов — раз в сутки ночью
            asyncio.create_task(_refresh_races())


@asynccontextmanager
async def lifespan(_app):
    db.init()
    auth.init()
    extras.init()
    recovery.init()
    race_calendar.init()
    task = None
    if config.SYNC_INTERVAL_MIN > 0 and not config.DEMO:
        task = asyncio.create_task(_background_sync())
    yield
    if task:
        task.cancel()


app = FastAPI(title="Ironman Dashboard", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# Без входа доступны только страница логина и её оформление
PUBLIC = {"/login", "/api/login", "/setup", "/api/setup", "/api/invite", "/api/widget", "/styles.css", "/manifest.webmanifest", "/sw.js"}
PUBLIC_PREFIX = ("/icons/",)
# Тренер видит всё, но не меняет данные и не трогает подключения спортсмена
COACH_DENY = (("POST", "/api/tp-cookie"), ("POST", "/api/race-calendar"), ("POST", "/api/swim-fix"), ("PUT", "/api/goals"), ("PUT", "/api/thresholds"), ("PUT", "/api/race"), ("POST", "/api/weight"),
              ("POST", "/api/exclude"), ("POST", "/api/manual"), ("DELETE", "/api/manual"), ("GET", "/api/fitbit"))


@app.middleware("http")
async def require_login(request: Request, call_next):
    path = request.url.path
    if config.DEMO or path in PUBLIC or path.startswith(PUBLIC_PREFIX):
        return await call_next(request)
    user = auth.user_by_token(request.cookies.get(auth.COOKIE))
    if not user:
        if path.startswith("/api/"):
            return JSONResponse({"detail": "Нужно войти"}, status_code=401)
        return RedirectResponse("/login")
    if user["role"] == "coach" and any(request.method == m and path.startswith(p) for m, p in COACH_DENY):
        return JSONResponse({"detail": "Тренеру доступен только просмотр"}, status_code=403)
    request.state.user = user
    return await call_next(request)


class Credentials(BaseModel):
    login: str
    password: str


@app.post("/api/login")
def api_login(c: Credentials, request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0].strip()
    try:
        token = auth.login(c.login, c.password, ip)
    except PermissionError as e:
        raise HTTPException(429, str(e))
    if not token:
        raise HTTPException(401, "Неверный логин или пароль")
    resp = JSONResponse({"ok": True})
    resp.set_cookie(auth.COOKIE, token, max_age=auth.SESSION_DAYS * 86400, httponly=True,
                    secure=request.url.scheme == "https", samesite="lax", path="/")
    return resp


class Setup(BaseModel):
    token: str
    password: str


@app.post("/api/invite")
def invite_info(s: Setup):
    u = auth.invite_user(s.token)
    if not u:
        raise HTTPException(404, "Ссылка недействительна или устарела — попросите новую")
    return {"login": u["login"], "name": u["name"], "role_name": auth.ROLES.get(u["role"], u["role"])}


@app.post("/api/setup")
def setup(s: Setup, request: Request):
    try:
        token = auth.accept_invite(s.token, s.password)
    except PermissionError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    resp = JSONResponse({"ok": True})
    resp.set_cookie(auth.COOKIE, token, max_age=auth.SESSION_DAYS * 86400, httponly=True,
                    secure=request.url.scheme == "https", samesite="lax", path="/")
    return resp


@app.get("/setup")
def setup_page():
    return FileResponse(WEB / "setup.html")


@app.post("/api/logout")
def api_logout(request: Request):
    auth.logout(request.cookies.get(auth.COOKIE))
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(auth.COOKIE, path="/")
    return resp


@app.get("/api/me")
def me(request: Request):
    u = getattr(request.state, "user", None) or {"login": "demo", "name": "", "role": "athlete"}
    return {**u, "role_name": auth.ROLES.get(u["role"], u["role"])}


@app.get("/login")
def login_page(request: Request):
    if auth.user_by_token(request.cookies.get(auth.COOKIE)):
        return RedirectResponse("/")
    return FileResponse(WEB / "login.html")


@app.get("/api/overview")
def overview():
    return service.overview()


@app.get("/api/calendar")
def calendar(start: str, end: str):
    try:
        date.fromisoformat(start), date.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "Даты в формате YYYY-MM-DD")
    return service.calendar(start, end)


@app.get("/api/fitness")
def fitness(days: int = 180, forward: int = 21):
    return service.fitness(min(days, 1500), min(forward, 120))


@app.get("/api/load-breakdown")
def load_breakdown(days: int = 14):
    return service.load_breakdown(min(max(days, 7), 42))


@app.get("/api/volume")
def volume(weeks: int = 16):
    return service.volume(min(weeks, 120))


@app.get("/api/health")
def health(days: int = 60):
    return service.health(min(days, 730))


@app.get("/api/regime")
def regime(days: int = 60):
    return service.regime(min(days, 730))


@app.get("/api/goals")
def get_goals():
    return goals.summary()


@app.put("/api/goals")
def put_goals(g: dict):
    goals.set_goals(g)
    return goals.summary()


@app.get("/api/discipline/{sport}")
def discipline(sport: str):
    if sport not in goals.RACE:
        raise HTTPException(404, "Неизвестная дисциплина")
    return goals.discipline(sport)


@app.get("/api/track/{source}/{source_id}")
async def track(source: str, source_id: str):
    import json as _json
    with db.session() as c:
        row = c.execute("SELECT data FROM tracks WHERE source=? AND source_id=?", (source, source_id)).fetchone()
    if row:
        return _json.loads(row["data"])
    if source != "garmin":
        raise HTTPException(404, "Трек есть только у тренировок Garmin")
    from .connectors import garmin
    try:
        data = await asyncio.to_thread(garmin.track, source_id)
    except Exception as e:
        raise HTTPException(502, f"Garmin: {e}")
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO tracks (source, source_id, data) VALUES (?,?,?)",
                  (source, source_id, _json.dumps(data)))
    return data


def _thr_public():
    t = thresholds.get()
    return {"ftp": t["ftp"], "lthr": t["lthr_run"], "lthr_bike": t["lthr_bike"],
            "zones_run": t["zones_run"], "zones_bike": t["zones_bike"], "weight": t["weight"]}


@app.get("/api/thresholds")
def get_thresholds():
    return thresholds.get(detailed=True)


@app.put("/api/thresholds")
def put_thresholds(values: dict):
    return thresholds.set_manual(values)


@app.get("/api/race")
def get_race():
    return extras.race()


@app.put("/api/race")
def put_race(r: dict):
    try:
        return extras.set_race(r)
    except (KeyError, ValueError):
        raise HTTPException(400, "Нужны название и дата старта")


@app.get("/api/path")
def get_path():
    return extras.path()


@app.get("/api/records")
def get_records():
    return extras.records()


@app.get("/api/efficiency/{sport}")
def get_efficiency(sport: str):
    if sport not in ("run", "bike"):
        raise HTTPException(404, "Только бег и велосипед")
    return extras.efficiency(sport)


@app.get("/api/sleep-impact")
def get_sleep_impact():
    return extras.sleep_impact()


class CommentIn(BaseModel):
    key: str
    date: str
    text: str


@app.get("/api/comments")
def get_comments(start: str = "", end: str = "", recent: int = 0):
    if recent:
        return extras.recent_comments(min(recent, 50))
    return extras.comments(start, end)


@app.post("/api/comments")
def post_comment(c: CommentIn, request: Request):
    try:
        return extras.add_comment(request.state.user, c.key, c.date, c.text)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/comments/{cid}")
def del_comment(cid: int, request: Request):
    if not extras.delete_comment(request.state.user, cid):
        raise HTTPException(404, "Можно удалить только свой комментарий")
    return {"ok": True}


@app.get("/api/report")
def get_report(week: str):
    try:
        return extras.report(week)
    except ValueError:
        raise HTTPException(400, "Неделя в формате YYYY-MM-DD")


@app.get("/api/weight")
def get_weight(days: int = 365):
    return extras.weights(min(days, 1500))


@app.post("/api/weight")
def post_weight(w: dict):
    try:
        extras.add_weight(w["date"], float(w["kg"]))
    except (KeyError, ValueError) as e:
        raise HTTPException(400, str(e))
    return extras.weights()


@app.get("/api/gear")
def get_gear():
    return extras.gear()


@app.post("/api/exclude/{source}/{source_id}")
def exclude(source: str, source_id: str, body: dict):
    extras.set_excluded(source, source_id, bool(body.get("excluded", True)))
    return {"ok": True}


@app.get("/api/readiness")
def readiness():
    return recovery.today()


@app.get("/api/readiness/history")
def readiness_history(days: int = 30):
    return recovery.history(min(days, 120))


@app.get("/api/widget")
def widget(token: str = ""):
    """Сводка для виджета на рабочем столе — только чтение, по отдельному ключу (не паролю)."""
    if not auth.check_widget_token(token):
        raise HTTPException(401, "Неверный ключ виджета")
    return recovery.widget_summary()


@app.post("/api/swim-fix/{source}/{source_id}")
def swim_fix(source: str, source_id: str, body: dict):
    """Плавание: свои гребки на отрезок по стилям, ручная дистанция, «как в Garmin» или сброс."""
    from . import swim
    for style, v in (body.get("spl") or {}).items():
        if v not in (None, ""):
            swim.set_spl(float(body.get("pool_m") or 50), style, float(v))
    if body.get("keep_garmin"):
        swim.set_fix(source, source_id, keep_garmin=True)
    elif body.get("distance_m"):
        swim.set_fix(source, source_id, distance_m=float(body["distance_m"]))
    else:
        swim.set_fix(source, source_id, clear=True)
    return {"ok": True}


@app.post("/api/tp-cookie")
async def tp_cookie(body: dict):
    from .connectors import trainingpeaks
    v = (body.get("cookie") or "").strip()
    if len(v) < 20:
        raise HTTPException(400, "Похоже, это не cookie — скопируйте значение Production_tpAuth целиком")
    trainingpeaks.set_cookie(v)
    res = await asyncio.to_thread(sync.run, ["tp"])
    return res[0] if res else {"ok": False, "message": "не запустилось"}


@app.get("/api/race-calendar")
def race_cal():
    return {**race_calendar.list_events(), "refreshing": _races_running}


@app.post("/api/race-calendar/mark/{eid}")
def race_mark(eid: str):
    return {"marked": race_calendar.toggle_mark(eid)}


@app.post("/api/race-calendar/refresh")
async def race_refresh():
    asyncio.create_task(_refresh_races())
    return {"started": True}


@app.get("/api/status")
def status(request: Request):
    if getattr(request.state, "user", {}).get("role") == "coach":
        return {"demo": False, "configured": {}, "log": [], "race": extras.race(),
                "thresholds": _thr_public(), "recovery_source": config.RECOVERY_SOURCE}
    with db.session() as c:
        log = [dict(r) for r in c.execute("SELECT * FROM sync_log ORDER BY id DESC LIMIT 20")]
    return {"demo": config.DEMO, "configured": sync.configured(), "log": log,
            "race": extras.race(),
            "thresholds": _thr_public(),
            "recovery_source": config.RECOVERY_SOURCE}


@app.post("/api/sync")
async def run_sync():
    if config.DEMO:
        return [{"source": "demo", "ok": True, "message": "Демо-режим: синхронизация отключена"}]
    return await asyncio.to_thread(sync.run)


class ManualWorkout(BaseModel):
    date: str
    start: str
    end: str
    sport: str = "hockey"
    title: str = ""
    note: str = ""


@app.post("/api/manual")
async def add_manual(w: ManualWorkout):
    try:
        date.fromisoformat(w.date)
        return await asyncio.to_thread(manual.add, w.date, w.start, w.end, w.sport, w.title, w.note)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(400, str(e))


@app.delete("/api/manual/{source_id}")
def delete_manual(source_id: str):
    manual.delete(source_id)
    return {"ok": True}


@app.get("/api/fitbit/login")
def fitbit_login():
    try:
        return RedirectResponse(fitbit.auth_url())
    except RuntimeError as e:
        raise HTTPException(400, str(e))


@app.get("/api/fitbit/callback")
def fitbit_callback(code: str = "", state: str = "", error: str = ""):
    if error or not code:
        raise HTTPException(400, f"Fitbit отказал в доступе: {error}")
    fitbit.handle_callback(code, state)
    sync.run(["fitbit"])
    return RedirectResponse("/#settings")


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/", StaticFiles(directory=WEB), name="web")
