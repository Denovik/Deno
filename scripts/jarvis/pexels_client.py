import os
import random
import requests
from datetime import datetime
from config import PEXELS_API_KEY, NICHES, TEMP_DIR


def get_stock_videos(niche, count=4, keywords=None):
    """Holt mehrere verschiedene Stock-Videos mit unterschiedlichen Keywords.

    Wenn keywords übergeben wird: diese direkt verwenden.
    Sonst: zufällige Keywords aus der Nischen-Konfiguration.
    """
    if keywords and len(keywords) > 0:
        # Keywords aus Skript-Analyse verwenden
        selected_keywords = keywords[:count]
        # Auffüllen falls zu wenig
        if len(selected_keywords) < count:
            fallback = NICHES[niche]["pexels_keywords"].copy()
            random.shuffle(fallback)
            selected_keywords = selected_keywords + fallback[:(count - len(selected_keywords))]
    else:
        # Bisheriges Verhalten: zufällig aus Nische
        niche_keywords = NICHES[niche]["pexels_keywords"].copy()
        random.shuffle(niche_keywords)
        selected_keywords = niche_keywords[:count]

    paths = []
    for kw in selected_keywords:
        try:
            path = _fetch_one_video(kw, niche)
            paths.append(path)
        except Exception as e:
            print(f"[pexels_client] Übersprungen ({kw}): {e}")
    if not paths:
        raise RuntimeError("Kein einziges Stock-Video konnte geladen werden.")
    return paths


def _fetch_one_video(query, niche):
    """Holt ein einzelnes Video für einen Suchbegriff."""
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "orientation": "portrait", "size": "medium", "per_page": 30}
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Pexels Fehler {response.status_code}")
    videos = response.json().get("videos", [])
    if not videos:
        raise RuntimeError(f"Keine Videos für '{query}'")
    video = random.choice(videos[:15])
    video_files = video.get("video_files", [])
    hd_files = [f for f in video_files if f.get("quality") in ["hd", "sd"] and f.get("height", 0) >= 720]
    if not hd_files:
        hd_files = video_files
    chosen_file = sorted(hd_files, key=lambda f: f.get("height", 0), reverse=True)[0]
    os.makedirs(TEMP_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    video_path = os.path.join(TEMP_DIR, f"stock-{niche}-{date_str}-{query[:10].replace(' ','-')}.mp4")
    print(f"[pexels_client] Lade Video herunter: {query} ({chosen_file.get('height')}p)")
    r = requests.get(chosen_file["link"], stream=True)
    with open(video_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[pexels_client] Stock-Video gespeichert: {os.path.basename(video_path)}")
    return video_path


def get_stock_video(niche, duration_seconds=60):
    """Holt ein passendes Stock-Video von Pexels. Gibt Pfad zur heruntergeladenen Datei zurück."""
    keywords = NICHES[niche]["pexels_keywords"]
    query = random.choice(keywords)

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": "portrait",
        "size": "medium",
        "per_page": 30,
    }

    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Pexels Fehler {response.status_code}: {response.text}")

    data = response.json()
    videos = data.get("videos", [])
    if not videos:
        raise RuntimeError(f"Keine Videos für '{query}' gefunden.")

    # Bevorzuge Videos die lang genug sind, sonst nimm das längste
    suitable = [v for v in videos if v.get("duration", 0) >= duration_seconds]
    video = random.choice(suitable) if suitable else max(videos, key=lambda v: v.get("duration", 0))

    # Beste HD-Qualität wählen (nicht 4K wegen Dateigröße)
    video_files = video.get("video_files", [])
    hd_files = [f for f in video_files if f.get("quality") in ["hd", "sd"] and f.get("height", 0) >= 720]
    if not hd_files:
        hd_files = video_files
    chosen_file = sorted(hd_files, key=lambda f: f.get("height", 0), reverse=True)[0]
    video_url = chosen_file["link"]

    # Herunterladen
    os.makedirs(TEMP_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    video_path = os.path.join(TEMP_DIR, f"stock-{niche}-{date_str}.mp4")

    print(f"[pexels_client] Lade Video herunter: {query} ({chosen_file.get('height')}p)")
    video_response = requests.get(video_url, stream=True)
    with open(video_path, "wb") as f:
        for chunk in video_response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"[pexels_client] Stock-Video gespeichert: {os.path.basename(video_path)}")
    return video_path
