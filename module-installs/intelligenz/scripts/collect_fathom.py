"""
Intelligenz: Fathom Meeting-Mitschrift-Sammler.

Zieht Meeting-Mitschriften ueber die Fathom REST API.
Gibt eine Liste von Meeting-Dicts zurueck, die direkt in db.write_meetings() passen.

Aufruf:
    python scripts/collect_fathom.py              # letzte 7 Tage
    python scripts/collect_fathom.py --days 30    # letzte 30 Tage
"""

import os
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

FATHOM_API = "https://api.fathom.ai/external/v1"


def _get_headers() -> dict:
    api_key = os.getenv("FATHOM_API_KEY")
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}


def collect(days: int = 7) -> list[dict]:
    """
    Fathom-Aufzeichnungen der letzten N Tage einsammeln.

    Gibt eine Liste von Meeting-Dicts zurueck, die direkt in db.write_meetings() passen.
    """
    api_key = os.getenv("FATHOM_API_KEY")
    if not api_key:
        print("Uebersprungen: FATHOM_API_KEY nicht in .env gesetzt")
        return []

    headers = _get_headers()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Schritt 1: Meetings mit Mitschrift und Zusammenfassung holen
    meetings_data = []
    cursor = None

    while True:
        params = {
            "created_after": since,
            "include_summary": "true",
            "include_transcript": "true",
            "include_action_items": "true",
        }
        if cursor:
            params["cursor"] = cursor

        try:
            resp = requests.get(
                f"{FATHOM_API}/meetings",
                headers=headers,
                params=params,
                timeout=60,
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unbekannt"
            print(f"Fehler: Fathom API hat HTTP {status} zurueckgegeben.")
            if status == 401:
                print("  -> Dein API-Key zieht nicht. Pruef Settings -> Integrations -> API in Fathom")
            return []
        except requests.exceptions.ConnectionError:
            print("Fehler: Keine Verbindung zu Fathom. Pruef deine Internetverbindung.")
            return []

        data = resp.json()

        # Fathom liefert mal eine Liste, mal ein paginiertes Objekt
        if isinstance(data, list):
            meetings_data.extend(data)
            break
        elif isinstance(data, dict):
            meetings_data.extend(data.get("meetings", data.get("data", [])))
            cursor = data.get("next_cursor") or data.get("cursor")
            if not cursor:
                break
        else:
            break

    # Schritt 2: Ins Standard-Meeting-Format giessen
    meetings = []
    for m in meetings_data:
        meeting_id = str(m.get("id", ""))
        if not meeting_id:
            continue

        # Mitschrift-Text aus Fathom-Format aufbauen
        # Fathom liefert Array von {speaker: {display_name}, text, timestamp}
        transcript_items = m.get("transcript", [])
        transcript_lines = []
        if isinstance(transcript_items, list):
            for item in transcript_items:
                speaker = "Unbekannt"
                if isinstance(item.get("speaker"), dict):
                    speaker = item["speaker"].get("display_name", "Unbekannt")
                elif isinstance(item.get("speaker"), str):
                    speaker = item["speaker"]
                text = item.get("text", "").strip()
                if text:
                    transcript_lines.append(f"[{speaker}] {text}")
        transcript_text = "\n".join(transcript_lines)

        # Teilnehmer aus den Sprechern
        speakers = set()
        if isinstance(transcript_items, list):
            for item in transcript_items:
                if isinstance(item.get("speaker"), dict):
                    name = item["speaker"].get("display_name")
                    email = item["speaker"].get("matched_calendar_invitee_email")
                    if name or email:
                        speakers.add(json.dumps({"name": name, "email": email}))
        participants = json.dumps([json.loads(s) for s in speakers]) if speakers else "[]"

        # Zusammenfassung
        summary = m.get("summary", "")

        # Action Items
        action_items = m.get("action_items", [])
        action_items_raw = json.dumps(action_items) if action_items else None

        # Datum
        created_at = m.get("created_at") or m.get("date") or ""
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
                start_time = dt.strftime("%H:%M:%S")
            except (ValueError, TypeError):
                date_str = str(created_at)[:10]
                start_time = None
        else:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            start_time = None

        # Dauer
        duration_minutes = m.get("duration_minutes") or m.get("duration")
        if duration_minutes and isinstance(duration_minutes, (int, float)):
            if duration_minutes > 1000:
                # Wahrscheinlich in Sekunden
                duration_minutes = round(duration_minutes / 60)

        meetings.append({
            "meeting_id": f"fathom_{meeting_id}",
            "source": "fathom",
            "title": m.get("title") or m.get("name") or "Unbenanntes Meeting",
            "date": date_str,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "participants": participants,
            "transcript_text": transcript_text,
            "summary": summary if isinstance(summary, str) else json.dumps(summary),
            "action_items_raw": action_items_raw,
            "external_url": m.get("url") or m.get("share_url"),
        })

    print(f"Fathom: {len(meetings)} Meetings der letzten {days} Tage gesammelt")
    return meetings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fathom-Mitschriften einsammeln")
    parser.add_argument("--days", type=int, default=7, help="Wie viele Tage zurueck (Standard: 7)")
    args = parser.parse_args()

    meetings = collect(days=args.days)
    if meetings:
        print(f"\nBeispiel-Meeting: {meetings[0]['title']} ({meetings[0]['date']})")
        print(f"  Mitschrift-Laenge: {len(meetings[0].get('transcript_text', ''))} Zeichen")
    else:
        print("Keine Meetings gesammelt.")
