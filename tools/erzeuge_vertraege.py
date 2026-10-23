"""Erzeugt das synthetische Mieterverzeichnis config/vertraege.json.

    python3 -m src.run && python3 tools/erzeuge_vertraege.py && python3 -m src.run

Es gibt keine echten Mieter in diesem Projekt und darf keine geben (Regel 1).
Das Verzeichnis ist erfunden, nach festen Annahmen und mit festem Startwert;
zwei Aufrufe liefern dieselbe Datei. Die Konkretisierung zum Prototyp
(E44) bestimmt den Umfang:

  Lage          1020 Wien - der einzige Bezirk mit Marktdaten.
  Groesse       nur Groessenklassen mit belastbarem Median in JEDEM Abruf
                (config.PORTFOLIO_GROESSEN). Gelesen aus
                data/processed/kennzahl_marktniveau.csv - deshalb laeuft die
                Pipeline einmal vor diesem Skript.
  Branche       nur Branchen mit lueckenloser KV-Reihe 2024-2026 in der
                gepruefte Extraktion (data/extrakt/, Gate 4).
  Miete         heute nahe am Marktmedian des ERSTEN Abrufs (25.09.2026),
                zwischen 86 und 102 % davon. Aeltere Marktdaten gibt es nicht.
  Lohnzettel    drei Monatsbezuege vor Vertragsabschluss, wie sie ein
                Vermieter verlangt; das Niveau aus berufsgruppen.json
                (dort als PLATZHALTER gekennzeichnet), Monat = Jahr / 14.
  Bonitaet      Bruttomiete bei Abschluss hoechstens 35 % des Haushaltsnetto
                (E40); sonst wird neu gezogen.
  Anpassung     85 % mit Wertsicherung: letzte Anpassung am 1. April des
                juengsten Jahres, das mindestens 12 Monate nach Abschluss
                liegt; ohne Klausel ist die letzte Anpassung der Abschluss.

Was es nicht gibt: Namen, Adressen, Geburtsdaten. Ein Vertrag ist eine
Kennung, eine Wohnung und ein Haushalt aus Zahlen.
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "config" / "vertraege.json"

STARTWERT = 20261023
ANZAHL = 50
STICHTAG = date(2026, 10, 23)
ERSTER_ABRUF = "2026-09-25"
MIETE_ZU_MARKT = (0.86, 1.02)          # ANNAHME
ANTEIL_KLAUSEL = 0.85                  # ANNAHME
INDEX_RATE_PA = 0.04                   # ANNAHME, Rueckrechnung auf die Miete bei Abschluss
ANTEIL_ZWEITEINKOMMEN = 0.40           # ANNAHME, vor der Bonitaetspruefung
QUOTE_BEI_ABSCHLUSS_MAX = 0.35         # ANNAHME
LOHNZETTEL_STREUUNG = (0.97, 1.06)     # Ueberstunden, Zulagen je Monat
FLAECHE = {"50-80": (55.0, 79.9), "80-100": (80.0, 99.9)}


def portfolio_groessen() -> list[str]:
    import sys
    sys.path.insert(0, str(WURZEL))
    from src import config as C
    return list(C.PORTFOLIO_GROESSEN)


def marktmedian_erster_abruf() -> dict[str, float]:
    pfad = WURZEL / "data" / "processed" / "kennzahl_marktniveau.csv"
    with open(pfad, encoding="utf-8", newline="") as f:
        return {r["groessenklasse"]: float(r["median_eur_m2"])
                for r in csv.DictReader(f, delimiter=";")
                if r["plz"] == "1020" and r["abruf_datum"] == ERSTER_ABRUF}


def branchen_mit_reihe() -> list[str]:
    pfad = sorted((WURZEL / "data" / "extrakt").glob("kv_erhoehungen_*.json"))[-1]
    ds = json.loads(pfad.read_text(encoding="utf-8"))["erhoehungen"]
    jahre: dict[str, set[int]] = {}
    for d in ds:
        jahre.setdefault(d["branche_id"], set()).add(d["jahr"])
    return sorted(b for b, j in jahre.items() if {2024, 2025, 2026} <= j)


def letzte_anpassung(abschluss: date, klausel: bool) -> date:
    if not klausel:
        return abschluss
    for jahr in range(STICHTAG.year, abschluss.year, -1):
        kandidat = date(jahr, 4, 1)
        monate = (kandidat.year - abschluss.year) * 12 + kandidat.month - abschluss.month
        if kandidat <= STICHTAG and monate >= 12:
            return kandidat
    return abschluss


def erzeugen() -> dict:
    rng = random.Random(STARTWERT)
    port = json.loads((WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    beruf = json.loads((WURZEL / "config" / "berufsgruppen.json").read_text(encoding="utf-8"))
    annahmen = port["annahmen"]
    bk = annahmen["betriebskosten_eur_m2"]["wert"]
    nf = annahmen["netto_von_brutto_faktor"]["wert"]
    niveau = beruf["einkommen_niveau"]
    markt = marktmedian_erster_abruf()
    groessen = portfolio_groessen()
    branchen = branchen_mit_reihe()
    anteile = {g["gruppe_id"]: g["anteil_portfolio"] for g in beruf["gruppen"] if g["gruppe_id"] in branchen}
    summe = sum(anteile.values())

    # Zusammensetzung nach Anteil, nicht nach Zufall des Startwerts
    liste: list[str] = []
    for b in branchen:
        liste += [b] * round(anteile[b] / summe * ANZAHL)
    liste = (liste + [branchen[0]] * ANZAHL)[:ANZAHL]
    rng.shuffle(liste)

    vertraege = []
    for i in range(ANZAHL):
        klasse = groessen[i % len(groessen)]
        flaeche = round(rng.uniform(*FLAECHE[klasse]), 1)
        abschluss = date(rng.choice([2024, 2025]), rng.randint(1, 12), 1)
        if abschluss.year == 2024 and abschluss.month == 1:
            abschluss = date(2024, 2, 1)   # KV-Reihe beginnt mit den Abschluessen 2024
        klausel = rng.random() < ANTEIL_KLAUSEL
        anpassung = letzte_anpassung(abschluss, klausel)
        miete_m2 = markt[klasse] * rng.uniform(*MIETE_ZU_MARKT)
        miete = round(miete_m2 * flaeche, 2)
        jahre_index = (anpassung.year - abschluss.year) if klausel else 0
        miete_abschluss = round(miete / ((1 + INDEX_RATE_PA) ** jahre_index), 2)
        b = liste[i]
        for _ in range(5000):
            zweit = rng.random() < ANTEIL_ZWEITEINKOMMEN
            monat = niveau[b]["median"] / 14 * math.exp(rng.gauss(0, niveau[b]["sigma_log"]))
            zettel = [round(monat * rng.uniform(*LOHNZETTEL_STREUUNG), 2) for _ in range(3)]
            gehalt = sum(zettel) / 3
            netto_haushalt = gehalt * 14 * (1.55 if zweit else 1.0) * nf
            if (miete_abschluss + bk * flaeche) * 12 / netto_haushalt <= QUOTE_BEI_ABSCHLUSS_MAX:
                break
        else:
            raise RuntimeError(f"Kein tragfaehiger Haushalt fuer {b}")
        vertraege.append({
            "vertrag_id": f"LS-{i + 1:02d}",
            "plz": "1020",
            "groessenklasse": klasse,
            "flaeche_m2": flaeche,
            "abschluss": abschluss.isoformat(),
            "wertsicherung": klausel,
            "letzte_anpassung": anpassung.isoformat(),
            "miete_aktuell_eur": miete,
            "miete_bei_abschluss_eur": miete_abschluss,
            "branche_id": b,
            "lohnzettel_brutto_eur": zettel,
            "zweiteinkommen": zweit,
        })
    return {
        "_zweck": "Synthetisches Mieterverzeichnis fuer den Demo-Fall (E44). Keine echten Personen.",
        "_erzeugt_von": "tools/erzeuge_vertraege.py",
        "_startwert": STARTWERT,
        "_annahmen": {"miete_zu_markt_erster_abruf": MIETE_ZU_MARKT, "anteil_wertsicherung": ANTEIL_KLAUSEL,
                      "indexrate_rueckrechnung_pa": INDEX_RATE_PA, "anteil_zweiteinkommen": ANTEIL_ZWEITEINKOMMEN,
                      "quote_bei_abschluss_max": QUOTE_BEI_ABSCHLUSS_MAX,
                      "lohnzettel_streuung": LOHNZETTEL_STREUUNG, "gehaelter_je_jahr": 14,
                      "groessenklassen": groessen, "branchen": branchen},
        "vertraege": vertraege,
    }


if __name__ == "__main__":
    daten = erzeugen()
    ZIEL.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(daten['vertraege'])} Vertraege -> {ZIEL.relative_to(WURZEL)}")
