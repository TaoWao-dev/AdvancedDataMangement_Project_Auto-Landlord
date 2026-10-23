"""Schritt 5: das Entscheidungsmodell an die Daten anschliessen.

Liest die Marktmiete je Cluster aus der Datenbank (v_cluster_marktmiete,
also aus SQL), rechnet je Vertrag die Empfehlung mit src/entscheidung.py und
schreibt das Ergebnis in die Tabellen modelllauf, empfehlung und
empfehlung_sensitivitaet zurueck. Was danach in der Vorlage steht, kommt
wieder aus SQL (kennzahl_empfehlung*.sql) - die Arithmetik liegt in Python,
weil sie iteriert, nicht weil die Zahlen am SQL vorbei sollen.

Portfolio-Fixpunkt (E18). Wer viele aehnliche Wohnungen im selben Quartal
neu vermietet, konkurriert mit sich selbst: der Leerstand je Neuvermietung
steigt mit der Zahl der erwarteten Auszuege im Cluster und Quartal. Die
erwarteten Auszuege haengen aber von den Angeboten ab, und die Angebote vom
Leerstand. Deshalb wird iteriert, mit 50/50-Daempfung - ungedaempft
pendelte die erste Fassung zwischen zwei Zustaenden. Konvergiert der Lauf
nicht, steht das in modelllauf.konvergiert, und Gate 3 laesst keine Vorlage
entstehen. Ein Zwischenstand ist kein Ergebnis.

Ein Cluster ohne verwendbare Marktmiete bekommt keine Empfehlung. Es steht
in modelllauf mit seiner eignung - die Luecke bleibt sichtbar.
"""
from __future__ import annotations

import json
import sqlite3

from . import config as C
from .entscheidung import bewerten

DAEMPFUNG = 0.5
TOLERANZ_MONATE = 0.01
MAX_ITER = 50

# Parameter, deren Rand die Sensitivitaet durchspielt. Die Spannen kommen
# aus config/portfolio.json; die Marktmiete wird zusaetzlich mit Q1 und Q3
# aus derselben Kennzahlzeile gerechnet.
SENSITIVE = ["wechselbereitschaft_k", "leerstand_monate", "marktrisiko_abschlag",
             "umzugskosten_eur", "belastungsquote_schmerzgrenze"]


def parameter_laden() -> tuple[dict, list[float]]:
    port = json.loads((C.WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    par = {k: v["wert"] for k, v in port["annahmen"].items()}
    spannen = {k: v["sensitivitaet"] for k, v in port["annahmen"].items()}
    par["_spannen"] = spannen
    return par, port["angebotsraster"]["aufschlaege_pct"]


def vertraege_laden() -> list[dict]:
    return json.loads((C.WURZEL / "config" / "vertraege.json")
                      .read_text(encoding="utf-8"))["vertraege"]


def quartal(vertragsende: str) -> int:
    return (int(vertragsende[5:7]) - 1) // 3 + 1


def beste_option(v: dict, markt: float, par: dict, raster: list[float],
                 leerstand: float) -> dict:
    """Bestes Angebot im Raster gegen 'auslaufen lassen'.

    'Auslaufen' heisst: kein Angebot, sicher neu vermieten. Sein Barwert ist
    bw_auszug - unabhaengig vom Angebot. Es gewinnt nur, wenn jedes Angebot
    im Erwartungswert schlechter ist als der sichere Auszug.
    """
    szen = [bewerten(v["miete_aktuell_eur"], v["flaeche_m2"], markt,
                     v["einkommen_brutto_pa"], v["zweiteinkommen"], a, par,
                     leerstand_monate=leerstand) for a in raster]
    # Bei Gleichstand das niedrigere Angebot: gleicher Erwartungswert mit
    # hoeherer Annahmewahrscheinlichkeit ist das geringere Risiko.
    bestes = max(szen, key=lambda s: (s.bw_erwartet, -s.aufschlag_pct))
    null = next(s for s in szen if s.aufschlag_pct == 0)
    if bestes.bw_auszug > bestes.bw_erwartet:
        return {"option": "auslaufen", "szenario": None, "p": 0.0,
                "bw": bestes.bw_auszug, "bw_null": null.bw_erwartet,
                "bw_auslaufen": bestes.bw_auszug}
    return {"option": "verlaengern", "szenario": bestes, "p": bestes.p,
            "bw": bestes.bw_erwartet, "bw_null": null.bw_erwartet,
            "bw_auslaufen": bestes.bw_auszug}


def fixpunkt(vertraege: list[dict], markt: float, par: dict,
             raster: list[float]) -> tuple[dict, dict, int, bool]:
    """Leerstand je Quartal, bis Angebote und erwartete Auszuege zusammenpassen."""
    basis = par["leerstand_monate"]
    zuschlag = par["leerstand_zuschlag_je_gleichzeitiger_neuvermietung"]
    leer = {quartal(v["vertragsende"]): basis for v in vertraege}
    ergebnis: dict = {}
    for it in range(1, MAX_ITER + 1):
        ergebnis = {v["vertrag_id"]: beste_option(v, markt, par, raster,
                                                  leer[quartal(v["vertragsende"])])
                    for v in vertraege}
        auszuege: dict[int, float] = {q: 0.0 for q in leer}
        for v in vertraege:
            auszuege[quartal(v["vertragsende"])] += 1.0 - ergebnis[v["vertrag_id"]]["p"]
        # Die erste Neuvermietung je Quartal ist der Normalfall (Basis); erst
        # jede weitere konkurriert mit ihr.
        ziel = {q: basis + zuschlag * max(0.0, auszuege[q] - 1.0) for q in leer}
        neu = {q: DAEMPFUNG * leer[q] + (1 - DAEMPFUNG) * ziel[q] for q in leer}
        delta = max(abs(neu[q] - leer[q]) for q in leer)
        leer = neu
        if delta < TOLERANZ_MONATE:
            return ergebnis, leer, it, True
    return ergebnis, leer, MAX_ITER, False


def ausfuehren(con: sqlite3.Connection) -> dict:
    par, raster = parameter_laden()
    vertraege = vertraege_laden()

    con.executemany(
        "INSERT INTO vertrag VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(v["vertrag_id"], v["cluster_id"], v["flaeche_m2"], v["abschluss_jahr"],
          v["vertragsende"], int(v["wertsicherung"]), v["miete_aktuell_eur"],
          v["berufsgruppe"], v["einkommen_brutto_pa"], int(v["zweiteinkommen"]))
         for v in vertraege])

    markt = {r["cluster_id"]: dict(r) for r in con.execute(
        """SELECT c.cluster_id, c.abruf_datum, c.median_eur_m2, c.fallzahl, c.eignung,
                  b.q1_eur_m2, b.q3_eur_m2
           FROM v_cluster_marktmiete c
           LEFT JOIN v_bezirksvergleich b ON b.plz = c.plz""")}

    zahlen = {"cluster_gerechnet": 0, "cluster_ohne_markt": 0,
              "empfehlungen": 0, "nicht_konvergiert": 0}
    for cid in sorted({v["cluster_id"] for v in vertraege}):
        m = markt.get(cid, {"eignung": "kein Schnappschuss"})
        if m.get("eignung") != "verwendbar":
            con.execute("INSERT INTO modelllauf VALUES (?,?,?,?,?,?,?,?)",
                        (cid, m.get("abruf_datum"), m.get("median_eur_m2"),
                         m.get("fallzahl"), m.get("eignung") or "kein Schnappschuss",
                         None, None, None))
            zahlen["cluster_ohne_markt"] += 1
            print(f"modell: {cid:<9} keine Empfehlung - {m.get('eignung')}")
            continue

        vs = [v for v in vertraege if v["cluster_id"] == cid]
        mm = m["median_eur_m2"]
        erg, leer, it, ok = fixpunkt(vs, mm, par, raster)
        mittel_leer = sum(leer.values()) / len(leer)
        con.execute("INSERT INTO modelllauf VALUES (?,?,?,?,?,?,?,?)",
                    (cid, m["abruf_datum"], mm, m["fallzahl"], m["eignung"],
                     it, int(ok), round(mittel_leer, 3)))
        zahlen["cluster_gerechnet"] += 1
        zahlen["nicht_konvergiert"] += 0 if ok else 1
        print(f"modell: {cid:<9} Marktmiete {mm} EUR/m2 (n={m['fallzahl']}), "
              f"Fixpunkt {'konvergiert' if ok else 'NICHT konvergiert'} "
              f"nach {it} Runde(n), Leerstand im Mittel {mittel_leer:.2f} Monate")

        for v in vs:
            e = erg[v["vertrag_id"]]
            s = e["szenario"]
            con.execute(
                "INSERT INTO empfehlung VALUES (?,?,?,?,?,?,?,?,?,?)",
                (v["vertrag_id"], e["option"],
                 s.aufschlag_pct if s else None, s.angebot_netto if s else None,
                 s.angebot_eur_m2 if s else None, s.p if s else None,
                 s.quote if s else None, e["bw"], e["bw_null"], e["bw_auslaufen"]))
            zahlen["empfehlungen"] += 1

            leer_v = leer[quartal(v["vertragsende"])]
            for name in SENSITIVE + ["marktmiete"]:
                if name == "marktmiete":
                    raender = [("unten", m["q1_eur_m2"]), ("oben", m["q3_eur_m2"])]
                else:
                    sp = par["_spannen"][name]
                    raender = [("unten", sp[0]), ("oben", sp[-1])]
                for rand, wert in raender:
                    p2 = dict(par)
                    markt2 = mm
                    if name == "marktmiete":
                        markt2 = wert
                    else:
                        p2[name] = wert
                    # Der Leerstand selbst ist ein sensibler Parameter; sonst
                    # gilt der Fixpunkt-Leerstand des Basisfalls.
                    l2 = wert if name == "leerstand_monate" else leer_v
                    e2 = beste_option(v, markt2, p2, raster, l2)
                    con.execute(
                        "INSERT INTO empfehlung_sensitivitaet VALUES (?,?,?,?,?,?)",
                        (v["vertrag_id"], name, rand, wert, e2["option"],
                         e2["szenario"].aufschlag_pct if e2["szenario"] else None))
    con.commit()
    return zahlen
