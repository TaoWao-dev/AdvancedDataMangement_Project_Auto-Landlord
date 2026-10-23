"""Grader fuer die Analysen 1-3: Kennzahl-Abfrage gegen Referenzantwort.

Die Ausgabe des Providers (evals/providers/sql_kennzahl.py) ist die Zeile
der Abfrage als JSON. Verglichen wird Feld fuer Feld mit der Toleranz aus
der Referenz: 0,01 EUR/m2 bei Median und Quartilen, 0 bei Fallzahlen,
exakt bei Text. Dieselbe Pruefung wie test_kennzahlen_stimmen_mit_den_
referenzantworten, hier als Teil der Suite und mit Trefferquote.
"""
from __future__ import annotations

try:
    from .gemeinsam import ergebnis, json_aus_antwort
except ImportError:  # promptfoo laedt die Datei als einzelnes Skript
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gemeinsam import ergebnis, json_aus_antwort  # noqa: E402


def pruefen(antwort, erwartet: dict, toleranz: float = 0.01) -> dict:
    obj = json_aus_antwort(antwort)
    if obj is None:
        return ergebnis(False, "keine Zeile geliefert", 0.0)
    falsch = []
    for feld, soll in erwartet.items():
        ist = obj.get(feld)
        if isinstance(soll, (int, float)) and not isinstance(soll, bool):
            ok = ist is not None and abs(float(ist) - float(soll)) <= (
                0 if isinstance(soll, int) else toleranz) + 1e-9
        else:
            ok = str(ist) == str(soll)
        if not ok:
            falsch.append(f"{feld}: soll {soll!r}, ist {ist!r}")
    score = 1 - len(falsch) / max(1, len(erwartet))
    return ergebnis(not falsch, "; ".join(falsch) or f"{len(erwartet)} Felder stimmen", score)


def get_assert(output, context):
    v = context["vars"]
    return pruefen(output, v["erwartet"], v.get("toleranz", 0.01))
