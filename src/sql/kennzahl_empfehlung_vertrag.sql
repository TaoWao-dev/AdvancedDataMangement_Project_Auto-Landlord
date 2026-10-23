-- Kennzahl 5: Die Empfehlung je Vertrag, fuer den Anhang der Vorlage.
--
-- Die Frage: Was bieten wir diesem Mieter an, und wie wahrscheinlich nimmt
-- er an?
--
-- Fallstrick: luecke_zum_markt_pct ist die Differenz der heutigen Miete zur
-- beobachteten Angebotsmiete, nicht zur Abschlussmiete (Annahme A4). Die
-- Spalten berufsgruppe und belastungsquote beschreiben ein ERFUNDENES
-- Haushaltseinkommen; das Einkommen begruendet nie den Preis (E05), es
-- bremst nur ueber Annahme und Ausfallrisiko. Vertraege ohne Marktmiete
-- erscheinen nicht - sie stehen in kennzahl_empfehlung als Luecke.
SELECT v.vertrag_id,
       v.cluster_id,
       v.vertragsende,
       v.flaeche_m2,
       v.wertsicherung,
       ROUND(v.miete_aktuell_eur / v.flaeche_m2, 2)                     AS miete_aktuell_eur_m2,
       m.marktmiete_eur_m2,
       ROUND(100.0 * (m.marktmiete_eur_m2 * v.flaeche_m2 - v.miete_aktuell_eur)
             / v.miete_aktuell_eur, 1)                                  AS luecke_zum_markt_pct,
       e.option,
       e.aufschlag_pct,
       e.angebot_eur,
       e.angebot_eur_m2,
       e.p_annahme,
       v.berufsgruppe,
       e.belastungsquote,
       e.bw_empfehlung,
       e.bw_nur_index,
       e.bw_auslaufen,
       (SELECT COUNT(DISTINCT COALESCE(s.aufschlag_pct, -1))
          FROM empfehlung_sensitivitaet s WHERE s.vertrag_id = v.vertrag_id) AS varianten_ueber_sensitivitaet
FROM empfehlung e
JOIN vertrag v     ON v.vertrag_id = e.vertrag_id
JOIN modelllauf m  ON m.cluster_id = v.cluster_id
ORDER BY v.vertragsende, v.vertrag_id;
