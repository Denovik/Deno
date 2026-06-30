# Prime

> Lies den Kontext und mach dich für die Sitzung bereit.

## Was du tust

1. Lies `CLAUDE.md` vollständig
2. Lies alle Dateien in `context/` durch
3. Lies `context/group/key-metrics.md` (Aktuelle Kennzahlen aus der Datenbank — automatisch aktualisiert)
4. Wenn `context/import/` Dateien enthält, schau auch dort rein
5. `HISTORY.md`: CEO-GPT-Logbuch (was wurde gebaut, wann, von wem)
6. `docs/_index.md`: Doku-Routing-Index (hier findest du die passenden Dokus)

**On-Demand:** `reference/data-access.md` enthält volle Tabellen-Schemas und SQL-Beispiele — nur laden, wenn eine Aufgabe tiefere Daten-Analyse braucht.

## Zusammenfassung an den Geschäftsführer

Wenn du fertig gelesen hast, fass kurz zusammen:

1. **Wer er ist und was sein Business macht.** Ein bis zwei Sätze. Zeig, dass du das Bild hast.
2. **Seine Rolle.** Wofür er verantwortlich ist und wo seine Zeit hingeht.
3. **Aktuelle Prioritäten.** Was diese Wochen oder dieses Quartal zählt.
4. **Stand der Zahlen.** Aktuelle Kennzahlen aus `context/group/key-metrics.md` (Datenbank-Stand). Alles über 2 Tage alt kurz markieren. Für tiefere Analyse ist direkte SQL-Abfrage auf `data/data.db` möglich (`reference/data-access.md` für Schemas).
5. **Verfügbare Befehle.** Welche Slash-Befehle in `.claude/commands/` liegen.
6. **Bereit.** Bestätige knapp, dass du im Bild bist und auf Anweisungen wartest.

## Verhalten

- Keine Fachsprache. Normales Deutsch.
- Knapp, nicht überfrachtet. Der Geschäftsführer will einen Überblick, kein Protokoll.
- Wenn `context/` noch leer oder dünn ist, sag das ehrlich. Empfiehl `/install module-installs/kontext`, damit das Gehirn deines Mitarbeiters einen echten Stand bekommt.
- Wenn etwas in den Kontext-Dateien widersprüchlich oder veraltet wirkt, weis darauf hin. Nicht überstimmen, sondern fragen.

## Verwandter Befehl

Für Dennis' Leben außerhalb des Business — Ziele, Aufgaben, Wissen, Gesundheit, Finanzen — gibt es `/personal-prime`. Läuft unabhängig von diesem Befehl, muss nicht jede Sitzung mit aufgerufen werden.
