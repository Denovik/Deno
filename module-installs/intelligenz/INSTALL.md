# Intelligenz: Installation

<!-- MODUL-METADATEN
modul: intelligenz
version: v1
status: RELEASED
released: 2026-02-26
requires: [kontext, daten]
phase: 2
category: Kern-Module
complexity: medium
api_keys: 1-3
setup_time: 20-30 Minuten
-->

---

## FÜR CLAUDE (Anleitung für dich, das Programm)

Du hilfst dem Member, die **Intelligenz** seines Mitarbeiters aufzubauen. Das ist der dritte Schritt im Gehirn deines Mitarbeiters, nach Kontext und Daten. Dein Mitarbeiter hört ab jetzt bei Meetings und Team-Chats mit und vergisst nichts.

**Deine Rolle:** Du bist Setup-Begleiter und Werkstattmeister. Du fragst sauber durch, was der Member nutzt, baust die Verbindungen, testest sie und übergibst.

**Verhalten:**
- Geh davon aus, dass der Member nicht technisch ist, außer er sagt was anderes
- Erklär in einfacher Sprache, was du gerade tust, bevor du es tust
- Feier kleine Wins ("Erstes Meeting gezogen, dein Mitarbeiter hat ab jetzt ein Gedächtnis für deine Calls.")
- Wenn was schiefläuft, schmeiß keine Fehler-Logs raus, erklär das Problem in einem Satz und schlag die Lösung vor
- Sprich aufmunternd, der Member baut hier etwas Echtes
- Niemals "schau in die Logs", finde das Problem und sag es ihm

**Pacing:**
- Nicht durchrasen. Nach Meilensteinen kurz halten.
- Nach dem Workshop: "Gut. Ich weiß jetzt, womit du arbeitest. Wir bauen die Verbindungen jetzt."
- Nach API-Keys: "Alle Keys geprüft. Der trockene Teil ist durch, jetzt der schöne."
- Nach Installation: "Steht. Wir testen."
- Nach Test: "Es läuft. Dein Mitarbeiter hört ab jetzt bei allem mit. Schau, was du jetzt fragen kannst."

**Custom-Recorder-Pfad:**
Wenn der Member weder Fireflies noch Fathom nutzt, hilfst du ihm beim Bauen einer eigenen Anbindung. So:
1. Frag, welchen Recorder er nutzt
2. Such im Web nach der API-Doku dieser Plattform
3. Sei ehrlich. "Ja, die haben eine offene API, ich kann das bauen." Oder: "Die API ist nur in Enterprise-Tarifen freigegeben, lieber Fireflies oder Fathom nehmen."
4. Wenn machbar, schreib ein `collect_custom.py` im selben Format wie die Fireflies- und Fathom-Varianten (Liste von Meeting-Dicts mit meeting_id, source, title, date, start_time, duration_minutes, participants, transcript_text, summary, action_items_raw, external_url)
5. Die Datei braucht eine `collect(days=7)`-Funktion, die diese Liste zurückgibt

---

## ÜBERSICHT (lies das dem Member vor dem Start vor)

Jetzt bauen wir den letzten Bereich vom Gehirn, nämlich Intelligenz. Das ist der dritte Schritt im Gehirn, nach Kontext (wer du bist) und Daten (deine Zahlen). Jetzt geht's um Ohren und Erinnerung. Dein Mitarbeiter hört bei jedem Meeting mit und liest jede Team-Nachricht, und beides bleibt für immer durchsuchbar.

Wenn wir fertig sind, hast du:

- **Meeting-Mitschriften** automatisch gezogen, aus Fireflies, Fathom oder deinem eigenen Recorder
- **Slack-Nachrichten** täglich gesammelt, durchsuchbar nach Kanal, Person, Stichwort, Datum
- **Tagestranskript** auf Abruf ("Was lief auf Slack letzten Dienstag?")
- **Auto-Einordnung** nach Abteilung, falls du Teams hast, sodass Vertriebs-Calls als Vertrieb getaggt werden
- **Direkte Suche.** "Find das Meeting mit Jimmy letzte Woche." "Hat jemand das Rebrand in Slack erwähnt?"
- **Automatischer Lauf** nach Zeitplan. Einmal eingerichtet, läuft weiter.

**Setup-Zeit:** 20 bis 30 Minuten
**Laufende Kosten:** kostenlos, wenn du die freien Tarife von Fireflies oder Fathom nutzt. Die Slack API ist gratis. Hier laufen keine KI-Kosten, das ist reines Sammeln und Speichern.
**Voraussetzung:** Kontext und Daten sollten schon installiert sein. Wir brauchen das Team-Register für die Einordnung.

---

## WORKSHOP

Bevor wir bauen, klären wir, womit du arbeitest. Frag den Member diese Sachen ab.

### Frage 1: Recorder

"Womit nimmst du deine Meetings auf? Das Tool, das in deinen Zoom-, Meet- oder Teams-Call reingeht und das Transkript baut."

**Optionen:**
- **A) Fireflies.ai.** Fertige Anbindung da. Leichtester Weg.
- **B) Fathom.** Auch eine fertige Anbindung. Genauso leicht.
- **C) Was anderes.** Ich schau mir die Plattform an und baue dir eine eigene Anbindung oder sag dir, was sich lohnt.
- **D) Ich nehme noch nicht auf.** Kein Problem. Schau dir [Fireflies](https://fireflies.ai) (freier Tarif, unbegrenzt Meetings) oder [Fathom](https://fathom.ai) (großzügiger freier Tarif, super für Zoom) an. Richte einen ein, lass zwei oder drei Meetings aufnehmen, dann komm zurück.

Notier: `RECORDER = fireflies | fathom | custom | keiner`

Bei C: frag nach der Plattform, such die API-Doku, prüf ehrlich, ob es geht. Wenn ja, sag dem Member, dass du beim Installieren die Anbindung baust. Wenn nein, sei direkt. "Die Plattform hat keine offene API für Transkripte. Ich empfehle Fireflies oder Fathom, beide haben freie Tarife und arbeiten mit Zoom, Google Meet und Teams."

Bei D: Meetings überspringen wir erstmal, weiter mit Slack.

### Frage 2: Team-Chat

"Nutzt du Slack im Team? Oder andere Tools wie Teams, eigene Chats, oder primär E-Mail?"

**Optionen:**
- **A) Slack.** Top, wir richten den Slack-Sammler ein. Du baust dazu eine kleine Slack-App, ich führe dich Schritt für Schritt durch, dauert fünf Minuten.
- **B) Teams oder Email.** Den Slack-Teil lassen wir weg. Du kriegst trotzdem die Meeting-Mitschriften. Eine Teams-Anbindung lässt sich später nachrüsten, wenn du sie brauchst.
- **C) Eh kein Team-Chat.** Kein Stress, Slack-Teil aus, Meetings reichen.

Notier: `SLACK_AKTIV = true | false`

Wenn ja: "Wie viele Slack-Workspaces willst du anbinden? Die meisten haben einen, manche einen extra für Kunden oder Partner."

Notier: `SLACK_WORKSPACES = 1 | 2 | ...`

### Frage 3: Abteilungs-Tagging (optional)

"Hast du verschiedene Abteilungen oder Teams in deinem Business? Zum Beispiel Vertrieb, Produkt, Operations, Support?"

- **A) Ja, ich hab Abteilungen.** "Sag mir welche, dann richte ich die Einordnung ein, sodass deine Meetings automatisch getaggt werden."
- **B) Nein, nur ich oder ein kleines Team.** "Lassen wir simpel, alle Meetings landen in einem Topf. Du kannst das später nachziehen."

Notier: `ABTEILUNGEN = [liste] | keine`

### Frage 4: Wie oft sammeln

"Wie oft soll dein Mitarbeiter neue Meetings und Nachrichten einsammeln?"

- **A) Täglich** (empfohlen, einfach, zuverlässig, wenig API-Last)
- **B) Alle vier Stunden** (näher an Echtzeit, gut, wenn Meetings schneller verfügbar sein sollen)
- **C) Jede Stunde** (am reaktivsten, kostet mehr API-Calls)

Notier: `SAMMEL_INTERVALL = täglich | 4h | 1h`

**Vorher schauen, ob schon ein Zeitplan läuft:**

```bash
# macOS
launchctl list | grep -i "ceogpt\|collect\|cron"
# Linux
crontab -l
```

Wenn aus den Daten schon ein Sammel-Job läuft, sag dem Member: "Du hast schon einen Sammel-Job laufen. Wir hängen die Intelligenz an den bestehenden Zeitplan ran, statt einen zweiten zu bauen."

Nach dem Workshop kurz zurückspielen: "Stand. Recorder {recorder}, Slack {an/aus}, Abteilungen {ja/nein}, Sammlung {intervall}. Passt das?"

---

## VORAUSSETZUNGEN

Jede Voraussetzung prüfen, bevor du weitermachst.

### Python 3.10 oder höher
```bash
python3 --version
```
Wenn zu alt oder nicht da, OS-spezifische Install-Schritte geben.

### pip
```bash
python3 -m pip --version
```
Wenn nicht da:
```bash
python3 -m ensurepip --upgrade
```

### CEO-GPT steht
```bash
ls CLAUDE.md
```
Wenn keine CLAUDE.md da ist: "Du hast Kontext noch nicht eingerichtet. Das muss zuerst, das baut die Basis, in die Intelligenz reinhakt."

### Team-Register aus Daten
Prüf, ob aus den Daten schon eine Datenbank existiert:
```bash
python3 -c "
import sqlite3, glob, os
dbs = glob.glob('data/*.db')
if dbs:
    for db in dbs:
        conn = sqlite3.connect(db)
        tables = [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
        print(f'{db}: {tables}')
        conn.close()
else:
    print('Keine Datenbank gefunden, Intelligenz legt data/intel.db neu an')
"
```

**Wenn eine Daten-Datenbank existiert** (irgendeine `.db` in `data/` mit `staff_registry`): Intelligenz nutzt die. Notier den Pfad.

**Wenn keine da ist:** Intelligenz baut eine eigene unter `data/intel.db`. Das Team-Register bleibt leer, alle Meetings landen erstmal in "allgemein", bis du Team-Mitglieder einträgst.

Notier: `DB_PATH = {Pfad zur bestehenden DB} | data/intel.db`

[VERIFY] Alle Voraussetzungen geben Versionen aus, keine Fehler.

"Alles steht. Weiter?"

---

## API-KEYS

Nur die Keys einsammeln, die der Member laut Workshop braucht.

### Fireflies API Key [falls RECORDER = fireflies]

1. Geh auf [app.fireflies.ai/integrations](https://app.fireflies.ai/integrations)
2. Scroll runter zum Bereich "Fireflies API" (oder such nach "API")
3. Klick auf "API & Webhooks" oder ähnlich
4. Kopier deinen API Key (lange Zeichenkette)
5. Häng ihn hier rein, ich leg ihn sicher in deine .env

[VERIFY]
```bash
python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('FIREFLIES_API_KEY')
if not key: print('FEHLER: Key nicht in .env'); exit(1)
r = requests.post('https://api.fireflies.ai/graphql',
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
    json={'query': '{ transcripts(limit: 1) { id title } }'},
    timeout=15)
data = r.json()
if 'errors' in data: print(f'FEHLER: {data[\"errors\"][0][\"message\"]}')
else: print(f'Fireflies verbunden, {len(data.get(\"data\",{}).get(\"transcripts\",[]))} aktuelle Mitschrift(en) gefunden')
"
```
Erwartet: "Fireflies verbunden, X aktuelle Mitschrift(en) gefunden"
Bei "invalid token": "Der Key zieht nicht. Geh nochmal auf app.fireflies.ai/integrations und kopier den vollständigen Key. Wenn der alte abgelaufen ist, gibt's da einen Regenerate-Button."

### Fathom API Key [falls RECORDER = fathom]

1. Geh auf [app.fathom.ai](https://app.fathom.ai) und log dich ein
2. Klick auf dein Profil-Icon, dann **Settings**
3. Klick auf **Integrations** in der Seitenleiste
4. Find den **API**-Bereich
5. Klick **Generate API Key** (oder kopier den bestehenden)
6. Häng ihn hier rein

[VERIFY]
```bash
python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('FATHOM_API_KEY')
if not key: print('FEHLER: Key nicht in .env'); exit(1)
r = requests.get('https://api.fathom.ai/external/v1/meetings',
    headers={'X-Api-Key': key},
    params={'include_summary': 'true'},
    timeout=15)
if r.status_code == 401: print('FEHLER: Key ungültig, prüf Settings → Integrations → API in Fathom')
elif r.status_code == 200: print(f'Fathom verbunden, Key bestätigt')
else: print(f'Unerwartete Antwort: HTTP {r.status_code}')
"
```
Erwartet: "Fathom verbunden, Key bestätigt"

### Slack Bot Token [falls SLACK_AKTIV = true]

Etwa fünf Minuten. Wir bauen eine kleine Slack-App, die Nachrichten lesen darf.

1. Geh auf [api.slack.com/apps](https://api.slack.com/apps)
2. Klick **Create New App**
3. Wähl **From scratch**
4. Nenn sie wie du willst, zum Beispiel "CEO-GPT Intelligenz"
5. Wähl dein CEO-GPT aus der Liste
6. Klick **Create App**

Jetzt die Rechte:

7. Links in der Seitenleiste **OAuth & Permissions** anklicken
8. Runterscrollen zu **Scopes** → **Bot Token Scopes**
9. Diese Scopes hinzufügen (jeweils "Add an OAuth Scope" klicken):
   - `channels:history` Nachrichten in öffentlichen Kanälen lesen
   - `channels:read` Kanal-Liste sehen
   - `channels:join` öffentlichen Kanälen beitreten, um sie zu lesen
   - `users:read` User-IDs in Namen auflösen
10. Scroll wieder hoch, klick **Install to CEO-GPT**
11. Klick **Allow** auf dem Berechtigungs-Screen
12. Kopier das **Bot User OAuth Token** (startet mit `xoxb-`)
13. Häng es hier rein

[VERIFY]
```bash
python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('SLACK_TOKEN_MAIN')
if not token: print('FEHLER: Token nicht in .env'); exit(1)
r = requests.get('https://slack.com/api/auth.test',
    headers={'Authorization': f'Bearer {token}'}, timeout=15)
data = r.json()
if data.get('ok'): print(f'Slack verbunden, CEO-GPT: {data.get(\"team\", \"unbekannt\")}')
else: print(f'FEHLER: {data.get(\"error\", \"unbekannt\")}, prüf, dass du das Bot User OAuth Token (xoxb-) kopiert hast')
"
```
Erwartet: "Slack verbunden, CEO-GPT: DeinWorkspace"

**Wichtiger Hinweis zu Slack-Kanälen:** "Dein Bot liest nur Kanäle, in die er eingeladen wurde. Nach dem Setup gehst du in jeden Kanal, den du sammeln willst, und tippst `/invite @CEO-GPT Intelligenz` (oder wie du deine App genannt hast). Fang mit den zentralen Kanälen an, mehr kannst du jederzeit nachladen."

Bei mehreren Arbeitsplätzen brauchst du pro CEO-GPT eine eigene Slack-App. Die Tokens kommen dann als `SLACK_TOKEN_MAIN`, `SLACK_TOKEN_CLIENTS` und so weiter rein.

Wenn alle Keys da sind: "Keys geprüft. Der trockene Teil ist durch, jetzt der schöne."

---

## INSTALLATION

### Abhängigkeiten

```bash
pip install requests python-dotenv
```

[VERIFY]
```bash
python3 -c "import requests; from dotenv import load_dotenv; print('Abhängigkeiten OK')"
```

### .env

Schreib die .env mit den eingesammelten Keys ins CEO-GPT-Root (gleicher Ordner wie CLAUDE.md).

Nur die Keys reinpacken, die wirklich da sind:
```
# Intelligenz API Keys
FIREFLIES_API_KEY=...    (nur bei Fireflies)
FATHOM_API_KEY=...       (nur bei Fathom)
SLACK_TOKEN_MAIN=...     (nur bei Slack)
SLACK_TOKEN_CLIENTS=...  (nur bei mehreren Workspaces)
```

**Wenn schon eine .env existiert:** Keys anhängen, nichts überschreiben.

[VERIFY]
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); keys = [k for k in os.environ if k.startswith(('FIREFLIES_', 'FATHOM_', 'SLACK_TOKEN_'))]; print(f'Config OK: {len(keys)} Intelligenz-Keys geladen')"
```

### Skript-Ordner anlegen

Leg `scripts/intel/` an (oder wo es im CEO-GPT passt). Kopier alle Intelligenz-Skripte da rein:

**Diese Dateien anlegen:**
- `scripts/intel/db.py` Datenbank und Such-Hilfen
- `scripts/intel/collect_fireflies.py` Fireflies-Anbindung (falls aktiv)
- `scripts/intel/collect_fathom.py` Fathom-Anbindung (falls aktiv)
- `scripts/intel/collect_slack.py` Slack-Anbindung (falls aktiv)
- `scripts/intel/classify.py` Meeting-Einordnung
- `scripts/intel/collect_all.py` Sammler-Orchestrator

Schreib jede Datei aus den Inhalten in `scripts/` von diesem Modul. **Import-Pfade anpassen**, falls die CEO-GPT-Struktur abweicht. Die Skripte importieren sich gegenseitig relativ aus dem gleichen Ordner.

**Pfad-Hinweis:** `db.py` setzt `WORKSPACE_ROOT = Path(__file__).resolve().parent.parent`. Das geht davon aus, dass die Skripte zwei Ebenen tief liegen (`scripts/intel/db.py` zeigt aufs CEO-GPT-Root). Bei abweichender Struktur den Pfad so anpassen, dass `DB_PATH` auf `{workspace_root}/data/intel.db` zeigt.

**Wenn schon eine Datenbank aus den Daten existiert:** `db.py` so anpassen, dass `DB_PATH` auf die bestehende zeigt. Die Intelligenz-Tabellen (meetings, slack_messages, staff_registry, collection_log) dazu anlegen, falls sie noch nicht da sind.

[VERIFY] Nach dem Anlegen aller Dateien:
```bash
python3 scripts/intel/db.py
```
Erwartet: "Datenbank initialisiert unter: data/intel.db" (oder dem bestehenden Pfad), Tabellen-Liste.

### Team-Register füllen (nur bei Abteilungen)

Wenn der Member im Workshop Abteilungen genannt hat, jetzt das Team-Register füllen.

Frag: "Lass uns dein Team eintragen. Pro Person brauch ich Name, Email, Rolle und Abteilung. Du kannst tippen oder eine Liste reinpasten."

Dann ab in die Datenbank:
```python
import sys; sys.path.insert(0, 'scripts/intel')
from db import get_connection, write_staff

conn = get_connection()
staff = [
    {"email": "person@firma.de", "name": "Person Name", "role": "Rolle", "team": "firma", "department": "vertrieb"},
    # ... mehr Team-Mitglieder
]
count = write_staff(conn, staff)
print(f"{count} Team-Mitglieder eingetragen")
conn.close()
```

Wenn keine Abteilungen, Schritt überspringen. Alles landet im "allgemein"-Topf.

### Eigener Recorder (nur bei RECORDER = custom)

Falls der Member einen eigenen Recorder hat:

1. API-Doku der Plattform im Web suchen
2. Prüfen, ob es Endpunkte gibt für:
   - Aufzeichnungen listen oder suchen (Pflicht)
   - Transkript-Text holen (Pflicht)
   - Teilnehmer-Infos (nice to have)
3. Wenn die API passt, `scripts/intel/collect_custom.py` nach diesem Muster bauen:

```python
"""Eigene Anbindung für {Plattform-Name}."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

def collect(days: int = 7) -> list[dict]:
    """Sammelt Meetings der letzten N Tage.
    Gibt Liste von Meeting-Dicts zurück mit:
    - meeting_id (str, eindeutig)
    - source (str, z.B. "otter")
    - title (str)
    - date (str, JJJJ-MM-TT)
    - start_time (str, HH:MM:SS, optional)
    - duration_minutes (int, optional)
    - participants (str, JSON-Array von {name, email})
    - transcript_text (str, volle Mitschrift)
    - summary (str, optional)
    - action_items_raw (str, JSON, optional)
    - external_url (str, optional)
    """
    # HIER DEINE LOGIK
    pass
```

4. `collect_all.py` so anpassen, dass es aus `collect_custom` importiert statt aus `collect_fireflies` oder `collect_fathom`.

Wenn die API nicht reicht, sei ehrlich und empfiehl Fireflies oder Fathom.

---

## TEST

### Schnell-Test: Datenbank

```bash
python3 scripts/intel/db.py
```
Erwartet: Pfad und Tabellen-Liste.

### Test: Meeting-Sammlung

```bash
python3 scripts/intel/collect_all.py --meetings-only
```
Erwartet: "Fireflies: X Meetings gesammelt" (oder Fathom-Äquivalent) und "X Datensätze in Datenbank geschrieben".

Wenn null Meetings: "Normal, wenn du gerade erst den Recorder eingerichtet hast. Heißt nur, die Verbindung steht, aber in den letzten sieben Tagen gab's keine Aufzeichnungen. Probier `--days 30`, um weiter zurückzuschauen, oder warte aufs nächste Meeting."

### Test: Slack-Sammlung (falls aktiv)

```bash
python3 scripts/intel/collect_all.py --slack-only
```
Erwartet: "Sammle Slack-Workspace: main..." und "X Nachrichten in Datenbank geschrieben".

Wenn null Nachrichten: "Dein Slack-Bot ist noch in keinem Kanal. Geh in deinen aktivsten Kanal und tipp `/invite @DeinBot`, dann nochmal laufen lassen."

### Voller Test: Daten abfragen

Nach erfolgreicher Sammlung dem Member zeigen, was er machen kann:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts/intel')
from db import get_connection, get_meeting_stats

conn = get_connection()
stats = get_meeting_stats(conn)
print('=== Deine Intelligenz-Datenbank ===')
print(f'  Meetings: {stats[\"total_meetings\"]}')
print(f'  Slack-Nachrichten: {stats[\"total_slack_messages\"]}')
print(f'  Team-Mitglieder: {stats[\"team_members\"]}')
if stats['latest_meeting_date']:
    print(f'  Letztes Meeting: {stats[\"latest_meeting_date\"]}')
conn.close()
"
```

Beispiel-Suche:
```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts/intel')
from db import get_connection

conn = get_connection()
results = conn.execute('SELECT title, date, duration_minutes FROM meetings ORDER BY date DESC LIMIT 5').fetchall()
if results:
    print('Letzte Meetings:')
    for r in results:
        print(f'  {r[1]}: {r[0]} ({r[2] or \"?\"} min)')
else:
    print('Noch keine Meetings, kommen rein, sobald dein Recorder welche aufnimmt.')
conn.close()
"
```

Wenn alles greift, sag mit Pause und Wärme:
> *"Dein Mitarbeiter hört bei allen deinen Meetings und Chats mit. Er vergisst nichts."*

Sammlung läuft im Hintergrund weiter. Fragen, die du jetzt stellen kannst: "Find das Meeting mit [Name] letzte Woche" oder "Such in Slack nach [Thema]".

---

## ZEITPLAN

Damit neue Meetings und Nachrichten automatisch reinfließen, ohne dass du dran denkst.

### Erst schauen, ob schon ein Plan läuft

```bash
# macOS
ls ~/Library/LaunchAgents/ | grep -i "ceogpt\|collect"
# Linux
crontab -l 2>/dev/null
```

**Wenn aus den Daten schon ein Sammler läuft:** Intelligenz an den bestehenden Orchestrator anhängen statt einen zweiten Plan zu bauen. In das bestehende `collect_all.py` (oder Äquivalent) diese Zeilen rein:
```python
# Intelligenz-Sammlung
from scripts.intel.collect_all import run as intel_run
intel_run()
```

**Wenn kein Plan da ist, neu aufsetzen:**

### macOS (launchd)

Die Plist-Vorlage liegt unter `config/com.ceogpt.intelligenz-collect.plist`. Pfade ersetzen:

1. Vorlage kopieren:
```bash
cp config/com.ceogpt.intelligenz-collect.plist ~/Library/LaunchAgents/com.ceogpt.intelligenz-collect.plist
```

2. Plist bearbeiten, Platzhalter ersetzen:
   - `__VENV_PYTHON__` Pfad zu Python (z.B. `/Users/name/workspace/.venv/bin/python` oder `python3`)
   - `__SCRIPTS_DIR__` absoluter Pfad zu `scripts/intel/`
   - `__WORKSPACE_ROOT__` absoluter Pfad zum CEO-GPT-Root
   - `__INTERVAL__` Sekunden zwischen Läufen:
     - Täglich: `86400`
     - Alle vier Stunden: `14400`
     - Jede Stunde: `3600`

3. Laden:
```bash
launchctl load ~/Library/LaunchAgents/com.ceogpt.intelligenz-collect.plist
```

4. Prüfen:
```bash
launchctl list | grep ceogpt.intelligenz
```

### Linux (cron)

```bash
crontab -e
```

Eine dieser Zeilen ergänzen (Pfad anpassen):
```
# Täglich um 6 Uhr
0 6 * * * cd /pfad/zum/workspace && python3 scripts/intel/collect_all.py >> data/intel-collect.log 2>&1

# Alle vier Stunden
0 */4 * * * cd /pfad/zum/workspace && python3 scripts/intel/collect_all.py >> data/intel-collect.log 2>&1

# Jede Stunde
0 * * * * cd /pfad/zum/workspace && python3 scripts/intel/collect_all.py >> data/intel-collect.log 2>&1
```

**Wichtig bei Laptops:** Der Rechner muss zur geplanten Zeit wach sein. Bei macOS unter Systemeinstellungen → Energie "Festplatten in Ruhezustand versetzen" deaktivieren und "Automatischen Ruhezustand verhindern, wenn das Display aus ist" aktivieren.

---

## WAS DU JETZT MACHEN KANNST

Frag deinen Mitarbeiter direkt:

**Meeting-Suche:**
- "Find das Meeting, das ich letzte Woche mit [Name] hatte"
- "Was wurde im Team-Meeting am Dienstag besprochen?"
- "Such in meinen Meetings nach allem, was mit Website-Relaunch zu tun hat"

**Slack-Suche:**
- "Hat diese Woche jemand [Thema] in Slack erwähnt?"
- "Was lief gestern in #allgemein?"
- "Gib mir eine Zusammenfassung der Slack-Aktivität vom letzten Freitag"

**Schnell-Abfragen (laufen im Hintergrund):**
```sql
-- Meetings mit einer bestimmten Person
SELECT title, date, summary FROM meetings
WHERE participants LIKE '%anna%' ORDER BY date DESC LIMIT 5;

-- Meeting-Transkripte durchsuchen
SELECT title, date, substr(transcript_text, 1, 200) FROM meetings
WHERE transcript_text LIKE '%budget%' ORDER BY date DESC;

-- Alle Slack-Nachrichten aus einem Kanal an einem Datum
SELECT user_name, text FROM slack_messages
WHERE channel_name = 'allgemein'
AND DATE(datetime(CAST(ts AS REAL), 'unixepoch')) = '2026-02-25'
ORDER BY ts;

-- Slack-Tagestranskript über alle Kanäle
SELECT channel_name, user_name, text FROM slack_messages
WHERE DATE(datetime(CAST(ts AS REAL), 'unixepoch')) = '2026-02-25'
ORDER BY ts;

-- Meeting-Statistik nach Stream
SELECT stream, COUNT(*) as anzahl FROM meetings
WHERE stream IS NOT NULL GROUP BY stream;
```

**`/tagestranskript`:** Wenn du den Befehl einrichtest (in `.claude/commands/tagestranskript.md`), spuckt dein Mitarbeiter dir auf Zuruf alle Meetings und Chats des Tages als sauberes Transkript zurück. Lass dir das als nächsten Schritt einrichten, wenn du das brauchst.

**Beispiel-Fragen, mit denen du jeden Morgen starten kannst:**

- "Was war gestern im Team das Wichtigste, was ich verpasst habe?"
- "Welche Entscheidung hat sich diese Woche durch mehrere Meetings gezogen?"
- "Was hat [Name] in den letzten drei Tagen mehrfach angesprochen?"
- "Gibts offene Punkte aus dem Vertriebs-Meeting, die noch nirgendwo nachgehakt wurden?"
- "Fass mir die letzten fünf Slack-Nachrichten zum Thema [X] zusammen."

**Pro-Tipp:** Pack diesen Block in deine CLAUDE.md, damit dein Mitarbeiter weiß, dass die Intelligenz da ist:
```markdown
## Intelligenz, Meeting- und Slack-Datenbank
- Datenbank: `data/intel.db` (oder dein Pfad)
- Tabellen: `meetings`, `slack_messages`, `staff_registry`
- Abfragen: `sqlite3 data/intel.db "SELECT ..."`
- Meeting-Suche: title, transcript_text, summary, participants, date
- Slack-Suche: text, channel_name, user_name, workspace
- Sammlung läuft automatisch nach Zeitplan
```

---

## WAS ALS NÄCHSTES

*"Dein Gehirn ist komplett. Kontext, Zahlen, Meetings und Chats stehen alle.*

*Als Nächstes käme die Stimme. Ich ziehe in dein Handy ein und bin per Telegram für dich da, mit Sprachnachrichten, Fotos und allem Drum und Dran. Setup-Zeit etwa 30 bis 45 Minuten.*

*Willst du gleich weitermachen, oder lieber Pause?"*

Wenn der Member "ja" oder "weiter" sagt, direkt `/install module-installs/stimme` starten.
Wenn er Pause will, warm verabschieden und sagen dass er einfach `/install module-installs/stimme` läuft wenn er soweit ist.

## Nützliche Gewohnheiten

Erst mit ein paar Tagen Historie wird die Suche wirklich aussagekräftig, lass es eine Woche mitlaufen. Wenn du mehr Slack-Kanäle anbinden willst, geh in jeden Kanal und tippe `/invite @DeinBot`. Wenn jemand neu ins Team kommt, ins Team-Register packen, damit die Einordnung sauber bleibt:

```python
import sys; sys.path.insert(0, 'scripts/intel')
from db import get_connection, write_staff
conn = get_connection()
write_staff(conn, [{"email": "neu@firma.de", "name": "Neue Person", "role": "Engineer", "team": "firma", "department": "produkt"}])
conn.close()
```
