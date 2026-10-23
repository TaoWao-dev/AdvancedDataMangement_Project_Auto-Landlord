"""Gegenprobe: fangen die Grader-Tests absichtlich eingebaute Fehler?

    python3 evals/gegenprobe_grader.py

tests/test_graders.py zeigt, dass die Grader richtige Antworten durchlassen
und typische falsche abweisen. Ob diese Tests selbst scharf genug sind, zeigt
erst ein Grader, der kaputt ist: jede Mutation unten baut einen plausiblen
Fehler in einen Grader ein; mindestens ein Test muss dann rot werden.

Lauf vom 23.10.2026: in der ersten Fassung ueberlebten 2 von 6 Mutationen
(Teilwort-Treffer in der Klassifikation, Toleranz auf der Fallzahl). Die
Tests wurden nachgeschaerft; seither werden alle 6 gefangen. Der Quelltext
wird nach jeder Mutation wiederhergestellt, auch bei Abbruch.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent

MUTATIONEN = [
    ("evals/graders/zahlen_herkunft.py", "    return None\n\n\ndef pruefen",
     "    return 'immer'\n\n\ndef pruefen", "jede Zahl gilt als belegt"),
    ("evals/graders/zahlen_herkunft.py", "if abs(c - v) <= p / 2 + 1e-9:",
     "if abs(c - v) <= 1:", "Rundung auf +-1 statt auf die Stellenzahl"),
    ("evals/graders/extraktion.py", "        return soll is None and ist is None",
     "        return True", "null stimmt mit jedem Wert"),
    ("evals/graders/extraktion.py", '          "fundstelle_zeile"]', "          ]",
     "Fundstelle wird nicht geprueft"),
    ("evals/graders/klassifikation.py", "return t if t in ERLAUBT else None",
     "return next((w for w in sorted(ERLAUBT) if w in t), None)", "Teilwort zaehlt als Antwort"),
    ("evals/graders/sql_referenz.py", "0 if isinstance(soll, int) else toleranz",
     "toleranz", "Fallzahl mit Euro-Toleranz"),
]


def main() -> int:
    ueberlebt = 0
    for datei, alt, neu, name in MUTATIONEN:
        p = WURZEL / datei
        orig = p.read_text(encoding="utf-8")
        if alt not in orig:
            print(f"VERALTET  {name}: Stelle nicht gefunden - Mutation anpassen")
            ueberlebt += 1
            continue
        p.write_text(orig.replace(alt, neu, 1), encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(WURZEL / "tests" / "test_graders.py")],
                               capture_output=True, text=True, cwd=WURZEL)
        finally:
            p.write_text(orig, encoding="utf-8")
        rot = [z.split()[1].rstrip(":") for z in r.stdout.splitlines() if z.strip().startswith("ROT")]
        print(f"{'gefangen ' if rot else 'UEBERLEBT'} {name:<42} {', '.join(rot[:2])}")
        ueberlebt += 0 if rot else 1
    print(f"\n{len(MUTATIONEN) - ueberlebt} von {len(MUTATIONEN)} Mutationen gefangen")
    return 1 if ueberlebt else 0


if __name__ == "__main__":
    sys.exit(main())
