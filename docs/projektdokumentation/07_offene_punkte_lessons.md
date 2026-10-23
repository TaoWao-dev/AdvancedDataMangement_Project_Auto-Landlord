# Offene Punkte, Schwächen, Lessons

Stand 23.10.2026, nach der Konkretisierung zum Prototyp (E44). Was das Projekt
nicht kann, steht hier vollständig — nicht verteilt auf Fußnoten.

## Die fünf Schwächen des Projekts

Formuliert vom Studierenden für die Endpräsentation; je Punkt, woran er im
Repository nachweisbar ist.

### 1. Die Daten, die man will, lassen sich nur mit menschlichem Input beschaffen — und das Labelling ist mühsam

Die Inseratsplattform untersagt automatisierten Zugriff (`robots.txt`,
archiviert); jeder der drei Abrufe ist von Hand über `view-source:`
gespeichert. Zweimal entstand dabei die falsche Seite (E09, Vorfall 2 in
`02_schritt1_datenzugriff.md`), und erst Gate 1 hat es gemerkt. Das
Labelling für die Evals scheiterte zweimal: Gemeindewohnungen ließen sich
am Titel nicht erkennen (E38), und die erste Markierliste stammte von einem
Modell statt vom Menschen (E37). Am Ende wurde die Bereinigung vereinfacht
(E46): Weil sich aus den Daten nicht zu 100 % feststellen lässt, worum es
sich bei einer Anzeige handelt, und die Sortierung durch das LLM nicht
wesentlich schlechter ist als die eines Menschen, gelten die Regeln des
Modells (Objekttyp, ausdrückliche Nennung im Titel) ohne weiteren
Labelling-Aufwand.

### 2. Auch die KV-Seiten müssen von Hand gespeichert werden — die Pipeline braucht immer einen Menschen als Auslöser

Die ÖGB- und WKO-Seiten sind aus der Arbeitsumgebung nicht abrufbar
(Proxy 403); eine Zusammenfassung über eine Modellsuche wäre als Referenz
wertlos (E28). Sie wurden am 23.10. von Hand gespeichert (E41). Damit hat die
Pipeline zwei manuelle Eingänge, und jeder neue Datenstand — die 14-tägige
Marktwertkontrolle, jede neue KV-Runde — beginnt mit einem Menschen im
Browser. Automatisiert ist alles **nach** dem Speichern; das Speichern selbst
lässt sich nicht automatisieren, ohne die Nutzungsbedingungen zu brechen.

### 3. Die Evals prüfen Rechnungen, nicht ob das Ergebnis stimmt

Was die Suite prüfen kann: dass SQL und eine zweite Rechnung dieselben
Zahlen liefern (9/9), dass jede Zahl der Vorlage aus einer Kennzahl stammt
(Grader `zahlen_herkunft`), dass eine extrahierte Zahl wörtlich in der
Quelle steht (Gate 4). Was sie nicht prüfen kann: ob die Empfehlung richtig
ist. Dafür gibt es keine Geschäftslogik, gegen die man prüfen könnte — keine
echten Verträge, keine Abschlussmieten, keine beobachtete Reaktion von
Mietern auf eine Erhöhung. Die Extraktion besteht 5/5, aber Referenz und
Extraktion stammen vom selben Modell (E45): das belegt Konsistenz, nicht
Richtigkeit.

Am schwächsten ist das Filtern der Inserate. Gemeindewohnungen und
WG-Zimmer verzerren den Markt nach unten, möblierte Kurzzeitangebote nach
oben; erkennbar sind nur die ausdrücklich benannten (E33, E38). Weder ein
Mensch noch ein Modell kann am Inserat zuverlässig sagen, was der Rest ist —
also gibt es für dieses Eval keinen Maßstab.

### 4. Es waren deutlich weniger Werkzeuge nötig als vorgeschlagen

Gebraucht wurden: Python mit Standardbibliothek, SQLite, Git/GitHub und ein
Sprachmodell in der Arbeitssitzung. Nicht gebraucht: LM Studio (E45 — kein
unmittelbarer Nutzen, mehr Komplexität), Jupyter, Power BI, NotebookLM.
promptfoo ist konfiguriert (`evals/suite_*.yaml`), lief in der Sitzung aber
nicht, weil keine Paketquelle erreichbar war; derselbe Ablauf läuft ohne
Installation über `evals/lauf.py` (E42). Die Pipeline hat keine einzige
Abhängigkeit außerhalb von Python.

### 5. Mieter automatisiert auszupressen ist zum Glück nicht so einfach

Die Informationslage, die dafür nötig wäre, lässt sich mit einem Chatbot und
einer Pipeline nicht herstellen: der Markt ist nur in Stichproben
beobachtbar, Einkommen nur über Branchen-Mindestlöhne, das Verhalten der
Mieter gar nicht. Die Empfehlung hängt fast vollständig an einer
ungemessenen Annahme — wie bereitwillig Mieter wechseln (43 von 50
Empfehlungen ändern sich am Rand ihrer Spanne, `kennzahl_sensitivitaet`).

Und wo das Modell doch wirkt, wirkt es so, wie man es befürchten würde: Ein
Erwartungswert-Optimierer verlangt dort mehr, wo es leichter durchgeht. Bei
gleicher Wohnung bekommt der Haushalt mit höherem Einkommen eine Rasterstufe
mehr empfohlen (E47) — obwohl das Projekt sich vorgenommen hatte, das
Einkommen nicht als Preisargument zu verwenden (E05).

## Datenlücken

| Lücke | Wirkung | Wie sie sichtbar ist |
|---|---|---|
| Marktreihe seit 25.09.2026, drei Abrufe, der erste eine Teilseite | Marktveränderung „seit letzter Erhöhung" ist für alle 50 Verträge nur seit dem ersten Abruf messbar | `empfehlung.bezug_vor_beobachtung`, `kennzahl_marktentwicklung` |
| ein Bezirk (1020) | kein Vergleich zwischen Lagen | `kennzahl_abdeckung` |
| KV-Lohn ist Mindestlohn, nicht Ist-Gehalt | Einkommensentwicklung eher unterschätzt (IT: hohe Überzahlung) | A2, `kennzahl_kv_entwicklung` |
| Tag des Abschlusses fehlt bei 4 von 15 KV-Datensätzen | gerechnet ab 1. Jänner | `kv_erhoehung.datum_angenommen` |
| Einkommensniveaus sind Platzhalter | fast alle Haushalte brauchen ein Zweiteinkommen | E40, A11 |
| kein Satz 2026 für Versicherungen; öffentlicher Dienst ohne 2024; Wirtschaftstreuhänder entfernt, ersetzt durch Handelsarbeiter | Branchen nicht im Demo-Portfolio | E46, E48 |
| Indexreihen (VPI) nicht geladen | Wertsicherung pauschal angenommen | A10 |

## Risiken

1. **Die Empfehlung ist vor allem eine Aussage über eine Annahme.** Die
   Wechselbereitschaft ist ungemessen und bewegt fast alle Empfehlungen.
2. **Ein Verhaltensmodell für Verlängerungen auf laufende Verträge
   angewendet.** Es erwartet auch ohne Erhöhung viele Auszüge; die
   Euro-Beträge sind deshalb unsicherer als die Rangfolge.
3. **Rechtlich ist eine Erhöhung im laufenden Vertrag nur über die
   Wertsicherung möglich.** Die Empfehlung sagt, was der Markt trägt, nicht
   was sofort durchsetzbar ist. Kein Rechtsrat.
4. **Die Zahlenprüfung der Vorlage ist für kleine Zahlen ohne Zitat
   schwach** (E43), und Richtungsfehler in Worten sieht kein Grader.
5. **Die Historie zwischen 10.10. und 23.10. ist leer.** Der Revisionspunkt
   von E30 ist eingetreten.

## Drei Lessons

### 1. Ein grünes Gate sagt nichts über den Sinn — und ein Test, der nicht läuft, ist kein Test

Mehrmals lief alles grün, und das Ergebnis war falsch oder ungeprüft: der
Median über Gebrauchtwaren ohne Gate 1 (E09), Haushalte, die mehr Miete
zahlten als sie verdienten (E40), sechs Tests, die hinter dem Läuferblock
standen und nie ausgeführt wurden, und ein Test, der mit seiner Toleranz
genau den Befund verdeckte, den er melden sollte (E47). Gefunden hat das
jeweils ein Blick auf eine einzelne Zahl, nicht ein weiterer Test.

### 2. Der Maßstab darf nicht vom Gemessenen stammen — das gilt für Referenzen und für Prüfer

Goldset aus Snippets (E02), Referenzen aus einer Modellzusammenfassung
(E28), eine vom Modell ausgefüllte Markierliste (E37), Referenz und
Extraktion vom selben Modell (E45): Jedes Mal hätte die Trefferquote gut
ausgesehen und wenig bedeutet. Auch die Prüfer brauchen einen Prüfer: Die
Gegenprobe mit eingebauten Fehlern fand zwei zu schwache Grader-Tests, die
eigene Vorlage eine verrechnete Zahl, die als belegt galt, und Gate 4 hielt
„2,5" für einen Teil von „2,55".

### 3. Die teure Unsicherheit ist selten die, an der man modelliert

Viel Arbeit floss in das Entscheidungsmodell — Annahmekurve, Ausfallrisiko,
Fixpunkt mit Dämpfung. Die Sensitivität zeigt, dass die Empfehlung an einer
ungemessenen Verhaltensannahme und an der Marktmiete hängt, nicht an diesen
Teilen; die Dämpfung erwies sich im Demo-Portfolio sogar als unnötig (E46).
Die nächste Investition gehört in Messung, nicht in ein feineres Modell —
und die Sensitivität hätte früher laufen sollen.
