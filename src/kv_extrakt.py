"""Gate 4: die LLM-Extraktion der KV-Erhoehungen gegen den Wortlaut pruefen.

Die Extraktion (data/extrakt/kv_erhoehungen_*.json) ist die Ausgabe eines
Sprachmodells (prompts/kv_zeitreihe_v1.md). Sie geht nur in die Datenbank,
wenn jeder Datensatz an seiner Quelle haengt:

  1. Datei und Zeile existieren in kv_textblock.
  2. Der Wortlaut steht zeichengenau im Text dieser Zeile.
  3. Jeder extrahierte Prozentsatz und Betrag steht im Wortlaut - als Ziffer
     im deutschen Format oder als Zahlwort ("drei Prozent").
  4. Ein Datum steht im Wortlaut oder in der eigens genannten Datumszeile.

Was Gate 4 NICHT prueft: ob das Modell die richtige Zeile fuer die richtige
Branche und das richtige Jahr gewaehlt hat. Ein Wortlaut aus dem
Arbeiter-KV besteht Gate 4, wenn die Zahl darin steht. Das prueft erst das
Eval gegen die Referenzen (evals/references/kv_extraktion.json). Gate 4
faengt Halluzination, nicht Verwechslung.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
from pathlib import Path

from . import config as C

EXTRAKT = C.WURZEL / "data" / "extrakt"
ZAHLWORT = {1: "ein", 2: "zwei", 3: "drei", 4: "vier", 5: "fünf", 6: "sechs",
            7: "sieben", 8: "acht", 9: "neun", 10: "zehn"}
MONAT = {1: "Jänner", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni",
         7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November",
         12: "Dezember"}


def _schreibweisen(v: float) -> list[str]:
    out = {f"{v:g}".replace(".", ","), f"{v:.2f}".replace(".", ",")}
    if v == int(v):
        out.add(str(int(v)))
        if int(v) in ZAHLWORT:
            out.add(ZAHLWORT[int(v)])
        out.add(f"{int(v):,}".replace(",", "."))      # 3.750
    return sorted(out)


def _datum_schreibweisen(iso: str) -> list[str]:
    d = date.fromisoformat(iso)
    return [f"{d.day}. {MONAT[d.month]} {d.year}", f"{d.day}.{d.month}.{d.year}",
            f"{d.day}. {d.month}. {d.year}", f"{d.day}. {MONAT[d.month]}"]


def neueste_datei() -> Path | None:
    dateien = sorted(EXTRAKT.glob("kv_erhoehungen_*.json"))
    return dateien[-1] if dateien else None


def pruefen(datensaetze: list[dict], con: sqlite3.Connection) -> list[str]:
    def text(datei: str, zeile: int) -> str | None:
        rows = con.execute("SELECT text FROM kv_textblock WHERE datei = ? AND zeile_original = ?",
                           (datei, zeile)).fetchall()
        return "\n".join(r[0] for r in rows) if rows else None

    fehler = []
    for i, d in enumerate(datensaetze):
        wer = f"{d.get('branche_id')} {d.get('jahr')}"
        t = text(d["datei"], d["zeile"])
        if t is None:
            fehler.append(f"{wer}: Zeile {d['datei']}:{d['zeile']} gibt es nicht")
            continue
        if d["wortlaut"] not in t:
            fehler.append(f"{wer}: Wortlaut steht nicht in Zeile {d['zeile']}")
            continue
        for feld in ("prozent_min", "prozent_max", "prozent_mittel_laut_quelle",
                     "fixbetrag_eur", "deckel_eur"):
            v = d.get(feld)
            # Mit Zahlgrenzen: "2,5" steckt als Zeichenkette in "2,55". Die
            # erste Fassung prueft ohne Grenze und liess 2,5 % durch (Test
            # test_gate4_faengt_zahl_die_nicht_im_wortlaut_steht).
            if v is not None and not any(
                    re.search(rf"(?<![\d,.]){re.escape(s)}(?![\d]|,\d)", d["wortlaut"])
                    for s in _schreibweisen(float(v))):
                fehler.append(f"{wer}: {feld}={v} steht nicht im Wortlaut")
        if d.get("gueltig_ab"):
            quelle = d["wortlaut"]
            if d.get("datum_zeile"):
                dt = text(d.get("datum_datei") or d["datei"], d["datum_zeile"])
                if dt is None or d.get("datum_wortlaut", "") not in dt:
                    fehler.append(f"{wer}: Datumswortlaut steht nicht in Zeile {d['datum_zeile']}")
                    continue
                quelle = d["datum_wortlaut"]
            if not any(s in quelle for s in _datum_schreibweisen(d["gueltig_ab"])):
                # "ab 1. April und ... 2024": Tag und Monat im Wortlaut, Jahr dabei
                j = date.fromisoformat(d["gueltig_ab"])
                if not (f"{j.day}. {MONAT[j.month]}" in quelle and str(j.year) in quelle):
                    fehler.append(f"{wer}: gueltig_ab={d['gueltig_ab']} steht nicht im Wortlaut")
    return fehler


def satz_fuer_index(d: dict) -> float:
    """Ein Satz je Abschluss. Nennt die Quelle bei einer Staffelung einen
    Durchschnitt, gilt dieser; sonst die Mitte der Spanne. Das ist eine
    Rechenregel des Programms, keine Angabe der Quelle."""
    if d.get("prozent_mittel_laut_quelle") is not None:
        return float(d["prozent_mittel_laut_quelle"])
    return (float(d["prozent_min"]) + float(d["prozent_max"])) / 2


def laden(con: sqlite3.Connection) -> dict:
    pfad = neueste_datei()
    if pfad is None:
        print("kv_extrakt: keine Extraktion vorhanden - uebersprungen")
        return {"datensaetze": 0}
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    ds = daten["erhoehungen"]
    fehler = pruefen(ds, con)
    print(f"\n  GATE 4: Extraktion gegen Wortlaut ({pfad.name}, {len(ds)} Datensaetze)")
    for f in fehler:
        print(f"    FEHLER {f}")
    if fehler:
        print("  GATE 4: NICHT BESTANDEN - die Extraktion geht nicht in die Datenbank.")
        raise SystemExit(2)
    print("  GATE 4: bestanden")
    for d in ds:
        # Ein Datum, das die Quelle nicht nennt, wird fuer die Rechnung auf den
        # 1. Jaenner gesetzt - sichtbar in datum_angenommen, nicht still.
        angenommen = d.get("gueltig_ab") is None
        con.execute(
            "INSERT INTO kv_erhoehung VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (d["branche_id"], d["jahr"],
             d.get("gueltig_ab") or f"{d['jahr']}-01-01", int(angenommen),
             d["prozent_min"], d["prozent_max"], d.get("prozent_mittel_laut_quelle"),
             round(satz_fuer_index(d), 4), d.get("fixbetrag_eur"), d.get("deckel_eur"),
             d["datei"], d["zeile"], d["wortlaut"]))
    con.commit()
    return {"datensaetze": len(ds), "datei": pfad.name, "modell": daten.get("_modell")}
