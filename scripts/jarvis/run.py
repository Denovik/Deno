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
from script_generator import generate_script, generate_title, extract_keywords
from voice_generator import generate_voice
from pexels_client import get_stock_video, get_stock_videos
from video_builder import build_video
from poster_youtube import upload_to_youtube
from poster_instagram import post_to_instagram
from poster_tiktok import post_to_tiktok
from performance_tracker import log_video, build_weighted_combos


def make_one_video(niche, language, dry_run=False, ab_variant=None):
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

    # 3. B-Roll Keywords aus Skript-Inhalt extrahieren
    broll_keywords = extract_keywords(script, niche, language)

    # 4. Mehrere Hintergrund-Videos holen (wechseln alle ~10 Sek) — mit Skript-Keywords
    stock_path = get_stock_videos(niche, count=6, keywords=broll_keywords)

    # 5. Video bauen
    output_path = os.path.join(OUTPUTS_DIR, "videos", f"{label}.mp4")
    video_path = build_video(audio_path, stock_path, script, output_path, word_timings)

    # 6. Titel und Beschreibung
    title = generate_title(script, niche, language)
    print(f"[jarvis] Titel: {title}")
    description = f"{script[:500]}\n\n#shorts #motivation #fakten #wissen"
    tags = ["motivation", "fakten", "wissen", "deutsch", "english", "viral", "shorts"]

    results = {"label": label, "video_path": video_path}

    # 7. Auf Plattformen posten
    youtube_id = None
    instagram_id = None

    try:
        youtube_id = upload_to_youtube(video_path, title, description, tags)
        results["youtube"] = youtube_id
    except Exception as e:
        print(f"[jarvis] YouTube fehlgeschlagen: {e}")
        results["youtube"] = f"FEHLER: {e}"

    try:
        instagram_id = post_to_instagram(video_path, title, language, niche)
        results["instagram"] = instagram_id
    except Exception as e:
        print(f"[jarvis] Instagram fehlgeschlagen: {e}")
        results["instagram"] = f"FEHLER: {e}"

    try:
        tt_id = post_to_tiktok(video_path, script[:150], language)
        results["tiktok"] = tt_id
    except Exception as e:
        print(f"[jarvis] TikTok fehlgeschlagen: {e}")
        results["tiktok"] = f"FEHLER: {e}"

    # 8. Temp-Dateien aufräumen
    for path in [audio_path]:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    # Stock-Videos sind eine Liste
    if isinstance(stock_path, list):
        for p in stock_path:
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
    else:
        try:
            if stock_path and os.path.exists(stock_path):
                os.remove(stock_path)
        except Exception:
            pass

    # 8. Performance loggen
    log_video(label, niche, language, youtube_id=youtube_id, instagram_id=instagram_id, ab_variant=ab_variant)

    print(f"[jarvis] Video fertig: {label}")
    return results


def make_ab_test(niche, language, dry_run=False):
    """Erstellt zwei Varianten (A + B) für denselben Nische/Sprache-Slot."""
    print(f"\n[jarvis] A/B-Test: {niche} / {language}")
    result_a = make_one_video(niche, language, dry_run=dry_run, ab_variant="A")
    result_b = make_one_video(niche, language, dry_run=dry_run, ab_variant="B")
    return [result_a, result_b]


def run_daily(count=1, dry_run=False):
    """Produziert `count` Videos mit gewichteten Nischen und Sprachen."""
    # Gewichtete Nischen-Auswahl basierend auf Performance (Fallback: 70/30 DE/EN)
    selected = build_weighted_combos(NICHES, count)

    all_results = []
    ab_done_this_run = False

    for niche, lang in selected:
        # 25% Chance auf A/B-Test (max einmal pro Lauf)
        if not ab_done_this_run and not dry_run and random.random() < 0.25:
            results = make_ab_test(niche, lang, dry_run=dry_run)
            all_results.extend(results)
            ab_done_this_run = True
        else:
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
