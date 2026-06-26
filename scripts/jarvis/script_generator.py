import os
import anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY, NICHES, SCRIPTS_DIR


def generate_script(niche: str, language: str) -> str:
    """Generiert ein Skript per Claude API. Gibt den fertigen Text zurück."""
    if niche not in NICHES:
        raise ValueError(f"Unbekannte Nische: {niche}. Verfügbar: {list(NICHES.keys())}")
    if language not in ["de", "en"]:
        raise ValueError(f"Unbekannte Sprache: {language}. Verfügbar: de, en")

    niche_config = NICHES[niche]
    prompt_key = f"prompt_{language}"
    system_prompt = niche_config[prompt_key]

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
