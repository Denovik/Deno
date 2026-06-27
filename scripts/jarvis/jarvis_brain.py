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
import jarvis_actions

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
    "WICHTIG: Du kannst nicht nur reden, sondern auch HANDELN. Wenn Dennis dich bittet, "
    "Videos zu erstellen oder zu posten / die Pipeline zu starten, dann FÜHRE das mit deinem "
    "Werkzeug 'video_pipeline_starten' aus — sag nicht, er solle es selbst im Terminal machen. "
    "Du HAST Zugriff darauf. Mit 'pipeline_status' kannst du nachsehen, ob eine Produktion läuft.\n\n"
    "=== KONTEXT ÜBER DENNIS UND SEIN BUSINESS ===\n" + load_context()
)

# Werkzeuge, die Jarvis tatsächlich ausführen kann
TOOLS = [
    {
        "name": "video_pipeline_starten",
        "description": "Startet die Jarvis Content-Pipeline: erstellt automatisch Videos (Skript, Stimme, Untertitel, Musik) und postet sie auf YouTube und Instagram. Nutze das, wenn Dennis sagt, er will jetzt Videos erstellen/posten oder die Pipeline starten/ausführen.",
        "input_schema": {
            "type": "object",
            "properties": {
                "anzahl": {"type": "integer", "description": "Anzahl der Videos (Standard 1, maximal 4)"}
            },
            "required": [],
        },
    },
    {
        "name": "pipeline_status",
        "description": "Prüft, ob gerade eine Video-Produktion läuft und wie die letzte ausging.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "analyse_starten",
        "description": "Analysiert die Content-Performance auf YouTube und Instagram: welche Videos laufen gut, was nicht, und gibt konkrete Empfehlungen. Nutze das, wenn Dennis sagt: analysiere meine Videos / wie laufen meine Videos / was funktioniert / gib mir eine Auswertung.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


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
    """Schickt die Frage an Claude (mit Werkzeugen + Gesprächsverlauf) und gibt die Antwort zurück.
    Führt aus, was Jarvis anfordert (z.B. Pipeline starten), bevor er antwortet."""
    history.append({"role": "user", "content": user_text})

    for _ in range(5):   # Sicherheitslimit gegen Endlosschleifen
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history,
        )
        history.append({"role": "assistant", "content": message.content})

        if message.stop_reason != "tool_use":
            # Fertig — Text aus den Blöcken zusammensetzen
            text = " ".join(b.text for b in message.content if b.type == "text").strip()
            return text

        # Werkzeuge ausführen und Ergebnisse zurückgeben
        results = []
        for block in message.content:
            if block.type == "tool_use":
                func = jarvis_actions.ACTIONS.get(block.name)
                output = func(**block.input) if func else f"Unbekannte Aktion: {block.name}"
                print(f"[jarvis_brain] Aktion ausgeführt: {block.name}({block.input}) → {output[:60]}...")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        history.append({"role": "user", "content": results})

    return "Ich konnte die Aktion gerade nicht sauber abschließen — versuch es bitte nochmal."


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
