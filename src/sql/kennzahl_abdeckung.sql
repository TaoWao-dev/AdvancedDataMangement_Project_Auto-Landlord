-- Kennzahl 4: Abdeckung und Alter des Datenstands.
--
-- Die Frage: Welche Bezirke haben wir, welche fehlen, wie alt ist der
-- Stand, und ist er vollstaendig? Diese Abfrage gehoert an den Anfang jeder
-- Entscheidungsvorlage - sie sagt, wovon die Vorlage ueberhaupt spricht.
--
-- immer_vollstaendig = 0 heisst: mindestens ein Schnappschuss enthielt nur
-- die erste Ergebnisseite. Der Median beschreibt dann nicht den Bezirk.
SELECT plz,
       bezirk_name,
       COALESCE(cluster_id, '-')          AS cluster_id,
       rolle,
       schnappschuesse,
       COALESCE(letzter_abruf, '-')       AS letzter_abruf,
       COALESCE(beobachtungen, 0)         AS beobachtungen,
       COALESCE(treffer_letzter, 0)       AS treffer_letzter,
       immer_vollstaendig,
       CASE WHEN schnappschuesse = 0 THEN 'fehlt'
            WHEN immer_vollstaendig = 0 THEN 'nur Teilseite'
            ELSE 'ok' END                 AS befund
FROM v_abdeckung
ORDER BY rolle, plz;
