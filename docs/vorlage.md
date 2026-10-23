# Entscheidungsvorlage: Mietanpassung im Portfolio Leopoldstadt (Demo-Fall)

## 1 Kopf

| | |
|---|---|
| **An** | Leitung Asset Management Wohnen |
| **Entscheidung** | Für jeden laufenden Mietvertrag: Miete erhöhen oder nicht, und um wie viel? |
| **Bis wann** | laufend, im Takt der 14-tägigen Marktwertkontrolle; nächster Abruf vor der nächsten Anpassungsrunde |
| **Empfehlung in einem Satz** | Eine Erhöhung anbieten, wo die Miete unter dem Markt liegt — in der Klasse 50–80 m² bei 18 von 25 Verträgen (Median 6 %), in der Klasse 80–100 m² bei 11 von 25 (Median 0 %) [kennzahl_empfehlung] —, sonst nicht erhöhen. |
| **Datenstand** | Marktdaten Leopoldstadt vom 23.10.2026 [kennzahl_empfehlung]; KV-Abschlüsse vom 23.10.2026 [kennzahl_kv_entwicklung] |
| **Wichtigster Vorbehalt** | Die Mieter sind **synthetisch**, das Verhaltensmodell beruht auf **Annahmen**, und der Markt ist erst seit drei Abrufen beobachtet. Die Empfehlung zeigt den Mechanismus, sie ist kein Budget. |

Jede Zahl nennt in eckigen Klammern die Abfrage (`src/sql/<name>.sql`,
Ergebnis in `data/processed/<name>.csv`). Formuliert hat ein Sprachmodell
nach `prompts/vorlage_v2.md`; gerechnet hat es nicht. Ein Prüfprogramm
gleicht jede Zahl gegen die Tabellen ab. Das ganze Verzeichnis:
`python3 -m src.demo` und `docs/demo/mieterverzeichnis.html`.

## 2 Ausgangslage

Das Portfolio umfasst 50 vermietete Eigentumswohnungen in der Leopoldstadt.
Bei jedem Vertrag stellt sich die Frage, ob die Miete erhöht werden kann,
ohne den Mieter zu verlieren. Zwei Dinge sollen das beantworten: wie sich der
Markt für vergleichbar große Wohnungen seit der letzten Erhöhung entwickelt
hat, und wie sich der Kollektivvertragslohn in der Branche des Mieters
entwickelt hat.

## 3 Wie die Entscheidung vorbereitet wurde

**Gemessen:** die Angebotsmieten der Leopoldstadt an drei Tagen im Abstand
von zwei Wochen, insgesamt 285 verschiedene Inserate
[kennzahl_inseratsdauer]. Die Seiten hat ein Mensch im Browser gespeichert;
das Portal untersagt automatisierten Abruf.

**Extrahiert:** die KV-Abschlüsse 2024 bis 2026 für fünf Branchen aus den
Seiten von ÖGB und WKO, die ebenfalls von Hand gespeichert wurden. Ein
Sprachmodell hat die Zahlen herausgelesen; ein Programm hat jede davon
gegen den Wortlaut der Quellzeile geprüft, bevor sie verwendet wurde.

**Simuliert:** das Mieterverzeichnis — Wohnung, Miete, letzte Erhöhung,
Branche, drei Lohnzettel vor Vertragsabschluss.

**Gerechnet:** für jeden Vertrag der erwartete Ertrag über 5 Jahre bei
jedem Erhöhungsschritt von 0 bis 40 %, gewichtet mit der Wahrscheinlichkeit,
dass der Mieter bleibt. Gewählt wird der Schritt mit dem höchsten
Erwartungswert.

## 4 Die entscheidenden Daten

### Markt für vergleichbare Wohnungen

| Größenklasse | Abruf | Fallzahl | Median €/m² | Belastbarkeit | seit erstem Abruf | Quelle |
|---|---|---:|---:|---|---:|---|
| 50–80 m² | 25.09.2026 | 37 | 24,98 | belastbar | — | [kennzahl_marktentwicklung] |
| 50–80 m² | 23.10.2026 | 64 | 24,25 | belastbar | −2,9 % | [kennzahl_marktentwicklung] |
| 80–100 m² | 25.09.2026 | 15 | 26,67 | belastbar | — | [kennzahl_marktentwicklung] |
| 80–100 m² | 23.10.2026 | 33 | 23,86 | belastbar | −10,5 % | [kennzahl_marktentwicklung] |

Zwei Einschränkungen gehören direkt zu diesen Zahlen. Der erste Abruf war
nur die erste Ergebnisseite; der Rückgang bei 80–100 m² ist zum großen Teil
der Unterschied zwischen dieser Teilseite und dem vollständigen Angebot,
nicht ein fallender Markt. Und **alle** letzten Mieterhöhungen im
Verzeichnis liegen vor dem ersten Abruf [kennzahl_empfehlung]: Die Frage
„wie hat sich der Markt seit der letzten Erhöhung bewegt" lässt sich heute
nur für die Zeit seit dem 25.09.2026 beantworten.

Ein Inserat steht im Mittel 14 Tage, beobachtet bis zu 28 Tage; 46 % der
älteren Inserate sind beim letzten Abruf noch online
[kennzahl_inseratsdauer].

### KV-Lohn je Branche

| Branche | 2024 | 2025 | 2026 | Quelle |
|---|---:|---:|---:|---|
| Banken | 7,25 % | 3 % | 3 % | [kennzahl_kv_entwicklung] |
| IT | 7,8 % | 3,2 % | 2,9 % | [kennzahl_kv_entwicklung] |
| Elektroindustrie | 7,5 % | 3 % | 3 % | [kennzahl_kv_entwicklung] |
| Handelsangestellte | 8,43 % | 3,3 % | 2,55 % | [kennzahl_kv_entwicklung] |
| Privatkrankenanstalten | 9,15 % | 2,7 % | 3 % bis 3.750 € | [kennzahl_kv_entwicklung] |

Bei IT 2026 ist der Satz die Mitte einer Staffel, beim Handel 2024 der
Durchschnitt, den die Quelle selbst nennt. Wo die Quelle keinen Tag nennt
(Elektroindustrie und Handel 2024 und 2025), wird ab 1. Jänner gerechnet.
Der KV-Lohn ist ein Mindestlohn; was Mieter tatsächlich verdienen, kann
stärker steigen.

## 5 Optionen und Konsequenzen

| Größenklasse | Verträge | erhöhen | nicht erhöhen | Median | höchste | Ertrag 5 J. mit Empfehlung | ohne Erhöhung | Quelle |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 50–80 m² | 25 | 18 | 7 | 6 % | 12 % | 2.114.466 € | 2.081.879 € | [kennzahl_empfehlung] |
| 80–100 m² | 25 | 11 | 14 | 0 % | 6 % | 2.772.252 € | 2.765.974 € | [kennzahl_empfehlung] |

Der Mehrertrag gegenüber „nirgends erhöhen" liegt bei 32.587 € bzw.
6.278 € über 5 Jahre [kennzahl_empfehlung]. Das ist wenig, weil die
simulierten Mieten nahe am Markt liegen; erhöht wird dort, wo eine Miete
deutlich darunter liegt.

**Was das für einzelne Mieter heißt.** Bei einer Handelsangestellten
(Vertrag LS-45) liegt der Markt 12,8 % über ihrer Miete; empfohlen werden
12 %, ihre Mietbelastung stiege von 35,3 % auf 39,1 % des
Haushaltsnettos, und sie nimmt nur zu 46 % an [kennzahl_empfehlung_vertrag].
Bei einer Bankangestellten (Vertrag LS-29) liegt der Markt nur 9,7 % über
ihrer Miete; empfohlen werden ebenfalls 12 %, ihre Belastung stiege von 15 %
auf 16,6 %, und sie nimmt zu 60 % an [kennzahl_empfehlung_vertrag].

Das ist der wichtigste Befund dieser Vorlage: **Das Einkommen wirkt doch auf
die Höhe.** Das Modell soll das Einkommen nur für die Frage nutzen, ob ein
Mieter annimmt. Weil aber ein Mieter mit hohem Einkommen eher annimmt, lohnt
sich bei ihm eine Rasterstufe mehr — die Bankangestellte landet über dem
Markt, die Handelsangestellte darunter. Die Regel „das Einkommen ist kein
Preisargument" hält im Modell nicht vollständig.

## 6 Empfehlung und wann sie kippt

1. Die Erhöhungen aus `kennzahl_empfehlung_vertrag` als **Obergrenze** für
   die nächste Anpassung verwenden, nicht als Automatik: Wo die Empfehlung
   über den Marktmedian geht (wie bei LS-29), auf den Markt begrenzen.
2. Bei Verträgen, in denen die Belastung nach der Erhöhung über 35 % läge,
   nicht erhöhen — diese Grenze hat der Vermieter bei Vertragsabschluss
   selbst angelegt.
3. Die Marktwertkontrolle im 14-Tage-Takt fortführen; erst mit mehreren
   vollständigen Abrufen ist eine Veränderung des Markts von der Auswahl der
   Inserate zu trennen.

**Woran die Empfehlung hängt** [kennzahl_sensitivitaet]:

| Annahme am Rand | Wert | Empfehlungen geändert (von 50) | mittlere Erhöhung |
|---|---:|---:|---:|
| Wechselbereitschaft niedrig | 0,3 | 43 | 8,3 % |
| kein Marktrisikoabschlag | 0,0 | 32 | 5,3 % |
| Marktrisikoabschlag hoch | 12 % | 20 | 2,2 % |
| Leerstand 4 Monate | 4,0 | 7 | 2,9 % |

Im Basisfall liegt die mittlere Erhöhung bei 3,4 % [kennzahl_sensitivitaet].
Wie bereitwillig Mieter wechseln, ist die Annahme, an der fast alles hängt —
und sie ist nicht gemessen. Liegt der Markt am oberen Quartil, steigt die
mittlere Erhöhung in einer Klasse auf 27,6 %, am unteren fällt sie auf 0,0 %
[kennzahl_sensitivitaet].

## 7 Grenzen

- **Synthetische Mieter.** Verzeichnis, Mieten und Lohnzettel sind
  erfunden (`config/vertraege.json`). Die Einkommensniveaus sind
  Platzhalter; dass fast alle Haushalte für diese Mieten ein Zweiteinkommen
  brauchen, zeigt, dass sie zu niedrig angesetzt sind.
- **Modell für Verlängerungen, angewendet auf laufende Verträge.** Das
  Verhaltensmodell erwartet auch ohne Erhöhung viele Auszüge (11,1 bzw. 13,5
  je 25 Verträge über 5 Jahre) [kennzahl_empfehlung]. Für laufende Verträge
  ist das zu hoch; die Rangfolge der Empfehlungen ist brauchbarer als die
  Euro-Beträge.
- **Kurze Marktreihe.** Drei Abrufe, der erste eine Teilseite. Eine
  Mieterhöhung vor dem 25.09.2026 hat keinen gemessenen Marktbezug.
- **Angebot ist nicht Abschluss.** Inserate zeigen, was verlangt wird.
- **Bereinigung vereinfacht.** WG-Zimmer und ausdrücklich genannte
  Gemeindewohnungen sind aus dem Markt genommen; was eine Anzeige sonst ist,
  lässt sich aus den Daten nicht sicher sagen. Möblierte Kurzzeitangebote
  bleiben im Markt und heben den Median eher an.
- **Rechtsrahmen.** Während eines laufenden Vertrags ist eine Erhöhung nur
  über die vereinbarte, seit 01.01.2026 gedeckelte Wertsicherung möglich;
  darüber hinaus nur bei Verlängerung oder Neuvereinbarung. Die Empfehlung
  sagt, was der Markt trägt, nicht was rechtlich sofort durchsetzbar ist.
  Kein Rechtsrat.
- **Das Einkommen ist kein Preisargument** — und Abschnitt 5 zeigt, dass
  das Modell diese Regel nicht vollständig einhält. Die Belastung durch
  höhere Mieten tragen die Mieter; das ist die Prämisse dieses Auftrags.
