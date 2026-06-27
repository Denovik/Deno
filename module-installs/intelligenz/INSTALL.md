# INSTALL: Intelligenz-Modul

> Diese Datei ist für deinen Mitarbeiter (Claude) geschrieben.

---

## FÜR CLAUDE — Verhaltensregeln

- Erkläre jeden Schritt in normalem Deutsch, bevor du ihn ausführst
- Pausiere nach jedem Meilenstein
- Kein Fachjargon, keine rohen Fehlermeldungen
- Passe dich an den aktuellen Stand des CEO-GPT an

---

## Was diese Fähigkeit einrichtet

Ein wöchentliches Analyse-Skript, das:
1. Die letzten YouTube-Videos mit ihren Statistiken abruft (Views, Likes, Kommentare)
2. Die letzten Instagram-Reels mit ihrer Performance abruft
3. Diese Daten mit Claude analysiert: Was funktioniert? Was nicht? Warum?
4. Einen knappen Bericht in `outputs/berichte/` speichert
5. Die wichtigsten Erkenntnisse in `context/current-data.md` ergänzt

Das Ergebnis: Jarvis weiß beim nächsten `/prime`, was auf deinen Kanälen wirklich läuft — und kann gezielte Empfehlungen geben.

---

## Schritt 1: Voraussetzungen prüfen

- Ist `scripts/daten/fetch_stats.py` vorhanden? (Daten-Modul)
- Ist `credentials/youtube_daten_token.pickle` vorhanden? (YouTube-Lese-Zugang)
- Ist `META_ACCESS_TOKEN` in `.env` gesetzt?
- Ist `ANTHROPIC_API_KEY` in `.env` gesetzt?

Falls Daten-Modul fehlt: Erst `/install module-installs/daten` ausführen.

---

## Schritt 2: Performance-Abruf für YouTube

Erweitere `scripts/daten/fetch_stats.py` NICHT — lege stattdessen ein separates Skript an:
`scripts/intelligenz/analyse.py`

YouTube-Teil:
- Letzte 10 Videos des Kanals abrufen (Titel, Views, Likes, Kommentare, Veröffentlichungsdatum)
- Nutze den bestehenden `youtube_daten_token.pickle` mit `youtube.readonly`-Scope

---

## Schritt 3: Performance-Abruf für Instagram

Instagram-Teil in demselben Skript:
- Letzte 10 Reels abrufen (Caption/Titel, like_count, comments_count, timestamp)
- Nutze `META_ACCESS_TOKEN` und `INSTAGRAM_ACCOUNT_ID` aus `.env`
- Endpoint: `/{ig-user-id}/media?fields=id,caption,like_count,comments_count,timestamp,media_type`

---

## Schritt 4: Claude-Analyse

Die gesammelten Daten werden an Claude (claude-sonnet-4-6) geschickt mit dem Auftrag:
- Welche Videos/Reels performen am besten? (Muster erkennen: Thema, Sprache, Titel-Stil)
- Was läuft unterdurchschnittlich?
- 3 konkrete Empfehlungen für die nächste Woche

---

## Schritt 5: Bericht speichern

- Bericht als Markdown nach `outputs/berichte/YYYY-MM-DD-analyse.md`
- Kurzzusammenfassung (3-5 Zeilen) in `context/current-data.md` unter neuem Abschnitt "## Letzte Analyse"

---

## Schritt 6: Wöchentlichen Lauf einrichten

launchd-Job `com.jarvis.intelligenz.plist`: jeden Montag um 09:00 Uhr.

---

## Schritt 7: Jarvis-Aktion ergänzen

In `scripts/jarvis/jarvis_actions.py` eine neue Aktion `analyse_starten` hinzufügen,
damit Dennis Jarvis sagen kann: "Jarvis, analysiere meine Videos" — und er es wirklich ausführt.

---

## Erfolgskriterium

1. `python3 scripts/intelligenz/analyse.py` läuft ohne Fehler
2. Ein Bericht erscheint in `outputs/berichte/`
3. `context/current-data.md` hat einen "Letzte Analyse"-Abschnitt
4. Jarvis kann auf Zuruf analysieren
