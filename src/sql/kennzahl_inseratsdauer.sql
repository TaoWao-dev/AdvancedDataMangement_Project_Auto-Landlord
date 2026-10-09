-- Kennzahl 5: Inseratsdauer je Bezirk.
--
-- Die Frage: Wie lange steht ein Inserat online? Das ist der empirische
-- Schaetzer fuer die Leerstandsannahme im Entscheidungsmodell, die bisher
-- ein Parameter mit Sensitivitaetsspanne ist (config/portfolio.json,
-- leerstand_monate).
--
-- Gemessen wird nur zu den Abrufen. Daraus folgen zwei Arten von Luecken:
--
-- ZENSIERT: Ein Inserat, das im juengsten Abruf seiner PLZ noch steht, ist
-- nicht abgeschlossen. Seine Dauer ist eine Untergrenze.
--
-- UNGEMESSEN: Ein Inserat, das nur in EINEM Abruf zu sehen war und danach
-- fehlt, ist irgendwann zwischen zwei Abrufen verschwunden. Seine Dauer ist
-- unbekannt, nicht null. Es zaehlt deshalb nicht in den Mittelwert - frueher
-- tat es das mit 0 Tagen und zog ihn auf 0,0.
--
-- Was mit wenigen Abrufen schon belastbar ist: der Anteil der aelteren
-- Inserate, der im juengsten Abruf noch online ist. Liegt er bei 14 Tagen
-- Abstand ueber 0,5, steht ein typisches Inserat laenger als zwei Wochen.
WITH letzter AS (
  SELECT plz, MAX(zuletzt_gesehen) AS tag FROM v_inseratsdauer GROUP BY plz
)
SELECT d.plz,
       b.bezirk_name,
       COUNT(*)                                            AS inserate,
       SUM(d.zensiert)                                      AS davon_zensiert,
       ROUND(1.0 * SUM(d.zensiert) / COUNT(*), 2)           AS anteil_zensiert,
       SUM(CASE WHEN d.zensiert = 0 AND d.beobachtungen = 1
                THEN 1 ELSE 0 END)                          AS abgaenge_ungemessen,
       ROUND(AVG(CASE WHEN d.zensiert = 0 AND d.beobachtungen > 1
                      THEN d.dauer_tage END), 1)            AS mittel_tage_abgeschlossen,
       MAX(d.dauer_tage)                                    AS max_tage_beobachtet,
       ROUND(1.0 * SUM(CASE WHEN d.erst_gesehen < l.tag AND d.zensiert = 1
                            THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN d.erst_gesehen < l.tag
                               THEN 1 ELSE 0 END), 0), 2)  AS anteil_aeltere_noch_online,
       CASE WHEN SUM(d.zensiert) = COUNT(*)
            THEN 'nicht auswertbar: nur ein Abruf'
            WHEN SUM(CASE WHEN d.zensiert = 0 AND d.beobachtungen > 1
                          THEN 1 ELSE 0 END) = 0
            THEN 'Dauer noch nicht messbar, nur Anteil noch online'
            WHEN 1.0 * SUM(d.zensiert) / COUNT(*) > 0.5
            THEN 'mit Vorsicht: ueberwiegend zensiert'
            ELSE 'auswertbar' END                           AS befund
FROM v_inseratsdauer d
JOIN bezirk b  ON b.plz = d.plz
JOIN letzter l ON l.plz = d.plz
GROUP BY d.plz, b.bezirk_name
ORDER BY d.plz;
