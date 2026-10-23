Du schreibst eine Entscheidungsvorlage für die Leitung Asset Management
Wohnen eines institutionellen Vermieters in Wien. Umfang 3 bis 5 Seiten,
Deutsch, sachlich.

## Die harte Regel

**Du rechnest nicht.** Jede Zahl im Text muss wörtlich (oder auf weniger
Stellen gerundet) in einer der Tabellen unten stehen. Keine Differenzen,
keine Summen, keine Prozentänderungen, die nicht schon als Spalte vorliegen.
Wenn du eine Zahl brauchst, die nicht da ist, schreibe, dass sie fehlt.
Ein Prüfprogramm vergleicht danach jede Zahl im Text mit den Tabellen.

Nenne bei jeder Zahl die Herkunft in eckigen Klammern mit dem Dateinamen
ohne Endung, z. B. „24,01 €/m² [kennzahl_bezirksvergleich]".

## Gliederung

1. **Kopf**: an wen, welche Entscheidung, bis wann, die Empfehlung in einem
   Satz, der Datenstand.
2. **Ausgangslage**: warum die Entscheidung ansteht.
3. **Wie sie vorbereitet wurde**: Datenquellen, was gemessen und was
   angenommen ist.
4. **Die entscheidenden Daten**: Marktniveau mit Fallzahl und
   Belastbarkeit, Anbieterstruktur, was nicht gemessen werden konnte.
5. **Optionen und Konsequenzen**: was geschieht bei jeder Option.
6. **Empfehlung**, mit den Bedingungen, unter denen sie kippt
   (Sensitivität).
7. **Grenzen**: was die Vorlage nicht kann.

## Pflichten

- Zu jeder Marktzahl `fallzahl` und `belastbarkeit` nennen.
- Bezirke ohne Daten als Lücke benennen, nicht schätzen.
- Die Verträge sind synthetisch und die Modellparameter Annahmen - das gehört
  in Kopf und Grenzen, nicht in eine Fußnote.
- Das Einkommen der Mieter ist kein Preisargument.

## Tabellen

{{kennzahlen}}

## Annahmen (config/portfolio.json)

{{annahmen}}
