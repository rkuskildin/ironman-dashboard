"""SQLite-хранилище: план, факт, здоровье, журнал синхронизаций."""
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS planned_workouts (
    source       TEXT NOT NULL,
    source_id    TEXT NOT NULL,
    date         TEXT NOT NULL,
    sport        TEXT NOT NULL,
    title        TEXT,
    description  TEXT,
    coach_comments TEXT,
    duration_s   REAL,
    distance_m   REAL,
    tss          REAL,
    PRIMARY KEY (source, source_id)
);
CREATE TABLE IF NOT EXISTS activities (
    source       TEXT NOT NULL,
    source_id    TEXT NOT NULL,
    date         TEXT NOT NULL,
    start_time   TEXT,
    sport        TEXT NOT NULL,
    title        TEXT,
    duration_s   REAL,
    distance_m   REAL,
    elevation_m  REAL,
    avg_hr       REAL,
    max_hr       REAL,
    avg_power    REAL,
    np           REAL,
    tss          REAL,
    calories     REAL,
    athlete_comments TEXT,
    PRIMARY KEY (source, source_id)
);
CREATE TABLE IF NOT EXISTS daily_health (
    date          TEXT NOT NULL,
    source        TEXT NOT NULL,
    resting_hr    REAL,
    hrv           REAL,
    sleep_s       REAL,
    deep_s        REAL,
    rem_s         REAL,
    sleep_score   REAL,
    steps         REAL,
    body_battery  REAL,
    stress        REAL,
    readiness     REAL,
    PRIMARY KEY (date, source)
);
CREATE TABLE IF NOT EXISTS fitness_daily (
    date TEXT PRIMARY KEY,
    ctl REAL, atl REAL, tsb REAL
);
CREATE TABLE IF NOT EXISTS garmin_status (
    date TEXT PRIMARY KEY,
    data TEXT
);
CREATE TABLE IF NOT EXISTS tracks (
    source TEXT, source_id TEXT, data TEXT,
    PRIMARY KEY (source, source_id)
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT (datetime('now','localtime')),
    source TEXT, ok INTEGER, message TEXT
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def session():
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


MIGRATIONS = {
    "daily_health": {"bed_time": "TEXT", "wake_time": "TEXT"},
    "activities": {"start_gmt": "TEXT", "fitbit_avg_hr": "REAL", "fitbit_max_hr": "REAL", "analysis": "TEXT",
                   "moving_s": "REAL", "has_gps": "INTEGER", "parent_id": "TEXT", "kind": "TEXT"},
}


def init():
    with session() as c:
        c.executescript(SCHEMA)
        for table, cols in MIGRATIONS.items():
            have = {r[1] for r in c.execute(f"PRAGMA table_info({table})")}
            for col, typ in cols.items():
                if col not in have:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")


def upsert(conn, table: str, row: dict):
    cols = list(row)
    conn.execute(
        f"INSERT OR REPLACE INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        [row[k] for k in cols],
    )


def upsert_health(conn, row: dict):
    """Обновляет только непустые поля, чтобы разные запросы не затирали друг друга."""
    row = {k: v for k, v in row.items() if v is not None}
    conn.execute("INSERT OR IGNORE INTO daily_health (date, source) VALUES (?, ?)", (row["date"], row["source"]))
    fields = [k for k in row if k not in ("date", "source")]
    if fields:
        conn.execute(
            f"UPDATE daily_health SET {','.join(f'{k}=?' for k in fields)} WHERE date=? AND source=?",
            [row[k] for k in fields] + [row["date"], row["source"]],
        )


def log(source: str, ok: bool, message: str):
    with session() as c:
        c.execute("INSERT INTO sync_log (source, ok, message) VALUES (?,?,?)", (source, int(ok), message[:500]))
