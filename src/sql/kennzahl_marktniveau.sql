-- Kennzahl 1: Preisniveau je Bezirk, Groessenklasse und Abruf.
--
-- Die Frage: Was kostet ein Quadratmeter Angebotsmiete, und wie sicher ist
-- diese Zahl? Die Spalte belastbarkeit zuerst lesen: bei 'nicht belastbar'
-- (unter 8 Faellen) beschreibt der Median eine Handvoll Inserate, nicht
-- einen Markt.
--
-- Referenzantwort: evals/references/marktniveau.json
-- Unabhaengig nachgerechnet von evals/nachrechnen_marktniveau.py (ohne SQL).
-- Die drei Handproben stehen in evals/references/handproben.json und sind
-- noch nicht bestaetigt - siehe 05_schritt4_abfragen_referenzen.md.
SELECT m.plz,
       b.bezirk_name,
       b.rolle,
       m.groessenklasse,
       m.abruf_datum,
       m.fallzahl,
       m.median_eur_m2,
       m.q1_eur_m2,
       m.q3_eur_m2,
       m.min_eur_m2,
       m.max_eur_m2,
       m.davon_privat,
       m.davon_gewerblich,
       m.belastbarkeit
FROM v_marktniveau m
JOIN bezirk b ON b.plz = m.plz
ORDER BY m.plz,
         CASE m.groessenklasse WHEN 'bis 50' THEN 1 WHEN '50-80' THEN 2
                               WHEN '80-100' THEN 3 ELSE 4 END,
         m.abruf_datum;
