# Betriebshandbuch

Stand 23.10.2026. Für wen: wer die Pipeline laufen lässt, neue Daten
einspielt oder die Vorlage erneuert.

## 1 Zweck

Die Pipeline liefert der Leitung Asset Management Wohnen je auslaufendem
Mietvertrag ein Verlängerungsangebot, gestützt auf beobachtete Marktmieten.
Ergebnis: `docs/vorlage.md`, jede Zahl aus `data/processed/kennzahl_*.csv`.

## 2 Starten

```bash
git clone https://github.com/TaoWao-dev/AdvancedDataMangement_Project_Auto-Landlord.git
cd AdvancedDataMangement_Project_Auto-Landlord
python3 -m src.run                 # 4 Schritte, 3 Gates, unter 1 s
python3 tests/test_pipeline.py     # 53 Tests
python3 tests/test_modell.py       # 26 Tests
python3 tests/test_graders.py      # 26 Tests
```

Python ≥ 3.10, nur Standardbibliothek, kein Netz, keine Zugangsdaten.
Erfolg: `GATE 3: bestanden`, acht Zeilen `derive:`.

## 3 Neue Daten einspielen

| Was | Schritte |
|---|---|
| Inserate (neuer Abruf oder Bezirk) | Suchseite mit `view-source:` öffnen, speichern → `data/raw_original/<datum>/` → `python3 tools/redigiere_schnappschuss.py <original> data/raw/<datum>/<name>` → neuer Bezirk zusätzlich in `config.BEZIRKE` |
| KV-Seiten | mit `view-source:` speichern → `python3 tools/kv_quellen_aufbereiten.py <datum> <dateien>` |
| Vertragsbestand | `tools/erzeuge_vertraege.py` ändern und laufen lassen; nie von Hand in `config/vertraege.json` |

Danach `python3 -m src.run`, alle Tests, dann committen — Datenbank und
Kennzahl-CSV gehören in den Commit. Originale bleiben in
`data/raw_original/` (gitignored).

## 4 Evals laufen lassen

```bash
python3 evals/baue_tests.py                      # nach jeder Referenzänderung
python3 evals/lauf.py sql vorlage                # ohne Modell
EVAL_MODELL=qwen/qwen3-8b python3 evals/lauf.py kv_extraktion moebliert
# oder: cd evals && npx promptfoo@latest eval -c suite_kv_extraktion.yaml
```

LM Studio mit geladenem `qwen/qwen3-8b` auf Port 1234. Ergebnisse in
`evals/results/` (lokal); Trefferquote je Task nach
`docs/projektdokumentation/06_schritt5_analyse_vorlage.md`, neue
Prompt-Version nach `prompts/CHANGELOG.md` mit „vorher → nachher".

## 5 Ergebnis lesen

Zuerst `belastbarkeit` und `fallzahl`, dann die Zahl. Eine Zeile mit
„kein Schnappschuss" ist eine Lücke, kein Wert null. `kennzahl_sensitivitaet`
zeigt, an welcher Annahme eine Empfehlung hängt — heute an der Marktmiete.

## 6 Bekannte Schwächen

Ein Bezirk von fünf beschafft; Verträge synthetisch; Indexreihen fehlen;
Inseratsdauer nicht messbar; Marktmiete aus Angeboten, nicht Abschlüssen;
Zahlenprüfung der Vorlage für kleine Zahlen ohne Zitat schwach. Vollständig:
`docs/projektdokumentation/07_offene_punkte_lessons.md`.

## 7 Wenn etwas hängt

| Meldung | Ursache | Behebung |
|---|---|---|
| `GATE 1 … verticalId = 5` | Marktplatz statt Immobilien gespeichert | Seite mit `view-source:` neu laden |
| `PLZ wie erwartet: Dateiname sagt …` | veraltetes `__NEXT_DATA__` | dito, nicht durchklicken |
| `GATE 2` bricht ab | Kontaktmuster in einem Feld | Allowlist prüfen — **nicht** das Muster lockern |
| `GATE 3 … Fixpunkt konvergiert` rot | Modellparameter erzeugen Schwingung | Parameter prüfen; keine Vorlage erzeugen |
| `test_vertragsgenerator_ist_deterministisch` rot | `config/vertraege.json` von Hand geändert | `python3 tools/erzeuge_vertraege.py` |
| Suite: „nicht gelaufen: kein Modell erreichbar" | LM Studio aus | Server starten, Modell laden |
| Suite: „2 passende Zeilen" | Referenz ohne Datenstand | `datenstand` im Testfall setzen |

Weitere Fälle: `docs/troubleshooting.md`.
