-- Views der Marktbeobachtung.
--
-- Drei Grundsaetze:
--   1. Jede Aggregatzeile fuehrt ihre Fallzahl mit. Ein Median ueber vier
--      Inserate ist kein Marktpreis, und das muss man sehen koennen.
--   2. Gefiltert wird auf aktive Inserate. Reservierte Objekte sind kein
--      Angebot mehr; sie wuerden den Median nach oben ziehen, weil
--      ueberdurchschnittlich attraktive Wohnungen schneller reserviert sind.
--   3. Alles ist nach PLZ gruppiert. Ein Bezirk mehr heisst eine Datei mehr,
--      keine Aenderung an diesen Views.

-- Analysebasis: aktive Inserate mit Miete und Flaeche.
DROP VIEW IF EXISTS v_angebot;
CREATE VIEW v_angebot AS
SELECT b.*,
       CASE WHEN b.flaeche_m2 <  50 THEN 'bis 50'
            WHEN b.flaeche_m2 <  80 THEN '50-80'
            WHEN b.flaeche_m2 <= 100 THEN '80-100'
            ELSE 'ueber 100' END        AS groessenklasse,
       substr(b.abruf_ts, 1, 10)        AS abruf_datum
FROM inserat_beobachtung b
WHERE b.status = 'aktiv'
  AND b.miete_eur  IS NOT NULL
  AND b.flaeche_m2 IS NOT NULL;

-- Preisniveau je PLZ, Groessenklasse und Abruf.
-- Median ueber Fensterfunktion, weil SQLite kein PERCENTILE_CONT kennt.
DROP VIEW IF EXISTS v_marktniveau;
CREATE VIEW v_marktniveau AS
WITH rang AS (
  SELECT plz, groessenklasse, abruf_datum, eur_pro_m2, privat, gewerblich,
         ROW_NUMBER() OVER (PARTITION BY plz, groessenklasse, abruf_datum
                            ORDER BY eur_pro_m2) AS r,
         COUNT(*)    OVER (PARTITION BY plz, groessenklasse, abruf_datum) AS n
  FROM v_angebot
)
SELECT plz, groessenklasse, abruf_datum,
       n                                            AS fallzahl,
       ROUND(AVG(CASE WHEN r IN ((n+1)/2, (n+2)/2)
                      THEN eur_pro_m2 END), 2)      AS median_eur_m2,
       ROUND(MIN(eur_pro_m2), 2)                    AS min_eur_m2,
       ROUND(MAX(eur_pro_m2), 2)                    AS max_eur_m2,
       ROUND(AVG(CASE WHEN r = (n+3)/4   THEN eur_pro_m2 END), 2) AS q1_eur_m2,
       ROUND(AVG(CASE WHEN r = (3*n+3)/4 THEN eur_pro_m2 END), 2) AS q3_eur_m2,
       SUM(privat)                                  AS davon_privat,
       SUM(gewerblich)                              AS davon_gewerblich,
       CASE WHEN n >= 15 THEN 'belastbar'
            WHEN n >= 8  THEN 'duenn'
            ELSE 'nicht belastbar' END              AS belastbarkeit
FROM rang
GROUP BY plz, groessenklasse, abruf_datum, n;

-- Median getrennt nach Anbietertyp. Noetig, weil moeblierte
-- Kurzzeitwohnungen gewerblicher Anbieter den Gesamtmedian nach oben ziehen.
-- Die Differenz ist selbst ein Ergebnis.
DROP VIEW IF EXISTS v_marktniveau_anbietertyp;
CREATE VIEW v_marktniveau_anbietertyp AS
WITH basis AS (
  SELECT plz, groessenklasse, abruf_datum, eur_pro_m2,
         CASE WHEN privat = 1 THEN 'privat' ELSE 'gewerblich' END AS anbietertyp
  FROM v_angebot
), rang AS (
  SELECT b.*,
         ROW_NUMBER() OVER (PARTITION BY plz, groessenklasse, abruf_datum,
                                         anbietertyp
                            ORDER BY eur_pro_m2) AS r,
         COUNT(*)    OVER (PARTITION BY plz, groessenklasse, abruf_datum,
                                         anbietertyp) AS n
  FROM basis b
)
SELECT plz, groessenklasse, abruf_datum, anbietertyp,
       n                                        AS fallzahl,
       ROUND(AVG(CASE WHEN r IN ((n+1)/2, (n+2)/2)
                      THEN eur_pro_m2 END), 2)  AS median_eur_m2
FROM rang
GROUP BY plz, groessenklasse, abruf_datum, anbietertyp, n;

-- Bezirksvergleich im Zielsegment, juengster Abruf je PLZ.
-- Die Mehrbezirks-Sicht: eine Zeile je Bezirk, direkt vergleichbar.
DROP VIEW IF EXISTS v_bezirksvergleich;
CREATE VIEW v_bezirksvergleich AS
WITH aktuell AS (
  SELECT m.* FROM v_marktniveau m
  JOIN (SELECT plz, groessenklasse, MAX(abruf_datum) AS d
        FROM v_marktniveau GROUP BY plz, groessenklasse) j
    ON j.plz = m.plz AND j.groessenklasse = m.groessenklasse
   AND j.d = m.abruf_datum
  WHERE m.groessenklasse = '80-100'
)
SELECT a.plz, b.bezirk_name, b.cluster_id, b.rolle,
       a.abruf_datum, a.fallzahl, a.median_eur_m2,
       a.q1_eur_m2, a.q3_eur_m2, a.davon_gewerblich,
       ROUND(100.0 * a.davon_gewerblich / a.fallzahl, 1)  AS gewerblich_pct,
       a.belastbarkeit,
       RANK() OVER (ORDER BY a.median_eur_m2 DESC)        AS rang_teuer,
       ROUND(a.median_eur_m2 - AVG(a.median_eur_m2) OVER (), 2)
                                                          AS abstand_zum_mittel
FROM aktuell a
JOIN bezirk b ON b.plz = a.plz;

-- Marktmiete je Portfolio-Cluster. Bindeglied zum Entscheidungsmodell:
-- es braucht je Cluster genau eine Zahl. Bezirke ohne Schnappschuss
-- erscheinen mit NULL - sichtbare Luecke statt eingesetzter Annahme.
DROP VIEW IF EXISTS v_cluster_marktmiete;
CREATE VIEW v_cluster_marktmiete AS
SELECT b.cluster_id, b.plz, b.bezirk_name,
       v.abruf_datum, v.median_eur_m2, v.fallzahl, v.belastbarkeit,
       CASE WHEN v.median_eur_m2 IS NULL          THEN 'kein Schnappschuss'
            WHEN v.belastbarkeit = 'nicht belastbar' THEN 'Fallzahl zu klein'
            ELSE 'verwendbar' END AS eignung
FROM bezirk b
LEFT JOIN v_bezirksvergleich v ON v.plz = b.plz
WHERE b.cluster_id IS NOT NULL;

-- Preisaenderungen waehrend der Laufzeit.
-- Braucht mindestens zwei Schnappschuesse derselben PLZ; sonst leer.
DROP VIEW IF EXISTS v_preisaenderung;
CREATE VIEW v_preisaenderung AS
SELECT ad_id, plz,
       MIN(abruf_ts)                            AS erst_gesehen,
       MAX(abruf_ts)                            AS zuletzt_gesehen,
       COUNT(*)                                 AS beobachtungen,
       MIN(miete_eur)                           AS miete_min,
       MAX(miete_eur)                           AS miete_max,
       ROUND(100.0 * (MAX(miete_eur) - MIN(miete_eur))
             / MIN(miete_eur), 1)               AS aenderung_pct
FROM inserat_beobachtung
WHERE miete_eur IS NOT NULL
GROUP BY ad_id, plz
HAVING COUNT(DISTINCT miete_eur) > 1;

-- Inseratsdauer. Schaetzer fuer die Leerstandsannahme im
-- Entscheidungsmodell - bisher eine Annahme, kuenftig eine Messung.
-- Zensierung beachten: ein Inserat im letzten Schnappschuss seiner PLZ ist
-- noch offen, seine Dauer ist eine Untergrenze.
DROP VIEW IF EXISTS v_inseratsdauer;
CREATE VIEW v_inseratsdauer AS
SELECT b.ad_id, b.plz,
       MIN(b.abruf_ts)                          AS erst_gesehen,
       MAX(b.abruf_ts)                          AS zuletzt_gesehen,
       COUNT(*)                                 AS beobachtungen,
       CAST(julianday(MAX(b.abruf_ts)) - julianday(MIN(b.abruf_ts))
            AS INTEGER)                         AS dauer_tage,
       CASE WHEN MAX(b.abruf_ts) = (SELECT MAX(abruf_ts)
                                    FROM inserat_beobachtung
                                    WHERE plz = b.plz)
            THEN 1 ELSE 0 END                   AS zensiert
FROM inserat_beobachtung b
GROUP BY b.ad_id, b.plz;

-- Anbieterstruktur je Bezirk und Groessenklasse.
DROP VIEW IF EXISTS v_anbieterstruktur;
CREATE VIEW v_anbieterstruktur AS
SELECT plz, abruf_datum, groessenklasse,
       COUNT(*)                                     AS n,
       SUM(privat)                                  AS privat,
       SUM(gewerblich)                              AS gewerblich,
       ROUND(100.0 * SUM(gewerblich) / COUNT(*), 1) AS gewerblich_pct
FROM v_angebot
GROUP BY plz, abruf_datum, groessenklasse;

-- Abdeckung: welche Bezirke haben wir, welche fehlen, wie alt ist der Stand?
DROP VIEW IF EXISTS v_abdeckung;
CREATE VIEW v_abdeckung AS
SELECT b.plz, b.bezirk_name, b.cluster_id, b.rolle,
       COUNT(DISTINCT s.snapshot_id)                   AS schnappschuesse,
       MAX(s.abruf_ts)                                 AS letzter_abruf,
       SUM(s.geliefert)                                AS beobachtungen,
       MAX(s.treffer_gesamt)                           AS treffer_letzter,
       MIN(COALESCE(s.vollstaendig, 1))                AS immer_vollstaendig
FROM bezirk b
LEFT JOIN snapshot s ON s.plz = b.plz
GROUP BY b.plz, b.bezirk_name, b.cluster_id, b.rolle;
