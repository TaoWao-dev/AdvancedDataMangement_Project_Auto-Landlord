-- Kennzahl 4: Die Empfehlung je Cluster - das, was die Leitung entscheidet.
--
-- Die Frage: Fuer wie viele Vertraege empfiehlt das Modell welche Option,
-- mit welchem Aufschlag, und was bringt das gegenueber der reinen
-- Fortschreibung der Bestandsmiete?
--
-- Fallstrick: eine Zeile mit eignung <> 'verwendbar' hat KEINE Empfehlung,
-- weil fuer diesen Bezirk keine Marktmiete beobachtet ist. Nicht als null
-- Euro lesen. Die Vertraege sind synthetisch (Annahme A10), die
-- Modellparameter nicht belegt (docs/annahmen.md) - die Zahlen sind eine
-- Groessenordnung, kein Budget. Ob eine Empfehlung an einer Annahme haengt,
-- zeigt kennzahl_sensitivitaet.
--
-- Referenzantwort: keine aus einer Zweitimplementierung. Geprueft durch
-- tests/test_modell.py (Fixpunkt, Gegenkraft) und Gate 3 (Konvergenz).
WITH e AS (
  SELECT v.cluster_id, e.*
  FROM empfehlung e JOIN vertrag v ON v.vertrag_id = e.vertrag_id
),
r AS (
  SELECT cluster_id, aufschlag_pct,
         ROW_NUMBER() OVER (PARTITION BY cluster_id ORDER BY aufschlag_pct) AS rn,
         COUNT(*)     OVER (PARTITION BY cluster_id)                        AS n
  FROM e WHERE option = 'verlaengern'
)
SELECT m.cluster_id,
       m.datenstand,
       m.marktmiete_eur_m2,
       m.marktmiete_fallzahl,
       m.eignung,
       (SELECT COUNT(*) FROM vertrag v WHERE v.cluster_id = m.cluster_id)     AS vertraege,
       COUNT(e.vertrag_id)                                                   AS mit_empfehlung,
       SUM(e.option = 'verlaengern')                                         AS verlaengern,
       SUM(e.option = 'auslaufen')                                           AS auslaufen,
       (SELECT AVG(aufschlag_pct) FROM r
         WHERE r.cluster_id = m.cluster_id
           AND rn IN ((n + 1) / 2, (n + 2) / 2))                             AS median_aufschlag_pct,
       MIN(e.aufschlag_pct)                                                  AS min_aufschlag_pct,
       MAX(e.aufschlag_pct)                                                  AS max_aufschlag_pct,
       ROUND(AVG(e.p_annahme), 3)                                            AS mittel_p_annahme,
       ROUND(SUM(1.0 - COALESCE(e.p_annahme, 0)), 1)                         AS erwartete_auszuege,
       ROUND(SUM(e.bw_empfehlung), 0)                                        AS bw_empfehlung_summe,
       ROUND(SUM(e.bw_nur_index), 0)                                         AS bw_nur_index_summe,
       ROUND(SUM(e.bw_empfehlung - e.bw_nur_index), 0)                       AS mehrwert_gegen_nur_index,
       m.konvergiert,
       m.iterationen,
       m.leerstand_monate                                                    AS leerstand_fixpunkt_monate
FROM modelllauf m
LEFT JOIN e ON e.cluster_id = m.cluster_id
GROUP BY m.cluster_id
ORDER BY m.cluster_id;
