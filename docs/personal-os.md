# System: Personal OS

> Dennis' zweites Gehirn — Ziele, Aufgaben, Wissen, Gesundheit und Finanzen außerhalb des Mindwave-Business, innerhalb desselben CEO-GPT.

## Architektur

```
[/personal-prime] --> liest personal-os/*.md + personal.db --> Zusammenfassung an Dennis
```

Markdown für qualitative Inhalte (Ziele, Notizen, Wissen, Aufgaben). SQLite (`personal.db`) nur für zeitreihenartige, strukturierte Daten (Gesundheit, Finanz-Transaktionen, Aufgaben-Historie). Bewusst getrennt von `data/data.db` (Business-Kennzahlen).

## Wichtige Dateien

| Datei | Zweck |
|---|---|
| `personal-os/profil.md` | Wer Dennis lebensweit ist (Gegenstück zu `context/personal-info.md`) |
| `personal-os/ziele-notizen/ziele.md` | Langfristige persönliche Ziele |
| `personal-os/ziele-notizen/notizen.md` | Laufendes Gedanken-Log |
| `personal-os/aufgaben-termine/aufgaben.md` | Lebensweite To-do-Liste |
| `personal-os/aufgaben-termine/routinen.md` | Wiederkehrende persönliche Routinen |
| `personal-os/wissen/archiv.md` | Index aller Bücher/Kurse/Artikel-Notizen |
| `personal-os/gesundheit-finanzen/gesundheit.md` | Gesundheits-Übersicht |
| `personal-os/gesundheit-finanzen/finanzen.md` | Persönliche Finanzen (lokal, nicht in Git) |
| `personal-os/personal.db` | SQLite — `health_daily`, `finance_transactions`, `tasks_log` (lokal, nicht in Git) |
| `personal-os/db_schema.sql` | Schema-Quelle für `personal.db` |
| `scripts/personal-os/init_db.py` | Legt `personal.db` an, idempotent |
| `.claude/commands/personal-prime.md` | Befehl `/personal-prime` |
| `reference/personal-os-data-access.md` | Vollständige Schema-Doku + Beispiel-Abfragen |

## Wie es läuft

1. Dennis ruft `/personal-prime` auf
2. Mitarbeiter liest `profil.md`, `ziele-notizen/`, `aufgaben-termine/`, `wissen/archiv.md`, `gesundheit-finanzen/`
3. Fasst zusammen: wer er lebensweit ist, aktuelle Ziele, offene Aufgaben, Wissens-Stand, Gesundheit/Finanzen
4. Bei Bedarf für tiefere Analyse: `reference/personal-os-data-access.md` für SQL-Zugriff auf `personal.db`

## Konfiguration

Keine API-Keys nötig. Reine lokale Markdown- + SQLite-Struktur.

## Häufige Aktionen

**Datenbank neu anlegen/prüfen:**
```bash
python3 scripts/personal-os/init_db.py
```

**Sitzung starten:**
```
/personal-prime
```

## Abhängigkeiten

- **Braucht:** Nichts Externes — reine lokale Struktur
- **Wird genutzt von:** Nur `/personal-prime`. Kein Business-System (`scripts/jarvis/`, `scripts/daten/`) greift darauf zu — bewusste Trennung.

## Historie

| Datum | Änderung |
|---|---|
| 2026-06-30 | Erste Doku — Personal OS Grundgerüst aufgebaut (siehe `plans/2026-06-30-personal-os.md`) |
