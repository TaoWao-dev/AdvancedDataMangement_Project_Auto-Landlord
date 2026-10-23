# Schritt 5 — Evaluierung und Entscheidungsvorlage

**Frage dieses Schritts:** Werden die Referenzen zu Evals gegen ein Modell,
übersteht die Pipeline Datenänderungen, und schreibt das Modell eine
Vorlage, deren Zahlen aus SQL kommen?

**Abnahmekriterium:** Jede Analyse hat einen Task in der Suite, jeder Task
läuft gegen seine Referenz, und jede Zahl der Vorlage hat eine Herkunft, die
ein Programm prüft. Wo ein Task nicht gelaufen ist, steht das da — als
„nicht gelaufen", nicht als Ergebnis.

## Die Suite

| Task | Analyse | Werkzeug | Fälle | Referenz entstanden durch | Grader |
|---|---|---|---:|---|---|
| `sql` | 1–3 Preisniveau, Anbietertyp, Abdeckung, Inseratsdauer | SQL | 9 | Zweitimplementierungen ohne `src/` und SQL (`nachrechnen_*.py`) | `sql_referenz` |
| `kv_extraktion` | 4 Fortschreibung der Einkommen | Prompt `kv_extraktion_v1` | 8 | Wortlaut der gespeicherten KV-Seiten, Lesung zu bestätigen (E41) | `extraktion` |
| `moebliert` | Bereinigung der Marktmiete (E38) | Prompt `moebliert_v1` | — | Markierung des Studierenden, steht aus | `klassifikation` |
| `vorlage` | 5 Entscheidungsvorlage | Prompt `vorlage_v1` | 2 | Kennzahl-CSV und Gliederung | `zahlen_herkunft`, `vorlage_pflichten` |

Konfiguration: `evals/suite_*.yaml` (promptfoo). Testfälle: `evals/tests/*.json`,
erzeugt aus `evals/references/` durch `evals/baue_tests.py`. Dieselben
Testdateien und Grader führt `evals/lauf.py` ohne Node aus (E42).

**Datenänderung überstanden — als Test, nicht als Behauptung.** Die
Referenzen vom 25.09. laufen gegen eine Pipeline, die inzwischen auch den
Abruf vom 09.10. enthält. `marktniveau` filtert nach Abruftag und läuft auf
dem vollen Datenstand: der neue Abruf lässt die alten Werte unverändert. Die
übrigen Fälle beschreiben ausdrücklich den 25.09.; der SQL-Provider baut
dafür eine Wegwerf-Datenbank nur aus diesem Rohordner. Ohne das Pinnen
meldet er „2 passende Zeilen" statt eine zu wählen. Der neue Fall
`inseratsdauer_zwei_abrufe` prüft den Stand nach der Änderung.

### Was das Modell sieht (Context Engineering)

- **Extraktion:** die ganze gespeicherte ÖGB-Seite (402 Textblöcke, 2026
  bis 2024) und die WKO-Listen, jede Zeile mit ihrer Fundstelle `[Z …]`,
  gelesen aus der Tabelle `kv_textblock`. Bewusst **nicht** vorgefiltert:
  ein Filter, der nur die passenden Absätze durchlässt, würde die
  Extraktion vorwegnehmen, und das Eval würde den Filter messen.
- **Vorlage:** die acht Kennzahl-CSV als Text und die Annahmen aus
  `config/portfolio.json` — sonst nichts. Keine Rohdaten, kein Code.

### Modellwahl

| Rolle | Modell | Warum | Kosten |
|---|---|---|---|
| Extraktion, Klassifikation | **Qwen3 8B**, lokal über LM Studio, gepinnt `qwen/qwen3-8b`, Stand 23.10.2026, Temperatur 0, Seed 20261023 | in der Werkzeugliste der LV, läuft ohne Konto und ohne Datenabfluss; Extraktion aus Fließtext braucht kein großes Modell, und genau das soll die Suite zeigen | 0 € |
| Alternative | `qwen/qwen3-8b:free` über OpenRouter | ohne lokale Hardware; Rate-Limit | 0 € |
| Vorlage v1 | Claude Opus 5.5 in der Arbeitssitzung | heute das einzige erreichbare Modell; offen gekennzeichnet (E43) | im Rahmen des bestehenden Zugangs |

## Ergebnisse

Lauf vom 23.10.2026 mit `python3 evals/lauf.py` in der Arbeitssitzung:

| Task | Trefferquote | davon bestätigte Referenz | Modell | Anfragen | Zeit | Kosten |
|---|---|---|---|---:|---:|---:|
| `sql` | **9/9 (100 %)** | 0 von 9 bestätigt¹ | SQL | 0 | 0,4 s | 0 € |
| `vorlage` | **2/2 (100 %)** | 2/2 | Claude Opus 5.5 (Text), Grader deterministisch | 0² | < 0,1 s | 0 € |
| `kv_extraktion` | **nicht gelaufen** | — | Qwen3 8B nicht erreichbar | 0 | — | — |
| `moebliert` | **nicht gelaufen** | — | Referenz fehlt | 0 | — | — |

¹ Die SQL-Referenzen sind Zweitimplementierungen und tragen
`von_hand_bestaetigt: false`; die drei **Handproben** dazu sind vom
Studierenden am 09.10. bestätigt (`handproben.json`).
² Die Vorlage wurde in der Arbeitssitzung geschrieben; gezählt sind hier nur
Anfragen der Suite. Die Prüfung selbst braucht kein Modell.

**Was diese Zahlen aussagen, und was nicht.** 9/9 heißt: SQL und eine
unabhängige zweite Rechnung kommen auf dieselben Zahlen — auch nachdem neue
Daten dazugekommen sind. 2/2 bei der Vorlage heißt: keine Zahl ohne
Herkunft, alle Pflichtabschnitte da. Es heißt **nicht**, dass die Vorlage
gut ist; drei inhaltliche Fehler des ersten Entwurfs hat der Grader nicht
gefunden (unten). Über das Modell für Extraktion und Klassifikation sagt der
heutige Lauf nichts.

### Der Grader wurde selbst geprüft

- `tests/test_graders.py`, 26 Tests: je Grader, was bestehen muss und was
  scheitern muss — darunter die wahrscheinlichen Modellfehler
  (Vorjahreswert, erfundenes Datum, gleicher Prozentsatz aus dem
  Arbeiter-KV, Forderung statt Abschluss, selbst gerechnete Differenz).
- `evals/gegenprobe_grader.py` baut 7 Fehler in die Grader ein. In der
  ersten Fassung der Tests überlebten 2 von 6; nach dem Nachschärfen werden
  7 von 7 gefangen.
- Die Referenz der Extraktion besteht ihren eigenen Grader in allen 8
  Fällen (`test_referenzantwort_selbst_besteht_jeden_fall`).

## Herkunft jeder Zahl in der Vorlage

`docs/vorlage.md` nennt bei jeder Zahl die Abfrage in eckigen Klammern.
`evals/graders/zahlen_herkunft.py` liest alle 118 Zahlen, ordnet jede einer
Kennzahl-CSV, einer Annahme in `config/portfolio.json` oder einer Konstante
mit Begründung (`evals/graders/vorlage_konstanten.json`) zu und lässt den
Test scheitern, wenn eine übrig bleibt. Steht im selben Absatz ein Zitat,
muss die Zahl aus genau dieser Datei kommen.

| Herkunft | Abfrage | Was in der Vorlage daraus wird |
|---|---|---|
| Marktmiete, Fallzahl, Quartile | `kennzahl_marktniveau`, `kennzahl_bezirksvergleich` | Abschnitt 4, Tabelle Marktmiete |
| privat / gewerblich | `kennzahl_anbietertyp` | Abschnitt 4 |
| Inseratsdauer | `kennzahl_inseratsdauer` | Abschnitt 4 |
| Lücken | `kennzahl_abdeckung`, `kennzahl_empfehlung` | Abschnitte 3, 4 |
| Empfehlung, Barwerte, Optionen | `kennzahl_empfehlung`, `kennzahl_empfehlung_vertrag` | Abschnitte 1, 5, 6 |
| Sensitivität | `kennzahl_sensitivitaet` | Abschnitt 6 |

**Was der Grader nicht fand.** Im ersten Entwurf standen „40 der 50
Wohnungen" (gerechnet, und falsch — es sind 30), eine verdrehte Richtung der
Marktlücke und „fast doppelt" statt „mehr als doppelt". Alle drei fand die
eigene Durchsicht vor dem Commit. Die 40 hatte der Grader als belegt
gewertet, weil sie im Angebotsraster vorkommt; seitdem bindet ein Zitat die
Zahl an die zitierte Datei (E43). Für Zahlen ohne Zitat im Absatz — in v1
sind es 64 von 118 — bleibt „belegt" ein schwacher Beleg.

## Was die Vorlage empfiehlt, und ob das Sinn ergibt

Die Empfehlung — im Nordbahnviertel allen 20 Mietern ein Angebot nahe der
beobachteten Marktmiete — ist plausibel und zugleich das am wenigsten
belastbare Ergebnis des Projekts:

- **Plausibel**, weil die Angebote dort landen, wo der Markt steht, und
  weil ein Vermieter mit Mieten deutlich unter Markt tatsächlich so handeln
  würde. Das Modell bietet nicht mehr als den Markt an, obwohl das Raster es
  erlaubt; die Gegenkräfte (E17) wirken.
- **Wenig belastbar**, weil die Sensitivität zeigt, dass die Empfehlung
  fast vollständig an einer Zahl hängt: Am unteren Quartil der Marktmiete
  schrumpft der mittlere Aufschlag gegen null, am oberen verdoppelt er sich
  mehr als. Die Verhaltensparameter — die eigentlichen Annahmen — ändern
  wenig. Die richtige Investition ist deshalb Messung (Bezirke, Abrufe,
  Bereinigung um möblierte Angebote), nicht Modellverfeinerung.
- **Ein Fehler, der fast durchgegangen wäre:** Die erste Fassung des
  Vertragsbestands hatte Haushalte, die mehr Miete zahlten, als sie
  verdienten. Das Modell rechnete damit klaglos, und Gate 3 bestand. Erst
  der Blick auf die Spalte `belastungsquote` zeigte den Unsinn (E40).

## Selbsttest aus frischem Klon

*Wird nach dem Push des letzten Commits eingetragen.*
