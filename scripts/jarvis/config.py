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
    "Schreib den gesprochenen Text OHNE Emojis. Kurze, kraftvolle Sätze. "
    "RETENTION-REGELN: "
    "(1) OFFENE SCHLEIFE — PFLICHT: Der allererste Satz stellt eine Frage oder verspricht eine Auflösung, die der Zuschauer erst am Ende bekommt. "
    "Beispiele: 'Die Antwort darauf hat mein Leben verändert. Sie kommt am Ende.' oder "
    "'Einer dieser Punkte wird dich schockieren. Welcher, erfährst du am Schluss.' "
    "Der Zuschauer MUSS bis zum Ende schauen, um die Auflösung zu bekommen. "
    "(2) Muster-Unterbrechung in der Mitte: Ein Satz der überrascht. Beispiel: 'Aber hier kommt der Teil, den die wenigsten kennen.' "
    "(3) AUFLÖSUNG AM ENDE — PFLICHT: Der vorletzte oder letzte inhaltliche Satz loest die offene Schleife direkt auf. "
    "Beispiel: Wenn der Hook war 'Einer dieser Fakten hat mein Leben veraendert', dann endet das Skript mit 'Und dieser Fakt war: [konkrete Antwort].' "
    "Die Aufloesung muss sich wie eine echte Erkenntnis anfuehlen, nicht wie ein leeres Versprechen. "
    "(4) Spannungsbogen: Aufbau → Eskalation → Auflösung. Jeder Satz baut auf dem vorherigen auf. "
)

_HOOK_REGEL_EN = (
    "MOST IMPORTANT RULE: The first 3 seconds decide everything. "
    "Start with a provocative question OR a shock statement that instantly creates curiosity. "
    "Examples: 'What if everything you believe about X is completely wrong?' or "
    "'Most people make this one mistake their entire lives.' "
    "Avoid generic openings like 'Did you know', 'Hey', 'Today I will show you'. "
    "Write the spoken text WITHOUT emojis. Short, powerful sentences. "
    "RETENTION RULES: "
    "(1) OPEN LOOP — MANDATORY: The very first sentence asks a question or promises a reveal that only comes at the end. "
    "Examples: 'The answer to this changed my life. I'll tell you at the end.' or "
    "'One of these points will shock you. You'll find out which one at the end.' "
    "The viewer MUST watch until the end to get the resolution. "
    "(2) Pattern interrupt in the middle: A sentence that surprises. Example: 'But here's the part most people don't know.' "
    "(3) PAYOFF AT THE END — MANDATORY: The second-to-last or last content sentence directly resolves the open loop. "
    "Example: If the hook was 'One of these facts changed my life', the script ends with 'And that fact was: [concrete answer].' "
    "The payoff must feel like a real insight, not an empty promise. "
    "(4) Tension arc: Setup → Escalation → Resolution. Each sentence builds on the previous one. "
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
            "Baue Spannung auf. Ende mit der Aufloesung der offenen Schleife, danach ein kurzer CTA wie 'Folg mir fuer mehr.' "
            "Schreib NUR den gesprochenen Text, keine Regieanweisungen, keine Klammern."
        ),
        "prompt_en": (
            _HOOK_REGEL_EN + " "
            "You are an expert in viral English motivational content on TikTok. "
            "Write a script for a 60-second faceless video. "
            "Rules: Start DIRECTLY with a strong hook sentence (no greeting, no 'Hey'). "
            "Use short, powerful sentences. Maximum 10 words per sentence. "
            "Build tension. End with the resolution of the open loop, then a short CTA like 'Follow me for more.' "
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
            "Ende mit der Aufloesung der offenen Schleife (der schockierendste Fakt kommt am Schluss), danach 'Folg mir fuer mehr.' "
            "Schreib NUR den gesprochenen Text, keine Regieanweisungen."
        ),
        "prompt_en": (
            _HOOK_REGEL_EN + " "
            "You are an expert in viral English facts content on TikTok. "
            "Write a script for a 60-second faceless video with 4-5 surprising facts. "
            "Rules: Start with a mind-blowing fact or a shocking statement. "
            "Each fact should surprise or shock. Short sentences. "
            "End with the resolution of the open loop (the most shocking fact comes last), then 'Follow me for more.' "
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

# Quickfire-Prompts (30s — höhere Completion Rate)
QUICKFIRE_PROMPTS = {
    "de": (
        "WICHTIGSTE REGEL: Du schreibst ein 30-SEKUNDEN Skript. Maximal 60 Wörter. "
        "Kein Wort zu viel. "
        "Starte mit einem Ein-Satz-Hook der sofort schockiert oder überrascht. "
        "Dann 2-3 Sätze Kern-Information. "
        "Ende mit einer Frage die zum Kommentieren animiert. "
        "Schreib NUR den gesprochenen Text. KEIN Kommentar über die Länge."
    ),
    "en": (
        "MOST IMPORTANT RULE: You are writing a 30-SECOND script. Maximum 60 words. "
        "No word too many. "
        "Start with a one-sentence hook that immediately shocks or surprises. "
        "Then 2-3 sentences of core information. "
        "End with a question that invites comments. "
        "Write ONLY the spoken text. NO comment about the length."
    ),
}

# Ausgabe-Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
VIDEOS_DIR = os.path.join(OUTPUTS_DIR, "videos")
TEMP_DIR = os.path.join(VIDEOS_DIR, "temp")
TIKTOK_DIR = os.path.join(VIDEOS_DIR, "tiktok")
SCRIPTS_DIR = os.path.join(OUTPUTS_DIR, "scripts")
LOG_FILE = os.path.join(SCRIPTS_DIR, "log.txt")
