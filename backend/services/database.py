from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

from backend.models.database import SCHEMA_SQL

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "backend/data/nyayasetu.db"))
DOCUMENT_STORAGE_DIR = Path(os.getenv("DOCUMENT_STORAGE_DIR", "backend/data/uploads"))


def connect_database() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCUMENT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=30, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def initialize_database() -> None:
    with connect_database() as connection:
        connection.executescript(SCHEMA_SQL)


def get_db() -> Iterator[sqlite3.Connection]:
    connection = connect_database()
    try:
        yield connection
    finally:
        connection.close()
