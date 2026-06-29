import os
import re
import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, NICHES, SCRIPTS_DIR


def _remove_emojis(text):
    """Entfernt Emojis aus dem Text für sauberes Video-Rendering."""
    # Breites Unicode-Pattern für Emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbole & Piktogramme
        "\U0001F680-\U0001F6FF"  # Transport & Karten
        "\U0001F1E0-\U0001F1FF"  # Flaggen
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F900-\U0001F9FF"  # Ergänzende Symbole
        "\U00002600-\U000026FF"  # Verschiedene Symbole
        "\U0001FA00-\U0001FA6F"  # Schach-Symbole
        "\U0001FA70-\U0001FAFF"  # Weitere Symbole
        "\U00002500-\U00002BEF"  # Verschiedene technische Zeichen
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()


def _get_recent_scripts(niche, language, count=15):
    """Liest die letzten N Skripte dieser Nische+Sprache aus dem Skript-Ordner."""
    if not os.path.exists(SCRIPTS_DIR):
        return []
    files = sorted(
        [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(f"-{niche}-{language}.txt")],
        reverse=True
    )[:count]
    scripts = []
    for fname in files:
        try:
            with open(os.path.join(SCRIPTS_DIR, fname), encoding="utf-8") as f:
                content = f.read()
                # Nur den eigentlichen Text (nach dem Header)
                parts = content.split("=" * 60 + "\n", 1)
                if len(parts) > 1:
                    scripts.append(parts[1].strip()[:300])
        except Exception:
            pass
    return scripts


def extract_keywords(script_text, niche, language):
    """Ruft Claude auf und gibt 4 passende Pexels-Keywords für das Skript zurück."""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = (
            "Lies dieses Video-Skript und gib mir 4 konkrete englische Suchbegriffe für Pexels Stock-Videos zurück, "
            "die visuell zum Inhalt passen. Nur die Begriffe, kommagetrennt, keine Erklärung. "
            "Beispiel: 'money cash, luxury car, city night, success businessman'\n\n"
            f"Skript:\n{script_text}"
        )
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip().strip("`")
        keywords = [kw.strip().strip("`").strip("'\"") for kw in raw.split(",") if kw.strip().strip("`")]
        # Sicherstellen dass wir 4 Keywords haben
        if len(keywords) >= 1:
            print(f"[script_generator] B-Roll Keywords: {keywords[:4]}")
            return keywords[:4]
    except Exception as e:
        print(f"[script_generator] Keyword-Extraktion fehlgeschlagen, nutze Nischen-Fallback: {e}")

    # Fallback: zufällige Nischen-Keywords
    from config import NICHES
    import random
    fallback = NICHES[niche]["pexels_keywords"].copy()
    random.shuffle(fallback)
    return fallback[:4]


def generate_script(niche, language):
    """Generiert ein Skript per Claude API. Gibt den fertigen Text zurück."""
    if niche not in NICHES:
        raise ValueError(f"Unbekannte Nische: {niche}. Verfügbar: {list(NICHES.keys())}")
    if language not in ["de", "en"]:
        raise ValueError(f"Unbekannte Sprache: {language}. Verfügbar: de, en")

    niche_config = NICHES[niche]
    prompt_key = f"prompt_{language}"
    system_prompt = niche_config[prompt_key]

    # Letzte Skripte laden und als Kontext mitgeben
    recent = _get_recent_scripts(niche, language)
    if recent:
        avoid_block = "\n\nDiese Themen wurden bereits produziert — wähle ein völlig anderes Thema, erwähne diese Liste NICHT im Skript:\n"
        for i, s in enumerate(recent, 1):
            avoid_block += f"\n[{i}] {s[:200]}...\n"
        avoid_block += "\nSchreib das neue Skript direkt, ohne Kommentar über die Themenwahl."
        system_prompt = system_prompt + avoid_block

    # Trending-Thema holen und in den Prompt einbauen
    try:
        from trends_client import get_trending_topic
        topic = get_trending_topic(niche)
        if topic:
            system_prompt = system_prompt + f"\n\nAKTUELLES THEMA: Schreib das Skript über dieses spezifische Thema: '{topic}'"
    except Exception:
        pass  # Kein Trending-Thema → freie Themenwahl

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Schreib jetzt das Skript." if language == "de" else "Write the script now."}
        ],
        system=system_prompt,
    )

    script_text = message.content[0].text.strip()

    # Emojis aus dem Skript-Text entfernen (für sauberes Video-Rendering)
    script_text = _remove_emojis(script_text)
    # Gedankenstriche und Bindestriche zwischen Sätzen entfernen
    script_text = re.sub(r"\s*—\s*", " ", script_text)
    script_text = re.sub(r"\s*–\s*", " ", script_text)
    # Mehrfache Leerzeichen bereinigen
    script_text = re.sub(r"  +", " ", script_text).strip()

    # Skript speichern
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d-%H%M")
    filename = f"{date_str}-{niche}-{language}.txt"
    filepath = os.path.join(SCRIPTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Nische: {niche} | Sprache: {language} | Erstellt: {datetime.now()}\n")
        f.write("=" * 60 + "\n")
        f.write(script_text)

    print(f"[script_generator] Skript gespeichert: {filename}")
    return script_text


def generate_title(script_text, niche, language):
    """Erzeugt einen packenden, content-bezogenen Titel fürs Video (ohne Datum/Zahlencodes)."""
    if language == "de":
        instruction = (
            "Schreib einen kurzen, neugierig machenden YouTube-Shorts-Titel für dieses Video. "
            "Maximal 60 Zeichen. KEIN Datum, KEINE Uhrzeit, KEINE technischen Codes. "
            "Pack 1-2 passende Emojis rein wenn es passt. Gib NUR den Titel zurück, sonst nichts.\n\n"
            f"Skript:\n{script_text}"
        )
    else:
        instruction = (
            "Write a short, curiosity-driving YouTube Shorts title for this video. "
            "Max 60 characters. NO date, NO time, NO technical codes. "
            "Add 1-2 fitting emojis if appropriate. Return ONLY the title, nothing else.\n\n"
            f"Script:\n{script_text}"
        )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": instruction}],
    )
    title = message.content[0].text.strip().strip('"').strip()
    # Sicherheitsnetz: auf 100 Zeichen kürzen (YouTube-Limit)
    return title[:100]
