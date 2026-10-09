# Arbeitsanweisung für dieses Repository

Diese Datei ist der Dauerauftrag an jede KI-Sitzung, die in diesem Repository
arbeitet. Sie ist bewusst kurz und verbietet mehr, als sie vorschreibt.

## Worum es geht

Ein institutioneller Vermieter mit 50 Eigentumswohnungen (80–100 m², drei
Wiener Neubauquartiere) muss je auslaufendem Mietvertrag entscheiden: **zu
welchem Mietzins die Fünfjahresverlängerung anbieten — oder auslaufen lassen und
neu vermieten?** Entscheidungsträgerin ist die Leitung Asset Management Wohnen.

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

## Wie man hier arbeitet

```bash
python3 -m src.run                  # die ganze Pipeline: 4 Schritte, 3 Gates
python3 tests/test_pipeline.py      # 32 Tests (pytest-kompatibel, läuft auch ohne)
python3 tests/test_modell.py        # 26 Tests
```

Kein Netz, keine Zugangsdaten, keine Installation — Standardbibliothek. Nach
jeder Änderung an `src/` laufen beide Testdateien, **bevor** committet wird.

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

## Wo was steht

| | |
|---|---|
| Entscheidungen mit Alternativen | `docs/projektdokumentation/01_entscheidungslog.md` |
| Datenzugriff, Rechtslage, Vorfälle | `docs/projektdokumentation/02_schritt1_datenzugriff.md` |
| Modellannahmen mit Sensitivitätsspanne | `docs/annahmen.md`, `config/portfolio.json` |
| Quellen, Allowlist, Bezirke, Schwellen | `src/config.py` — und nur dort |
| eine Frage je Datei, mit Fallstrick im Kopf | `src/sql/kennzahl_*.sql` |

## Arbeitsteilung Programm gegen Prompt

Das Kriterium: **was prüfbar sein muss, gehört in Code; was Sprache ist, gehört
ins Modell.** Die Tabelle je Aufgabe steht im Entscheidungslog unter E27.
Prompts dürfen formulieren und aus Fließtext extrahieren. Sie dürfen nicht
rechnen, nicht filtern, was ein Gate prüfen muss, und keine Zahl erzeugen.

## Was noch fehlt

Indexreihen-Loader, die acht Extraktionsreferenzen samt Quelldokument (E28),
Prompts, Eval-Suite, Vorlagengenerator. Vier von fünf Bezirken sind nicht
beschafft — `v_abdeckung` weist das aus. Das ist der Stand, nicht ein
Versehen.
