# Schritt 5 — Evaluierung und Entscheidungsvorlage

**Frage dieses Schritts:** Werden die Referenzen zu Evals gegen ein Modell,
übersteht die Pipeline Datenänderungen, und schreibt das Modell eine
Vorlage, deren Zahlen aus SQL kommen?

**Abnahmekriterium:** Jede Analyse hat einen Task in der Suite, jeder Task
läuft gegen seine Referenz, und jede Zahl der Vorlage hat eine Herkunft, die
ein Programm prüft. Wo ein Task nicht gelaufen ist, steht das da.

**Stand 23.10.2026, abends:** Der Zuschnitt ist auf den Demo-Fall umgestellt
— Empfehlung zur Mietanpassung je laufendem Vertrag (E44). Die Vorlage ist
v2; v1 (Verlängerungsentscheidung) liegt in der Git-Historie.

## Der Demo-Fall in einem Durchlauf

```bash
python3 -m src.run          # 3 Abrufe, KV-Extraktion durch Gate 4, Modell, 10 Kennzahlen
python3 -m src.demo         # Mieterverzeichnis mit Empfehlung, docs/demo/mieterverzeichnis.html
python3 -m src.demo LS-27   # ein Vertrag Schritt für Schritt
```

## Die Suite

| Task | Analyse | Werkzeug | Fälle | Referenz entstanden durch | Grader |
|---|---|---|---:|---|---|
| `sql` | 1–3 Preisniveau, Anbietertyp, Abdeckung, Inseratsdauer | SQL | 9 | Zweitimplementierungen ohne `src/` und SQL | `sql_referenz` |
| `kv_extraktion_gespeichert` | 4 KV-Erhöhungen je Branche | Prompt `kv_zeitreihe_v1`, Ausgabe gespeichert | 7 (5 gewertet), alle bestätigt | Wortlaut der KV-Seiten, Lesung, vom Studierenden bestätigt (E41, E48) | `extraktion` |
| Gate 4 | 4, vor der Datenbank | Programm | 15 Datensätze | Wortlaut der Quellzeile | `src/kv_extrakt.py` |
| `vorlage` | 5 Entscheidungsvorlage | Prompt `vorlage_v2` | 2 | Kennzahl-CSV und Gliederung | `zahlen_herkunft`, `vorlage_pflichten` |
| ~~`moebliert`~~ | Bereinigung der Marktmiete | — | — | entfallen (E46): kein Maßstab, weder Mensch noch Modell entscheiden es sicher | — |

Konfiguration: `evals/suite_*.yaml` (promptfoo); Testfälle `evals/tests/*.json`
aus `evals/references/`; derselbe Ablauf ohne Node: `evals/lauf.py` (E42).

### Was das Modell sieht

- **Extraktion:** die ganze gespeicherte ÖGB-Seite (402 Textblöcke, 2024
  bis 2026, mit Forderungen und Arbeiter-KVs als Ablenker) und die
  WKO-Listen, jede Zeile mit Fundstelle `[Z …]`, aus `kv_textblock`. Nicht
  vorgefiltert — ein Filter würde die Extraktion vorwegnehmen.
- **Vorlage:** die zehn Kennzahl-CSV und die Annahmen aus
  `config/portfolio.json`, sonst nichts.

### Modellwahl

| Rolle | Modell | Warum | Kosten |
|---|---|---|---|
| KV-Extraktion, Vorlage | Claude Opus 5.5 in der Arbeitssitzung, 23.10.2026 | einziges erreichbares Modell; LM Studio ohne unmittelbaren Nutzen (E45) | im bestehenden Zugang |
| Absicherung der Extraktion | **kein Modell**: Gate 4 prüft jeden Datensatz gegen den Wortlaut | eine Halluzination soll nicht vom Urteil eines zweiten Modells abhängen | 0 € |
| vorgesehen, nicht genutzt | Qwen3 8B lokal (LM Studio), gepinnt in `suite_kv_extraktion.yaml` | bleibt als Weg für einen unabhängigen Zweitlauf | 0 € |

## Ergebnisse

Lauf vom 23.10.2026 mit `python3 evals/lauf.py`:

| Task | Trefferquote | Modell | Anfragen | Zeit | Kosten |
|---|---|---|---:|---:|---:|
| `sql` | **9/9 (100 %)** | SQL | 0 | 0,6 s | 0 € |
| Gate 4 | **15/15 Datensätze** an ihrer Quelle | Programm | 0 | < 0,1 s | 0 € |
| `kv_extraktion_gespeichert` | **5/5 gewertete (100 %), alle gegen bestätigte Referenzen**, 2 nicht gewertet | Claude Opus 5.5 (gespeicherte Ausgabe) | 1 Extraktion | < 0,1 s | 0 € |
| `vorlage` v2 | **2/2 (100 %)** — 122 Zahlen mit Herkunft | Claude Opus 5.5 (Text) | 1 Vorlage | < 0,1 s | 0 € |

**Was diese Zahlen aussagen, und was nicht.**

- `sql`: SQL und eine unabhängige Rechnung kommen auf dieselben Zahlen —
  auch nach zwei weiteren Abrufen, die den Datenbestand von 90 auf 442 Beobachtungen gebracht haben.
- `kv_extraktion_gespeichert`: Referenz-Lesung und Extraktion stammen vom
  selben Modell. Seit der Durchsicht des Studierenden am 23.10. sind alle 7
  Referenzfälle bestätigt — ohne Korrektur an einem erwarteten Feld (E48).
  5/5 heißt damit: die Extraktion trifft die vom Menschen bestätigten
  Werte. Unabhängig ist die Bestätigung aber nur so weit, wie der Mensch
  die Quelle selbst gelesen hat. `ist_prozent` fragt der Zeitreihen-Prompt
  nicht ab und ist nicht gewertet; Versicherungen und öffentlicher Dienst
  deckt die Zeitreihe nicht ab. **Mit 7 Fällen ist die Vorgabe von
  mindestens 8 Extraktionsfällen unterschritten** — der achte Fall
  (Wirtschaftstreuhänder) wurde auf Wunsch des Studierenden entfernt.
- Gate 4 belegt, dass keine Zahl erfunden ist. Eine Verwechslung — etwa der
  Arbeiter- statt Angestellten-KV im Handel, gleicher Satz — besteht Gate 4
  (`test_gate4_faengt_keine_verwechslung`).
- `vorlage`: keine Zahl ohne Herkunft, Pflichtabschnitte da. Ob die
  Empfehlung richtig ist, prüft kein Grader (07, Schwäche 3).

**Die Pipeline hat die Datenänderung bemerkt.** Nach dem dritten Abruf
fiel die Vorlage v1 durch: 19 ihrer Zahlen waren vom neuen Datenstand nicht
mehr gedeckt. Das ist der gewünschte Effekt — eine veraltete Vorlage wird
rot, statt still falsch zu bleiben. Fünf Pipeline-Tests brachen ebenfalls,
weil sie Zahlen vom 09.10. fest verdrahtet hatten; sie prüfen jetzt die
Regel, nicht den Datenstand.

### Die Prüfer wurden selbst geprüft

- `tests/test_graders.py` (27 Tests): je Grader, was bestehen und was
  scheitern muss.
- `evals/gegenprobe_grader.py`: 7 eingebaute Fehler, 7 gefangen. In der
  ersten Fassung überlebten 2 von 6.
- Gate 4: 5 Tests, darunter einer für die bekannte Grenze (Verwechslung).
  Ein Test fand einen echten Fehler: „2,5" stand als Zeichenkette in
  „2,55", Gate 4 hätte den falschen Satz durchgelassen (E45).
- Beim Ausbau gefunden: sechs Pipeline-Tests standen hinter dem
  Läuferblock und liefen nie. Seit der Korrektur laufen alle 61.

## Herkunft jeder Zahl in der Vorlage

| Herkunft | Abfrage | in der Vorlage |
|---|---|---|
| Markt je Größe und Abruf | `kennzahl_marktentwicklung` | Abschnitt 4 |
| Inseratsdauer | `kennzahl_inseratsdauer` | Abschnitt 4 |
| KV-Abschlüsse mit Fundstelle | `kennzahl_kv_entwicklung` | Abschnitt 4 |
| Empfehlung je Größenklasse | `kennzahl_empfehlung` | Abschnitte 1, 5, 7 |
| Empfehlung je Vertrag | `kennzahl_empfehlung_vertrag` | Abschnitt 5 |
| Sensitivität | `kennzahl_sensitivitaet` | Abschnitt 6 |

Der Grader fand in v2 drei Dinge, die die eigene Durchsicht nicht sah: eine
PLZ in einer Zeile, die eine Datei ohne PLZ zitiert, und zweimal ein
typografisches Minus, das er als Plus las — Letzteres ein Fehler im Grader,
behoben und als Test festgehalten. Die eigene Durchsicht fand dafür eine
addierte Zahl („29 von 50"), die als Summe nicht aus SQL kommt.

## Was die Vorlage empfiehlt, und ob das Sinn ergibt

- **Plausibel:** Erhöht wird, wo die Miete unter dem Markt liegt, nicht
  erhöht, wo sie darüber liegt; die Größenordnung (Median 6 % bzw. 0 %)
  passt zu Mieten, die nahe am Markt simuliert sind.
- **Nicht belastbar:** Fast alle Empfehlungen ändern sich, wenn die
  ungemessene Wechselbereitschaft am Rand ihrer Spanne liegt. Die
  Marktveränderung „seit letzter Erhöhung" misst für alle Verträge nur die
  Zeit seit dem ersten Abruf.
- **Ein Befund, der nicht beabsichtigt war:** Bei gleicher Wohnung bekommt
  der Haushalt mit höherem Einkommen eine Rasterstufe mehr empfohlen (E47).
  Die Regel „das Einkommen ist kein Preisargument" stand im Code-Kommentar,
  galt aber im Modell nicht vollständig — und der Test dazu hatte den
  Effekt mit seiner Toleranz verdeckt.

## Selbsttest aus frischem Klon

| | |
|---|---|
| **Datum** | 23.10.2026, 19:52 Wiener Zeit |
| **Stand** | Commit `28005bf` auf `main`, frisch von GitHub geklont in ein leeres Verzeichnis |
| **Befolgt** | nur „Sofort ausprobieren" der README, Befehl für Befehl, einschließlich `src.demo` |
| **Dauer** | 8 Sekunden für Klon, Pipeline, Demo, drei Testdateien, Testfallbau und Suite |
| **Ergebnis** | Gates 1–4 bestanden; 61 + 26 + 27 Tests grün; Suite `sql` 9/9, `kv_extraktion_gespeichert` 5/5, `vorlage` 2/2 |
| **Was danach anders war** | nichts: `git status` leer — Datenbank, Kennzahl-CSV, Demo-Seite und Testfälle entstehen byteweise wie im Commit |

**Was gehakt hat — vor dem Selbsttest, beim Bauen:** sechs Tests liefen
nie (hinter dem Läuferblock); fünf Tests brachen am neuen Abruf, weil sie
Zahlen fest verdrahtet hatten; Gate 4 brach in gepinnten Datenständen ohne
KV-Texte ab; Demo und ein SQL-Kommentar behaupteten noch, das Einkommen
wirke nicht auf die Höhe — das widersprach E47 und ist nach dem Selbsttest
korrigiert. Ein erster Selbsttest am Nachmittag (Stand `f30f541`, vor dem
Demo-Fall) lief ebenfalls ohne Haken durch.

**Was dieser Selbsttest nicht zeigt.** Er lief in derselben Arbeitsumgebung
(Linux, Python 3.13), nur in einem anderen Verzeichnis und aus dem
entfernten Stand. Ein Lauf auf dem Rechner des Studierenden steht aus.
