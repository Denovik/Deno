"""
Jarvis-Kern — geteilte Logik für Terminal- und Web-Interface.
Spracherkennung (faster-whisper) + Denken (Claude) + Stimme (ElevenLabs).
"""

import os
import requests
import anthropic
from config import (
    ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_DE, BASE_DIR
)

WHISPER_MODEL = "small"          # guter Kompromiss Genauigkeit/Tempo
CLAUDE_MODEL = "claude-sonnet-4-6"

_whisper = None                  # lazy geladen


def load_context() -> str:
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
    "Du bist sein professioneller, freundlicher Mitarbeiter. Du kennst sein Business "
    "(siehe Kontext) und denkst mit. Wenn du etwas nicht weißt, sag es ehrlich.\n\n"
    "=== KONTEXT ÜBER DENNIS UND SEIN BUSINESS ===\n" + load_context()
)


def get_whisper():
    """Lädt das Spracherkennungs-Modell (einmalig)."""
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        print("[jarvis_brain] Lade Spracherkennung (einmalig)...")
        _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _whisper


def transcribe(audio_path: str) -> str:
    """Wandelt eine Audio-Datei (WAV/WEBM/MP3) in Text um — lokal, kostenlos."""
    model = get_whisper()
    segments, _ = model.transcribe(audio_path, language="de")
    return " ".join(seg.text for seg in segments).strip()


def make_client():
    """Erzeugt den Anthropic-Client."""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


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


def synthesize(text: str) -> bytes:
    """Wandelt Text in Jarvis-Stimme (ElevenLabs) um. Gibt MP3-Bytes zurück."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID_DE}"
    headers = {"Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3, "use_speaker_boost": True},
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs Fehler {r.status_code}: {r.text}")
    return r.content
