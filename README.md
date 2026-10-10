# Mietportfolio Wien — Verlängerungsentscheidung

> Die Projektbeschreibung des Repositoryinhabers, wörtlich:
>
> **AdvancedDataManagement_Project_Auto-Landlord**
> My github repo for a dystopian data-management project that scrapes
> rent-prices and income levels to optimize the maximum extractable rent from
> the tennants of a real estate company. DO NOT DO THIS IN REALLIFE!

**Eine Berichtigung zur Beschreibung, die für die Bewertung wichtig ist:** das
Projekt *scraped* nicht. Die robots.txt der Inseratsplattform verbietet
automatisierten Zugriff ausdrücklich; die Schnappschüsse werden von einem
Menschen im Browser gespeichert, und erst die Verarbeitung ist automatisiert.
Das ist eine der zentralen Entscheidungen des Projekts, nicht ein Detail —
siehe `docs/projektdokumentation/02_schritt1_datenzugriff.md` und
Entscheidungslog E06. Einkommensdaten fließen nicht in die Preisbildung ein,
sondern nur in Annahme- und Ausfallwahrscheinlichkeit (E05).

Für jeden auslaufenden Mietvertrag: zu welchem Mietzins bieten wir die
Fünfjahresverlängerung an — oder lassen wir auslaufen und vermieten neu?

**Entscheidungsträger:** Leitung Asset Management Wohnen.
**Portfolio:** 50 Eigentumswohnungen, 80–100 m², drei Wiener Neubauquartiere.

## Sofort ausprobieren

```bash
python3 -m src.run                   # die ganze Pipeline, vier Schritte, drei Gates
python3 tests/test_pipeline.py    # 45 Tests: Parser, Umwandlung, Gates, PII, SQL
python3 tests/test_modell.py         # 26 Tests: Wertsicherung, Entscheidungsmodell
```

Kein Netzzugang, keine Zugangsdaten, keine Installation: die Pipeline läuft mit
der Standardbibliothek. `python3 -m src.run` löscht die Datenbank und baut sie
aus `data/raw/` neu — zwei Läufe melden deshalb dieselben Zahlen
(`test_zweiter_lauf_liefert_dieselben_zahlen`).

Der Lauf arbeitet gegen einen echten, eingecheckten Schnappschuss —
90 Mietwohnungsinserate aus 1020 Wien, abgerufen am 25.09.2026 um 15:55.
Kein Netzzugang nötig.

## Die Datenbeschaffung ist eine bewusste Entscheidung

Die willhaben-robots.txt verbietet im Kopfkommentar ausdrücklich jeden
automatisierten Zugriff. Die Datei ist als
`docs/willhaben_robots_2026-09-25.txt` archiviert.

Konsequenz: **ein Mensch speichert die Seite, die Pipeline verarbeitet sie.**
Der Abruf ist ein dokumentierter manueller Schritt, alles danach ist
automatisiert, getestet und über SHA256 rückführbar. Die vollständige
Begründung samt Rechtslage steht in `docs/projektdokumentation/02_schritt1_datenzugriff.md`.

Eine frühere Fassung dieses Projekts ging von einer anderen Rechtslage aus.
Die Korrektur ist dort protokolliert — nachvollziehbare Irrtümer gehören in
die Dokumentation, nicht in den Papierkorb.

## Der Vorfall, der das Gate begründet

Beim Beschaffen entstanden zwei Dateien, beide benannt wie die Suche für
1020 Wien. Nur eine war es:

| Datei | verticalId | rowsFound | Inserate | PLZ |
|---|---|---|---|---|
| `data/raw/2026-09-25/wh_1020_mietwohnungen_2026-09-25T1555.json` | 2 Immobilien | 154 | 90 | alle 1020 |
| `data/sample/negativ_falscher_vertical.json` | 5 Marktplatz | 13.353.029 | 30 | 24 verschiedene |

Die zweite ist syntaktisch einwandfreies JSON derselben Struktur. Ohne
Eingangsprüfung hätte die Pipeline daraus einen Median über Gebrauchtwaren aus
ganz Österreich gerechnet, ohne abzustürzen.

Sie liegt deshalb als **Negativ-Fixture** im Repository und ist Teil der
Testsuite. Das Gate lehnt sie mit vier Begründungen ab.

## Aufbau

```
src/     run.py               die Pipeline: vier Schritte, drei Gates
         extract.py           Schritt 1  data/raw/ -> data/interim/ + Provenienz
         clean.py             Schritt 2  Umwandlung, PII-Allowlist, Kontrolle
         integrate.py         Schritt 3  Datenbank neu bauen und laden
         derive.py            Schritt 4  alle kennzahl_*.sql -> CSV
         wh_next_data.py      __NEXT_DATA__ -> Inserate, drei Speicherwege
         validierung.py       Gate 1: ist das die richtige Seite?
         config.py            Quellen, Allowlist, Bezirke, Schwellen
         wertsicherung.py     gedeckelte Indexierung nach MieWeG
         entscheidung.py      Annahmemodell und Barwertvergleich
         sql/  schema.sql · views.sql · kennzahl_*.sql (eine Frage je Datei)
config/  berufsgruppen.json   7 KV-Reihen mit Unschärfegrad
         portfolio.json       Rechtsrahmen, 11 Annahmen mit Sensitivitätsspanne
data/    raw/<datum>/         Quelle der Wahrheit, unverändert
         interim/             Arbeitskopie mit provenienz.json (SHA256 je Datei)
         processed/           mietportfolio.sqlite + kennzahl_*.csv
         sample/              Negativ-Fixture für die Gates
docs/    projektdokumentation/01_entscheidungslog.md   24 Entscheidungen
         projektdokumentation/02_schritt1_datenzugriff.md
         annahmen.md · willhaben_robots_2026-09-25.txt
CLAUDE.md  Dauerauftrag fuer jede KI-Sitzung in diesem Repository
tests/   test_pipeline.py (32) · test_modell.py (26)
tools/   snapshot.js          selbstprüfendes Beschaffungsskript für die Konsole
```

Noch nicht in diesem Stand: Indexreihen-Loader, Evals, Prompts,
Vorlagengenerator, Dashboard. Von fünf Bezirken ist einer beschafft —
`v_abdeckung` weist die vier anderen als „noch nicht beschafft" aus, statt zu
schweigen.


Noch nicht in diesem Stand: Vertragsgenerator, Indexreihen-Loader,
Vorlagengenerator und das Dashboard. Die Marktseite der Pipeline steht,
die Portfolioseite ist als Modell getestet, aber noch nicht verdrahtet.

## Pipeline und Kontrollpunkte

```
Quellen ─► extract ─► clean ─► GATE 1+2 ─► integrate ─► derive ─► GATE 3 ─► Modell ─► Vorlage
```

| Gate | Prüft | Bei Fehler |
|---|---|---|
| 1 | richtige Seite: Trefferzahl, PLZ-Einheitlichkeit, Feldabdeckung, Fallzahl | Datei wird nicht geschrieben |
| 2 | keine personenbezogenen Daten nach der Allowlist | Datei wird nicht geschrieben |
| 3 | Plausibilität der Kennzahlen: Portal-€/m² gegen eigene Rechnung, Median zwischen Min und Max, jede Beobachtung mit Bezirk | keine Vorlage |
| 4 | *geplant:* LLM-Extraktion gegen Referenzantworten | keine Vorlage |

Die Faktentabelle ist **append-only**: derselbe Inseratsschlüssel erscheint je
Schnappschuss erneut, nichts wird aktualisiert. Preisänderungen und
Inseratsdauer fallen daraus heraus, ohne eigens erhoben zu werden. Die
Inseratsdauer ist zugleich der Schätzer für die Leerstandsannahme im
Entscheidungsmodell — bisher eine Annahme, künftig eine Messung.

## Erste Ergebnisse (1020 Wien, 25.09.2026, aktive Inserate)

| Größenklasse | n | Median €/m² | Q1 | Q3 | Belastbarkeit |
|---|---:|---:|---:|---:|---|
| bis 50 m² | 10 | 33,49 | 25,16 | 41,94 | dünn |
| 50–80 m² | 37 | 24,98 | 21,05 | 33,91 | belastbar |
| **80–100 m²** | **15** | **26,67** | 20,77 | 30,79 | belastbar |
| über 100 m² | 24 | 19,02 | 17,75 | 21,57 | belastbar |

Der Größengradient — kleiner heißt teurer pro m² — ist aus der Literatur
bekannt und spricht dafür, dass wir das richtige Feld lesen.

**Vorbehalt, der ins Ergebnis gehört:** im Zielsegment sind 80 % der Inserate
gewerblich, ein einzelner Anbieter möblierter Kurzzeitwohnungen stellt 17 der
90. Der gewerbliche Median liegt 16 % über dem privaten — bei nur drei
privaten Fällen. Deshalb weist `v_marktniveau` die Fallzahl und
`v_anbieterstruktur` den gewerblichen Anteil je Zeile mit aus.

## Offen

- weitere Abrufe von 1020, damit eine Inseratsdauer messbar wird — zwei
  Abrufe (25.09., 09.10.) zeigen bisher nur, dass 70 % der Inserate nach 14
  Tagen noch stehen
- die übrigen vier Bezirke; 1020 ist seit dem 09.10. vollständig (178 von 178)
- Gemeindewohnungen: nur die ausdrücklich genannten (3 von 178) werden ausgeschlossen, der Rest bleibt unerkannt (E38)
- Reihennamen gegen die amtliche Klassifikation abgleichen

- Referenzantworten für die Evals, wörtlich aus den Quelldokumenten mit Seitenzahl
- Dashboard

## Hinweise

- Keine personenbezogenen Daten. Mieter und Verträge sind synthetisch.
- Der Rechtsrahmen ist nach öffentlichen Zusammenfassungen modelliert und
  stellt keinen Rechtsrat dar.
- Alle Modellparameter mit Sensitivitätsspanne: `docs/annahmen.md`,
  `config/portfolio.json`.