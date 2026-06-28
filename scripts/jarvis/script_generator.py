import os
import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, NICHES, SCRIPTS_DIR


def _get_recent_scripts(niche: str, language: str, count: int = 15) -> list[str]:
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


def generate_script(niche: str, language: str) -> str:
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
        avoid_block = "\n\nWICHTIG: Diese Themen und Einstiege wurden bereits verwendet — NICHT wiederholen, komplett neues Thema wählen:\n"
        for i, s in enumerate(recent, 1):
            avoid_block += f"\n[{i}] {s[:200]}...\n"
        system_prompt = system_prompt + avoid_block

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


def generate_title(script_text: str, niche: str, language: str) -> str:
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
