"""Tests gegen echte Schnappschuesse. Kein Netz, keine Zufallswerte.

Datenbasis, beide im Repo:

    data/raw/2026-09-25/wh_1020_mietwohnungen_2026-09-25T1555.json
        der richtige Schnappschuss, 90 Inserate aus 1020 Wien

    data/sample/negativ_falscher_vertical.json
        die versehentlich gespeicherte Marktplatzseite (verticalId 5,
        13,3 Mio Treffer). Sie ist gueltiges JSON und wuerde ohne Gate
        stillschweigend einen Median liefern. Deshalb liegt sie hier.

Aufruf:

    python3 -m pytest tests/        (wenn pytest vorhanden)
    python3 tests/test_pipeline.py  (ohne pytest, gleicher Umfang)
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from src import clean as CL          # noqa: E402
from src import config as C          # noqa: E402
from src import derive, integrate    # noqa: E402
from src import validierung as V     # noqa: E402
from src import wh_next_data as P    # noqa: E402

ECHT = WURZEL / "data" / "raw" / "2026-09-25" / \
    "wh_1020_mietwohnungen_2026-09-25T1555.json"
REFERENZEN = WURZEL / "evals" / "references"
FALSCH = WURZEL / "data" / "sample" / "negativ_falscher_vertical.json"


# ------------------------------------------------------------------- Parser
def test_parst_echten_schnappschuss():
    s = P.parse(ECHT)
    assert len(s.inserate) == 90, len(s.inserate)
    assert s.treffer_gesamt == 154
    assert s.geliefert == 90


def test_abrufzeit_kommt_vom_server_nicht_vom_parser():
    """Damit ein erneut verarbeiteter Schnappschuss demselben Zeitpunkt
    zugeordnet bleibt - sonst waere der zweite Lauf ein anderer Datenstand."""
    s = P.parse(ECHT)
    assert s.abruf_ts.startswith("2026-09-25T15:55"), s.abruf_ts
    assert all(i.abruf_ts == s.abruf_ts for i in s.inserate)


def test_pflichtfelder_vollstaendig():
    s = P.parse(ECHT)
    assert all(i.ad_id and i.plz and i.miete_eur for i in s.inserate)
    assert sum(1 for i in s.inserate if i.flaeche_m2) == 89  # 1 ohne Flaeche


def test_fehlende_werte_bleiben_none_und_werden_nicht_geschaetzt():
    s = P.parse(ECHT)
    ohne = [i for i in s.inserate if i.flaeche_m2 is None]
    assert len(ohne) == 1
    assert ohne[0].eur_pro_m2 is None


def test_status_wird_uebernommen():
    s = P.parse(ECHT)
    status: dict[str, int] = {}
    for i in s.inserate:
        status[i.status] = status.get(i.status, 0) + 1
    assert status == {"aktiv": 87, "reserviert": 3}, status


def test_mehrwertige_freiflaeche_wird_liste():
    s = P.parse(ECHT)
    assert [i for i in s.inserate if len(i.freiflaeche) > 1]
    assert all(isinstance(i.freiflaeche, list) for i in s.inserate)


def test_eur_pro_m2_des_portals_stimmt_mit_eigener_rechnung():
    """Kontrolle der Feldbedeutung: PRICE / ESTATE_SIZE muss
    PRICE/SQUARE_METER ergeben. Wenn nicht, meint ein Feld etwas anderes
    als angenommen."""
    s = P.parse(ECHT)
    n = 0
    for i in s.inserate:
        if i.miete_eur and i.flaeche_m2 and i.eur_pro_m2:
            assert abs(i.miete_eur / i.flaeche_m2 - i.eur_pro_m2) < 0.02, i.ad_id
            n += 1
    assert n > 80, n


# --------------------------------------------------- Umwandlungen (clean.py)
def test_dezimalpunkt_wird_nicht_als_tausenderpunkt_gelesen():
    """willhaben liefert '24.791666' als Dezimalpunkt. Ein naives
    replace('.','') machte daraus 24791666 - ein Fehler, der plausibel
    aussieht, weil keine Zeile ausfaellt."""
    assert CL.to_number("24.791666") == 24.791666
    assert CL.to_number("1.234,56") == 1234.56
    assert CL.to_number("1 234,56") == 1234.56
    assert CL.to_number("0,76-") == -0.76
    assert CL.to_number("") is None
    assert CL.to_number("-999") is None          # Luecke, nicht Messwert


def test_datum_wird_tag_zuerst_gelesen():
    """04.06.2025 ist der 4. Juni. Monat zuerst waere der 6. April - ein
    Fehler, der nur an Tagen ueber 12 auffaellt."""
    d = CL.to_date("04.06.2025")
    assert (d.year, d.month, d.day) == (2025, 6, 4)
    assert CL.to_date("2025-06-04") == d
    assert CL.to_date("13.13.2025") is None


def test_plz_wird_vierstellig_normalisiert():
    assert CL.normalize_plz("1020 Wien, Leopoldstadt") == "1020"
    assert CL.normalize_plz("Wien") is None


def test_allowlist_verwirft_anbieterdaten():
    s = P.parse(ECHT)
    from dataclasses import asdict
    sauber, verworfen = CL.drop_pii(asdict(s.inserate[0]))
    assert "seo_url" in verworfen
    assert set(sauber) <= set(C.PII_ERLAUBT)
    assert "privat" in sauber, "Privat/Gewerblich muss bleiben, das ist Analyse"


def test_kein_pii_in_bereinigten_zeilen():
    from dataclasses import asdict
    s = P.parse(ECHT)
    zeilen = [CL.drop_pii(asdict(i))[0] for i in s.inserate]
    assert CL.pii_kontrolle(zeilen) == []


def test_eigener_dateiname_ist_kein_pii_befund():
    """Der Schnappschussname enthaelt Zifferngruppen und traf das
    Telefonmuster. Ausgenommen wurde das Feld, nicht das Muster."""
    zeilen = [{"plz": "1020", "ad_id": "1808408930",
               "snapshot_datei": "wh_1020_mietwohnungen_2026-09-25T1555.json"}]
    assert CL.pii_kontrolle(zeilen) == []


def test_redaktion_findet_kontaktdaten():
    t, tr = CL.redigiere_text("Anfragen an max.muster@example.at oder "
                              "+43 664 1234567, siehe www.example.at")
    assert "max.muster@" not in t and "1234567" not in t
    assert set(tr) == {"email", "url", "telefon"}


def test_redaktion_laesst_normalen_text_unveraendert():
    t, tr = CL.redigiere_text("Helle Wohnung mit Balkon in Ruhelage")
    assert tr == [] and t == "Helle Wohnung mit Balkon in Ruhelage"


# --------------------------------------------------------- Gate 1 (Eingang)
def test_gate_laesst_richtigen_schnappschuss_durch():
    b = V.pruefe(P.parse(ECHT), erwartete_plz="1020")
    assert V.bestanden(b), [x for x in b if x.stufe == "fehler"]


def test_gate_faengt_falsche_seite_ab():
    b = V.pruefe(P.parse(FALSCH), erwartete_plz="1020")
    assert not V.bestanden(b)
    gruende = {x.pruefung for x in b if x.stufe == "fehler"}
    assert "richtige Rubrik" in gruende       # verticalId 5 statt 2
    assert "Trefferzahl plausibel" in gruende
    assert "einheitliche PLZ" in gruende


def test_unvollstaendige_seite_ist_warnung_kein_fehler():
    s = P.parse(ECHT)
    assert not s.vollstaendig                      # 90 von 154
    b = V.pruefe(s, erwartete_plz="1020")
    assert V.bestanden(b)
    assert any(x.pruefung == "Vollstaendigkeit" and x.stufe == "warnung"
               for x in b)


def test_plz_kommt_aus_dem_dateinamen():
    """Die Namenskonvention wh_<plz>_<suche>_<datum>.json ist die einzige
    unabhaengige Quelle dafuer, welchen Bezirk die Datei zeigen SOLL."""
    assert V.plz_aus_dateiname("wh_1100_mietwohnungen_2026-10-02T0910.json") \
        == "1100"
    assert V.plz_aus_dateiname("irgendwas.json") is None


def test_gate_meldet_plz_abweichung():
    """Der Vorfall: drei Dateien mit 1010/1030 im Namen enthielten 1020er
    Daten, weil __NEXT_DATA__ bei Navigation im Browser nicht nachlaedt."""
    b = V.pruefe(P.parse(ECHT), erwartete_plz="1100")
    assert not V.bestanden(b)
    assert any("PLZ" in x.pruefung for x in b if x.stufe == "fehler")


# ------------------------------------------------- Datenbank und Kennzahlen
def _baue(pfad: Path) -> sqlite3.Connection:
    res = integrate.ausfuehren(pfad=pfad)
    derive.ausfuehren(res["con"])
    return res["con"]


def test_median_liegt_zwischen_min_und_max(tmp_path=None):
    ziel = Path(tmp_path or C.PROCESSED) / "test_median.sqlite"
    con = _baue(ziel)
    kaputt = con.execute(
        "SELECT COUNT(*) FROM v_marktniveau"
        " WHERE median_eur_m2 < min_eur_m2 OR median_eur_m2 > max_eur_m2"
    ).fetchone()[0]
    con.close()
    ziel.unlink(missing_ok=True)
    assert kaputt == 0


def test_jede_beobachtung_haengt_an_einem_bezirk(tmp_path=None):
    ziel = Path(tmp_path or C.PROCESSED) / "test_fk.sqlite"
    con = _baue(ziel)
    waise = con.execute(
        "SELECT COUNT(*) FROM inserat_beobachtung io"
        " LEFT JOIN bezirk b ON b.plz = io.plz WHERE b.plz IS NULL"
    ).fetchone()[0]
    con.close()
    ziel.unlink(missing_ok=True)
    assert waise == 0


def test_fallzahl_steht_an_jeder_aggregatzeile(tmp_path=None):
    """Ein Median ueber vier Inserate ist kein Marktpreis. Ohne Fallzahl in
    derselben Zeile sieht man den Unterschied nicht."""
    ziel = Path(tmp_path or C.PROCESSED) / "test_fallzahl.sqlite"
    con = _baue(ziel)
    zeilen = con.execute("SELECT * FROM v_marktniveau").fetchall()
    con.close()
    ziel.unlink(missing_ok=True)
    assert zeilen
    for z in zeilen:
        assert z["fallzahl"] >= 1
        assert z["belastbarkeit"] in ("belastbar", "duenn", "nicht belastbar")


def test_zweiter_lauf_liefert_dieselben_zahlen(tmp_path=None):
    """Abnahmekriterium der Lehrveranstaltung fuer Schritt 2. Die Datenbank
    wird bei jedem Lauf aus data/raw/ neu gebaut; deshalb darf sie sich
    zwischen zwei Laeufen nicht unterscheiden."""
    basis = Path(tmp_path or C.PROCESSED)
    fingerabdruecke = []
    for i in (1, 2):
        ziel = basis / f"test_lauf{i}.sqlite"
        con = _baue(ziel)
        fingerabdruecke.append([
            tuple(r) for r in con.execute(
                "SELECT plz, groessenklasse, abruf_datum, fallzahl,"
                " median_eur_m2, q1_eur_m2, q3_eur_m2 FROM v_marktniveau"
                " ORDER BY plz, groessenklasse, abruf_datum")])
        con.close()
        ziel.unlink(missing_ok=True)
    assert fingerabdruecke[0] == fingerabdruecke[1]
    assert fingerabdruecke[0], "leerer Vergleich beweist nichts"


def test_datenbank_ist_byteweise_reproduzierbar(tmp_path=None):
    """Die Datenbank wird committet (Vorgabe Schritt 3). Das ist nur sinnvoll,
    wenn zwei Laeufe dieselbe Datei erzeugen - sonst rauscht bei jedem Lauf ein
    Diff durch. Dafuer darf kein Wert aus der Uhr kommen: qs_befund fuehrt den
    DATENSTAND, nicht den Laufzeitpunkt (Entscheidungslog E26)."""
    import hashlib, time
    basis = Path(tmp_path or C.PROCESSED)
    hashes = []
    for i in (1, 2):
        ziel = basis / f"test_byte{i}.sqlite"
        con = integrate.ausfuehren(pfad=ziel)["con"]
        con.close()
        hashes.append(hashlib.sha256(ziel.read_bytes()).hexdigest())
        ziel.unlink(missing_ok=True)
        if i == 1:
            time.sleep(1.1)      # eine Sekunde Abstand: eine Uhrzeit im
                                 # Datenbestand wuerde jetzt auffallen
    assert hashes[0] == hashes[1], hashes


def test_reservierte_inserate_zaehlen_nicht_zum_angebot(tmp_path=None):
    """Reservierte Objekte sind kein Angebot mehr und ueberdurchschnittlich
    attraktiv - sie wuerden den Median nach oben ziehen."""
    ziel = Path(tmp_path or C.PROCESSED) / "test_status.sqlite"
    con = _baue(ziel)
    alle = con.execute("SELECT COUNT(*) FROM inserat_beobachtung").fetchone()[0]
    angebot = con.execute("SELECT COUNT(*) FROM v_angebot").fetchone()[0]
    res = con.execute("SELECT COUNT(*) FROM inserat_beobachtung"
                      " WHERE status = 'reserviert'").fetchone()[0]
    con.close()
    ziel.unlink(missing_ok=True)
    assert res == 3
    assert angebot == alle - res - 1      # 3 reserviert, 1 ohne Flaeche


def test_fehlende_bezirke_erscheinen_als_luecke_nicht_als_annahme(tmp_path=None):
    """v_cluster_marktmiete muss fuer jeden Portfolio-Cluster eine Zeile
    liefern, auch ohne Schnappschuss - mit 'kein Schnappschuss' statt einer
    stillschweigend eingesetzten Zahl."""
    ziel = Path(tmp_path or C.PROCESSED) / "test_luecke.sqlite"
    con = _baue(ziel)
    zeilen = {r["plz"]: r["eignung"]
              for r in con.execute("SELECT plz, eignung FROM v_cluster_marktmiete")}
    con.close()
    ziel.unlink(missing_ok=True)
    portfolio = {b["plz"] for b in C.BEZIRKE if b["cluster_id"]}
    assert set(zeilen) == portfolio, (set(zeilen), portfolio)
    assert zeilen["1100"] == "kein Schnappschuss"


# ------------------------------------------------- Vorgaben der Lehrveranstaltung
def test_datenbankname_kommt_aus_der_konfiguration():
    """Die Vorgabe: der Datenbankname steht in src/config.py (PROJEKT).
    Zweimal dieselbe Zeichenkette zu pflegen ist eine Fehlerquelle."""
    assert C.DB.name == f"{C.PROJEKT}.sqlite", C.DB.name
    assert C.DB.parent == C.PROCESSED


def test_alle_tabellen_des_schemas_existieren_und_sind_gefuellt_oder_erklaert(
        tmp_path=None):
    """Jede Tabelle aus schema.sql muss in der gebauten Datenbank vorkommen.
    Leer sein darf sie - aber nur die, deren Quelle nachweislich fehlt."""
    ziel = Path(tmp_path or C.PROCESSED) / "test_tabellen.sqlite"
    con = _baue(ziel)
    schema = (C.SQL / "schema.sql").read_text(encoding="utf-8")
    erwartet = set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)", schema))
    da = {r["name"] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    fehlend = erwartet - da
    zahlen = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in sorted(erwartet & da)}
    con.close()
    ziel.unlink(missing_ok=True)
    assert not fehlend, fehlend
    # erwartet leer, mit Grund:
    #   indexreihe       - Tariflohnindex und VPI noch nicht beschafft
    #   zuordnungsluecke - es gibt keine Luecke, das ist das gute Ergebnis
    leer_erlaubt = {"indexreihe", "zuordnungsluecke"}
    unerwartet_leer = {t for t, n in zahlen.items()
                       if n == 0 and t not in leer_erlaubt}
    assert not unerwartet_leer, (unerwartet_leer, zahlen)
    assert zahlen["bezirk"] == len(C.BEZIRKE)
    assert zahlen["snapshot"] >= 1
    assert zahlen["inserat_beobachtung"] == 90


def test_keine_personenspalte_in_der_datenbank(tmp_path=None):
    """Die Datenbank wird committet. Eine Spalte, die nicht in der Allowlist
    steht, hat in ihr nichts zu suchen - unabhaengig davon, ob gerade ein
    Wert darin steht."""
    ziel = Path(tmp_path or C.PROCESSED) / "test_pii.sqlite"
    con = _baue(ziel)
    verboten = set(C.PII_VERWORFEN)
    treffer = []
    for (tab,) in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'").fetchall():
        for s in con.execute(f"PRAGMA table_info({tab})"):
            if s["name"].lower() in verboten:
                treffer.append(f"{tab}.{s['name']}")
    con.close()
    ziel.unlink(missing_ok=True)
    assert not treffer, treffer


def test_kennzahlen_stimmen_mit_den_referenzantworten(tmp_path=None):
    """Der Kern von Schritt 4: die Abfragen werden gegen Referenzen geprueft,
    die unabhaengig entstanden sind (evals/nachrechnen_marktniveau.py liest die
    Rohdatei ohne src/ und ohne SQL). Weichen sie ab, ist eine der beiden
    Seiten falsch - und das soll auffallen, nicht untergehen."""
    ziel = Path(tmp_path or C.PROCESSED) / "test_referenz.sqlite"
    con = _baue(ziel)
    ref = json.loads((REFERENZEN / "marktniveau.json").read_text(encoding="utf-8"))
    geprueft = 0
    for fall in ref["faelle"]:
        f = fall["eingabe"]["filter"]
        r = con.execute(
            """SELECT fallzahl, median_eur_m2, q1_eur_m2, q3_eur_m2,
                      min_eur_m2, max_eur_m2, davon_privat, davon_gewerblich,
                      belastbarkeit
               FROM v_marktniveau
               WHERE plz = ? AND groessenklasse = ? AND abruf_datum = ?""",
            (f["plz"], f["groessenklasse"], f["abruf_datum"])).fetchone()
        assert r is not None, fall["fall_id"]
        for feld, soll in fall["erwartete_antwort"].items():
            ist = r[feld]
            tol = fall["toleranz"].get(feld, 0)
            if isinstance(soll, (int, float)) and not isinstance(soll, bool):
                assert abs(ist - soll) <= tol, (fall["fall_id"], feld, ist, soll)
            else:
                assert ist == soll, (fall["fall_id"], feld, ist, soll)
            geprueft += 1
    con.close()
    ziel.unlink(missing_ok=True)
    assert geprueft >= 30, geprueft


def test_referenzen_tragen_herkunft_und_unsicherheit():
    """Die Vorgabe verlangt je Fall Eingabe, erwartete Antwort, Herkunft
    (wer, wann) und Unsicherheit. Eine Referenz ohne Herkunft ist eine
    Behauptung."""
    dateien = sorted(REFERENZEN.glob("*.json"))
    assert dateien, "keine Referenzdateien"
    for d in dateien:
        inhalt = json.loads(d.read_text(encoding="utf-8"))
        for fall in inhalt["faelle"]:
            if "rolle" in fall:          # handproben.json, anderes Schema
                assert {"rechnung", "erwartet_eur_m2"} <= set(fall), fall
                continue
            fehlend = {"fall_id", "eingabe", "erwartete_antwort", "pruefregel",
                       "herkunft", "unsicherheit"} - set(fall)
            assert not fehlend, (d.name, fall.get("fall_id"), fehlend)
            assert {"wer", "wann"} <= set(fall["herkunft"]), fall["fall_id"]


if __name__ == "__main__":
    import tempfile
    fehler = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, fn in sorted(globals().items()):
            if not (name.startswith("test_") and callable(fn)):
                continue
            try:
                kwargs = {"tmp_path": tmp} if "tmp_path" in \
                    fn.__code__.co_varnames[:fn.__code__.co_argcount] else {}
                fn(**kwargs)
                print(f"  ok    {name}")
            except AssertionError as e:
                fehler += 1
                print(f"  ROT   {name}: {e}")
            except Exception as e:  # noqa: BLE001
                fehler += 1
                print(f"  BRUCH {name}: {type(e).__name__}: {e}")
    print(f"\n{'alle Tests gruen' if not fehler else f'{fehler} Test(s) rot'}")
    sys.exit(1 if fehler else 0)
