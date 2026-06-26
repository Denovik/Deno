# Jarvis Content Bot

Vollautomatischer Content-Bot. Erstellt täglich Kurzvideos für TikTok, Instagram und YouTube — ohne manuelle Arbeit.

## Was er macht

1. Generiert ein Skript (Motivation oder Fakten & Wissen, Deutsch oder Englisch)
2. Wandelt es per ElevenLabs in eine KI-Stimme um
3. Lädt ein passendes Stock-Video von Pexels herunter
4. Baut ein 60-Sekunden 9:16 Video mit Stimme + Stock + Untertiteln
5. Postet automatisch auf TikTok (2x täglich), Instagram (1x) und YouTube (1x)

## Starten

```bash
cd scripts/jarvis

# Abhängigkeiten installieren
pip3 install -r requirements.txt

# Testlauf (nur Skript generieren, kein Video, kein Post)
python3 run.py --dry-run

# Einmalig 2 Videos erstellen und posten
python3 run.py --once --count 2

# Dauerbetrieb (täglich 08:00 Uhr)
python3 run.py
```

## Keys, die du brauchst

| Variable | Wozu | Wo holen |
|---|---|---|
| `ANTHROPIC_API_KEY` | Skript-Generierung | console.anthropic.com |
| `ELEVENLABS_API_KEY` | KI-Stimme | elevenlabs.io |
| `ELEVENLABS_VOICE_ID_DE` | Deutsche Stimme | ElevenLabs Voice Library |
| `ELEVENLABS_VOICE_ID_EN` | Englische Stimme | ElevenLabs Voice Library |
| `PEXELS_API_KEY` | Stock-Videos | pexels.com/api |
| `TIKTOK_ACCESS_TOKEN` | TikTok posten | TikTok Developer Portal |
| `META_ACCESS_TOKEN` | Instagram posten | Meta for Developers |
| `INSTAGRAM_ACCOUNT_ID` | Instagram posten | Meta for Developers |
| `YOUTUBE_CLIENT_SECRET_PATH` | YouTube hochladen | Google Cloud Console |

Alle Keys kommen in `.env` im CEO-GPT-Root (nie committen).

## Fehlende Keys

Wenn ein Key fehlt, überspringt der Bot diese Plattform und macht weiter. Kein Crash.

## Ausgabe-Ordner

```
outputs/
  scripts/     → Generierte Skripte als .txt
  videos/      → Fertige MP4-Videos
    temp/      → Temporäre Audio- und Stock-Dateien (automatisch gelöscht)
```

## Automatisch starten (Cron)

Damit der Bot täglich ohne dein Zutun läuft:

```bash
# Crontab öffnen
crontab -e

# Täglich 08:00 Uhr
0 8 * * * cd /Users/dennisgluck/Desktop/CLAUDE/ceogpt-start && python3 scripts/jarvis/run.py --once --count 4
```
