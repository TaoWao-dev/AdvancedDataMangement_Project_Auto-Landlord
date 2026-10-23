-- Datenmodell mietportfolio. Zielsystem SQLite, laeuft auf MySQL 8 mit
-- denselben Views (Fensterfunktionen noetig, 5.7 reicht nicht).
--
-- Jeder Lauf loescht die Datenbank und baut sie neu, aus ALLEN Rohordnern
-- unter data/raw/. Damit ist der zweite Lauf identisch zum ersten und die
-- Historie bleibt vollstaendig.
--
-- Schluesselentscheidung: ad_id allein ist KEIN Primaerschluessel der
-- Beobachtungstabelle. Dieselbe Anzeige erscheint in jedem Schnappschuss
-- erneut - das ist erwuenscht, denn daraus fallen Preisaenderung und
-- Inseratsdauer heraus. Der Schluessel ist (snapshot_id, ad_id).

PRAGMA foreign_keys = ON;

-- ────────────────────────────────────────────────────────── Herkunft
CREATE TABLE snapshot (
  snapshot_id     INTEGER PRIMARY KEY,
  datei           TEXT    NOT NULL,
  sha256          TEXT    NOT NULL UNIQUE,   -- faengt dieselbe Datei
                                             -- unter zwei Namen ab
  abruf_ts        TEXT    NOT NULL,          -- searchDate des Servers,
                                             -- nicht die Verarbeitungszeit
  plz             TEXT    NOT NULL,
  treffer_gesamt  INTEGER NOT NULL,
  geliefert       INTEGER NOT NULL,
  vollstaendig    INTEGER NOT NULL,
  beschaffung     TEXT    NOT NULL DEFAULT 'manuell'
);

-- ──────────────────────────────────────────────────────── Dimensionen
CREATE TABLE bezirk (
  plz         TEXT PRIMARY KEY,
  bezirk_nr   INTEGER,
  bezirk_name TEXT NOT NULL,
  cluster_id  TEXT,                          -- NULL = Referenzgebiet
  rolle       TEXT NOT NULL                  -- portfolio | referenz
);

-- Ausgeschlossene Objekttypen mit Grund, aus config.OBJEKTTYP_AUSGESCHLOSSEN.
-- Steht in der Datenbank, damit ein Ausschluss sichtbar bleibt und nicht nur
-- als Filter in einer View existiert.
CREATE TABLE objekttyp_ausschluss (
  objekttyp TEXT PRIMARY KEY,
  grund     TEXT NOT NULL
);

CREATE TABLE indexreihe (
  reihe     TEXT    NOT NULL,
  jahr      INTEGER NOT NULL,
  indexwert REAL    NOT NULL,
  quelle    TEXT    NOT NULL,
  PRIMARY KEY (reihe, jahr)
);

-- Textbloecke der KV-Seiten (Quelle fuer die Extraktion, E28). Kein Feld
-- daraus wird hier interpretiert; das macht das Modell, geprueft gegen
-- evals/references/kv_extraktion.json. zeile_original ist die Fundstelle
-- im gespeicherten Quelltext - dieselbe Zahl steht in der Referenz.
CREATE TABLE kv_textblock (
  datei          TEXT    NOT NULL,
  block_nr       INTEGER NOT NULL,
  abrufdatum     TEXT    NOT NULL,
  quelle_url     TEXT,
  zeile_original INTEGER NOT NULL,
  text           TEXT    NOT NULL,
  PRIMARY KEY (datei, block_nr)
);

-- KV-Erhoehungen je Branche und Jahr: Ausgabe der LLM-Extraktion, nur nach
-- Gate 4 (Wortlaut steht in der Quellzeile, src/kv_extrakt.py). satz_index
-- ist eine Rechenregel des Programms (Durchschnitt laut Quelle, sonst Mitte
-- der Spanne), keine Angabe der Quelle.
CREATE TABLE kv_erhoehung (
  branche_id        TEXT    NOT NULL,
  jahr              INTEGER NOT NULL,
  gueltig_ab        TEXT    NOT NULL,
  datum_angenommen  INTEGER NOT NULL,       -- 1 = Quelle nennt keinen Tag
  prozent_min       REAL    NOT NULL,
  prozent_max       REAL    NOT NULL,
  prozent_mittel_laut_quelle REAL,
  satz_index        REAL    NOT NULL,
  fixbetrag_eur     REAL,
  deckel_eur        REAL,
  datei             TEXT    NOT NULL,
  zeile_original    INTEGER NOT NULL,
  wortlaut          TEXT    NOT NULL,
  PRIMARY KEY (branche_id, jahr)
);

-- ───────────────────────────────────────────────────────────── Fakten
CREATE TABLE inserat_beobachtung (
  snapshot_id     INTEGER NOT NULL REFERENCES snapshot(snapshot_id),
  ad_id           TEXT    NOT NULL,
  abruf_ts        TEXT    NOT NULL,
  status          TEXT    NOT NULL,          -- aktiv | reserviert
  plz             TEXT    NOT NULL REFERENCES bezirk(plz),
  miete_eur       REAL,
  flaeche_m2      REAL,
  wohnflaeche_m2  REAL,
  eur_pro_m2      REAL,
  zimmer          REAL,
  stock           INTEGER,
  objekttyp       TEXT,
  freiflaeche     TEXT,                      -- ; -getrennt
  privat          INTEGER,
  gewerblich      INTEGER,
  veroeffentlicht TEXT,
  lagequalitaet   REAL,
  -- 1 = Titel nennt Gemeindewohnung ausdruecklich, 0 = Titel geprueft, nicht
  -- genannt (heisst NICHT: keine Gemeindewohnung), NULL = Titel lag nicht vor
  gemeinde_explizit INTEGER,
  PRIMARY KEY (snapshot_id, ad_id)
);
CREATE INDEX ix_beob_ad  ON inserat_beobachtung(ad_id);
CREATE INDEX ix_beob_plz ON inserat_beobachtung(plz);
CREATE INDEX ix_beob_ts  ON inserat_beobachtung(abruf_ts);

-- Zeilen, die keinen Partner gefunden haben. Nicht stillschweigend
-- verworfen, sondern gezaehlt und benannt.
CREATE TABLE zuordnungsluecke (
  quelle     TEXT NOT NULL,
  schluessel TEXT NOT NULL,
  grund      TEXT NOT NULL,
  anzahl     INTEGER NOT NULL
);

-- Qualitaetsbefunde. Kein Lauf-Zeitstempel: der Zeitpunkt ist der
-- DATENSTAND, zu dem der Befund gehoert (abruf_ts des Schnappschusses).
-- Sonst waere die Datenbank keine reine Funktion von data/raw/ mehr, und
-- zwei Laeufe ergaeben unterschiedliche Dateien - siehe Entscheidungslog E25.
CREATE TABLE qs_befund (
  datenstand TEXT,
  objekt   TEXT NOT NULL,
  pruefung TEXT NOT NULL,
  stufe    TEXT NOT NULL,                    -- ok | warnung | fehler
  detail   TEXT
);

-- ─────────────────────────────────────────────── Portfolio und Modell
-- Synthetisches Mieterverzeichnis aus config/vertraege.json (E44). Keine
-- Personen: eine Kennung, eine Wohnung, ein Haushalt aus Zahlen. Die drei
-- Lohnzettel sind die Bruttobezuege der drei Monate vor Vertragsabschluss.
CREATE TABLE vertrag (
  vertrag_id          TEXT PRIMARY KEY,
  plz                 TEXT    NOT NULL REFERENCES bezirk(plz),
  groessenklasse      TEXT    NOT NULL,
  flaeche_m2          REAL    NOT NULL,
  abschluss           TEXT    NOT NULL,
  wertsicherung       INTEGER NOT NULL,
  letzte_anpassung    TEXT    NOT NULL,
  miete_aktuell_eur   REAL    NOT NULL,
  miete_bei_abschluss_eur REAL NOT NULL,
  branche_id          TEXT    NOT NULL,
  lohnzettel_1_eur    REAL    NOT NULL,
  lohnzettel_2_eur    REAL    NOT NULL,
  lohnzettel_3_eur    REAL    NOT NULL,
  zweiteinkommen      INTEGER NOT NULL
);

-- Je Groessenklasse: welche Marktmiete, ob der Fixpunkt konvergiert ist.
CREATE TABLE modelllauf (
  segment           TEXT PRIMARY KEY,         -- Groessenklasse
  datenstand        TEXT,
  marktmiete_eur_m2 REAL,
  marktmiete_fallzahl INTEGER,
  eignung           TEXT NOT NULL,            -- belastbarkeit der Marktmiete
  iterationen       INTEGER,
  konvergiert       INTEGER,
  leerstand_monate  REAL
);

-- Je Vertrag: Markt- und KV-Entwicklung seit der letzten Anpassung und die
-- Empfehlung. markt_bezug ist der Abruf, der der letzten Anpassung am
-- naechsten liegt; bezug_vor_beobachtung = 1, wenn die Anpassung vor dem
-- ersten Abruf lag - dann gibt es keine aeltere Marktzahl.
CREATE TABLE empfehlung (
  vertrag_id              TEXT PRIMARY KEY REFERENCES vertrag(vertrag_id),
  markt_bezug_datum       TEXT NOT NULL,
  markt_bezug_eur_m2      REAL NOT NULL,
  bezug_vor_beobachtung   INTEGER NOT NULL,
  markt_jetzt_datum       TEXT NOT NULL,
  markt_jetzt_eur_m2      REAL NOT NULL,
  markt_veraenderung_pct  REAL NOT NULL,
  kv_seit_anpassung_pct   REAL NOT NULL,
  kv_seit_abschluss_pct   REAL NOT NULL,
  einkommen_jetzt_eur_pa  REAL NOT NULL,      -- Lohnzettel x KV x 14
  erhoehen                INTEGER NOT NULL,   -- 0 = nicht erhoehen
  erhoehung_pct           REAL NOT NULL,
  neue_miete_eur          REAL NOT NULL,
  neue_miete_eur_m2       REAL NOT NULL,
  p_annahme               REAL NOT NULL,
  belastungsquote_jetzt   REAL NOT NULL,
  belastungsquote_neu     REAL NOT NULL,
  bw_empfehlung           REAL NOT NULL,
  bw_ohne_erhoehung       REAL NOT NULL,
  bw_auszug               REAL NOT NULL
);

-- Sensitivitaet: dieselbe Optimierung mit je einem Parameter am Rand seiner
-- Spanne (config/portfolio.json; Marktmiete: Q1 und Q3).
CREATE TABLE empfehlung_sensitivitaet (
  vertrag_id    TEXT NOT NULL REFERENCES vertrag(vertrag_id),
  parameter     TEXT NOT NULL,
  rand          TEXT NOT NULL,
  wert          REAL NOT NULL,
  option        TEXT NOT NULL,
  erhoehung_pct REAL,
  PRIMARY KEY (vertrag_id, parameter, rand)
);
