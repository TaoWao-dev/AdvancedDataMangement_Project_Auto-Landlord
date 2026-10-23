-- Kennzahl 6: Das Mieterverzeichnis mit Empfehlung - je laufendem Vertrag.
--
-- Die Frage: sollen wir die Miete erhoehen, und um wie viel? Daneben die
-- beiden Groessen, nach denen der Asset-Manager fragt: wie hat sich der
-- Markt fuer vergleichbare Wohnungen seit der letzten Erhoehung bewegt,
-- und wie der KV-Lohn der Branche des Mieters.
--
-- Fallstricke: bezug_vor_beobachtung = 1 heisst, die letzte Erhoehung liegt
-- vor unserem ersten Abruf - markt_veraenderung_pct misst dann nur die Zeit
-- seit dem 25.09.2026. Die KV-Entwicklung bestimmt NICHT die Hoehe der
-- Empfehlung (Obergrenze ist der Markt), sondern wie wahrscheinlich der
-- Mieter annimmt (E05, E44). Die neue Miete kann den Marktmedian um eine
-- Rasterstufe ueberschreiten (Umzugskosten halten den Mieter). Die Mieter
-- sind synthetisch (E44).
SELECT v.vertrag_id,
       v.groessenklasse,
       v.flaeche_m2,
       v.branche_id,
       v.letzte_anpassung,
       ROUND(v.miete_aktuell_eur / v.flaeche_m2, 2)          AS miete_aktuell_eur_m2,
       v.miete_aktuell_eur,
       e.markt_bezug_datum,
       e.markt_bezug_eur_m2,
       e.bezug_vor_beobachtung,
       e.markt_jetzt_eur_m2,
       e.markt_veraenderung_pct,
       ROUND(100.0 * (e.markt_jetzt_eur_m2 * v.flaeche_m2 - v.miete_aktuell_eur)
             / v.miete_aktuell_eur, 1)                       AS luecke_zum_markt_pct,
       e.kv_seit_anpassung_pct,
       e.kv_seit_abschluss_pct,
       ROUND((v.lohnzettel_1_eur + v.lohnzettel_2_eur + v.lohnzettel_3_eur) / 3, 0)
                                                             AS gehalt_lohnzettel_eur_monat,
       e.belastungsquote_jetzt,
       CASE WHEN e.erhoehen = 1 THEN 'erhoehen' ELSE 'nicht erhoehen' END AS empfehlung,
       e.erhoehung_pct,
       e.neue_miete_eur,
       e.neue_miete_eur_m2,
       e.p_annahme,
       e.belastungsquote_neu,
       ROUND(e.bw_empfehlung - e.bw_ohne_erhoehung, 0)       AS mehrwert_5j_eur
FROM vertrag v
JOIN empfehlung e ON e.vertrag_id = v.vertrag_id
ORDER BY v.groessenklasse, v.vertrag_id;
