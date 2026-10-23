"""Erzeugt den synthetischen Vertragsbestand config/vertraege.json.

    python3 tools/erzeuge_vertraege.py

Es gibt keine echten Mietvertraege in diesem Projekt und darf keine geben
(Regel 1 in CLAUDE.md). Der Bestand ist erfunden - aber nach festen,
benannten Annahmen und mit festem Startwert. Zwei Aufrufe liefern
byte-identische Dateien; die Datei ist committet und wird von der Pipeline
gelesen, nicht bei jedem Lauf neu gewuerfelt.

Annahmen (alle in docs/annahmen.md unter A10 und A11):

  - 50 Vertraege, Cluster und Einheiten aus config/portfolio.json
  - Abschlussjahr 2019-2022, gleichverteilt
  - Vertragsende Juli 2027 bis Juni 2028, Monat gleichverteilt. Entschieden
    wird 6 Monate vor Vertragsende; die erste Tranche entscheidet im
    1. Quartal 2027 (00_auftrag.md) und betrifft damit Vertragsenden ab
    Juli 2027. Korrektur 23.10.: die erste Fassung liess Vertraege ab
    Jaenner 2027 enden - deren Entscheidung waere vor dem heutigen Tag
    faellig gewesen.
  - Startmiete = angenommenes Marktniveau des Abschlussjahres * Streuung
  - 85 % mit Wertsicherungsklausel; mit Klausel bis 2026 fortgeschrieben
    mit einer pauschalen Jahresrate, weil die Indexreihen nicht beschafft
    sind (siehe 07_offene_punkte_lessons.md). Die Rate ist eine Annahme,
    keine Messung.
  - Berufsgruppe nach anteil_portfolio, Einkommen lognormal um den Median
    aus config/berufsgruppen.json (dort als PLATZHALTER gekennzeichnet)
  - 40 % der Haushalte mit Zweiteinkommen
  - Bonitaetspruefung bei Abschluss: ein Haushalt, dessen Bruttomiete
    (netto + Betriebskosten) ueber 35 % seines Nettoeinkommens laege, haette
    den Vertrag nicht bekommen. Sein Einkommen wird neu gezogen.

Korrektur 23.10.2026: die erste Fassung zog das Einkommen unabhaengig von
der Miete. Ergebnis waren Belastungsquoten bis 1,22 - Haushalte, die mehr
Miete zahlen als sie verdienen. Das Modell rechnete damit klaglos und
empfahl trotzdem Aufschlaege; erst der Blick auf die Spalte belastungsquote
zeigte, dass der Bestand selbst unmoeglich war (Entscheidungslog E40).
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "config" / "vertraege.json"

STARTWERT = 20261023

# ANNAHME: Angebotsniveau Neubau 80-100 m2 je Abschlussjahr, EUR/m2 netto.
# Nicht gemessen - es gibt fuer diese Jahre keinen Schnappschuss.
MARKT_JE_JAHR = {2019: 15.8, 2020: 16.4, 2021: 17.3, 2022: 18.9}
STREUUNG = 0.06              # +-6 % um das Jahresniveau
ANTEIL_KLAUSEL = 0.85
INDEX_RATE_PA = 0.040        # ANNAHME, pauschal, bis 2026
STICHJAHR = 2026
ANTEIL_ZWEITEINKOMMEN = 0.40
ENDE_MONATE = [f"2027-{m:02d}" for m in range(7, 13)] + [f"2028-{m:02d}" for m in range(1, 7)]
QUOTE_BEI_ABSCHLUSS_MAX = 0.35   # ANNAHME: uebliche Bonitaetsgrenze


def berufsgruppen_ziehen(rng: random.Random, gruppen: list[dict], n: int) -> list[str]:
    # Nach Anteil aufrunden und kuerzen statt frei zu wuerfeln: so entspricht
    # die Zusammensetzung dem Portfolio und nicht dem Zufall eines Startwerts.
    liste: list[str] = []
    for g in gruppen:
        liste += [g["gruppe_id"]] * round(g["anteil_portfolio"] * n)
    while len(liste) < n:
        liste.append(gruppen[0]["gruppe_id"])
    liste = liste[:n]
    rng.shuffle(liste)
    return liste


def erzeugen() -> dict:
    rng = random.Random(STARTWERT)
    port = json.loads((WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    beruf = json.loads((WURZEL / "config" / "berufsgruppen.json").read_text(encoding="utf-8"))
    niveau = beruf["einkommen_niveau"]
    annahmen = port["annahmen"]

    n = sum(c["einheiten"] for c in port["cluster"])
    gruppen = berufsgruppen_ziehen(rng, beruf["gruppen"], n)

    vertraege = []
    i = 0
    for c in port["cluster"]:
        for k in range(c["einheiten"]):
            jahr = rng.choice(sorted(MARKT_JE_JAHR))
            flaeche = round(rng.uniform(port["wohnung"]["flaeche_min_m2"],
                                        port["wohnung"]["flaeche_max_m2"]), 1)
            start_m2 = MARKT_JE_JAHR[jahr] * rng.uniform(1 - STREUUNG, 1 + STREUUNG)
            klausel = rng.random() < ANTEIL_KLAUSEL
            jahre = STICHJAHR - jahr
            heute_m2 = start_m2 * ((1 + INDEX_RATE_PA) ** jahre if klausel else 1.0)
            g = gruppen[i]
            brutto_miete_start = (start_m2 + annahmen["betriebskosten_eur_m2"]["wert"]) * flaeche
            # Neu ziehen statt anheben: angehoben laegen alle Abgewiesenen
            # genau auf der Grenze, und die Verteilung haette einen Knick.
            # Zweiteinkommen wird mitgezogen - wer im Handel 90 m2 Neubau
            # mietet, hat meist eines. Das ist die Auslese des Vermieters,
            # nicht eine Verzerrung des Generators.
            for _ in range(5000):
                zweit = rng.random() < ANTEIL_ZWEITEINKOMMEN
                einkommen = niveau[g]["median"] * math.exp(rng.gauss(0, niveau[g]["sigma_log"]))
                haushalt_netto = (einkommen * (1.55 if zweit else 1.0)
                                  * annahmen["netto_von_brutto_faktor"]["wert"])
                if brutto_miete_start * 12 / haushalt_netto <= QUOTE_BEI_ABSCHLUSS_MAX:
                    break
            else:
                raise RuntimeError(f"Kein tragfaehiges Einkommen fuer {g} gefunden")
            vertraege.append({
                "vertrag_id": f"{c['cluster_id'][:2]}-{k + 1:02d}",
                "cluster_id": c["cluster_id"],
                "flaeche_m2": flaeche,
                "abschluss_jahr": jahr,
                "vertragsende": ENDE_MONATE[rng.randrange(len(ENDE_MONATE))],
                "wertsicherung": klausel,
                "miete_start_eur": round(start_m2 * flaeche, 2),
                "miete_aktuell_eur": round(heute_m2 * flaeche, 2),
                "berufsgruppe": g,
                "einkommen_brutto_pa": round(einkommen, -2),
                "zweiteinkommen": zweit,
            })
            i += 1

    return {
        "_zweck": "Synthetischer Vertragsbestand. Keine echten Personen, keine echten Vertraege.",
        "_erzeugt_von": "tools/erzeuge_vertraege.py",
        "_startwert": STARTWERT,
        "_annahmen": {
            "markt_je_abschlussjahr_eur_m2": {str(k): v for k, v in MARKT_JE_JAHR.items()},
            "streuung": STREUUNG,
            "anteil_wertsicherung": ANTEIL_KLAUSEL,
            "indexrate_pa_bis_2026": INDEX_RATE_PA,
            "anteil_zweiteinkommen": ANTEIL_ZWEITEINKOMMEN,
            "quote_bei_abschluss_max": QUOTE_BEI_ABSCHLUSS_MAX,
        },
        "vertraege": vertraege,
    }


if __name__ == "__main__":
    daten = erzeugen()
    ZIEL.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(daten['vertraege'])} Vertraege -> {ZIEL.relative_to(WURZEL)}")
