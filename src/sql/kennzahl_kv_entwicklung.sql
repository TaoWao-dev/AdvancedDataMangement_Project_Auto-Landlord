-- Kennzahl 5: Wie hat sich der KV-Lohn je Branche entwickelt?
--
-- Die Abschluesse 2024-2026 je Branche, wie sie die LLM-Extraktion gefunden
-- und Gate 4 gegen den Wortlaut der Quelle geprueft hat - mit Fundstelle.
--
-- Fallstrick: satz_index ist eine Rechenregel des Programms (Durchschnitt
-- laut Quelle, sonst Mitte der Spanne). datum_angenommen = 1 heisst: die
-- Quelle nennt keinen Tag, gerechnet wird ab 1. Jaenner. Ein Deckel wirkt
-- je Mieter - die Wirkung steht in kennzahl_empfehlung_vertrag.
-- Der KV-Lohn ist der Mindestlohn laut Kollektivvertrag, nicht das
-- Ist-Gehalt (A2).
SELECT k.branche_id,
       k.jahr,
       k.gueltig_ab,
       k.datum_angenommen,
       k.prozent_min,
       k.prozent_max,
       k.satz_index,
       k.fixbetrag_eur,
       k.deckel_eur,
       k.datei                                              AS quelle_datei,
       k.zeile_original                                     AS quelle_zeile,
       (SELECT COUNT(*) FROM vertrag v WHERE v.branche_id = k.branche_id) AS mieter_im_portfolio
FROM kv_erhoehung k
ORDER BY k.branche_id, k.jahr;
