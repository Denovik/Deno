#!/usr/bin/env python3
"""
Jarvis Web-Interface — visueller Arc-Reactor, händefrei.
Start: python3 scripts/jarvis/web_app.py
Dann im Browser: http://localhost:5005

Nutzt die geteilte Kern-Logik aus jarvis_brain.py.
"""

import os
import base64
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from config import ANTHROPIC_API_KEY, ELEVENLABS_API_KEY
import jarvis_brain as brain

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
PORT = 5005

app = Flask(__name__, static_folder=WEB_DIR)

# Gesprächsverlauf + Claude-Client (eine Sitzung, ein Nutzer)
_history = []
_client = None


def _client_lazy():
    global _client
    if _client is None:
        _client = brain.make_client()
    return _client


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/api/talk", methods=["POST"])
def talk():
    """Empfängt Audio, transkribiert, fragt Claude, gibt Antwort + Stimme zurück."""
    if "audio" not in request.files:
        return jsonify({"error": "kein Audio"}), 400

    blob = request.files["audio"]
    tmp = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
    blob.save(tmp.name)
    tmp.close()

    try:
        text = brain.transcribe(tmp.name)
    finally:
        os.remove(tmp.name)

    if not text:
        return jsonify({"text": "", "answer": "", "audio": None, "empty": True})

    answer = brain.think(_client_lazy(), _history, text)
    audio_bytes = brain.synthesize(answer)
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    return jsonify({"text": text, "answer": answer, "audio": audio_b64})


@app.route("/api/reset", methods=["POST"])
def reset():
    """Setzt den Gesprächsverlauf zurück."""
    _history.clear()
    return jsonify({"ok": True})


def main():
    if not ANTHROPIC_API_KEY or not ELEVENLABS_API_KEY:
        print("Fehlt: ANTHROPIC_API_KEY oder ELEVENLABS_API_KEY in .env")
        return
    print("[jarvis-web] Lade Spracherkennung vor...")
    brain.get_whisper()   # einmal vorladen, damit die erste Antwort schnell ist
    print(f"\n  JARVIS ist bereit → http://localhost:{PORT}\n")
    app.run(host="127.0.0.1", port=PORT, debug=False)


if __name__ == "__main__":
    main()
