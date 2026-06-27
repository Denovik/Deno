# INSTALL: Daten-Modul

> Diese Datei ist für deinen Mitarbeiter (Claude) geschrieben. Sie führt durch das geführte Setup.

---

## FÜR CLAUDE — Verhaltensregeln für diese Installation

- Erkläre jeden Schritt in normalem Deutsch, bevor du ihn ausführst
- Pausiere nach jedem Meilenstein und warte auf Bestätigung
- Kein Fachjargon, keine rohen Fehlermeldungen
- Feiere Fortschritte: jeder Schritt ist Bandbreite zurück
- Passe dich an den aktuellen Stand des CEO-GPT an (nicht stur dem Plan folgen wenn schon etwas existiert)

---

## Was diese Fähigkeit einrichtet

Ein tägliches Datenabruf-Skript, das echte Zahlen von YouTube und Instagram holt und automatisch in `context/current-data.md` schreibt. Damit hat dein Mitarbeiter beim Start jeder Sitzung den echten aktuellen Stand — ohne dass du Zahlen von Hand einträgst.

**Was danach automatisch läuft:**
- YouTube: Abonnenten, Views, Watch-Time der letzten 7 Tage
- Instagram: Follower, Reichweite, Post-Performance
- Alles landet täglich in `context/current-data.md`

---

## Schritt 1: Voraussetzungen prüfen

Prüfe:
- Existiert `credentials/youtube_token.pickle`? (YouTube-Zugang)
- Ist `META_ACCESS_TOKEN` in `.env` gesetzt? (Instagram-Zugang)
- Ist `scripts/jarvis/config.py` vorhanden? (Basis-Konfiguration)

Wenn YouTube-Token fehlt: Hinweis geben, dass zuerst YouTube-OAuth einzurichten ist (läuft normalerweise schon).
Wenn Meta-Token fehlt: Hinweis geben, dass Instagram-Setup zuerst nötig ist.

---

## Schritt 2: Daten-Skript anlegen

Lege `scripts/daten/fetch_stats.py` an. Das Skript:

1. Holt YouTube-Kanal-Statistiken (Abonnenten, Gesamt-Views) über die YouTube Data API v3
2. Holt Instagram-Konto-Statistiken (Follower) über die Instagram Graph API
3. Liest die aktuelle `context/current-data.md`
4. Ersetzt die Zahlen in der Kennzahlen-Tabelle
5. Schreibt den Zeitstempel des letzten Abrufs

Verwende die bestehenden Credentials aus `credentials/` und `.env` — keine neuen Keys nötig.

---

## Schritt 3: Täglichen Abruf einrichten

Füge einen zweiten launchd-Job hinzu (ähnlich wie `com.jarvis.daily`), der `fetch_stats.py` täglich um 08:00 Uhr ausführt — damit die Zahlen zu Tagesbeginn aktuell sind.

Plist-Datei: `~/Library/LaunchAgents/com.jarvis.daten.plist`

---

## Schritt 4: Ersten Abruf manuell testen

Führe `python3 scripts/daten/fetch_stats.py` einmal aus und zeige dem Geschäftsführer, was in `context/current-data.md` steht.

---

## Schritt 5: CLAUDE.md aktualisieren

Trage das neue Skript in die Ordner-Übersicht in CLAUDE.md ein.

---

## Erfolgskriterium

Die Installation ist abgeschlossen, wenn:
1. `scripts/daten/fetch_stats.py` läuft ohne Fehler
2. Echte YouTube- und Instagram-Zahlen in `context/current-data.md` stehen
3. Der tägliche Abruf-Job geladen ist (`launchctl list | grep jarvis.daten`)
