import sqlite3
import logging
import os

from config import DB_PATH, SCHEMA_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection, creating the data directory if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Execute the schema SQL to create tables (safe to run multiple times)."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)
