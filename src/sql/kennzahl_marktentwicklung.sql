-- Kennzahl 4: Wie hat sich das Preisniveau je Groessenklasse entwickelt?
--
-- Die Frage des Asset-Managers: um wie viel hat sich der Markt fuer
-- Wohnungen vergleichbarer Groesse seit der letzten Mieterhoehung bewegt?
-- Diese Abfrage zeigt die Reihe je Abruf (14-taegige Marktwertkontrolle);
-- den Bezug je Vertrag zeigt kennzahl_empfehlung_vertrag.
--
-- Fallstrick: der erste Abruf (25.09.) war eine Teilseite (90 von 154),
-- die beiden folgenden sind vollstaendig. Ein Teil der "Veraenderung" zum
-- ersten Abruf ist deshalb Auswahl, nicht Markt. Aeltere Marktdaten gibt
-- es nicht - eine Mieterhoehung vor dem 25.09.2026 hat keinen gemessenen
-- Marktbezug.
SELECT m.plz,
       m.groessenklasse,
       CASE WHEN m.groessenklasse IN ('50-80', '80-100') THEN 1 ELSE 0 END AS im_portfolio,
       m.abruf_datum,
       a.vollstaendig                                       AS abruf_vollstaendig,
       m.fallzahl,
       m.median_eur_m2,
       m.belastbarkeit,
       ROUND(100.0 * (m.median_eur_m2 - LAG(m.median_eur_m2) OVER w)
             / LAG(m.median_eur_m2) OVER w, 1)              AS veraenderung_zum_vorabruf_pct,
       ROUND(100.0 * (m.median_eur_m2 - FIRST_VALUE(m.median_eur_m2) OVER w)
             / FIRST_VALUE(m.median_eur_m2) OVER w, 1)      AS veraenderung_seit_erstem_abruf_pct
FROM v_marktniveau m
JOIN v_abruf a ON a.plz = m.plz AND a.abruf_datum = m.abruf_datum
WINDOW w AS (PARTITION BY m.plz, m.groessenklasse ORDER BY m.abruf_datum)
ORDER BY m.plz,
         CASE m.groessenklasse WHEN 'bis 50' THEN 1 WHEN '50-80' THEN 2
                               WHEN '80-100' THEN 3 ELSE 4 END,
         m.abruf_datum;
