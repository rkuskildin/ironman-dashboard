"""Настройки из файла .env (см. .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
load_dotenv(ROOT / ".env")


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_float(name: str, default: float) -> float:
    try:
        return float(env(name) or default)
    except ValueError:
        return default


# IRONMAN_DEMO=1 — работать с отдельной демо-базой, не трогая реальные данные
DEMO = env("IRONMAN_DEMO") == "1"
DB_PATH = DATA_DIR / ("demo.db" if DEMO else "ironman.db")

# Публичный адрес панели (для ссылок-приглашений)
PUBLIC_URL = env("PUBLIC_URL", "http://localhost:8000").rstrip("/")

# Цель
RACE_NAME = env("RACE_NAME", "Ironman")
RACE_DATE = env("RACE_DATE", "2028-09-30")

# Пороговые значения спортсмена (для расчёта TSS, если источник его не дал)
FTP = env_float("FTP", 200)                 # Вт
LTHR = env_float("LTHR", 165)               # пульс ПАНО, уд/мин
RUN_THRESHOLD_PACE = env_float("RUN_THRESHOLD_PACE", 300)   # сек/км
SWIM_CSS = env_float("SWIM_CSS", 120)       # сек/100 м

# TrainingPeaks
TP_ICAL_URL = env("TP_ICAL_URL")
TP_AUTH_COOKIE = env("TP_AUTH_COOKIE")      # значение cookie Production_tpAuth

# Garmin
GARMIN_EMAIL = env("GARMIN_EMAIL")
GARMIN_PASSWORD = env("GARMIN_PASSWORD")
GARMIN_TOKEN_DIR = DATA_DIR / "garmin_tokens"

# Fitbit через Google Health API (OAuth-клиент из Google Cloud Console)
GOOGLE_HEALTH_CLIENT_ID = env("GOOGLE_HEALTH_CLIENT_ID")
GOOGLE_HEALTH_CLIENT_SECRET = env("GOOGLE_HEALTH_CLIENT_SECRET")
GOOGLE_HEALTH_REDIRECT_URI = env("GOOGLE_HEALTH_REDIRECT_URI", "http://localhost:8000/api/fitbit/callback")
FITBIT_TOKEN_FILE = DATA_DIR / "google_health_token.json"

# Откуда брать сон, HRV и пульс покоя (fitbit | garmin)
RECOVERY_SOURCE = env("RECOVERY_SOURCE", "fitbit")

# Режим: лечь не позже BEDTIME_TARGET по часовому поясу UTC+BEDTIME_TZ (Москва = 3)
BEDTIME_TARGET = env("BEDTIME_TARGET", "23:00")
BEDTIME_TZ = env_float("BEDTIME_TZ", 3)

# Как часто синхронизировать в фоне (минуты, 0 = выключено)
SYNC_INTERVAL_MIN = int(env_float("SYNC_INTERVAL_MIN", 60))
SYNC_DAYS_BACK = int(env_float("SYNC_DAYS_BACK", 30))
SYNC_DAYS_FORWARD = int(env_float("SYNC_DAYS_FORWARD", 21))
