"""Schritt 4b: Empfehlung je laufendem Mietvertrag (Demo-Fall, E44).

Fuer jeden Vertrag im Mieterverzeichnis (config/vertraege.json):

  Markt   Median der Angebotsmiete seiner Groessenklasse in 1020 im juengsten
          Abruf - und im Abruf, der seiner letzten Mieterhoehung am naechsten
          liegt (frueheste Beobachtung nicht vor der Erhoehung). Liegt die
          Erhoehung vor dem ersten Abruf (25.09.2026), ist der Bezug der erste
          Abruf, und bezug_vor_beobachtung = 1 sagt das. Aelter sind unsere
          Marktdaten nicht.
  KV      Entwicklung des KV-Lohns seiner Branche seit der letzten Erhoehung
          und seit Vertragsabschluss, aus kv_erhoehung (LLM-Extraktion nach
          Gate 4). Ein Deckel ("bis 3.750 Euro") wirkt je Mieter: wer mehr
          verdient, bekommt den Prozentsatz nur auf den Deckelbetrag.
  Einkommen  Durchschnitt der drei Lohnzettel bei Abschluss, fortgeschrieben
          mit der KV-Entwicklung, mal 14 Bezuege. Es wirkt NUR auf die
          Annahmewahrscheinlichkeit und das Ausfallrisiko (E05, E44), nicht
          auf den Preis. Die Empfehlung folgt dem Abstand zum Markt; sie kann
          ihn um eine Rasterstufe ueberschreiten, weil ein Umzug den Mieter
          Geld kostet und er deshalb knapp ueber Markt eher bleibt als geht
          (Annahme umzugskosten_eur). Einen Deckel bei Marktmiete gibt es
          nicht - das zeigt die Spalte neue_miete_eur_m2 gegen
          markt_jetzt_eur_m2.
  Empfehlung  das Angebot im Raster, das den erwarteten Barwert ueber
          fuenf Jahre maximiert (src/entscheidung.py), gegen "keine Erhoehung"
          und "Auszug in Kauf nehmen". Aufschlag 0 heisst: nicht erhoehen.

Wer mit vielen Wohnungen derselben Groesse gleichzeitig neu vermietet,
konkurriert mit sich selbst - der Leerstand je Groessenklasse wird als
Fixpunkt mit Daempfung bestimmt (E18). Konvergiert er nicht, laesst Gate 3
keine Vorlage entstehen.

Die Arithmetik liegt hier, weil sie iteriert; die Ergebnisse gehen in
Tabellen, und was die Vorlage zitiert, kommt aus kennzahl_*.sql (E39).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date

from . import config as C
from .entscheidung import bewerten

DAEMPFUNG = 0.5
TOLERANZ_MONATE = 0.01
MAX_ITER = 50
STICHTAG = "2026-10-23"

SENSITIVE = ["wechselbereitschaft_k", "leerstand_monate", "marktrisiko_abschlag",
             "umzugskosten_eur", "belastungsquote_schmerzgrenze"]


def parameter_laden() -> tuple[dict, list[float]]:
    port = json.loads((C.WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    par = {k: v["wert"] for k, v in port["annahmen"].items()}
    par["_spannen"] = {k: v["sensitivitaet"] for k, v in port["annahmen"].items()}
    return par, port["angebotsraster"]["aufschlaege_pct"]


def vertraege_laden() -> list[dict]:
    return json.loads((C.WURZEL / "config" / "vertraege.json")
                      .read_text(encoding="utf-8"))["vertraege"]


def gehalt_bei_abschluss(v: dict) -> float:
    return sum(v["lohnzettel_brutto_eur"]) / len(v["lohnzettel_brutto_eur"])


def kv_faktor(erhoehungen: list[dict], branche: str, seit: str, bis: str,
              gehalt_start: float) -> tuple[float, float]:
    """(Faktor, Gehalt am Ende). Nur Erhoehungen mit gueltig_ab nach 'seit'
    und bis einschliesslich 'bis'. Ein Deckel begrenzt die Erhoehung auf den
    Prozentsatz des Deckelbetrags."""
    g = gehalt_start
    for e in sorted((e for e in erhoehungen if e["branche_id"] == branche
                     and seit < e["gueltig_ab"] <= bis), key=lambda e: e["gueltig_ab"]):
        basis = min(g, e["deckel_eur"]) if e["deckel_eur"] else g
        g = g + basis * e["satz_index"] / 100
    return g / gehalt_start, g


def beste_option(v: dict, markt: float, einkommen: float, par: dict, raster: list[float],
                 leerstand: float) -> dict:
    szen = [bewerten(v["miete_aktuell_eur"], v["flaeche_m2"], markt, einkommen,
                     v["zweiteinkommen"], a, par, leerstand_monate=leerstand) for a in raster]
    # Bei Gleichstand das niedrigere Angebot: gleicher Erwartungswert mit
    # hoeherer Annahmewahrscheinlichkeit ist das geringere Risiko.
    bestes = max(szen, key=lambda s: (s.bw_erwartet, -s.aufschlag_pct))
    null = next(s for s in szen if s.aufschlag_pct == 0)
    return {"szenario": bestes, "null": null}


def fixpunkt(vs: list[dict], markt: float, einkommen: dict, par: dict,
             raster: list[float]) -> tuple[dict, float, int, bool]:
    basis = par["leerstand_monate"]
    zuschlag = par["leerstand_zuschlag_je_gleichzeitiger_neuvermietung"]
    leer = basis
    erg: dict = {}
    for it in range(1, MAX_ITER + 1):
        erg = {v["vertrag_id"]: beste_option(v, markt, einkommen[v["vertrag_id"]], par, raster, leer)
               for v in vs}
        # Erwartete Auszuege je Jahr: die Erhoehungen verteilen sich auf die
        # Anpassungstermine eines Jahres, deshalb ein Viertel je Quartal.
        auszuege = sum(1 - erg[v["vertrag_id"]]["szenario"].p for v in vs) / 4
        ziel = basis + zuschlag * max(0.0, auszuege - 1.0)
        neu = DAEMPFUNG * leer + (1 - DAEMPFUNG) * ziel
        if abs(neu - leer) < TOLERANZ_MONATE:
            return erg, neu, it, True
        leer = neu
    return erg, leer, MAX_ITER, False


def ausfuehren(con: sqlite3.Connection) -> dict:
    par, raster = parameter_laden()
    vertraege = vertraege_laden()
    erh = [dict(r) for r in con.execute(
        "SELECT branche_id, gueltig_ab, satz_index, deckel_eur FROM kv_erhoehung")]

    # Markt je Groessenklasse und Abruf, aus der View (SQL), nicht neu gerechnet
    markt = {}
    for r in con.execute("""SELECT groessenklasse, abruf_datum, median_eur_m2, fallzahl,
                                   q1_eur_m2, q3_eur_m2, belastbarkeit
                            FROM v_marktniveau WHERE plz = '1020' ORDER BY abruf_datum"""):
        markt.setdefault(r["groessenklasse"], []).append(dict(r))

    for v in vertraege:
        z = v["lohnzettel_brutto_eur"]
        con.execute("INSERT INTO vertrag VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (v["vertrag_id"], v["plz"], v["groessenklasse"], v["flaeche_m2"],
                     v["abschluss"], int(v["wertsicherung"]), v["letzte_anpassung"],
                     v["miete_aktuell_eur"], v["miete_bei_abschluss_eur"], v["branche_id"],
                     z[0], z[1], z[2], int(v["zweiteinkommen"])))

    zahlen = {"segmente": 0, "empfehlungen": 0, "nicht_konvergiert": 0, "ohne_markt": 0}
    for klasse in sorted({v["groessenklasse"] for v in vertraege}):
        reihe = markt.get(klasse, [])
        jetzt = reihe[-1] if reihe else None
        vs = [v for v in vertraege if v["groessenklasse"] == klasse]
        if not jetzt or jetzt["belastbarkeit"] == "nicht belastbar":
            con.execute("INSERT INTO modelllauf VALUES (?,?,?,?,?,?,?,?)",
                        (klasse, jetzt and jetzt["abruf_datum"], jetzt and jetzt["median_eur_m2"],
                         jetzt and jetzt["fallzahl"], "keine belastbare Marktmiete", None, None, None))
            zahlen["ohne_markt"] += 1
            continue
        einkommen, kv = {}, {}
        for v in vs:
            g0 = gehalt_bei_abschluss(v)
            f_ab, g_jetzt = kv_faktor(erh, v["branche_id"], v["abschluss"], STICHTAG, g0)
            # seit der letzten Anpassung: Gehalt zu diesem Zeitpunkt als Start
            _, g_anp = kv_faktor(erh, v["branche_id"], v["abschluss"], v["letzte_anpassung"], g0)
            f_anp, _ = kv_faktor(erh, v["branche_id"], v["letzte_anpassung"], STICHTAG, g_anp)
            einkommen[v["vertrag_id"]] = g_jetzt * 14
            kv[v["vertrag_id"]] = (f_ab, f_anp)
        mm = jetzt["median_eur_m2"]
        erg, leer, it, ok = fixpunkt(vs, mm, einkommen, par, raster)
        con.execute("INSERT INTO modelllauf VALUES (?,?,?,?,?,?,?,?)",
                    (klasse, jetzt["abruf_datum"], mm, jetzt["fallzahl"], jetzt["belastbarkeit"],
                     it, int(ok), round(leer, 3)))
        zahlen["segmente"] += 1
        zahlen["nicht_konvergiert"] += 0 if ok else 1
        print(f"modell: {klasse:<7} Marktmiete {mm} EUR/m2 (n={jetzt['fallzahl']}, "
              f"{jetzt['abruf_datum']}), Fixpunkt {'konvergiert' if ok else 'NICHT konvergiert'} "
              f"nach {it} Runde(n), Leerstand {leer:.2f} Monate")

        for v in vs:
            s, n = erg[v["vertrag_id"]]["szenario"], erg[v["vertrag_id"]]["null"]
            bezug = next((r for r in reihe if r["abruf_datum"] >= v["letzte_anpassung"]), reihe[0])
            vor = int(v["letzte_anpassung"] < reihe[0]["abruf_datum"])
            f_ab, f_anp = kv[v["vertrag_id"]]
            con.execute(
                "INSERT INTO empfehlung VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (v["vertrag_id"], bezug["abruf_datum"], bezug["median_eur_m2"], vor,
                 jetzt["abruf_datum"], mm,
                 round(100 * (mm / bezug["median_eur_m2"] - 1), 1),
                 round(100 * (f_anp - 1), 2), round(100 * (f_ab - 1), 2),
                 round(einkommen[v["vertrag_id"]], 0),
                 int(s.aufschlag_pct > 0), s.aufschlag_pct, s.angebot_netto, s.angebot_eur_m2,
                 s.p, n.quote, s.quote, s.bw_erwartet, n.bw_erwartet, s.bw_auszug))
            zahlen["empfehlungen"] += 1

            for name in SENSITIVE + ["marktmiete"]:
                if name == "marktmiete":
                    raender = [("unten", jetzt["q1_eur_m2"]), ("oben", jetzt["q3_eur_m2"])]
                else:
                    sp = par["_spannen"][name]
                    raender = [("unten", sp[0]), ("oben", sp[-1])]
                for rand, wert in raender:
                    p2, m2 = dict(par), mm
                    if name == "marktmiete":
                        m2 = wert
                    else:
                        p2[name] = wert
                    l2 = wert if name == "leerstand_monate" else leer
                    e2 = beste_option(v, m2, einkommen[v["vertrag_id"]], p2, raster, l2)["szenario"]
                    con.execute("INSERT INTO empfehlung_sensitivitaet VALUES (?,?,?,?,?,?)",
                                (v["vertrag_id"], name, rand, wert,
                                 "erhoehen" if e2.aufschlag_pct > 0 else "nicht erhoehen",
                                 e2.aufschlag_pct))
    con.commit()
    return zahlen
