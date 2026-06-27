"""
Intelligenz: Slack-Nachrichten-Sammler.

Zieht die letzten 24 Stunden aus allen oeffentlichen Kanaelen deiner Slack-Workspaces.
Loest User-IDs in Anzeigenamen auf und expandiert Thread-Antworten.

WICHTIG: Der Slack-Bot sieht nur Kanaele, in die er eingeladen wurde.
Nach dem Setup in jeden gewuenschten Kanal gehen und /invite @DeinBot tippen.

Aufruf:
    python scripts/collect_slack.py
"""

import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SLACK_API = "https://slack.com/api"

# Rate Limit: rund 50 Requests pro Minute fuer Tier-3-Methoden
RATE_LIMIT_SLEEP = 0.5


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _api_call(token: str, method: str, params: dict = None) -> dict:
    """Slack-API-Aufruf."""
    resp = requests.get(
        f"{SLACK_API}/{method}",
        headers=_headers(token),
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        error = data.get("error", "unknown_error")
        if error == "not_authed" or error == "invalid_auth":
            raise RuntimeError(
                f"Slack-Auth fehlgeschlagen. Token ungueltig oder abgelaufen.\n"
                f"  -> Geh auf https://api.slack.com/apps -> deine App -> OAuth & Permissions\n"
                f"  -> Bot User OAuth Token kopieren und in .env aktualisieren"
            )
        if error == "channel_not_found":
            return data  # Nicht fatal, Kanal ueberspringen
        raise RuntimeError(f"Slack-API-Fehler ({method}): {error}")
    return data


def _get_channels(token: str) -> list[dict]:
    """Alle Kanaele holen, die der Bot sieht. Mit Pagination."""
    channels = []
    cursor = None
    while True:
        params = {"types": "public_channel", "limit": 200, "exclude_archived": "true"}
        if cursor:
            params["cursor"] = cursor
        data = _api_call(token, "conversations.list", params)
        channels.extend(data.get("channels", []))
        cursor = data.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(RATE_LIMIT_SLEEP)
    return channels


def _get_history(token: str, channel_id: str, oldest: str) -> list[dict]:
    """Nachrichten eines Kanals seit Timestamp holen."""
    messages = []
    cursor = None
    while True:
        params = {"channel": channel_id, "oldest": oldest, "limit": 200}
        if cursor:
            params["cursor"] = cursor
        try:
            data = _api_call(token, "conversations.history", params)
        except RuntimeError:
            break  # Kanaele, die wir nicht lesen koennen, ueberspringen
        messages.extend(data.get("messages", []))
        cursor = data.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(RATE_LIMIT_SLEEP)
    return messages


def _get_thread_replies(token: str, channel_id: str, thread_ts: str) -> list[dict]:
    """Alle Antworten in einem Thread holen."""
    try:
        data = _api_call(token, "conversations.replies", {
            "channel": channel_id, "ts": thread_ts, "limit": 200,
        })
        msgs = data.get("messages", [])
        return [m for m in msgs if m.get("ts") != thread_ts]
    except Exception:
        return []


def _resolve_users(token: str, user_ids: set[str]) -> dict[str, str]:
    """User-IDs in Anzeigenamen aufloesen."""
    cache = {}
    for uid in user_ids:
        if not uid or uid in cache:
            continue
        try:
            data = _api_call(token, "users.info", {"user": uid})
            user = data.get("user", {})
            name = (user.get("profile", {}).get("display_name")
                    or user.get("real_name")
                    or user.get("name")
                    or uid)
            cache[uid] = name
        except Exception:
            cache[uid] = uid
        time.sleep(0.2)
    return cache


def _collect_workspace(workspace_name: str, token: str) -> dict:
    """Letzte 24 Stunden aus einem Workspace sammeln."""
    oldest = str((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())

    channels = _get_channels(token)
    all_messages = []
    user_ids = set()
    threads_expanded = 0

    # Bot- und System-Subtypes ueberspringen
    skip_subtypes = {"channel_join", "channel_leave", "channel_topic",
                     "channel_purpose", "channel_name"}

    for ch in channels:
        ch_id = ch["id"]
        ch_name = ch.get("name", "")
        time.sleep(RATE_LIMIT_SLEEP)

        messages = _get_history(token, ch_id, oldest)

        for msg in messages:
            subtype = msg.get("subtype", "")
            if subtype in skip_subtypes:
                continue

            uid = msg.get("user", "")
            if uid:
                user_ids.add(uid)

            reactions = None
            if msg.get("reactions"):
                reactions = [{"name": r["name"], "count": r["count"]}
                             for r in msg["reactions"]]

            reply_count = msg.get("reply_count", 0)
            msg_record = {
                "workspace": workspace_name,
                "channel_id": ch_id,
                "channel_name": ch_name,
                "user_id": uid,
                "ts": msg["ts"],
                "thread_ts": msg.get("thread_ts") if msg.get("thread_ts") != msg["ts"] else None,
                "message_type": subtype or "message",
                "text": msg.get("text", ""),
                "has_files": 1 if msg.get("files") else 0,
                "reactions": reactions,
                "reply_count": reply_count,
            }
            all_messages.append(msg_record)

            # Threads expandieren
            if reply_count > 0:
                replies = _get_thread_replies(token, ch_id, msg["ts"])
                threads_expanded += 1
                for reply in replies:
                    r_uid = reply.get("user", "")
                    if r_uid:
                        user_ids.add(r_uid)
                    r_reactions = None
                    if reply.get("reactions"):
                        r_reactions = [{"name": r["name"], "count": r["count"]}
                                       for r in reply["reactions"]]
                    all_messages.append({
                        "workspace": workspace_name,
                        "channel_id": ch_id,
                        "channel_name": ch_name,
                        "user_id": r_uid,
                        "ts": reply["ts"],
                        "thread_ts": reply.get("thread_ts"),
                        "message_type": reply.get("subtype", "message"),
                        "text": reply.get("text", ""),
                        "has_files": 1 if reply.get("files") else 0,
                        "reactions": r_reactions,
                        "reply_count": 0,
                    })
                time.sleep(RATE_LIMIT_SLEEP)

    # User-Namen aufloesen
    user_map = _resolve_users(token, user_ids)
    for msg in all_messages:
        msg["user_name"] = user_map.get(msg.get("user_id", ""), msg.get("user_id"))

    return {
        "workspace": workspace_name,
        "channels_read": len(channels),
        "messages_collected": len(all_messages),
        "threads_expanded": threads_expanded,
        "messages": all_messages,
    }


def collect() -> tuple[list[dict], dict]:
    """Slack-Nachrichten aus allen konfigurierten Workspaces sammeln.

    Findet Workspace-Tokens automatisch. Jede Umgebungsvariable, die mit
    SLACK_TOKEN_ anfaengt, gilt als eigener Workspace. Der Teil nach
    SLACK_TOKEN_ wird zum Workspace-Namen.

    Gibt zurueck:
        (nachrichten_liste, statistik_dict)
    """
    # Alle SLACK_TOKEN_*-Variablen finden
    tokens = {}
    for key, value in os.environ.items():
        if key.startswith("SLACK_TOKEN_") and value and value.strip():
            workspace_name = key.replace("SLACK_TOKEN_", "").lower()
            tokens[workspace_name] = value.strip()

    if not tokens:
        print("Uebersprungen: kein Slack-Token gefunden. Setz SLACK_TOKEN_MAIN (oder aehnlich) in .env")
        return [], {}

    all_messages = []
    stats = {}

    for ws_name, token in tokens.items():
        try:
            print(f"Sammle Slack-Workspace: {ws_name}...")
            result = _collect_workspace(ws_name, token)
            all_messages.extend(result["messages"])
            stats[ws_name] = {
                "channels": result["channels_read"],
                "messages": result["messages_collected"],
                "threads": result["threads_expanded"],
            }
            print(f"  -> {result['messages_collected']} Nachrichten aus {result['channels_read']} Kanaelen")
        except Exception as e:
            print(f"  -> Fehler bei {ws_name}: {e}")
            stats[ws_name] = {"error": str(e)}

    return all_messages, stats


if __name__ == "__main__":
    messages, stats = collect()
    print(f"\nGesamt: {len(messages)} Nachrichten")
    print(f"Stand: {json.dumps(stats, indent=2)}")
