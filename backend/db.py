import sqlite3
import json

from .config import DB_PATH


def init_db():
    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY,
            created_at TEXT,
            symbol TEXT,
            horizon TEXT,
            action TEXT,
            score REAL,
            payload TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_signal(signal):
    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        """
        INSERT INTO signals
        (created_at, symbol, horizon, action, score, payload)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            signal["generated_at"],
            signal["symbol"],
            signal["horizon"],
            signal["action"],
            signal["score"],
            json.dumps(signal),
        ),
    )

    connection.commit()
    connection.close()


def recent(limit=100):
    connection = sqlite3.connect(DB_PATH)

    rows = connection.execute(
        "SELECT payload FROM signals ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()

    connection.close()

    return [json.loads(row[0]) for row in rows]
