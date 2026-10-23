# SQLite handler for Luminos

from __future__ import annotations
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("LUMINOS_DB_PATH", str(Path(__file__).with_name("data") / "LUMINOS.db"))

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
    mana INTEGER NOT NULL DEFAULT 0,
    max_mana INTEGER NOT NULL DEFAULT 0,
    gold INTEGER NOT NULL DEFAULT 0,
    potions INTEGER NOT NULL DEFAULT 2,
    weapon TEXT,
    attack_bonus INTEGER NOT NULL DEFAULT 0,
    armour TEXT,
    armour_bonus INTEGER NOT NULL DEFAULT 0,
    location TEXT NOT NULL DEFAULT 'Luminos',
    enemy_name TEXT,
    enemy_hp INTEGER NOT NULL DEFAULT 0,
    enemy_attack INTEGER NOT NULL DEFAULT 0,
    last_action_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS player_items (
    email TEXT NOT NULL,
    item TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (email, item),
    FOREIGN KEY (email) REFERENCES players(email) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS player_quests (
    email TEXT NOT NULL,
    quest_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    progress INTEGER NOT NULL DEFAULT 0,
    accepted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, quest_id),
    FOREIGN KEY(email) REFERENCES players(email) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS player_bosses (
    email TEXT NOT NULL,
    boss_id TEXT NOT NULL,
    defeated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email, boss_id),
    FOREIGN KEY(email) REFERENCES players(email) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS processed_messages (
    message_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def connect() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn

def initialise() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        #Migrating from V1.1 Databases
        columns = {row[1] for row in conn.execute("PRAGMA table_info(players)")}
        if "mana" not in columns:
            conn.execute("ALTER TABLE players ADD COLUMN mana INTEGER NOT NULL DEFAULT 0")
        if "max_mana" not in columns:
            conn.execute("ALTER TABLE players ADD COLUMN max_mana INTEGER NOT NULL DEFAULT 0")
        if "weapon" not in columns:
            conn.execute("ALTER TABLE players ADD COLUMN weapon TEXT")
        if "attack_bonus" not in columns:
            conn.execute("ALTER TABLE players ADD COLUMN attack_bonus INTEGER NOT NULL DEFAULT 0")
        if "armour" not in columns:
            conn.execute("ALTER TABLE players ADD COLUMN armour TEXT")
        if "armour_bonus" not in columns:
            conn.execute("ALTER TABLE players ADD COLUMN armour_bonus INTEGER NOT NULL DEFAULT 0")
            # Give existing characters mana when upgrading from v1.1.
        mana_by_class = {"WARRIOR": 3, "MAGE": 12, "ROGUE": 5, "PALADIN": 8,
                        "RANGER": 6, "CLERIC": 12, "WARLOCK": 14, "BARD": 10}
        for class_name, mana in mana_by_class.items():
            conn.execute("UPDATE players SET max_mana=?, mana=? WHERE class=? AND max_mana=0",
                         (mana, mana, class_name))
