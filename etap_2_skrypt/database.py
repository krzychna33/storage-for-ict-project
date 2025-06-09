import sqlite3
import os
from typing import Optional

def init_db():
    """Inicjalizacja bazy danych z tabelą kluczy dla satelitów"""
    conn = sqlite3.connect("keys.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS satellite_keys (
            satellite_id TEXT PRIMARY KEY,
            key_value BLOB NOT NULL,
            description TEXT
        )
    """)
    
    # Przykładowe dane testowe
    if cursor.execute("SELECT COUNT(*) FROM satellite_keys").fetchone()[0] == 0:
        test_keys = [
            ("SAT-001", os.urandom(32)),
            ("SAT-002", os.urandom(32)),
        ]
        cursor.executemany(
            "INSERT INTO satellite_keys (satellite_id, key_value) VALUES (?, ?)",
            test_keys
        )
    conn.commit()
    conn.close()

def get_key_for_satellite(satellite_id: str) -> Optional[bytes]:
    """Pobiera klucz dla konkretnego satelity"""
    conn = sqlite3.connect("keys.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT key_value FROM satellite_keys WHERE satellite_id = ?",
        (satellite_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_satellite_key(satellite_id: str, key: bytes, description: str = ""):
    """Dodaje nowy klucz dla satelity"""
    conn = sqlite3.connect("keys.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO satellite_keys VALUES (?, ?, ?)",
        (satellite_id, key, description)
    )
    conn.commit()
    conn.close()