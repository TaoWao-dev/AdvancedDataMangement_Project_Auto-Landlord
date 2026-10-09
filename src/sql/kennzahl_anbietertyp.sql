-- Kennzahl 3: Median getrennt nach Anbietertyp.
--
-- Die Frage: Wie stark verzerren gewerbliche Anbieter den Median? Ein
-- einzelner Anbieter moeblierter Kurzzeitwohnungen stellte im ersten
-- Schnappschuss 17 von 90 Inseraten in 1020.
--
-- Die Differenz zwischen den Zeilen 'privat' und 'gewerblich' ist selbst das
-- Ergebnis. Bei Fallzahlen unter 8 ist sie nicht belastbar - im ersten
-- Schnappschuss traf das auf die privaten Inserate des Zielsegments zu (n=3).
--
-- Referenzantwort: evals/references/anbietertyp.json
SELECT a.plz,
       b.bezirk_name,
       a.groessenklasse,
       a.abruf_datum,
       a.anbietertyp,
       a.fallzahl,
       a.median_eur_m2,
       CASE WHEN a.fallzahl >= 15 THEN 'belastbar'
            WHEN a.fallzahl >= 8  THEN 'duenn'
            ELSE 'nicht belastbar' END AS belastbarkeit
FROM v_marktniveau_anbietertyp a
JOIN bezirk b ON b.plz = a.plz
WHERE a.groessenklasse = '80-100'
ORDER BY a.plz, a.abruf_datum, a.anbietertyp;
