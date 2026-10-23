# Arbeitsanweisung für dieses Repository

Diese Datei ist der Dauerauftrag an jede KI-Sitzung, die in diesem Repository
arbeitet. Sie ist bewusst kurz und verbietet mehr, als sie vorschreibt.

## Was das ist

Ein institutioneller Vermieter mit 50 vermieteten Wohnungen in der
Leopoldstadt (50–80 und 80–100 m²) will für jeden **laufenden** Mietvertrag
wissen: **die Miete erhöhen oder nicht, und um wie viel?** Grundlage sind
die Marktentwicklung für vergleichbare Größen (willhaben, von Hand
gespeichert) und die KV-Lohnentwicklung der Branche des Mieters (ÖGB/WKO,
von einem Sprachmodell extrahiert, von Gate 4 geprüft). Die Mieter sind
synthetisch. Entscheidungsträgerin ist die Leitung Asset Management Wohnen.
Das ist die Konkretisierung zum lauffähigen Prototyp vom 23.10.2026 (E44);
der Auftrag im Vollausbau (drei Quartiere, Verlängerungsentscheidung) steht
in `00_auftrag.md` und ist durch weitere Daten jederzeit erweiterbar.

Bewertet wird nicht das Modellergebnis, sondern **der Arbeitsprozess und das
Urteil darüber, ob das Modellergebnis Sinn ergibt.** Das ändert die Reihenfolge
der Prioritäten: eine belegte Unsicherheit ist wertvoller als eine glatte Zahl.

## Fünf Regeln, die nicht verhandelbar sind

1. **Keine personenbezogenen Daten. Nirgends.** Nicht in der Datenbank, nicht
   in `data/raw/`, nicht in einem Prompt, nicht in der Git-Historie. Der Filter
   ist eine Allowlist in `config.PII_ERLAUBT` und läuft in `src/clean.py` —
   **nie** in einer Anweisung an ein Sprachmodell. Ein Prompt ist keine
   Zusicherung. Neue Rohdateien gehen vor dem Commit durch
   `tools/redigiere_schnappschuss.py`.
2. **Zahlen kommen aus SQL.** Was in der Entscheidungsvorlage als Zahl steht,
   kommt aus einer `src/sql/kennzahl_*.sql` und nennt sie als Herkunft. Ein
   Sprachmodell formuliert, es rechnet nicht.
3. **Jede Aggregatzeile führt ihre Fallzahl mit.** Ein Median über vier
   Inserate sieht in einer Tabelle aus wie einer über vierzig. Wer eine
   Kennzahl ohne `fallzahl` und `belastbarkeit` weitergibt, schneidet die
   Unsicherheit ab.
4. **Keine kostenpflichtigen Werkzeuge.** Sie bringen in der Bewertung keinen
   Vorteil. Die Werkzeugwahl gehört dokumentiert, nicht optimiert.
5. **Jede Entscheidung mit Alternative sofort ins Entscheidungslog**
   (`docs/projektdokumentation/01_entscheidungslog.md`), nicht am Ende
   rekonstruiert. Wo es keine Alternative gab, war es keine Entscheidung und
   gehört nicht hinein. Jeder Eintrag nennt einen **Revisionspunkt**: woran man
   erkennen würde, dass die Entscheidung falsch war.

## Starten

```bash
python3 -m src.run                  # Pipeline: 4 Schritte, 4 Gates, Modell, 10 Kennzahlen
python3 -m src.demo                 # Mieterverzeichnis mit Empfehlung (+ LS-27 für einen Vertrag)
python3 tests/test_pipeline.py      # 61 Tests (pytest-kompatibel, läuft auch ohne)
python3 tests/test_modell.py        # 26 Tests
python3 tests/test_graders.py       # 28 Tests der Eval-Grader
python3 evals/baue_tests.py && python3 evals/lauf.py sql kv_extraktion_gespeichert vorlage
```

Kein Netz, keine Zugangsdaten, keine Installation — Standardbibliothek. Nach
jeder Änderung an `src/` oder `evals/graders/` laufen alle drei Testdateien,
**bevor** committet wird; nach einer Änderung an einem Grader zusätzlich
`python3 evals/gegenprobe_grader.py`.

`data/raw/` ist die Quelle der Wahrheit. Die Datenbank wird bei jedem Lauf
gelöscht und daraus neu gebaut; sie ist ein Ergebnis und jederzeit verwerfbar.
Deshalb melden zwei Läufe dieselben Zahlen — das ist ein Test, keine Hoffnung.

Ein Bezirk mehr ist **eine Datei mehr** in `data/raw/<datum>/` plus ein Eintrag
in `config.BEZIRKE`. Wer dafür eine View ändern muss, hat etwas falsch gebaut.

## Gewohnheiten, die sich bewährt haben

- **Kommentare begründen, sie beschreiben nicht.** `# Punkt nur dann
  Tausendertrenner, wenn auch ein Komma vorkommt — sonst wird 24.791666 zu
  24791666` ist nützlich. `# Zahl umwandeln` ist es nicht.
- **Lücken sichtbar machen statt füllen.** Ein Bezirk ohne Schnappschuss
  erscheint als „kein Schnappschuss", nicht als geschätzter Wert. Eine leere
  Kennzahl-CSV behält ihre Kopfzeile.
- **Fehler gehören in die Dokumentation, nicht in den Papierkorb.** Vier
  Irrtümer dieses Projekts sind im Entscheidungslog protokolliert, samt Ursache.
  Das ist Teil der Bewertung, nicht ein Schönheitsfehler.
- **Prüfungen, die man einschalten muss, sind an dem Tag aus, an dem sie
  gebraucht werden.** Gates laufen immer.
- **Bei Zweifel an einer Feldbedeutung: eine Kreuzprobe schreiben.** Dass
  `PRICE / ESTATE_SIZE` das vom Portal gelieferte `PRICE/SQUARE_METER` ergibt,
  ist ein Test — und er würde eine stille Bedeutungsänderung fangen.
- **Deutsch.** Code, Kommentare, Dokumentation und Commit-Nachrichten. ASCII in
  Code und Commit-Nachrichten (`ue` statt `ü`), Umlaute in Markdown.

## Commits

Eine abgeschlossene Arbeitseinheit, eine Festschreibung. Die Nachricht sagt in
der ersten Zeile **was**, im Rumpf **warum** — und bei einer Korrektur, was
schiefgegangen war. Commits nur zu Abgabeterminen wären wieder eine
rekonstruierte Historie.

Autor ist der Studierende, Claude steht als `Co-Authored-By` in der
Nachricht (E31). Wer was entschieden hat, steht im Entscheidungslog, nicht in
der Autorenzeile.

Abgabemarkierungen: `termin3` (Schritte 1–4, 9.10.), `termin4` (Schritt 5,
23.10.).

## Wo was liegt

| | |
|---|---|
| Entscheidungen mit Alternativen | `docs/projektdokumentation/01_entscheidungslog.md` |
| Datenzugriff, Rechtslage, Vorfälle | `docs/projektdokumentation/02_schritt1_datenzugriff.md` |
| Evals, Ergebnisse, Selbsttest | `docs/projektdokumentation/06_schritt5_analyse_vorlage.md` |
| Lücken, Risiken, Lessons | `docs/projektdokumentation/07_offene_punkte_lessons.md` |
| die Entscheidungsvorlage | `docs/vorlage.md` |
| Modellannahmen mit Sensitivitätsspanne | `docs/annahmen.md`, `config/portfolio.json` |
| Quellen, Allowlist, Bezirke, Schwellen | `src/config.py` — und nur dort |
| synthetisches Mieterverzeichnis | `config/vertraege.json`, erzeugt von `tools/erzeuge_vertraege.py` |
| KV-Extraktion (LLM-Ausgabe) und Gate 4 | `data/extrakt/`, `src/kv_extrakt.py` |
| Demo | `src/demo.py`, `docs/demo/mieterverzeichnis.html`, Colab-Notebook `docs/demo/auto_landlord_demo.ipynb` (nur Anzeige) |
| Endpräsentation (12 Folien, ca. 11 min) | `docs/vortrag/auto-landlord.pdf` |
| Vorbereitung auf Live-Fragen | `docs/interview_prompt.md` |
| eine Frage je Datei, mit Fallstrick im Kopf | `src/sql/kennzahl_*.sql` |
| Referenzen, Testfälle, Grader, Suiten | `evals/` (siehe `evals/README.md`) |
| Prompts, versioniert | `prompts/<aufgabe>_v<n>.md`, `prompts/CHANGELOG.md` |
| Rohdaten (redigiert) und Herkunft | `data/raw/<datum>/`, je Ordner `HERKUNFT.md` |

## Datenmodell

SQLite, `data/processed/mietportfolio.sqlite`, bei jedem Lauf neu gebaut
und byteweise reproduzierbar (E15, E26). Schema in `src/sql/schema.sql`.

| Tabelle | Schlüssel | Inhalt |
|---|---|---|
| `bezirk` | `plz` | Bezirke und Cluster aus `config.BEZIRKE` |
| `snapshot` | `snapshot_id`, `sha256` unique | eine gespeicherte Seite |
| `inserat_beobachtung` | `(snapshot_id, ad_id)` | Fakten, append-only (E13) |
| `kv_textblock` | `(datei, block_nr)` | KV-Seiten, je Block mit Originalzeile |
| `kv_erhoehung` | `(branche_id, jahr)` | KV-Abschlüsse aus der LLM-Extraktion, nur nach Gate 4 |
| `vertrag` | `vertrag_id` | Mieterverzeichnis: Größe, Branche, drei Lohnzettel, letzte Anpassung (A10) |
| `modelllauf` | `segment` | Marktmiete, Belastbarkeit, Konvergenz je Größenklasse |
| `empfehlung` | `vertrag_id` | Markt- und KV-Entwicklung seit letzter Anpassung, Empfehlung, Barwerte |
| `empfehlung_sensitivitaet` | `(vertrag_id, parameter, rand)` | Empfehlung am Rand jeder Annahme |
| `indexreihe` | `(reihe, jahr)` | VPI, Tariflohnindex — noch leer |
| `qs_befund`, `zuordnungsluecke`, `objekttyp_ausschluss` | — | Protokoll: was auffiel, was keinen Partner fand, was mit Grund ausgeschlossen ist |

Views (`src/sql/views.sql`) gruppieren nach PLZ; ein Abruf ist alle Seiten
einer PLZ an einem Tag (`v_abruf`, E32). Die Kennzahl-Abfragen lesen nur
Views und Ergebnistabellen.

## Arbeitsteilung Programm gegen Prompt

Das Kriterium: **was prüfbar sein muss, gehört in Code; was Sprache ist, gehört
ins Modell.** Die Tabelle je Aufgabe steht im Entscheidungslog unter E27.
Prompts dürfen formulieren und aus Fließtext extrahieren. Sie dürfen nicht
rechnen, nicht filtern, was ein Gate prüfen muss, und keine Zahl erzeugen.

## Regeln für Evals und Prompts

- Eine Referenz entsteht vor dem Modell, aus dem Dokument oder einer
  Zweitimplementierung — nie aus einer Modellantwort. Was eine Lesung
  braucht, steht auf `von_hand_bestaetigt: false`, bis ein Mensch es
  bestätigt (E28, E37, E41).
- Neue Prompt-Version = neue Datei (`_v2.md`), alte bleibt; eine Zeile im
  Changelog mit Suite vorher → nachher.
- Ein nicht gelaufener Task heißt „nicht gelaufen", nicht 0 %.
- Ein Grader ist erst geprüft, wenn ein eingebauter Fehler ihn rot macht
  (`evals/gegenprobe_grader.py`).

## Neue Daten — immer mit einem Menschen

Willhaben- und KV-Seiten speichert ein Mensch über `view-source:`. Danach:
Inserate durch `tools/redigiere_schnappschuss.py`, KV-Seiten durch
`tools/kv_quellen_aufbereiten.py`; eine neue KV-Extraktion als neue Datei
in `data/extrakt/` — sie geht nur durch Gate 4 in die Datenbank. Nach neuen
Daten `tools/erzeuge_vertraege.py` nur, wenn sich das Verzeichnis ändern soll.

## Was noch fehlt

Eine längere Marktreihe, echte Einkommensniveaus, ein zweites Modell für die
Extraktion. Vollständig, mit
den fünf Schwächen des Projekts, in `07_offene_punkte_lessons.md`.
