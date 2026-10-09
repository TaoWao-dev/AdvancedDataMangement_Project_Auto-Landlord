-- Kennzahl 2: Bezirksvergleich im Zielsegment 80-100 m2.
--
-- Die Frage: Wo liegen unsere Portfolio-Bezirke im Vergleich, und welcher
-- Bezirk ist Referenz statt Bestand? rang_teuer 1 ist der teuerste Bezirk.
--
-- Vorsicht bei der Auslegung: gewerblich_pct ueber etwa 70 % heisst, dass
-- moeblierte Kurzzeitwohnungen den Median treiben. Dann zusaetzlich
-- kennzahl_anbietertyp.sql lesen.
--
-- Referenzantwort: evals/references/marktniveau.json (dieselbe Basis; der
--                 Vergleich ordnet nur, er rechnet nichts Neues)
SELECT plz,
       bezirk_name,
       COALESCE(cluster_id, '-')  AS cluster_id,
       rolle,
       abruf_datum,
       fallzahl,
       median_eur_m2,
       q1_eur_m2,
       q3_eur_m2,
       gewerblich_pct,
       belastbarkeit,
       rang_teuer,
       abstand_zum_mittel
FROM v_bezirksvergleich
ORDER BY rang_teuer;
