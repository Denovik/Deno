# Plan: Jarvis-Pipeline vom Mac auf den Hetzner-Server umziehen

**Erstellt:** 2026-06-30
**Status:** Umgesetzt
**Anfrage:** Die komplette Jarvis-Content-Pipeline soll vom lokalen Mac auf den bestehenden Hetzner-Server (167.233.95.3) umziehen, damit automatisches Posten nicht mehr davon abhängt, dass Dennis' Mac an und online ist.

---

## Überblick

### Was dieser Plan erreicht

Nach Umsetzung läuft die gesamte Jarvis-Pipeline (Skript-Generierung, Sprachsynthese, Videobau, Posten auf YouTube/Instagram/TikTok, Daten-Sammlung, wöchentliche Analyse) eigenständig auf dem Hetzner-Server statt auf Dennis' Mac. Der Server war bisher nur Host der Landingpage (mindwaveofficial.com); er wird jetzt zusätzlich zum Produktions-Standort der Content-Pipeline. Die lokale Mac-Pipeline bleibt vorerst als Fallback bestehen, wird aber deaktiviert, sobald der Server-Betrieb bestätigt läuft.

### Warum das zählt

Aktuell scheitert die Pipeline lokal an einer macOS-Berechtigungssperre (Hintergrund-Prozesse dürfen nicht auf den Schreibtisch-Ordner zugreifen) — das hat bereits die Daten-Sammlung (08:00) und den Video-Post (19:00) lahmgelegt. Ein Server-Betrieb löst dieses Problem nicht nur, sondern macht das System grundsätzlich robuster: kein Risiko mehr durch Schlafmodus, Neustarts, Stromausfall oder geschlossenen Laptop-Deckel auf dem Mac. Das ist eine Voraussetzung für "vollautomatisiert" im eigentlichen Sinn — das Nordstern-Ziel (2.000 €/Monat bis Ende 2026) braucht eine Pipeline, die ohne Dennis' Zutun zuverlässig läuft.

---

## Aktueller Stand

### Bestehende relevante Struktur

- `scripts/jarvis/` — komplette Pipeline: `run.py` (Orchestrator), `script_generator.py`, `voice_generator.py`, `pexels_client.py`, `video_builder.py`, `poster_youtube.py`, `poster_instagram.py`, `poster_tiktok.py`, `performance_tracker.py`, `trends_client.py`, `config.py`, `requirements.txt`
- `scripts/jarvis/daily_run.sh` — Shell-Wrapper, aktiviert lokales `venv`, ruft `run.py --once --count 2` auf, schreibt Log nach `outputs/logs/daily-*.log`
- `scripts/daten/` — separate Pipeline für YouTube/Instagram-Kennzahlen-Sammlung (`collect.py`), schreibt in `data/data.db` und generiert `context/group/key-metrics.md`
- `scripts/intelligenz/analyse.py` — wöchentliche Performance-Analyse, schreibt nach `outputs/berichte/`
- `~/Library/LaunchAgents/com.jarvis.daily.plist` (19:00 täglich), `com.jarvis.daten.plist` (08:00 täglich), `com.jarvis.intelligenz.plist` (montags 09:00) — macOS launchd, rein lokal, kein Server-Äquivalent vorhanden
- `.env` (Projekt-Root, gitignored) — alle API-Keys: `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `PEXELS_API_KEY`, `META_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`, `TIKTOK_CLIENT_KEY`/`TIKTOK_CLIENT_SECRET`/`TIKTOK_ACCESS_TOKEN`/`TIKTOK_OPEN_ID`, `YOUTUBE_CLIENT_SECRET_PATH`, plus weitere für andere Module
- `credentials/` (gitignored) — `youtube_client_secret.json`, `youtube_token.pickle`, `youtube_daten_token.pickle` (OAuth-Tokens, an dieses Mac-Setup gebunden — YouTube-OAuth-Flow lief lokal im Browser)
- `venv/` (Projekt-Root, gitignored) — lokales Python-3.9-venv mit allen Paketen aus `requirements.txt`
- `outputs/` — generierte Videos, Skripte, Logs, Berichte; bisher komplett lokal auf dem Mac
- Server 167.233.95.3 — Hetzner Cloud, aktuell nur Nginx + `/var/www/mindwave` (Landingpage). Kein SSH-Schlüssel für diese Sitzung hinterlegt — Server-seitige Befehle müssen von Dennis selbst im Terminal ausgeführt werden, mit Anleitung

### Lücken oder Probleme, die der Plan löst

- macOS blockiert `launchd`-Hintergrundzugriff auf den im Schreibtisch-Ordner liegenden Projektordner → Daten-Sammlung und Video-Post schlagen fehl (bestätigter `PermissionError` aus den Logs)
- Pipeline ist an Mac-Verfügbarkeit gekoppelt (an, wach, online) — kein robuster Produktionsbetrieb
- Kein bestehender Mechanismus, um Secrets (`.env`, `credentials/`) sicher auf einen Server zu übertragen — beide sind absichtlich gitignored, dürfen nicht über Git transportiert werden
- YouTube-OAuth-Tokens sind an den lokalen Browser-Flow gebunden — müssen geprüft werden, ob sie auf dem Server ohne erneuten interaktiven Login funktionieren (Refresh-Token-basiert, sollte funktionieren, aber zu verifizieren)
- Kein Server-seitiges Äquivalent zu `launchd` eingerichtet (Cron oder systemd-Timer fehlt komplett)

---

## Geplante Änderungen

### Zusammenfassung der Änderungen

- Python 3.11+, ffmpeg und Build-Abhängigkeiten auf dem Server installieren, eigenes venv unter `/opt/mindwave/jarvis` anlegen
- Projekt-Code (nur `scripts/jarvis/`, `scripts/daten/`, `scripts/intelligenz/`, `context/`, `data/`, `outputs/`-Grundstruktur, keine `venv/`, kein `.git`) per `rsync` über SSH auf den Server kopieren
- `.env` und `credentials/` ausschließlich per `scp`/`rsync` über die bestehende SSH-Verbindung übertragen — niemals über Git, niemals im Klartext irgendwo zwischengespeichert
- YouTube-OAuth-Tokens vor dem Umzug einmal lokal frisch validieren (Refresh-Token-Gültigkeit prüfen), dann mit übertragen
- Neue Wrapper-Skripte `scripts/jarvis/server_run.sh`, `scripts/daten/server_collect.sh`, `scripts/intelligenz/server_analyse.sh` analog zu `daily_run.sh`, aber für Server-Pfade
- Cron-Einträge auf dem Server als Ersatz für die drei `launchd`-Pläne, mit identischen Zeiten (19:00, 08:00, montags 09:00)
- Test-Lauf auf dem Server mit `--dry-run`, dann ein echter Einzel-Lauf (`--once --count 1`) vor produktivem Cron-Schalten
- Lokale `launchd`-Agents werden erst deaktiviert (`launchctl unload`), nachdem der Server-Betrieb mindestens einen vollen Produktiv-Zyklus bestätigt erfolgreich durchlaufen hat
- `CLAUDE.md` und `reference/` um einen Hinweis ergänzen, dass die Pipeline jetzt auf dem Server läuft, inkl. wie man sie von dort aus prüft/neu startet
- Neue Referenz-Datei `reference/server-deployment.md` mit Server-Zugang, Pfaden, Cron-Übersicht, Neustart-/Debug-Befehlen

### Neue Dateien

| Pfad | Zweck |
|---|---|
| `scripts/jarvis/server_run.sh` | Server-Wrapper für die tägliche Video-Produktion (ersetzt `daily_run.sh` auf dem Server) |
| `scripts/daten/server_collect.sh` | Server-Wrapper für die tägliche Daten-Sammlung |
| `scripts/intelligenz/server_analyse.sh` | Server-Wrapper für die wöchentliche Analyse |
| `reference/server-deployment.md` | Server-Pfade, Cron-Übersicht, SSH-Zugang, Debug-/Neustart-Befehle |
| `scripts/jarvis/deploy_to_server.sh` | Lokales Hilfsskript: rsync von Code + sicherem `.env`/`credentials`-Transfer auf den Server (für künftige Updates) |

### Geänderte Dateien

| Pfad | Änderungen |
|---|---|
| `CLAUDE.md` | Abschnitt zu `scripts/jarvis/` ergänzen: Hinweis dass Produktion jetzt auf dem Server läuft, lokaler Start nur noch für Tests gedacht |
| `reference/data-access.md` | Hinweis ergänzen, dass die Datenbank jetzt primär auf dem Server gepflegt wird und für lokale Analyse zurückgespiegelt werden kann |

### Gelöschte Dateien (falls vorhanden)

Keine — lokale `launchd`-Konfigurationen werden deaktiviert (`launchctl unload`), nicht gelöscht, als Fallback-Option falls der Server-Betrieb Probleme macht.

---

## Design-Entscheidungen

### Wichtige Entscheidungen

1. **Cron statt systemd-Timer**: Der Server hat bereits eine einfache Single-Service-Rolle (Nginx). Cron ist für drei feste Tageszeiten ausreichend, einfacher zu debuggen für einen nicht-technischen Geschäftsführer, und braucht keine Unit-Dateien. systemd-Timer wäre Overkill für diesen Anwendungsfall.
2. **Eigenes venv unter `/opt/mindwave/jarvis` statt im Home-Verzeichnis**: Folgt Server-Konvention, sauber getrennt von der Landingpage unter `/var/www/mindwave`, vermeidet Rechte-Konflikte mit dem Web-Server-Prozess.
3. **Secrets ausschließlich per direktem SSH-Transfer, nie über Git**: `.env` und `credentials/` sind bewusst gitignored. Diese Regel bleibt für den Server-Umzug bestehen — sie wandern direkt vom Mac auf den Server über eine verschlüsselte SSH-Verbindung, nie als Datei im Repo oder in einem Zwischenspeicher.
4. **Lokale launchd-Agents bleiben als Fallback bestehen, nur deaktiviert**: Bei einem ersten Server-Umzug können unvorhergesehene Probleme auftreten (z.B. Server-Ressourcen-Limits bei der Videoverarbeitung). Komplettes Löschen der lokalen Automatisierung vor bestätigtem Server-Erfolg wäre ein unnötiges Risiko für die Kontinuität des Postings.
5. **Schrittweiser Umstieg mit explizitem Bestätigungs-Punkt vor dem produktiven Cron-Schalten**: Erst Dry-Run, dann ein einzelner echter Lauf, erst danach der volle Zeitplan — verhindert, dass ein Konfigurationsfehler sofort mehrfach täglich auf allen drei Plattformen postet.

### Verworfene Alternativen

- **Docker-Container auf dem Server**: Würde sauberere Isolation bringen, aber deutlich mehr Komplexität (Image bauen, Volumes für Outputs, Container-Neustarts) für einen Solo-Betrieb mit aktuell sehr überschaubarer Last. Verworfen zugunsten von direktem venv-Betrieb, kann später nachgezogen werden, falls die Pipeline wächst.
- **Managed Cloud Functions/Serverless statt eigenem Server**: Würde Kaltstart-Probleme bei moviepy/ffmpeg-lastigen Video-Renderings verursachen und die Kostenkontrolle erschweren. Der bereits laufende, bezahlte Hetzner-Server ist die pragmatischere und kosteneffizientere Wahl (passt zum "möglichst kosteneffizient"-Grundsatz aus `context/business-info.md`).
- **GitHub Actions als Cron-Ersatz**: Würde Secrets in GitHub Actions Secrets verlegen statt auf dem eigenen Server, und Video-Rendering ist für CI-Runner ressourcenintensiv/zeitlich begrenzt (Job-Timeouts). Verworfen zugunsten von direktem Server-Cron.

### Offene Fragen

1. **Reicht die Server-Hardware für moviepy-Videoverarbeitung?** Muss vor dem produktiven Schalten mit einem echten Test-Lauf geprüft werden (Schritt 7). Falls der Server zu schwach ist (RAM/CPU), braucht es ein Hetzner-Upgrade — das ist ein Folge-Schritt, kein Blocker für diesen Plan, aber im Test-Schritt zu beobachten.
2. **Funktionieren die YouTube-OAuth-Refresh-Tokens ohne erneuten interaktiven Login auf dem Server?** Google-OAuth-Refresh-Tokens sind in der Regel langlebig und nicht an eine IP/Maschine gebunden, aber das muss im Test-Lauf (Schritt 7) verifiziert werden — falls nicht, braucht es einen erneuten lokalen OAuth-Flow mit Übertragung des neuen Tokens.

---

## Schritt-für-Schritt-Aufgaben

In dieser Reihenfolge ausführen. Schritte, die auf dem Server laufen, sind als Anleitung für Dennis formuliert (kein SSH-Zugriff in dieser Sitzung) — der Mitarbeiter gibt die exakten Befehle vor, Dennis führt sie im eigenen Terminal aus und meldet das Ergebnis zurück.

### 1. YouTube-OAuth-Tokens lokal validieren

Vor dem Umzug sicherstellen, dass die vorhandenen Tokens gültig und übertragbar sind.

**Aktionen:**
- Lokal prüfen: `python3 -c "import pickle; t = pickle.load(open('credentials/youtube_token.pickle','rb')); print(t.valid, t.expired, bool(t.refresh_token))"` für beide Token-Dateien
- Falls `refresh_token` vorhanden und nicht leer: Token ist server-tauglich (Google erneuert automatisch)
- Falls kein Refresh-Token: vor dem Umzug einmal lokal `poster_youtube.py`-Login-Flow neu durchlaufen lassen, damit ein gültiger Refresh-Token vorliegt

**Betroffene Dateien:**
- `credentials/youtube_token.pickle`
- `credentials/youtube_daten_token.pickle`

---

### 2. Server-Grundausstattung installieren

Python, ffmpeg und Build-Werkzeuge auf dem Hetzner-Server bereitstellen.

**Aktionen:**
- Anleitung an Dennis für SSH-Sitzung auf dem Server geben:
  ```
  ssh root@167.233.95.3
  apt update && apt install -y python3.11 python3.11-venv python3-pip ffmpeg git
  mkdir -p /opt/mindwave/jarvis
  ```
- Python-Version und ffmpeg-Installation bestätigen lassen (`python3.11 --version`, `ffmpeg -version`)

**Betroffene Dateien:**
- Keine lokalen Dateien — reine Server-Einrichtung

---

### 3. Projekt-Code auf den Server übertragen

Nur die für die Pipeline nötigen Ordner kopieren, kein `venv/`, kein `.git`.

**Aktionen:**
- Lokales Hilfsskript `scripts/jarvis/deploy_to_server.sh` erstellen (siehe Inhalt unten), das `rsync` mit Ausschlussliste nutzt
- Inhalt von `deploy_to_server.sh`:
  ```bash
  #!/bin/bash
  # Synct Jarvis-Pipeline-Code auf den Hetzner-Server. Secrets NICHT enthalten — siehe Schritt 4 im Plan.
  SERVER="root@167.233.95.3"
  REMOTE_DIR="/opt/mindwave/jarvis"
  LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

  rsync -avz --progress \
    --exclude 'venv/' \
    --exclude '.git/' \
    --exclude '.env' \
    --exclude 'credentials/' \
    --exclude 'outputs/videos/*.mp4' \
    --exclude '__pycache__/' \
    "$LOCAL_DIR/scripts/jarvis/" "$SERVER:$REMOTE_DIR/scripts/jarvis/"
  rsync -avz --progress "$LOCAL_DIR/scripts/daten/" "$SERVER:$REMOTE_DIR/scripts/daten/"
  rsync -avz --progress "$LOCAL_DIR/scripts/intelligenz/" "$SERVER:$REMOTE_DIR/scripts/intelligenz/"
  rsync -avz --progress "$LOCAL_DIR/context/" "$SERVER:$REMOTE_DIR/context/"
  rsync -avz --progress "$LOCAL_DIR/data/data.db" "$SERVER:$REMOTE_DIR/data/data.db" 2>/dev/null || echo "data.db noch nicht vorhanden, wird beim ersten Lauf erzeugt"

  echo "Code-Sync fertig. Secrets separat per scp übertragen (siehe Schritt 4 im Server-Umzugs-Plan)."
  ```
- Dennis führt das Skript lokal aus: `bash scripts/jarvis/deploy_to_server.sh`

**Betroffene Dateien:**
- `scripts/jarvis/deploy_to_server.sh` (neu)

---

### 4. Secrets sicher übertragen

`.env` und `credentials/` getrennt vom Code-Sync, direkt per `scp`.

**Aktionen:**
- Anleitung an Dennis, lokal auszuführen:
  ```bash
  scp .env root@167.233.95.3:/opt/mindwave/jarvis/.env
  scp -r credentials/ root@167.233.95.3:/opt/mindwave/jarvis/credentials/
  ```
- Nach Übertragung auf dem Server Berechtigungen einschränken (Anleitung für Dennis):
  ```bash
  ssh root@167.233.95.3
  chmod 600 /opt/mindwave/jarvis/.env
  chmod -R 600 /opt/mindwave/jarvis/credentials/*
  ```

**Betroffene Dateien:**
- Keine lokalen Dateien — reine Übertragung

---

### 5. Server-venv einrichten

**Aktionen:**
- Anleitung an Dennis für SSH-Sitzung:
  ```bash
  ssh root@167.233.95.3
  cd /opt/mindwave/jarvis
  python3.11 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r scripts/jarvis/requirements.txt
  ```
- Bestätigen lassen, dass die Installation ohne Fehler durchläuft (moviepy/ffmpeg-Bindings sind erfahrungsgemäß die wahrscheinlichste Fehlerquelle)

**Betroffene Dateien:**
- Keine lokalen Dateien — reine Server-Einrichtung

---

### 6. Server-Wrapper-Skripte erstellen

Analog zu `daily_run.sh`, aber mit Server-Pfaden statt Mac-Pfaden.

**Aktionen:**
- `scripts/jarvis/server_run.sh` lokal erstellen, Inhalt analog zu `daily_run.sh`, aber:
  - `PROJECT_DIR="/opt/mindwave/jarvis"`
  - venv-Aktivierung über `$PROJECT_DIR/venv/bin/activate`
  - Log-Ziel bleibt `$PROJECT_DIR/outputs/logs/`
- `scripts/daten/server_collect.sh` analog für `scripts/daten/collect.py`
- `scripts/intelligenz/server_analyse.sh` analog für `scripts/intelligenz/analyse.py`
- Alle drei Skripte per `deploy_to_server.sh`-Lauf (Schritt 3 erneut ausführen) auf den Server mitübertragen
- Auf dem Server ausführbar machen: `chmod +x /opt/mindwave/jarvis/scripts/jarvis/server_run.sh` (und die anderen beiden)

**Betroffene Dateien:**
- `scripts/jarvis/server_run.sh` (neu)
- `scripts/daten/server_collect.sh` (neu)
- `scripts/intelligenz/server_analyse.sh` (neu)

---

### 7. Test-Lauf auf dem Server

Vor produktivem Schalten bestätigen, dass alles funktioniert.

**Aktionen:**
- Anleitung an Dennis für SSH-Sitzung:
  ```bash
  ssh root@167.233.95.3
  cd /opt/mindwave/jarvis
  source venv/bin/activate
  python3 scripts/jarvis/run.py --dry-run --once --count 1
  ```
- Dry-Run-Ergebnis prüfen (Skript-Generierung sollte ohne Fehler durchlaufen)
- Danach ein echter Einzel-Lauf, NICHT als Dry-Run:
  ```bash
  python3 scripts/jarvis/run.py --once --count 1
  ```
- Prüfen: Video wurde erzeugt, auf mindestens einer Plattform erfolgreich gepostet (YouTube-Upload bestätigt OAuth-Funktion ohne erneuten interaktiven Login)
- Falls der Server bei der Videoverarbeitung sehr langsam ist oder abbricht (RAM/CPU-Limit): als offenes Problem festhalten, ggf. Hetzner-Plan-Upgrade als Folge-Schritt empfehlen, nicht in diesem Plan lösen
- `scripts/daten/server_collect.sh` einmal manuell testen
- `scripts/intelligenz/server_analyse.sh` einmal manuell testen (kann mit vorhandenen Daten laufen, auch außerhalb von Montag)

**Betroffene Dateien:**
- Keine — Verifikation

---

### 8. Server-Cron einrichten

Erst nachdem Schritt 7 erfolgreich war.

**Aktionen:**
- Anleitung an Dennis, auf dem Server `crontab -e` zu öffnen und folgende Zeilen einzutragen:
  ```cron
  0 19 * * * /opt/mindwave/jarvis/scripts/jarvis/server_run.sh >> /opt/mindwave/jarvis/outputs/logs/cron-daily.log 2>&1
  0 8 * * * /opt/mindwave/jarvis/scripts/daten/server_collect.sh >> /opt/mindwave/jarvis/outputs/logs/cron-daten.log 2>&1
  0 9 * * 1 /opt/mindwave/jarvis/scripts/intelligenz/server_analyse.sh >> /opt/mindwave/jarvis/outputs/logs/cron-intelligenz.log 2>&1
  ```
- Bestätigen lassen mit `crontab -l`, dass die Einträge korrekt gespeichert sind
- Server-Zeitzone prüfen (`timedatectl`), damit 19:00/08:00/09:00 wirklich der deutschen Zeit entsprechen — bei Abweichung Cron-Zeiten entsprechend anpassen oder Server-Zeitzone auf `Europe/Berlin` setzen

**Betroffene Dateien:**
- Keine lokalen Dateien — reine Server-Konfiguration

---

### 9. Lokale launchd-Agents deaktivieren (nicht löschen)

Erst nach mindestens einem vollständig erfolgreichen Server-Produktivzyklus (also nach dem ersten automatischen 19:00-Lauf über Cron).

**Aktionen:**
- Lokal ausführen:
  ```bash
  launchctl unload ~/Library/LaunchAgents/com.jarvis.daily.plist
  launchctl unload ~/Library/LaunchAgents/com.jarvis.daten.plist
  launchctl unload ~/Library/LaunchAgents/com.jarvis.intelligenz.plist
  ```
- Plist-Dateien selbst NICHT löschen — bleiben als Fallback, falls der Server-Betrieb später Probleme macht und kurzfristig auf lokal zurückgewechselt werden muss
- Dennis explizit informieren, dass dieser Schritt erst nach bestätigtem Server-Erfolg gemacht wird, nicht automatisch in dieser Umsetzung

**Betroffene Dateien:**
- Keine — `launchctl`-Befehle, keine Dateiänderung

---

### 10. Doku aktualisieren

**Aktionen:**
- `reference/server-deployment.md` neu anlegen: SSH-Zugang (`ssh root@167.233.95.3`), Server-Pfad (`/opt/mindwave/jarvis`), Cron-Übersicht (Zeiten + Befehle), wie man Logs einsieht (`tail -f /opt/mindwave/jarvis/outputs/logs/cron-daily.log`), wie man einen manuellen Lauf auf dem Server startet, wie man bei Problemen zurück auf lokal wechselt (`launchctl load` der drei Plists)
- `CLAUDE.md` in der Tabelle bei `scripts/jarvis/` und `scripts/daten/` ergänzen: Hinweis "Läuft produktiv auf dem Server (167.233.95.3), siehe `reference/server-deployment.md`. Lokaler Start nur noch für Tests."
- `reference/data-access.md` Hinweis ergänzen: `data/data.db` wird jetzt primär auf dem Server gepflegt; für lokale Analyse per `scp root@167.233.95.3:/opt/mindwave/jarvis/data/data.db data/data.db` zurückspiegeln

**Betroffene Dateien:**
- `reference/server-deployment.md` (neu)
- `CLAUDE.md`
- `reference/data-access.md`

---

## Verbindungen und Abhängigkeiten

### Dateien, die auf diesen Bereich verweisen

- `CLAUDE.md` referenziert `scripts/jarvis/` und `scripts/daten/` in der Ordner-Tabelle — wird in Schritt 10 aktualisiert
- `reference/data-access.md` referenziert `data/data.db` — wird in Schritt 10 aktualisiert
- `personal-os/profil.md` und `context/business-info.md` referenzieren das Business als "vollautomatisiert" — dieser Plan macht das erstmals technisch wahr

### Updates für Konsistenz

- `HISTORY.md`: nach Umsetzung Eintrag "Jarvis-Pipeline auf Server umgezogen" ergänzen
- `docs/_index.md`: neuer Eintrag für `reference/server-deployment.md` als Anlaufstelle bei Server-Betriebsfragen

### Auswirkung auf bestehende Abläufe

- `/prime` liest weiterhin `context/group/key-metrics.md` — dieser Stand kommt künftig vom Server statt vom lokalen `collect.py`-Lauf; Genauigkeit bleibt gleich, nur die Quelle der Ausführung ändert sich
- Lokales manuelles Starten der Pipeline (`python3 scripts/jarvis/run.py --once`) bleibt weiterhin möglich für Tests, postet aber dann live — genau wie bisher, keine Verhaltensänderung
- A/B-Tests und Performance-Tracking (`performance_tracker.py`) laufen unverändert weiter, jetzt nur auf dem Server statt lokal

---

## Prüf-Checkliste

- [ ] YouTube-Refresh-Tokens vor dem Umzug als gültig bestätigt
- [ ] Python 3.11, ffmpeg, venv erfolgreich auf dem Server installiert
- [ ] Code per `deploy_to_server.sh` ohne Fehler übertragen
- [ ] `.env` und `credentials/` sicher übertragen, Rechte auf 600 gesetzt
- [ ] Server-venv mit allen `requirements.txt`-Paketen installiert
- [ ] Dry-Run auf dem Server erfolgreich
- [ ] Echter Einzel-Lauf auf dem Server erfolgreich (Video erzeugt + mindestens ein Plattform-Post bestätigt)
- [ ] Cron-Einträge korrekt gesetzt, Server-Zeitzone passt zu Europe/Berlin
- [ ] Mindestens ein automatischer 19:00-Produktivlauf über Cron erfolgreich bestätigt, bevor lokale launchd-Agents deaktiviert werden
- [ ] `reference/server-deployment.md` vollständig und korrekt
- [ ] `CLAUDE.md` und `reference/data-access.md` spiegeln den neuen Server-Betrieb

---

## Erfolgskriterien

Die Umsetzung ist fertig, wenn:

1. Die Jarvis-Pipeline läuft eigenständig auf dem Hetzner-Server nach Zeitplan (19:00 täglich), ohne dass Dennis' Mac dafür an oder online sein muss
2. Ein vollständiger automatischer Produktivzyklus (Skript → Video → Post auf mindestens YouTube) über Server-Cron bestätigt erfolgreich war
3. Dennis anhand von `reference/server-deployment.md` selbstständig den Server-Status prüfen und bei Bedarf einen manuellen Lauf starten kann

---

## Notizen

- Dieser Plan deckt den **Umzug** ab, nicht die TikTok-Freigabe oder Trade-Republic-Integration — die laufen unabhängig weiter und sind in `context/strategy.md` als offene Punkte festgehalten.
- Sollte sich der Server als zu schwach für die Videoverarbeitung herausstellen (siehe Offene Frage 1), ist ein Hetzner-Plan-Upgrade ein separater, kleiner Folge-Schritt — kein Grund, diesen Plan zu blockieren.
- Ein künftiges Docker-basiertes Setup (siehe verworfene Alternative) kann nachgezogen werden, falls die Pipeline wächst (mehr Nischen, mehr Sprachen, höhere Frequenz) und Isolation/Skalierung wichtiger wird als jetzt.
- `deploy_to_server.sh` ist bewusst wiederverwendbar angelegt — künftige Code-Änderungen an der Pipeline werden über dasselbe Skript erneut auf den Server gespielt, statt jedes Mal manuell zu kopieren.
