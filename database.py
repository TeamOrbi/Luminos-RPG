# SQLite handler for Eldoria

from __future__ import annotations
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("ELDORIA_DB_PATH", str(Path(__file__).with_name("data") / "eldoria.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    email TEXT PRIMARY KEY,
    name TEXT,
    class TEXT,
    status TEXT NOT NULL DEFAULT 'awaiting_name',
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    hp INTEGER NOT NULL DEFAULT 30,
    max_hp INTEGER NOT NULL DEFAULT 30,
    gold INTEGER NOT NULL DEFAULT 0,
    potions INTEGER NOT NULL DEFAULT 2,
    location TEXT NOT NULL DEFAULT 'Eldoria',
    enemy_name TEXT,
    enemy_hp INTEGER NOT NULL DEFAULT 0,
    enemy_attack INTEGER NOT NULL DEFAULT 0,
    last_action_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS processed_messages (
    message_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def connect() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=true, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn

def initialise() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
