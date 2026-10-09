"""Zentrale Konfiguration: Quellen, Leseeinstellungen, PII-Regeln, Pfade.

Alles, was sich beim Wechsel auf andere Daten aendert, steht hier und nirgends
sonst. Die Pipeline nimmt den neuesten Datumsordner unter data/raw/.
"""
from __future__ import annotations

import json
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
RAW = WURZEL / "data" / "raw"
INTERIM = WURZEL / "data" / "interim"
PROCESSED = WURZEL / "data" / "processed"
SAMPLE = WURZEL / "data" / "sample"
SQL = Path(__file__).resolve().parent / "sql"
PROJEKT = "mietportfolio"          # Name des Projekts und der Datenbankdatei
DB = PROCESSED / f"{PROJEKT}.sqlite"

# ─────────────────────────────────────────────────────────────── Quellen
#
# leser: welche Funktion in src/clean.py die Datei verarbeitet
# muster: Dateinamensmuster im Rohordner (glob)
# pflicht: fehlt die Quelle, bricht die Pipeline ab
#
# Der willhaben-Abruf ist manuell. Grund: die robots.txt der Seite verbietet
# automatisierten Zugriff ausdruecklich (docs/projektdokumentation/
# 02_schritt1_datenzugriff.md). tools/snapshot.js hilft beim Speichern und
# bricht ab, wenn die Seite nicht zur URL passt.
QUELLEN = {
    "willhaben": {
        "muster": "wh_*.json",
        "leser": "willhaben",
        "form": "JSON (__NEXT_DATA__ einer Next.js-Suchseite)",
        "beschaffung": "manuell im Browser gespeichert",
        "lizenz": "Nutzung nur als unwesentlicher Teil; robots.txt archiviert",
        "pflicht": True,
    },
    "tariflohnindex": {
        "muster": "tli_*.csv",
        "leser": "tariflohnindex",
        "form": "CSV, Statistik Austria OGD",
        "beschaffung": "automatisch, data.statistik.gv.at",
        "lizenz": "CC-BY 4.0",
        "pflicht": False,
    },
    "vpi": {
        "muster": "vpi_*.csv",
        "leser": "vpi",
        "form": "CSV, Statistik Austria OGD",
        "beschaffung": "automatisch, data.statistik.gv.at",
        "lizenz": "CC-BY 4.0",
        "pflicht": False,
    },
}

# ─────────────────────────────────────────────────────────────── PII
#
# Allowlist statt Blocklist: was nicht ausdruecklich erlaubt ist, wird
# verworfen. Eine Blocklist waere die falsche Richtung, weil sie bei jedem
# neuen Feld von willhaben stillschweigend durchlaesst.
#
# Die Entfernung passiert in src/clean.py, nicht spaeter im Prompt.
PII_ERLAUBT = frozenset({
    "ad_id", "abruf_ts", "status", "plz", "bezirk", "lage",
    "miete_eur", "flaeche_m2", "wohnflaeche_m2", "eur_pro_m2",
    "zimmer", "stock", "objekttyp", "freiflaeche",
    "privat", "gewerblich_anbieter", "veroeffentlicht", "lagequalitaet",
})

# Was verworfen wird, mit Begruendung fuer die Dokumentation.
PII_VERWORFEN = {
    "seo_url": "enthaelt den Inseratstitel und fuehrt auf das Anbieterprofil",
    "orgname": "Firmenname, haeufig mit Personennamen",
    "orgid": "Kennung des Anbieterprofils",
    "org_uuid": "Kennung des Anbieterprofils",
    "advertiser_ref": "Referenz des Anbieters",
    "advertiserinfo": "Anbieterlabel, haeufig mit Personennamen",
    "body_dyn": "Freitext mit moeglichen Kontaktdaten",
    "description": "Inseratstitel, potenziell mit Kontaktdaten",
    "heading": "wie description",
    "coordinates": "punktgenaue Koordinate der Wohnung; PLZ genuegt uns",
    "address": "Strassenname; PLZ genuegt uns",
    "all_image_urls": "Bilder, nicht benoetigt",
    "mmo": "Bildpfad",
}

# ─────────────────────────────────────────────── Bezirke und Cluster
#
# rolle 'portfolio': dort halten wir Wohnungen, die Marktmiete geht in die
#                    Entscheidung ein
# rolle 'referenz' : liefert nur Marktkontext
BEZIRKE = [
    {"plz": "1020", "bezirk_nr": 2,  "bezirk_name": "Leopoldstadt",
     "cluster_id": "NORDBAHN", "rolle": "portfolio"},
    {"plz": "1100", "bezirk_nr": 10, "bezirk_name": "Favoriten",
     "cluster_id": "SONNWEND", "rolle": "portfolio"},
    {"plz": "1220", "bezirk_nr": 22, "bezirk_name": "Donaustadt",
     "cluster_id": "SEESTADT", "rolle": "portfolio"},
    {"plz": "1010", "bezirk_nr": 1,  "bezirk_name": "Innere Stadt",
     "cluster_id": None, "rolle": "referenz"},
    {"plz": "1030", "bezirk_nr": 3,  "bezirk_name": "Landstrasse",
     "cluster_id": None, "rolle": "referenz"},
]

# ─────────────────────────────────────────────── Datenausschluesse
# Objekttypen, die kein Wohnungsangebot sind. Die Beobachtung bleibt in der
# Faktentabelle; nur v_angebot (und damit jede Kennzahl) laesst sie aus.
# Jeder Eintrag braucht einen Grund - er steht in der Datenbank
# (objekttyp_ausschluss) und im Entscheidungslog.
OBJEKTTYP_AUSGESCHLOSSEN = {
    "Zimmer/WG": "Miete gilt fuer ein Zimmer, Flaeche fuer die ganze Wohnung - "
                 "der Quadratmeterpreis ist bedeutungslos (09.10.: 699 EUR "
                 "bei 100 m2 = 6,99 EUR/m2 im Zielsegment)",
}

# ─────────────────────────────────────────────── Qualitaetsschwellen
SCHWELLEN = {
    "min_inserate_je_schnappschuss": 20,
    "min_fallzahl_belastbar": 15,
    "min_fallzahl_duenn": 8,
    "max_treffer_bezirkssuche": 100_000,
    "min_anteil_gleiche_plz": 0.9,
    "min_feldabdeckung": 0.9,
    "eval_schwelle": 0.80,
}

ZIELSEGMENT = "80-100"   # Groessenklasse des Portfolios


def neuester_rohordner() -> Path:
    """Der Ordner mit dem jüngsten Abrufdatum unter data/raw/."""
    ordner = sorted(p for p in RAW.iterdir() if p.is_dir()) if RAW.exists() else []
    if not ordner:
        raise SystemExit(
            f"kein Datumsordner unter {RAW}. Anlegen als data/raw/<JJJJ-MM-TT>/ "
            f"und die Rohdateien hineinlegen (siehe README).")
    return ordner[-1]


def alle_rohordner() -> list[Path]:
    """Alle Datumsordner, aufsteigend.

    Die Pipeline baut die Datenbank aus ALLEN Ordnern neu. Damit ist jeder
    Lauf reproduzierbar (gleiche Zahlen bei zweitem Lauf) und die Historie
    bleibt trotzdem vollstaendig - Voraussetzung dafuer, dass Preisaenderung
    und Inseratsdauer messbar werden.
    """
    if not RAW.exists():
        return []
    return sorted(p for p in RAW.iterdir() if p.is_dir())


def modellparameter() -> dict:
    """Die Annahmen des Entscheidungsmodells als flaches Dict."""
    cfg = json.loads((WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    return {k: v["wert"] for k, v in cfg["annahmen"].items()}
