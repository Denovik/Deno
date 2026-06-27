#!/usr/bin/env python3
"""
Jarvis Voice-Interface — mit Jarvis sprechen.
Start: python3 scripts/jarvis/voice_chat.py

Ablauf je Runde:
  Enter drücken → sprechen → Enter drücken → Jarvis hört zu, denkt nach und antwortet mit Stimme.
  "tschüss" / "beenden" sagen oder Strg+C beendet.
"""

import os
import sys
import wave
import queue
import threading
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from config import (
    ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_DE, BASE_DIR
)

SAMPLE_RATE = 16000          # 16 kHz — ideal für Spracherkennung
WHISPER_MODEL = "small"      # guter Kompromiss Genauigkeit/Tempo
CLAUDE_MODEL = "claude-sonnet-4-6"

_whisper = None              # wird beim ersten Mal geladen (lazy)


def _load_context() -> str:
    """Liest die context/-Dateien für Jarvis' Hintergrundwissen über Dennis."""
    parts = []
    ctx_dir = os.path.join(BASE_DIR, "context")
    for name in ["personal-info.md", "business-info.md", "strategy.md", "current-data.md"]:
        path = os.path.join(ctx_dir, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                parts.append(f"### {name}\n{f.read()}")
    return "\n\n".join(parts)


SYSTEM_PROMPT = (
    "Du bist Jarvis, der persönliche KI-Assistent und beste Mitarbeiter von Dennis. "
    "Du sprichst per Stimme mit ihm — antworte deshalb natürlich, klar und KURZ "
    "(2-4 Sätze, wie im echten Gespräch), ohne Aufzählungen, Markdown oder Code. "
    "Du duzt Dennis nicht von dir aus über die Maßen — du bist sein professioneller, "
    "freundlicher Mitarbeiter. Du kennst sein Business (siehe Kontext) und denkst mit. "
    "Wenn du etwas nicht weißt, sag es ehrlich.\n\n"
    "=== KONTEXT ÜBER DENNIS UND SEIN BUSINESS ===\n" + _load_context()
)


def record_until_enter() -> str:
    """Nimmt Mikrofon auf, bis Enter gedrückt wird. Gibt Pfad zur WAV-Datei zurück."""
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    frames = []
    stop_event = threading.Event()

    def wait_for_enter():
        input()
        stop_event.set()

    threading.Thread(target=wait_for_enter, daemon=True).start()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback):
        while not stop_event.is_set():
            try:
                frames.append(q.get(timeout=0.1))
            except queue.Empty:
                pass

    if not frames:
        return None

    audio = np.concatenate(frames, axis=0)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(tmp.name, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return tmp.name


def transcribe(wav_path: str) -> str:
    """Wandelt Sprache in Text um — lokal mit faster-whisper (kostenlos, offline)."""
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        print("[jarvis] Lade Spracherkennung (einmalig)...")
        _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _ = _whisper.transcribe(wav_path, language="de")
    return " ".join(seg.text for seg in segments).strip()


def think(client, history: list, user_text: str) -> str:
    """Schickt die Frage an Claude (mit Gesprächsverlauf) und gibt die Antwort zurück."""
    history.append({"role": "user", "content": user_text})
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    answer = message.content[0].text.strip()
    history.append({"role": "assistant", "content": answer})
    return answer


def speak(text: str):
    """Wandelt Text in Jarvis-Stimme (ElevenLabs) um und spielt ihn ab."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID_DE}"
    headers = {"Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3, "use_speaker_boost": True},
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code != 200:
        print(f"[jarvis] Stimme-Fehler {r.status_code}: {r.text}")
        return
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(r.content)
    tmp.close()
    subprocess.run(["afplay", tmp.name])
    os.remove(tmp.name)


def main():
    if not ANTHROPIC_API_KEY or not ELEVENLABS_API_KEY:
        print("Fehlt: ANTHROPIC_API_KEY oder ELEVENLABS_API_KEY in .env")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    history = []

    print("=" * 55)
    print("  JARVIS Voice-Interface")
    print("  Enter drücken → sprechen → Enter drücken.")
    print("  'tschüss' sagen oder Strg+C beendet.")
    print("=" * 55)

    try:
        while True:
            input("\n[Enter drücken und sprechen...] ")
            print("[jarvis] Höre zu... (Enter zum Stoppen)")
            wav = record_until_enter()
            if not wav:
                print("[jarvis] Nichts gehört, nochmal.")
                continue

            text = transcribe(wav)
            os.remove(wav)
            if not text:
                print("[jarvis] Konnte nichts verstehen, nochmal.")
                continue
            print(f"\n  Du: {text}")

            if any(w in text.lower() for w in ["tschüss", "beenden", "auf wiedersehen", "ende"]):
                speak("Bis später, Dennis. Ich bin da, wenn du mich brauchst.")
                print("[jarvis] Tschüss!")
                break

            answer = think(client, history, text)
            print(f"  Jarvis: {answer}\n")
            speak(answer)
    except KeyboardInterrupt:
        print("\n[jarvis] Beendet.")


if __name__ == "__main__":
    main()
