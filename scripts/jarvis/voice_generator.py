import os
import json
import requests
from datetime import datetime
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_DE, ELEVENLABS_VOICE_ID_EN, TEMP_DIR


def generate_voice(script_text: str, language: str) -> tuple:
    """
    Wandelt Text per ElevenLabs in MP3 um und gibt Wort-Timestamps zurück.
    Gibt (audio_path, word_timings) zurück.
    word_timings = [{"word": "Hallo", "start": 0.0, "end": 0.4}, ...]
    """
    voice_id = ELEVENLABS_VOICE_ID_DE if language == "de" else ELEVENLABS_VOICE_ID_EN

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    headers = {
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

    data = response.json()

    # Audio speichern
    import base64
    audio_bytes = base64.b64decode(data["audio_base64"])
    os.makedirs(TEMP_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    audio_path = os.path.join(TEMP_DIR, f"voice-{language}-{date_str}.mp3")
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # Wort-Timestamps aus Zeichen-Timestamps berechnen
    alignment = data.get("alignment", {})
    chars = alignment.get("characters", [])
    char_starts = alignment.get("character_start_times_seconds", [])
    char_ends = alignment.get("character_end_times_seconds", [])

    word_timings = []
    if chars and char_starts:
        current_word = ""
        word_start = 0.0
        word_end = 0.0
        for i, (ch, t_start, t_end) in enumerate(zip(chars, char_starts, char_ends)):
            if ch in " \n\r\t" or i == len(chars) - 1:
                if ch != " ":
                    current_word += ch
                    word_end = t_end
                if current_word.strip():
                    word_timings.append({
                        "word": current_word.strip(),
                        "start": word_start,
                        "end": word_end,
                    })
                current_word = ""
                if i + 1 < len(chars):
                    word_start = char_starts[i + 1]
            else:
                if not current_word:
                    word_start = t_start
                current_word += ch
                word_end = t_end

    print(f"[voice_generator] Audio gespeichert: {os.path.basename(audio_path)} ({len(word_timings)} Wörter getimestamp)")
    return audio_path, word_timings
