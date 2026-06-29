#!/usr/bin/env python3
"""
Kommentar-Responder — holt Kommentare von YouTube + Instagram und antwortet automatisch.
Limit: max 5 Antworten pro Lauf, nur auf Kommentare ohne bisherige Antwort.
Start: python3 scripts/jarvis/comment_responder.py
Läuft automatisch täglich um 12:00 Uhr (via systemd).
"""

import os
import sys
import pickle
import requests
import anthropic
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
DATEN_TOKEN = BASE_DIR / "credentials" / "youtube_daten_token.pickle"

MAX_REPLIES_PER_RUN = 5


def generate_reply(comment_text, video_topic, language="de"):
    """Generiert eine authentische Antwort auf einen Kommentar."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    if language == "de":
        prompt = (
            f"Du bist der Betreiber des Kanals MINDWAVE (Motivation, Fakten, Psychologie, Finanzen). "
            f"Antworte auf diesen Kommentar authentisch, freundlich und kurz (max 2 Sätze). "
            f"Kein 'Hey' oder übertriebene Floskeln. Keine Emojis außer 1 passendes am Ende.\n\n"
            f"Kommentar: {comment_text}"
        )
    else:
        prompt = (
            f"You are the creator of MINDWAVE channel (motivation, facts, psychology, finance). "
            f"Reply to this comment authentically, friendly, and briefly (max 2 sentences). "
            f"No 'Hey' or excessive filler. Max 1 fitting emoji at the end.\n\n"
            f"Comment: {comment_text}"
        )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def reply_youtube_comments():
    """Holt unbeantworte YouTube-Kommentare und antwortet darauf."""
    replied = 0
    try:
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        with open(DATEN_TOKEN, "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        yt = build("youtube", "v3", credentials=creds)

        # Kommentare der letzten Videos holen
        threads = yt.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId="mine",
            maxResults=20,
            order="time",
        ).execute()

        for thread in threads.get("items", []):
            if replied >= MAX_REPLIES_PER_RUN:
                break
            snippet = thread["snippet"]["topLevelComment"]["snippet"]
            # Nur unbeantwortete Kommentare
            if thread["snippet"].get("totalReplyCount", 0) > 0:
                continue
            comment_text = snippet.get("textDisplay", "")
            if not comment_text or len(comment_text) < 5:
                continue

            reply = generate_reply(comment_text, "", "de")
            try:
                yt.comments().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "parentId": thread["id"],
                            "textOriginal": reply,
                        }
                    }
                ).execute()
                print(f"[comment] YouTube beantwortet: '{comment_text[:50]}' → '{reply[:60]}'")
                replied += 1
            except Exception as e:
                print(f"[comment] YouTube-Antwort fehlgeschlagen: {e}")

    except Exception as e:
        print(f"[comment] YouTube-Kommentare fehlgeschlagen: {e}")
    return replied


def reply_instagram_comments():
    """Holt unbeantwortete Instagram-Kommentare und antwortet darauf."""
    replied = 0
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return 0
    try:
        # Letzte 10 Medien holen
        media_resp = requests.get(
            f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media",
            params={"fields": "id,caption", "limit": 5, "access_token": META_ACCESS_TOKEN},
            timeout=15,
        )
        if media_resp.status_code != 200:
            return 0

        for media in media_resp.json().get("data", []):
            if replied >= MAX_REPLIES_PER_RUN:
                break
            media_id = media["id"]

            # Kommentare zu diesem Post
            comments_resp = requests.get(
                f"https://graph.instagram.com/v21.0/{media_id}/comments",
                params={"fields": "id,text,replies", "access_token": META_ACCESS_TOKEN},
                timeout=15,
            )
            if comments_resp.status_code != 200:
                continue

            for comment in comments_resp.json().get("data", []):
                if replied >= MAX_REPLIES_PER_RUN:
                    break
                # Nur unbeantwortete
                if comment.get("replies", {}).get("data"):
                    continue
                comment_text = comment.get("text", "")
                if not comment_text or len(comment_text) < 5:
                    continue

                reply = generate_reply(comment_text, "", "de")
                try:
                    requests.post(
                        f"https://graph.instagram.com/v21.0/{comment['id']}/replies",
                        params={"message": reply, "access_token": META_ACCESS_TOKEN},
                        timeout=15,
                    )
                    print(f"[comment] Instagram beantwortet: '{comment_text[:50]}' → '{reply[:60]}'")
                    replied += 1
                except Exception as e:
                    print(f"[comment] Instagram-Antwort fehlgeschlagen: {e}")

    except Exception as e:
        print(f"[comment] Instagram-Kommentare fehlgeschlagen: {e}")
    return replied


def main():
    print("[comment] Starte Kommentar-Responder...")
    yt_count = reply_youtube_comments()
    ig_count = reply_instagram_comments()
    print(f"[comment] Fertig: {yt_count} YouTube + {ig_count} Instagram Antworten")


if __name__ == "__main__":
    main()
