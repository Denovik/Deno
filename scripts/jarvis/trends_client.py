import os
import random
import anthropic
from config import ANTHROPIC_API_KEY

# Themen-Pool pro Nische — manuell kuriert, aber Claude wählt das aktuell passendste
TREND_TOPICS = {
    "motivation": [
        "Prokrastination überwinden", "Disziplin aufbauen", "Gewohnheiten ändern",
        "Selbstsabotage stoppen", "Komfortzone verlassen", "Morgenroutine optimieren",
        "Ziele setzen und erreichen", "Innere Stimme", "Versagen als Lehrer",
        "Mindset Shift", "Resilienz aufbauen", "Fokus verbessern",
    ],
    "fakten": [
        "Ozean Geheimnisse", "Weltraum Fakten", "Menschlicher Körper", "Tier-Rekorde",
        "Historische Zufälle", "Technologie der Zukunft", "Optische Täuschungen erklären",
        "Mathe-Paradoxon", "Quantenphysik einfach", "Extremes Wetter",
        "Unterwasser-Welt", "Unsichtbare Welt (Bakterien/Atome)",
    ],
    "psychologie": [
        "Dunning-Kruger-Effekt", "Confirmation Bias", "Stockhholm-Syndrom",
        "Impostor-Syndrom", "Sunk Cost Fallacy", "Halo-Effekt",
        "Priming-Effekt", "Cognitive Dissonance", "Bystander-Effekt",
        "Social Proof", "Anchoring Bias", "FOMO Psychologie",
    ],
    "finanzen": [
        "Compound Interest Magie", "Inflation verstehen", "ETF für Anfänger",
        "Reichste 1% Geheimnisse", "Schulden loswerden", "Passives Einkommen aufbauen",
        "Kreditkarten-Fallen", "Mietentscheidung vs. Kauf", "Steuern sparen legal",
        "Warren Buffett Prinzipien", "Crypto Risiken", "Notgroschen Regel",
    ],
}


def get_trending_topic(niche: str) -> str:
    """Gibt ein aktuell relevantes Thema für die Nische zurück."""
    topics = TREND_TOPICS.get(niche, [])
    if not topics:
        return None

    # Claude wählt das überraschendste/interessanteste Thema
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        topics_str = "\n".join(f"- {t}" for t in topics)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": (
                    f"Welches dieser Themen hat gerade das höchste virale Potenzial auf TikTok? "
                    f"Antworte NUR mit dem Thema, nichts sonst.\n\n{topics_str}"
                )
            }],
        )
        topic = message.content[0].text.strip().lstrip("- ").strip()
        print(f"[trends] Trending-Thema für {niche}: {topic}")
        return topic
    except Exception as e:
        print(f"[trends] Fallback auf Zufalls-Thema: {e}")
        return random.choice(topics)
