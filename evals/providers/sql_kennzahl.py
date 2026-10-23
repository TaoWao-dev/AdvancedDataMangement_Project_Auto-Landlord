"""Provider fuer die SQL-Tasks (Analysen 1-3) - das "Modell" ist hier SQL.

Baut fuer jeden Datenstand eine Wegwerf-Datenbank aus genau den Rohordnern,
die der Testfall nennt, fuehrt die Kennzahl-Abfrage aus und gibt die Zeile
zurueck, die zum Filter passt. Die committete Datenbank und die
Kennzahl-CSV werden dabei nicht angefasst: alle Pfade zeigen in ein
temporaeres Verzeichnis.

Warum je Datenstand: die Referenzen vom 25.09. beschreiben den Markt am
25.09. Seit dem Abruf vom 09.10. gibt es fuer dieselbe PLZ und Groessenklasse
zwei Zeilen. Ein Test, der dann "irgendeine" Zeile nimmt, misst Zufall. Der
Provider meldet Mehrdeutigkeit als Fehler, statt eine Zeile zu waehlen.

promptfoo:  providers: [{id: "file://providers/sql_kennzahl.py"}]
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))

from src import clean, config as C, derive, extract, integrate, modell  # noqa: E402

_CACHE: dict[tuple, dict[str, list[dict]]] = {}


def _bauen(datenstand: tuple[str, ...]) -> dict[str, list[dict]]:
    """Alle Kennzahlen fuer einen Datenstand, als Zeilenlisten je Abfrage."""
    if datenstand in _CACHE:
        return _CACHE[datenstand]
    # Im Projekt, nicht in /tmp: die Pipeline schreibt Pfade relativ zur
    # Projektwurzel in die Provenienz. Gitignored (data/.eval_*).
    tmp = Path(tempfile.mkdtemp(prefix=".eval_", dir=WURZEL / "data"))
    alt = (C.RAW, C.INTERIM, C.PROCESSED, C.DB)
    try:
        (tmp / "raw").mkdir()
        for d in datenstand:
            shutil.copytree(alt[0] / d, tmp / "raw" / d)
        C.RAW, C.INTERIM, C.PROCESSED = tmp / "raw", tmp / "interim", tmp / "processed"
        C.DB = C.PROCESSED / f"{C.PROJEKT}.sqlite"
        with contextlib.redirect_stdout(io.StringIO()):
            extract.ausfuehren()
            res = integrate.ausfuehren(clean.ausfuehren())
            modell.ausfuehren(res["con"])
            derive.ausfuehren(res["con"])
        con = res["con"]
        ergebnis = {}
        for pfad in derive.abfragen():
            rows = con.execute(pfad.read_text(encoding="utf-8")).fetchall()
            ergebnis[pfad.name] = [dict(r) for r in rows]
        con.close()
    finally:
        C.RAW, C.INTERIM, C.PROCESSED, C.DB = alt
        shutil.rmtree(tmp, ignore_errors=True)
    _CACHE[datenstand] = ergebnis
    return ergebnis


def _auswerten(art: str | None, zeilen: list[dict], filt: dict) -> dict:
    if art == "abdeckung":
        return {"bezirke_in_konfiguration": len(zeilen),
                "bezirke_mit_schnappschuss": sum(1 for z in zeilen if z["abrufe"]),
                "beobachtungen_gesamt": sum(z["beobachtungen"] for z in zeilen),
                "ohne_schnappschuss": sorted(z["plz"] for z in zeilen if not z["abrufe"])}
    if art == "inseratsdauer":
        z = [r for r in zeilen if r["plz"] == filt.get("plz", "1020")]
        if not z:
            return {"fehler": "keine Zeile"}
        r = z[0]
        return {"inserate": r["inserate"], "davon_zensiert": r["davon_zensiert"],
                "abgaenge_ungemessen": r["abgaenge_ungemessen"],
                "anteil_aeltere_noch_online": r["anteil_aeltere_noch_online"],
                "zeilen_mit_dauer_ueber_null": sum(
                    1 for x in zeilen if (x["mittel_tage_abgeschlossen"] or 0) > 0),
                "anteil_zensiert": r["anteil_zensiert"],
                "auswertbar": r["mittel_tage_abgeschlossen"] is not None}
    # Zeilenvergleich: alle Filterschluessel, die Spalten der Abfrage sind.
    # 'status' ist keine Spalte - die Abfragen zaehlen nur aktive Inserate.
    passend = [z for z in zeilen
               if all(str(z[k]) == str(v) for k, v in filt.items() if k in z)]
    if len(passend) != 1:
        return {"fehler": f"{len(passend)} passende Zeilen - Filter oder Datenstand mehrdeutig"}
    return passend[0]


def ausfuehren(vars_: dict) -> str:
    stand = tuple(vars_.get("datenstand") or sorted(p.name for p in C.RAW.iterdir() if p.is_dir()))
    alle = _bauen(stand)
    abfrage = Path(vars_["abfrage"]).name
    if abfrage not in alle:
        return json.dumps({"fehler": f"Abfrage {abfrage} unbekannt"})
    return json.dumps(_auswerten(vars_.get("auswertung"), alle[abfrage], vars_.get("filter", {})),
                      ensure_ascii=False)


def call_api(prompt, options, context):
    return {"output": ausfuehren(context["vars"])}
