# Intelligenz

> Dein Mitarbeiter hört bei allem mit und vergisst nichts. Jedes Meeting, jede Nachricht, durchsuchbar.

| Feld | Wert |
|---|---|
| Modul | `intelligenz` |
| Version | v1 |
| Status | RELEASED |
| Released | 2026-02-26 |
| Voraussetzung | Kontext und Daten |
| Setup-Zeit | 20 bis 30 Minuten |
| Laufende Kosten | kostenlos (kostenlose Tarife der Recorder reichen) |

## Was hier passiert

- **Meeting-Mitschriften** werden automatisch aus deinem Recorder gezogen (Fireflies, Fathom oder eigener Recorder) und landen in einer durchsuchbaren Datenbank.
- **Slack-Nachrichten** werden täglich eingesammelt, Kanal für Kanal, Person für Person, durchsuchbar nach Stichwort und Datum.
- **Tagestranskript** auf Knopfdruck. "Was lief am Slack letzten Dienstag?"
- **Automatische Einordnung** nach Abteilung, falls du Teams hast. Vertrieb, Operations, was auch immer du fährst.
- **Direkte Suche.** "Find das Meeting mit Jimmy letzte Woche." "Hat jemand das Rebrand in Slack erwähnt?"
- **Automatischer Lauf** nach Zeitplan. Einmal eingerichtet, läuft es weiter.

## Realität in DACH

Wenn dein Team mit Slack arbeitet, super, das hier ist gebaut dafür. Viele Teams im DACH-Raum laufen aber über Teams, Email-Threads oder sogar WhatsApp. Sag das beim Setup. Den Slack-Teil können wir weglassen, Teams oder eigene Verbindungen lassen sich später nachrüsten. Den Recorder-Teil (Fireflies, Fathom) nimmst du trotzdem mit, der zieht aus Zoom, Google Meet und Teams.

## Was du brauchst

- Einen Computer (Mac oder Linux)
- Claude Code installiert
- Kontext und Daten schon eingerichtet
- Einen Recorder-Zugang: [Fireflies](https://fireflies.ai) oder [Fathom](https://fathom.ai), beide haben kostenlose Tarife
- Optional einen Slack-Workspace

## Installation

1. Der `intelligenz` Ordner liegt schon in `module-installs/`
2. Führe `/install module-installs/intelligenz` aus
3. Dein Mitarbeiter führt dich durch den Setup-Workshop

**Geschätzte Setup-Zeit:** 20 bis 30 Minuten

## Kosten

Kostenlos in der Basis. Fireflies und Fathom haben kostenlose Tarife, die Slack API ist gratis. Die Datenbank liegt lokal bei dir, etwa ein MB pro hundert Meetings.

## Was hier drin liegt

| Datei | Zweck |
|---|---|
| `INSTALL.md` | Geführter Setup-Workshop (liest dein Mitarbeiter) |
| `README.md` | Diese Datei, der Überblick für dich |
| `scripts/db.py` | Datenbank und Such-Hilfen |
| `scripts/collect_fireflies.py` | Fireflies-Anbindung |
| `scripts/collect_fathom.py` | Fathom-Anbindung |
| `scripts/collect_slack.py` | Slack-Anbindung |
| `scripts/classify.py` | Meeting-Einordnung nach Abteilung |
| `scripts/collect_all.py` | Sammler-Orchestrator |
| `scripts/requirements.txt` | Python-Abhängigkeiten |
| `config/com.ceogpt.intelligenz-collect.plist` | macOS-Zeitplan-Vorlage |

## Was du danach kannst

- "Zeig mir die letzten fünf Meetings."
- "Find das Meeting mit Anna vom Dienstag."
- "Was wurde in Slack diese Woche zum Thema Preis besprochen?"
- "Gib mir das Slack-Tagestranskript vom 25. Februar."

Wenn du Abteilungen eingerichtet hast, kannst du auch filtern. "Zeig mir alle Vertriebs-Calls der letzten zwei Wochen."

## Pro-Tipp

Lad den Recorder direkt in deine Kalender-Einladungen ein. Fireflies und Fathom dockern sich an Zoom, Google Meet und Teams an. Jedes aufgezeichnete Gespräch wandert automatisch in deine Datenbank, ohne dass du dran denkst.

## Nach diesem Modul

Dein Mitarbeiter hört bei allen deinen Meetings und Chats mit. Er vergisst nichts. Im nächsten Schritt bekommt er eine Stimme mit `/install module-installs/stimme`.
