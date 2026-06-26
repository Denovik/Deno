import os
import time
import requests
from config import TIKTOK_ACCESS_TOKEN, TIKTOK_OPEN_ID

TIKTOK_API = "https://open.tiktokapis.com/v2"

HASHTAGS_DE = "#motivation #deutsch #lernen #erfolg #mindset #wissen #fyp #viral #foryou #tiktokdeutschland"
HASHTAGS_EN = "#motivation #english #success #mindset #facts #knowledge #fyp #viral #foryou #shorts"


def post_to_tiktok(video_path: str, caption: str, language: str = "de") -> str:
    """Postet Video auf TikTok per Content Posting API. Gibt Video-ID zurück."""
    if not TIKTOK_ACCESS_TOKEN or not TIKTOK_OPEN_ID:
        print("[poster_tiktok] ÜBERSPRUNGEN — TIKTOK_ACCESS_TOKEN oder TIKTOK_OPEN_ID fehlt in .env")
        return None

    hashtags = HASHTAGS_DE if language == "de" else HASHTAGS_EN
    title = f"{caption[:100]}\n{hashtags}"

    file_size = os.path.getsize(video_path)

    # Schritt 1: Upload initialisieren
    print("[poster_tiktok] Initialisiere Upload...")
    init_url = f"{TIKTOK_API}/post/publish/video/init/"
    init_payload = {
        "post_info": {
            "title": title,
            "privacy_level": "SELF_ONLY",  # Erst privat testen, dann auf PUBLIC stellen
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1,
        },
    }
    headers = {
        "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    init_r = requests.post(init_url, json=init_payload, headers=headers)
    if init_r.status_code != 200:
        raise RuntimeError(f"TikTok Init-Fehler: {init_r.text}")

    init_data = init_r.json().get("data", {})
    publish_id = init_data.get("publish_id")
    upload_url = init_data.get("upload_url")

    # Schritt 2: Video-Datei hochladen
    print("[poster_tiktok] Lade Video hoch...")
    with open(video_path, "rb") as f:
        video_data = f.read()

    upload_headers = {
        "Content-Type": "video/mp4",
        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
        "Content-Length": str(file_size),
    }
    upload_r = requests.put(upload_url, data=video_data, headers=upload_headers)
    if upload_r.status_code not in (200, 201, 204):
        raise RuntimeError(f"TikTok Upload-Fehler: {upload_r.text}")

    # Schritt 3: Status prüfen
    print("[poster_tiktok] Warte auf Verarbeitung...")
    for _ in range(10):
        time.sleep(10)
        status_url = f"{TIKTOK_API}/post/publish/status/fetch/"
        status_r = requests.post(
            status_url,
            json={"publish_id": publish_id},
            headers=headers,
        )
        status_data = status_r.json().get("data", {})
        status = status_data.get("status")
        if status == "PUBLISH_COMPLETE":
            video_id = status_data.get("publicaly_available_post_id", [publish_id])[0]
            print(f"[poster_tiktok] Video veröffentlicht: {video_id}")
            return video_id
        elif status in ("FAILED", "PUBLISH_FAILED"):
            raise RuntimeError(f"TikTok Verarbeitungsfehler: {status_data}")

    print("[poster_tiktok] Timeout beim Warten auf TikTok-Status.")
    return publish_id
