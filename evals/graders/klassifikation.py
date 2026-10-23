"""Grader fuer die Titelklassifikation "moebliert / Kurzzeit" (E38).

Massstab: Markierung des Studierenden (evals/references/moebliert.json).
Erlaubte Antworten: ja, nein, unklar. Faelle, die der Studierende als
"unklar" markiert hat, gehen nicht in die Trefferquote (E37, offen gelassen
und hier so entschieden): ein Titel, bei dem schon der Mensch unsicher ist,
taugt nicht als Massstab. Sie werden getrennt gezaehlt.
"""
from __future__ import annotations

import re

try:
    from .gemeinsam import ergebnis, json_aus_antwort
except ImportError:  # promptfoo laedt die Datei als einzelnes Skript
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gemeinsam import ergebnis, json_aus_antwort  # noqa: E402

ERLAUBT = {"ja", "nein", "unklar"}


def label_aus_antwort(antwort) -> str | None:
    obj = json_aus_antwort(antwort)
    if obj and isinstance(obj.get("moebliert_kurzzeit"), str):
        lab = obj["moebliert_kurzzeit"].strip().lower()
        return lab if lab in ERLAUBT else None
    # Ohne JSON nur eine Antwort, die aus genau einem erlaubten Wort besteht -
    # sonst wuerde "nein, ja eher doch" als nein gewertet.
    if isinstance(antwort, str):
        t = re.sub(r"<think>.*?</think>", "", antwort, flags=re.S).strip().lower().strip(".\"' ")
        return t if t in ERLAUBT else None
    return None


def pruefen(antwort, soll: str) -> dict:
    ist = label_aus_antwort(antwort)
    if soll == "unklar":
        return ergebnis(True, "Referenz unklar - nicht gewertet", 1.0) | {"gewertet": False}
    if ist is None:
        return ergebnis(False, "keine gueltige Antwort (ja/nein/unklar)") | {"gewertet": True}
    return ergebnis(ist == soll, f"soll {soll}, ist {ist}") | {"gewertet": True}


def get_assert(output, context):
    return pruefen(output, context["vars"]["erwartet"])
