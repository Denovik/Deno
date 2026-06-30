# Plan: Personal OS — Dennis' zweites Gehirn innerhalb von ceogpt-start

**Erstellt:** 2026-06-30
**Status:** Umgesetzt
**Anfrage:** Ein persönliches Betriebssystem aufbauen, das über das Mindwave-Business hinausgeht — Ziele, Aufgaben, Wissen, Gesundheit/Finanzen und Business-Daten an einem Ort, sauber getrennt aber im selben CEO-GPT.

---

## Überblick

### Was dieser Plan erreicht

Dieser Plan erweitert `ceogpt-start` um einen neuen Bereich `personal-os/`, der Dennis' ganzes Leben abbildet — nicht nur das Business. Fünf Säulen: Ziele & Notizen, Aufgaben & Termine, Wissen & Lernen, Gesundheit & Finanzen, und eine engere Verzahnung der bestehenden Business-Daten-Pipeline mit dem Gesamtbild. Ein neuer Befehl `/personal-prime` lädt diesen Bereich, ergänzend zum bestehenden `/prime` fürs Business.

### Warum das zählt

Aktuell deckt `ceogpt-start` nur das Mindwave-Business ab. Dennis ist aber gleichzeitig Vollzeit-Angestellter, baut das Business nebenher auf und hat ein Leben außerhalb davon (Gesundheit, Finanzen, Lernen, persönliche Ziele). Ohne einen Ort, an dem das zusammen sichtbar ist, bleibt die Sicht auf sein Leben fragmentiert — Business-Fortschritt und Lebens-Fortschritt laufen getrennt. Ein Personal OS gibt ihm einen einzigen Ort, an dem sein Mitarbeiter das Gesamtbild kennt: nicht nur "wie läuft Mindwave", sondern "wie läuft Dennis' Leben, und wie hängt das Business da rein".

---

## Aktueller Stand

### Bestehende relevante Struktur

- `context/` — Business-Kontext: `business-info.md`, `personal-info.md`, `strategy.md`, `current-data.md`, `group/key-metrics.md` (auto-generiert), `import/` (Dokumente-Eingang)
- `data/data.db` — SQLite mit Business-Kennzahlen (YouTube, Instagram Tagesstände)
- `scripts/daten/` — Sammel-Pipeline für Business-Daten (collect.py, collect_youtube.py, collect_instagram.py, generate_metrics.py, db.py)
- `.claude/commands/prime.md` — lädt `CLAUDE.md` + `context/` + Kennzahlen + Historie zu Sitzungsbeginn, reines Business-Briefing
- `.claude/commands/task-audit.md` — kartiert wiederkehrende Business-Aufgaben (hat schon einen Bereich "Persönliches und Lebens-Admin", aber nur als Business-Nebenkategorie)
- `reference/data-access.md` — Schema-Dokumentation für SQL-Zugriff auf `data.db`
- `outputs/` — fertige Arbeitsergebnisse, nach Typ geordnet (`outputs/berichte/`, `outputs/videos/`, etc.)
- `HISTORY.md` — zeitliches Logbuch aller Änderungen am CEO-GPT
- `docs/_index.md` — Doku-Routing für gebaute Systeme

`personal-info.md` enthält bereits Eckdaten zu Dennis (27, Vodafone-Verkäufer, Nebenprojekt Mindwave), ist aber strikt business-gerahmt — beschreibt ihn nur in seiner Rolle als Gründer.

### Lücken oder Probleme, die der Plan löst

- Kein Ort für persönliche Ziele, Notizen oder Reflexionen — nur Business-Strategie existiert
- Keine Aufgaben-/Termin-Verwaltung über das Business hinaus — `task-audit` kartiert nur, verwaltet aber nichts laufend
- Kein Wissens-Archiv — Bücher, Kurse, Artikel werden nirgends festgehalten
- Keine Gesundheits- oder persönliche Finanz-Daten — `data/data.db` enthält nur Business-Kennzahlen
- `/prime` lädt ausschließlich Business-Kontext — der Mitarbeiter hat beim Sitzungsstart kein Bild von Dennis' Gesamtleben
- Risiko bei naivem Ansatz: persönliche und Business-Finanzen in derselben Datenbank/Tabelle vermischen, was Auswertungen und Privatsphäre durcheinanderbringt

---

## Geplante Änderungen

### Zusammenfassung der Änderungen

- Neuer Ordner `personal-os/` als eigener Wurzel-Bereich (gleiche Ebene wie `context/`, `data/`, `scripts/`) — klar abgegrenzt vom Business, aber im selben Projekt
- Fünf Unterbereiche darin: `ziele-notizen/`, `aufgaben-termine/`, `wissen/`, `gesundheit-finanzen/`, plus eine `profil.md` als Gegenstück zu `context/personal-info.md`, aber lebensweit statt rollenweit
- Eigene SQLite-Datenbank `personal-os/personal.db` für strukturierte Daten (Aufgaben, Gesundheits-Tracking, persönliche Finanzen) — bewusst getrennt von `data/data.db`, damit Business- und Privat-Kennzahlen nie vermischt werden
- Neuer Befehl `/personal-prime` lädt den Personal-OS-Kontext, analog zu `/prime` fürs Business
- Bestehendes `/prime` bekommt einen kurzen Hinweis-Absatz, dass `/personal-prime` für den Lebensbereich existiert, OHNE den Business-Fokus von `/prime` selbst zu verwässern
- `CLAUDE.md` wird um den neuen Bereich ergänzt (Ordnerstruktur-Tabelle, neuer Befehl, Erste-Schritte-Hinweis)
- Business-Daten-Pipeline bleibt unverändert in `scripts/daten/` — Personal OS referenziert sie nur lesend für das Gesamtbild, baut sie nicht um

### Neue Dateien

| Pfad | Zweck |
|---|---|
| `personal-os/profil.md` | Wer Dennis ist — lebensweit, nicht nur als Gründer. Werte, Lebenssituation, was ihm wichtig ist. |
| `personal-os/ziele-notizen/ziele.md` | Langfristige persönliche Ziele, getrennt von Business-Strategie (z.B. Gesundheit, Beziehungen, Freiheit) |
| `personal-os/ziele-notizen/notizen.md` | Laufendes Gedanken- und Ideen-Log, chronologisch, niedrige Einstiegshürde |
| `personal-os/aufgaben-termine/aufgaben.md` | Lebensweite To-do-Liste (nicht nur Business) — einfache Markdown-Checkliste nach Bereich |
| `personal-os/aufgaben-termine/routinen.md` | Wiederkehrende persönliche Routinen (täglich/wöchentlich/monatlich) |
| `personal-os/wissen/archiv.md` | Index aller festgehaltenen Bücher/Kurse/Artikel mit Kurz-Take-aways und Verweis auf Detail-Dateien |
| `personal-os/wissen/notizen/.gitkeep` | Unterordner für einzelne Wissens-Notizen (eine Datei pro Buch/Kurs), startet leer |
| `personal-os/gesundheit-finanzen/gesundheit.md` | Gesundheits-Tracking-Übersicht (Schlaf, Fitness, Gewohnheiten) — manuell gepflegt oder per Skript befüllt |
| `personal-os/gesundheit-finanzen/finanzen.md` | Persönliche Finanzen — Übersicht, getrennt von Business-Affiliate-Einnahmen |
| `personal-os/personal.db` | SQLite-Datenbank für strukturierte Personal-OS-Daten (Tagesstände Gesundheit, Finanz-Transaktionen, Aufgaben-Historie) — wird vom Setup-Skript angelegt, nicht von Hand |
| `personal-os/db_schema.sql` | Schema-Definition für `personal.db` (Tabellen: `health_daily`, `finance_transactions`, `tasks_log`) |
| `scripts/personal-os/init_db.py` | Einmalig: legt `personal.db` aus `db_schema.sql` an, falls noch nicht vorhanden |
| `reference/personal-os-data-access.md` | Schema-Doku für `personal.db`, analog zu `reference/data-access.md` fürs Business |
| `.claude/commands/personal-prime.md` | Neuer Befehl: lädt Personal-OS-Kontext zu Sitzungsbeginn |

### Geänderte Dateien

| Pfad | Änderungen |
|---|---|
| `CLAUDE.md` | Ordnerstruktur-Tabelle um `personal-os/` ergänzen; neuen Befehl `/personal-prime` in die Befehlsliste aufnehmen; kurzer Absatz im "Was das hier ist"-Bereich, der klarstellt, dass es jetzt Business- UND Personal-Bereich gibt |
| `.claude/commands/prime.md` | Ein Satz am Ende: Hinweis, dass `/personal-prime` für den Lebensbereich (Ziele, Gesundheit, Wissen, Aufgaben) existiert — kein inhaltlicher Eingriff in den bestehenden Business-Fokus |
| `.gitignore` | `personal-os/personal.db` NICHT ignorieren (soll wie `data/data.db` versioniert/gesichert werden) — aber prüfen, ob sensible Inhalte (Finanzen) stattdessen bewusst lokal/ungetrackt bleiben sollen (siehe Offene Fragen) |

### Gelöschte Dateien (falls vorhanden)

Keine.

---

## Design-Entscheidungen

### Wichtige Entscheidungen

1. **Eigener Root-Ordner `personal-os/` statt Unterordner in `context/`**: `context/` ist laut `CLAUDE.md` klar als "Was dein Mitarbeiter über dich weiß" für das Business definiert und wird komplett bei `/prime` geladen. Würde Personal-OS-Inhalte dort hineingemischt, würde jede Business-Sitzung unnötig Lebens-Kontext mitladen (Kontext-Bloat) und die saubere Trennung Business/Privat ginge verloren. Ein eigener Root-Ordner mit eigenem Lade-Befehl hält beides trennbar, aber im selben Projekt wie gewünscht.
2. **Eigene Datenbank `personal.db` statt Erweiterung von `data/data.db`**: `data/data.db` ist beschrieben als "alle Kennzahlen als Tagesstände" fürs Business und wird von der bestehenden `scripts/daten/`-Pipeline automatisch befüllt. Persönliche Gesundheits- und Finanzdaten dort einzumischen würde das Schema verwässern und das Risiko erhöhen, dass ein künftiges Business-Reporting-Skript versehentlich private Daten mit ausgibt. Trennung folgt demselben Muster, das das Projekt schon für Business-Daten etabliert hat (eigene DB, eigenes Access-Doc).
3. **Markdown-first für Ziele/Notizen/Wissen, SQLite nur für klar strukturierte, zeitreihenartige Daten (Gesundheit, Finanz-Transaktionen, Aufgaben-Log)**: folgt dem bestehenden Muster im Projekt — `context/*.md` für qualitativen, sich langsam ändernden Kontext; `data.db` für Tagesstände/Zeitreihen. Ziele und Notizen sind Gedanken, kein Tabellenformat; Gesundheit/Finanzen sind klassische Tagesstand-Daten wie die bestehende YouTube/Instagram-Pipeline.
4. **`/personal-prime` als separater Befehl statt `/prime` zu erweitern**: `/prime` ist fest als Business-Sitzungsstart etabliert (wird in "Erste Schritte" und "Sitzungs-Ablauf" in `CLAUDE.md` so beschrieben). Ihn um einen kompletten Lebensbereich zu erweitern würde ihn aufblähen und jede reine Business-Sitzung mit Lebens-Kontext belasten, den sie nicht braucht. Zwei Einstiegspunkte lassen Dennis wählen, welchen Hut er gerade aufhat.
5. **Business-Daten-Pipeline (`scripts/daten/`) bleibt unangetastet**: Die Anfrage nennt "Business-Daten sammeln, verbessern und weiterentwickeln" als einen der fünf Bereiche. Dieser Plan baut das Personal OS als Rahmen drumherum, der die bestehende Pipeline referenziert (in `profil.md`/`personal-prime.md` verlinkt), tastet die Pipeline selbst aber nicht an — eine inhaltliche Weiterentwicklung der Business-Daten-Sammlung (z.B. neue Metriken, TikTok-Anbindung) ist eine eigene, spätere Plan-Iteration, sobald TikTok-Freigabe und Trade-Republic-Status feststehen. Das hält diesen Plan fokussiert auf die Personal-OS-Struktur selbst.

### Verworfene Alternativen

- **Komplett getrenntes zweites Projekt** wurde in der Rückfrage an Dennis explizit verworfen — er wollte es innerhalb von `ceogpt-start`.
- **Alles in `context/` einsortieren** wurde verworfen (siehe Entscheidung 1) — würde Business-Kontext-Ladevorgänge aufblähen und die klare Markengrenze zwischen "das ist Mindwave" und "das ist Dennis' Leben" auflösen.
- **Eine gemeinsame Datenbank mit Tabellen-Präfixen (`personal_health_daily` statt eigene DB)** wurde verworfen — eine physisch getrennte Datei ist robuster gegen versehentliches Mit-Auswerten/Mit-Sichern persönlicher Daten bei Business-Reports und macht eine künftige unterschiedliche Backup-/Privatsphäre-Behandlung einfacher.

### Offene Fragen

1. **Sollen `personal-os/gesundheit-finanzen/finanzen.md` und `personal.db` ins Git-Repo committet werden, oder lokal bleiben (gitignored)?** Das Projekt versioniert aktuell alles außer `.env` und `credentials/`. Persönliche Finanzdaten sind sensibler als Business-Affiliate-Zahlen. Empfehlung in diesem Plan: gitignored, bis Dennis das anders entscheidet — wird unten als expliziter Schritt mit Rückfrage markiert.
2. **Wie soll `personal.db` befüllt werden — manuell, oder per Skript (z.B. Anbindung an Apple Health, Bank-Export)?** Dieser Plan baut nur das Grundgerüst (Schema + manuelles Pflegen über Markdown-Notizen, die bei Bedarf in die DB überführt werden). Eine automatische Anbindung (Health-App, Banking-API) ist ein separates späteres Modul, ähnlich wie `module-installs/daten` für Business.

---

## Schritt-für-Schritt-Aufgaben

In dieser Reihenfolge ausführen.

### 1. Git-Tracking-Entscheidung für sensible Personal-OS-Daten klären

Bevor Dateien angelegt werden: kurz mit Dennis abstimmen, ob `personal-os/gesundheit-finanzen/` (insbesondere `finanzen.md` und `personal.db`) versioniert oder lokal gehalten werden soll. Default für diesen Plan: lokal halten (gitignored), bis er explizit "committen" sagt.

**Aktionen:**
- Rückfrage an Dennis vor Umsetzung (oder: Default "gitignored" anwenden und in der Umsetzungs-Zusammenfassung explizit nennen, leicht änderbar)
- `.gitignore` um `personal-os/gesundheit-finanzen/finanzen.md` und `personal-os/personal.db` ergänzen, falls Default angewendet wird

**Betroffene Dateien:**
- `.gitignore`

---

### 2. Ordnerstruktur `personal-os/` anlegen

Grundgerüst für alle fünf Bereiche schaffen.

**Aktionen:**
- Ordner anlegen: `personal-os/`, `personal-os/ziele-notizen/`, `personal-os/aufgaben-termine/`, `personal-os/wissen/`, `personal-os/wissen/notizen/`, `personal-os/gesundheit-finanzen/`
- `.gitkeep` in `personal-os/wissen/notizen/` (Ordner startet leer, soll aber im Repo sichtbar sein)

**Betroffene Dateien:**
- `personal-os/wissen/notizen/.gitkeep`

---

### 3. `personal-os/profil.md` schreiben

Lebensweites Gegenstück zu `context/personal-info.md`. Nutzt bereits bekannte Eckdaten aus `context/personal-info.md` als Ausgangspunkt, erweitert um Lebensbereiche außerhalb der Gründer-Rolle.

**Aktionen:**
- Datei anlegen mit Abschnitten: Wer Dennis ist (kurz, lebensweit statt rollenweit), Lebenssituation (Job bei Vodafone, Nebenprojekt Mindwave, Zeitbudget), was ihm wichtig ist (Platzhalter, von Dennis später zu füllen), wie die fünf Personal-OS-Bereiche zusammenhängen (kurze Erklärung wie bei `context/business-info.md` "Wie das zusammenhängt")
- Explizit referenzieren: "Für die Gründer-Rolle siehe `context/personal-info.md` — diese Datei ergänzt das um den Rest des Lebens."
- Platzhalter-Abschnitte klar als "von Dennis auszufüllen" markieren, nicht erfinden, was er nicht gesagt hat

**Betroffene Dateien:**
- `personal-os/profil.md`

---

### 4. Ziele & Notizen aufsetzen

**Aktionen:**
- `personal-os/ziele-notizen/ziele.md` anlegen: Struktur für langfristige persönliche Ziele (z.B. Kategorien wie Gesundheit, Beziehungen, Freiheit/Finanzen, Wachstum), explizit getrennt von `context/strategy.md` (Business). Felder pro Ziel: Was, Warum, Zeithorizont, Status. Leere Vorlage mit 1-2 Beispiel-Platzhaltern, die als "<von dir auszufüllen>" markiert sind.
- `personal-os/ziele-notizen/notizen.md` anlegen: chronologisches Log-Format (Datum + Eintrag), niedrigste Einstiegshürde — Kopfzeile erklärt "schreib hier einfach rein, Ordnung kommt später"

**Betroffene Dateien:**
- `personal-os/ziele-notizen/ziele.md`
- `personal-os/ziele-notizen/notizen.md`

---

### 5. Aufgaben & Termine aufsetzen

**Aktionen:**
- `personal-os/aufgaben-termine/aufgaben.md` anlegen: Markdown-Checklisten-Format, gruppiert nach Lebensbereich (Business, Gesundheit, Privates, Sonstiges), nicht nach Datum — Termine/Kalender werden in dieser Phase NICHT mit einer externen Kalender-API verknüpft (kein Tool-Zugriff vorhanden), sondern als einfache Liste mit Datum-Feld geführt
- `personal-os/aufgaben-termine/routinen.md` anlegen: Tabelle mit Spalten Routine / Frequenz (täglich, wöchentlich, monatlich) / Bereich — leer mit Erklärung, wie es zu pflegen ist
- Kurzer Hinweis in beiden Dateien: für Business-spezifische wiederkehrende Aufgaben bleibt `/task-audit` die Quelle der Wahrheit, diese Dateien sind für alles drüber hinaus

**Betroffene Dateien:**
- `personal-os/aufgaben-termine/aufgaben.md`
- `personal-os/aufgaben-termine/routinen.md`

---

### 6. Wissens-Archiv aufsetzen

**Aktionen:**
- `personal-os/wissen/archiv.md` anlegen: Index-Tabelle (Titel, Typ [Buch/Kurs/Artikel], Datum, Status [gelesen/in Arbeit/geplant], Kurz-Take-away, Link zur Detail-Notiz in `wissen/notizen/`)
- Erklärender Kopf-Absatz: wie ein neuer Eintrag angelegt wird (Detail-Datei in `notizen/` + Zeile im Index)
- `personal-os/wissen/notizen/.gitkeep` (bereits in Schritt 2 angelegt) — Ordner bleibt leer bis erster Eintrag

**Betroffene Dateien:**
- `personal-os/wissen/archiv.md`

---

### 7. Gesundheit & Finanzen — Markdown-Übersichten

**Aktionen:**
- `personal-os/gesundheit-finanzen/gesundheit.md` anlegen: Übersichts-Format mit Abschnitten für aktuelle Gewohnheiten/Routinen (Schlaf, Bewegung, Ernährung — als Freitext/Checkliste, nicht erfunden), Verweis auf `personal.db`-Tabelle `health_daily` für strukturiertes Tracking sobald gewünscht
- `personal-os/gesundheit-finanzen/finanzen.md` anlegen: persönliche Finanz-Übersicht, EXPLIZIT getrennt von Business-Affiliate-Einnahmen (die bleiben in `context/current-data.md` / `data/data.db`) — Abschnitt, der das klarstellt, damit nie vermischt wird
- Beide Dateien klar mit "Stand: <Datum>, manuell gepflegt" kennzeichnen, keine Zahlen erfinden

**Betroffene Dateien:**
- `personal-os/gesundheit-finanzen/gesundheit.md`
- `personal-os/gesundheit-finanzen/finanzen.md`

---

### 8. `personal.db`-Schema und Setup-Skript

**Aktionen:**
- `personal-os/db_schema.sql` schreiben mit drei Tabellen:
  - `health_daily` (date TEXT PRIMARY KEY, sleep_hours REAL, weight_kg REAL, exercise_minutes INTEGER, mood_score INTEGER, notes TEXT, logged_at TEXT)
  - `finance_transactions` (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, description TEXT, amount_eur REAL, type TEXT CHECK(type IN ('einnahme','ausgabe')), logged_at TEXT)
  - `tasks_log` (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, area TEXT, completed_date TEXT, logged_at TEXT)
- `scripts/personal-os/init_db.py` schreiben (folgt Muster von `scripts/daten/db.py`): liest `db_schema.sql`, legt `personal-os/personal.db` an falls nicht vorhanden, idempotent (kann mehrfach laufen ohne Fehler)
- Einmal ausführen zur Verifikation: `python3 scripts/personal-os/init_db.py`

**Betroffene Dateien:**
- `personal-os/db_schema.sql`
- `scripts/personal-os/init_db.py`
- `personal-os/personal.db` (wird vom Skript erzeugt, nicht von Hand)

---

### 9. Daten-Zugriffs-Doku schreiben

**Aktionen:**
- `reference/personal-os-data-access.md` anlegen, im Stil von `reference/data-access.md`: Pfad zur DB, wie verbinden, Tabellen-Schema-Beschreibung für alle drei Tabellen, Hinweis dass diese DB getrennt von `data/data.db` ist und warum (Verweis auf diesen Plan / Design-Entscheidung 2)

**Betroffene Dateien:**
- `reference/personal-os-data-access.md`

---

### 10. Befehl `/personal-prime` anlegen

**Aktionen:**
- `.claude/commands/personal-prime.md` schreiben, strukturell analog zu `.claude/commands/prime.md`:
  - Liest `personal-os/profil.md`, alle Dateien in `personal-os/ziele-notizen/`, `personal-os/aufgaben-termine/`, `personal-os/wissen/archiv.md`, `personal-os/gesundheit-finanzen/`
  - On-Demand-Hinweis: `reference/personal-os-data-access.md` nur laden, wenn tiefere Datenanalyse (Gesundheit/Finanzen) gebraucht wird
  - Zusammenfassung an Dennis: wer er lebensweit ist, aktuelle persönliche Ziele, offene Aufgaben, was zuletzt im Wissens-Archiv dazukam, Gesundheits-/Finanz-Stand falls gepflegt
  - Gleicher Verhaltens-Block wie bei `/prime`: normales Deutsch, knapp, ehrlich sagen wenn ein Bereich noch leer ist (keine Inhalte erfinden)
  - Abschlusshinweis: für Business-Sitzungsstart bleibt `/prime` zuständig, beide Befehle ergänzen sich, müssen nicht beide pro Sitzung laufen

**Betroffene Dateien:**
- `.claude/commands/personal-prime.md`

---

### 11. `/prime` um Verweis ergänzen

**Aktionen:**
- Am Ende von `.claude/commands/prime.md`, nach dem bestehenden "Verhalten"-Abschnitt, einen kurzen neuen Abschnitt "Verwandter Befehl" anfügen: ein bis zwei Sätze, dass `/personal-prime` für Dennis' Lebensbereich (Ziele, Aufgaben, Wissen, Gesundheit, Finanzen) existiert und unabhängig davon läuft
- Keine inhaltliche Änderung am bestehenden Business-Fokus von `/prime`

**Betroffene Dateien:**
- `.claude/commands/prime.md`

---

### 12. `CLAUDE.md` aktualisieren

**Aktionen:**
- In der Ordnerstruktur-Übersicht (Code-Block + Tabelle) `personal-os/` mit Unterordnern ergänzen, kurz erklärt
- In der Tabelle unter der Struktur-Übersicht eine Zeile für `personal-os/` hinzufügen: "Dennis' Leben außerhalb des Business — Ziele, Aufgaben, Wissen, Gesundheit, Finanzen. Wird bei `/personal-prime` gelesen."
- Im Abschnitt "Befehle" einen neuen Unterabschnitt `### /personal-prime` nach `/prime` einfügen, mit Kurzbeschreibung und Beispiel
- Im Abschnitt "Was das hier ist" ODER "Kontext-Zusammenfassung" einen knappen Satz ergänzen, dass es jetzt zwei Bereiche gibt: Business (`/prime`) und Leben (`/personal-prime`) — ohne den bestehenden Business-Fokus der Datei zu verwässern, da `ceogpt-start` weiterhin in erster Linie das CEO-GPT fürs Business ist und Personal OS eine bewusste Erweiterung obendrauf
- "Erste Schritte"-Abschnitt: optionalen Hinweis ergänzen, dass nach der Business-Einrichtung bei Bedarf auch `personal-os/` befüllt werden kann (kein Pflichtschritt, da Personal OS optional zur Kern-Funktion ist)

**Betroffene Dateien:**
- `CLAUDE.md`

---

### 13. Prüfen und gegenlesen

**Aktionen:**
- `python3 scripts/personal-os/init_db.py` erneut laufen lassen, bestätigen dass es idempotent ist (zweiter Lauf erzeugt keinen Fehler, keine doppelten Tabellen)
- Mit SQLite prüfen, dass alle drei Tabellen in `personal-os/personal.db` existieren (`sqlite3 personal-os/personal.db ".tables"`)
- Alle neuen Markdown-Dateien auf Platzhalter-Konsistenz prüfen — keine erfundenen Zahlen oder Fakten über Dennis, alles als "von dir auszufüllen" markiert, wo keine echten Daten vorliegen
- `CLAUDE.md` und `.claude/commands/prime.md` gegenlesen, dass Verweise auf `/personal-prime` korrekt und konsistent sind
- `.gitignore` prüfen, dass sensible Personal-OS-Dateien gemäß Entscheidung aus Schritt 1 korrekt behandelt werden

**Betroffene Dateien:**
- Keine neuen, nur Verifikation der oben genannten

---

## Verbindungen und Abhängigkeiten

### Dateien, die auf diesen Bereich verweisen

- `CLAUDE.md` verweist nach Umsetzung auf `personal-os/` und `/personal-prime`
- `.claude/commands/prime.md` verweist nach Umsetzung kurz auf `/personal-prime`
- `context/personal-info.md` wird in `personal-os/profil.md` referenziert (nicht dupliziert)

### Updates für Konsistenz

- `HISTORY.md`: nach Umsetzung (über `/commit` oder manuell) einen Eintrag "Personal OS aufgebaut" ergänzen
- `docs/_index.md`: prüfen ob ein System-Doku-Eintrag für "Personal OS" sinnvoll ist (analog zu Jarvis/Daten-Pipeline) — empfohlen, da es ein neues eigenständiges System ist, das künftige Sitzungen wiederfinden müssen

### Auswirkung auf bestehende Abläufe

- `/prime` bleibt inhaltlich unverändert für Business-Sitzungen, bekommt nur einen Verweis-Satz
- Bestehende Business-Datenpipeline (`scripts/daten/`), `data/data.db`, `context/` bleiben vollständig unangetastet
- Neuer optionaler Sitzungs-Einstieg `/personal-prime` für Sitzungen, in denen es um Dennis' Leben statt ums Business geht
- Kein bestehender Automatisierungs-Lauf (Jarvis-Pipeline, Daten-Sammlung, Intelligenz-Analyse) wird durch diesen Plan berührt

---

## Prüf-Checkliste

- [ ] `personal-os/` mit allen fünf Unterbereichen existiert
- [ ] `personal-os/profil.md` enthält keine erfundenen Fakten, nur Bekanntes + klar markierte Platzhalter
- [ ] `personal-os/personal.db` existiert und enthält die drei Tabellen `health_daily`, `finance_transactions`, `tasks_log`
- [ ] `scripts/personal-os/init_db.py` läuft fehlerfrei und ist idempotent (zweiter Lauf ohne Fehler)
- [ ] `reference/personal-os-data-access.md` beschreibt das Schema korrekt und vollständig
- [ ] `.claude/commands/personal-prime.md` existiert und folgt dem Muster von `prime.md`
- [ ] `.claude/commands/prime.md` enthält den neuen Verweis-Satz, ohne sonst verändert zu sein
- [ ] `CLAUDE.md` spiegelt die neue Struktur (Ordner-Tabelle, Befehlsliste, Erste-Schritte-Hinweis)
- [ ] `.gitignore` behandelt sensible Personal-OS-Dateien gemäß Entscheidung aus Schritt 1
- [ ] Keine bestehende Business-Datei (`context/*`, `data/data.db`, `scripts/daten/*`) wurde inhaltlich verändert

---

## Erfolgskriterien

Die Umsetzung ist fertig, wenn:

1. Dennis `/personal-prime` ausführen kann und eine ehrliche, nicht erfundene Zusammenfassung seines aktuellen Personal-OS-Stands bekommt (auch wenn die meisten Bereiche anfangs noch leer/Platzhalter sind)
2. `personal-os/personal.db` technisch einsatzbereit ist für künftiges Gesundheits-/Finanz-Tracking, ohne dass Business-Daten berührt wurden
3. `CLAUDE.md` für eine neue Sitzung klar erklärt, dass es jetzt zwei Bereiche gibt (Business via `/prime`, Leben via `/personal-prime`) und wie sie zusammenhängen

---

## Notizen

- Dieser Plan baut bewusst nur das **Grundgerüst**. Die eigentliche Befüllung (Dennis' echte Ziele, Wissens-Einträge, Gesundheitsdaten) ist seine Aufgabe danach, im Gespräch mit seinem Mitarbeiter — nicht Teil dieser Umsetzung, da sonst Fakten erfunden würden.
- Eine spätere Ausbaustufe könnte ein `module-installs/personal-os`-Paket draus machen (wie bei `daten` oder `intelligenz`), falls Dennis das System später an andere weitergeben will (`/share`). Für jetzt reicht die direkte Umsetzung in diesem Projekt.
- Automatische Anbindungen (Apple Health, Bank-Schnittstellen, Kalender-Sync) sind bewusst NICHT Teil dieses Plans — das wäre ein eigenes Folge-Modul, sobald das Grundgerüst steht und sich im Alltag bewährt hat.
- Offene Frage 1 (Git-Tracking sensibler Daten) sollte vor `/implement` kurz mit Dennis bestätigt werden, auch wenn ein sinnvoller Default (gitignored) im Plan vorgesehen ist.

---

## Umsetzungs-Notizen

**Umgesetzt:** 2026-06-30

### Zusammenfassung

Personal-OS-Grundgerüst komplett aufgebaut: Ordnerstruktur (`profil.md`, `ziele-notizen/`, `aufgaben-termine/`, `wissen/`, `gesundheit-finanzen/`), eigene SQLite-Datenbank mit drei Tabellen (`health_daily`, `finance_transactions`, `tasks_log`), Setup-Skript (idempotent geprüft), Daten-Zugriffs-Doku, neuer Befehl `/personal-prime`, Verweis in `/prime`, `CLAUDE.md` vollständig aktualisiert (Struktur, Befehlsliste, Erste-Schritte). System-Doku unter `docs/personal-os.md` angelegt und in `docs/_index.md` eingetragen. `HISTORY.md` ergänzt.

### Abweichungen vom Plan

Keine inhaltlichen Abweichungen. Offene Frage 1 (Git-Tracking sensibler Daten) wurde vor Umsetzung mit Dennis geklärt: "Nur lokal" — `personal-os/personal.db` und `personal-os/gesundheit-finanzen/finanzen.md` sind gitignored.

### Aufgetretene Probleme

Keine.
