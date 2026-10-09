# Herkunft des Schnappschusses vom 25.09.2026

| | |
|---|---|
| Quelle | willhaben.at, Suche „Mietwohnungen Wien 1020 Leopoldstadt", `?rows=90` |
| Abruf | 25.09.2026, 15:55 — laut `searchDate` des Servers, nicht laut Parseruhr |
| Beschaffung | manuell durch einen Menschen (Begründung: `docs/projektdokumentation/02_schritt1_datenzugriff.md`) |
| Treffer der Suche | 154 |
| Auf dieser Seite | 90 → Teilseite, im Qualitätsbericht als Warnung geführt |

## Zwei Dateien, zwei Hashes

Die hier liegende Datei ist **nicht** das gespeicherte Original, sondern eine
redigierte Fassung. Das Original enthält personenbezogene Daten und liegt
deshalb nicht im Repository.

| | SHA256 |
|---|---|
| Original, nur lokal | `a9854b6c231c60987100bee0c7317e4d9f567e4e94396f7e7eb7d31ffcf925c2` |
| redigierte Fassung, hier | `a7cf1adb7a93ec07ff2eafdf301ab972277014b71a3bb84e88dfc5f421cb2c87` |

Erzeugt mit:

```bash
python3 tools/redigiere_schnappschuss.py \
    <original>.json data/raw/2026-09-25/wh_1020_mietwohnungen_2026-09-25T1555.json
```

Das Werkzeug prüft selbst, dass der Parser aus beiden Fassungen dieselbe Zahl
Inserate, dieselbe Trefferzahl, denselben Abrufzeitpunkt und dieselbe
Privat/Gewerblich-Verteilung liest. Der Beleg, dass die Redaktion kein Ergebnis
verändert hat: die fünf Kennzahl-CSV sind vor und nach der Redaktion
bit-identisch (`data/processed/kennzahl_*.csv`).

Was entfernt wurde und warum, steht im Kopf von
`tools/redigiere_schnappschuss.py` und maschinenlesbar im Block `_redaktion`
der Datei selbst.
