# Projektdokumentation — Übersicht

Mietportfolio Wien, Verlängerungsentscheidung. Was wann abgegeben wird, Datei
für Datei. Die Inhalte stehen in den verlinkten Dateien, nicht hier.

## Die Dateien

| Datei | Inhalt | Abgabe | Stand 9.10.2026 |
|---|---|---|---|
| [`00_auftrag.md`](projektdokumentation/00_auftrag.md) | Adressat, Entscheidung, drei Analysen mit Werkzeug, was nicht drin ist | 26.9., laufend | **fertig** |
| [`01_entscheidungslog.md`](projektdokumentation/01_entscheidungslog.md) | je Entscheidung Datum, Alternative, Grund, Folge | laufend | **27 Einträge** |
| [`02_schritt1_datenzugriff.md`](projektdokumentation/02_schritt1_datenzugriff.md) | Quellentabelle, verworfene Kandidaten, Personenbezug | termin3 | **fertig** |
| [`03_schritt2_normalisieren.md`](projektdokumentation/03_schritt2_normalisieren.md) | Zahlen aus dem Lauf, Qualitätsbericht mit sechs Fragen, PII-Entscheidung | termin3 | **fertig** |
| [`04_schritt3_datenmodell.md`](projektdokumentation/04_schritt3_datenmodell.md) | Tabellen, Schlüssel, Beziehungen, Zuordnungslücken, Startbefehl | termin3 | **fertig** |
| [`05_schritt4_abfragen_referenzen.md`](projektdokumentation/05_schritt4_abfragen_referenzen.md) | je Analyse Werkzeug, Referenz, Herkunft, Prüfregel, Toleranz | termin3 | **fertig**, Extraktionsfälle offen |
| `06_schritt5_analyse_vorlage.md` | Eval-Suite, Modellwahl, Herkunft jeder Zahl, Selbsttest | termin4 | offen |
| `07_offene_punkte_lessons.md` | Datenlücken, Risiken, drei Lessons | termin4 | offen |

## Deliverable 2 · Datenpipeline (Tag `termin3`, 9.10.)

| Verlangt | Wo | Stand |
|---|---|---|
| Pipeline | `src/run.py`, `config.py`, `clean.py`, `integrate.py`, `derive.py` | **läuft**, zweimal mit identischem Ergebnis, byteweise geprüft |
| Datenmodell | [`src/sql/schema.sql`](../src/sql/schema.sql) | 6 Tabellen, Primär- und Fremdschlüssel, `NOT NULL` wo es gilt |
| Datenbank | `data/processed/mietportfolio.sqlite` | committet, 84 kB, ohne Personenspalten (Test) |
| Abfragen | `src/sql/kennzahl_*.sql` | 5 Abfragen, Ergebnis als CSV in `data/processed/` |
| Referenzantworten | `evals/references/` | 8 numerische Fälle + 3 Handproben; **8 Extraktionsfälle offen**, Grund in 05 |
| Test | `tests/test_pipeline.py` | 32 Tests grün, dazu `tests/test_modell.py` mit 26 |
| Projektdokumentation 00–05 | dieser Ordner | fertig |
| Betriebshandbuch, Entwurf | [`docs/betrieb.md`](betrieb.md) | Starten, neue Daten, Schwächen, Störungen |

**Was an Deliverable 2 fehlt und warum:** die acht Extraktionsfälle. Sie
brauchen das Kollektivvertragsdokument im Wortlaut; aus einer
Modellzusammenfassung gebildet wären sie wertlos, und genau dieser Fehler ist
in einer früheren Projektfassung schon einmal passiert (E02). Die Beschaffung
ist in [`evals/references/README.md`](../evals/references/README.md) beschrieben.

## Deliverable 1 · Pitch (26.9.)

| Verlangt | Wo | Stand |
|---|---|---|
| Poster | [`docs/pitch/poster_mietportfolio.pdf`](pitch/poster_mietportfolio.pdf) | **nachgereicht**, A3 hoch, eine Seite. Quelle: `poster_mietportfolio.html` — im Browser öffnen und als PDF drucken. **`[NAME]` und `[MATRIKELNUMMER]` sind noch einzusetzen.** |
| Auftrag | `00_auftrag.md` | fertig |
| Rohdaten | `data/raw/2026-09-25/` | 1 Schnappschuss, 90 Inserate; vier Bezirke fehlen |

## Deliverable 3 · Evaluierung und Vorlage (Tag `termin4`, 23.10.)

Offen: `docs/vorlage.md`, `prompts/`, `evals/<suite>.yaml`, `evals/graders/`,
`06`, `07`, Betriebshandbuch final, `.env.example`, Selbsttest aus frischem
Klon.

## Abweichungen von der Vorgabe, bewusst

| Vorgabe | Was wir tun | Begründung |
|---|---|---|
| „`data/raw/` ist gitignored" | redigierte Schnappschüsse sind committet, unredigierte nicht | der Zweck des Satzes — Personenbezug, Größe — ist durch die Redaktion erfüllt, und Schritt 5 verlangt einen lauffähigen Klon (E25) |
| Beispieldaten in `data/sample/` | dort liegt nur die Negativ-Fixture | im Beispielprojekt heißt `sample` „synthetisch erzeugt"; echte Daten so zu benennen verschleiert die Herkunft (E25) |
| „drei Werte von Hand nachrechnen" | eine Zweitimplementierung rechnet nach, die drei Handproben sind einzeln ausgewiesen und **noch nicht bestätigt** | zwei Programme können denselben Denkfehler teilen; die Handprobe bleibt eine Aufgabe für den Menschen (05) |
