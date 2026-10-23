# Projektdokumentation — Übersicht

Mietportfolio Wien, Verlängerungsentscheidung. Was wann abgegeben wird, Datei
für Datei. Die Inhalte stehen in den verlinkten Dateien, nicht hier.

## Die Dateien

| Datei | Inhalt | Abgabe | Stand 23.10.2026 abends |
|---|---|---|---|
| [`00_auftrag.md`](projektdokumentation/00_auftrag.md) | Adressat, Entscheidung, drei Analysen mit Werkzeug, was nicht drin ist | 26.9., laufend | **fertig** |
| [`01_entscheidungslog.md`](projektdokumentation/01_entscheidungslog.md) | je Entscheidung Datum, Alternative, Grund, Revisionspunkt | laufend | **48 Einträge** |
| [`02_schritt1_datenzugriff.md`](projektdokumentation/02_schritt1_datenzugriff.md) | Quellentabelle, verworfene Kandidaten, Personenbezug | termin3, ergänzt | **fertig**, KV-Quelle ergänzt |
| [`03_schritt2_normalisieren.md`](projektdokumentation/03_schritt2_normalisieren.md) | Zahlen aus dem Lauf, Qualitätsbericht mit sechs Fragen je Quelle | termin3, ergänzt | **fertig** |
| [`04_schritt3_datenmodell.md`](projektdokumentation/04_schritt3_datenmodell.md) | Tabellen, Schlüssel, Beziehungen, Zuordnungslücken | termin3, ergänzt | **fertig**, Modelltabellen ergänzt |
| [`05_schritt4_abfragen_referenzen.md`](projektdokumentation/05_schritt4_abfragen_referenzen.md) | je Analyse Werkzeug, Referenz, Herkunft, Prüfregel, Toleranz | termin3, ergänzt | **fertig**, Extraktionsfälle angelegt |
| [`06_schritt5_analyse_vorlage.md`](projektdokumentation/06_schritt5_analyse_vorlage.md) | Eval-Suite, Modellwahl, Ergebnisse, Herkunft jeder Zahl, Selbsttest | termin4 | **fertig**, Prototyp (E44) |
| [`07_offene_punkte_lessons.md`](projektdokumentation/07_offene_punkte_lessons.md) | die fünf Schwächen, Datenlücken, Risiken, drei Lessons | termin4 | **fertig** |

## Deliverable 3 · Evaluierung und Vorlage (Tag `termin4`, 23.10.)

| Verlangt | Wo | Stand |
|---|---|---|
| Entscheidungsvorlage | [`docs/vorlage.md`](vorlage.md), Demo [`docs/demo/mieterverzeichnis.html`](demo/mieterverzeichnis.html) | v2 (Prototyp, E44); jede Zahl mit Herkunft, vom Grader geprüft |
| Prompts | `prompts/*_v<n>.md`, `prompts/CHANGELOG.md` | vier Aufgaben, je Version eine Zeile im Changelog |
| Eval-Suite | `evals/suite_*.yaml`, `evals/graders/` | 4 Suiten, Modell gepinnt; Grader mit Selbsttest und Gegenprobe |
| Ergebnisse | `06_schritt5_analyse_vorlage.md` | sql 9/9, Gate 4 15/15, Extraktion 5/5 (Konsistenz), vorlage 2/2; Klassifikation entfallen |
| Projektdokumentation | 06 und 07 neu, 00–05 aktualisiert | fertig |
| Betriebshandbuch | [`docs/betrieb.md`](betrieb.md) | sieben Abschnitte |
| Agent-Anweisung | [`CLAUDE.md`](../CLAUDE.md) | Was, wo, Datenmodell, Regeln, Starten |
| Abhängigkeiten | `requirements.txt`, `.env.example` | Versionen, alle Variablen der Suite |
| Selbsttest | `06_schritt5_analyse_vorlage.md` | frischer Klon nach README |

## Deliverable 2 · Datenpipeline (Tag `termin3`, 9.10.)

Pipeline, Datenmodell, Datenbank, fünf Abfragen, Referenzen, Tests und
Dokumentation 00–05. Was am 9.10. fehlte — die acht Extraktionsfälle —
ist mit E41 nachgereicht.

## Deliverable 1 · Pitch (26.9.)

Poster: [`docs/pitch/poster_mietportfolio.pdf`](pitch/poster_mietportfolio.pdf).
`[NAME]` und `[MATRIKELNUMMER]` sind noch einzusetzen.

## Abweichungen von der Vorgabe, bewusst

| Vorgabe | Was wir tun | Begründung |
|---|---|---|
| „`data/raw/` ist gitignored" | redigierte Rohdaten sind committet, Originale nicht | Personenbezug und Größe sind durch die Redaktion erledigt, und der Selbsttest verlangt einen lauffähigen Klon (E25) |
| Beispieldaten in `data/sample/` | dort liegt nur die Negativ-Fixture | `sample` heißt im Beispielprojekt „synthetisch"; echte Daten so zu benennen verschleiert die Herkunft (E25) |
| Judge-Eval für die Vorlage | deterministischer Zahlenabgleich | die Frage ist prüfbar; ein Judge-Modell trüge das Risiko, das es prüfen soll (E42) |
| Suite in promptfoo | promptfoo **und** ein Läufer ohne Node, mit denselben Gradern | npm/PyPI in der Arbeitssitzung nicht erreichbar; die Pipeline kommt ohne Installation aus (E42) |
