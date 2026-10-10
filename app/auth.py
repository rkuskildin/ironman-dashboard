"""Вход в панель: пользователи (спортсмен / тренер), сессии в cookie, защита от перебора.

Пользователи заводятся на сервере:
    python -m app.auth add <логин> --role athlete|coach   # спросит пароль
    python -m app.auth list
    python -m app.auth remove <логин>
"""
import argparse
import getpass
import hashlib
import hmac
import secrets
import sys
import time
from collections import defaultdict

from . import config, db

ROLES = {"athlete": "Спортсмен", "coach": "Тренер"}
SESSION_DAYS = 30
COOKIE = "ironman_session"
_ITER = 240_000

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    login TEXT PRIMARY KEY, name TEXT, role TEXT NOT NULL, pw_hash TEXT NOT NULL,
    created TEXT DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS invites (
    token_hash TEXT PRIMARY KEY, login TEXT NOT NULL, expires REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY, login TEXT NOT NULL, expires REAL NOT NULL
);
"""


def init():
    with db.session() as c:
        c.executescript(SCHEMA)


def _hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITER)
    return f"pbkdf2${_ITER}${salt.hex()}${dk.hex()}"


def _verify(password: str, stored: str) -> bool:
    try:
        _, it, salt, dk = stored.split("$")
        got = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(it))
        return hmac.compare_digest(got.hex(), dk)
    except ValueError:
        return False


def _th(token: str) -> str:  # в базе храним только хеш токена сессии
    return hashlib.sha256(token.encode()).hexdigest()


# ---- защита от перебора: 5 неудачных попыток за 15 минут с одного IP или на один логин ----
_fails: dict[str, list[float]] = defaultdict(list)


def throttled(*keys: str) -> bool:
    now = time.time()
    for k in keys:
        _fails[k] = [t for t in _fails[k] if now - t < 900]
        if len(_fails[k]) >= 5:
            return True
    return False


def login(username: str, password: str, ip: str) -> str | None:
    username = username.strip().lower()
    if throttled("ip:" + ip, "u:" + username):
        raise PermissionError("Слишком много попыток — подождите 15 минут")
    with db.session() as c:
        row = c.execute("SELECT pw_hash FROM users WHERE login=?", (username,)).fetchone()
    # сравнение делаем всегда, чтобы время ответа не выдавало существование логина
    ok = _verify(password, row["pw_hash"] if row else _hash("x"))
    if not (row and ok):
        _fails["ip:" + ip].append(time.time())
        _fails["u:" + username].append(time.time())
        return None
    token = secrets.token_urlsafe(32)
    with db.session() as c:
        c.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
        c.execute("INSERT INTO sessions (token_hash, login, expires) VALUES (?,?,?)",
                  (_th(token), username, time.time() + SESSION_DAYS * 86400))
    return token


def user_by_token(token: str | None) -> dict | None:
    if not token:
        return None
    with db.session() as c:
        row = c.execute("SELECT u.login, u.name, u.role FROM sessions s JOIN users u ON u.login=s.login "
                        "WHERE s.token_hash=? AND s.expires > ?", (_th(token), time.time())).fetchone()
    return dict(row) if row else None


def logout(token: str | None):
    if token:
        with db.session() as c:
            c.execute("DELETE FROM sessions WHERE token_hash=?", (_th(token),))


INVITE_HOURS = 72
BASE_URL = config.PUBLIC_URL


def create_invite(login: str, role: str, name: str = "") -> str:
    """Учётка без пароля + одноразовая ссылка, по которой человек сам задаёт пароль."""
    login = login.strip().lower()
    token = secrets.token_urlsafe(24)
    with db.session() as c:
        c.execute("INSERT INTO users (login, name, role, pw_hash) VALUES (?,?,?,'!') "
                  "ON CONFLICT(login) DO UPDATE SET role=excluded.role, name=COALESCE(NULLIF(excluded.name,''), users.name)",
                  (login, name, role))
        c.execute("DELETE FROM invites WHERE login=?", (login,))
        c.execute("INSERT INTO invites (token_hash, login, expires) VALUES (?,?,?)",
                  (_th(token), login, time.time() + INVITE_HOURS * 3600))
    return f"{BASE_URL}/setup#{token}"   # токен во фрагменте — не попадает в логи сервера и Referer


def invite_user(token: str) -> dict | None:
    with db.session() as c:
        row = c.execute("SELECT u.login, u.name, u.role FROM invites i JOIN users u ON u.login=i.login "
                        "WHERE i.token_hash=? AND i.expires > ?", (_th(token), time.time())).fetchone()
    return dict(row) if row else None


def accept_invite(token: str, password: str) -> str:
    u = invite_user(token)
    if not u:
        raise PermissionError("Ссылка недействительна или устарела — попросите новую")
    if len(password) < 10:
        raise ValueError("Пароль должен быть не короче 10 символов")
    with db.session() as c:
        c.execute("UPDATE users SET pw_hash=? WHERE login=?", (_hash(password), u["login"]))
        c.execute("DELETE FROM invites WHERE login=?", (u["login"],))
        c.execute("DELETE FROM sessions WHERE login=?", (u["login"],))
    token_s = secrets.token_urlsafe(32)
    with db.session() as c:
        c.execute("INSERT INTO sessions (token_hash, login, expires) VALUES (?,?,?)",
                  (_th(token_s), u["login"], time.time() + SESSION_DAYS * 86400))
    return token_s


def has_users() -> bool:
    with db.session() as c:
        return c.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None


# ---------------- CLI ----------------
def _cli():
    db.init()
    init()
    p = argparse.ArgumentParser(prog="ironman-user")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="добавить пользователя или сменить пароль")
    a.add_argument("login")
    a.add_argument("--role", choices=ROLES, default="athlete")
    a.add_argument("--name", default="")
    i = sub.add_parser("invite", help="ссылка, по которой человек сам задаст пароль")
    i.add_argument("login")
    i.add_argument("--role", choices=ROLES, default="athlete")
    i.add_argument("--name", default="")
    sub.add_parser("list")
    r = sub.add_parser("remove")
    r.add_argument("login")
    args = p.parse_args()

    if args.cmd == "invite":
        url = create_invite(args.login, args.role, args.name)
        print(f"Ссылка для {args.login} ({ROLES[args.role]}), действует {INVITE_HOURS} ч:\n{url}")
        return
    if args.cmd == "list":
        with db.session() as c:
            for row in c.execute("SELECT login, name, role, created, pw_hash FROM users ORDER BY created"):
                state = "ждёт пароль" if row["pw_hash"] == "!" else "активен"
                print(f"{row['login']:16} {ROLES.get(row['role'], row['role']):10} {row['name'] or '':20} {state:12} {row['created']}")
        return
    if args.cmd == "remove":
        with db.session() as c:
            c.execute("DELETE FROM sessions WHERE login=?", (args.login.lower(),))
            n = c.execute("DELETE FROM users WHERE login=?", (args.login.lower(),)).rowcount
        print("Удалён" if n else "Нет такого пользователя")
        return
    pw = getpass.getpass(f"Пароль для {args.login}: ")
    if len(pw) < 10:
        sys.exit("Пароль должен быть не короче 10 символов")
    if getpass.getpass("Ещё раз: ") != pw:
        sys.exit("Пароли не совпали")
    with db.session() as c:
        c.execute("INSERT INTO users (login, name, role, pw_hash) VALUES (?,?,?,?) "
                  "ON CONFLICT(login) DO UPDATE SET pw_hash=excluded.pw_hash, role=excluded.role, "
                  "name=COALESCE(NULLIF(excluded.name,''), users.name)",
                  (args.login.lower(), args.name, args.role, _hash(pw)))
        c.execute("DELETE FROM sessions WHERE login=?", (args.login.lower(),))  # старые сессии — выйти
    print(f"Готово: {args.login} ({ROLES[args.role]})")


if __name__ == "__main__":
    _cli()
