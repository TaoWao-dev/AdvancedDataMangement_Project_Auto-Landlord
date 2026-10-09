-- Kennzahl 5: Inseratsdauer je Bezirk.
--
-- Die Frage: Wie lange steht ein Inserat online? Das ist der empirische
-- Schaetzer fuer die Leerstandsannahme im Entscheidungsmodell, die bisher
-- ein Parameter mit Sensitivitaetsspanne ist (config/portfolio.json,
-- leerstand_monate).
--
-- ZENSIERUNG: Ein Inserat, das im letzten Schnappschuss seiner PLZ noch
-- steht, ist nicht abgeschlossen. Seine Dauer ist eine Untergrenze. Solange
-- anteil_zensiert nahe 1 liegt, taugt der Mittelwert nichts - dann braucht
-- es weitere Abrufe. Bei einem einzigen Schnappschuss ist er 1,0.
SELECT d.plz,
       b.bezirk_name,
       COUNT(*)                                          AS inserate,
       SUM(d.zensiert)                                    AS davon_zensiert,
       ROUND(1.0 * SUM(d.zensiert) / COUNT(*), 2)         AS anteil_zensiert,
       ROUND(AVG(CASE WHEN d.zensiert = 0
                      THEN d.dauer_tage END), 1)          AS mittel_tage_abgeschlossen,
       MAX(d.dauer_tage)                                  AS max_tage_beobachtet,
       CASE WHEN SUM(d.zensiert) = COUNT(*)
            THEN 'nicht auswertbar: nur ein Abruf'
            WHEN 1.0 * SUM(d.zensiert) / COUNT(*) > 0.5
            THEN 'mit Vorsicht: ueberwiegend zensiert'
            ELSE 'auswertbar' END                         AS befund
FROM v_inseratsdauer d
JOIN bezirk b ON b.plz = d.plz
GROUP BY d.plz, b.bezirk_name
ORDER BY d.plz;
