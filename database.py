"""
database.py
Handles SQLite connection and schema initialization.

Why SQLite? It requires zero configuration — no separate server to run.
The database is stored in a single file (employees.db), which is perfect
for learning and portfolio projects.
"""

import sqlite3

DB_PATH = "employees.db"


def get_connection():
    """
    Returns a new SQLite connection with row_factory set to Row,
    which lets us access columns by name instead of index.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates the employees table if it doesn't already exist.
    Called once on server startup.

    Schema design decisions:
    - email is UNIQUE to prevent duplicate entries (enforced at DB level)
    - age has a CHECK constraint — negative age should never reach the database
    - is_active defaults to 1 (TRUE) for new employees
    - created_at is auto-filled by SQLite using CURRENT_TIMESTAMP
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            department  TEXT    NOT NULL,
            age         INTEGER NOT NULL CHECK(age >= 18),
            is_active   INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized — employees table ready.")
