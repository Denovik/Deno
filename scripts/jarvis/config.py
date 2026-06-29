import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID_DE = os.getenv("ELEVENLABS_VOICE_ID_DE", "pNInz6obpgDQGcFmaJgB")  # Default: Adam (DE-fähig)
ELEVENLABS_VOICE_ID_EN = os.getenv("ELEVENLABS_VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
YOUTUBE_CLIENT_SECRET_PATH = os.getenv("YOUTUBE_CLIENT_SECRET_PATH", "credentials/youtube_client_secret.json")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
TIKTOK_OPEN_ID = os.getenv("TIKTOK_OPEN_ID")
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")

# Sprachen
LANGUAGES = ["de", "en"]

# Video-Einstellungen
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_DURATION_TARGET = 60  # Sekunden

# Posting-Zeiten (24h Format)
POSTING_SCHEDULE = {
    "tiktok": ["09:00", "18:00"],
    "instagram": ["12:00"],
    "youtube": ["15:00"],
}

_HOOK_REGEL_DE = (
    "WICHTIGSTE REGEL: Die ersten 3 Sekunden entscheiden alles. "
    "Starte mit einer provokativen Frage ODER einem Schock-Statement das sofort neugierig macht. "
    "Beispiele: 'Was wäre, wenn alles was du über X glaubst, falsch ist?' oder "
    "'Die meisten Menschen machen diesen einen Fehler ihr ganzes Leben lang.' "
    "Vermeide generische Einstiege wie 'Wusstest du dass', 'Hey', 'Heute zeige ich dir'. "
    "Schreib den gesprochenen Text OHNE Emojis. Kurze, kraftvolle Sätze."
)

_HOOK_REGEL_EN = (
    "MOST IMPORTANT RULE: The first 3 seconds decide everything. "
    "Start with a provocative question OR a shock statement that instantly creates curiosity. "
    "Examples: 'What if everything you believe about X is completely wrong?' or "
    "'Most people make this one mistake their entire lives.' "
    "Avoid generic openings like 'Did you know', 'Hey', 'Today I will show you'. "
    "Write the spoken text WITHOUT emojis. Short, powerful sentences."
)

# Nischen-Konfiguration
NICHES = {
    "motivation": {
        "name_de": "Motivation",
        "name_en": "Motivation",
        "prompt_de": (
            _HOOK_REGEL_DE + " "
            "Du bist ein Experte für viralen deutschsprachigen Motivations-Content auf TikTok. "
            "Schreib ein Skript für ein 60-Sekunden Faceless-Video. "
            "Regeln: Starte DIREKT mit einem starken Hook-Satz (keine Begrüßung, kein 'Hey'). "
            "Nutze kurze, kraftvolle Sätze. Jeder Satz ist maximal 10 Wörter lang. "
            "Baue Spannung auf. Ende mit: 'Folg mir für mehr.' "
            "Schreib NUR den gesprochenen Text, keine Regieanweisungen, keine Klammern."
        ),
        "prompt_en": (
            _HOOK_REGEL_EN + " "
            "You are an expert in viral English motivational content on TikTok. "
            "Write a script for a 60-second faceless video. "
            "Rules: Start DIRECTLY with a strong hook sentence (no greeting, no 'Hey'). "
            "Use short, powerful sentences. Maximum 10 words per sentence. "
            "Build tension. End with: 'Follow me for more.' "
            "Write ONLY the spoken text, no stage directions, no brackets."
        ),
        "pexels_keywords": [
            "sunset mountain", "running athlete", "city success", "motivation sunrise", "winner podium",
            "boxing training", "road highway", "skyscraper city", "ocean waves", "forest running",
            "gym workout", "night city lights", "climbing mountain", "sprinting track", "eagle flying",
            "storm lightning", "waterfall nature", "dark street rain", "rooftop city", "fire flames",
            "sunrise beach", "abstract energy", "stock market", "entrepreneur office", "luxury car",
        ],
    },
    "fakten": {
        "name_de": "Fakten & Wissen",
        "name_en": "Facts & Knowledge",
        "prompt_de": (
            _HOOK_REGEL_DE + " "
            "Du bist ein Experte für viralen deutschsprachigen Fakten-Content auf TikTok. "
            "Schreib ein Skript für ein 60-Sekunden Faceless-Video mit 4-5 überraschenden Fakten. "
            "Regeln: Starte mit einem verblüffenden Fakt oder einer Schock-Aussage. "
            "Jeder Fakt soll überraschen oder schockieren. Kurze Sätze. "
            "Ende mit: 'Folg mir für mehr erstaunliche Fakten.' "
            "Schreib NUR den gesprochenen Text, keine Regieanweisungen."
        ),
        "prompt_en": (
            _HOOK_REGEL_EN + " "
            "You are an expert in viral English facts content on TikTok. "
            "Write a script for a 60-second faceless video with 4-5 surprising facts. "
            "Rules: Start with a mind-blowing fact or a shocking statement. "
            "Each fact should surprise or shock. Short sentences. "
            "End with: 'Follow me for more amazing facts.' "
            "Write ONLY the spoken text, no stage directions."
        ),
        "pexels_keywords": [
            "space galaxy", "ocean deep", "nature wildlife", "science laboratory", "earth aerial",
            "underwater coral", "brain neuron", "volcano eruption", "northern lights", "desert dunes",
            "microscope cells", "robot technology", "ancient ruins", "deep sea creatures", "tornado storm",
            "solar system", "dna molecule", "quantum physics", "rainforest jungle", "arctic ice",
            "satellite earth", "cave exploration", "black hole space", "crystal minerals", "city timelapse",
        ],
    },
    "psychologie": {
        "name_de": "Psychologie",
        "name_en": "Psychology",
        "prompt_de": (
            _HOOK_REGEL_DE + " "
            "Du bist ein Experte für viralen deutschsprachigen Psychologie-Content auf TikTok. "
            "Schreib ein Skript für ein 60-Sekunden Faceless-Video über einen faszinierenden "
            "psychologischen Effekt, Denkfehler oder Verhaltensphänomen. "
            "Regeln: Starte mit einem Beispiel das jeder kennt aber niemand versteht. "
            "Erkläre den Effekt einfach. Kurze Sätze. "
            "Ende mit: 'Folg mir für mehr Psychologie-Fakten.' "
            "Schreib NUR den gesprochenen Text, keine Regieanweisungen."
        ),
        "prompt_en": (
            _HOOK_REGEL_EN + " "
            "You are an expert in viral English psychology content on TikTok. "
            "Write a script for a 60-second faceless video about a fascinating psychological effect, "
            "cognitive bias, or behavioral phenomenon. "
            "Rules: Start with an example everyone knows but nobody understands. "
            "Explain the effect simply. Short sentences. "
            "End with: 'Follow me for more psychology facts.' "
            "Write ONLY the spoken text, no stage directions."
        ),
        "pexels_keywords": [
            "brain thinking", "human behavior", "crowd people", "mirror reflection", "mind meditation",
            "social interaction", "decision making", "stress anxiety", "happy emotion", "eye contact",
            "body language", "subconscious dream", "memory neural", "fear dark", "confidence walk",
            "manipulation power", "dopamine reward", "sleep psychology", "group dynamics", "self control",
            "anxiety breathing", "therapy session", "emotional intelligence", "habit formation", "attention focus",
        ],
    },
    "finanzen": {
        "name_de": "Finanzen & Geld",
        "name_en": "Finance & Money",
        "prompt_de": (
            _HOOK_REGEL_DE + " "
            "Du bist ein Experte für viralen deutschsprachigen Finanz-Content auf TikTok. "
            "Schreib ein Skript für ein 60-Sekunden Faceless-Video über einen Geld-Trick, "
            "Finanz-Fehler den die meisten machen, oder einen überraschenden Fakt über Reichtum. "
            "Regeln: Starte mit einem Fakt der schockiert oder neidisch macht. "
            "Erkläre praktisch und konkret. Kurze Sätze. "
            "Ende mit: 'Folg mir für mehr Geld-Wissen.' "
            "Schreib NUR den gesprochenen Text, keine Regieanweisungen."
        ),
        "prompt_en": (
            _HOOK_REGEL_EN + " "
            "You are an expert in viral English finance content on TikTok. "
            "Write a script for a 60-second faceless video about a money trick, "
            "financial mistake most people make, or a surprising fact about wealth. "
            "Rules: Start with a fact that shocks or creates envy. "
            "Be practical and concrete. Short sentences. "
            "End with: 'Follow me for more money knowledge.' "
            "Write ONLY the spoken text, no stage directions."
        ),
        "pexels_keywords": [
            "money cash", "stock market", "luxury lifestyle", "cryptocurrency bitcoin", "rich mansion",
            "bank vault", "credit card", "real estate", "gold bars", "businessman suit",
            "investment chart", "dollar bills", "luxury car", "trading screen", "financial freedom",
            "wallet empty", "debt stress", "compound interest", "passive income", "startup office",
            "shopping mall", "saving money", "poverty contrast", "wealth success", "financial planning",
        ],
    },
}

# Ausgabe-Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
VIDEOS_DIR = os.path.join(OUTPUTS_DIR, "videos")
TEMP_DIR = os.path.join(VIDEOS_DIR, "temp")
TIKTOK_DIR = os.path.join(VIDEOS_DIR, "tiktok")
SCRIPTS_DIR = os.path.join(OUTPUTS_DIR, "scripts")
LOG_FILE = os.path.join(SCRIPTS_DIR, "log.txt")
