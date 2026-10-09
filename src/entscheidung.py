"""Annahmemodell und Barwertvergleich.

Die Entscheidung je auslaufendem Vertrag: zu welchem Mietzins bieten wir die
Fuenfjahresverlaengerung an - oder lassen wir auslaufen?

  p(annahme)   Wahrscheinlichkeit, dass der Mieter annimmt statt auszuziehen.
               Getrieben vom Preisvorteil gegenueber dem Markt abzueglich
               seiner Umzugskosten, gebremst durch die Mietbelastungsquote.
  Barwert      Ueber fuenf Jahre Bindung, diskontiert. Bei Auszug mit
               Leerstand, Neuvermietungskosten und danach Marktmiete.

Erwartungswert = p * BW(Annahme) + (1-p) * BW(Auszug).

Das Einkommen des Mieters wirkt an zwei Stellen und NICHT als Preisargument:
in der Annahmewahrscheinlichkeit und im Ausfallrisiko.

Alle Parameter stehen in config/portfolio.json mit Sensitivitaetsspanne.
Empirisch belegt ist keiner davon.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

BINDUNG_JAHRE = 5


def belastungsquote(miete_netto_eur: float, flaeche_m2: float,
                    betriebskosten_eur_m2: float,
                    einkommen_brutto_pa: float, netto_faktor: float,
                    zweiteinkommen: bool = False) -> float:
    brutto_monat = miete_netto_eur + betriebskosten_eur_m2 * flaeche_m2
    haushalt = einkommen_brutto_pa * (1.55 if zweiteinkommen else 1.0)
    netto = haushalt * netto_faktor
    if netto <= 0:
        return float("inf")
    return brutto_monat * 12.0 / netto


def p_annahme(angebot_eur_m2: float, marktmiete_eur_m2: float,
              flaeche_m2: float, umzugskosten_eur: float,
              quote: float, quote_grenze: float, k: float) -> float:
    umzug_pro_m2 = umzugskosten_eur / (BINDUNG_JAHRE * 12.0 * flaeche_m2)
    vorteil = (marktmiete_eur_m2 - angebot_eur_m2) + umzug_pro_m2
    p = 1.0 / (1.0 + math.exp(-k * vorteil))
    if quote > quote_grenze:
        p *= math.exp(-6.0 * (quote - quote_grenze))
    return max(0.0, min(1.0, p))


def p_zahlungsausfall(quote: float, quote_grenze: float) -> float:
    """Hier wirkt das Mietereinkommen als Risikogroesse, nicht als Preisargument."""
    if quote <= quote_grenze:
        return 0.005
    return min(0.35, 0.005 + 0.9 * (quote - quote_grenze) ** 1.6)


def barwert(mieten_pro_jahr: list[float], diskont: float) -> float:
    return sum(m / ((1 + diskont) ** (i + 1)) for i, m in enumerate(mieten_pro_jahr))


@dataclass
class Szenario:
    aufschlag_pct: float
    angebot_netto: float
    angebot_eur_m2: float
    quote: float
    p: float
    p_ausfall: float
    bw_annahme: float
    bw_auszug: float
    bw_erwartet: float


def bewerten(miete_aktuell: float, flaeche_m2: float, marktmiete_eur_m2: float,
             einkommen_brutto_pa: float, zweiteinkommen: bool,
             aufschlag_pct: float, par: dict,
             wertsicherung_pct_pa: float = 2.5,
             leerstand_monate: float | None = None) -> Szenario:
    angebot = miete_aktuell * (1 + aufschlag_pct / 100.0)
    angebot_m2 = angebot / flaeche_m2

    quote = belastungsquote(angebot, flaeche_m2, par["betriebskosten_eur_m2"],
                            einkommen_brutto_pa, par["netto_von_brutto_faktor"],
                            zweiteinkommen)
    p = p_annahme(angebot_m2, marktmiete_eur_m2, flaeche_m2,
                  par["umzugskosten_eur"], quote,
                  par["belastungsquote_schmerzgrenze"],
                  par["wechselbereitschaft_k"])

    d = par["diskontsatz_pa"]
    g = 1 + wertsicherung_pct_pa / 100.0

    p_aus = p_zahlungsausfall(quote, par["belastungsquote_schmerzgrenze"])
    ausfall_monate = par.get("ausfall_monate_je_fall", 4.0)
    bleibt = [angebot * (12 - p_aus * ausfall_monate) * (g ** i)
              for i in range(BINDUNG_JAHRE)]
    bw_bleibt = barwert(bleibt, d)

    leer = par["leerstand_monate"] if leerstand_monate is None else leerstand_monate
    abschlag = 1.0 - par.get("marktrisiko_abschlag", 0.0)
    markt_netto = marktmiete_eur_m2 * flaeche_m2 * abschlag
    kosten = par["neuvermietungskosten_monatsmieten"] * markt_netto
    erstes = markt_netto * max(0.0, 12 - leer) - kosten
    geht = [erstes] + [markt_netto * 12 * (g ** i) for i in range(1, BINDUNG_JAHRE)]
    bw_geht = barwert(geht, d)

    return Szenario(aufschlag_pct, round(angebot, 2), round(angebot_m2, 2),
                    round(quote, 4), round(p, 4), round(p_aus, 4),
                    round(bw_bleibt, 0), round(bw_geht, 0),
                    round(p * bw_bleibt + (1 - p) * bw_geht, 0))


def optimieren(miete_aktuell: float, flaeche_m2: float, marktmiete_eur_m2: float,
               einkommen_brutto_pa: float, zweiteinkommen: bool,
               aufschlaege: list[float], par: dict,
               leerstand_monate: float | None = None) -> list[Szenario]:
    return sorted(
        (bewerten(miete_aktuell, flaeche_m2, marktmiete_eur_m2,
                  einkommen_brutto_pa, zweiteinkommen, a, par,
                  leerstand_monate=leerstand_monate) for a in aufschlaege),
        key=lambda s: s.aufschlag_pct)
