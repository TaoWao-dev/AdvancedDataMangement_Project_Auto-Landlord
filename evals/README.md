# Evals

Jede Analyse wird gegen eine Referenzantwort geprüft, die **vor** dem Modell
existiert. Die Referenzen sind der Maßstab, die Suiten ihre Ausführung, die
Grader die Prüfregel.

```
references/      Maßstab, je Fall mit Herkunft und Unsicherheit
tests/           Testfälle der Suiten, erzeugt aus references/ (baue_tests.py)
kontext/         was das Modell sieht, erzeugt aus Datenbank und Kennzahl-CSV
graders/         Prüfregeln, reines Python, selbst getestet (tests/test_graders.py)
providers/       SQL und Datei als "Modell" für die nicht-sprachlichen Tasks
suite_*.yaml     promptfoo-Konfiguration je Task, Modell gepinnt
lauf.py          dieselbe Suite ohne Node, nur Standardbibliothek
```

## Die Tasks

| Task | Analyse | Werkzeug | Fälle | Referenz | Grader |
|---|---|---|---:|---|---|
| `sql` | 1–3 Preisniveau, Anbietertyp, Abdeckung/Dauer | SQL | 8 | Zweitimplementierung `nachrechnen_marktniveau.py` | `sql_referenz` |
| `kv_extraktion_gespeichert` | 4 KV-Erhöhungen | gespeicherte Ausgabe von **Prompt** `kv_zeitreihe_v1` | 7 (5 gewertet) | Wortlaut der KV-Seiten, vom Studierenden bestätigt (E48) | `extraktion` |
| `kv_extraktion` | 4, Zweitlauf | **Prompt** `kv_extraktion_v1`, lokales Modell (optional) | 8 | dito | `extraktion` |
| ~~`moebliert`~~ | entfallen (E46) | — | — | kein Maßstab | `klassifikation` (bleibt geprüft) |
| `vorlage` | 5 Entscheidungsvorlage | **Prompt** `vorlage_v2` | 2 | Kennzahl-CSV | `zahlen_herkunft`, `vorlage_pflichten` |

Vor der Datenbank prüft **Gate 4** (`src/kv_extrakt.py`) jede extrahierte
KV-Zahl gegen den Wortlaut ihrer Quellzeile — ohne Modell.

## Laufen lassen

```bash
python3 -m src.run                 # Datenbank und Kennzahlen
python3 evals/baue_tests.py        # Testfälle und Kontext aus den Referenzen
python3 evals/lauf.py sql kv_extraktion_gespeichert vorlage
python3 tests/test_graders.py      # Grader gegen eigene Positiv-/Negativfälle
python3 evals/gegenprobe_grader.py # fangen diese Tests eingebaute Fehler?
```

Mit Modell (LM Studio, Qwen3 8B, lokal, kostenlos):

```bash
EVAL_BASE_URL=http://localhost:1234/v1 EVAL_MODELL=qwen/qwen3-8b \
  python3 evals/lauf.py kv_extraktion moebliert
# oder mit promptfoo:
cd evals && npx promptfoo@latest eval -c suite_kv_extraktion.yaml
```

Ergebnisse landen in `evals/results/` und bleiben lokal. Die Zahlen gehören
in `docs/projektdokumentation/06_schritt5_analyse_vorlage.md`, zusammen mit
Modell, Datum, Zeit und Anfragen, und jede neue Prompt-Version in
`prompts/CHANGELOG.md` mit „vorher → nachher".

## Regeln

- Referenzantworten entstehen durch Kopieren aus dem Dokument oder durch
  eine unabhängige Zweitimplementierung, nie aus einer Modellantwort (E02,
  E28, E37). Wo eine Lesung nötig war, steht `von_hand_bestaetigt: false`,
  bis ein Mensch sie geprüft hat; `lauf.py` weist bestätigte und
  unbestätigte Fälle getrennt aus.
- Ein Task, der nicht gelaufen ist, steht als „nicht gelaufen" in der
  Tabelle — nicht als 0 %, und erst recht nicht als geschätzter Wert.
- Eine Referenz darf verlangen, dass **nichts** behauptet wird
  (`inseratsdauer_nicht_messbar`; bei Versicherungen: Datum ja, Prozentsatz nein).
