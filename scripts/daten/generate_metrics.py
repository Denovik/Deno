"""
Daten: Kennzahlen-Generator

Liest die Datenbank und erzeugt eine lesbare key-metrics.md.
Diese Datei wird vom /prime-Befehl geladen, damit dein Mitarbeiter
immer frische Zahlen sieht.

Nutzung:
    python scripts/daten/generate_metrics.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = WORKSPACE_ROOT / "data" / "data.db"
OUTPUT_PATH = WORKSPACE_ROOT / "context" / "group" / "key-metrics.md"


def fmt_number(value, prefix="", suffix=""):
    if value is None:
        return "Keine Daten"
    if isinstance(value, float):
        return f"{prefix}{value:,.0f}{suffix}"
    return f"{prefix}{value:,}{suffix}"


def fmt_currency(value, symbol="€"):
    if value is None:
        return "Keine Daten"
    return f"{symbol}{value:,.0f}"


def fmt_pct(value):
    if value is None:
        return "Keine Daten"
    return f"{value:.1f}%"


def query_one(conn, sql):
    try:
        row = conn.execute(sql).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def query_all(conn, sql):
    try:
        return [dict(r) for r in conn.execute(sql).fetchall()]
    except Exception:
        return []


def table_exists(conn, name):
    r = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return r is not None


# ============================================================
# SEKTIONS-GENERATOREN
# ============================================================

def section_youtube(conn):
    """YouTube Channel-Zahlen."""
    if not table_exists(conn, "youtube_daily"):
        return []
    lines = ["## YouTube (Mindwave)"]
    row = query_one(conn, "SELECT * FROM youtube_daily ORDER BY date DESC LIMIT 1")
    if row:
        lines.append(f"| Kennzahl | Wert | Stand |")
        lines.append(f"|----------|------|-------|")
        lines.append(f"| Abonnenten | {fmt_number(row.get('subscribers'))} | {row.get('date', '?')} |")
        lines.append(f"| Views gesamt | {fmt_number(row.get('total_views'))} | {row.get('date', '?')} |")
        lines.append(f"| Videos | {fmt_number(row.get('total_videos'))} | {row.get('date', '?')} |")
        if row.get('views_30d') is not None:
            lines.append(f"| Views (30 Tage) | {fmt_number(row.get('views_30d'))} | {row.get('date', '?')} |")
        if row.get('videos_published_30d') is not None:
            lines.append(f"| Neue Videos (30 Tage) | {fmt_number(row.get('videos_published_30d'))} | {row.get('date', '?')} |")
    lines.append("")

    # Top-Videos
    top_videos = query_all(conn, """
        SELECT title, views, likes, published_date
        FROM youtube_videos
        ORDER BY views DESC LIMIT 5
    """)
    if top_videos:
        lines.append("### Top-Videos")
        lines.append("| Titel | Views | Likes | Datum |")
        lines.append("|-------|-------|-------|-------|")
        for v in top_videos:
            title = (v.get('title', '') or '')[:40]
            lines.append(f"| {title} | {fmt_number(v.get('views'))} | {fmt_number(v.get('likes'))} | {v.get('published_date', '?')} |")
        lines.append("")

    return lines


def section_youtube_monetization(conn):
    """YouTube Partner Program Fortschritt."""
    if not table_exists(conn, "youtube_daily"):
        return []
    row = query_one(conn, "SELECT * FROM youtube_daily ORDER BY date DESC LIMIT 1")
    if not row:
        return []

    YPP_SUBSCRIBERS_THRESHOLD = 500
    YPP_WATCHTIME_THRESHOLD = 3000  # Stunden

    subscribers = row.get("subscribers") or 0
    watchtime = row.get("watchtime_hours_est") or 0

    sub_pct = min(100, round(subscribers / YPP_SUBSCRIBERS_THRESHOLD * 100, 1))
    wt_pct = min(100, round(watchtime / YPP_WATCHTIME_THRESHOLD * 100, 1))
    overall_pct = round((sub_pct + wt_pct) / 2, 1)

    lines = [
        "## YouTube Monetarisierung",
        f"- Abonnenten: {subscribers:,} / {YPP_SUBSCRIBERS_THRESHOLD:,} (YPP-Schwelle) — {sub_pct}%",
        f"- Watchtime (geschätzt): {watchtime:,.0f} / {YPP_WATCHTIME_THRESHOLD:,} Stunden — {wt_pct}%",
        f"- Gesamtfortschritt: {overall_pct}%",
        "",
    ]
    return lines


def section_instagram(conn):
    """Instagram Konto-Zahlen."""
    if not table_exists(conn, "instagram_daily"):
        return []
    lines = ["## Instagram (mind.wave26)"]
    row = query_one(conn, "SELECT * FROM instagram_daily ORDER BY date DESC LIMIT 1")
    if row:
        lines.append(f"| Kennzahl | Wert | Stand |")
        lines.append(f"|----------|------|-------|")
        lines.append(f"| Follower | {fmt_number(row.get('followers'))} | {row.get('date', '?')} |")
        lines.append(f"| Posts gesamt | {fmt_number(row.get('media_count'))} | {row.get('date', '?')} |")
    lines.append("")
    return lines


# ============================================================
# HAUPT-GENERATOR
# ============================================================

SECTIONS = [
    section_youtube,
    section_youtube_monetization,
    section_instagram,
]


def generate(conn):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# Kennzahlen",
        "",
        f"> Automatisch aus der Datenbank erzeugt. Letztes Update: {today}",
        f"> Quelle: `data/data.db` | Neu erzeugen: `python scripts/daten/generate_metrics.py`",
        "",
    ]

    for section_fn in SECTIONS:
        try:
            section_lines = section_fn(conn)
            if section_lines:
                lines.extend(section_lines)
        except Exception as e:
            lines.append(f"<!-- Fehler in {section_fn.__name__}: {e} -->")
            lines.append("")

    lines.append("## Datenfrische")
    lines.append("| Quelle | Letzter Datensatz | Status |")
    lines.append("|--------|-------------------|--------|")

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name != 'collection_log' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()

    date_columns = {"youtube_videos": "last_updated"}
    for t in tables:
        name = t["name"]
        date_col = date_columns.get(name, "date")
        try:
            row = conn.execute(f"SELECT MAX({date_col}) as d FROM {name}").fetchone()
            if row and row["d"]:
                lines.append(f"| {name} | {row['d']} | verbunden |")
            else:
                lines.append(f"| {name} | — | leer |")
        except Exception:
            lines.append(f"| {name} | — | keine Datums-Spalte |")

    lines.append("")
    return "\n".join(lines)


def main():
    if not DB_PATH.exists():
        print(f"Datenbank nicht gefunden unter {DB_PATH}")
        print("Erst sammeln: python scripts/daten/collect.py")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    content = generate(conn)
    conn.close()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content)
    print(f"Kennzahlen geschrieben nach: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
