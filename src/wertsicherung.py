"""Wertsicherung nach dem gedeckelten Modell (MieWeG, ab 1.1.2026).

Modellierung nach oeffentlichen Zusammenfassungen. KEIN Rechtsrat.

Regel:
1. Erhoehungssatz nach vertraglicher Vereinbarung (VPI-Jahresdurchschnitte).
2. Deckelung: je Jahr seit dem letzten verwendeten Indexwert sind 3 Prozent
   voll wirksam, von allem darueber nur die Haelfte.
       zulaessig = 3*n + (roh - 3*n)/2   falls roh > 3*n, sonst roh
3. Anpassung hoechstens einmal jaehrlich, fruehestens ab 1. April.
4. Vollanwendung: feste Deckel 1 % (2026), 2 % (2027).

Ohne Klausel im Vertrag keine Erhoehung waehrend der Laufzeit.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

FREIBETRAG_PCT_PRO_JAHR = 3.0
ANTEIL_UEBER_FREIBETRAG = 0.5
FRUEHESTER_MONAT = 4
VOLLANWENDUNG_DECKEL = {2026: 1.0, 2027: 2.0}


def roh_erhoehung_pct(vpi_neu: float, vpi_basis: float) -> float:
    if vpi_basis <= 0:
        raise ValueError("vpi_basis muss groesser als 0 sein")
    return (vpi_neu / vpi_basis - 1.0) * 100.0


def deckeln(roh_pct: float, jahre_seit_basis: int) -> float:
    if jahre_seit_basis < 1:
        raise ValueError("jahre_seit_basis muss mindestens 1 sein")
    if roh_pct <= 0:
        return 0.0
    frei = FREIBETRAG_PCT_PRO_JAHR * jahre_seit_basis
    if roh_pct <= frei:
        return roh_pct
    return frei + (roh_pct - frei) * ANTEIL_UEBER_FREIBETRAG


def anpassung_zulaessig(stichtag: date, letzte: date | None) -> bool:
    if stichtag.month < FRUEHESTER_MONAT:
        return False
    return letzte is None or stichtag.year > letzte.year


@dataclass
class Anpassung:
    zulaessig: bool
    roh_pct: float
    gedeckelt_pct: float
    wirksam_pct: float
    miete_neu: float
    grund: str


def anpassen(miete_alt: float, vpi_neu: float, vpi_basis: float,
             jahre_seit_basis: int, stichtag: date,
             letzte_anpassung: date | None = None,
             hat_klausel: bool = True,
             vollanwendung: bool = False) -> Anpassung:
    if not hat_klausel:
        return Anpassung(False, 0.0, 0.0, 0.0, miete_alt,
                         "keine Wertsicherungsklausel im Vertrag")
    if not anpassung_zulaessig(stichtag, letzte_anpassung):
        return Anpassung(False, 0.0, 0.0, 0.0, miete_alt,
                         "Anpassungstermin nicht erreicht")
    roh = roh_erhoehung_pct(vpi_neu, vpi_basis)
    ged = deckeln(roh, jahre_seit_basis)
    if vollanwendung and stichtag.year in VOLLANWENDUNG_DECKEL:
        wirksam = min(ged, VOLLANWENDUNG_DECKEL[stichtag.year])
        grund = f"Vollanwendung, gesetzlicher Deckel {stichtag.year}"
    else:
        wirksam, grund = ged, "Teilanwendung, gedeckeltes Modell"
    return Anpassung(True, roh, ged, wirksam,
                     round(miete_alt * (1 + wirksam / 100.0), 2), grund)


def fortschreiben(miete_start: float, vpi: dict[int, float],
                  jahr_start: int, jahr_ende: int,
                  hat_klausel: bool = True) -> dict[int, float]:
    verlauf = {jahr_start: round(miete_start, 2)}
    miete, basis = miete_start, jahr_start - 1
    for jahr in range(jahr_start + 1, jahr_ende + 1):
        if not hat_klausel or jahr - 1 not in vpi or basis not in vpi:
            verlauf[jahr] = round(miete, 2)
            continue
        a = anpassen(miete, vpi[jahr - 1], vpi[basis],
                     jahre_seit_basis=max(1, (jahr - 1) - basis),
                     stichtag=date(jahr, 4, 1), hat_klausel=True)
        if a.zulaessig and a.wirksam_pct > 0:
            miete, basis = a.miete_neu, jahr - 1
        verlauf[jahr] = round(miete, 2)
    return verlauf
