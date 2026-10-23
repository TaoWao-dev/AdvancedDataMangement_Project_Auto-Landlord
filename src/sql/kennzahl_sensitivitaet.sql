-- Kennzahl 8: An welcher Annahme haengt die Empfehlung?
--
-- Jeder Parameter am unteren und oberen Rand seiner Spanne
-- (config/portfolio.json; Marktmiete: Q1 und Q3 der juengsten Kennzahlzeile).
-- 'geaendert' zaehlt Vertraege, deren empfohlene Erhoehung sich aendert -
-- auch um eine Rasterstufe. Ein Parameter mit vielen Aenderungen ist der,
-- den man messen sollte, bevor man der Empfehlung folgt.
SELECT s.parameter,
       s.rand,
       s.wert,
       COUNT(*)                                                    AS vertraege,
       SUM(s.erhoehung_pct <> e.erhoehung_pct)                     AS geaendert,
       SUM(s.option = 'nicht erhoehen')                            AS nicht_erhoehen,
       ROUND(AVG(s.erhoehung_pct), 1)                              AS mittel_erhoehung_pct,
       ROUND((SELECT AVG(erhoehung_pct) FROM empfehlung), 1)       AS mittel_erhoehung_basis_pct
FROM empfehlung_sensitivitaet s
JOIN empfehlung e ON e.vertrag_id = s.vertrag_id
GROUP BY s.parameter, s.rand, s.wert
ORDER BY geaendert DESC, s.parameter, s.rand;
