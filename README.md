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
git clone https://github.com/TaoWao-dev/AdvancedDataMangement_Project_Auto-Landlord.git
cd AdvancedDataMangement_Project_Auto-Landlord
python3 -m src.run                  # Pipeline: 4 Schritte, 3 Gates, Modell, 8 Kennzahlen
python3 tests/test_pipeline.py      # 53 Tests: Parser, Gates, PII, SQL, Modell an den Daten
python3 tests/test_modell.py        # 26 Tests: Wertsicherung, Entscheidungsmodell
python3 tests/test_graders.py       # 26 Tests: die Grader der Eval-Suite
python3 evals/baue_tests.py         # Testfälle und Modellkontext aus den Referenzen
python3 evals/lauf.py sql vorlage   # Eval-Suite ohne Modell
```

Python 3.10 oder neuer, nur Standardbibliothek: kein Netz, keine
Zugangsdaten, keine Installation. `python3 -m src.run` löscht die Datenbank
und baut sie aus `data/raw/` neu — zwei Läufe ergeben dieselbe Datei
(`test_datenbank_ist_byteweise_reproduzierbar`).

Die Modell-Tasks der Suite (Extraktion aus KV-Texten, Titelklassifikation)
brauchen ein lokales Modell — LM Studio mit `qwen/qwen3-8b`, kostenlos:

```bash
EVAL_MODELL=qwen/qwen3-8b python3 evals/lauf.py kv_extraktion moebliert
# oder mit promptfoo:  cd evals && npx promptfoo@latest eval -c suite_kv_extraktion.yaml
```

## Das Ergebnis

**[`docs/vorlage.md`](docs/vorlage.md)** — die Entscheidungsvorlage für die
Leitung Asset Management Wohnen. Kurz: im Nordbahnviertel (1020) allen 20
Mietern die Verlängerung nahe der beobachteten Marktmiete von 24,01 €/m²
anbieten (n = 32, belastbar); für Sonnwendviertel und Seestadt keine
Empfehlung, weil dort keine Marktdaten vorliegen. Die Sensitivität zeigt,
dass die Empfehlung fast vollständig an der Marktmiete hängt.

Jede Zahl der Vorlage kommt aus `data/processed/kennzahl_*.csv` und nennt
ihre Abfrage; ein Grader prüft das (`evals/graders/zahlen_herkunft.py`).

| Wo | Was |
|---|---|
| [`docs/projektdokumentation/`](docs/projektdokumentation.md) | Auftrag, Entscheidungslog (43 Einträge), Schritte 1–5, offene Punkte und Lessons |
| [`docs/betrieb.md`](docs/betrieb.md) | Betriebshandbuch: starten, neue Daten, Evals, Störungen |
| [`evals/README.md`](evals/README.md) | Referenzen, Grader, Suiten |
| [`CLAUDE.md`](CLAUDE.md) | Arbeitsanweisung für jede KI-Sitzung in diesem Repository |

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
src/       run.py            die Pipeline
           extract.py        Schritt 1  data/raw/ -> data/interim/ + Provenienz
           clean.py          Schritt 2  Umwandlung, PII-Allowlist, Kontrolle
           integrate.py      Schritt 3  Datenbank neu bauen und laden
           modell.py         Schritt 4  Marktmiete aus SQL -> Empfehlung je Vertrag
           derive.py         Schritt 4  alle kennzahl_*.sql -> CSV
           entscheidung.py   Annahmemodell und Barwertvergleich
           wertsicherung.py  gedeckelte Indexierung
           validierung.py    Gate 1: ist das die richtige Seite?
           config.py         Quellen, Allowlist, Bezirke, Schwellen
           sql/              schema.sql · views.sql · kennzahl_*.sql (eine Frage je Datei)
config/    portfolio.json    Rechtsrahmen, Annahmen mit Sensitivitätsspanne
           berufsgruppen.json, vertraege.json (synthetisch, erzeugt)
data/      raw/<datum>/      redigierte Rohdaten + HERKUNFT.md (Quelle der Wahrheit)
           processed/        mietportfolio.sqlite + kennzahl_*.csv
           sample/           Negativ-Fixture für Gate 1
evals/     references/ tests/ graders/ providers/ suite_*.yaml lauf.py
prompts/   kv_extraktion_v1.md · moebliert_v1.md · vorlage_v1.md · CHANGELOG.md
tools/     snapshot.js · redigiere_schnappschuss.py · kv_quellen_aufbereiten.py
           quelltext_zu_text.py · erzeuge_vertraege.py
tests/     test_pipeline.py · test_modell.py · test_graders.py
```

## Pipeline und Kontrollpunkte

```
Quellen ─► extract ─► clean ─► GATE 1+2 ─► integrate ─► modell ─► derive ─► GATE 3 ─► Vorlage ─► Suite
```

| Gate | Prüft | Bei Fehler |
|---|---|---|
| 1 | richtige Seite: Rubrik, Trefferzahl, PLZ, Feldabdeckung | Datei wird nicht aufgenommen |
| 2 | keine personenbezogenen Daten (Allowlist, Kontrollsuche, auch in KV-Texten) | Abbruch |
| 3 | Kennzahlen plausibel; Modell konvergiert; keine Empfehlung ohne Marktmiete | keine Vorlage |
| Suite | SQL gegen Zweitimplementierung; Vorlage: jede Zahl mit Herkunft; Modell gegen Referenzen | Befund in `06_schritt5` |

## Stand und Lücken

Ein Bezirk von fünf beschafft, zwei Abrufe, Verträge synthetisch,
Indexreihen nicht geladen, Modelllauf der Extraktion ausstehend. Die
vollständige Liste mit Wirkung und Abhilfe steht in
[`07_offene_punkte_lessons.md`](docs/projektdokumentation/07_offene_punkte_lessons.md).

## Hinweise

- Keine personenbezogenen Daten. Mieter und Verträge sind synthetisch.
- Der Rechtsrahmen ist nach öffentlichen Zusammenfassungen modelliert und
  stellt keinen Rechtsrat dar.
- Alle Modellparameter mit Sensitivitätsspanne: `docs/annahmen.md`,
  `config/portfolio.json`.
