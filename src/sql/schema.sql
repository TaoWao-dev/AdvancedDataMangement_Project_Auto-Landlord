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

CREATE TABLE indexreihe (
  reihe     TEXT    NOT NULL,
  jahr      INTEGER NOT NULL,
  indexwert REAL    NOT NULL,
  quelle    TEXT    NOT NULL,
  PRIMARY KEY (reihe, jahr)
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
