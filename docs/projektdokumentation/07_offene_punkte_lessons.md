# Offene Punkte, Risiken, Lessons

Stand 23.10.2026. Was das Projekt nicht kann, steht hier vollständig —
nicht verteilt auf Fußnoten.

## Datenlücken

| Lücke | Wirkung | Wie sie sichtbar ist | Was sie schließt |
|---|---|---|---|
| **Vier von fünf Bezirken nicht beschafft** (1100, 1220, 1010, 1030) | 30 der 50 Verträge ohne Empfehlung; kein Bezirksvergleich | `kennzahl_abdeckung` „fehlt", `modelllauf.eignung` „kein Schnappschuss" | je ein vollständiger Abruf über `view-source:` (docs/betrieb.md) |
| **Zwei Abrufe, 14 Tage** | Inseratsdauer nicht messbar, Leerstand bleibt Annahme | `kennzahl_inseratsdauer.befund` | dritter Abruf 1020 vor der ersten Tranche |
| **Indexreihen (VPI, Tariflohnindex) nicht geladen** | Bestandsmieten pauschal mit 4 % p. a. fortgeschrieben, Einkommen gar nicht | `indexreihe` hat 0 Zeilen; A10, A12 | Statistik Austria OGD, automatisch abrufbar (CC-BY) |
| **KV-Extraktion nicht gelaufen** | die Einkommensfortschreibung, für die sie gebaut ist, fehlt | Suite: „nicht gelaufen" | lokaler Lauf mit Qwen3 8B, danach `config/berufsgruppen.json` |
| **Möbliert-Klassifikation ohne Referenz** | Marktmiete enthält möblierte Kurzzeitangebote, eher zu hoch | `suite_moebliert` ohne Fälle | Markierliste v3 vom Studierenden |
| **KV-Referenzen unbestätigt** | 8 Extraktionsfälle sind eine Lesung durch Claude | `von_hand_bestaetigt: false` | Bestätigung in `evals/erfasse_kv_referenz.py` |
| **Kein Satz 2026 für Versicherungen, Wirtschaftstreuhänder, Landesspitäler** | drei Reihen ohne Fortschreibung | Referenz erwartet „nicht gefunden" | WKO-PDFs der Gehaltsordnungen speichern |
| **Spitalreihe ersetzt** | Referenz nutzt Privatkrankenanstalten statt „Bundesländer – Krankenanstalten" | E41, Unsicherheit im Fall | klären, wo die Spitalsmieter tatsächlich beschäftigt sind |

## Risiken

1. **Die Empfehlung ist eine Wette auf eine Zahl.** Die Sensitivität zeigt:
   Am unteren Quartil der Marktmiete schrumpft der mittlere Aufschlag fast
   auf null, am oberen verdoppelt er sich mehr als (`kennzahl_sensitivitaet`).
   Die Marktmiete beruht auf 32 Angebotsinseraten eines Tages.
2. **Angebot ist nicht Abschluss.** Inserate zeigen, was verlangt wird. Der
   Abschlag von 6 % dafür ist nicht belegt.
3. **Synthetische Verträge.** Die Spreizung der Ergebnisse kommt zum
   größten Teil aus dem erfundenen Bestand (A10). Mit echten Verträgen kann
   die Empfehlung je Vertrag ganz anders aussehen; die Richtung
   („verlängern nahe am Markt statt auslaufen") ist robuster als die Höhe.
4. **Erwartet wird, dass etwa jeder zweite Mieter auszieht.** Das Modell
   hält das für wirtschaftlich; es kennt aber weder Reputationsfolgen noch
   die Kapazität der Vermarktung. Ein Fehler in der Wechselbereitschaft
   (dem empfindlichsten Verhaltensparameter) ändert alle 20 Angebote.
5. **Die Zahlenprüfung der Vorlage ist für kleine Zahlen schwach.** Ohne
   Zitat im Absatz passt eine kleine Zahl fast immer irgendwo (E43).
   Richtungsfehler in Worten („unter" statt „über") sieht kein Grader.
6. **Rechtsrahmen nach Zusammenfassungen.** Die gedeckelte Wertsicherung ist
   nicht aus dem Gesetzestext modelliert. Kein Rechtsrat.
7. **Die Historie zwischen 10.10. und 23.10. ist leer.** E30 hatte als
   Revisionspunkt: „Liegen zwischen 9.10. und 23.10. nur Commits am
   Abgabetag, ist die Entscheidung gescheitert." Zwischen dem 10.10. und dem
   23.10. gibt es keinen Commit. Die Commits des 23.10. sind einzelne
   Arbeitseinheiten mit Begründung — aber der Revisionspunkt ist
   eingetreten, und das steht hier.

## Drei Lessons

### 1. Ein Gate, das besteht, sagt nichts über den Sinn

Zweimal in diesem Projekt lief alles grün, und das Ergebnis war Unsinn: der
Median über Gebrauchtwaren, der ohne Gate 1 entstanden wäre (E09), und der
Vertragsbestand, dessen Haushalte mehr Miete zahlten als sie verdienten
(E40). Gates prüfen Form und Wertebereich; ob ein Haushalt mit 122 %
Belastung existieren kann, prüft keines. Gefunden hat beide Fehler ein
Blick auf eine einzelne Spalte, nicht ein Test. Seither wird jede neue
Kennzahl einmal von Hand gelesen, bevor sie weiterverwendet wird — und was
dabei auffällt, wird zum Test (`test_vertragsbestand_ist_bei_abschluss_leistbar`).

### 2. Der Maßstab darf nicht vom Gemessenen stammen — und das gilt auch für den Prüfer

Dreimal stand dieselbe Versuchung im Raum: ein Goldset aus
Suchtreffer-Snippets (E02), Extraktionsreferenzen aus einer
Modellzusammenfassung (E28), eine Markierliste, die ein Modell ausgefüllt
hatte (E37). Jedes Mal wäre die Trefferquote gut gewesen und hätte nichts
bedeutet. Die Antwort war jedes Mal dieselbe: Ein Mensch beschafft oder
markiert, Code kopiert wörtlich, und was eine Lesung braucht, bleibt
unbestätigt, bis ein Mensch es bestätigt. Am 23.10. kam die Kehrseite
dazu: auch der Grader braucht einen Prüfer. Die Gegenprobe mit eingebauten
Fehlern zeigte, dass 2 von 6 durchgingen, und die eigene Vorlage zeigte,
dass eine verrechnete Zahl als „belegt" galt. Ein Eval ist erst so gut wie
der Nachweis, dass es rot werden kann.

### 3. Die teure Unsicherheit ist selten die, an der man modelliert

Viel Arbeit floss in das Entscheidungsmodell: Annahmekurve, Ausfallrisiko,
Portfolio-Fixpunkt mit Dämpfung. Die Sensitivität zeigt, dass diese Teile
die Empfehlung kaum bewegen — die Leerstandsannahme ändert 4 von 20
Angeboten. Die Marktmiete, eine einzige gemessene Zahl, ändert alle 20 und
den mittleren Aufschlag zwischen fast null und mehr als dem Doppelten. Für
die Leitung heißt das: die nächste Investition gehört in Messung (Bezirke,
Abrufe, möblierte Angebote herausrechnen), nicht in ein feineres Modell. Für
das Projekt heißt es: die Sensitivität hätte früher laufen sollen — sie
hätte gezeigt, wohin die Zeit gehört.
