from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

_SCHEMA = """
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    flag TEXT,
    error_message TEXT,
    started_at TEXT,
    finished_at TEXT,
    duration_seconds REAL DEFAULT 0,
    attempt_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id),
    category TEXT NOT NULL DEFAULT 'discovery',
    content TEXT NOT NULL,
    raw_line TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    used_in_attempt INTEGER
);

CREATE TABLE IF NOT EXISTS stdout_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_facts_challenge ON facts(challenge_id, created_at);
CREATE INDEX IF NOT EXISTS idx_hints_challenge ON hints(challenge_id, created_at);
CREATE INDEX IF NOT EXISTS idx_stdout_challenge ON stdout_log(challenge_id, id DESC);
"""

_db_path: Path | None = None


def configure(db_path: str | Path) -> None:
    global _db_path
    _db_path = Path(db_path)
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    try:
        conn.executescript(_SCHEMA)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_conn() -> Generator[sqlite3.Connection, None, None]:
    if _db_path is None:
        raise RuntimeError("Database not configured. Call configure() first.")
    conn = sqlite3.connect(str(_db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn
