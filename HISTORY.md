# CEO-GPT Historie

> Zeitliches Logbuch aller Arbeiten in diesem CEO-GPT. Wird jede Session aktualisiert.
> Neueste Einträge oben. Jeder Eintrag hat Datum, Titel und Bullet Points.
>
> **So läuft's:** Wenn du `/commit` nach einer sinnvollen Arbeit ausführst, trägt dein
> Mitarbeiter hier automatisch ein. Du musst diese Datei nicht selbst schreiben.

---

## 2026-06-30

### Jarvis-Pipeline auf Hetzner-Server umgezogen

- Pipeline läuft jetzt vollautomatisch auf Server 167.233.95.3 — Mac muss nicht mehr an sein
- Cron-Zeitplan: Videos 19:00, Daten-Sammlung 08:00, Analyse montags 09:00 (Zeitzone Europe/Berlin)
- Server-Toolkit: Python 3.14.4, ffmpeg 8.0.1, venv mit allen Paketen, Musik übertragen
- Zwei Bugs gefixt: 4K-Video-Begrenzung (max 1920p), Download-Vollständigkeits-Check
- Lokale launchd-Agents deaktiviert (Plist-Dateien als Fallback erhalten)
- Deployment-Skript: `bash scripts/jarvis/deploy_to_server.sh`
- Doku: `reference/server-deployment.md`
- Plan: `plans/2026-06-30-jarvis-server-umzug.md`

### Personal OS aufgebaut

- Neuer Bereich `personal-os/` — Dennis' Leben außerhalb des Mindwave-Business: Profil, Ziele & Notizen, Aufgaben & Termine, Wissens-Archiv, Gesundheit & Finanzen
- Eigene SQLite-Datenbank `personal-os/personal.db` (Tabellen `health_daily`, `finance_transactions`, `tasks_log`), bewusst getrennt von `data/data.db`
- Neuer Befehl `/personal-prime` lädt den Personal-OS-Kontext, unabhängig von `/prime`
- Gesundheits-/Finanzdaten bleiben lokal (gitignored), nicht versioniert
- `CLAUDE.md` und `docs/_index.md` aktualisiert, Doku unter `docs/personal-os.md`
- Plan: `plans/2026-06-30-personal-os.md`

## 2026-06-27

### Jarvis Web-Interface (visueller Arc-Reactor, händefrei)

- Lokale Web-App: `web_app.py` (Flask) + `web/index.html` (Arc-Reactor-Oberfläche)
- Händefrei: Browser erkennt per Voice-Activity-Detection, wann man fertig spricht
- Orb-Zustände: bereit → höre zu → denke nach → spricht
- Kern-Logik in `jarvis_brain.py` extrahiert (geteilt mit Terminal-Interface)
- Doppelklick-Starter `start_jarvis.command`, Server auf http://localhost:5005
- Server-Kette getestet: Transkript, Claude-Antwort mit Kontext, Sprach-Antwort ok

### Jarvis Voice-Interface gebaut

- `scripts/jarvis/voice_chat.py` — mit Jarvis sprechen, er antwortet mit Stimme
- Lokale Spracherkennung (faster-whisper, kostenlos/offline), Claude als Gehirn, ElevenLabs-Stimme
- Jarvis kennt Dennis' Business-Kontext (lädt `context/`-Dateien)
- Kette getestet: Spracherkennung erkannte deutschen Testsatz wortgenau, Jarvis antwortet im richtigen Ton
- Plan: `plans/2026-06-27-jarvis-voice-interface.md`

### Jarvis: Untertitel, Musik, Titel & Plattform-Anbindung

- Untertitel-Sync gefixt (frame-genaues Einbrennen Wort für Wort, kein Overlap)
- Content-bezogene Video-Titel statt Datum/Codes (`generate_title` per Claude)
- Leise Hintergrundmusik (12%) aus `music/` unter die Stimme gemischt
- **YouTube live & vollautomatisch:** Kanal "Mindwave", OAuth eingerichtet, täglicher Auto-Lauf (launchd, 19:00, 2 Videos)
- **Instagram live & vollautomatisch:** Creator-Konto + FB-Seite + Meta-App, Posting über neue Instagram-API (graph.instagram.com), Video-Hosting via catbox.moe — erfolgreich getestet
- TikTok-App eingereicht, wartet auf Review-Freigabe
- Dateien: `video_builder.py`, `script_generator.py`, `run.py`, `poster_youtube.py`, `poster_instagram.py`, `daily_run.sh`

### Jarvis Content Bot implementiert

- Alle 8 Bot-Dateien erstellt unter `scripts/jarvis/`
- Skript-Generator (Claude API), Stimme (ElevenLabs), Stock-Video (Pexels), Video-Builder (MoviePy)
- Poster für YouTube, Instagram und TikTok
- Haupt-Orchestrator `run.py` mit `--dry-run`, `--once`, `--count` Flags
- Dry-run erfolgreich: alle Module importieren, Ablauf startet sauber
- CLAUDE.md und .env aktualisiert mit neuen Keys und Jarvis-Struktur
- Nächster Schritt: Anthropic-Guthaben aufladen, dann erster echter Lauf

## YYYY-MM-DD

### Erstes Setup

- CEO-GPT mit Kontext und Absicherung initialisiert
- Git aufgesetzt und mit GitHub verbunden
- Doku-System angelegt (docs/ Ordner mit Routing-Index)
- /commit Befehl installiert für strukturierte Commits mit automatischer Doku
