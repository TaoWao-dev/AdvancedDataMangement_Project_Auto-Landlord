"""Grader fuer Analyse 5, Teil 2: Pflichten der Vorlage, die kein Zahlenabgleich sieht.

Geprueft wird, dass die Gliederung da ist und dass die drei Dinge drinstehen,
die beim Weitergeben am ehesten abgeschnitten werden: die Luecken (Bezirke
ohne Daten), die Fallzahl an den Marktzahlen und der Hinweis, dass Vertraege
synthetisch und Parameter Annahmen sind. Es ist eine Stichwortpruefung - sie
belegt, dass etwas erwaehnt ist, nicht dass es gut erklaert ist. Das bleibt
Aufgabe des Menschen, der die Vorlage liest.
"""
from __future__ import annotations

import re

try:
    from .gemeinsam import ergebnis
except ImportError:  # promptfoo laedt die Datei als einzelnes Skript
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gemeinsam import ergebnis  # noqa: E402

ABSCHNITTE = ["Ausgangslage", "vorbereitet", "Daten", "Optionen", "Empfehlung", "Grenzen"]
PFLICHT = {
    "Luecke Favoriten genannt": r"1100|Favoriten|Sonnwend",
    "Luecke Donaustadt genannt": r"1220|Donaustadt|Seestadt",
    "Fallzahl genannt": r"[Ff]allzahl|\bn\s*=\s*\d",
    "Belastbarkeit genannt": r"belastbar",
    "Vertraege als synthetisch benannt": r"synthetisch|erfunden",
    "Annahmen als Annahmen benannt": r"Annahme",
    "Einkommen nicht als Preisargument": r"[Ee]inkommen[^.]{0,120}(kein|nicht)[^.]{0,40}Preis",
}


def pruefen(text: str) -> dict:
    fehlend = [a for a in ABSCHNITTE
               if not re.search(rf"(?m)^#+[^\n]*{a}", text)]
    fehlend += [name for name, muster in PFLICHT.items() if not re.search(muster, text)]
    n = len(ABSCHNITTE) + len(PFLICHT)
    return ergebnis(not fehlend, "alles vorhanden" if not fehlend else "fehlt: " + ", ".join(fehlend),
                    1 - len(fehlend) / n)


def get_assert(output, context):
    return pruefen(output)
