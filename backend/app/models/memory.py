import sqlite3
from .database import DB_PATH

def get_mapping(key: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM memory WHERE key = ?", (key.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def set_mapping(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key.lower(), value))
    conn.commit()
    conn.close()
