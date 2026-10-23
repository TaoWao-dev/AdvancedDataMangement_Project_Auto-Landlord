-- Kennzahl 7: Die Empfehlung je Groessenklasse, zusammengefasst.
--
-- Fallstrick: Barwerte ueber fuenf Jahre im Erwartungswert, auf
-- synthetischen Vertraegen und unbelegten Verhaltensparametern
-- (docs/annahmen.md) - eine Groessenordnung, kein Budget. Ob eine
-- Empfehlung an einer Annahme haengt, zeigt kennzahl_sensitivitaet.
WITH e AS (
  SELECT v.groessenklasse, v.wertsicherung, e.*
  FROM empfehlung e JOIN vertrag v ON v.vertrag_id = e.vertrag_id
),
r AS (
  SELECT groessenklasse, erhoehung_pct,
         ROW_NUMBER() OVER (PARTITION BY groessenklasse ORDER BY erhoehung_pct) AS rn,
         COUNT(*)     OVER (PARTITION BY groessenklasse)                        AS n
  FROM e
)
SELECT m.segment                                   AS groessenklasse,
       m.datenstand,
       m.marktmiete_eur_m2,
       m.marktmiete_fallzahl,
       m.eignung,
       COUNT(e.vertrag_id)                         AS vertraege,
       SUM(e.erhoehen)                             AS erhoehen,
       SUM(1 - e.erhoehen)                         AS nicht_erhoehen,
       (SELECT AVG(erhoehung_pct) FROM r WHERE r.groessenklasse = m.segment
          AND rn IN ((n + 1) / 2, (n + 2) / 2))    AS median_erhoehung_pct,
       MIN(e.erhoehung_pct)                        AS min_erhoehung_pct,
       MAX(e.erhoehung_pct)                        AS max_erhoehung_pct,
       SUM(e.bezug_vor_beobachtung)                AS bezug_vor_beobachtung,
       ROUND(AVG(e.p_annahme), 3)                  AS mittel_p_annahme,
       ROUND(SUM(1.0 - e.p_annahme), 1)            AS erwartete_auszuege,
       ROUND(SUM(e.bw_empfehlung), 0)              AS bw_empfehlung_summe,
       ROUND(SUM(e.bw_ohne_erhoehung), 0)          AS bw_ohne_erhoehung_summe,
       ROUND(SUM(e.bw_empfehlung - e.bw_ohne_erhoehung), 0) AS mehrwert_gegen_ohne_erhoehung,
       m.konvergiert,
       m.iterationen,
       m.leerstand_monate                          AS leerstand_fixpunkt_monate
FROM modelllauf m
LEFT JOIN e ON e.groessenklasse = m.segment
GROUP BY m.segment
ORDER BY m.segment;
