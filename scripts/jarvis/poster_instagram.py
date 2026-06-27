import os
import time
import requests
from config import META_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID

# Neue Instagram-API (Instagram-Login-Flow) — Token beginnt mit "IGA..."
GRAPH_API = "https://graph.instagram.com/v21.0"

HASHTAGS_DE = "#motivation #deutsch #lernen #erfolg #mindset #wissen #viral #fyp #reels #shorts"
HASHTAGS_EN = "#motivation #english #success #mindset #facts #knowledge #viral #fyp #reels #shorts"


def _upload_public(video_path: str) -> str:
    """Lädt das Video kurz zu catbox.moe hoch und gibt die öffentliche URL zurück.
    Instagram braucht eine öffentlich erreichbare Video-URL (kein Datei-Upload)."""
    print("[poster_instagram] Lade Video für öffentliche URL hoch...")
    with open(video_path, "rb") as f:
        resp = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            timeout=180,
        )
    url = resp.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Upload fehlgeschlagen: {url}")
    print(f"[poster_instagram] Öffentliche URL: {url}")
    return url


def post_to_instagram(video_path: str, caption: str, language: str = "de") -> str:
    """Postet ein Reel auf Instagram. Gibt die Media-ID zurück."""
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("[poster_instagram] ÜBERSPRUNGEN — META_ACCESS_TOKEN oder INSTAGRAM_ACCOUNT_ID fehlt in .env")
        return None

    hashtags = HASHTAGS_DE if language == "de" else HASHTAGS_EN
    full_caption = f"{caption}\n\n{hashtags}"

    # Schritt 0: Video öffentlich erreichbar machen
    video_url = _upload_public(video_path)

    # Schritt 1: Reel-Container erstellen
    print("[poster_instagram] Erstelle Reel-Container...")
    container_url = f"{GRAPH_API}/{INSTAGRAM_ACCOUNT_ID}/media"
    r = requests.post(container_url, data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": full_caption[:2200],
        "access_token": META_ACCESS_TOKEN,
    })
    if r.status_code != 200:
        raise RuntimeError(f"Instagram Container-Fehler: {r.text}")
    container_id = r.json()["id"]

    # Schritt 2: Warten bis Instagram das Video verarbeitet hat
    print("[poster_instagram] Warte auf Verarbeitung...")
    for _ in range(20):
        time.sleep(15)
        status_r = requests.get(
            f"{GRAPH_API}/{container_id}",
            params={"fields": "status_code", "access_token": META_ACCESS_TOKEN},
        )
        status = status_r.json().get("status_code")
        if status == "FINISHED":
            break
        elif status == "ERROR":
            raise RuntimeError(f"Instagram Verarbeitung fehlgeschlagen: {status_r.text}")

    # Schritt 3: Veröffentlichen
    print("[poster_instagram] Veröffentliche Reel...")
    pub_r = requests.post(
        f"{GRAPH_API}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
        data={"creation_id": container_id, "access_token": META_ACCESS_TOKEN},
    )
    if pub_r.status_code != 200:
        raise RuntimeError(f"Instagram Publish-Fehler: {pub_r.text}")

    post_id = pub_r.json()["id"]
    print(f"[poster_instagram] Reel veröffentlicht: {post_id}")
    return post_id
