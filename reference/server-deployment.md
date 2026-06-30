# Server-Deployment — Jarvis-Pipeline

> Die Jarvis-Content-Pipeline läuft produktiv auf dem Hetzner-Server (167.233.95.3). Der Mac muss dafür nicht an sein.

---

## Server-Zugang

```bash
ssh -i ~/.ssh/mindwave_hetzner root@167.233.95.3
```

SSH-Schlüssel liegt lokal unter `~/.ssh/mindwave_hetzner`.

## Server-Pfade

| Was | Pfad auf dem Server |
|---|---|
| Projekt-Root | `/opt/mindwave/jarvis` |
| Pipeline-Skripte | `/opt/mindwave/jarvis/scripts/jarvis/` |
| Daten-Skripte | `/opt/mindwave/jarvis/scripts/daten/` |
| Analyse-Skripte | `/opt/mindwave/jarvis/scripts/intelligenz/` |
| Musik | `/opt/mindwave/jarvis/music/` |
| Zugangsdaten | `/opt/mindwave/jarvis/credentials/` |
| API-Keys | `/opt/mindwave/jarvis/.env` |
| Datenbank | `/opt/mindwave/jarvis/data/data.db` |
| Logs (Cron) | `/opt/mindwave/jarvis/outputs/logs/` |

## Automatische Zeitpläne (Cron)

Server-Zeitzone: `Europe/Berlin` (CEST, +0200)

| Zeit | Was | Log |
|---|---|---|
| täglich 19:00 | Videos produzieren + posten | `outputs/logs/cron-daily.log` |
| täglich 08:00 | YouTube/Instagram-Daten sammeln | `outputs/logs/cron-daten.log` |
| montags 09:00 | Wöchentliche Performance-Analyse | `outputs/logs/cron-intelligenz.log` |

## Logs live ansehen

```bash
ssh -i ~/.ssh/mindwave_hetzner root@167.233.95.3
tail -f /opt/mindwave/jarvis/outputs/logs/cron-daily.log
```

## Manuellen Lauf starten

```bash
ssh -i ~/.ssh/mindwave_hetzner root@167.233.95.3
cd /opt/mindwave/jarvis
source venv/bin/activate
python3 scripts/jarvis/run.py --once --count 1
```

## Code-Update auf den Server übertragen

Lokal im Projekt-Ordner:

```bash
cd /Users/dennisgluck/Desktop/CLAUDE/ceogpt-start
bash scripts/jarvis/deploy_to_server.sh
```

Danach Ausführungsrechte erneuern:

```bash
ssh -i ~/.ssh/mindwave_hetzner root@167.233.95.3 "chmod +x /opt/mindwave/jarvis/scripts/jarvis/server_run.sh /opt/mindwave/jarvis/scripts/daten/server_collect.sh /opt/mindwave/jarvis/scripts/intelligenz/server_analyse.sh"
```

## Zurück auf lokalen Mac (Notfall-Fallback)

```bash
launchctl load ~/Library/LaunchAgents/com.jarvis.daily.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.daten.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.intelligenz.plist
```

Deaktivieren wieder:

```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.daily.plist
launchctl unload ~/Library/LaunchAgents/com.jarvis.daten.plist
launchctl unload ~/Library/LaunchAgents/com.jarvis.intelligenz.plist
```

## Datenbank lokal spiegeln

```bash
scp -i ~/.ssh/mindwave_hetzner root@167.233.95.3:/opt/mindwave/jarvis/data/data.db data/data.db
```
