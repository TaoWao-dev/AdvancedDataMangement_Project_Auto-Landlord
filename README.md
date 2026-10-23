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

**Lauffähiger Prototyp (23.10.2026, E44):** Für jeden laufenden
Mietvertrag eines fiktiven Portfolios in der Leopoldstadt — soll die Miete
erhöht werden, und um wie viel? Grundlage: wie sich der Markt für Wohnungen
vergleichbarer Größe und der KV-Lohn der Branche des Mieters seit der
letzten Erhöhung entwickelt haben. Der Prototyp ist auf den Bezirk, die
Größen und die Berufsgruppen konkretisiert, für die belastbare Daten
vorliegen; weitere Bezirke oder Berufsgruppen sind eine Datei bzw. ein
geprüfter Extraktionsdatensatz mehr.

**Entscheidungsträger:** Leitung Asset Management Wohnen.
**Portfolio:** 50 Wohnungen in 1020 Wien, 50–80 und 80–100 m², Mieter
synthetisch, mit Branche und drei Lohnzetteln.

## Sofort ausprobieren

```bash
git clone https://github.com/TaoWao-dev/AdvancedDataMangement_Project_Auto-Landlord.git
cd AdvancedDataMangement_Project_Auto-Landlord
python3 -m src.run                  # Pipeline: 4 Schritte, 4 Gates, Modell, 10 Kennzahlen
python3 -m src.demo                 # Mieterverzeichnis mit Empfehlung je Vertrag
python3 -m src.demo LS-27           # ein Vertrag Schritt für Schritt
python3 tests/test_pipeline.py      # 61 Tests: Parser, Gates, PII, SQL, Gate 4, Modell
python3 tests/test_modell.py        # 26 Tests: Wertsicherung, Entscheidungsmodell
python3 tests/test_graders.py       # 28 Tests: die Grader der Eval-Suite
python3 evals/baue_tests.py         # Testfälle und Modellkontext aus den Referenzen
python3 evals/lauf.py sql kv_extraktion_gespeichert vorlage   # Eval-Suite
```

Python 3.10 oder neuer, nur Standardbibliothek: kein Netz, keine
Zugangsdaten, keine Installation. `python3 -m src.run` löscht die Datenbank
und baut sie aus `data/raw/` neu — zwei Läufe ergeben dieselbe Datei
(`test_datenbank_ist_byteweise_reproduzierbar`).

Kein Modell nötig: die KV-Extraktion liegt als geprüfte Modellausgabe in
`data/extrakt/` und geht nur durch Gate 4 (Wortlaut steht in der
Quellzeile) in die Datenbank.

## Das Ergebnis

**[`docs/vorlage.md`](docs/vorlage.md)** — die Entscheidungsvorlage, und
**[`docs/demo/mieterverzeichnis.html`](docs/demo/mieterverzeichnis.html)** —
das Verzeichnis mit Empfehlung je Vertrag. Die Endpräsentation liegt unter
[`docs/vortrag/auto-landlord.pdf`](docs/vortrag/auto-landlord.pdf).
Live-Demo im Browser, ohne Installation:
[![In Colab öffnen](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TaoWao-dev/AdvancedDataMangement_Project_Auto-Landlord/blob/main/docs/demo/auto_landlord_demo.ipynb)
(`docs/demo/auto_landlord_demo.ipynb`). Das Notebook klont das Repo und
startet dieselben Befehle wie die Kommandozeile. Es liest nur die Kennzahlen
und rechnet nichts selbst. Kurz: erhöhen, wo die Miete unter
dem Markt liegt (50–80 m²: 18 von 25 Verträgen, Median 6 %; 80–100 m²: 11
von 25, Median 0 %). Zwei Befunde sind wichtiger als die Zahlen: Die
Empfehlung hängt fast vollständig an einer ungemessenen Annahme über das
Wechselverhalten der Mieter, und bei gleicher Wohnung bekommt der Haushalt
mit höherem Einkommen eine Stufe mehr empfohlen (E47).

Jede Zahl der Vorlage kommt aus `data/processed/kennzahl_*.csv` und nennt
ihre Abfrage; ein Grader prüft das (`evals/graders/zahlen_herkunft.py`).

| Wo | Was |
|---|---|
| [`docs/projektdokumentation/`](docs/projektdokumentation.md) | Auftrag, Entscheidungslog (48 Einträge), Schritte 1–5, die fünf Schwächen und drei Lessons |
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
           kv_extrakt.py     Gate 4: LLM-Extraktion gegen den Wortlaut der Quelle
           modell.py         Schritt 4  Markt + KV seit letzter Erhoehung -> Empfehlung je Vertrag
           demo.py           Mieterverzeichnis mit Empfehlung, Konsole und HTML
           derive.py         Schritt 4  alle kennzahl_*.sql -> CSV
           entscheidung.py   Annahmemodell und Barwertvergleich
           wertsicherung.py  gedeckelte Indexierung
           validierung.py    Gate 1: ist das die richtige Seite?
           config.py         Quellen, Allowlist, Bezirke, Schwellen
           sql/              schema.sql · views.sql · kennzahl_*.sql (eine Frage je Datei)
config/    portfolio.json    Rechtsrahmen, Annahmen mit Sensitivitätsspanne
           berufsgruppen.json, vertraege.json (Mieterverzeichnis, synthetisch)
data/      extrakt/          KV-Erhoehungen aus der LLM-Extraktion (Eingang von Gate 4)
           raw/<datum>/      redigierte Rohdaten + HERKUNFT.md (Quelle der Wahrheit)
           processed/        mietportfolio.sqlite + kennzahl_*.csv
           sample/           Negativ-Fixture für Gate 1
evals/     references/ tests/ graders/ providers/ suite_*.yaml lauf.py
prompts/   kv_zeitreihe_v1.md · kv_extraktion_v1.md · vorlage_v2.md (+ v1) · CHANGELOG.md
tools/     snapshot.js · redigiere_schnappschuss.py · kv_quellen_aufbereiten.py
           quelltext_zu_text.py · erzeuge_vertraege.py
tests/     test_pipeline.py · test_modell.py · test_graders.py
```

## Pipeline und Kontrollpunkte

```
Quellen ─► extract ─► clean ─► GATE 1+2 ─► integrate ─► GATE 4 ─► modell ─► derive ─► GATE 3 ─► Vorlage/Demo ─► Suite
```

| Gate | Prüft | Bei Fehler |
|---|---|---|
| 1 | richtige Seite: Rubrik, Trefferzahl, PLZ, Feldabdeckung | Datei wird nicht aufgenommen |
| 2 | keine personenbezogenen Daten (Allowlist, Kontrollsuche, auch in KV-Texten) | Abbruch |
| 4 | LLM-Extraktion der KV-Abschlüsse: Wortlaut, Zahl und Datum stehen in der Quellzeile | Extraktion geht nicht in die Datenbank |
| 3 | Kennzahlen plausibel; Fixpunkt konvergiert; jeder Vertrag mit Empfehlung auf belastbarem Markt; Portfolio-Größen in jedem Abruf belastbar; jede Branche mit KV-Reihe | keine Vorlage |
| Suite | SQL gegen Zweitimplementierung; Vorlage: jede Zahl mit Herkunft; Modell gegen Referenzen | Befund in `06_schritt5` |

## Stand und Schwächen

Drei Abrufe, ein Bezirk, synthetische Mieter, KV-Extraktion vom Modell der
Arbeitssitzung. Die fünf Schwächen des Projekts — manuelle Beschaffung,
manueller Auslöser, Evals ohne Geschäftslogik, weniger Werkzeuge als
gedacht, und warum automatisiertes Auspressen nicht so einfach ist — stehen
mit Belegen in [`07_offene_punkte_lessons.md`](docs/projektdokumentation/07_offene_punkte_lessons.md).

## Hinweise

- Keine personenbezogenen Daten. Mieter und Verträge sind synthetisch.
- Der Rechtsrahmen ist nach öffentlichen Zusammenfassungen modelliert und
  stellt keinen Rechtsrat dar.
- Alle Modellparameter mit Sensitivitätsspanne: `docs/annahmen.md`,
  `config/portfolio.json`.
