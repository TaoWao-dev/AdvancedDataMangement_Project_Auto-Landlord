# Entscheidungsvorlage: Verlängerungsangebote im Mietportfolio Wien

## 1 Kopf

| | |
|---|---|
| **An** | Leitung Asset Management Wohnen |
| **Entscheidung** | Zu welchem Mietzins wird je auslaufendem Vertrag die Verlängerung um 5 Jahre angeboten — oder wird der Vertrag auslaufen gelassen und neu vermietet? |
| **Bis wann** | je Vertrag 6 Monate vor Vertragsende; erste Tranche im 1. Quartal 2027 (Beginn 01.01.2027) |
| **Empfehlung in einem Satz** | Im Nordbahnviertel allen 20 Mietern die Verlängerung zur beobachteten Marktmiete anbieten (Aufschlag 12 bis 25 %, Median 15 %) — für Sonnwendviertel und Seestadt heute **nicht** entscheiden, sondern zuerst deren Marktmiete erheben. |
| **Datenstand** | Marktdaten 1020 Wien vom 09.10.2026 [kennzahl_bezirksvergleich]; Vorlage vom 23.10.2026 |
| **Wichtigster Vorbehalt** | Die Verträge sind **synthetisch**, die Modellparameter **Annahmen**. Gemessen ist nur die Marktmiete — und an ihr hängt die Empfehlung fast vollständig (Abschnitt 6). |

Jede Zahl in dieser Vorlage nennt in eckigen Klammern die Abfrage, aus der
sie stammt (`src/sql/<name>.sql`, Ergebnis in `data/processed/<name>.csv`),
oder die Annahme in `config/portfolio.json`. Formuliert wurde der Text von
einem Sprachmodell nach `prompts/vorlage_v1.md`; gerechnet hat es nicht. Ein
Prüfprogramm (`evals/graders/zahlen_herkunft.py`) gleicht jede Zahl gegen
die Kennzahltabellen ab.

## 2 Ausgangslage

Das Portfolio umfasst 50 Eigentumswohnungen mit 80 bis 100 m² in 3 Wiener
Neubauquartieren. Die befristeten Mietverträge laufen zwischen Juli 2027 und
Juni 2028 aus. Für jeden Vertrag ist zu entscheiden, ob und zu welchem
Mietzins eine Verlängerung angeboten wird.

Bisher wurde das nach Gefühl entschieden. Zwei Dinge waren unbekannt: das
aktuelle Preisniveau in den eigenen Quartieren und die Frage, bei welchem
Angebot ein Mieter eher auszieht als verlängert. Beides bestimmt, ob ein
Aufschlag Geld bringt oder Leerstand kostet.

Die Entscheidung hat drei Optionen je Vertrag: nur die vertragliche
Wertsicherung weitergeben, einen Aufschlag bis zur Marktmiete anbieten, oder
den Vertrag auslaufen lassen und neu vermieten.

## 3 Wie die Entscheidung vorbereitet wurde

**Gemessen:** die Angebotsmieten im Inseratsportal für 1020 Wien, an zwei
Tagen gespeichert (25.09.2026 und 09.10.2026), zusammen 205 verschiedene
Inserate [kennzahl_inseratsdauer]. Die Seiten wurden von Hand im Browser
gespeichert, weil das Portal automatisierten Abruf untersagt; verarbeitet
werden sie von einer Pipeline mit drei Prüfstufen.

**Nicht gemessen:** Für Favoriten (Sonnwendviertel) und Donaustadt
(Seestadt) gibt es noch keinen Abruf; beide stehen in der Abdeckung als
„fehlt" [kennzahl_abdeckung]. Die Entwicklung der Einkommen nach den
Kollektivvertragsabschlüssen 2026 wird gerade als Modellaufgabe aufgebaut,
ist aber noch nicht in die Rechnung eingeflossen.

**Angenommen:** die Verträge selbst (synthetischer Bestand, siehe Abschnitt
7) und die Verhaltensparameter des Modells — wie schnell Mieter bei einem
Preisunterschied wechseln, wie lange eine Wohnung leer steht, was eine
Neuvermietung kostet. Jede Annahme hat eine Spanne, und Abschnitt 6 zeigt,
welche davon die Empfehlung verändert.

**Gerechnet:** je Vertrag der Barwert über 5 Jahre für jedes Angebot im
Raster von 0 bis 40 % Aufschlag, gewichtet mit der geschätzten
Wahrscheinlichkeit, dass der Mieter annimmt. Weil viele ähnliche Wohnungen
im selben Quartal frei werden können, wird der Leerstand je Quartal so lange
angepasst, bis Angebote und erwartete Auszüge zusammenpassen. Das Verfahren
kam nach 7 Runden zur Ruhe, bei einem Leerstand von rund 3,05 Monaten statt
der angenommenen 2,5 [kennzahl_empfehlung].

## 4 Die entscheidenden Daten

### Marktmiete im Zielsegment 80–100 m², 1020 Wien

| Abruf | Fallzahl | Median €/m² | Q1 | Q3 | Belastbarkeit | Quelle |
|---|---:|---:|---:|---:|---|---|
| 25.09.2026 | 15 | 26,67 | 20,77 | 30,79 | belastbar | [kennzahl_marktniveau] |
| 09.10.2026 | 32 | 24,01 | 19,88 | 29,21 | belastbar | [kennzahl_marktniveau] |

Der Wert vom 09.10.2026 ist der verwendete: Dieser Abruf ist vollständig,
der vom 25.09.2026 war nur die erste von mehreren Ergebnisseiten. Dass der
Median zwischen den beiden Abrufen von 26,67 auf 24,01 €/m² fällt, ist
deshalb kein Marktrückgang, sondern vor allem der Unterschied zwischen
einer Teilseite und dem ganzen Angebot. Es zeigt aber, wie empfindlich die
Zahl auf die Auswahl der Inserate reagiert.

### Wer anbietet

| Abruf | Anbieter | Fallzahl | Median €/m² | Belastbarkeit | Quelle |
|---|---|---:|---:|---|---|
| 09.10.2026 | gewerblich | 20 | 24,9 | belastbar | [kennzahl_anbietertyp] |
| 09.10.2026 | privat | 12 | 22,61 | dünn | [kennzahl_anbietertyp] |

62,5 % der Inserate im Segment sind gewerblich [kennzahl_bezirksvergleich].
Gewerbliche Anbieter — darunter möblierte Kurzzeitwohnungen — liegen höher.
Die Marktmiete von 24,01 €/m² ist damit eher eine Obergrenze dessen, was
ein unmöbliertes Neubauangebot erzielt. Eine Bereinigung um möblierte
Angebote ist vorbereitet (Klassifikation des Inseratstitels), aber noch
nicht gelaufen.

### Wie lange Inserate stehen

Von den Inseraten des ersten Abrufs stehen 70 % zwei Wochen später noch
online; beobachtet ist eine Dauer von höchstens 14 Tagen
[kennzahl_inseratsdauer]. Eine Leerstandsdauer lässt sich daraus noch nicht
messen — 178 Inserate sind beim letzten Abruf noch offen. Belastbar ist nur:
Ein typisches Inserat steht länger als zwei Wochen. Das stützt die Annahme
von 2,5 Monaten Leerstand nicht und widerlegt sie nicht.

### Was nicht gemessen ist

Für die beiden anderen Quartiere — Sonnwendviertel (20 Verträge) und
Seestadt (10 Verträge) — gibt es keine Marktmiete [kennzahl_empfehlung]. Für sie gibt die
Vorlage bewusst **keine** Empfehlung ab. Eine Übertragung des Werts aus
der Leopoldstadt wäre eine Schätzung, keine Messung.

## 5 Optionen und Konsequenzen (Nordbahnviertel, 20 Verträge)

| Option | Barwert 5 Jahre, Summe | Quelle |
|---|---:|---|
| nur Wertsicherung weitergeben (Aufschlag 0) | 2.104.246 € | [kennzahl_empfehlung] |
| alle Verträge auslaufen lassen und neu vermieten | 2.080.265 € | [kennzahl_empfehlung] |
| **Empfehlung: Angebot je Vertrag nach Modell** | **2.251.247 €** | [kennzahl_empfehlung] |

Gegenüber der reinen Wertsicherung bringt die Empfehlung im Erwartungswert
147.001 € mehr, gegenüber dem Auslaufenlassen 170.982 € [kennzahl_empfehlung].

**Was die Empfehlung kostet.** Die Angebote liegen zwischen 23,55 und
24,7 €/m², also an der beobachteten Marktmiete. Die geschätzte
Annahmewahrscheinlichkeit liegt im Mittel bei 48 %; erwartet werden 10,4
Auszüge [kennzahl_empfehlung]. Die Empfehlung nimmt also bewusst in Kauf,
dass etwa die Hälfte der Mieter auszieht — weil die Bestandsmieten so weit
unter dem Markt liegen, dass sich auch eine Neuvermietung mit Leerstand
rechnet. Das ist operativ eine Aufgabe für die Vermarktung im Jahr 2027 und
der Grund, warum der Leerstand im Modell mit der Zahl gleichzeitiger
Auszüge steigt.

**Warum die Aufschläge so verschieden sind.** Sie folgen dem Abstand der
heutigen Miete zum Markt. Beim Vertrag ohne Wertsicherung liegt die
Marktmiete 23 % über der heutigen Miete, angeboten werden 25 % Aufschlag;
bei einem Vertrag mit Wertsicherung, bei dem der Markt nur 11,1 % darüber
liegt, sind es 12 %
[kennzahl_empfehlung_vertrag]. Nur 1 der 20 Verträge hat keine
Wertsicherungsklausel [kennzahl_empfehlung].

**Auslaufen lassen** empfiehlt das Modell bei keinem Vertrag
[kennzahl_empfehlung]: Ein sicherer Auszug ist in jedem Fall schlechter als
ein Angebot nahe am Markt, das der Mieter annehmen oder ablehnen kann.

## 6 Empfehlung und wann sie kippt

**Empfehlung.**

1. Nordbahnviertel: allen 20 Mietern die Verlängerung zum Angebot aus
   `kennzahl_empfehlung_vertrag` anbieten, beginnend mit der Tranche im
   1. Quartal 2027.
2. Sonnwendviertel und Seestadt: keine Entscheidung auf Basis dieser
   Vorlage. Zuerst je einen vollständigen Abruf für 1100 und 1220
   beschaffen.
3. Vor der ersten Tranche einen dritten Abruf für 1020: Er macht die
   Inseratsdauer erstmals messbar und prüft, ob 24,01 €/m² hält.

**Woran die Empfehlung hängt.** Jeder Parameter wurde an den Rand seiner
Spanne gesetzt [kennzahl_sensitivitaet]:

| Parameter | Wert | Angebote geändert (von 20) | mittlerer Aufschlag |
|---|---:|---:|---:|
| Marktmiete = Q1 | 19,88 €/m² | 20 | 0,6 % |
| Marktmiete = Q3 | 29,21 €/m² | 20 | 36,5 % |
| Wechselbereitschaft niedrig | 0,3 | 20 | 20,5 % |
| Marktrisikoabschlag 0 | 0,0 | 17 | 19,3 % |
| Marktrisikoabschlag hoch | 12 % | 16 | 12,7 % |
| Leerstand 1,5 Monate | 1,5 | 4 | 16,5 % |
| Leerstand 4 Monate | 4,0 | 4 | 15,0 % |

Im Basisfall liegt der mittlere Aufschlag bei 15,7 % [kennzahl_sensitivitaet].

Die Lesart ist eindeutig: **Die Empfehlung ist im Wesentlichen eine Aussage
über die Marktmiete.** Liegt der Markt am unteren Quartil, gibt es fast
nichts aufzuschlagen; liegt er am oberen, mehr als doppelt so viel wie
empfohlen. Die Leerstandsannahme dagegen ändert nur 4 von 20 Angeboten. Wer
die Empfehlung absichern will, investiert in bessere Marktdaten — weitere
Abrufe, die Bereinigung um möblierte Angebote —, nicht in die Feinjustierung
der Modellparameter.

Kein Parameter am Rand seiner Spanne führt dazu, dass ein Vertrag besser
ausläuft [kennzahl_sensitivitaet]. Die Richtung „verlängern statt auslaufen"
ist also robust; die Höhe des Angebots ist es nicht.

## 7 Grenzen dieser Vorlage

- **Die Verträge sind synthetisch.** Bestand, Mieten und Haushaltseinkommen
  sind nach festen Annahmen erzeugt (`config/vertraege.json`). Beim Erzeugen
  bestand jeder Haushalt eine Bonitätsprüfung (Bruttomiete höchstens 35 %
  des Nettoeinkommens); dadurch haben 44 der 50 Haushalte ein
  Zweiteinkommen statt der angenommenen 40 %, also 88 %. Das heißt: Die
  Einkommensannahmen passen nicht gut zu diesem Segment.
- **Angebot ist nicht Abschluss.** Die Marktmiete stammt aus Inseraten. Was
  tatsächlich gezahlt wird, liegt darunter; der Abschlag dafür (6 %) ist
  eine Annahme.
- **Ein Bezirk, zwei Tage.** Die Marktmiete beruht auf 32 Inseraten eines
  einzigen Abrufs [kennzahl_bezirksvergleich].
- **Einkommen nicht fortgeschrieben.** Die Haushaltseinkommen stehen auf dem
  Stand bei Vertragsabschluss. Das Modell schätzt die heutige Belastung
  eher zu hoch und bietet eher zu vorsichtig an.
- **Das Einkommen ist kein Preisargument.** Es wirkt im Modell nur auf die
  Wahrscheinlichkeit, dass ein Mieter annimmt, und auf das Ausfallrisiko —
  der Mietzins bemisst sich am Objekt und am Markt. Die Belastung durch
  höhere Mieten tragen die Mieter; das ist die Prämisse dieses Auftrags,
  nicht ein Nebeneffekt.
- **Kein Rechtsrat.** Der Rahmen der gedeckelten Wertsicherung seit
  01.01.2026 ist nach öffentlichen Zusammenfassungen modelliert.
