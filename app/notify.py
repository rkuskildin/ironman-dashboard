"""Push-уведомления на телефон (Web Push, без сторонних мессенджеров).

Тренеру — когда появилась новая тренировка спортсмена; спортсмену — когда тренер оценил
тренировку; обоим — о новом комментарии другой стороны. Ключи VAPID создаются один раз
и лежат в data/vapid_private.pem.
"""
import base64
import json
import logging
from datetime import date, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from . import config, db

log = logging.getLogger(__name__)
KEY_FILE = config.DB_PATH.parent / "vapid_private.pem"
CONTACT = "mailto:noreply@ironman.local"

SCHEMA = """
CREATE TABLE IF NOT EXISTS push_subs (
    endpoint TEXT PRIMARY KEY, login TEXT NOT NULL, role TEXT NOT NULL, sub TEXT NOT NULL,
    created TEXT DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS push_sent (key TEXT PRIMARY KEY, ts TEXT DEFAULT (datetime('now','localtime')));
"""
SPORT_RU = {"run": "Бег", "bike": "Велосипед", "swim": "Плавание", "strength": "Силовая", "hockey": "Хоккей",
            "football": "Футбол", "trail": "Трейл", "multisport": "Триатлон", "other": "Тренировка"}


def init():
    with db.session() as c:
        c.executescript(SCHEMA)
        # первый запуск: всё, что уже есть, считаем отправленным — без лавины уведомлений
        if not c.execute("SELECT 1 FROM settings WHERE key='push_seeded'").fetchone():
            c.execute("INSERT OR IGNORE INTO push_sent (key) SELECT 'a:' || source || ':' || source_id FROM activities")
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('push_seeded', '1')")


def _private_key():
    if not KEY_FILE.exists():
        k = ec.generate_private_key(ec.SECP256R1())
        KEY_FILE.write_bytes(k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                             serialization.NoEncryption()))
        KEY_FILE.chmod(0o600)
    return serialization.load_pem_private_key(KEY_FILE.read_bytes(), None)


def public_key() -> str:
    raw = _private_key().public_key().public_bytes(serialization.Encoding.X962,
                                                   serialization.PublicFormat.UncompressedPoint)
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def subscribe(user: dict, sub: dict):
    if not str(sub.get("endpoint", "")).startswith("https://") or not (sub.get("keys") or {}).get("p256dh"):
        raise ValueError("Неверная подписка")
    with db.session() as c:
        c.execute("INSERT OR REPLACE INTO push_subs (endpoint, login, role, sub) VALUES (?,?,?,?)",
                  (sub["endpoint"], user["login"], user["role"], json.dumps(sub)))


def unsubscribe(user: dict, endpoint: str):
    with db.session() as c:
        c.execute("DELETE FROM push_subs WHERE endpoint=? AND login=?", (endpoint, user["login"]))


def send(role: str, title: str, body: str, url: str = "/", login: str | None = None) -> int:
    """Отправить всем подпискам роли (или одного пользователя). Возвращает число доставленных."""
    from pywebpush import WebPushException, webpush
    with db.session() as c:
        q, args = "SELECT endpoint, sub FROM push_subs WHERE role=?", [role]
        if login:
            q, args = "SELECT endpoint, sub FROM push_subs WHERE login=?", [login]
        subs = c.execute(q, args).fetchall()
    _private_key()
    payload = json.dumps({"title": title, "body": body, "url": url}, ensure_ascii=False)
    sent = 0
    for endpoint, sub in subs:
        try:
            webpush(json.loads(sub), payload, vapid_private_key=str(KEY_FILE), vapid_claims={"sub": CONTACT}, ttl=86400)
            sent += 1
        except WebPushException as e:
            code = getattr(e.response, "status_code", None)
            if code in (404, 410):  # подписка отозвана — убираем
                with db.session() as c:
                    c.execute("DELETE FROM push_subs WHERE endpoint=?", (endpoint,))
            else:
                log.warning("push %s: %s", code, e)
        except Exception as e:  # сеть и т. п. — уведомление не должно ломать синхронизацию
            log.warning("push: %s", e)
    return sent


def _workout_text(a: dict) -> str:
    parts = []
    if a.get("distance_m"):
        km = a["distance_m"] / 1000
        parts.append(f"{int(a['distance_m'])} м" if a["sport"] == "swim" else f"{km:.1f} км".replace(".", ","))
    if a.get("duration_s"):
        m = round(a["duration_s"] / 60)
        parts.append(f"{m // 60} ч {m % 60:02d} мин" if m >= 60 else f"{m} мин")
    if a.get("avg_hr"):
        parts.append(f"пульс {round(a['avg_hr'])}")
    if a.get("tss"):
        parts.append(f"TSS {round(a['tss'])}")
    return " · ".join(parts)


def new_workouts() -> int:
    """Тренеру — о каждой новой тренировке с часов (или добавленной вручную) за последние 2 дня."""
    since = (date.today() - timedelta(days=2)).isoformat()
    with db.session() as c:
        if not c.execute("SELECT 1 FROM push_subs WHERE role='coach'").fetchone():
            return 0
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM activities WHERE date >= ? AND source IN ('garmin','manual') "
            "AND COALESCE(kind,'') != 'leg' AND 'a:' || source || ':' || source_id NOT IN (SELECT key FROM push_sent) "
            "ORDER BY start_time", (since,))]
        for a in rows:
            c.execute("INSERT OR IGNORE INTO push_sent (key) VALUES (?)", (f"a:{a['source']}:{a['source_id']}",))
        u = c.execute("SELECT name, login FROM users WHERE role='athlete' ORDER BY rowid LIMIT 1").fetchone()
    name = (u["name"] or u["login"]) if u else "Спортсмен"
    for a in rows:
        sport = "multisport" if a.get("kind") == "multisport_parent" else a["sport"]
        title = f"{name}: {a.get('title') or SPORT_RU.get(sport, 'Тренировка')}"
        send("coach", title, _workout_text(a) or "Тренировка завершена — оцените", "/#calendar")
    return len(rows)
