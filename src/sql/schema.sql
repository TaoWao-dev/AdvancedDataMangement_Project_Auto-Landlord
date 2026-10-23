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
-- Synthetischer Vertragsbestand aus config/vertraege.json (Annahme A10).
-- Keine Personen: berufsgruppe und einkommen sind erfundene Modellgroessen.
CREATE TABLE vertrag (
  vertrag_id          TEXT PRIMARY KEY,
  cluster_id          TEXT    NOT NULL,
  flaeche_m2          REAL    NOT NULL,
  abschluss_jahr      INTEGER NOT NULL,
  vertragsende        TEXT    NOT NULL,      -- JJJJ-MM
  wertsicherung       INTEGER NOT NULL,
  miete_aktuell_eur   REAL    NOT NULL,
  berufsgruppe        TEXT    NOT NULL,
  einkommen_brutto_pa REAL    NOT NULL,
  zweiteinkommen      INTEGER NOT NULL
);

-- Ein Eintrag je Modelllauf und Cluster: welche Marktmiete, ob der
-- Portfolio-Fixpunkt konvergiert ist (E18). Ein Cluster ohne verwendbare
-- Marktmiete steht hier mit eignung <> 'verwendbar' und bekommt KEINE
-- Empfehlung - Luecke sichtbar statt geschaetzt.
CREATE TABLE modelllauf (
  cluster_id        TEXT PRIMARY KEY,
  datenstand        TEXT,                    -- abruf_datum der Marktmiete
  marktmiete_eur_m2 REAL,
  marktmiete_fallzahl INTEGER,
  eignung           TEXT NOT NULL,
  iterationen       INTEGER,
  konvergiert       INTEGER,                 -- NULL = nicht gerechnet
  leerstand_monate  REAL                     -- Ergebnis des Fixpunkts
);

-- Die Empfehlung je Vertrag im Basisfall. Option ist 'verlaengern' oder
-- 'auslaufen'. Alle Barwerte in EUR ueber fuenf Jahre, diskontiert.
CREATE TABLE empfehlung (
  vertrag_id        TEXT PRIMARY KEY REFERENCES vertrag(vertrag_id),
  option            TEXT NOT NULL,
  aufschlag_pct     REAL,                    -- NULL bei 'auslaufen'
  angebot_eur       REAL,
  angebot_eur_m2    REAL,
  p_annahme         REAL,
  belastungsquote   REAL,
  bw_empfehlung     REAL NOT NULL,           -- Erwartungswert der Option
  bw_nur_index      REAL NOT NULL,           -- Aufschlag 0: Bestandsmiete
  bw_auslaufen      REAL NOT NULL
);

-- Sensitivitaet: dieselbe Optimierung mit je einem Parameter am unteren und
-- oberen Rand seiner Spanne aus config/portfolio.json. Zeigt, ob eine
-- Empfehlung an einer Annahme haengt.
CREATE TABLE empfehlung_sensitivitaet (
  vertrag_id    TEXT NOT NULL REFERENCES vertrag(vertrag_id),
  parameter     TEXT NOT NULL,
  rand          TEXT NOT NULL,               -- unten | oben
  wert          REAL NOT NULL,
  option        TEXT NOT NULL,
  aufschlag_pct REAL,
  PRIMARY KEY (vertrag_id, parameter, rand)
);
