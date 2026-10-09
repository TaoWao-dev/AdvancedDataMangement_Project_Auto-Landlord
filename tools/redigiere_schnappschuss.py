"""Schnappschuss auf das reduzieren, was die Pipeline braucht.

    python3 tools/redigiere_schnappschuss.py <quelle.json> <ziel.json>

Warum das noetig ist
--------------------
Eine gespeicherte willhaben-Ergebnisseite enthaelt deutlich mehr als die
Inserate. Zwei Funde aus dem geprueften Schnappschuss:

  props.pageProps.searchResult.dmpUserIdentities.wh_uuid
      eine Kennung des BROWSERS, mit dem gespeichert wurde. Sie beschreibt
      nicht den Markt, sondern die Person am Rechner.

  ORGNAME, advertiserInfo.label, ADVERTISER_REF, ORGID, ORG_UUID, ADDRESS,
  COORDINATES, BODY_DYN, HEADING, description
      Anbieterangaben, haeufig mit Personennamen ("MMI Mario Molnar
      Immobilienberatung", "Realbuero Dr. C. Huber"), dazu Freitexte und
      punktgenaue Koordinaten.

Die Pipeline verwirft all das ohnehin (Allowlist, Entscheidungslog E11) - aber
erst NACH dem Einlesen. Die Rohdatei selbst traegt es weiter, und ein Git-Push
traegt es unwiderruflich in die Historie. Die Vorgabe der Lehrveranstaltung
lautet: keine personenbezogenen Daten, nirgends.

Was diese Redaktion tut
-----------------------
Sie erhaelt die Struktur und die Feldnamen, ersetzt aber die Werte der nicht
gebrauchten Felder durch "[ENTFERNT]". Feldnamen zu behalten ist Absicht: sie
belegen, was die Quelle liefert, ohne den Inhalt zu verbreiten.

Eine Ausnahme mit Begruendung: advertiserInfo.label wird nicht auf
"[ENTFERNT]" gesetzt, sondern auf "Privat" beziehungsweise "[GEWERBLICH]".
Der Parser leitet daraus die Unterscheidung privat/gewerblich ab, und die ist
eine Analysegroesse - der gewerbliche Median liegt 16 % ueber dem privaten.
Die Unterscheidung bleibt, der Name verschwindet.

Die unveraenderte Datei bleibt beim Menschen, der sie gespeichert hat. Ihr
SHA256 steht in data/raw/<datum>/HERKUNFT.md - damit ist nachweisbar, dass die
redigierte Fassung aus ihr entstanden ist.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import wh_next_data as WH  # noqa: E402

ENTFERNT = "[ENTFERNT]"

# Attribute, deren WERT die Pipeline liest (src/wh_next_data.parse).
ATTRIBUTE_BEHALTEN = {
    "ADID", "POSTCODE", "DISTRICT", "LOCATION", "PRICE", "ESTATE_SIZE",
    "ESTATE_SIZE/LIVING_AREA", "PRICE/SQUARE_METER", "NUMBER_OF_ROOMS",
    "FLOOR", "PROPERTY_TYPE", "FREE_AREA_TYPE_NAME", "ISPRIVATE",
    "PUBLISHED_String", "LOCATION_QUALITY",
}

# Schluessel von searchResult, die das Gate und der Parser brauchen.
SUCHE_BEHALTEN = {"searchDate", "rowsFound", "rowsRequested", "rowsReturned",
                  "verticalId", "heading", "searchId"}

# Schluessel je Inserat, die erhalten bleiben.
INSERAT_BEHALTEN = {"id", "verticalId", "advertStatus", "advertiserInfo",
                    "attributes"}


def _attribut(a: dict) -> dict:
    name = a.get("name")
    if name in ATTRIBUTE_BEHALTEN:
        return {"name": name, "values": a.get("values") or []}
    return {"name": name, "values": [ENTFERNT]}


def _inserat(ad: dict) -> dict:
    label = (ad.get("advertiserInfo") or {}).get("label")
    return {
        "id": ad.get("id"),
        "verticalId": ad.get("verticalId"),
        "advertStatus": {"id": (ad.get("advertStatus") or {}).get("id"),
                         "description": (ad.get("advertStatus") or {})
                         .get("description")},
        # Nur die Unterscheidung, nicht der Name. Siehe Modulkopf.
        "advertiserInfo": {"label": "Privat" if label == "Privat"
                           else ("[GEWERBLICH]" if label else None)},
        "attributes": {"attribute": [
            _attribut(a) for a in ad.get("attributes", {}).get("attribute", [])]},
        "description": ENTFERNT,
        "selfLink": ENTFERNT,
    }


def redigiere(quelle: Path, ziel: Path) -> dict:
    roh = WH.lade_rohdaten(quelle)
    sr = roh["props"]["pageProps"]["searchResult"]
    ads = sr.get("advertSummaryList", {}).get("advertSummary", []) or []

    sha_original = hashlib.sha256(quelle.read_bytes()).hexdigest()
    entfernte_suchfelder = sorted(k for k in sr if k not in SUCHE_BEHALTEN
                                  and k != "advertSummaryList")
    entfernte_inseratsfelder = sorted(
        {k for ad in ads for k in ad} - INSERAT_BEHALTEN)
    entfernte_attribute = sorted(
        {a.get("name") for ad in ads
         for a in ad.get("attributes", {}).get("attribute", [])}
        - ATTRIBUTE_BEHALTEN)

    neu = {
        "_redaktion": {
            "werkzeug": "tools/redigiere_schnappschuss.py",
            "quelle_datei": quelle.name,
            "quelle_sha256": sha_original,
            "hinweis": "Reduzierte Fassung. Werte nicht benoetigter Felder "
                       "sind durch [ENTFERNT] ersetzt, Feldnamen bleiben "
                       "stehen. Die unveraenderte Datei liegt nicht im "
                       "Repository; Begruendung in der Modul-Dokumentation "
                       "und in docs/projektdokumentation/02_schritt1_datenzugriff.md.",
            "entfernte_suchfelder": entfernte_suchfelder,
            "entfernte_inseratsfelder": entfernte_inseratsfelder,
            "entfernte_attributwerte": entfernte_attribute,
        },
        "props": {"pageProps": {"searchResult": {
            **{k: sr.get(k) for k in SUCHE_BEHALTEN if k in sr},
            "advertSummaryList": {"advertSummary": [_inserat(a) for a in ads]},
        }}},
    }

    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(neu, ensure_ascii=False, indent=1),
                    encoding="utf-8")

    # Kontrolle: der Parser muss aus der redigierten Fassung dasselbe lesen.
    alt, jung = WH.parse(quelle), WH.parse(ziel)
    gleich = (len(alt.inserate) == len(jung.inserate)
              and alt.treffer_gesamt == jung.treffer_gesamt
              and alt.abruf_ts == jung.abruf_ts
              and sum(1 for i in alt.inserate if i.privat)
              == sum(1 for i in jung.inserate if i.privat)
              and sum(1 for i in alt.inserate if i.gewerblich_anbieter)
              == sum(1 for i in jung.inserate if i.gewerblich_anbieter))
    return {
        "quelle_sha256": sha_original,
        "ziel_sha256": hashlib.sha256(ziel.read_bytes()).hexdigest(),
        "bytes_vorher": quelle.stat().st_size,
        "bytes_nachher": ziel.stat().st_size,
        "inserate": len(jung.inserate),
        "gleiche_lesung": gleich,
        "entfernte_attributwerte": len(entfernte_attribute),
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    r = redigiere(Path(sys.argv[1]), Path(sys.argv[2]))
    for k, v in r.items():
        print(f"  {k:<24} {v}")
    if not r["gleiche_lesung"]:
        print("\n  FEHLER: der Parser liest aus der redigierten Fassung etwas "
              "anderes. Nicht verwenden.")
        sys.exit(2)
