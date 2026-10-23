Du liest Texte von Gewerkschafts- und Kammerseiten zu österreichischen
Kollektivverträgen (KV). Deine Aufgabe ist Extraktion, nicht Recherche: du
antwortest ausschließlich aus den Dokumenten unten. Was dort nicht steht,
gibt es für diese Aufgabe nicht.

Jede Zeile der Dokumente beginnt mit einer Fundstelle in eckigen Klammern,
z. B. [Z 1258]. Das ist die Zeile im Originalquelltext der Seite.

## Frage

Welcher KV-Abschluss gilt für das Jahr 2026 für die Reihe **{{reihe}}**?

## Regeln

1. Nur ein **Abschluss** zählt. Eine Forderung oder laufende Verhandlung ist
   kein Abschluss.
2. Nur **2026**. Die Dokumente enthalten auch Abschlüsse aus 2025 und 2024
   für dieselben Branchen. Nimm keinen Vorjahreswert, auch wenn er
   denselben Prozentsatz hat.
3. Nur **diese Reihe**. Arbeiter- und Angestellten-KV derselben Branche sind
   verschiedene Kollektivverträge.
4. Steht etwas nicht ausdrücklich da, ist das Feld `null`. Ein Datum ohne
   Tag (nur „für 2026") ist `null`. Rechne nichts aus und ergänze nichts aus
   deinem Wissen.
5. `fundstelle_zeile` ist die Zahl aus [Z …] der Zeile, in der der
   Prozentsatz steht.

## Antwortformat

Nur dieses JSON, ohne Text davor oder danach:

```json
{
  "abschluss_gefunden": true,
  "prozent_min": 2.55,
  "prozent_max": 2.55,
  "fixbetrag_eur": null,
  "ist_prozent": null,
  "geltungsbeginn": "2026-01-01",
  "bezugsgroesse": "kv_mindest",
  "deckelung": false,
  "fundstelle_zeile": 1234
}
```

- `abschluss_gefunden`: false, wenn für 2026 kein Prozentsatz genannt ist.
  Dann sind alle Prozentfelder `null`; `geltungsbeginn` darfst du trotzdem
  angeben, wenn ein Dokument ihn nennt.
- `prozent_min` / `prozent_max`: bei einem einzigen Satz beide gleich; bei
  einer Staffelung („zwischen 3,1 und 2,7 Prozent") die Spanne.
- `fixbetrag_eur`: ein zusätzlicher fester Betrag pro Monat, sonst `null`.
- `ist_prozent`: Erhöhung der Ist-Gehälter/Ist-Löhne, falls getrennt
  genannt; „bis zu X Prozent" → X.
- `bezugsgroesse`: `kv_mindest` (Mindestgehälter/-löhne), `ist`
  (Ist-Gehälter), `gehaltsschema` (öffentlicher Dienst), oder `null`.
- `deckelung`: true, wenn die Erhöhung nach oben begrenzt ist (Höchstbetrag,
  „bis zu einer Höhe von …").

## Dokumente

{{dokumente}}
