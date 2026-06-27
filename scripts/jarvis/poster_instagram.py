import os
import time
import requests
from config import META_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID

# Neue Instagram-API (Instagram-Login-Flow) — Token beginnt mit "IGA..."
GRAPH_API = "https://graph.instagram.com/v21.0"

# Nischen-spezifische Hashtags für maximale Reichweite
HASHTAGS = {
    ("motivation", "de"): "#motivation #erfolg #mindset #disziplin #selbstbewusstsein #ziele #erfolgreich #inspiration #motivationdeutsch #durchhalten #reels #fyp #viral",
    ("motivation", "en"): "#motivation #success #mindset #discipline #selfimprovement #goals #hustle #inspiration #grindset #motivationalvideo #reels #fyp #viral",
    ("fakten", "de"): "#fakten #wissen #wusstestdu #faktenwissen #allgemeinwissen #lernen #bildung #interessant #faktencheck #wissenswert #reels #fyp #viral",
    ("fakten", "en"): "#facts #knowledge #didyouknow #funfacts #interesting #education #factsdaily #mindblowing #learnsomething #knowledgeispower #reels #fyp #viral",
}
HASHTAGS_FALLBACK_DE = "#motivation #wissen #erfolg #fakten #mindset #reels #fyp #viral"
HASHTAGS_FALLBACK_EN = "#motivation #knowledge #success #facts #mindset #reels #fyp #viral"


SERVER_IP = "167.233.95.3"
SERVER_PORT = 8080
SERVER_PUBLIC_DIR = "/opt/mindwave/public"
_IS_SERVER = os.path.exists(SERVER_PUBLIC_DIR)


def _upload_public(video_path: str) -> str:
    """Stellt das Video öffentlich bereit.
    Auf dem Hetzner-Server: direkt über den eingebauten File-Server (Port 8080).
    Lokal: Upload zu catbox.moe als Fallback."""
    import shutil, uuid
    filename = f"{uuid.uuid4().hex}.mp4"

    if _IS_SERVER:
        dest = os.path.join(SERVER_PUBLIC_DIR, filename)
        shutil.copy2(video_path, dest)
        url = f"http://{SERVER_IP}:{SERVER_PORT}/{filename}"
        print(f"[poster_instagram] Video bereitgestellt: {url}")
        return url

    # Fallback: catbox.moe (lokal/Mac)
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


def post_to_instagram(video_path: str, caption: str, language: str = "de", niche: str = None) -> str:
    """Postet ein Reel auf Instagram. caption = packender Titel (wie YouTube).
    Hängt nischen-spezifische Hashtags an. Gibt die Media-ID zurück."""
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("[poster_instagram] ÜBERSPRUNGEN — META_ACCESS_TOKEN oder INSTAGRAM_ACCOUNT_ID fehlt in .env")
        return None

    hashtags = HASHTAGS.get((niche, language))
    if not hashtags:
        hashtags = HASHTAGS_FALLBACK_DE if language == "de" else HASHTAGS_FALLBACK_EN
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
