# Personal OS — Daten-Zugriff

> Leitfaden für direkte Datenbank-Abfragen im Personal-OS-Bereich. Laden wenn tiefere Gesundheits-/Finanz-Analyse nötig ist.

## Datenbank

- **Pfad:** `personal-os/personal.db` (SQLite)
- **Verbinden:** `import sqlite3; conn = sqlite3.connect("personal-os/personal.db")`
- **Anlegen/Aktualisieren:** `python3 scripts/personal-os/init_db.py` (idempotent, sicher mehrfach ausführbar)
- **Schema-Quelle:** `personal-os/db_schema.sql`

**Wichtig:** Diese Datenbank ist bewusst getrennt von `data/data.db` (Business-Kennzahlen). Persönliche Gesundheits- und Finanzdaten sollen nie mit Business-Reports vermischt werden. `personal-os/personal.db` ist zudem nicht in Git versioniert (siehe `.gitignore`) — bleibt lokal auf dem Rechner.

---

## Tabellen-Aufbau

### health_daily
Tagesstand für persönliches Gesundheits-Tracking.

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| date | TEXT | Datum (YYYY-MM-DD), Primärschlüssel |
| sleep_hours | REAL | Schlafstunden |
| weight_kg | REAL | Gewicht in kg |
| exercise_minutes | INTEGER | Bewegung in Minuten |
| mood_score | INTEGER | Stimmung, frei wählbare Skala |
| notes | TEXT | Freitext-Notizen |
| logged_at | TEXT | Zeitstempel des Eintrags (ISO) |

### finance_transactions
Persönliche Finanz-Transaktionen (getrennt von Business-Affiliate-Einnahmen).

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| id | INTEGER | Primärschlüssel, automatisch |
| date | TEXT | Datum der Transaktion (YYYY-MM-DD) |
| category | TEXT | Kategorie (z.B. Gehalt, Miete, Lebensmittel) |
| description | TEXT | Beschreibung |
| amount_eur | REAL | Betrag in Euro |
| type | TEXT | `einnahme` oder `ausgabe` |
| logged_at | TEXT | Zeitstempel des Eintrags (ISO) |

### tasks_log
Historie erledigter persönlicher Aufgaben (Ergänzung zu `personal-os/aufgaben-termine/aufgaben.md`).

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| id | INTEGER | Primärschlüssel, automatisch |
| task | TEXT | Aufgabe |
| area | TEXT | Lebensbereich (Business, Gesundheit, Privates, Sonstiges) |
| completed_date | TEXT | Erledigt am (YYYY-MM-DD) |
| logged_at | TEXT | Zeitstempel des Eintrags (ISO) |

---

## Beispiel-Abfragen

```python
import sqlite3
conn = sqlite3.connect("personal-os/personal.db")
cur = conn.cursor()

# Letzte 7 Tage Schlaf
cur.execute("SELECT date, sleep_hours FROM health_daily ORDER BY date DESC LIMIT 7")

# Ausgaben des aktuellen Monats
cur.execute("SELECT category, SUM(amount_eur) FROM finance_transactions WHERE type='ausgabe' AND date LIKE '2026-06%' GROUP BY category")
```
