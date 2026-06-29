import os
import random
import datetime
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


def get_seasonal_topics() -> dict:
    """Gibt saisonale Themen basierend auf dem aktuellen Monat zurück."""
    month = datetime.datetime.now().month
    seasonal = {
        1:  {"motivation": ["Neujahrsvorsätze umsetzen", "Januar-Motivation"], "fakten": ["Winterschlaf Fakten", "Kältere Fakten"], "psychologie": ["Frischer Start Psychologie", "Neujahr Gewohnheiten"], "finanzen": ["Jahresbudget planen", "Steuerrückerstattung"]},
        2:  {"motivation": ["Valentinstag Selbstliebe", "Februar Durchhalten"], "fakten": ["Liebe und Gehirn", "Herzfakten"], "psychologie": ["Liebe Psychologie", "Attachment Styles"], "finanzen": ["Romantik und Geld", "Paar-Finanzen"]},
        3:  {"motivation": ["Frühling Neuanfang", "März Energie"], "fakten": ["Frühlings-Fakten", "Tag-Nacht-Gleiche"], "psychologie": ["Frühjahrsputz Psychologie", "Saisonale Depression"], "finanzen": ["Steuererklärung", "Frühlings-Sparziele"]},
        4:  {"motivation": ["Quartalsziele Q2", "April Frische"], "fakten": ["Regen Fakten", "Aprilwetter Wissenschaft"], "psychologie": ["Humor Psychologie", "Lachen Wissenschaft"], "finanzen": ["Q1 Rückblick", "Investieren im Frühling"]},
        5:  {"motivation": ["Maifeiertag Bedeutung", "Frühlingsenergie"], "fakten": ["Mai Naturphänomene", "Bienen Fakten"], "psychologie": ["Mutterrolle Psychologie", "Familie Bindung"], "finanzen": ["Urlaub finanzieren", "Sommer sparen"]},
        6:  {"motivation": ["Sommerziele", "Halbzeit Motivation"], "fakten": ["Sommer Fakten", "Sonnenwende"], "psychologie": ["FOMO Sommer", "Ferienpsychologie"], "finanzen": ["Halbjahres-Check", "Urlaub ohne Schulden"]},
        7:  {"motivation": ["Hochsommer Energie", "Urlaubs-Mindset"], "fakten": ["Hitze Fakten", "Meer Geheimnisse"], "psychologie": ["Urlaubspsychologie", "Erholung Wissenschaft"], "finanzen": ["Urlaubsbudget", "Sommerjobs"]},
        8:  {"motivation": ["Augustziele", "Back-to-School Mindset"], "fakten": ["August Astronomie", "Schulstart Fakten"], "psychologie": ["Lernen Psychologie", "Konzentration verbessern"], "finanzen": ["Schulkosten", "Herbst vorbereiten"]},
        9:  {"motivation": ["Herbst Neustart", "Septemberziele"], "fakten": ["Herbst Naturphänomene", "Ernte Fakten"], "psychologie": ["Herbst-Blues", "Saisonwechsel Psychologie"], "finanzen": ["Q3 Abschluss", "Wintervorrat Finanzen"]},
        10: {"motivation": ["Halloween Angst überwinden", "Oktober Energie"], "fakten": ["Halloween Ursprung", "Herbstfakten"], "psychologie": ["Angst Psychologie", "Dunkelheit und Stimmung"], "finanzen": ["Jahresendplanung", "Weihnachtsbudget starten"]},
        11: {"motivation": ["Novembermotivation", "Dankbarkeit Mindset"], "fakten": ["Black Friday Psychologie", "November Fakten"], "psychologie": ["Dankbarkeit Wissenschaft", "Winterdepression"], "finanzen": ["Black Friday clever shoppen", "Jahresabschluss Finanzen"]},
        12: {"motivation": ["Jahresrückblick", "Weihnachtsmotivation"], "fakten": ["Weihnachten Ursprung", "Winter Fakten"], "psychologie": ["Stress Weihnachten", "Jahreswechsel Psychologie"], "finanzen": ["Jahresabschluss", "Neues Jahr Finanzplan"]},
    }
    return seasonal.get(month, {})


def get_trending_topic(niche: str) -> str:
    """Gibt ein aktuell relevantes Thema für die Nische zurück."""
    topics = list(TREND_TOPICS.get(niche, []))
    if not topics:
        return None

    # Saisonale Themen ergänzen
    seasonal = get_seasonal_topics()
    if niche in seasonal:
        topics = topics + seasonal[niche]

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
