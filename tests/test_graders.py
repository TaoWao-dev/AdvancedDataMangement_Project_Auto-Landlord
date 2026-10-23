"""Selbstpruefung der Grader (Vorgabe Deliverable 3: "Grader selbst geprueft").

Ein Grader, der immer gruen ist, misst nichts. Jeder Grader bekommt hier
Faelle, die bestehen MUESSEN, und Faelle, die scheitern MUESSEN - darunter
genau die Fehler, die ein Modell bei dieser Aufgabe wahrscheinlich macht.

    python3 tests/test_graders.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from evals.graders import (extraktion, klassifikation, sql_referenz,  # noqa: E402
                           vorlage_pflichten, zahlen_herkunft)
from evals.graders.gemeinsam import json_aus_antwort  # noqa: E402

KV = json.loads((WURZEL / "evals" / "references" / "kv_extraktion.json").read_text(encoding="utf-8"))
FALL = {f["fall_id"]: f for f in KV["faelle"]}


# ──────────────────────────────────────────────────────────── gemeinsam
def test_json_aus_antwort_mit_zaun_und_denkblock():
    t = '<think>{"falsch": 1}</think>\nHier:\n```json\n{"a": 1}\n```\nfertig'
    assert json_aus_antwort(t) == {"a": 1}


def test_kaputtes_json_wird_nicht_repariert():
    assert json_aus_antwort('{"a": 1,}') is None


# ──────────────────────────────────────────────────────────── Extraktion
def test_referenzantwort_selbst_besteht_jeden_fall():
    """Die Untergrenze: wer genau die Referenz liefert, besteht."""
    for fid, f in FALL.items():
        r = extraktion.pruefen(json.dumps(f["erwartete_antwort"]), f["erwartete_antwort"])
        assert r["pass"], (fid, r["reason"])


def test_vorjahreswert_faellt_durch():
    """Versicherung 2026: kein Satz in der Quelle. 2,9 % ist 2025."""
    soll = FALL["kv_versicherung_innendienst"]["erwartete_antwort"]
    ist = dict(soll, abschluss_gefunden=True, prozent_min=2.9, prozent_max=2.9,
               fixbetrag_eur=19.5, fundstelle_zeile=3623)
    assert not extraktion.pruefen(json.dumps(ist), soll)["pass"]


def test_erfundenes_datum_faellt_durch():
    """Oeffentlicher Dienst: die Quelle nennt kein Datum. 1.1.2026 ist plausibel und falsch."""
    soll = FALL["kv_oeffentlicher_dienst"]["erwartete_antwort"]
    ist = dict(soll, geltungsbeginn="2026-01-01")
    r = extraktion.pruefen(json.dumps(ist), soll)
    assert not r["pass"] and "geltungsbeginn" in r["reason"]


def test_gleicher_prozentsatz_aus_falschem_kv_faellt_ueber_die_fundstelle():
    """Handel: Arbeiter und Angestellte haben beide 2,55 %. Nur die Zeile trennt."""
    soll = FALL["kv_handel_angestellte"]["erwartete_antwort"]
    ist = dict(soll, fundstelle_zeile=1911)
    r = extraktion.pruefen(json.dumps(ist), soll)
    assert not r["pass"] and "fundstelle" in r["reason"]


def test_forderung_statt_abschluss_faellt_durch():
    soll = FALL["kv_it"]["erwartete_antwort"]
    ist = dict(soll, prozent_min=3.9, prozent_max=3.9, fundstelle_zeile=680)
    assert not extraktion.pruefen(json.dumps(ist), soll)["pass"]


def test_spanne_als_einzelwert_faellt_durch():
    soll = FALL["kv_it"]["erwartete_antwort"]
    ist = dict(soll, prozent_min=3.1, prozent_max=3.1)
    assert not extraktion.pruefen(json.dumps(ist), soll)["pass"]


def test_nicht_bewertetes_feld_zaehlt_nicht():
    soll = FALL["kv_privatkrankenanstalten"]["erwartete_antwort"]
    ist = dict(soll, bezugsgroesse="ist")
    assert extraktion.pruefen(json.dumps(ist), soll, ["bezugsgroesse"])["pass"]
    assert not extraktion.pruefen(json.dumps(ist), soll)["pass"]


def test_null_heisst_null_nicht_null_prozent():
    soll = FALL["kv_wirtschaftstreuhaender"]["erwartete_antwort"]
    ist = dict(soll, prozent_min=0, prozent_max=0)
    assert not extraktion.pruefen(json.dumps(ist), soll)["pass"]


def test_zahl_als_text_wird_verglichen_nicht_abgelehnt():
    soll = FALL["kv_handel_angestellte"]["erwartete_antwort"]
    ist = dict(soll, prozent_min="2.55", prozent_max="2.55")
    assert extraktion.pruefen(json.dumps(ist), soll)["pass"]


def test_prosa_statt_json_faellt_durch():
    soll = FALL["kv_handel_angestellte"]["erwartete_antwort"]
    assert not extraktion.pruefen("Die Gehälter steigen um 2,55 Prozent.", soll)["pass"]


# ──────────────────────────────────────────────────────── Klassifikation
def test_klassifikation_richtig_falsch_unklar():
    assert klassifikation.pruefen('{"moebliert_kurzzeit": "ja"}', "ja")["pass"]
    assert not klassifikation.pruefen('{"moebliert_kurzzeit": "nein"}', "ja")["pass"]
    assert klassifikation.pruefen("nein", "nein")["pass"]


def test_unklare_referenz_wird_nicht_gewertet():
    r = klassifikation.pruefen('{"moebliert_kurzzeit": "ja"}', "unklar")
    assert r["gewertet"] is False


def test_ausweichende_antwort_ist_keine_antwort():
    # Beide Richtungen: eine Antwort, die beide Woerter enthaelt, darf weder
    # als ja noch als nein durchgehen (Gegenprobe vom 23.10.: die erste
    # Fassung dieses Tests prueft nur eine Richtung und liess einen
    # Teilwort-Grader durch).
    assert not klassifikation.pruefen("nein, eher doch ja", "nein")["pass"]
    assert not klassifikation.pruefen("nein, eher doch ja", "ja")["pass"]
    assert not klassifikation.pruefen("unklar, eher ja", "ja")["pass"]
    assert not klassifikation.pruefen('{"moebliert_kurzzeit": "vielleicht"}', "nein")["pass"]


# ──────────────────────────────────────────────────────────── SQL
def test_sql_toleranz_und_fallzahl_exakt():
    soll = {"fallzahl": 15, "median_eur_m2": 26.67, "belastbarkeit": "belastbar"}
    assert sql_referenz.pruefen('{"fallzahl": 15, "median_eur_m2": 26.674, "belastbarkeit": "belastbar"}', soll)["pass"]
    assert not sql_referenz.pruefen('{"fallzahl": 16, "median_eur_m2": 26.67, "belastbarkeit": "belastbar"}', soll)["pass"]
    assert not sql_referenz.pruefen('{"fallzahl": 15, "median_eur_m2": 26.69, "belastbarkeit": "belastbar"}', soll)["pass"]
    assert not sql_referenz.pruefen('{"fehler": "2 passende Zeilen"}', soll)["pass"]
    # Fallzahl exakt, auch wenn die Toleranz fuer Euro-Werte grosszuegig ist.
    # Mit 0,01 war das von einer Toleranzpruefung nicht zu unterscheiden.
    assert not sql_referenz.pruefen('{"fallzahl": 16, "median_eur_m2": 26.67, "belastbarkeit": "belastbar"}',
                                    soll, toleranz=1.0)["pass"]


# ───────────────────────────────────────────────────── Zahlenherkunft
Q = {"kennzahl": [(24.01, "kennzahl_bezirksvergleich.csv:median_eur_m2"),
                  (32.0, "kennzahl_bezirksvergleich.csv:fallzahl"),
                  (0.482, "kennzahl_empfehlung.csv:mittel_p_annahme"),
                  (147001.0, "kennzahl_empfehlung.csv:mehrwert_gegen_nur_index"),
                  (2251247.0, "kennzahl_empfehlung.csv:bw_empfehlung_summe")],
     "annahme": [(2.5, "config/portfolio.json:leerstand_monate")],
     "konstante": [(50.0, "konstante: Portfoliogroesse")],
     "daten": {"2026-10-09": "kennzahl_marktniveau.csv:abruf_datum"}}


def test_belegte_zahlen_bestehen():
    t = ("Die Marktmiete liegt bei 24,01 €/m² (n = 32) [kennzahl_bezirksvergleich]. "
         "Annahme 2,5 Monate Leerstand. Datenstand 09.10.2026, 50 Wohnungen.\n\n"
         "Barwert 2.251.247 €, Mehrwert rund 147.000 €, Annahmequote 48 % [kennzahl_empfehlung].")
    r = zahlen_herkunft.pruefen(t, Q)
    assert r["pass"], r["reason"]


def test_erfundene_zahl_faellt_durch():
    r = zahlen_herkunft.pruefen("Der gewerbliche Median liegt 16 % über dem privaten.", Q)
    assert not r["pass"] and "16 %" in r["reason"]


def test_falsch_gerundet_faellt_durch():
    assert zahlen_herkunft.pruefen("rund 24,0 €/m²", Q)["pass"]
    assert not zahlen_herkunft.pruefen("rund 24,1 €/m²", Q)["pass"]


def test_selbst_gerechnete_differenz_faellt_durch():
    """24,01 - 2,5 = 21,51: eine Rechnung des Modells, keine Kennzahl."""
    assert not zahlen_herkunft.pruefen("Abstand 21,51 €/m²", Q)["pass"]


def test_bezeichner_sind_keine_zahlen():
    t = "Siehe E39, Annahme A10, Q1 und `kennzahl_empfehlung_vertrag.csv`, Vertrag NO-07."
    r = zahlen_herkunft.pruefen(t, Q)
    assert r["pass"] and not r["belegt"], r


def test_zitat_bindet_an_die_zitierte_datei():
    """Der echte Fehler aus der ersten Vorlage: 20 + 10 Vertraege, geschrieben
    als 40. Die 40 stand zufaellig in einer anderen Quelle und galt als belegt."""
    q = {"kennzahl": [(20.0, "kennzahl_empfehlung.csv:vertraege"),
                      (10.0, "kennzahl_empfehlung.csv:vertraege"),
                      (40.0, "kennzahl_sensitivitaet.csv:wert")],
         "annahme": [], "konstante": [(50.0, "konstante: Portfolio")], "daten": {}}
    falsch = "Für 40 der 50 Wohnungen gibt es keine Marktmiete [kennzahl_empfehlung]."
    richtig = "Sonnwendviertel (20 Verträge) und Seestadt (10 Verträge) [kennzahl_empfehlung]."
    assert not zahlen_herkunft.pruefen(falsch, q)["pass"]
    assert zahlen_herkunft.pruefen(richtig, q)["pass"]
    # ohne Zitat greift die Bindung nicht - dann ist es nur ein schwacher Beleg
    assert zahlen_herkunft.pruefen("Für 40 der 50 Wohnungen.", q)["pass"]


def test_typografisches_minus_ist_ein_vorzeichen():
    q = {"kennzahl": [(-2.9, "kennzahl_marktentwicklung.csv:veraenderung_seit_erstem_abruf_pct")],
         "annahme": [], "konstante": [], "daten": {}}
    assert zahlen_herkunft.pruefen("Rückgang −2,9 % [kennzahl_marktentwicklung]", q)["pass"]
    assert zahlen_herkunft.pruefen("Rückgang -2,9 % [kennzahl_marktentwicklung]", q)["pass"]
    assert not zahlen_herkunft.pruefen("Anstieg 2,9 % [kennzahl_marktentwicklung]", q)["pass"]


def test_falsches_datum_faellt_durch():
    assert not zahlen_herkunft.pruefen("Datenstand 10.10.2026", Q)["pass"]


def test_bekannte_luecke_jahreszahl():
    """Dokumentierte Grenze: vierstellige Jahreszahlen werden nicht geprueft.
    Faellt dieser Test, hat jemand die Ausnahme geaendert - dann den
    Modulkopf und 06_schritt5 anpassen."""
    assert zahlen_herkunft.pruefen("Im Jahr 2031 waere das anders.", Q)["pass"]


def test_echte_kennzahlen_sind_als_quelle_lesbar():
    q = zahlen_herkunft.quellen_laden()
    assert len(q["kennzahl"]) > 100 and q["daten"]


# ────────────────────────────────────────────────────── Pflichten Vorlage
def test_pflichten_vollstaendig_und_unvollstaendig():
    gut = ("# Vorlage\n## Ausgangslage\n## Wie sie vorbereitet wurde\n## Die entscheidenden Daten\n"
           "## Optionen\n## Empfehlung\n## Grenzen\nFallzahl, belastbar. Der erste Abruf war eine Teilseite. "
           "Verträge synthetisch, Parameter sind Annahmen. Das Einkommen ist kein Preisargument.")
    assert vorlage_pflichten.pruefen(gut)["pass"]
    schlecht = gut.replace("Der erste Abruf war eine Teilseite. ", "")
    r = vorlage_pflichten.pruefen(schlecht)
    assert not r["pass"] and "Marktbeobachtung" in r["reason"] and "Teilseite" in r["reason"]


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
