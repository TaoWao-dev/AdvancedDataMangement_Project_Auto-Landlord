# Betriebshandbuch

Stand 23.10.2026. Für wen: wer die Pipeline laufen lässt, neue Daten
einspielt oder die Vorlage erneuert.

## 1 Zweck

Die Pipeline liefert der Leitung Asset Management Wohnen für jeden
laufenden Mietvertrag eine Empfehlung, ob und um wie viel die Miete zu
erhöhen ist — mit Markt- und KV-Entwicklung seit der letzten Erhöhung
(Demo-Fall, E44). Ergebnis: `docs/vorlage.md` und
`docs/demo/mieterverzeichnis.html`, jede Zahl aus `data/processed/kennzahl_*.csv`.

## 2 Starten

```bash
git clone https://github.com/TaoWao-dev/AdvancedDataMangement_Project_Auto-Landlord.git
cd AdvancedDataMangement_Project_Auto-Landlord
python3 -m src.run                 # 4 Schritte, 4 Gates, unter 1 s
python3 -m src.demo                # Mieterverzeichnis mit Empfehlung
python3 tests/test_pipeline.py     # 61 Tests
python3 tests/test_modell.py       # 26 Tests
python3 tests/test_graders.py      # 28 Tests
```

Python ≥ 3.10, nur Standardbibliothek, kein Netz, keine Zugangsdaten.
Erfolg: `GATE 4: bestanden`, `GATE 3: bestanden`, zehn Zeilen `derive:`.

## 3 Neue Daten einspielen

| Was | Schritte |
|---|---|
| Inserate (neuer Abruf oder Bezirk) | Suchseite mit `view-source:` öffnen, speichern → `data/raw_original/<datum>/` → `python3 tools/redigiere_schnappschuss.py <original> data/raw/<datum>/<name>` → neuer Bezirk zusätzlich in `config.BEZIRKE` |
| KV-Seiten | mit `view-source:` speichern → `python3 tools/kv_quellen_aufbereiten.py <datum> <dateien>` → neue Extraktion mit `prompts/kv_zeitreihe_v1.md` als `data/extrakt/kv_erhoehungen_<datum>.json`; Gate 4 prüft sie beim nächsten Lauf |
| Mieterverzeichnis | `tools/erzeuge_vertraege.py` ändern und laufen lassen (nach einem ersten `src.run`); nie von Hand in `config/vertraege.json` |

Danach `python3 -m src.run`, alle Tests, dann committen — Datenbank und
Kennzahl-CSV gehören in den Commit. Originale bleiben in
`data/raw_original/` (gitignored).

## 4 Evals laufen lassen

```bash
python3 evals/baue_tests.py                      # nach jeder Referenzänderung
python3 evals/lauf.py sql kv_extraktion_gespeichert vorlage
# optional, unabhängiger Zweitlauf mit lokalem Modell (LM Studio, qwen/qwen3-8b):
EVAL_MODELL=qwen/qwen3-8b python3 evals/lauf.py kv_extraktion
```

Ergebnisse in
`evals/results/` (lokal); Trefferquote je Task nach
`docs/projektdokumentation/06_schritt5_analyse_vorlage.md`, neue
Prompt-Version nach `prompts/CHANGELOG.md` mit „vorher → nachher".

## 5 Ergebnis lesen

Zuerst `belastbarkeit` und `fallzahl`, dann die Zahl. Eine Zeile mit
„kein Schnappschuss" ist eine Lücke, kein Wert null. `kennzahl_sensitivitaet`
zeigt, an welcher Annahme eine Empfehlung hängt — heute vor allem an der Wechselbereitschaft der Mieter, danach an der Marktmiete.

## 6 Bekannte Schwächen

Jeder neue Datenstand braucht einen Menschen im Browser; Mieter
synthetisch; Marktreihe erst seit 25.09.2026; Marktmiete aus Angeboten;
Extraktion und Referenz vom selben Modell; die Empfehlung hängt an einer
ungemessenen Verhaltensannahme. Vollständig:
`docs/projektdokumentation/07_offene_punkte_lessons.md`.

## 7 Wenn etwas hängt

| Meldung | Ursache | Behebung |
|---|---|---|
| `GATE 1 … verticalId = 5` | Marktplatz statt Immobilien gespeichert | Seite mit `view-source:` neu laden |
| `PLZ wie erwartet: Dateiname sagt …` | veraltetes `__NEXT_DATA__` | dito, nicht durchklicken |
| `GATE 2` bricht ab | Kontaktmuster in einem Feld | Allowlist prüfen — **nicht** das Muster lockern |
| `GATE 4: NICHT BESTANDEN` | ein extrahierter Wert steht nicht im Wortlaut der Quellzeile | Datensatz in `data/extrakt/` prüfen — nie das Gate lockern |
| `GATE 3 … jede Branche mit KV-Reihe` rot | Branche im Verzeichnis ohne geprüfte KV-Reihe | Extraktion ergänzen oder Branche aus dem Verzeichnis nehmen |
| `GATE 3 … Portfolio-Größen in jedem Abruf belastbar` rot | neuer Abruf mit zu wenigen Inseraten einer Größe | Seiten vollständig speichern; sonst `config.PORTFOLIO_GROESSEN` prüfen |
| `GATE 3 … Fixpunkt konvergiert` rot | Modellparameter erzeugen Schwingung | Parameter prüfen; keine Vorlage erzeugen |
| `test_vertragsgenerator_ist_deterministisch` rot | `config/vertraege.json` von Hand geändert | `python3 tools/erzeuge_vertraege.py` |
| Suite: „nicht gelaufen: kein Modell erreichbar" | LM Studio aus | Server starten, Modell laden |
| Suite: „2 passende Zeilen" | Referenz ohne Datenstand | `datenstand` im Testfall setzen |

Weitere Fälle: `docs/troubleshooting.md`.
