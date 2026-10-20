"""Синхронизация всех источников.

    python -m app.sync              # всё, что настроено в .env
    python -m app.sync garmin-login # первый вход в Garmin (с кодом MFA)
    python -m app.sync demo         # заполнить демо-базу
"""
import sys

from . import config, db
from .connectors import fitbit, garmin, trainingpeaks


def configured() -> dict[str, bool]:
    return {
        "tp_ical": bool(config.TP_ICAL_URL),
        "tp": bool(trainingpeaks.current_cookie()),
        "garmin": config.GARMIN_TOKEN_DIR.exists(),  # только после ручного garmin-login
        "fitbit": fitbit.connected(),
    }


def run(sources: list[str] | None = None) -> list[dict]:
    db.init()
    jobs = {
        "tp_ical": lambda: trainingpeaks.sync_ical(),
        "tp": lambda: trainingpeaks.sync_api(config.SYNC_DAYS_BACK, config.SYNC_DAYS_FORWARD),
        "garmin": lambda: garmin.sync(config.SYNC_DAYS_BACK),
        "fitbit": lambda: fitbit.sync(config.SYNC_DAYS_BACK),
    }
    enabled = configured()
    results = []
    for name, job in jobs.items():
        if sources and name not in sources:
            continue
        if not sources and not enabled[name]:
            continue
        try:
            msg, ok = job(), True
        except Exception as e:
            msg, ok = f"{e.__class__.__name__}: {e}", False
        db.log(name, ok, msg)
        results.append({"source": name, "ok": ok, "message": msg})
    return results


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "garmin-login":
        garmin.login(interactive=True)
        print("Garmin: токены сохранены в", config.GARMIN_TOKEN_DIR)
    elif cmd == "demo":
        from .demo import generate
        generate()
    else:
        for r in run(sys.argv[1:] or None):
            print(("✓ " if r["ok"] else "✗ ") + r["source"] + ": " + r["message"])
