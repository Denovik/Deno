-- Personal OS Datenbank-Schema
-- Getrennt von data/data.db (Business-Kennzahlen) — siehe reference/personal-os-data-access.md

CREATE TABLE IF NOT EXISTS health_daily (
    date TEXT PRIMARY KEY,
    sleep_hours REAL,
    weight_kg REAL,
    exercise_minutes INTEGER,
    mood_score INTEGER,
    notes TEXT,
    logged_at TEXT
);

CREATE TABLE IF NOT EXISTS finance_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    description TEXT,
    amount_eur REAL,
    type TEXT CHECK(type IN ('einnahme','ausgabe')),
    logged_at TEXT
);

CREATE TABLE IF NOT EXISTS tasks_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    area TEXT,
    completed_date TEXT,
    logged_at TEXT
);
