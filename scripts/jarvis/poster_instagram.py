import os
import time
import requests
from config import META_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID

GRAPH_API = "https://graph.facebook.com/v19.0"

HASHTAGS_DE = "#motivation #deutsch #lernen #erfolg #mindset #wissen #tiktokdeutschland #viral #fyp #shorts"
HASHTAGS_EN = "#motivation #english #success #mindset #facts #knowledge #viral #fyp #shorts #reels"


def post_to_instagram(video_path: str, caption: str, language: str = "de") -> str:
    """Postet Reel per Meta Graph API. Gibt Post-ID zurück."""
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("[poster_instagram] ÜBERSPRUNGEN — META_ACCESS_TOKEN oder INSTAGRAM_ACCOUNT_ID fehlt in .env")
        return None

    hashtags = HASHTAGS_DE if language == "de" else HASHTAGS_EN
    full_caption = f"{caption}\n\n{hashtags}"

    # Schritt 1: Container erstellen
    print("[poster_instagram] Erstelle Reel-Container...")
    container_url = f"{GRAPH_API}/{INSTAGRAM_ACCOUNT_ID}/media"
    container_params = {
        "media_type": "REELS",
        "video_url": video_path,  # Muss eine öffentliche URL sein
        "caption": full_caption,
        "access_token": META_ACCESS_TOKEN,
    }
    r = requests.post(container_url, data=container_params)
    if r.status_code != 200:
        raise RuntimeError(f"Instagram Container-Fehler: {r.text}")
    container_id = r.json()["id"]

    # Schritt 2: Warten bis Container verarbeitet
    print("[poster_instagram] Warte auf Verarbeitung...")
    for _ in range(10):
        time.sleep(15)
        status_url = f"{GRAPH_API}/{container_id}"
        status_r = requests.get(status_url, params={"fields": "status_code", "access_token": META_ACCESS_TOKEN})
        status = status_r.json().get("status_code")
        if status == "FINISHED":
            break
        elif status == "ERROR":
            raise RuntimeError("Instagram Video-Verarbeitung fehlgeschlagen.")

    # Schritt 3: Veröffentlichen
    publish_url = f"{GRAPH_API}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    publish_params = {"creation_id": container_id, "access_token": META_ACCESS_TOKEN}
    pub_r = requests.post(publish_url, data=publish_params)
    if pub_r.status_code != 200:
        raise RuntimeError(f"Instagram Publish-Fehler: {pub_r.text}")

    post_id = pub_r.json()["id"]
    print(f"[poster_instagram] Reel veröffentlicht: {post_id}")
    return post_id
