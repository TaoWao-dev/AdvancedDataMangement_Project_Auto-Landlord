# Schritt 4 — Abfragen und Referenzantworten

**Frage dieses Schritts:** die Kennzahlen als SQL, und für jede Analyse eine
Referenzantwort, die **vor** dem Modell existiert.

**Abnahmekriterium:** für jede Analyse steht, woran erkannt wird, ob das Modell
recht hat — und kein Modell ist dafür gelaufen. Das ist der Stand dieses
Dokuments: es sind noch keine Modellergebnisse darin, und das ist Absicht.

## Je Analyse: Werkzeug, Referenz, Prüfregel

| # | Analyse | Werkzeug | Referenz | Herkunft der Referenz | Prüfregel | Toleranz |
|---|---|---|---|---|---|---|
| 1 | Preisniveau je Bezirk und Größenklasse | **SQL** — `kennzahl_marktniveau.sql`, `kennzahl_bezirksvergleich.sql` | `evals/references/marktniveau.json`, 4 Fälle à 9 Felder | Zweitimplementierung `evals/nachrechnen_marktniveau.py`, 9.10.2026 — liest die Rohdatei ohne `src/` und ohne SQL | numerischer Vergleich je Feld | 0,01 €/m² bei Median und Quartilen, 0 bei Fallzahlen |
| 2 | Unterschied privat gegen gewerblich | **SQL** — `kennzahl_anbietertyp.sql` | `evals/references/anbietertyp.json`, 2 Fälle | wie 1 | numerischer Vergleich | 0,01 €/m², 0 bei Fallzahl |
| 3 | Inseratsdauer und Preisänderung | **SQL** — `kennzahl_inseratsdauer.sql`, `v_preisaenderung` | `evals/references/abdeckung_und_dauer.json`, Fall `inseratsdauer_nicht_messbar` | wie 1 | exakter Vergleich | — |
| 4 | Fortschreibung der Einkommen je Berufsgruppe | **Prompt** — Extraktion aus Kollektivvertragstexten | `evals/references/kv_extraktion.json` | **noch nicht erfasst**, siehe unten | Feldvergleich mit Teilpunkten | Prozentsatz exakt, Datum exakt |
| 5 | Entscheidungsvorlage formulieren | **Prompt**, Zahlen aus 1–3 | Prüfung gegen die Kennzahltabelle, nicht gegen einen Text | — | Judge: keine Zahl im Text, die nicht in der Tabelle steht | 0 |

Die Analysen 1 bis 3 sind reines SQL. Analyse 4 ist der eigentliche
Modellanteil, Analyse 5 der Formulierungsanteil. Rechnen tut das Modell in
keinem Fall.

## Die drei Handproben

Die Vorgabe verlangt, drei Werte je Abfrage **von Hand** nachzurechnen. Die
Zweitimplementierung ist das nicht — sie ist eine unabhängige
Programmimplementierung, und zwei Programme können denselben Denkfehler teilen.
Die drei Werte stehen deshalb einzeln in `evals/references/handproben.json`,
jeder mit der Rechnung, die man in einen Taschenrechner tippt:

| Rolle | Inserat | Rechnung | Erwartet |
|---|---|---|---|
| Median | `808118316` | 2400,00 / 90,00 | 26,6667 €/m² |
| Q1 | `1606747239` | 1745,00 / 84,00 | 20,7738 €/m² |
| Q3 | `1729042096` | 2525,00 / 82,00 | 30,7927 €/m² |

**Bestätigt am 9.10.2026.** Der Studierende hat alle drei Divisionen mit dem
Taschenrechner nachgerechnet und kam auf 26,66666666666667, 20,77380952380952
und 30,79268292682927 €/m² — übereinstimmend mit der Referenz. Seine Werte
stehen als `handwert` in `handproben.json`, eingetragen über
`HANDPROBEN_BESTAETIGT` im Skript, nicht von Hand in der JSON.

`von_hand_bestaetigt` wird nur `true`, wenn der eingetragene Handwert zum
heute berechneten Wert passt. Ändert sich die Rohdatei oder die Auswahl des
Median-Inserats, fällt die Bestätigung beim nächsten Lauf von selbst weg,
statt auf einem anderen Inserat stehen zu bleiben.

Was die Handprobe nicht abdeckt: dass Miete und Fläche in der Spalte
„Rechnung" wirklich die Werte der Rohdatei sind. Das prüfen die
Zweitimplementierung und `test_eur_pro_m2_des_portals_stimmt_mit_eigener_rechnung`.

## Wo „richtig" unsicher ist

**Die Quartile sind definitionsabhängig.** Die Views verwenden die Rangformel
`r = (n+3)/4` beziehungsweise `(3n+3)/4`, nicht lineare Interpolation. Bei
n = 15 liefert ein Statistikprogramm mit anderer Konvention leicht andere
Quartile. Gegen diese Referenz zu prüfen heißt deshalb: die Definition der View
zu prüfen, nicht „das Quartil an sich". Das steht als `unsicherheit` an jedem
Fall dran.

**Der private Median im Zielsegment ruht auf drei Fällen.** Er steht nicht in
der Referenz, weil er belastbar wäre, sondern weil die **Differenz** zwischen
den Anbietertypen der Befund ist: der gewerbliche Median liegt 16 % über dem
privaten, und ein einzelner Anbieter möblierter Kurzzeitwohnungen stellt 17 der
90 Inserate. Wer den Gesamtmedian als Marktmiete nimmt, überschätzt sie.

**Fall 3 erwartet ausdrücklich ein Nicht-Ergebnis.** Mit einem einzigen
Schnappschuss ist jede Inseratsdauer null Tage und zensiert. Der Fall ist
bestanden, wenn die Abfrage die Unauswertbarkeit meldet (`anteil_zensiert` = 1,
`auswertbar` = false) — und nicht, wenn sie eine Dauer von null Tagen als
Messwert ausgibt. Eine Referenz darf verlangen, dass nichts behauptet wird.

**Die Referenz selbst steht auf einer Teilseite.** 90 von 154 Treffern. Sie ist
korrekt für die gespeicherte Seite und falsch für „den Markt in 1020". Jede
Zeile trägt `abruf_datum`, damit das nicht verloren geht.

## Analyse 4: was fehlt, und warum es nicht geschätzt wird

Für die Extraktion verlangt die Vorgabe mindestens acht Fälle. Die Fälle sind
festgelegt — es sind die sieben Berufsgruppen aus `config/berufsgruppen.json`
plus der öffentliche Dienst als Vergleichsreihe:

| Fall | Kollektivvertragsreihe | Zu extrahieren |
|---|---|---|
| 1 | Banken und Bankiers | Prozentsatz, Geltungsbeginn, Bezugsgröße (KV-Mindestlohn oder Ist-Lohn), Deckelung |
| 2 | Versicherungsunternehmungen/Innendienst | dito |
| 3 | Fachverband Unternehmensberatung, Buchhaltung und IT | dito |
| 4 | Elektro- u. Elektronikindustrie | dito |
| 5 | Handelsangestellte Allgemeiner Groß- und Kleinhandel | dito |
| 6 | Privatkrankenanstalten / konfessionelle Einrichtungen | dito |
| 7 | Wirtschaftstreuhänder | dito |
| 8 | Öffentlicher Dienst (Vergleichsreihe) | dito |

**Was fehlt, ist das Quelldokument.** Die Abschlüsse stehen auf öffentlichen
Seiten von ÖGB und WKO. Mein eigener Zugriff darauf liefert eine
**Zusammenfassung durch ein Sprachmodell**, nicht den Wortlaut der Seite — und
eine Referenzantwort aus einer Modellzusammenfassung zu bilden heißt, das
Modell gegen sich selbst zu prüfen.

Genau dieser Fehler ist in einer früheren Projektfassung passiert
(Entscheidungslog E02): das Goldset enthielt Texte, die aus Suchtreffer-
Ausschnitten rekonstruiert waren, und das Eval maß die eigene Formulierung.
Die Trefferquote sah gut aus und bedeutete nichts.

Konsequenz, und sie ist dieselbe wie bei den Inseratsdaten: **ein Mensch
speichert die Seite, die Pipeline verarbeitet sie.** Danach werden die acht
Fälle wörtlich aus dem gespeicherten Dokument erfasst, mit Fundstelle. Bis
dahin steht `evals/references/kv_extraktion.json` nicht im Repository — eine
leere Referenzdatei mit Platzhaltern wäre schlechter als keine, weil sie
aussieht wie Arbeit.

Die Beschaffungsanleitung steht in `evals/references/README.md`. Sie gehört zu
Deliverable 3; der Termin dafür ist der 23.10.

## Was die Abfragen selbst dokumentieren

Jede `kennzahl_*.sql` trägt im Kopf drei Dinge: die Frage, die sie beantwortet,
den Pfad ihrer Referenzantwort und den Fallstrick beim Lesen des Ergebnisses.
Beispiele:

- `kennzahl_marktniveau.sql`: „`belastbarkeit` zuerst lesen. Eine Zeile mit
  `nicht belastbar` ist kein Marktpreis."
- `kennzahl_inseratsdauer.sql`: „`anteil_zensiert` nahe 1 heißt: unbrauchbar.
  Jedes Inserat im jüngsten Schnappschuss seiner PLZ ist noch offen, seine
  Dauer ist eine Untergrenze."

Der Grund für den Fallstrick-Kommentar: die CSV wird später einem Sprachmodell
vorgelegt, das daraus Prosa macht. Wer die Tabelle blind zitiert, zitiert
Unsinn — und der Hinweis steht dort, wo er gelesen wird.

## Prüfung als Test, nicht als Behauptung

`test_kennzahlen_stimmen_mit_den_referenzantworten` liest
`evals/references/marktniveau.json`, baut die Datenbank und vergleicht Feld für
Feld: 36 Einzelvergleiche. `test_referenzen_tragen_herkunft_und_unsicherheit`
prüft, dass jeder Fall Eingabe, erwartete Antwort, Prüfregel, Herkunft (wer,
wann) und Unsicherheit trägt — eine Referenz ohne Herkunft ist eine Behauptung.
