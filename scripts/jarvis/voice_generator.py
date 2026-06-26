import os
import requests
from datetime import datetime
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_DE, ELEVENLABS_VOICE_ID_EN, TEMP_DIR


def generate_voice(script_text: str, language: str) -> str:
    """Wandelt Text per ElevenLabs API in MP3 um. Gibt Pfad zur MP3-Datei zurück."""
    voice_id = ELEVENLABS_VOICE_ID_DE if language == "de" else ELEVENLABS_VOICE_ID_EN

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": script_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs Fehler {response.status_code}: {response.text}")

    os.makedirs(TEMP_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    audio_path = os.path.join(TEMP_DIR, f"voice-{language}-{date_str}.mp3")

    with open(audio_path, "wb") as f:
        f.write(response.content)

    print(f"[voice_generator] Audio gespeichert: {os.path.basename(audio_path)}")
    return audio_path
