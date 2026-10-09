"""Schritt 2: je Quelle eine saubere Tabelle.

Eine Funktion je Quelle. Jede zaehlt, was sie getan hat, und gibt die Zahlen
zurueck - das ist der Qualitaetsbericht in Zahlen.

Die Stellen, an denen Entscheidungen fallen, stehen oben in dieser Datei:
normalisieren von Zahlen, Datumsangaben und Schluesseln. Falsch entschieden
sieht eine Umwandlung unauffaellig aus.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from . import config as C
from . import validierung as V
from . import wh_next_data as WH

# ───────────────────────────────────────────── Umwandlungsentscheidungen

LUECKE_TEXT = {"", "-", "--", "n/a", "na", "nan", "luecke", "lücke",
               "#bezug!", "#wert!", "#div/0!"}
LUECKE_ZAHL = {-777.0, -999.0, -9999.0}


def to_number(value) -> float | None:
    """'1 234,56' und '1.234,56' -> 1234.56 · '0,76-' -> -0.76 · '' -> None.

    ENTSCHEIDUNG: ein Punkt gilt nur dann als Tausenderpunkt, wenn auch ein
    Komma vorkommt. willhaben liefert '24.791666' als Dezimalpunkt - ohne
    diese Regel wuerde daraus 24791666.

    Nachgestelltes Minus ('0,76-') kommt in oesterreichischen Abrechnungen
    fuer Rabatte vor.
    """
    if value is None or isinstance(value, (list, dict)):
        return None
    t = str(value).strip().replace("\xa0", "").replace(" ", "")
    if t.lower() in LUECKE_TEXT:
        return None
    negativ = t.endswith("-")
    if negativ:
        t = t[:-1]
    if "," in t and "." in t:
        t = t.replace(".", "")      # Punkt ist Tausendertrenner
    t = t.replace(",", ".")
    try:
        v = float(t)
    except ValueError:
        return None
    if v in LUECKE_ZAHL:
        return None
    return -v if negativ else v


def to_date(value) -> date | None:
    """'04.06.2025' -> 2025-06-04 (TAG ZUERST) · ISO · Excel-Seriennummer."""
    if value is None:
        return None
    t = str(value).strip()
    if not t or t.lower() in LUECKE_TEXT:
        return None
    if m := re.match(r"^(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", t):
        tag, monat, jahr = m.groups()
        try:
            return date(int(jahr), int(monat), int(tag))
        except ValueError:
            return None
    if m := re.match(r"^(\d{4})-(\d{2})-(\d{2})", t):
        return date(*map(int, m.groups()))
    if t.isdigit() and 20000 < int(t) < 60000:      # Excel-Serie ab 1900
        from datetime import timedelta
        return date(1899, 12, 30) + timedelta(days=int(t))
    return None


def normalize_plz(value) -> str | None:
    """Wiener PLZ vierstellig, nichts anderes."""
    if value is None:
        return None
    m = re.search(r"\b(\d{4})\b", str(value))
    return m.group(1) if m else None


# ───────────────────────────────────────────────────────── PII entfernen

def drop_pii(zeile: dict) -> tuple[dict, list[str]]:
    """Allowlist anwenden. Rueckgabe: (behalten, verworfene Feldnamen)."""
    behalten = {k: v for k, v in zeile.items() if k in C.PII_ERLAUBT}
    verworfen = sorted(k for k in zeile if k not in C.PII_ERLAUBT)
    return behalten, verworfen


TEL = re.compile(r"(?:\+\d{1,3}[\s/\-]?)?(?:\(?\d{2,4}\)?[\s/\-]?){2,}\d{2,}")
MAIL = re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}")
URL = re.compile(r"(?:https?://|www\.)\S+")
# Eigene technische Felder, keine Quelldaten: der Dateiname enthaelt
# Zifferngruppen (wh_1020_..._2026-09-25T1555) und sah fuer den
# Telefonmuster-Test wie eine Nummer aus. Bewusst ausgenommen, statt das
# Muster aufzuweichen - ein loses Muster findet die echten Faelle nicht mehr.
PII_UNVERDAECHTIG = {"plz", "ad_id", "abruf_ts", "veroeffentlicht",
                     "snapshot_datei", "status", "objekttyp", "freiflaeche"}


def redigiere_text(s: str | None) -> tuple[str | None, list[str]]:
    """Ersetzt Kontaktmuster in Freitext durch Platzhalter.

    Rueckgabe: (bereinigter Text, Trefferarten). Die Trefferliste geht in den
    Qualitaetsbericht - ein stiller Filter waere schlechter als einer, dessen
    Arbeit man sieht.

    Wird fuer die strukturierten willhaben-Felder nicht gebraucht, weil die
    Allowlist alle Freitextfelder verwirft. Gebraucht wird sie fuer den
    unstrukturierten Teil (Kollektivvertrags- und Gesetzestexte), der in den
    LLM-Schritt geht.
    """
    if not s:
        return s, []
    treffer, out = [], s
    for name, pat, ers in (("email", MAIL, "[E-MAIL ENTFERNT]"),
                           ("url", URL, "[URL ENTFERNT]"),
                           ("telefon", TEL, "[TELEFON ENTFERNT]")):
        neu_text, n = pat.subn(ers, out)
        if n:
            treffer.append(name)
            out = neu_text
    return out, treffer


def pii_kontrolle(zeilen: list[dict]) -> list[str]:
    """Letzter Schutz vor dem Schreiben: Kontaktmuster in allen Werten.

    Ein Treffer ist ein Fehler, keine Warnung - dann stimmt etwas an der
    Allowlist nicht.
    """
    befunde = []
    for i, z in enumerate(zeilen):
        for k, v in z.items():
            if not isinstance(v, str) or k in PII_UNVERDAECHTIG:
                continue
            if MAIL.search(v):
                befunde.append(f"Zeile {i}, Feld {k}: E-Mail-Muster")
            if URL.search(v):
                befunde.append(f"Zeile {i}, Feld {k}: URL")
            if len(v) > 6 and TEL.search(v):
                befunde.append(f"Zeile {i}, Feld {k}: Telefonmuster")
    return befunde


# ───────────────────────────────────────────────── Quelle: willhaben

def willhaben(interim: Path | None = None) -> dict:
    """Liest alle willhaben-Schnappschuesse aus data/interim/.

    Je Datei laeuft das Eingangs-Gate (src/validierung.py). Eine abgelehnte
    Datei wird gezaehlt und benannt, nicht stillschweigend verworfen und
    nicht geschrieben.
    """
    interim = interim or C.INTERIM
    prov = json.loads((interim / "provenienz.json").read_text(encoding="utf-8"))
    dateien = [d for d in prov["dateien"] if d["quelle"] == "willhaben"]

    zeilen: list[dict] = []
    schnappschuesse: list[dict] = []
    abgelehnt: list[dict] = []
    verworfene_felder: set[str] = set()
    gesehen_sha: dict[str, str] = {}

    for eintrag in dateien:
        pfad = C.WURZEL / eintrag["pfad_interim"]
        erwartete_plz = V.plz_aus_dateiname(pfad)
        s = WH.parse(pfad)

        befunde = V.pruefe(s, erwartete_plz=erwartete_plz,
                           min_inserate=C.SCHWELLEN["min_inserate_je_schnappschuss"])
        if eintrag["sha256"] in gesehen_sha:
            befunde.append(V.Befund(
                "fehler", "Inhalt schon vorhanden",
                f"byteweise identisch mit {gesehen_sha[eintrag['sha256']]}"))
        if erwartete_plz is None:
            befunde.append(V.Befund(
                "warnung", "PLZ aus Dateiname",
                "keine vierstellige PLZ im Dateinamen - Konvention "
                "wh_<plz>_<suche>_<datum>.json"))

        if not V.bestanden(befunde):
            abgelehnt.append({
                "datei": eintrag["datei"],
                "gruende": [f"{b.pruefung}: {b.detail}"
                            for b in befunde if b.stufe == "fehler"]})
            continue

        gesehen_sha[eintrag["sha256"]] = eintrag["datei"]
        plz_schnapp = erwartete_plz or normalize_plz(s.inserate[0].plz)

        for ins in s.inserate:
            roh = asdict(ins)
            roh["plz"] = normalize_plz(roh.get("plz"))
            roh["miete_eur"] = to_number(roh.get("miete_eur"))
            roh["flaeche_m2"] = to_number(roh.get("flaeche_m2"))
            roh["wohnflaeche_m2"] = to_number(roh.get("wohnflaeche_m2"))
            roh["eur_pro_m2"] = to_number(roh.get("eur_pro_m2"))
            roh["zimmer"] = to_number(roh.get("zimmer"))
            sauber, weg = drop_pii(roh)
            verworfene_felder.update(weg)
            sauber["snapshot_datei"] = eintrag["datei"]
            sauber["freiflaeche"] = (";".join(sauber["freiflaeche"])
                                     if sauber.get("freiflaeche") else None)
            zeilen.append(sauber)

        schnappschuesse.append({
            "datei": eintrag["datei"],
            "sha256": eintrag["sha256"],
            "abruf_ts": s.abruf_ts,
            "plz": plz_schnapp,
            "treffer_gesamt": s.treffer_gesamt,
            "geliefert": s.geliefert,
            "vollstaendig": int(s.vollstaendig),
            "warnungen": [f"{b.pruefung}: {b.detail}"
                          for b in befunde if b.stufe == "warnung"],
        })

    # letzte PII-Kontrolle vor der Rueckgabe
    pii_treffer = pii_kontrolle(zeilen)
    if pii_treffer:
        raise SystemExit("PII-Kontrolle fehlgeschlagen:\n  "
                         + "\n  ".join(pii_treffer[:10]))

    ohne_flaeche = sum(1 for z in zeilen if z["flaeche_m2"] is None)
    reserviert = sum(1 for z in zeilen if z["status"] != "aktiv")
    teilseiten = sum(1 for s in schnappschuesse if not s["vollstaendig"])

    print(f"clean willhaben: {len(schnappschuesse)} Schnappschuss/e "
          f"aufgenommen, {len(abgelehnt)} abgelehnt, {len(zeilen)} Inserate; "
          f"{ohne_flaeche} ohne Flaeche, {reserviert} reserviert, "
          f"{teilseiten} Teilseite(n); "
          f"{len(verworfene_felder)} Feld(er) als PII verworfen "
          f"({', '.join(sorted(verworfene_felder))})")
    for a in abgelehnt:
        print(f"                 ABGELEHNT {a['datei']}")
        for g in a["gruende"]:
            print(f"                   {g}")

    return {
        "zeilen": zeilen,
        "schnappschuesse": schnappschuesse,
        "abgelehnt": abgelehnt,
        "zahlen": {
            "schnappschuesse": len(schnappschuesse),
            "abgelehnt": len(abgelehnt),
            "inserate": len(zeilen),
            "ohne_flaeche": ohne_flaeche,
            "reserviert": reserviert,
            "teilseiten": teilseiten,
            "pii_felder_verworfen": sorted(verworfene_felder),
        },
    }


# ───────────────────────────────────── Quellen: Tariflohnindex, VPI

def _index_csv(interim: Path, quelle: str, reihe_spalte: str) -> dict:
    """Gemeinsamer Leser fuer die beiden OGD-Indexreihen.

    Noch nicht verdrahtet: die CSV liegt bis zur Beschaffung nicht vor. Der
    Leser ist da, damit der Platz im Datenmodell sichtbar bleibt statt als
    stillschweigende Luecke.
    """
    prov_pfad = interim / "provenienz.json"
    if not prov_pfad.exists():
        return {"zeilen": [], "zahlen": {"status": "keine Provenienz"}}
    prov = json.loads(prov_pfad.read_text(encoding="utf-8"))
    dateien = [d for d in prov["dateien"] if d["quelle"] == quelle]
    if not dateien:
        print(f"clean {quelle}: keine Datei vorhanden - uebersprungen")
        return {"zeilen": [], "zahlen": {"status": "nicht beschafft"}}

    import csv
    zeilen = []
    for eintrag in dateien:
        pfad = C.WURZEL / eintrag["pfad_interim"]
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f, delimiter=";"):
                reihe = row.get(reihe_spalte)
                jahr = to_number(row.get("jahr") or row.get("C-A10TLI-0"))
                wert = to_number(row.get("wert") or row.get("F-TLI"))
                if reihe and jahr and wert:
                    zeilen.append({"reihe": reihe, "jahr": int(jahr),
                                   "indexwert": wert, "quelle": quelle})
    print(f"clean {quelle}: {len(zeilen)} Jahreswerte")
    return {"zeilen": zeilen, "zahlen": {"jahreswerte": len(zeilen)}}


def tariflohnindex(interim: Path | None = None) -> dict:
    return _index_csv(interim or C.INTERIM, "tariflohnindex", "kollektivvertrag")


def vpi(interim: Path | None = None) -> dict:
    return _index_csv(interim or C.INTERIM, "vpi", "reihe")


# ───────────────────────────────────────────────────────────── Sammler

LESER = {
    "willhaben": willhaben,
    "tariflohnindex": tariflohnindex,
    "vpi": vpi,
}


def ausfuehren(interim: Path | None = None) -> dict:
    """Alle konfigurierten Quellen bereinigen."""
    out = {}
    for quelle, cfg in C.QUELLEN.items():
        out[quelle] = LESER[cfg["leser"]](interim)
    return out


if __name__ == "__main__":
    ausfuehren()
