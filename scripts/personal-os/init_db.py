#!/usr/bin/env python3
"""
Personal OS — Datenbank-Setup
Legt personal-os/personal.db aus personal-os/db_schema.sql an, falls noch nicht vorhanden.
Idempotent: mehrfaches Ausführen ist sicher.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "personal-os" / "personal.db"
SCHEMA_PATH = BASE_DIR / "personal-os" / "db_schema.sql"


def init_db():
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print(f"[personal-os] Datenbank bereit: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
