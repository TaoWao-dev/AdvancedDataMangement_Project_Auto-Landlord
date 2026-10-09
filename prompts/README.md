# Prompts

Noch nicht gefüllt. Regeln, die hier gelten:

- Eine Datei je Aufgabe, versioniert im Namen: `<name>_v1.md`, `<name>_v2.md`.
  Alte Fassungen bleiben — sonst ist nicht nachvollziehbar, gegen welchen
  Prompt ein Eval-Ergebnis entstanden ist.
- `CHANGELOG.md` sagt zu jeder neuen Version, **warum** sie entstand und was
  sich am Eval-Ergebnis geändert hat.
- Kein Prompt enthält eine Zusicherung, die auch Code leisten kann. Der
  PII-Filter steht in `src/clean.py`, nicht in einer Anweisung an das Modell
  (Entscheidungslog E11).
- Zahlen kommen aus SQL. Ein Prompt, der das Modell rechnen lässt, ist falsch
  gebaut.
