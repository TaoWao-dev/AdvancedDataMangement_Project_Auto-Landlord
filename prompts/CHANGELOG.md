# Prompt-Changelog

Je Version eine Zeile: warum sie entstand und was sich an der Suite
geändert hat (Trefferquote vorher → nachher). „nicht gelaufen" heißt, dass
gegen diese Version noch kein Modelllauf stattgefunden hat — nicht 0 %.

| Datum | Prompt | Version | Warum | Suite vorher → nachher | Modell |
|---|---|---|---|---|---|
| 2026-10-23 | `kv_extraktion` | v1 | erste Fassung; Regeln aus den Ablenkern der Referenz abgeleitet (Vorjahr, Forderung, Arbeiter-KV, Datum ohne Tag) | — → nicht gelaufen | — |
| 2026-10-23 | `moebliert` | v1 | erste Fassung nach E38; Beispiele aus den Markierregeln der Liste v3 | — → nicht gelaufen | — |
| 2026-10-23 | `vorlage` | v1 | erste Fassung; harte Regel „du rechnest nicht", Herkunft in Klammern | — → `docs/vorlage.md` v1, Zahlenprüfung siehe 06 | Claude Opus 5.5, Arbeitssitzung |
| 2026-10-23 | `kv_zeitreihe` | v1 | Demo-Fall (E44): alle Abschlüsse 2024–2026 je Branche mit Wortlaut für Gate 4 | — → Gate 4: 15/15 Datensätze; Eval gegen Referenzen 5/5 (Konsistenz, E45) | Claude Opus 5.5, Arbeitssitzung |
| 2026-10-23 | `vorlage` | v2 | Demo-Fall: Mietanpassung je laufendem Vertrag statt Verlängerung; v1 war nach dem dritten Abruf veraltet (19 Zahlen ohne Herkunft) | 1/2 → siehe 06 | Claude Opus 5.5, Arbeitssitzung |
