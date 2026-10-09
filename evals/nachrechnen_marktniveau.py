"""Referenzantworten fuer die numerischen Analysen - unabhaengig nachgerechnet.

    python3 evals/nachrechnen_marktniveau.py

Zweitimplementierung mit Absicht: liest die Rohdatei direkt, ohne src/clean.py,
ohne SQL und ohne die Views. Stimmen beide Wege ueberein, ist das eine echte
Kreuzprobe; wuerde dieselbe Funktion zweimal aufgerufen, waere es keine.

Was die Datei NICHT ist: eine Handrechnung. Die Vorgabe verlangt, dass drei
Werte je Abfrage von Hand nachgerechnet werden - mit Taschenrechner, aus der
Rohdatei. Dafuer markiert jeder Fall das Feld 'von_hand_bestaetigt'. Die drei
dafuer vorgesehenen Faelle stehen unten unter 'handproben'.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "data/raw/2026-09-25/wh_1020_mietwohnungen_2026-09-25T1555.json"
ZIEL = WURZEL / "evals/references"
ERFASST = {"wer": "Zweitimplementierung (LLM-gestuetzt), Pruefung durch den "
                  "Studierenden ausstehend",
           "wann": "2026-10-09",
           "wie": "evals/nachrechnen_marktniveau.py liest "
                  "data/raw/2026-09-25/wh_*.json direkt, ohne src/ und ohne SQL"}


def klasse(fl: float) -> str:
    return ("bis 50" if fl < 50 else "50-80" if fl < 80
            else "80-100" if fl <= 100 else "ueber 100")


def lies() -> list[dict]:
    d = json.loads(QUELLE.read_text(encoding="utf-8"))
    ads = d["props"]["pageProps"]["searchResult"]["advertSummaryList"]["advertSummary"]
    out = []
    for a in ads:
        at = {x["name"]: (x["values"][0] if len(x["values"]) == 1 else x["values"])
              for x in a["attributes"]["attribute"]}

        def f(k):
            try:
                return float(str(at.get(k)).replace(",", "."))
            except (TypeError, ValueError):
                return None
        out.append(dict(ad_id=a["id"], status=a["advertStatus"]["description"],
                        plz=at.get("POSTCODE"), miete=f("PRICE"),
                        flaeche=f("ESTATE_SIZE"),
                        privat=at.get("ISPRIVATE") == "1"))
    return out


def faelle() -> dict:
    zeilen = lies()
    aktiv = [z for z in zeilen if z["status"] == "aktiv" and z["miete"] and z["flaeche"]]
    f_marktniveau, f_anbieter = [], []

    for k in ("bis 50", "50-80", "80-100", "ueber 100"):
        g = [z for z in aktiv if klasse(z["flaeche"]) == k]
        w = sorted(round(z["miete"] / z["flaeche"], 6) for z in g)
        n = len(w)
        gew = sum(1 for z in g if not z["privat"])
        f_marktniveau.append({
            "fall_id": f"marktniveau_1020_{k.replace(' ', '_')}",
            "eingabe": {"abfrage": "src/sql/kennzahl_marktniveau.sql",
                        "filter": {"plz": "1020", "groessenklasse": k,
                                   "abruf_datum": "2026-09-25",
                                   "status": "aktiv"}},
            "erwartete_antwort": {
                "fallzahl": n,
                "median_eur_m2": round(statistics.median(w), 2),
                "q1_eur_m2": round(w[(n + 3) // 4 - 1], 2),
                "q3_eur_m2": round(w[(3 * n + 3) // 4 - 1], 2),
                "min_eur_m2": round(w[0], 2),
                "max_eur_m2": round(w[-1], 2),
                "davon_privat": n - gew,
                "davon_gewerblich": gew,
                "belastbarkeit": ("belastbar" if n >= 15 else
                                  "duenn" if n >= 8 else "nicht belastbar")},
            "pruefregel": "numerischer Vergleich",
            "toleranz": {"median_eur_m2": 0.01, "q1_eur_m2": 0.01,
                         "q3_eur_m2": 0.01, "fallzahl": 0},
            "herkunft": ERFASST,
            "von_hand_bestaetigt": False,
            "unsicherheit": (
                "Die Quartile verwenden die Rangformel der Views "
                "(r = (n+3)/4 bzw. (3n+3)/4), nicht lineare Interpolation. "
                "Andere Statistikprogramme liefern bei kleinem n leicht andere "
                "Quartile - gegen diese Referenz zu pruefen heisst, die "
                "Definition der View zu pruefen, nicht 'das Quartil an sich'."),
        })

    for typ, pred in (("privat", lambda z: z["privat"]),
                      ("gewerblich", lambda z: not z["privat"])):
        g = [z for z in aktiv if klasse(z["flaeche"]) == "80-100" and pred(z)]
        w = sorted(round(z["miete"] / z["flaeche"], 6) for z in g)
        f_anbieter.append({
            "fall_id": f"anbietertyp_1020_80-100_{typ}",
            "eingabe": {"abfrage": "src/sql/kennzahl_anbietertyp.sql",
                        "filter": {"plz": "1020", "groessenklasse": "80-100",
                                   "anbietertyp": typ}},
            "erwartete_antwort": {"fallzahl": len(w),
                                  "median_eur_m2": round(statistics.median(w), 2)},
            "pruefregel": "numerischer Vergleich",
            "toleranz": {"median_eur_m2": 0.01, "fallzahl": 0},
            "herkunft": ERFASST,
            "von_hand_bestaetigt": False,
            "unsicherheit": (
                "Drei private Faelle sind keine Stichprobe. Der Fall gehoert "
                "hierher, weil die DIFFERENZ zwischen den Anbietertypen der "
                "Befund ist - nicht, weil der private Median belastbar waere."),
        })

    abdeckung = [{
        "fall_id": "abdeckung_bezirke",
        "eingabe": {"abfrage": "src/sql/kennzahl_abdeckung.sql"},
        "erwartete_antwort": {
            "bezirke_in_konfiguration": 5,
            "bezirke_mit_schnappschuss": 1,
            "beobachtungen_gesamt": len(zeilen),
            "ohne_schnappschuss": ["1010", "1030", "1100", "1220"]},
        "pruefregel": "exakter Vergleich",
        "toleranz": {},
        "herkunft": ERFASST,
        "von_hand_bestaetigt": False,
        "unsicherheit": (
            "Keine. Der Fall prueft, dass die Luecke SICHTBAR bleibt - er "
            "faellt, sobald ein fehlender Bezirk stillschweigend verschwindet."),
    }, {
        "fall_id": "inseratsdauer_nicht_messbar",
        "eingabe": {"abfrage": "src/sql/kennzahl_inseratsdauer.sql"},
        "erwartete_antwort": {
            "zeilen_mit_dauer_ueber_null": 0,
            "anteil_zensiert": 1.0,
            "auswertbar": False,
            "begruendung": "ein einziger Schnappschuss; jede Dauer ist 0 Tage "
                           "und zensiert"},
        "pruefregel": "exakter Vergleich",
        "toleranz": {},
        "herkunft": ERFASST,
        "von_hand_bestaetigt": False,
        "unsicherheit": (
            "Erwartet wird hier ausdruecklich ein NICHT-Ergebnis. Der Fall "
            "ist bestanden, wenn die Abfrage die Unauswertbarkeit meldet, "
            "statt eine Dauer von 0 Tagen als Messwert auszugeben."),
    }]

    z80 = [z for z in aktiv if klasse(z["flaeche"]) == "80-100"]
    w80 = sorted(z80, key=lambda y: y["miete"] / y["flaeche"])
    handproben = []
    for name, idx in (("Median", (len(w80) - 1) // 2),
                      ("Q1", (len(w80) + 3) // 4 - 1),
                      ("Q3", (3 * len(w80) + 3) // 4 - 1)):
        x = w80[idx]
        handproben.append({
            "rolle": name, "ad_id": x["ad_id"],
            "rechnung": f"{x['miete']:.2f} / {x['flaeche']:.2f}",
            "erwartet_eur_m2": round(x["miete"] / x["flaeche"], 4),
            "von_hand_bestaetigt": False})

    return {"marktniveau": f_marktniveau, "anbietertyp": f_anbieter,
            "abdeckung_und_dauer": abdeckung, "handproben": handproben,
            "basis": {"inserate": len(zeilen), "aktiv_mit_miete_und_flaeche": len(aktiv)}}


def schreiben() -> None:
    d = faelle()
    kopf = {
        "_zweck": "Referenzantworten fuer Schritt 4. Sie existieren VOR dem "
                  "Modell und sind der Maßstab, an dem spaeter gemessen wird.",
        "_quelle": "data/raw/2026-09-25/wh_1020_mietwohnungen_2026-09-25T1555.json",
        "_erzeugt_von": "evals/nachrechnen_marktniveau.py",
        "_warnung": "Diese Datei wird nicht von Hand bearbeitet. Wer eine "
                    "Handprobe bestaetigt, setzt 'von_hand_bestaetigt' im Skript "
                    "und laesst es neu laufen.",
    }
    for name, inhalt in (("marktniveau", d["marktniveau"]),
                         ("anbietertyp", d["anbietertyp"]),
                         ("abdeckung_und_dauer", d["abdeckung_und_dauer"])):
        ZIEL.mkdir(parents=True, exist_ok=True)
        (ZIEL / f"{name}.json").write_text(
            json.dumps({**kopf, "faelle": inhalt}, ensure_ascii=False, indent=1)
            + "\n", encoding="utf-8")
        print(f"  {len(inhalt)} Fall/Faelle -> evals/references/{name}.json")
    (ZIEL / "handproben.json").write_text(
        json.dumps({**kopf,
                    "_zweck": "Die drei Werte, die laut Vorgabe von Hand "
                              "nachzurechnen sind. Taschenrechner genuegt.",
                    "faelle": d["handproben"]}, ensure_ascii=False, indent=1)
        + "\n", encoding="utf-8")
    print(f"  {len(d['handproben'])} Handproben -> evals/references/handproben.json")
    print(f"  Basis: {d['basis']}")


if __name__ == "__main__":
    schreiben()
    sys.exit(0)
