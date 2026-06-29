#!/usr/bin/env python3
"""
Performance Tracker — loggt jedes Video und berechnet Nischen-Gewichte.

Jedes gepostete Video wird in outputs/logs/video-log.json gespeichert.
Nach 48h können YouTube-Views abgerufen und Nischen-Gewichte aktualisiert werden.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
LOG_FILE = BASE_DIR / "outputs" / "logs" / "video-log.json"
WEIGHTS_FILE = BASE_DIR / "outputs" / "logs" / "niche-weights.json"


def log_video(label, niche, language, youtube_id=None, instagram_id=None, ab_variant=None):
    """Speichert ein Video-Log-Eintrag."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = _load_log()
    log.append({
        "label": label,
        "niche": niche,
        "language": language,
        "timestamp": datetime.now().isoformat(),
        "youtube_id": youtube_id,
        "instagram_id": instagram_id,
        "ab_variant": ab_variant,
        "views_48h": None,
    })
    _save_log(log)


def update_views(youtube_id, views):
    """Aktualisiert die Views für ein Video (nach 48h)."""
    log = _load_log()
    for entry in log:
        if entry.get("youtube_id") == youtube_id:
            entry["views_48h"] = views
    _save_log(log)


def get_niche_weights():
    """Gibt die aktuellen Nischen-Gewichte zurück. Fallback: gleiche Gewichtung."""
    if WEIGHTS_FILE.exists():
        try:
            return json.loads(WEIGHTS_FILE.read_text())
        except Exception:
            pass
    return {}


def update_niche_weights(yt_videos):
    """
    Berechnet neue Nischen-Gewichte aus YouTube-Views.
    yt_videos: Liste von {titel, datum, views, niche (optional)}
    Gleicht die Video-Titel mit dem Log ab um die Nische zu ermitteln.
    """
    log = _load_log()
    label_to_niche = {e["label"]: (e["niche"], e["language"]) for e in log}

    # Views pro Nische sammeln
    niche_views = {}
    niche_count = {}

    for entry in log:
        if entry.get("views_48h") is None:
            continue
        niche = entry["niche"]
        niche_views[niche] = niche_views.get(niche, 0) + entry["views_48h"]
        niche_count[niche] = niche_count.get(niche, 0) + 1

    if not niche_views:
        print("[performance] Noch keine 48h-Views — Gewichte bleiben gleich.")
        return

    # Durchschnittliche Views pro Nische
    avg_views = {n: niche_views[n] / niche_count[n] for n in niche_views}
    total = sum(avg_views.values())

    if total == 0:
        return

    # Normierte Gewichte (Summe = 1.0)
    raw_weights = {n: avg_views[n] / total for n in avg_views}

    # Nicht zu extrem: min 10% pro Nische die schon Daten hat
    weights = {}
    for niche in raw_weights:
        weights[niche] = max(0.10, raw_weights[niche])

    # Renormieren
    total_w = sum(weights.values())
    weights = {n: w / total_w for n, w in weights.items()}

    WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    WEIGHTS_FILE.write_text(json.dumps(weights, indent=2, ensure_ascii=False))
    print(f"[performance] Nischen-Gewichte aktualisiert: {weights}")
    return weights


def build_weighted_combos(niches, count):
    """
    Erstellt eine gewichtete Nischen/Sprache-Kombination basierend auf Performance.
    Fallback: 70% DE, 30% EN, alle Nischen gleich.
    """
    weights = get_niche_weights()
    niche_list = list(niches.keys())

    combos = []
    for niche in niche_list:
        weight = weights.get(niche, 1.0 / len(niche_list))
        # Anzahl Einträge proportional zum Gewicht (min 1)
        entries = max(1, round(weight * 10))
        combos += [(niche, "de")] * (entries * 7 // 10)
        combos += [(niche, "en")] * (entries * 3 // 10 + 1)

    import random
    random.shuffle(combos)
    return (combos * ((count // len(combos)) + 1))[:count]


def get_videos_ready_for_48h_check():
    """Gibt Videos zurück die 48h+ alt sind und noch keine Views haben."""
    log = _load_log()
    cutoff = datetime.now() - timedelta(hours=48)
    ready = []
    for entry in log:
        if entry.get("youtube_id") and entry.get("views_48h") is None:
            try:
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts < cutoff:
                    ready.append(entry)
            except Exception:
                pass
    return ready


def _load_log():
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except Exception:
            pass
    return []


def _save_log(log):
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))
