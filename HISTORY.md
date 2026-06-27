# CEO-GPT Historie

> Zeitliches Logbuch aller Arbeiten in diesem CEO-GPT. Wird jede Session aktualisiert.
> Neueste Einträge oben. Jeder Eintrag hat Datum, Titel und Bullet Points.
>
> **So läuft's:** Wenn du `/commit` nach einer sinnvollen Arbeit ausführst, trägt dein
> Mitarbeiter hier automatisch ein. Du musst diese Datei nicht selbst schreiben.

---

## 2026-06-27

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
