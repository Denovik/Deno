#!/usr/bin/env python3
"""
Jarvis Intelligenz — analysiert deine Content-Performance und gibt Empfehlungen.

Start: python3 scripts/intelligenz/analyse.py
Läuft auch automatisch jeden Montag um 09:00 Uhr (via launchd).
"""

import os
import sys
import json
import pickle
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts" / "jarvis"))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

DATEN_TOKEN = BASE_DIR / "credentials" / "youtube_daten_token.pickle"
BERICHTE_DIR = BASE_DIR / "outputs" / "berichte"
CURRENT_DATA = BASE_DIR / "context" / "current-data.md"
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_DE = datetime.now().strftime("%d.%m.%Y")


# ── YouTube: letzte Videos abrufen ────────────────────────────────────────────

def fetch_youtube_videos() -> list:
    """Holt die letzten 10 YouTube-Videos mit Statistiken."""
    try:
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        with open(DATEN_TOKEN, "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(DATEN_TOKEN, "wb") as f:
                pickle.dump(creds, f)

        yt = build("youtube", "v3", credentials=creds)

        # Eigene Video-IDs holen
        search = yt.search().list(
            part="id,snippet", forMine=True, type="video",
            maxResults=10, order="date"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search.get("items", [])]
        if not video_ids:
            return []

        # Statistiken für diese Videos holen
        stats = yt.videos().list(
            part="snippet,statistics", id=",".join(video_ids)
        ).execute()

        videos = []
        for item in stats.get("items", []):
            s = item.get("statistics", {})
            videos.append({
                "titel": item["snippet"]["title"],
                "datum": item["snippet"]["publishedAt"][:10],
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "kommentare": int(s.get("commentCount", 0)),
            })
        return videos

    except Exception as e:
        print(f"[intelligenz] YouTube-Abruf fehlgeschlagen: {e}")
        return []


# ── Instagram: letzte Reels abrufen ───────────────────────────────────────────

def fetch_instagram_reels() -> list:
    """Holt die letzten 10 Instagram-Reels mit Performance-Daten."""
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return []
    try:
        import requests
        resp = requests.get(
            f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media",
            params={
                "fields": "id,caption,like_count,comments_count,timestamp,media_type",
                "limit": 10,
                "access_token": META_ACCESS_TOKEN,
            },
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"[intelligenz] Instagram-Fehler {resp.status_code}: {resp.text[:100]}")
            return []

        reels = []
        for item in resp.json().get("data", []):
            if item.get("media_type") in ("VIDEO", "REELS"):
                caption = (item.get("caption") or "")[:80]
                reels.append({
                    "titel": caption,
                    "datum": item.get("timestamp", "")[:10],
                    "likes": item.get("like_count", 0),
                    "kommentare": item.get("comments_count", 0),
                })
        return reels

    except Exception as e:
        print(f"[intelligenz] Instagram-Abruf fehlgeschlagen: {e}")
        return []


# ── Claude-Analyse ────────────────────────────────────────────────────────────

def analysiere(yt_videos: list, ig_reels: list) -> str:
    """Schickt die Performance-Daten an Claude und bekommt eine Analyse zurück."""
    import anthropic

    yt_text = "\n".join(
        f"- [{v['datum']}] \"{v['titel']}\" — {v['views']} Views, {v['likes']} Likes"
        for v in yt_videos
    ) or "Keine YouTube-Videos gefunden."

    ig_text = "\n".join(
        f"- [{r['datum']}] \"{r['titel']}\" — {r['likes']} Likes, {r['kommentare']} Kommentare"
        for r in ig_reels
    ) or "Keine Instagram-Reels gefunden."

    prompt = f"""Du analysierst die Content-Performance des Kanals "Mindwave" (Motivation + Fakten/Wissen, DE + EN).

## YouTube (letzte Videos)
{yt_text}

## Instagram (letzte Reels)
{ig_text}

Analysiere kurz und präzise auf Deutsch:
1. **Was funktioniert gut?** (Muster bei erfolgreichen Videos: Thema, Sprache, Titel-Stil)
2. **Was läuft unterdurchschnittlich?**
3. **3 konkrete Empfehlungen** für die nächste Woche (was soll Jarvis anders machen?)

Maximal 300 Wörter. Keine Einleitung, direkt zur Sache."""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ── Bericht speichern ─────────────────────────────────────────────────────────

def speichere_bericht(analyse: str, yt_videos: list, ig_reels: list):
    """Schreibt den Analyse-Bericht nach outputs/berichte/."""
    BERICHTE_DIR.mkdir(parents=True, exist_ok=True)
    pfad = BERICHTE_DIR / f"{TODAY}-performance-analyse.md"

    yt_tabelle = "\n".join(
        f"| {v['datum']} | {v['titel'][:50]} | {v['views']} | {v['likes']} |"
        for v in yt_videos
    ) or "| — | Keine Daten | — | — |"

    ig_tabelle = "\n".join(
        f"| {r['datum']} | {r['titel'][:50]} | {r['likes']} | {r['kommentare']} |"
        for r in ig_reels
    ) or "| — | Keine Daten | — | — |"

    inhalt = f"""# Performance-Analyse — {TODAY_DE}

## YouTube — Letzte Videos

| Datum | Titel | Views | Likes |
|---|---|---|---|
{yt_tabelle}

## Instagram — Letzte Reels

| Datum | Caption | Likes | Kommentare |
|---|---|---|---|
{ig_tabelle}

## Jarvis-Analyse & Empfehlungen

{analyse}

---
_Automatisch erstellt von Jarvis Intelligenz am {TODAY_DE}_
"""
    pfad.write_text(inhalt, encoding="utf-8")
    print(f"[intelligenz] Bericht gespeichert: {pfad.name}")
    return pfad


def aktualisiere_kontext(analyse: str):
    """Schreibt die Kurzfassung der Analyse in context/current-data.md."""
    if not CURRENT_DATA.exists():
        return

    content = CURRENT_DATA.read_text(encoding="utf-8")

    # Kurzfassung: erste 5 Zeilen der Analyse
    kurzfassung = "\n".join(analyse.split("\n")[:6])
    eintrag = f"\n## Letzte Analyse\n\n**Stand:** {TODAY_DE}\n\n{kurzfassung}\n\n_Vollständiger Bericht: `outputs/berichte/{TODAY}-performance-analyse.md`_\n"

    # Vorhandenen Abschnitt ersetzen oder am Ende anhängen
    if "## Letzte Analyse" in content:
        import re
        content = re.sub(r"\n## Letzte Analyse\n.*?(?=\n## |\Z)", eintrag, content, flags=re.DOTALL)
    else:
        content = content.rstrip() + "\n" + eintrag

    CURRENT_DATA.write_text(content, encoding="utf-8")
    print("[intelligenz] context/current-data.md aktualisiert")


# ── Haupt-Ablauf ───────────────────────────────────────────────────────────────

def main():
    print(f"[intelligenz] Starte Analyse ({TODAY_DE}) ...")

    yt = fetch_youtube_videos()
    print(f"[intelligenz] YouTube: {len(yt)} Videos abgerufen")

    ig = fetch_instagram_reels()
    print(f"[intelligenz] Instagram: {len(ig)} Reels abgerufen")

    if not yt and not ig:
        print("[intelligenz] Keine Daten — Analyse übersprungen.")
        return

    print("[intelligenz] Claude analysiert ...")
    analyse = analysiere(yt, ig)
    print("[intelligenz] Analyse fertig.")

    pfad = speichere_bericht(analyse, yt, ig)
    aktualisiere_kontext(analyse)

    print(f"\n[intelligenz] ✅ Fertig. Bericht: outputs/berichte/{pfad.name}")
    print("\n── Kurzfassung ──────────────────────────────────────")
    print(analyse[:400])
    print("─────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()
