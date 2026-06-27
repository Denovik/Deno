# Plan: Jarvis Voice-Interface (mit Jarvis sprechen)

**Erstellt:** 2026-06-27
**Status:** Umgesetzt
**Anfrage:** Mit Jarvis sprechen können — Jarvis hört zu, denkt nach und antwortet mit seiner Stimme (Iron-Man-Gefühl)

---

## Überblick

### Was dieser Plan erreicht

Ein Sprach-Assistent: Dennis spricht ins Mikrofon, Jarvis wandelt die Sprache in Text um, denkt mit Claude darüber nach (kennt Dennis' Business-Kontext) und antwortet laut mit der ElevenLabs-Jarvis-Stimme. Start über einen einfachen Befehl im Terminal.

### Warum das zählt

Jarvis wird vom reinen Content-Bot zum echten Assistenten, den Dennis ansprechen kann — für Fragen, Ideen, Status-Abfragen zum Business. Das ist das emotionale Herzstück des "CEO-GPT als bester Mitarbeiter"-Gedankens.

---

## Aktueller Stand

### Bestehende relevante Struktur

- `scripts/jarvis/` — Content-Bot mit `voice_generator.py` (nutzt bereits ElevenLabs)
- `.env` — ANTHROPIC_API_KEY ✅, ELEVENLABS_API_KEY ✅, ELEVENLABS_VOICE_ID_DE=ej62nTkjlGLiric3Xofh ✅
- `context/` — Business-/Personen-/Strategie-Infos über Dennis
- `afplay` (macOS) zum Abspielen vorhanden

### Lücken

- Keine Mikrofon-Aufnahme (sounddevice fehlt)
- Keine Sprache-zu-Text (faster-whisper fehlt)
- OpenAI-Whisper-Cloud nicht nutzbar (keine Abrechnung im OpenAI-Konto)

---

## Geplante Änderungen

### Zusammenfassung

- Neue Abhängigkeiten installieren: `sounddevice`, `faster-whisper`
- Neues Skript `scripts/jarvis/voice_chat.py` — der Sprach-Assistent
- Jarvis-Persona als System-Prompt, lädt `context/`-Dateien für Hintergrundwissen
- Start per `python3 scripts/jarvis/voice_chat.py`

### Neue Dateien

| Pfad | Zweck |
|---|---|
| `scripts/jarvis/voice_chat.py` | Aufnahme → Transkription → Claude → ElevenLabs → Wiedergabe, in einer Schleife |

### Geänderte Dateien

| Pfad | Änderungen |
|---|---|
| `requirements.txt` (falls vorhanden) | sounddevice, faster-whisper ergänzen |
| `CLAUDE.md` | Voice-Befehl in die Befehlsübersicht aufnehmen |

---

## Design-Entscheidungen

1. **Sprache-zu-Text lokal mit faster-whisper**: kostenlos, offline, kein API-Konto nötig. Modell "small" (guter Kompromiss Genauigkeit/Tempo, ~150 MB, einmaliger Download). Braucht kein ffmpeg-Binary.
2. **Push-to-Talk im Terminal (v1)**: Enter drücken → reden → Enter drücken → Jarvis antwortet. Einfachste robuste Bedienung. (Später möglich: Aktivierungswort "Hey Jarvis".)
3. **Claude als Gehirn**: Modell claude-sonnet-4-6, mit Jarvis-Persona + geladenem Business-Kontext. Hält Gesprächsverlauf in der Sitzung.
4. **Stimme**: ElevenLabs, deutsche Jarvis-Stimme (ej62nTkjlGLiric3Xofh), Wiedergabe per afplay.
5. **Sprache**: Deutsch als Standard.

### Verworfene Alternativen

- OpenAI Whisper API (keine Abrechnung)
- macOS-Bordmittel-Diktat (schwer skriptbar, unzuverlässig)

### Offene Fragen

- Aktivierungswort statt Push-to-Talk? → später, v1 erst Enter-Taste
- Soll Jarvis Aktionen ausführen (z.B. Video posten auf Zuruf)? → später, v1 nur Gespräch

---

## Schritt-für-Schritt-Aufgaben

### 1. Abhängigkeiten installieren
- `pip install sounddevice faster-whisper` im venv
- Kurzer Test, dass beide importierbar sind

### 2. voice_chat.py schreiben
- Mikrofon-Aufnahme (sounddevice, WAV im Scratch/Temp)
- Transkription (faster-whisper, Modell "small", Sprache de)
- Claude-Anfrage mit Jarvis-System-Prompt + context/-Inhalten + Gesprächsverlauf
- ElevenLabs-Sprachausgabe (vorhandene Logik aus voice_generator.py wiederverwenden)
- Wiedergabe per afplay
- Schleife: Push-to-Talk, "Tschüss"/Strg+C beendet

### 3. Testen
- Einmal sprechen, prüfen ob Transkription stimmt, Jarvis sinnvoll + mit Stimme antwortet

### 4. CLAUDE.md aktualisieren
- Voice-Interface in die Übersicht aufnehmen

---

## Prüf-Checkliste

- [ ] sounddevice + faster-whisper installiert und importierbar
- [ ] Mikrofon-Aufnahme funktioniert (nimmt hörbar auf)
- [ ] Transkription erkennt gesprochenes Deutsch korrekt
- [ ] Claude antwortet im Jarvis-Ton, kennt Dennis' Kontext
- [ ] Antwort wird mit Jarvis-Stimme abgespielt
- [ ] Gespräch über mehrere Runden möglich
- [ ] CLAUDE.md aktualisiert

## Erfolgskriterien

1. Dennis startet ein Skript, spricht, und Jarvis antwortet hörbar mit seiner Stimme
2. Jarvis bezieht Business-Kontext in seine Antworten ein
3. Mehrere Gesprächsrunden ohne Neustart möglich

## Notizen

Erstes lauffähiges Voice-Interface (v1). Später: Aktivierungswort, Aktionen auf Zuruf (Video posten, Status abfragen), durchgehendes Zuhören.

---

## Umsetzungs-Notizen

**Umgesetzt:** 2026-06-27

### Zusammenfassung

`scripts/jarvis/voice_chat.py` gebaut: Push-to-Talk im Terminal → lokale Spracherkennung (faster-whisper, Modell "small") → Claude (Jarvis-Persona + Business-Kontext aus `context/`) → ElevenLabs-Stimme (DE) → Wiedergabe per afplay. Gesprächsverlauf bleibt in der Sitzung erhalten. `sounddevice` + `faster-whisper` installiert und in requirements.txt ergänzt.

### Abweichungen vom Plan

Keine.

### Aufgetretene Probleme

Keine. Vollständiger Test der Kette (Kontext → Stimme erzeugen → Spracherkennung → Claude) erfolgreich; Spracherkennung erkannte einen deutschen Testsatz wortgenau. Nur das Live-Mikrofon ist noch vom Nutzer zu testen.
