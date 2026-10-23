"""Grader fuer Analyse 4: Felder aus KV-Texten.

Massstab: evals/references/kv_extraktion.json, Feld erwartete_antwort.
Ein Fall ist bestanden, wenn JEDES bewertete Feld stimmt. Die Teilpunkte
(score) zeigen, wie nah das Modell war - entscheiden tut der Fall.

Feldregeln, und warum:
  Prozentsaetze  exakt auf 0,001. 2,55 statt 2,5 ist ein anderer Abschluss.
  Datum          exakt, ISO. Ein Datum, das die Quelle nicht nennt, muss null
                 sein - ein plausibles erfundenes Datum ist falsch, nicht fast
                 richtig (Fall oeffentlicher Dienst).
  null           stimmt nur mit null. "Nicht in der Quelle" ist eine Antwort.
  Fundstelle     die Zeile im Originalquelltext. Sie unterscheidet den
                 richtigen Abschnitt vom Ablenker mit demselben Prozentsatz.
"""
from __future__ import annotations

try:
    from .gemeinsam import ergebnis, json_aus_antwort
except ImportError:  # promptfoo laedt die Datei als einzelnes Skript
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gemeinsam import ergebnis, json_aus_antwort  # noqa: E402

FELDER = ["abschluss_gefunden", "prozent_min", "prozent_max", "fixbetrag_eur",
          "ist_prozent", "geltungsbeginn", "bezugsgroesse", "deckelung",
          "fundstelle_zeile"]
ZAHLEN = {"prozent_min", "prozent_max", "fixbetrag_eur", "ist_prozent"}


def _gleich(feld: str, soll, ist) -> bool:
    if soll is None or ist is None:
        return soll is None and ist is None
    if feld in ZAHLEN:
        try:
            return abs(float(ist) - float(soll)) <= 0.001
        except (TypeError, ValueError):
            return False
    if feld == "fundstelle_zeile":
        try:
            return int(ist) == int(soll)
        except (TypeError, ValueError):
            return False
    if isinstance(soll, bool):
        return ist is soll
    return str(ist).strip().lower() == str(soll).strip().lower()


def pruefen(antwort, erwartet: dict, nicht_bewertet: list[str] | None = None) -> dict:
    obj = json_aus_antwort(antwort)
    if obj is None:
        return ergebnis(False, "keine JSON-Antwort", 0.0)
    nicht_bewertet = set(nicht_bewertet or [])
    bewertet = [f for f in FELDER if f not in nicht_bewertet]
    falsch = [f"{f}: soll {erwartet.get(f)!r}, ist {obj.get(f)!r}"
              for f in bewertet if not _gleich(f, erwartet.get(f), obj.get(f))]
    score = 1 - len(falsch) / len(bewertet)
    if not falsch:
        return ergebnis(True, f"alle {len(bewertet)} Felder stimmen", 1.0)
    return ergebnis(False, "; ".join(falsch), score)


def get_assert(output, context):
    v = context["vars"]
    return pruefen(output, v["erwartet"], v.get("nicht_bewertet"))
