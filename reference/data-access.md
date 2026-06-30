# Daten-Zugriff

> Leitfaden für direkte Datenbank-Abfragen. Laden wenn tiefere Analyse nötig ist.

## Datenbank

- **Pfad:** `data/data.db` (SQLite) — primär auf dem Server gepflegt (seit 2026-06-30)
- **Server:** Täglich 08:00 automatisch aktualisiert via Cron auf 167.233.95.3
- **Lokal spiegeln:** `scp -i ~/.ssh/mindwave_hetzner root@167.233.95.3:/opt/mindwave/jarvis/data/data.db data/data.db`
- **Verbinden:** `import sqlite3; conn = sqlite3.connect("data/data.db")`
- **Manuell aktualisieren (lokal):** `python scripts/daten/collect.py`
- **Kennzahlen regenerieren:** `python scripts/daten/generate_metrics.py`

---

## Angebundene Quellen

| Quelle | Tabelle(n) | Sammler |
|--------|------------|---------|
| YouTube | `youtube_daily`, `youtube_videos` | `scripts/daten/collect_youtube.py` |
| Instagram | `instagram_daily` | `scripts/daten/collect_instagram.py` |

---

## Tabellen-Aufbau

### youtube_daily
Tagesstand des Mindwave-Kanals.

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| date | TEXT | Sammel-Datum (YYYY-MM-DD), Primärschlüssel |
| channel_name | TEXT | Kanal-Name |
| subscribers | INTEGER | Abonnenten |
| total_views | INTEGER | Gesamtaufrufe aller Videos |
| total_videos | INTEGER | Anzahl veröffentlichter Videos |
| views_30d | INTEGER | Aufrufe der letzten 30 Tage |
| videos_published_30d | INTEGER | Neue Videos in 30 Tagen |
| collected_at | TEXT | Zeitstempel der Sammlung (ISO) |

### youtube_videos
Performance einzelner Videos (aktualisiert bei jeder Sammlung).

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| video_id | TEXT | YouTube-Video-ID, Primärschlüssel |
| title | TEXT | Videotitel |
| published_date | TEXT | Veröffentlichungsdatum (YYYY-MM-DD) |
| views | INTEGER | Gesamtaufrufe |
| likes | INTEGER | Likes |
| comments | INTEGER | Kommentare |
| duration | TEXT | Länge (ISO 8601, z.B. PT1M30S) |
| last_updated | TEXT | Datum der letzten Aktualisierung |

### instagram_daily
Tagesstand des mind.wave26-Kontos.

| Spalte | Typ | Bedeutung |
|--------|-----|-----------|
| date | TEXT | Sammel-Datum (YYYY-MM-DD), Primärschlüssel |
| username | TEXT | Instagram-Nutzername |
| followers | INTEGER | Follower-Zahl |
| media_count | INTEGER | Gesamtanzahl Posts/Reels |
| collected_at | TEXT | Zeitstempel der Sammlung (ISO) |

---

## Häufige Abfragen

```python
import sqlite3
conn = sqlite3.connect("data/data.db")
conn.row_factory = sqlite3.Row
```

**Aktuellste YouTube-Zahlen:**
```sql
SELECT * FROM youtube_daily ORDER BY date DESC LIMIT 1
```

**YouTube-Trend letzte 30 Tage:**
```sql
SELECT date, subscribers, total_views FROM youtube_daily
ORDER BY date DESC LIMIT 30
```

**Wachstum diese Woche (Abonnenten heute vs. vor 7 Tagen):**
```sql
SELECT
  (SELECT subscribers FROM youtube_daily ORDER BY date DESC LIMIT 1) -
  (SELECT subscribers FROM youtube_daily ORDER BY date DESC LIMIT 1 OFFSET 7) as wachstum_7d
```

**Top-5 Videos nach Views:**
```sql
SELECT title, views, likes, published_date FROM youtube_videos
ORDER BY views DESC LIMIT 5
```

**Aktuellste Instagram-Zahlen:**
```sql
SELECT * FROM instagram_daily ORDER BY date DESC LIMIT 1
```

**Monatsvergleich (Views diesen vs. letzten Monat):**
```sql
SELECT
  strftime('%Y-%m', date) as monat,
  AVG(views_30d) as avg_views
FROM youtube_daily
GROUP BY monat
ORDER BY monat DESC LIMIT 2
```
