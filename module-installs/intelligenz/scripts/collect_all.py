"""
Intelligenz: Sammler-Orchestrator.

Faehrt alle konfigurierten Sammler (Meetings + Slack), schreibt in die Datenbank
und ordnet neue Meetings ein. Dieses Skript haengt am Zeitplan.

Aufruf:
    python scripts/collect_all.py                   # alle Sammler
    python scripts/collect_all.py --meetings-only   # nur Meetings
    python scripts/collect_all.py --slack-only       # nur Slack
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

# Sicherstellen, dass scripts/ im Pfad ist
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import init_db, write_meetings, write_slack, get_meeting_stats


def run(meetings_only: bool = False, slack_only: bool = False):
    """Alle konfigurierten Sammler fahren und in die Datenbank schreiben."""
    print(f"Intelligenz-Sammlung gestartet am {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    conn = init_db()

    # --- Meetings ---
    if not slack_only:
        meeting_records = []

        # Fireflies versuchen
        try:
            from collect_fireflies import collect as collect_fireflies
            ff_meetings = collect_fireflies()
            if ff_meetings:
                meeting_records.extend(ff_meetings)
        except ImportError:
            pass
        except Exception as e:
            print(f"Fireflies-Fehler: {e}")

        # Fathom versuchen
        try:
            from collect_fathom import collect as collect_fathom
            fathom_meetings = collect_fathom()
            if fathom_meetings:
                meeting_records.extend(fathom_meetings)
        except ImportError:
            pass
        except Exception as e:
            print(f"Fathom-Fehler: {e}")

        # In die Datenbank schreiben
        if meeting_records:
            count = write_meetings(conn, meeting_records)
            print(f"Meetings: {count} Datensaetze geschrieben")
        else:
            print("Meetings: nichts Neues gesammelt")

        # Neue Meetings einordnen
        try:
            from classify import classify_all
            classified = classify_all(conn)
            if classified:
                print(f"Einordnung: {classified} Meetings klassifiziert")
        except Exception as e:
            print(f"Einordnungs-Fehler: {e}")

    # --- Slack ---
    if not meetings_only:
        try:
            from collect_slack import collect as collect_slack
            messages, stats = collect_slack()
            if messages:
                count = write_slack(conn, messages)
                print(f"Slack: {count} Nachrichten geschrieben")
            else:
                print("Slack: nichts gesammelt")
        except Exception as e:
            print(f"Slack-Fehler: {e}")

    # --- Zusammenfassung ---
    print("\n" + "=" * 60)
    stats = get_meeting_stats(conn)
    print(f"Datenbank-Stand:")
    print(f"  Meetings:           {stats['total_meetings']}")
    print(f"  Slack-Nachrichten:  {stats['total_slack_messages']}")
    print(f"  Team-Mitglieder:    {stats['team_members']}")
    if stats['latest_meeting_date']:
        print(f"  Letztes Meeting:    {stats['latest_meeting_date']}")
    print("=" * 60)

    conn.close()
    print("Fertig.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intelligenz, Meetings und Nachrichten sammeln")
    parser.add_argument("--meetings-only", action="store_true", help="Nur Meetings")
    parser.add_argument("--slack-only", action="store_true", help="Nur Slack")
    args = parser.parse_args()

    run(meetings_only=args.meetings_only, slack_only=args.slack_only)
