# Annahmenregister

Keine dieser Zahlen ist empirisch belegt. Jede hat in
`config/portfolio.json` eine Sensitivitätsspanne.

## Rechtsrahmen (kein Rechtsrat)

| Regel | Umsetzung im Modell |
|---|---|
| Gedeckelte Wertsicherung | je Jahr seit letztem Indexwert 3 % voll, darüber die Hälfte |
| Anpassungstermin | einmal jährlich, frühestens 1. April |
| Inflationsmaßstab | VPI-Jahresdurchschnitt gegen Vorjahr |
| Mindestbefristung | 5 Jahre bei Unternehmer-Vermietern, ab 1.1.2026 |
| Kündigung Vermieter | nur § 30 MRG, gilt auch in der Teilanwendung |
| Vollanwendungsdeckel | 1 % per 1.4.2026, 2 % per 1.4.2027 — im Modell abbildbar, hier nicht einschlägig |

Nach öffentlichen Zusammenfassungen des MieWeG rekonstruiert, nicht aus dem
Gesetzestext. Vor jeder echten Verwendung juristisch prüfen lassen.

## Modellparameter

| Parameter | Wert | Wirkung, wenn er falsch ist |
|---|---|---|
| Leerstand | 2,5 Monate | linear im Barwert des Auszugsfalls |
| Neuvermietungskosten | 2 Monatsmieten | dito |
| Diskontsatz | 4,5 % p. a. | verschiebt alle Barwerte gleichmäßig, Rangfolge kaum |
| Umzugskosten Mieter | 4.500 € | verschiebt die Annahmekurve; höher = trägere Mieter |
| Schmerzgrenze Belastungsquote | 33 % | ab hier bremst die Leistbarkeit |
| Wechselbereitschaft k | 0,55 | Steilheit der Annahmekurve. **Der sensibelste Parameter.** |
| Marktrisikoabschlag | 6 % | macht den Bestandsmieter gegenüber der Neuvermietung attraktiver |
| Ausfallmonate je Fall | 4 | koppelt das Mietereinkommen an den Ertrag |
| Leerstandszuschlag je paralleler Neuvermietung | 0,35 Monate | der Portfolioeffekt; ohne ihn wären die 50 Entscheidungen unabhängig |

## Strukturelle Annahmen

**A1 — Niveau aus dem Dokument, Bewegung aus dem Index.** Gilt für Mieten
(Schnappschuss + VPI) wie für Einkommen (Lohnsteuerstatistik +
Tariflohnindex). Zwischen zwei Abrufen ist das Niveau fortgeschrieben, nicht
beobachtet.

**A2 — Der Tariflohnindex misst Mindestlöhne.** Die Überzahlung über dem KV
sieht er ausdrücklich nicht. Für Gruppen mit hoher Überzahlung ist unsere
Einkommensfortschreibung eine Untergrenze, keine Schätzung. Rangfolge der
Unschärfe: Bund (sehr niedrig) < Bank, Versicherung, Handel (niedrig) <
Industrie, Spital (mittel) < IT und Unternehmensberatung (hoch).

**A3 — Die IT-Reihe ist keine reine IT-Reihe.** In der KV-Klassifikation gibt
es keinen eigenen IT-Angestellten-KV. Verwendet wird die Fachverbandsebene
„Unternehmensberatung, Buchhaltung und Informationstechnologie", die drei
Branchen mischt.

**A4 — Angebotsmieten sind keine Abschlussmieten.** Der Schnappschuss zeigt,
was verlangt wird, nicht was gezahlt wird. Der Marktrisikoabschlag von 6 % ist
der Versuch, das abzubilden — belegt ist er nicht.

**A5 — Gewerbliche Anbieter verzerren den Median.** Im Segment 80–100 m² sind
80 % der Inserate gewerblich; ein einzelner Anbieter möblierter
Kurzzeitwohnungen stellt 17 der 90 Inserate. Der gewerbliche Median liegt 16 %
über dem privaten. `v_marktniveau` weist die Fallzahl je Zeile aus,
`v_anbieterstruktur` den gewerblichen Anteil.

**A6 — Eine Teilseite ist kein Markt.** Der Schnappschuss enthält 90 von 154
Treffern. Der Median beschreibt die erste Seite. Das Gate stuft das als
Warnung ein, nicht als Fehler — behoben wird es durch weitere Seiten.

**A7 — Marktmiete je Cluster, nicht je Wohnung.** Stockwerk, Freifläche und
Ausrichtung sind im Datenmodell erfasst, gehen aber nicht in die Marktmiete
ein. Für eine echte Bewertung müsste ein hedonischer Aufschlag dazu.

**A8 — Perfekte Voraussicht beim Angebot.** Das Modell unterstellt, dass die
heutige Marktmiete auch in fünf Jahren die richtige Referenz ist, lediglich
indexiert. Ein Marktabschwung ist nicht modelliert.

**A9 — Ein Angebot, keine Verhandlung.** In der Praxis wird nachverhandelt.
Das Modell kennt nur Annahme oder Auszug.

**A10 — Die Vertragshistorie ist erfunden.** Abschlussjahre 2019–2022,
Startmieten aus einem angenommenen Marktniveau je Jahr, 85 % mit
Wertsicherungsklausel. Diese Verteilung erzeugt den größten Teil der
Spreizung im Ergebnis — sie ist also nicht harmlos.
