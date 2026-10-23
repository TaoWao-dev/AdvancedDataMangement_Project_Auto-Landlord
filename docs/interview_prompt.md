# Interview-Prompt: Vorbereitung auf die Live-Fragen

Dieser Prompt macht ein Sprachmodell zum Prüfer der LVA. Er stellt die
Fragen, die in der Präsentation am 24.10. kommen können, einzeln, hakt nach
und sagt nach jeder Antwort, was gefehlt hat und wo im Repository der Beleg
liegt.

**Verwendung**
1. Einen neuen Chat öffnen. Ein kostenloses Modell reicht.
2. Diese Dateien anhängen:
   - `README.md` und `CLAUDE.md`
   - `docs/vorlage.md`
   - `docs/projektdokumentation/01_entscheidungslog.md`
   - `docs/projektdokumentation/06_schritt5_analyse_vorlage.md`
   - `docs/projektdokumentation/07_offene_punkte_lessons.md`
   - `docs/vortrag/auto-landlord.pdf`
3. Den Block unten als erste Nachricht einfügen.
4. Antworten wie im Vortrag geben: mündlich formuliert, kurz und mit Beleg.

Teil 2 ist der Erwartungshorizont, aus dem der Prüfer bewertet. Man kann ihn
auch ohne Modell als Spickzettel durchgehen. Jede Zahl darin steht in einer
der angehängten Dateien.

---

## Teil 1 · Der Prompt

```text
Du bist Prüfer in der Lehrveranstaltung "Advanced Data Management". Bewertet
wird NICHT das Modellergebnis, sondern der Arbeitsprozess und das Urteil der
Studierenden darüber, ob ein Modellergebnis Sinn ergibt.

Projekt: "Auto-Landlord" - ein Prototyp, der für 50 laufende Mietverträge in
der Leopoldstadt (Wien 1020) empfiehlt, ob und um wie viel die Miete erhöht
werden soll. Grundlage sind Angebotsmieten (willhaben, von Hand gespeichert)
und KV-Lohnerhöhungen der Branche des Mieters (ÖGB/WKO, von einem
Sprachmodell extrahiert). Die Mieter sind synthetisch. Die angehängten
Dateien sind die einzige Quelle über das Projekt.

So läuft das Interview:
1. Stelle genau EINE Frage und warte auf die Antwort.
2. Hake einmal nach, wenn die Antwort vage ist, keinen Beleg nennt oder
   etwas behauptet, das nicht in den Dateien steht. Frage dann nach
   Datei, Entscheidung (E-Nummer) oder Zahl.
3. Gib danach in höchstens drei Sätzen Feedback:
   - was gestimmt hat,
   - was gefehlt hat,
   - wo der Beleg im Repository liegt.
   Erfinde keine Zahlen. Wenn die Dateien etwas nicht hergeben, sag das.
4. Insgesamt 12 Fragen, mindestens je eine aus jedem Bereich:
   A Problem und Adressat · B Datenzugriff und Personendaten ·
   C Qualität, Gates, Datenmodell · D LLM-Einsatz · E Evals ·
   F Entscheidungsvorlage · G Grenzen, Recht, Ethik · H Arbeitsweise.
   Mindestens drei Fragen sollen unangenehm sein: Widersprüche,
   Schwächen, "Warum nicht einfach ...?".
5. Am Ende: je Bereich eine Note von 1 bis 5 mit einem Satz Begründung,
   dazu die drei Antworten, die vor der Prüfung noch geübt werden sollten.

Stil: sachlich, auf Deutsch, wie ein kritischer, fairer Prüfer. Kein Lob
ohne Grund. Beginne mit Frage 1.
```

---

## Teil 2 · Erwartungshorizont

### A · Problem und Adressat

| Frage | Kern einer guten Antwort | Beleg |
|---|---|---|
| Welches Problem löst das Projekt, in einem Satz? | Für jeden laufenden Mietvertrag: die Miete erhöhen oder nicht, und um wie viel. Adressatin ist die Leitung Asset Management Wohnen. | `docs/vorlage.md` Kopf, E04 |
| Was ist die Prämisse? | Kurz nach der KV-Lohnerhöhung anbieten, und zwar die Stufe mit dem höchsten Erwartungswert: Miete × Wahrscheinlichkeit, dass der Mieter bleibt. Sie ist bewusst zugespitzt. | Folien 2–3, `src/entscheidung.py` |
| Warum habt ihr das Thema zweimal gewechselt? | Leitha, dann Greifenstein, dann Mietportfolio. Jedes Mal fehlte der Datenzugriff oder ein echter Entscheider. | E01–E03 |
| Warum nur der 2. Bezirk, zwei Größenklassen und fünf Branchen? | Das ist eine **Konkretisierung zum lauffähigen Prototyp**, kein Wechsel des Umfangs. Gewählt wurde nur, was in jedem Abruf belastbar ist und eine lückenlose KV-Reihe 2024–2026 hat. Ein weiterer Bezirk ist eine Datei mehr. | E44, E46, `CLAUDE.md` |

### B · Datenzugriff und Personendaten

| Frage | Kern | Beleg |
|---|---|---|
| Warum kein Scraper? | Die `robots.txt` des Portals untersagt automatisierten Abruf (archiviert). Die KV-Seiten blockiert der Proxy. Ein Mensch speichert die Seiten über `view-source:`, alles danach ist Code. | E06, E35, `docs/willhaben_robots_2026-09-25.txt` |
| Wie stellt ihr sicher, dass keine Personendaten im Projekt sind? | Eine Allowlist im Code, nicht im Prompt (`config.PII_ERLAUBT`, angewendet in `clean.py`). Gate 2 bricht ab. Rohdateien werden vor dem Commit redigiert, die Originale bleiben lokal. Die Mieter sind erfunden. | E11, E19, E21, Regel 1 |
| Woher weiß man, dass eine Rohdatei nicht verändert wurde? | Über die SHA-256 je Datei in `HERKUNFT.md`. Die Datenbank wird bei jedem Lauf aus `data/raw/` neu gebaut. | E15, E25 |

### C · Qualität, Gates, Datenmodell

| Frage | Kern | Beleg |
|---|---|---|
| Was prüfen die vier Gates? | **1** Eingangsprüfung je Schnappschuss (PLZ, Vertikale, Vollständigkeit). **2** Personendaten, sonst Abbruch. **4** jede extrahierte KV-Zahl wörtlich in ihrer Quellzeile, bevor sie in die DB geht. **3** Kennzahlen und Modell plausibel (Fixpunkt konvergiert, Median zwischen Min und Max, keine Waisen). | `src/run.py`, `src/kv_extrakt.py` |
| Sind die Evals auch ein Gate? | Nein. Gates laufen immer in `src.run`, die Evals laufen getrennt mit `evals/lauf.py`. | Folie 4 |
| Warum SQLite und warum jedes Mal neu bauen? | Kein Server, keine Installation. Zwei Läufe liefern dieselben Bytes, das ist ein Test und keine Hoffnung. | E12, E15, E26 |
| Wie übersteht die Pipeline Datenänderungen? | Drei Abrufe, und mit jedem lief alles durch. Der erste (Teilseite) wird als Warnung gemeldet, nicht verschwiegen. Die SQL-Suite bleibt nach dem Wachstum von 90 auf 442 Beobachtungen bei 9/9. | 06, Qualitätsbericht |
| Warum der Median und nicht der Mittelwert? | Ausreißer wie möblierte Kurzzeitangebote kippen den Mittelwert. Jede Zeile führt ihre Fallzahl mit. | E16, Regel 3 |

### D · LLM-Einsatz

| Frage | Kern | Beleg |
|---|---|---|
| Was macht das Sprachmodell, was nicht? | Es extrahiert die KV-Sätze aus Fließtext und formuliert die Vorlage. Es rechnet nicht, filtert nichts, was ein Gate prüfen muss, und erzeugt keine Zahl. | E27, Regel 2 |
| Wie verhindert ihr erfundene KV-Zahlen? | Gate 4: Jede Zahl muss mit Zahlgrenzen wörtlich in ihrer Quellzeile stehen. Früher hätte „2,5“ in „2,55“ gepasst, das ist behoben. Eine Grenze bleibt: Den Arbeiter-KV mit demselben Satz erkennt nur das Eval. | E45, 06 |
| Warum kein lokales Modell (LM Studio)? | Es brachte keinen unmittelbaren Nutzen, nur mehr Komplexität. Die Extraktion lief mit dem Modell der Arbeitssitzung, die Ausgabe ist gespeichert und geprüft. | E45, Schwäche 4 |
| Was wurde aus der Klassifikation der Inserate? | Sie wurde **vereinfacht, nicht verworfen**. Was eine Anzeige ist, lässt sich aus den Daten nicht zu 100 % feststellen. Das LLM sortiert nicht wesentlich schlechter als ein Mensch, also gelten seine Regeln: Objekttyp und ausdrückliche Nennung im Titel. Möblierte Kurzzeitangebote bleiben im Markt. | E33, E38, E46 |

### E · Evals

| Frage | Kern | Beleg |
|---|---|---|
| Welche Ergebnisse habt ihr? | `sql` 9/9, Gate 4 15/15, KV-Extraktion 5/5 gewertete (8 Fälle, alle vom Menschen bestätigt), Vorlage 2/2 mit 122 Zahlen mit Herkunft, Gegenprobe 7/7. Kosten 0 €, keine Modellanfrage im Lauf. | 06 Ergebnisse |
| Was ist an 5/5 problematisch? | Referenz und Extraktion stammen vom selben Modell. Erst die Bestätigung durch den Menschen macht es mehr als Konsistenz. | E45, E48 |
| Warum kein LLM-Judge für die Vorlage? | Die Frage „Stammt jede Zahl aus einer Kennzahl?“ ist deterministisch prüfbar. Ein Judge hätte genau das Risiko, das er prüfen soll. Das Zitat bindet die Zahl an ihre Quelle. | E42, E43 |
| Wer prüft die Grader? | Die Gegenprobe baut absichtlich Fehler ein. Zuerst überlebten 2 von 6, eine verrechnete Zahl galt als belegt. Heute erkennt sie alle 7. | `evals/gegenprobe_grader.py`, Lesson 2 |
| Was prüfen die Evals nicht? | Ob die Empfehlung richtig ist. Es gibt keine echten Verträge und keine beobachtete Reaktion auf eine Erhöhung. Am schwächsten ist das Filtern der Inserate, dafür gibt es keinen Maßstab. | Schwäche 3 |
| Warum lief promptfoo nicht? | Die Paketquellen waren nicht erreichbar. Derselbe Ablauf läuft mit den gleichen Gradern über `evals/lauf.py`. | E42 |

### F · Entscheidungsvorlage

| Frage | Kern | Beleg |
|---|---|---|
| Was empfehlt ihr? | Eine Erhöhung anbieten, wo die Miete unter dem Markt liegt. Klasse 50–80 m²: 18 von 25 Verträgen, Median 6 %. Klasse 80–100 m²: 11 von 25, Median 0 %. | Vorlage, Kopf |
| Warum ist der Mehrertrag so klein (32.587 € bzw. 6.278 € über 5 Jahre)? | Die Mieten sind nahe am Markt simuliert. Erhöht wird nur, wo eine Miete deutlich darunter liegt. | Vorlage, Abschnitt 5 |
| Erklär LS-45 gegen LS-29. | Beide bekommen +12 %. Der Markt liegt 12,8 % bzw. 9,7 % über ihrer Miete. Die Bankangestellte verdient mehr und akzeptiert deshalb eher (60 % statt 46 %), also verlangt das Modell bei ihr mehr. Das Einkommen wirkt doch auf die Höhe. Die Vorlage deckelt deshalb auf den Markt und erhöht nicht über 35 % Belastung. | E47, Folie 9 |
| Warum verträgt der Handel am meisten? | Wegen der Lücke zum Markt (Median 11,8 % darunter), nicht wegen des Berufs. Die KV-Erhöhungen 2026 liegen überall um 3 %. | Folie 8 |
| Woran hängt die Empfehlung am stärksten? | An der Wechselbereitschaft, einer ungemessenen Annahme. Am unteren Rand ändern sich 43 von 50 Empfehlungen. | `kennzahl_sensitivitaet` |

### G · Grenzen, Recht, Ethik

| Frage | Kern | Beleg |
|---|---|---|
| Darf man das überhaupt? | Im laufenden Vertrag ist eine Erhöhung nur über die vereinbarte Wertsicherung möglich, die seit 1.1.2026 gedeckelt ist. Die Empfehlung sagt, was der Markt trägt, nicht was sofort durchsetzbar ist. Kein Rechtsrat. | Vorlage, Abschnitt 7 |
| Ist das nicht unethisch? | Die Prämisse ist bewusst zugespitzt, und das Ergebnis ist der Befund: Mieter automatisiert auszupressen ist zum Glück nicht so einfach. Markt, Einkommen und Verhalten sind nur bruchstückhaft beobachtbar, und wo das Modell wirkt, trifft es die mit mehr Einkommen. | Schwäche 5, E05, E47 |
| Was fehlt am meisten? | Die VPI-Reihe (Wertsicherung ist pauschal angenommen), eine längere Marktreihe, echte Einkommensniveaus und gemessene Reaktionen. | 07 Datenlücken |
| Warum nutzt ihr nicht die Gesetzesmaterialien oder den Tariflohnindex? | Der Tariflohnindex misst dasselbe wie die extrahierten KV-Reihen, nur gröber. Die Materialien würden dem Prototyp nichts bringen, solange der VPI fehlt. | 07 |

### H · Arbeitsweise

| Frage | Kern | Beleg |
|---|---|---|
| Was hat das LLM gemacht, was du? | Ehrlich antworten: Claude hat in der Arbeitssitzung den Großteil von Code und Dokumentation geschrieben und steht in jedem Commit als Co-Autor. Ich habe die Daten beschafft, die Labelling-Versuche gemacht, die KV-Referenzen gegen die Quelle bestätigt, den Umfang festgelegt und die Entscheidungen getroffen. Wer was entschieden hat, steht im Log. | E24, E31, E41, E48 |
| Warum ist die Commit-Historie zwischen 10.10. und 23.10. leer? | Der Revisionspunkt von E30 ist eingetreten. Das ist offen dokumentiert und nicht nachträglich geglättet. | E30, 07 Risiken |
| Welcher Fehler hat euch am meisten gelehrt? | Zum Beispiel Haushalte, die mehr Miete zahlten, als sie verdienten (E40), oder sechs Tests, die nie liefen. Alles war grün, und ein Blick auf eine einzelne Zahl fand den Fehler. | Lesson 1 |
| Was würdest du anders machen? | Die Sensitivität früher laufen lassen und in Messung investieren statt in ein feineres Modell. Die Dämpfung des Fixpunkts war im Demo-Portfolio unnötig. | Lesson 3, E18 |
| Kann man das live zeigen? | Ja, über das Colab-Notebook `docs/demo/auto_landlord_demo.ipynb`. Es klont das Repo, führt `python3 -m src.run` aus (8 s), zeigt die Ergebnisse und lässt Evals und Tests laufen. | README |

---

## Teil 3 · Zahlen, die sitzen sollten

| Zahl | Bedeutung | Quelle |
|---|---|---|
| 3 Abrufe, 285 Inserate, 442 Beobachtungen | Marktdaten 25.09., 09.10., 23.10.2026 | 06 |
| 24,25 / 23,86 €/m² | Marktmedian 50–80 / 80–100 m² am 23.10. | `kennzahl_marktentwicklung` |
| 15 KV-Datensätze | 5 Branchen × 2024–2026, alle durch Gate 4 | `kennzahl_kv_entwicklung` |
| 18/25 und 11/25 | Verträge mit Erhöhung je Größenklasse | `kennzahl_empfehlung` |
| 3,4 % → 8,3 % | mittlere Erhöhung: Basisfall → niedrige Wechselbereitschaft | `kennzahl_sensitivitaet` |
| 61 + 26 + 28 | Tests in Pipeline, Modell und Gradern | `CLAUDE.md` |
| E01–E48 | Einträge im Entscheidungslog, jeweils mit Alternative und Revisionspunkt | 01 |
