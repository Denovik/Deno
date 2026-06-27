"""
Intelligenz: Meeting-Einordnung.

Ordnet Meetings nach Abteilung oder Stream ein, basierend auf den Teilnehmer-Emails
und dem Team-Register. Wenn das Register leer ist, landet alles im "general"-Topf.

Aufruf:
    python scripts/classify.py                  # nur unklassifizierte Meetings
    python scripts/classify.py --reclassify     # alles neu einordnen
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Import aus dem Schwester-Modul
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from db import get_connection


def classify_meeting(conn, meeting: dict, department_streams: dict) -> dict:
    """Ein einzelnes Meeting nach Stream einordnen.

    Args:
        conn: Datenbank-Verbindung
        meeting: Dict mit participants, title, meeting_id
        department_streams: Abteilung -> Stream-Label
            z.B. {"vertrieb": "vertrieb", "produkt": "produkt", "leitung": "intern"}
            Wenn leer, landet alles in "general".

    Returns:
        {"stream": str, "call_type": str, "reason": str}
    """
    participants_json = meeting.get("participants", "")
    title = (meeting.get("title") or "").strip()

    # Teilnehmer parsen
    try:
        participants = json.loads(participants_json) if participants_json else []
    except (json.JSONDecodeError, TypeError):
        participants = []

    # Jeden Teilnehmer im Team-Register nachschlagen
    staff_found = []
    external_found = []

    for p in participants:
        email = None
        name = None
        if isinstance(p, dict):
            email = p.get("email", "")
            name = p.get("name", "")
        elif isinstance(p, str):
            if "@" in p:
                email = p
            else:
                name = p

        if email:
            row = conn.execute(
                "SELECT * FROM staff_registry WHERE LOWER(email) = LOWER(?)",
                (email.strip(),)
            ).fetchone()
            if row:
                staff_found.append(dict(row))
            else:
                external_found.append({"email": email, "name": name or email})
        elif name:
            row = conn.execute(
                "SELECT * FROM staff_registry WHERE LOWER(name) = LOWER(?)",
                (name.strip(),)
            ).fetchone()
            if row:
                staff_found.append(dict(row))
            else:
                external_found.append({"name": name})

    # Wenn keine Streams konfiguriert sind, alles -> "general"
    if not department_streams:
        call_type = "meeting"
        if len(staff_found) >= 2 and len(external_found) == 0:
            call_type = "team_meeting"
        elif len(staff_found) >= 1 and len(external_found) >= 1:
            call_type = "one_on_one"
        return {"stream": "general", "call_type": call_type, "reason": "keine_abteilungen_konfiguriert"}

    # Call-Typ bestimmen
    staff_count = len(staff_found)
    external_count = len(external_found)

    if staff_count >= 2 and external_count == 0:
        call_type = "team_meeting"
    elif staff_count >= 1 and external_count >= 1:
        call_type = "one_on_one"
    elif staff_count == 0 and external_count >= 2:
        call_type = "external"
    else:
        call_type = "meeting"

    # Stream aus der Abteilung der Team-Mitglieder
    if staff_found:
        dept = staff_found[0].get("department", "general")
        stream = department_streams.get(dept, dept)
        staff_names = [s["name"] for s in staff_found]
        reason = f"abteilung:{dept} team:{', '.join(staff_names)}"
    elif title:
        stream = _classify_by_title(title, department_streams)
        reason = f"titel_heuristik:{title[:60]}"
    else:
        stream = "general"
        reason = "keine_teilnehmer_kein_titel"

    return {"stream": stream, "call_type": call_type, "reason": reason}


def _classify_by_title(title: str, department_streams: dict) -> str:
    """Fallback: ueber Titel-Stichwoerter einordnen."""
    title_lower = title.lower()

    # Abteilungs-Name im Titel?
    for dept in department_streams:
        if dept.lower() in title_lower:
            return department_streams[dept]

    # Gaengige Stichwoerter
    for keyword in ["vertrieb", "sales", "demo", "discovery", "qualifizierung"]:
        if keyword in title_lower:
            return department_streams.get("vertrieb", department_streams.get("sales", "vertrieb"))

    for keyword in ["standup", "sync", "team", "intern", "weekly", "woechentlich"]:
        if keyword in title_lower:
            return "team_meeting"

    return "general"


def get_department_streams(conn) -> dict:
    """Abteilung -> Stream aus dem Team-Register bauen.

    Gibt zum Beispiel {"vertrieb": "vertrieb", "produkt": "produkt"} zurueck,
    aus den unterschiedlichen Abteilungen im Register.
    """
    rows = conn.execute(
        "SELECT DISTINCT department FROM staff_registry WHERE is_active = 1"
    ).fetchall()
    if not rows:
        return {}
    # Jede Abteilung zeigt per Default auf sich selbst als Stream
    return {row["department"]: row["department"] for row in rows}


def classify_all(conn, reclassify: bool = False) -> int:
    """Alle (oder nur unklassifizierten) Meetings einordnen. Gibt die Anzahl zurueck."""
    department_streams = get_department_streams(conn)

    if reclassify:
        cursor = conn.execute("SELECT meeting_id, title, participants FROM meetings")
    else:
        cursor = conn.execute(
            "SELECT meeting_id, title, participants FROM meetings WHERE stream IS NULL"
        )

    meetings = [dict(row) for row in cursor.fetchall()]
    if not meetings:
        print("Keine Meetings zu klassifizieren.")
        return 0

    now = datetime.now(timezone.utc).isoformat()
    count = 0

    for meeting in meetings:
        result = classify_meeting(conn, meeting, department_streams)
        conn.execute(
            "UPDATE meetings SET stream = ?, call_type = ?, classified_at = ? "
            "WHERE meeting_id = ?",
            (result["stream"], result["call_type"], now, meeting["meeting_id"])
        )
        count += 1

    conn.commit()
    streams_summary = {}
    for m in meetings:
        r = classify_meeting(conn, m, department_streams)
        streams_summary[r["stream"]] = streams_summary.get(r["stream"], 0) + 1

    print(f"{count} Meetings klassifiziert:")
    for stream, ct in sorted(streams_summary.items()):
        print(f"  {stream}: {ct}")

    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Meetings nach Abteilung oder Stream einordnen")
    parser.add_argument("--reclassify", action="store_true",
                        help="Alles neu einordnen, nicht nur unklassifizierte")
    args = parser.parse_args()

    conn = get_connection()
    classify_all(conn, reclassify=args.reclassify)
    conn.close()
