# Evals

Noch nicht gefüllt. Was hier hineinkommt, und in welcher Reihenfolge:

1. `references/*.json` — Referenzantworten, **wörtlich** aus dem Quelldokument
   kopiert, mit Datei und Seitenzahl. Mindestens 8–12 Fälle.
2. `<suite>.yaml` — promptfoo-Suite, die das Modell gegen diese Referenzen
   stellt.
3. `graders/` — Bewerter für Fälle, die kein exakter Vergleich erledigt.

**Die Lehre aus dem Fehlschlag der Vorversion** (Entscheidungslog E02): in einem
früheren Projektstand waren die Referenztexte aus Suchtreffer-Ausschnitten
rekonstruiert statt aus den PDFs kopiert. Ein Eval gegen die eigene
Formulierung misst nichts. Referenzantworten entstehen deshalb ausschließlich
durch Kopieren aus dem Dokument, und die Fundstelle steht dabei.
