# Auftrag

## Das Problem in einem Satz

Ein institutioneller Vermieter muss für 50 befristete Mietverträge, die in den
nächsten zwölf Monaten auslaufen, je Vertrag entscheiden, zu welchem Mietzins er
die Fünfjahresverlängerung anbietet — und tut das derzeit nach Gefühl, weil er
weder das aktuelle Marktniveau in seinen drei Quartieren kennt noch abschätzen
kann, bei welchem Preis der Mieter auszieht.

## Wer entscheidet was, bis wann

| | |
|---|---|
| **Adressat** | Leitung Asset Management Wohnen |
| **Entscheidung** | je auslaufendem Vertrag: Verlängerung zu welchem Mietzins anbieten — oder auslaufen lassen und neu vermieten |
| **Termin** | laufend, jeweils 6 Monate vor Vertragsende; erste Tranche 1. Quartal 2027 |
| **Entscheidungsraum** | das Angebotsraster aus `config/portfolio.json`: Bestandsmiete, gedeckelt indexiert, oder in Schritten darüber bis zur Marktmiete |
| **Was sich ändert** | der Mietzins im Verlängerungsanbot und die Reihenfolge, in der Objekte neu vermietet werden |
| **Wer profitiert** | der Eigentümer; die Belastung trägt der Mieter — das ist die Prämisse, nicht ein Nebeneffekt (siehe unten) |

Es ist eine echte Entscheidung: alle drei Optionen können gewinnen, und welche
gewinnt, hängt an den Daten. Zu hoch angesetzt zieht der Mieter aus, und
Leerstand, Neuvermietungskosten und Marktrisiko fressen den Aufschlag. Zu
niedrig angesetzt verschenkt man fünf Jahre lang die Differenz zum Markt.

## Zweck

Die Entscheidung soll von einer Zahl abhängen, die man prüfen kann, statt von
einer Vermutung über „den Markt". Drei Dinge liefert das Projekt dafür:

1. das beobachtete Preisniveau im Zielsegment je Bezirk, mit Fallzahl und
   Belastbarkeitsstufe statt eines Einzelwerts,
2. die gedeckelte Indexierung nach dem seit 1.1.2026 geltenden Rahmen,
   nachgerechnet statt geschätzt,
3. einen Barwertvergleich, der Annahme- und Ausfallwahrscheinlichkeit des
   Mieters gegen Leerstand und Neuvermietung stellt.

## Die drei Analysen

| Nr | Frage | Werkzeug | Abfrage | Belastbarkeit heute |
|---|---|---|---|---|
| 1 | Was kostet eine Wohnung im Zielsegment 80–100 m² je Bezirk? | SQL | `kennzahl_marktniveau.sql`, `kennzahl_bezirksvergleich.sql` | 1020 am 09.10.: n=32, belastbar, vollständiger Abruf. Vier Bezirke fehlen |
| 2 | Wie unterscheidet sich das Angebot privater und gewerblicher Anbieter? | SQL | `kennzahl_anbietertyp.sql` | 1020 am 09.10.: 12 privat gegen 20 gewerblich — privat dünn, gewerblich belastbar |
| 3 | Wie lange steht ein Inserat, und ändert sich der Preis dabei? | SQL | `kennzahl_inseratsdauer.sql`, `v_preisaenderung` | zwei Abrufe, 14 Tage Abstand: 70 % der Inserate vom 25.09. stehen noch; 10 Preisänderungen, 6 davon Senkungen. Eine Dauer ist noch nicht messbar |

Analyse 3 ist der Schätzer für die Leerstandsannahme im Entscheidungsmodell —
heute eine Annahme von 2,5 Monaten, künftig eine Messung. Mit zwei Abrufen
lässt sich erst sagen, dass ein typisches Inserat länger als zwei Wochen
steht; eine Dauer braucht weitere Abrufe (`kennzahl_inseratsdauer.csv`,
Spalte `befund`).

Die drei Analysen sind reines SQL. Dazu kommen zwei Aufgaben für das
Sprachmodell (Prompt), die keine eigene Kennzahl liefern, sondern die
Analysen stützen — sie stehen in `05_schritt4_abfragen_referenzen.md` als
Nummer 4 und 5: die Extraktion der Kollektivvertragsabschlüsse und die
Formulierung der Entscheidungsvorlage aus der Kennzahltabelle (siehe unten).

## Wo das Sprachmodell arbeitet, und wo nicht

**Nicht:** rechnen. Jede Zahl der Entscheidungsvorlage kommt aus einer
`kennzahl_*.sql` und nennt sie als Herkunft. Auch nicht: personenbezogene Daten
filtern — das macht eine Allowlist im Code (`src/clean.py`), kein Prompt.

**Ja:** die unstrukturierten Quellen. Kollektivvertragsabschlüsse liegen als
Fließtext vor, die Materialien zur gedeckelten Wertsicherung als Gesetzestext.
Daraus Prozentsätze, Geltungsbeginn und Geltungsbereich zu ziehen, ist
Extraktion, und sie wird gegen händisch erfasste Referenzantworten geprüft
(`evals/references/`). Ebenso: die Entscheidungsvorlage formulieren — aus der
Kennzahltabelle, mit einem Eval, das prüft, dass keine Zahl im Text steht, die
nicht in der Tabelle steht.

## Die Prämisse, offen benannt

Das Projekt optimiert den erzielbaren Mietzins eines Vermieters. Das ist
sozialpolitisch unangenehm, und die Projektbeschreibung des Repositorys sagt das
auch so. Für die Arbeit heißt es zwei Dinge:

**Das Einkommen des Mieters ist kein Preisargument.** Es geht nur in
Annahmewahrscheinlichkeit und Ausfallrisiko ein. Ein Mietzins bemisst sich am
Objekt und der vertraglichen Wertsicherung, nicht am Gehalt des Mieters — die
erste Projektfassung hatte das anders und war damit rechtlich nicht
anschlussfähig (Entscheidungslog E05).

**Es werden keine Daten über Personen verwendet.** Mieter und Verträge sind
erfunden. Aus den Inseratsdaten bleibt von der Anbieterseite nur das Flag
privat/gewerblich übrig. Die Vorgabe „keine personenbezogenen Daten" ist damit
nicht knapp erfüllt, sondern mit Abstand.

## Was dieses Projekt nicht kann

- Es sagt nicht, ob der Mieter das Anbot annimmt, sondern mit welcher
  geschätzten Wahrscheinlichkeit — und diese Schätzung ruht auf Parametern ohne
  empirischen Beleg (`docs/annahmen.md`).
- Der Tariflohnindex misst Mindestlöhne nach Kollektivvertrag, nicht Ist-Löhne
  mit Überzahlung. Bei IT-Berufen ist er ein schlechter Schätzer. Der
  Unschärfegrad steht je Berufsgruppe in `config/berufsgruppen.json`.
- Der Rechtsrahmen ist nach öffentlichen Zusammenfassungen modelliert, nicht aus
  dem Gesetzestext, und ist kein Rechtsrat.

## Änderungen seit dem Pitch

| Datum | Änderung |
|---|---|
| 26.09.2026 | Pitch im Gallery Walk. Das Feedback war durchgehend positiv; es kam keine Rückmeldung, die Adressat, Entscheidung oder Analysen in Frage gestellt hätte. |
| 26.09.–09.10.2026 | **Keine Änderungen am Auftrag.** Adressat, Entscheidung und die drei Analysen sind unverändert. Nach dem Pitch fielen zwei Umsetzungsentscheidungen, die den Auftrag nicht ändern, aber festlegen, wie er erfüllt wird: die Zuordnung Programm oder Prompt je Aufgabe (E27) und der Aufschub der Extraktionsreferenzen, bis das Quelldokument gespeichert ist (E28). |
