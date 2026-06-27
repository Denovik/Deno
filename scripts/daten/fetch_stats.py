#!/usr/bin/env python3
"""
Jarvis Daten-Abruf — holt echte Zahlen von YouTube und Instagram
und schreibt sie in context/current-data.md.

Start: python3 scripts/daten/fetch_stats.py
Läuft auch täglich automatisch um 08:00 Uhr (via launchd).
"""

import os
import sys
import re
import pickle
from datetime import datetime
from pathlib import Path

# Projektpfad aufsetzen
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts" / "jarvis"))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
TOKEN_PATH = BASE_DIR / "credentials" / "youtube_token.pickle"
CLIENT_SECRET_PATH = BASE_DIR / "credentials" / "youtube_client_secret.json"
CURRENT_DATA_PATH = BASE_DIR / "context" / "current-data.md"

TODAY = datetime.now().strftime("%d.%m.%Y")


# ── YouTube ────────────────────────────────────────────────────────────────────

def fetch_youtube_stats() -> dict:
    """Holt Abonnenten und Gesamt-Views vom Mindwave-Kanal."""
    try:
        import pickle as pk
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        SCOPES = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
        ]
        DATEN_TOKEN = BASE_DIR / "credentials" / "youtube_daten_token.pickle"

        creds = None
        if DATEN_TOKEN.exists():
            with open(DATEN_TOKEN, "rb") as f:
                creds = pk.load(f)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(DATEN_TOKEN, "wb") as f:
                pk.dump(creds, f)

        if not creds or not creds.valid:
            if CLIENT_SECRET_PATH.exists():
                flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
                creds = flow.run_local_server(port=0)
                with open(DATEN_TOKEN, "wb") as f:
                    pk.dump(creds, f)
                print("[daten] YouTube-Zugang eingerichtet und gespeichert.")
            else:
                print("[daten] YouTube Client Secret fehlt — YouTube-Zahlen übersprungen.")
                return {}

        youtube = build("youtube", "v3", credentials=creds)
        resp = youtube.channels().list(part="statistics", mine=True).execute()
        stats = resp["items"][0]["statistics"]
        return {
            "yt_abonnenten": int(stats.get("subscriberCount", 0)),
            "yt_views_gesamt": int(stats.get("viewCount", 0)),
            "yt_videos_gesamt": int(stats.get("videoCount", 0)),
        }
    except Exception as e:
        print(f"[daten] YouTube-Abruf fehlgeschlagen: {e}")
        return {}


# ── Instagram ──────────────────────────────────────────────────────────────────

def fetch_instagram_stats() -> dict:
    """Holt Follower-Zahl vom mind.wave26-Konto."""
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("[daten] META_ACCESS_TOKEN oder INSTAGRAM_ACCOUNT_ID fehlt — Instagram übersprungen.")
        return {}
    try:
        import requests
        resp = requests.get(
            f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}",
            params={"fields": "followers_count,media_count", "access_token": META_ACCESS_TOKEN},
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"[daten] Instagram-Fehler {resp.status_code}: {resp.text[:100]}")
            return {}
        d = resp.json()
        return {
            "ig_follower": d.get("followers_count", "unbekannt"),
            "ig_posts": d.get("media_count", "unbekannt"),
        }
    except Exception as e:
        print(f"[daten] Instagram-Abruf fehlgeschlagen: {e}")
        return {}


# ── current-data.md aktualisieren ─────────────────────────────────────────────

def update_current_data(yt: dict, ig: dict):
    """Schreibt die neuen Zahlen in die Kennzahlen-Tabelle in context/current-data.md."""
    if not CURRENT_DATA_PATH.exists():
        print(f"[daten] {CURRENT_DATA_PATH} nicht gefunden.")
        return

    content = CURRENT_DATA_PATH.read_text(encoding="utf-8")

    # Stand-Datum aktualisieren
    content = re.sub(r"\*\*Stand:\*\*.*", f"**Stand:** {TODAY} (automatisch abgerufen)", content)

    def replace_row(text, label, new_value, note=""):
        pattern = rf"(\|\s*{re.escape(label)}\s*\|)[^\|]*\|[^\|]*\|"
        replacement = rf"\1 {new_value} | {note} |" if note else rf"\1 {new_value} |  |"
        return re.sub(pattern, replacement, text)

    if yt:
        content = replace_row(content, "YouTube Abonnenten",
                               str(yt.get("yt_abonnenten", "?")),
                               f"Stand {TODAY}")
        content = replace_row(content, "YouTube Views gesamt",
                               str(yt.get("yt_views_gesamt", "?")),
                               f"Stand {TODAY}")

    if ig:
        content = replace_row(content, "Instagram Follower",
                               str(ig.get("ig_follower", "?")),
                               f"Stand {TODAY}")
        content = replace_row(content, "Instagram Posts",
                               str(ig.get("ig_posts", "?")),
                               f"Stand {TODAY}")

    CURRENT_DATA_PATH.write_text(content, encoding="utf-8")


# ── Haupt-Ablauf ───────────────────────────────────────────────────────────────

def main():
    print(f"[daten] Starte Daten-Abruf ({TODAY}) ...")

    yt = fetch_youtube_stats()
    if yt:
        print(f"[daten] YouTube → {yt['yt_abonnenten']} Abonnenten, {yt['yt_views_gesamt']} Views gesamt")
    else:
        print("[daten] YouTube → keine Daten")

    ig = fetch_instagram_stats()
    if ig:
        print(f"[daten] Instagram → {ig['ig_follower']} Follower, {ig['ig_posts']} Posts")
    else:
        print("[daten] Instagram → keine Daten")

    if yt or ig:
        update_current_data(yt, ig)
        print(f"[daten] ✅ context/current-data.md aktualisiert")
    else:
        print("[daten] Keine Zahlen abgerufen, current-data.md unverändert.")


if __name__ == "__main__":
    main()
