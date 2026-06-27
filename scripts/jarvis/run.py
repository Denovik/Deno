#!/usr/bin/env python3
"""
Jarvis Content Bot — Haupt-Orchestrator
Startet mit: python3 run.py
Testlauf:    python3 run.py --dry-run
Einmalig:    python3 run.py --once --count 2
"""

import os
import sys
import argparse
import random
import shutil
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from config import NICHES, LANGUAGES, POSTING_SCHEDULE, OUTPUTS_DIR, TEMP_DIR, BASE_DIR
from script_generator import generate_script, generate_title
from voice_generator import generate_voice
from pexels_client import get_stock_video
from video_builder import build_video
from poster_youtube import upload_to_youtube
from poster_instagram import post_to_instagram
from poster_tiktok import post_to_tiktok


def make_one_video(niche: str, language: str, dry_run: bool = False) -> dict:
    """Produziert und postet ein Video. Gibt Ergebnis-Dict zurück."""
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"{ts}-{niche}-{language}"
    print(f"\n{'='*50}")
    print(f"[jarvis] Starte Video: {label}")
    print(f"{'='*50}")

    # 1. Skript generieren
    script = generate_script(niche, language)
    print(f"[jarvis] Skript ({len(script)} Zeichen) fertig.")

    if dry_run:
        print("[jarvis] DRY-RUN: Skript generiert, kein Video wird erstellt.")
        return {"label": label, "script": script[:200], "dry_run": True}

    # 2. Stimme generieren (gibt audio_path + Wort-Timestamps zurück)
    audio_path, word_timings = generate_voice(script, language)

    # 3. Hintergrund-Video holen (eigene Videos bevorzugt, sonst Pexels)
    import glob
    bg_files = glob.glob(os.path.join(BASE_DIR, "backgrounds", "*.mp4")) + \
               glob.glob(os.path.join(BASE_DIR, "backgrounds", "*.mov"))
    if bg_files:
        stock_path = random.choice(bg_files)
        print(f"[jarvis] Hintergrund: {os.path.basename(stock_path)}")
    else:
        stock_path = get_stock_video(niche)

    # 4. Video bauen
    output_path = os.path.join(OUTPUTS_DIR, "videos", f"{label}.mp4")
    video_path = build_video(audio_path, stock_path, script, output_path, word_timings)

    # 5. Titel und Beschreibung
    title = generate_title(script, niche, language)
    print(f"[jarvis] Titel: {title}")
    description = f"{script[:500]}\n\n#shorts #motivation #fakten #wissen"
    tags = ["motivation", "fakten", "wissen", "deutsch", "english", "viral", "shorts"]

    results = {"label": label, "video_path": video_path}

    # 6. Auf Plattformen posten
    try:
        vid_id = upload_to_youtube(video_path, title, description, tags)
        results["youtube"] = vid_id
    except Exception as e:
        print(f"[jarvis] YouTube fehlgeschlagen: {e}")
        results["youtube"] = f"FEHLER: {e}"

    try:
        ig_id = post_to_instagram(video_path, title, language, niche)
        results["instagram"] = ig_id
    except Exception as e:
        print(f"[jarvis] Instagram fehlgeschlagen: {e}")
        results["instagram"] = f"FEHLER: {e}"

    try:
        tt_id = post_to_tiktok(video_path, script[:150], language)
        results["tiktok"] = tt_id
    except Exception as e:
        print(f"[jarvis] TikTok fehlgeschlagen: {e}")
        results["tiktok"] = f"FEHLER: {e}"

    # 7. Temp-Dateien aufräumen
    for path in [audio_path, stock_path]:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    print(f"[jarvis] Video fertig: {label}")
    return results


def run_daily(count: int = 4, dry_run: bool = False):
    """Produziert `count` Videos mit gemischten Nischen und Sprachen."""
    combos = [(n, l) for n in NICHES.keys() for l in LANGUAGES]
    random.shuffle(combos)
    selected = (combos * ((count // len(combos)) + 1))[:count]

    all_results = []
    for niche, lang in selected:
        result = make_one_video(niche, lang, dry_run=dry_run)
        all_results.append(result)

    # Tages-Report ausgeben
    print(f"\n{'='*50}")
    print(f"[jarvis] TAGES-REPORT — {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}")
    for r in all_results:
        print(f"  {r['label']}")
        if not r.get("dry_run"):
            for platform in ("tiktok", "instagram", "youtube"):
                val = r.get(platform, "—")
                print(f"    {platform}: {val}")
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Jarvis Content Bot")
    parser.add_argument("--dry-run", action="store_true", help="Nur Skript generieren, kein Video/Post")
    parser.add_argument("--once", action="store_true", help="Einmalig laufen statt Dauerschleife")
    parser.add_argument("--count", type=int, default=4, help="Anzahl Videos pro Durchlauf (Standard: 4)")
    args = parser.parse_args()

    if args.dry_run:
        print("[jarvis] DRY-RUN Modus — kein Video, kein Post, nur Skript-Test.")

    run_daily(count=args.count, dry_run=args.dry_run)

    if not args.once:
        import schedule
        import time

        schedule.every().day.at("08:00").do(run_daily, count=args.count, dry_run=args.dry_run)
        print("[jarvis] Geplant: täglich 08:00 Uhr. Strg+C zum Beenden.")
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()
