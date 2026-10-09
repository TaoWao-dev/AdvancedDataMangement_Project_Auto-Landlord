# Störungen

Nur Fälle, die tatsächlich aufgetreten sind. Die Tabelle wächst mit den
Vorfällen; sie wird nicht mit Hypothesen gefüllt.

| Symptom | Ursache | Behebung | Wie oft |
|---|---|---|---|
| `GATE 1 NICHT BESTANDEN`, `verticalId = 5`, `rowsFound = 13.353.029` | Marktplatzseite statt Immobiliensuche gespeichert | Bezirks-URL vollständig neu laden (eintippen, Enter), dann `tools/snapshot.js` | 3× am 25.09.2026 |
| `PLZ wie erwartet: Dateiname sagt 1010, Daten sagen 1020` | `__NEXT_DATA__` wird bei clientseitiger Navigation nicht aktualisiert; gespeichert wurde der serverseitig gerenderte Erstaufruf | nicht durchklicken — URL neu laden oder `view-source:` verwenden | 3× am 25.09.2026 |
| `sha256 schon aufgenommen` | dieselbe Datei unter neuem Namen gespeichert | neu laden statt umbenennen | 2× |
| `GATE 2` bricht ab, Feld `snapshot_datei`, „Telefonmuster" | eigenes technisches Feld traf das Telefonmuster (Zifferngruppen im Dateinamen) | Feld in `PII_UNVERDAECHTIG` aufnehmen — **nicht** das Muster lockern | 1× |
| `python3 -m pytest` findet pytest nicht | in dieser Umgebung nicht installierbar | `python3 tests/test_pipeline.py` — die Tests sind pytest-kompatibel geschrieben und haben einen eigenen Läufer am Dateiende | laufend |
| `kein Datumsordner unter data/raw` | Rohdaten fehlen (frischer Klon ohne Daten) | `data/raw/<JJJJ-MM-TT>/` anlegen und eine redigierte Datei hineinlegen | 1× |
| `git push` endet mit 403, „not in this session's authorized repository set" | das Repository ist der Arbeitssitzung nicht freigegeben | Repository in den Quellen der Sitzung eintragen; Sichtbarkeit auf „public" genügt **nicht** | laufend |
