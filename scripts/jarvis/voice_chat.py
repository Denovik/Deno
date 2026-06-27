#!/usr/bin/env python3
"""
Jarvis Voice-Interface (Terminal) — mit Jarvis sprechen.
Start: python3 scripts/jarvis/voice_chat.py

Ablauf je Runde:
  Enter drücken → sprechen → Enter drücken → Jarvis hört zu, denkt nach und antwortet mit Stimme.
  "tschüss" sagen oder Strg+C beendet.

Hinweis: Die Kern-Logik liegt in jarvis_brain.py (geteilt mit dem Web-Interface).
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
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from config import ANTHROPIC_API_KEY, ELEVENLABS_API_KEY
import jarvis_brain as brain

SAMPLE_RATE = 16000


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


def speak(text: str):
    """Erzeugt die Jarvis-Stimme und spielt sie ab."""
    audio = brain.synthesize(text)
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(audio)
    tmp.close()
    subprocess.run(["afplay", tmp.name])
    os.remove(tmp.name)


def main():
    if not ANTHROPIC_API_KEY or not ELEVENLABS_API_KEY:
        print("Fehlt: ANTHROPIC_API_KEY oder ELEVENLABS_API_KEY in .env")
        sys.exit(1)

    client = brain.make_client()
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

            text = brain.transcribe(wav)
            os.remove(wav)
            if not text:
                print("[jarvis] Konnte nichts verstehen, nochmal.")
                continue
            print(f"\n  Du: {text}")

            if any(w in text.lower() for w in ["tschüss", "beenden", "auf wiedersehen", "ende"]):
                speak("Bis später, Dennis. Ich bin da, wenn du mich brauchst.")
                print("[jarvis] Tschüss!")
                break

            answer = brain.think(client, history, text)
            print(f"  Jarvis: {answer}\n")
            speak(answer)
    except KeyboardInterrupt:
        print("\n[jarvis] Beendet.")


if __name__ == "__main__":
    main()
