"""Tests der Wertsicherung und des Entscheidungsmodells.

Geprueft wird nicht, ob die Parameter stimmen - das kann ohne empirische
Daten niemand. Geprueft wird, ob das Modell sich richtig VERHAELT:
Monotonie, Randfaelle, und dass das Optimum nicht automatisch am Rand liegt.

    python3 tests/test_modell.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from entscheidung import (barwert, belastungsquote, bewerten, optimieren,
                          p_annahme, p_zahlungsausfall)
from wertsicherung import (anpassen, anpassung_zulaessig, deckeln,
                           fortschreiben, roh_erhoehung_pct)

PAR = {"leerstand_monate": 2.5, "neuvermietungskosten_monatsmieten": 2.0,
       "diskontsatz_pa": 0.045, "umzugskosten_eur": 4500,
       "belastungsquote_schmerzgrenze": 0.33, "wechselbereitschaft_k": 0.55,
       "betriebskosten_eur_m2": 2.60, "netto_von_brutto_faktor": 0.66,
       "marktrisiko_abschlag": 0.06, "ausfall_monate_je_fall": 4.0}
AUF = [0, 3, 6, 9, 12, 15, 20, 25, 30, 40]


# ------------------------------------------------------------ Wertsicherung
def test_roh_erhoehung():
    assert abs(roh_erhoehung_pct(110.0, 100.0) - 10.0) < 1e-9


def test_unter_freibetrag_unveraendert():
    assert abs(deckeln(2.9, 1) - 2.9) < 1e-9
    assert abs(deckeln(3.0, 1) - 3.0) < 1e-9


def test_ueber_freibetrag_halbiert():
    assert abs(deckeln(9.0, 1) - 6.0) < 1e-9
    assert abs(deckeln(8.5, 1) - 5.75) < 1e-9   # der Wert von 2024


def test_freibetrag_skaliert_mit_jahren():
    assert abs(deckeln(6.0, 2) - 6.0) < 1e-9
    assert abs(deckeln(12.0, 2) - 9.0) < 1e-9


def test_deflation_senkt_miete_nicht():
    assert deckeln(-1.5, 1) == 0.0


def test_deckelung_monoton():
    w = [deckeln(x, 1) for x in (0, 2, 3, 5, 8, 12, 20)]
    assert all(a <= b for a, b in zip(w, w[1:]))


def test_ohne_klausel_keine_erhoehung():
    a = anpassen(1200.0, 110.0, 100.0, 1, date(2026, 4, 1), hat_klausel=False)
    assert not a.zulaessig and a.miete_neu == 1200.0


def test_vor_april_keine_anpassung():
    assert not anpassung_zulaessig(date(2026, 3, 31), None)
    assert anpassung_zulaessig(date(2026, 4, 1), None)


def test_nur_einmal_pro_jahr():
    assert not anpassung_zulaessig(date(2026, 9, 1), date(2026, 4, 1))
    assert anpassung_zulaessig(date(2027, 4, 1), date(2026, 4, 1))


def test_vollanwendungsdeckel_greift():
    a = anpassen(1000.0, 110.0, 100.0, 1, date(2026, 4, 1), vollanwendung=True)
    assert abs(a.wirksam_pct - 1.0) < 1e-9
    b = anpassen(1000.0, 110.0, 100.0, 1, date(2026, 4, 1))
    assert abs(b.wirksam_pct - 6.5) < 1e-9        # 3 + (10-3)/2


def test_fortschreibung_ohne_klausel_flach():
    vpi = {2020: 100.0, 2021: 102.8, 2022: 111.6, 2023: 120.2, 2024: 123.7}
    assert set(fortschreiben(1400.0, vpi, 2021, 2025, False).values()) == {1400.0}


def test_bestand_faellt_hinter_die_inflation_zurueck():
    """Kernaussage der Vorlage: die Deckelung laesst den Bestand zuruecktreten."""
    vpi = {2020: 100.0, 2021: 102.8, 2022: 111.6, 2023: 120.2, 2024: 123.7}
    v = fortschreiben(1400.0, vpi, 2021, 2025, True)
    assert 0 < (v[2025] / v[2021] - 1) < (vpi[2024] / vpi[2021] - 1)


# -------------------------------------------------------- Entscheidungsmodell
def test_belastungsquote_plausibel():
    assert 0.35 < belastungsquote(1400, 90, 2.6, 62000, 0.66) < 0.55


def test_zweiteinkommen_senkt_quote():
    assert (belastungsquote(1400, 90, 2.6, 62000, 0.66, True)
            < belastungsquote(1400, 90, 2.6, 62000, 0.66, False))


def test_annahme_faellt_mit_dem_preis():
    ps = [p_annahme(m, 17.0, 90, 4500, 0.30, 0.33, 0.55)
          for m in (12, 14, 16, 18, 20, 24)]
    assert all(a >= b for a, b in zip(ps, ps[1:]))


def test_weit_unter_markt_wird_angenommen():
    assert p_annahme(11.0, 17.0, 90, 4500, 0.25, 0.33, 0.55) > 0.9


def test_weit_ueber_markt_wird_abgelehnt():
    assert p_annahme(26.0, 17.0, 90, 4500, 0.30, 0.33, 0.55) < 0.1


def test_umzugstraegheit_hilft_dem_vermieter():
    """Der Kern des Geschaeftsmodells: bei gleichem Preis bleibt der Mieter."""
    assert p_annahme(17.0, 17.0, 90, 4500, 0.30, 0.33, 0.55) > 0.5
    assert abs(p_annahme(17.0, 17.0, 90, 0, 0.30, 0.33, 0.55) - 0.5) < 1e-9


def test_leistbarkeit_bremst_unabhaengig_vom_vorteil():
    assert (p_annahme(12.0, 17.0, 90, 4500, 0.55, 0.33, 0.55)
            < p_annahme(12.0, 17.0, 90, 4500, 0.30, 0.33, 0.55))


def test_zahlungsausfall_steigt_mit_belastung():
    assert p_zahlungsausfall(0.25, 0.33) < 0.02
    assert p_zahlungsausfall(0.45, 0.33) > p_zahlungsausfall(0.36, 0.33)
    assert p_zahlungsausfall(0.90, 0.33) <= 0.35


def test_barwert_diskontiert():
    assert barwert([100, 100], 0.0) == 200.0
    assert barwert([100, 100], 0.1) < 200.0


def test_auszugsbarwert_unabhaengig_vom_angebot():
    a = bewerten(1300, 90, 17.0, 62000, False, 0, PAR)
    b = bewerten(1300, 90, 17.0, 62000, False, 40, PAR)
    assert a.bw_auszug == b.bw_auszug


def test_hoeheres_angebot_erhoeht_annahmebarwert():
    bw = [s.bw_annahme for s in optimieren(1300, 90, 17.0, 62000, False, AUF, PAR)]
    assert all(a < b for a, b in zip(bw, bw[1:]))


def test_grosse_luecke_fuehrt_zu_marktmiete():
    s = optimieren(1150, 90, 17.0, 58000, False, AUF, PAR)
    assert max(s, key=lambda x: x.bw_erwartet).aufschlag_pct >= 25


def test_bei_kleiner_luecke_liegt_optimum_im_inneren():
    """Der interessante Fall: Vertrag nahe am Markt, Leerstand teuer."""
    par = dict(PAR, leerstand_monate=5.0,
               neuvermietungskosten_monatsmieten=3.0, marktrisiko_abschlag=0.10)
    s = optimieren(1450, 90, 17.0, 58000, False, AUF, par)
    assert max(s, key=lambda x: x.bw_erwartet).aufschlag_pct != AUF[-1]


def test_laengerer_leerstand_macht_auszug_unattraktiver():
    assert (bewerten(1300, 90, 17.0, 62000, False, 10, PAR, leerstand_monate=6.0).bw_auszug
            < bewerten(1300, 90, 17.0, 62000, False, 10, PAR, leerstand_monate=1.0).bw_auszug)


if __name__ == "__main__":
    fehler = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok    {name}")
            except AssertionError as e:
                fehler += 1
                print(f"  ROT   {name}: {e}")
    print(f"\n{'alle Tests gruen' if not fehler else f'{fehler} Test(s) rot'}")
    sys.exit(1 if fehler else 0)
