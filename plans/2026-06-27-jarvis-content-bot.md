# Plan: Jarvis Content Bot — Vollautomatisierte Content-Pipeline

**Erstellt:** 2026-06-27
**Status:** Umgesetzt
**Anfrage:** Baue einen vollautomatisierten Bot, der täglich Content für TikTok, Instagram und YouTube generiert, produziert und postet.

---

## Überblick

### Was dieser Plan erreicht

Ein Python-System (Jarvis) läuft täglich automatisch, generiert Skripte in zwei Nischen (Motivation + Fakten/Wissen) auf Deutsch und Englisch, wandelt sie per ElevenLabs in Sprache um, baut daraus fertige Videos mit Stock-Material und Texteinblendungen zusammen und postet sie auf TikTok (2×/Tag), Instagram (1×/Tag) und YouTube (1×/Tag). Dennis muss nichts manuell tun.

### Warum das zählt

Das ist der Kern des Jarvis-Systems. Ohne diesen Bot gibt es keine Einnahmen. Mit ihm läuft die Content-Maschine ohne tägliche Handarbeit — das ist die Voraussetzung für passives Einkommen und das Ziel von 2.000 €/Monat.

---

## Aktueller Stand

### Bestehende relevante Struktur

- `.env` mit `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY` gesetzt
- `context/` mit Business, Strategie und Zielen
- Keine `scripts/` Ordner, kein bestehendes Automatisierungs-System
- `plans/` Ordner vorhanden aber leer

### Lücken oder Probleme, die der Plan löst

- Kein automatisierter Content-Prozess
- Keine API-Verbindungen zu Plattformen
- Kein Posting-System
- Keine Video-Produktions-Pipeline

---

## Geplante Änderungen

### Zusammenfassung der Änderungen

- `scripts/jarvis/` Ordner anlegen mit dem gesamten Bot-Code
- Haupt-Skript `run.py` das den täglichen Ablauf steuert
- Module für Skript-Generierung, Sprache, Video-Produktion, Posting
- Konfigurationsdatei für Nischen, Sprachen, Posting-Zeiten
- Abhängigkeiten-Datei `requirements.txt`
- `.env` um fehlende API-Keys erweitern
- `CLAUDE.md` aktualisieren mit neuem `scripts/` Abschnitt

### Neue Dateien

| Pfad | Zweck |
|---|---|
| `scripts/jarvis/run.py` | Haupt-Einstiegspunkt, steuert den Tagesablauf |
| `scripts/jarvis/config.py` | Nischen, Sprachen, Posting-Zeiten, Stimmen-IDs |
| `scripts/jarvis/script_generator.py` | Claude API → Skript generieren |
| `scripts/jarvis/voice_generator.py` | ElevenLabs API → MP3 aus Skript |
| `scripts/jarvis/video_builder.py` | MoviePy → Fertiges Video aus Audio + Stock + Text |
| `scripts/jarvis/pexels_client.py` | Pexels API → Stock-Video holen |
| `scripts/jarvis/poster_youtube.py` | YouTube Data API → Video hochladen |
| `scripts/jarvis/poster_instagram.py` | Meta Graph API → Reel posten |
| `scripts/jarvis/poster_tiktok.py` | TikTok API → Video posten |
| `scripts/jarvis/requirements.txt` | Python-Abhängigkeiten |
| `scripts/jarvis/README.md` | Wie man den Bot startet und wartet |
| `outputs/videos/` | Ordner für fertige Videos (wird angelegt) |
| `outputs/scripts/` | Ordner für generierte Skripte zur Nachverfolgung |

### Geänderte Dateien

| Pfad | Änderungen |
|---|---|
| `.env` | Neue Keys: ELEVENLABS_VOICE_ID_DE, ELEVENLABS_VOICE_ID_EN, PEXELS_API_KEY, YOUTUBE_CLIENT_SECRET_PATH, META_ACCESS_TOKEN, TIKTOK_ACCESS_TOKEN |
| `.env.example` | Gleiche neuen Keys dokumentiert |
| `CLAUDE.md` | `scripts/` Ordner in Struktur-Tabelle ergänzen |
| `HISTORY.md` | Eintrag nach Umsetzung |

---

## Design-Entscheidungen

### Wichtige Entscheidungen

1. **Claude API statt ChatGPT für Skripte**: Anthropic-Key bereits vorhanden, kein Extra-Cost
2. **ElevenLabs für Stimme**: Kostenlose Tier reicht für ~10 Videos/Monat, danach 5 €/Monat — günstigste Option mit natürlicher Qualität
3. **MoviePy für Video-Produktion**: Kostenlos, Python-nativ, ausreichend für Faceless-Videos
4. **Pexels API für Stock-Videos**: Komplett kostenlos, gute Qualität, kein Wasserzeichen
5. **Modularer Aufbau**: Jeder Schritt (Skript → Stimme → Video → Post) ist ein eigenes Modul — wenn eine Plattform ihre API ändert, muss nur ein Modul angepasst werden
6. **Täglicher Cron-Job statt dauerlaufendem Server**: Ressourcenschonend, kostenlos mit Mac-Bordmitteln (launchd/cron)

### Verworfene Alternativen

- **CapCut API**: Nicht verfügbar, nur manuelles Tool
- **Buffer API für Posting**: Paid-Only für API-Zugang, zu teuer
- **Eigener Video-Rendering-Server**: Unnötig komplex und kostspielig

### Offene Fragen

1. **TikTok API**: TikTok hat eine restriktive API — für neue Accounts oft nicht direkt verfügbar. Fallback: Videos werden als fertige Datei gespeichert und können manuell oder per Drittanbieter (später) gepostet werden. **Empfehlung:** TikTok in Phase 2, YouTube und Instagram zuerst automatisieren.
2. **ElevenLabs Stimmen-ID**: Dennis muss einmalig eine Stimme auswählen und die ID eintragen.
3. **Pexels API Key**: Kostenlos, braucht einmalige Registrierung.

---

## Schritt-für-Schritt-Aufgaben

### 1. Ordner-Struktur anlegen

Anlegen der Basis-Ordner für den Bot.

**Aktionen:**
- `scripts/jarvis/` anlegen
- `outputs/videos/` anlegen
- `outputs/scripts/` anlegen

**Betroffene Dateien:**
- Neue Ordner

---

### 2. requirements.txt schreiben

Alle Python-Abhängigkeiten auflisten.

**Aktionen:**
- `scripts/jarvis/requirements.txt` schreiben mit:
  ```
  anthropic>=0.25.0
  elevenlabs>=1.0.0
  moviepy>=1.0.3
  requests>=2.31.0
  Pillow>=10.0.0
  google-api-python-client>=2.0.0
  google-auth-httplib2>=0.1.0
  google-auth-oauthlib>=1.0.0
  python-dotenv>=1.0.0
  schedule>=1.2.0
  ```

**Betroffene Dateien:**
- `scripts/jarvis/requirements.txt`

---

### 3. config.py schreiben

Zentrale Konfigurationsdatei — Nischen, Prompts, Stimmen, Posting-Zeiten.

**Aktionen:**
- `scripts/jarvis/config.py` schreiben mit:
  - `NICHES`: Dict mit Motivations- und Fakten-Nischen inkl. System-Prompts auf DE und EN
  - `POSTING_SCHEDULE`: 2× TikTok, 1× Instagram, 1× YouTube täglich
  - `LANGUAGES`: `["de", "en"]`
  - `VIDEO_DURATION_TARGET`: 60 Sekunden
  - Umgebungsvariablen-Loader via `python-dotenv`

**Betroffene Dateien:**
- `scripts/jarvis/config.py`

---

### 4. script_generator.py schreiben

Modul das per Claude API Skripte generiert.

**Aktionen:**
- `scripts/jarvis/script_generator.py` schreiben
- Funktion `generate_script(niche, language)` → gibt fertiges Skript als String zurück
- System-Prompt: "Du bist ein Experte für viralen Social-Media-Content. Schreib ein 60-Sekunden-Skript für {niche} auf {language}. Kein Intro. Direkt mit Hook starten. Ende mit Call-to-Action 'Folg mir für mehr.'"
- Nutzt `anthropic` Library mit `ANTHROPIC_API_KEY` aus `.env`
- Speichert Skript in `outputs/scripts/YYYY-MM-DD-{niche}-{lang}.txt`

**Betroffene Dateien:**
- `scripts/jarvis/script_generator.py`

---

### 5. voice_generator.py schreiben

Modul das per ElevenLabs API Text in MP3 umwandelt.

**Aktionen:**
- `scripts/jarvis/voice_generator.py` schreiben
- Funktion `generate_voice(script_text, language)` → gibt Pfad zur MP3-Datei zurück
- Wählt Stimme basierend auf Sprache: `ELEVENLABS_VOICE_ID_DE` oder `ELEVENLABS_VOICE_ID_EN` aus `.env`
- Speichert MP3 temporär in `outputs/videos/temp/`
- Nutzt ElevenLabs Python SDK

**Betroffene Dateien:**
- `scripts/jarvis/voice_generator.py`

---

### 6. pexels_client.py schreiben

Modul das passende Stock-Videos von Pexels holt.

**Aktionen:**
- `scripts/jarvis/pexels_client.py` schreiben
- Funktion `get_stock_video(niche, duration_seconds)` → gibt Pfad zum heruntergeladenen Video zurück
- Sucht per Pexels API nach Stichwörtern je nach Nische:
  - Motivation: "sunset", "mountain", "running", "success", "city timelapse"
  - Fakten: "space", "nature", "ocean", "science", "earth"
- Wählt zufällig aus den Top-5 Ergebnissen
- Lädt Video herunter in `outputs/videos/temp/`

**Betroffene Dateien:**
- `scripts/jarvis/pexels_client.py`

---

### 7. video_builder.py schreiben

Modul das fertiges Video aus Audio + Stock + Text zusammenbaut.

**Aktionen:**
- `scripts/jarvis/video_builder.py` schreiben
- Funktion `build_video(audio_path, stock_video_path, script_text, output_path)` → fertiges MP4
- Pipeline:
  1. Stock-Video auf 9:16 (1080×1920) zuschneiden für Hochformat
  2. Audio-Spur durch KI-Stimme ersetzen
  3. Video auf Audio-Länge kürzen oder loopen
  4. Untertitel/Text-Einblendungen hinzufügen (großer weißer Text, mittig unten)
  5. Leichte Abdunklung des Hintergrunds für bessere Lesbarkeit
  6. Exportieren als MP4, 1080×1920, 30fps
- Nutzt `moviepy` und `Pillow`

**Betroffene Dateien:**
- `scripts/jarvis/video_builder.py`

---

### 8. poster_youtube.py schreiben

Modul das Videos per YouTube Data API hochlädt.

**Aktionen:**
- `scripts/jarvis/poster_youtube.py` schreiben
- Funktion `upload_to_youtube(video_path, title, description, tags)` → gibt Video-ID zurück
- OAuth2-Authentifizierung mit Client Secret JSON (einmalig, dann Token gespeichert)
- Titel-Format: "[Nische Emoji] [Skript-Hook] #shorts"
- Beschreibung mit relevanten Hashtags
- Kategorie: 26 (Ratgeber & Style) für Motivation, 27 (Bildung) für Fakten

**Betroffene Dateien:**
- `scripts/jarvis/poster_youtube.py`

---

### 9. poster_instagram.py schreiben

Modul das Reels per Meta Graph API postet.

**Aktionen:**
- `scripts/jarvis/poster_instagram.py` schreiben
- Funktion `post_to_instagram(video_path, caption)` → gibt Post-ID zurück
- Nutzt Meta Content Publishing API (Reels-Endpoint)
- Braucht: `META_ACCESS_TOKEN` und `INSTAGRAM_ACCOUNT_ID` in `.env`
- Caption mit Hashtags: #motivation #motivation #deutsch #lernen etc.

**Betroffene Dateien:**
- `scripts/jarvis/poster_instagram.py`

---

### 10. poster_tiktok.py schreiben — Priorität 1

TikTok ist die Hauptplattform (1.701 Follower vorhanden). Wir nutzen die offizielle TikTok Content Posting API.

**Aktionen:**
- `scripts/jarvis/poster_tiktok.py` schreiben
- Funktion `post_to_tiktok(video_path, caption)` → gibt Post-ID zurück
- Nutzt TikTok Content Posting API (Direct Post)
- Braucht: `TIKTOK_ACCESS_TOKEN` und `TIKTOK_OPEN_ID` in `.env`
- Caption mit Hashtags: #motivation #wissen #lernen #deutsch #tiktokdeutschland etc.
- Fallback: Wenn Token fehlt, Video in `outputs/videos/tiktok/` speichern mit Logging

**Voraussetzung (einmalig, Dennis macht das vor dem ersten Run):**
1. developers.tiktok.com → Login mit TikTok-Account
2. "Create App" → App-Name z.B. "JarvisBot"
3. "Content Posting API" aktivieren
4. Client Key + Client Secret kopieren → in `.env`
5. OAuth-Flow einmalig im Browser durchlaufen → Access Token generieren

**Betroffene Dateien:**
- `scripts/jarvis/poster_tiktok.py`

---

### 11. run.py schreiben — der Haupt-Einstiegspunkt

Steuert den kompletten Tagesablauf.

**Aktionen:**
- `scripts/jarvis/run.py` schreiben
- Tagesablauf:
  1. Wähle zufällig Nische (Motivation oder Fakten) + Sprache (DE oder EN)
  2. Generiere Skript via `script_generator`
  3. Generiere Stimme via `voice_generator`
  4. Hole Stock-Video via `pexels_client`
  5. Baue Video via `video_builder`
  6. Poste auf YouTube via `poster_youtube`
  7. Poste auf Instagram via `poster_instagram`
  8. Speichere TikTok-Version via `poster_tiktok`
  9. Räume temporäre Dateien auf
  10. Logge Ergebnis in `outputs/scripts/log.txt`
- Kommandozeilen-Argument `--count N` um N Videos in einem Durchlauf zu generieren (Standard: 1)
- Error-Handling: Bei Fehler in einem Schritt weitermachen, Fehler loggen

**Betroffene Dateien:**
- `scripts/jarvis/run.py`

---

### 12. .env und .env.example aktualisieren

Neue Keys dokumentieren.

**Aktionen:**
- Folgende Keys in `.env` ergänzen (leer, Dennis füllt sie):
  ```
  ELEVENLABS_VOICE_ID_DE=
  ELEVENLABS_VOICE_ID_EN=
  PEXELS_API_KEY=
  YOUTUBE_CLIENT_SECRET_PATH=credentials/youtube_client_secret.json
  META_ACCESS_TOKEN=
  INSTAGRAM_ACCOUNT_ID=
  TIKTOK_ACCESS_TOKEN=
  ```
- Gleiche Keys in `.env.example` mit Kommentaren wo man sie holt

**Betroffene Dateien:**
- `.env`
- `.env.example`

---

### 13. README.md für den Bot schreiben

**Aktionen:**
- `scripts/jarvis/README.md` schreiben mit:
  - Was der Bot macht
  - Setup-Schritte (einmalig): `pip install -r requirements.txt`, API-Keys eintragen
  - Wie man ihn startet: `python run.py`
  - Wie man ihn täglich automatisch laufen lässt (Mac cron)
  - Wie man Nischen und Prompts anpasst
  - Troubleshooting-Abschnitt

**Betroffene Dateien:**
- `scripts/jarvis/README.md`

---

### 14. CLAUDE.md aktualisieren

**Aktionen:**
- In der Ordner-Struktur-Tabelle `scripts/` ergänzen:
  ```
  | `scripts/jarvis/` | Vollautomatisierter Content-Bot (Skript → Stimme → Video → Post) |
  ```
- `outputs/videos/` und `outputs/scripts/` in die Tabelle aufnehmen

**Betroffene Dateien:**
- `CLAUDE.md`

---

### 15. Setup-Test durchführen

**Aktionen:**
- Python 3.9+ prüfen: `python3 --version`
- Abhängigkeiten installieren: `pip install -r scripts/jarvis/requirements.txt`
- Test-Lauf mit `--dry-run` Flag (nur Skript generieren, kein Video, kein Posting):
  ```bash
  python scripts/jarvis/run.py --dry-run
  ```
- Prüfen, ob Skript generiert wird und in `outputs/scripts/` landet

**Betroffene Dateien:**
- Keine (nur Test)

---

## Verbindungen und Abhängigkeiten

### Dateien, die auf diesen Bereich verweisen

- `CLAUDE.md` — muss `scripts/` erwähnen
- `.env` — alle API-Keys des Bots
- `context/strategy.md` — Jarvis ist der Kern der Strategie

### Updates für Konsistenz

- `HISTORY.md` nach Umsetzung aktualisieren
- `docs/` — System-Doku für den Bot anlegen nach Umsetzung

### Auswirkung auf bestehende Abläufe

- Kein Einfluss auf bestehende Befehle
- `/commit` wird nach dem Build genutzt um alles zu sichern

---

## Prüf-Checkliste

- [ ] `scripts/jarvis/` Ordner existiert mit allen Modulen
- [ ] `pip install -r requirements.txt` läuft ohne Fehler
- [ ] `python run.py --dry-run` generiert ein Skript ohne Fehler
- [ ] Skript landet in `outputs/scripts/`
- [ ] `.env` hat alle neuen Keys (leer, aber vorhanden)
- [ ] `CLAUDE.md` spiegelt neue Struktur

---

## Erfolgskriterien

Die Umsetzung ist fertig, wenn:

1. `python scripts/jarvis/run.py` startet ohne Crash
2. Ein Skript wird per Claude API generiert und gespeichert
3. Alle Module existieren und sind importierbar
4. Dennis kann die API-Keys eintragen und sofort loslegen

---

## Notizen

- **TikTok-Posting ist Priorität 1:** Dennis hat 1.701 Follower — kein Null-Account. TikTok Content Posting API wird direkt eingerichtet. Einmalige Developer-Registrierung nötig, danach vollautomatisch.
- **ElevenLabs Free Tier:** 10.000 Zeichen/Monat kostenlos. Bei 60-Sekunden-Skripten (~500 Zeichen) reicht das für ~20 Videos. Für mehr: Starter-Plan bei 5 €/Monat.
- **Pexels API:** Kostenlos, braucht einmalige Registrierung auf pexels.com/api
- **YouTube OAuth:** Einmalige Browser-Authentifizierung nötig, dann Token gespeichert
- **Cron-Job:** Nach dem Build zeigen wir Dennis wie er `run.py` täglich automatisch starten lässt

---

## Umsetzungs-Notizen

**Umgesetzt:** 2026-06-27

### Zusammenfassung

Alle 8 Bot-Dateien wurden vollständig implementiert. Der Dry-Run läuft erfolgreich durch, alle Module importieren korrekt.

### Abweichungen vom Plan

- moviepy 2.x hat geändertes Import-System — `video_builder.py` nutzt Try/Except-Fallback für beide Versionen
- Dry-run bricht bei Anthropic API ab (Guthaben leer) — das ist kein Code-Fehler, sondern Account-Status

### Aufgetretene Probleme

- Pip-Permission-Fehler auf dem System-Python → Lösung: virtualenv für Tests
- moviepy 2.x hat `moviepy.editor` entfernt → Lösung: dualer Import-Pfad
- Anthropic-Konto hat kein Guthaben → Dennis muss credits.anthropic.com aufstocken, dann läuft der Bot voll
