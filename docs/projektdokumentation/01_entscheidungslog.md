# Entscheidungslog

Jede Entscheidung mit echter Alternative. Wo es keine Alternative gab, war es
keine Entscheidung und steht nicht hier.

**Zur Datierung, offen gesagt:** dieses Log wurde ab E19 mit dem jeweiligen
Tagesdatum geführt. E01–E18 sind in den Arbeitssitzungen davor gefallen und
hier nachträglich eingetragen. Sie tragen deshalb keine erfundenen Datumsangaben,
sondern die Phase, in der sie fielen. Der einzige datumsgenau belegte Zeitpunkt
in dieser Gruppe ist der Datenabruf am **25.09.2026, 15:55** — er steht im
Schnappschuss selbst (`searchDate`), nicht in einer Notiz.

Aufbau jedes Eintrags: Situation · Alternativen · Entscheidung · Begründung ·
Revisionspunkt (woran man erkennt, dass sie falsch war).

| Nr | Datum / Phase | Entscheidung | Alternative | Warum | Folge |
|---|---|---|---|---|---|
| [E01](#e01) | Themenwahl | Wasserentnahme-Ampel Leitha als Thema | fertige Kaggle-Daten; altes Strommarktthema | vorbereinigte Wettbewerbsdaten fallen am Kriterium der echten Quellen durch | `verworfen durch E02` |
| [E02](#e02) | Themenwahl | Wechsel auf Kraftwerk Greifenstein, Entscheider ist die Behoerde | Betreiber entscheidet ueber das Stauziel | der Betreiber optimiert innerhalb gegebener Grenzen - das ist Rechnen, keine Entscheidung | `verworfen durch E03` |
| [E03](#e03) | Themenwahl | Wechsel auf Mietportfolio Wien | beim Wasserthema bleiben und die Beschaffung reparieren | Beobachtbarkeit des Preisniveaus war die Bedingung, die zweimal fehlte | `ganzes Repository` |
| [E04](#e04) | Zuschnitt | Entscheider ist die Leitung Asset Management | Gesetzgeber; Mieter | nur der Vermieter hat Adressat, Termin und echte Optionen | `00_auftrag.md` |
| [E05](#e05) | Zuschnitt | Einkommen wirkt auf Annahme und Ausfall, nicht auf den Preis | Lohnabschluss als Begruendung des Mietzinses | der Mietzins bemisst sich am Objekt, nicht am Gehalt - sonst rechtlich nicht anschlussfaehig | `src/entscheidung.py, config/berufsgruppen.json` |
| [E06](#e06) | Datenzugriff | Manuelle Beschaffung, automatisierte Verarbeitung | Crawler bauen; Thema wechseln | die robots.txt untersagt automatisierten Zugriff ausdruecklich | `02_schritt1_datenzugriff.md, tools/snapshot.js` |
| [E07](#e07) | Datenzugriff | __NEXT_DATA__ parsen statt HTML-Klassen | CSS-Selektoren auf das gerenderte HTML | die Klassen sind generierte Hashes und aendern sich bei jedem Deploy | `src/wh_next_data.py` |
| [E08](#e08) | Datenzugriff | Abrufzeit aus searchDate des Servers | datetime.now() beim Verarbeiten | sonst haette dieselbe Datei bei jedem Lauf einen anderen Zeitstempel | `src/wh_next_data.py` |
| [E09](#e09) | Datenzugriff | PLZ aus dem Dateinamen ist Pflichtpruefung | optionaler Parameter erwartete_plz | eine Pruefung, die man einschalten muss, ist an dem Tag aus, an dem sie gebraucht wird | `src/validierung.py` |
| [E10](#e10) | Datenzugriff | Selbstpruefendes Beschaffungsskript | schriftliche Anleitung | die Fehlerquelle sitzt vor der Pipeline; ein Gate kostet einen ganzen Durchgang | `tools/snapshot.js` |
| [E11](#e11) | Datenschutz | Allowlist im Code, 18 Felder | Blocklist; Filterung im Prompt | eine Blocklist laesst jedes neue Feld durch; ein Prompt ist nicht testbar | `src/config.py, src/clean.py` |
| [E12](#e12) | Datenmodell | SQLite statt MySQL-Server | MySQL-Server betreiben | ein Server macht den Datenbankzustand zu etwas, das im Repository nicht steht | `src/sql/schema.sql` |
| [E13](#e13) | Datenmodell | Schluessel (snapshot_id, ad_id), append-only | ad_id als Schluessel, Zeile aktualisieren | Aktualisieren wirft Preisaenderung und Inseratsdauer weg | `src/sql/schema.sql` |
| [E14](#e14) | Datenmodell | PLZ als Fremdschluessel, Bezirke in der Konfiguration | Bezirk als Textspalte in der Faktenzeile | ein Bezirk mehr soll eine Datei mehr sein, keine Codeaenderung | `src/config.py, src/sql/views.sql` |
| [E15](#e15) | Datenmodell | Datenbank bei jedem Lauf neu bauen | inkrementell laden | sonst haengt das Ergebnis an der Reihenfolge der Laeufe | `src/integrate.py` |
| [E16](#e16) | Analyse | Median ueber Fensterfunktion, Fallzahl an jeder Zeile | Mittelwert; Aggregation in pandas | der Mittelwert kippt bei moeblierten Kurzzeitangeboten; Zahlen sollen aus SQL kommen | `src/sql/views.sql` |
| [E17](#e17) | Modell | Gegenkraefte ins Entscheidungsmodell | Zielgroesse ohne Gegenkraft, Grenzen extern | ein Modell, dessen Empfehlung nicht von den Daten abhaengt, ist eine Meinung mit Nachkommastellen | `src/entscheidung.py` |
| [E18](#e18) | Modell | Portfolio-Fixpunkt mit 50/50-Daempfung | Marktmiete als gegeben nehmen | sonst ueberschaetzt das Modell den Preis genau im Anwendungsfall | `src/entscheidung.py` |
| [E19](#e19) | 25.09. | PII-Logik in clean.py, Allowlist nur in config.py | pii.py behalten und importieren | zwei Fassungen derselben Liste laufen auseinander | `src/clean.py; src/pii.py entfernt` |
| [E20](#e20) | 25.09. | GitHub-Repository als gemeinsame Arbeitsflaeche | Dateien hin und her schicken; nur lokales Git | Anhaenge erzeugen Commits ohne Bezug zu den Arbeitsschritten | `Repository, origin` |
| [E21](#e21) | 25.09. | Redigierte Schnappschuesse im Repo, Originale nur lokal | Repo privat halten und Originale committen | ein Push ist unumkehrbar; git rm entfernt nichts aus der Historie | `tools/redigiere_schnappschuss.py` |
| [E22](#e22) | 25.09. | verticalId als erste Pruefung in Gate 1 | bei Trefferzahl und PLZ-Streuung bleiben | Indizien haetten eine seltene Marktplatzsuche durchgelassen | `src/validierung.py` |
| [E23](#e23) | 25.09. | Ein Dokument je Schritt | Schrittdokument fasst zusammen und verweist | eine Zusammenfassung, die niemand nachzieht, ist schlechter als keine | `02_schritt1_datenzugriff.md` |
| [E24](#e24) | 25.09. | Claude bleibt Autor der Commits | Studierender als Autor, Claude als Co-Autor | Wunsch des Studierenden; die Konsequenz ist benannt | `revidiert durch E31` |
| [E25](#e25) | 25.09. | data/raw/ wird committet | Vorgabe woertlich; oder nach data/sample/ verschieben | der Zweck des Satzes ist durch die Redaktion erfuellt; sample heisst synthetisch | `gitignore` |
| [E26](#e26) | 25.09. | Datenbank committet, Uhrzeit aus ihr entfernt | Datenbank ignorieren; oder Diff je Lauf hinnehmen | eine committete Datei mit Uhrzeit widerlegt die Reproduzierbarkeit | `src/sql/schema.sql, src/integrate.py` |
| [E27](#e27) | 09.10. | Je Aufgabe festgelegt: Programm oder Prompt | alles dem Modell geben; alles selbst programmieren | was pruefbar sein muss, gehoert in Code; was Sprache ist, ins Modell | `CLAUDE.md, 05_schritt4_abfragen_referenzen.md` |
| [E28](#e28) | 09.10. | Keine Extraktionsreferenzen ohne Quelldokument | acht Faelle aus der Modellrecherche bilden | eine Referenz aus einer Modellzusammenfassung prueft das Modell gegen sich selbst (E02) | `evals/references/README.md` |
| [E29](#e29) | 09.10. | Auftrag nach dem Pitch unveraendert | Scope oder Analysen nach dem Feedback anpassen | das Feedback war durchgehend positiv und stellte nichts davon in Frage | `00_auftrag.md` |
| [E30](#e30) | 09.10. | Repository-Stand entpackt committen, Schritte als einzelne Commits | ZIP als Abgabe belassen | ein ZIP ist fuer die Bewertung nicht lesbar und hat keine Historie | `Commits ab b65e6cf` |
| [E31](#e31) | 09.10. | Studierender als Autor, Claude als Co-Autor | Claude bleibt Autor (E24) | Wunsch des Studierenden; wer was beigetragen hat, steht weiterhin hier | `Git-Historie, CLAUDE.md` |
| [E32](#e32) | 09.10. | Seiten eines Tages sind ein Abruf | jede Seite als eigener Abruf; Seiten beim Einlesen zu einer Datei zusammenfuegen | sonst galten alle Inserate von Seite 1 als verschwunden; Zusammenfuegen haette die Herkunft je Datei verwischt | `src/sql/views.sql (v_abruf), src/clean.py, Commit 2d853b0` |
| [E33](#e33) | 09.10. | WG-Zimmer aus dem Angebot, sichtbar mit Grund | behalten; schon beim Einlesen verwerfen | Zimmerpreis auf Wohnungsflaeche ist kein Quadratmeterpreis; Verwerfen beim Einlesen waere unsichtbar | `src/config.py, objekttyp_ausschluss, Commit f6dd973` |
| [E34](#e34) | 09.10. | Gemeindewohnungen per Prompt klassifizieren | behalten; per Schlagwort im Titel ausschliessen | Entscheidung des Studierenden; liefert die Klassifikationsreferenz, die E28 offenlaesst | `E37, evals/references/ (folgt)` |
| [E37](#e37) | 09.10. | Referenz markiert der Studierende selbst; Modell-Labeling nur als Testfall | Modellmarkierung als Referenz uebernehmen | ein Modell als Massstab fuer ein Modell misst die eigene Formulierung (E02, E28) | `evals/references/ (folgt)` |
| [E35](#e35) | 09.10. | view-source als empfohlener Beschaffungsweg | gerendertes HTML parsen; nur snapshot.js | view-source holt die Seite immer frisch; das gerenderte HTML traegt Preise nur in CSS-Klassen | `02_schritt1_datenzugriff.md, docs/betrieb.md` |
| [E36](#e36) | 09.10. | Ungemessene Abgaenge nicht als null Tage; Anteil noch online als Kennzahl | Mittelwert mit 0 fuer Einmal-Gesehene; nur Mittelwert der Wiedergesehenen | eine unbekannte Dauer ist nicht null; mit zwei Abrufen ist der Anteil die einzige ehrliche Aussage | `src/sql/kennzahl_inseratsdauer.sql, Commit 8e7565a` |

---

## E01 {#e01}
### Wasserentnahme-Ampel für die Leitha als Projektthema
**Phase:** Themenwahl

**Situation.** Gesucht war ein Thema, zu dem es echte, laufend aktualisierte
österreichische Daten gibt und eine Entscheidung, die jemand tatsächlich trifft.

**Alternativen.**
1. Wasserentnahme-Ampel für einen Fluss (eHYD-Pegel + Trockenheitsindex).
2. Strommarkt-Thema aus einem früheren Projekt.
3. Ein Thema mit fertigen Kaggle-Daten.

**Entscheidung.** Variante 1.

**Begründung.** (3) fällt am Bewertungskriterium „existieren die Quellen
wirklich" durch — vorbereinigte Wettbewerbsdaten sind genau der Fall, den die
Lehrveranstaltung ausschließt. (2) war vorhanden, aber ohne
Entscheidungsträger.

**Was schiefging.** Die Pegeldaten ließen sich nicht verlässlich automatisiert
abrufen: das Download-Muster, das ich für eHYD angenommen hatte
(`MessstellenExtraData/owf?id=…&file=…`), lieferte im Test 404. Ich hatte es
aus einem Drittanbieter-Beispiel übernommen und nicht selbst geprüft. Das ist in
`02_schritt1_datenzugriff.md` als Irrtum protokolliert.

**Revisionspunkt.** Erledigt durch E02.

---

## E02 {#e02}
### Wechsel auf das Donaukraftwerk Greifenstein
**Phase:** Themenwahl

**Situation.** Das Wasserthema sollte bleiben, aber mit einer Entscheidung, die
eine benennbare Stelle trifft.

**Alternativen.**
1. Kraftwerksbetreiber entscheidet über Stauziel.
2. Wasserrechtsbehörde entscheidet über die Regel, innerhalb der der Betreiber
   entscheidet.

**Entscheidung.** Variante 2, auf ausdrücklichen Wunsch.

**Begründung.** Der Betreiber optimiert innerhalb gegebener Grenzen — das ist
Rechnen, keine Entscheidung mit Optionen. Die Behörde entscheidet über die
Grenzen selbst und hat konkurrierende Ziele (Energie, Schifffahrt, Ökologie).

**Was schiefging.** Zwei Dinge, beide dokumentiert.
Erstens hatte das Modell keine Gegenkraft: die Empfehlung war immer das
größtmögliche Stauzielband (→ E17). Zweitens war das Goldset für die
LLM-Auswertung ungültig, weil ich die `rohtext`-Felder aus Suchtreffer-Snippets
rekonstruiert hatte statt wörtlich aus den PDFs zu kopieren. Ein Eval gegen
meine eigene Formulierung misst nichts.

**Revisionspunkt.** Erledigt durch E03. Die Lehre aus dem Goldset gilt weiter:
Referenzantworten werden wörtlich aus dem Quelldokument kopiert, mit Seitenzahl.

---

## E03 {#e03}
### Wechsel auf das Mietportfolio Wien
**Phase:** Themenwahl

**Situation.** Nach zwei Anläufen fehlte immer noch eine Datenquelle, die sich
regelmäßig und ohne Bastelei neu abrufen lässt — das Kernstück einer Pipeline,
die Datenänderungen überleben soll.

**Alternativen.**
1. Beim Wasserthema bleiben und die Beschaffung reparieren.
2. Auf ein Thema wechseln, dessen Marktpreisniveau laufend beobachtbar ist:
   Mietinserate in drei Wiener Bezirken.

**Entscheidung.** Variante 2.

**Begründung.** Beobachtbarkeit des Preisniveaus war die Bedingung, die in
beiden Vorversionen fehlte. Ein Inseratsportal liefert sie täglich neu. Damit
wird auch das Bewertungskriterium „übersteht die Pipeline Datenänderungen"
prüfbar statt behauptet.

**Preis dieser Entscheidung.** Das Thema ist sozialpolitisch unangenehm — ein
Vermieter, der Mieten ausreizt. Ausdrücklich in Kauf genommen. Was das Projekt
nicht tut: es nutzt keine Daten über echte Personen (E11) und behauptet nicht,
das Ergebnis sei wünschenswert.

**Revisionspunkt.** Wenn im Zielsegment 80–100 m² dauerhaft weniger als acht
Inserate je Bezirk und Abruf stehen, trägt die Marktseite die Entscheidung
nicht.

---

## E04 {#e04}
### Entscheidungsträger ist die Leitung Asset Management, nicht eine Behörde
**Phase:** Zuschnitt

**Situation.** Dieselbe Frage wie in E02: wer entscheidet was?

**Alternativen.**
1. Vermieter entscheidet je Vertrag über den Verlängerungspreis.
2. Gesetzgeber entscheidet über die Indexierungsgrenze.
3. Mieter entscheidet über Annahme oder Auszug.

**Entscheidung.** Variante 1.

**Begründung.** (2) wäre eine Politikfolgenabschätzung mit Daten, die wir nicht
haben. (3) ist keine Entscheidung mit Datengrundlage, sondern Verhalten — und
geht als modellierte Reaktion in (1) ein. (1) hat einen Adressaten mit Namen und
Rolle, einen Termin (Vertragsende) und echte Optionen: verlängern zu X,
verlängern zu Y, auslaufen lassen.

**Revisionspunkt.** Wenn die Empfehlung unabhängig von den Daten immer dieselbe
Option wäre, ist es keine Entscheidung (vgl. E17).

---

## E05 {#e05}
### Einkommensdaten sind Annahme- und Risikogröße, nicht Preisargument
**Phase:** Zuschnitt

**Situation.** Erste Fassung: das Portfolio ist an gutverdienende Berufsgruppen
vermietet, deren Kollektivvertragsabschlüsse öffentlich sind — also Miete an
Lohnentwicklung koppeln.

**Alternativen.**
1. Lohnabschluss als Begründung des Mietzinses („ihr Gehalt ist gestiegen").
2. Lohnabschluss als Einflussgröße auf Annahmewahrscheinlichkeit und
   Ausfallrisiko.

**Entscheidung.** Variante 2.

**Begründung.** (1) ist rechtlich nicht anschlussfähig: der Mietzins bemisst
sich am Objekt und der vertraglichen Wertsicherung, nicht am Einkommen des
Mieters. Als Prognosegröße für Zahlungsfähigkeit und Umzugsbereitschaft ist die
Lohnentwicklung dagegen genau das Richtige — und wird damit zu einer Größe, die
das Modell braucht, aber nicht sicher kennt.

**Wichtige Unschärfe, die daraus folgt.** Der Tariflohnindex misst
**Mindestlöhne** nach Kollektivvertrag, nicht Ist-Löhne einschließlich
Überzahlung. Bei Berufsgruppen mit hoher Überzahlung (IT) ist er ein schlechter
Schätzer, im öffentlichen Dienst ein guter. `config/berufsgruppen.json` führt
diesen Unschärfegrad je Gruppe mit; er ist die wichtigste bekannte Schwäche des
Modells und gehört in die Entscheidungsvorlage.

**Revisionspunkt.** Sobald eine Ist-Lohn-Reihe je Branche verfügbar ist, ersetzt
sie den Tariflohnindex.

---

## E06 {#e06}
### Manuelle Beschaffung statt automatisiertem Abruf
**Phase:** Datenzugriff · belegt 25.09.2026

**Situation.** Das Portal hat keine offene API. Die `robots.txt` untersagt im
Kopfkommentar ausdrücklich jeden automatisierten Zugriff und ist damit eine
maschinenlesbare Nutzungsvorbehaltserklärung.

**Alternativen.**
1. Crawler bauen und den Vorbehalt ignorieren.
2. Ein Mensch speichert die Seite, die Pipeline verarbeitet die Datei.
3. Thema wechseln (erneut).

**Entscheidung.** Variante 2.

**Begründung.** (1) ist nicht verhandelbar — und für die Bewertung nichts wert,
weil der automatisierte Teil ohnehin erst nach dem Abruf beginnt. (3) wäre der
vierte Themenwechsel. (2) kostet einen dokumentierten manuellen Schritt und
liefert dafür einen Datenstand, dessen Herkunft über SHA256 nachweisbar ist.
Dass mein eigener Abrufversuch am Botschutz scheiterte, bestätigt die
Einschätzung eher als sie zu widerlegen.

**Zugehörige Korrektur.** Ich hatte zunächst behauptet, die `robots.txt`
blockiere nur Filterparameter — Quelle war die Dokumentation eines
Scraping-Anbieters, also eine interessierte Zusammenfassung. Die archivierte
Datei (`docs/willhaben_robots_2026-09-25.txt`) sagt etwas anderes. Die
Korrektur steht in `02_schritt1_datenzugriff.md`.

**Revisionspunkt.** Wenn das Portal eine dokumentierte API mit
Nutzungsbedingungen anbietet, entfällt der manuelle Schritt.

---

## E07 {#e07}
### `__NEXT_DATA__` parsen statt HTML-Struktur
**Phase:** Datenzugriff

**Situation.** Die gespeicherte Seite enthält die Inserate zweimal: als
gerendertes HTML und als JSON im Script-Tag `__NEXT_DATA__`.

**Alternativen.**
1. HTML mit CSS-Selektoren auslesen.
2. Das JSON auslesen.

**Entscheidung.** Variante 2, Pfad
`props.pageProps.searchResult.advertSummaryList.advertSummary[]`.

**Begründung.** Die CSS-Klassen sind generierte Hashes (`Box-sc-wfmb7k-0
jiBisN`) und ändern sich bei jedem Deploy des Portals. Ein Parser darauf ist bei
der nächsten Produktänderung still kaputt. Die JSON-Feldnamen (`PRICE`,
`ESTATE_SIZE`, `ISPRIVATE`) sind Teil der Anwendungsschnittstelle und stabiler.
Zusätzlich liefert das JSON Felder, die im HTML nicht stehen — etwa
`ISPRIVATE`, das für E11 die entscheidende Unterscheidung trägt.

**Revisionspunkt.** `test_eur_pro_m2_des_portals_stimmt_mit_eigener_rechnung`:
wenn das Portal Feldbedeutungen ändert, fällt der Test, nicht die Zahl.

---

## E08 {#e08}
### Abrufzeitpunkt kommt vom Server, nicht von der Uhr des Parsers
**Phase:** Datenzugriff

**Situation.** Jede Beobachtung braucht einen Zeitstempel. Naheliegend wäre
`datetime.now()` beim Verarbeiten.

**Alternativen.**
1. Verarbeitungszeitpunkt.
2. `searchDate` aus der Antwort des Servers.

**Entscheidung.** Variante 2.

**Begründung.** Mit (1) bekommt dieselbe Datei bei jeder Verarbeitung einen
neuen Zeitstempel — der zweite Lauf hätte einen anderen Datenstand als der
erste, und die Zeitreihe würde den Zeitpunkt der Verarbeitung statt den der
Beobachtung messen. (2) ist eine Eigenschaft der Daten, nicht des Laufs.

**Revisionspunkt.** `test_abrufzeit_kommt_vom_server_nicht_vom_parser` und
`test_zweiter_lauf_liefert_dieselben_zahlen`.

---

## E09 {#e09}
### PLZ aus dem Dateinamen ist Pflichtprüfung, nicht Option
**Phase:** Datenzugriff · Vorfall 25.09.2026

**Situation.** Drei gelieferte Schnappschüsse waren byte-identisch
(SHA256 `a2ca0e8b…`), obwohl sie nach drei verschiedenen Bezirken benannt
waren — und alle drei enthielten Marktplatzdaten statt Immobilien:
`verticalId: 5`, 13.353.029 Treffer.

**Ursache.** `__NEXT_DATA__` wird bei clientseitiger Navigation innerhalb der
Next.js-App **nicht** aktualisiert. Wer sich durch die Seite klickt und dann
speichert, speichert den serverseitig gerenderten Erstaufruf. Nur ein
vollständiger Seitenaufruf (URL eingeben, Enter) erzeugt frisches
`__NEXT_DATA__`.

**Alternativen.**
1. Prüfung als optionaler Parameter (`erwartete_plz=…`), aufrufbar bei Bedarf.
2. Prüfung immer, PLZ aus der Namenskonvention `wh_<plz>_<suche>_<datum>.json`.

**Entscheidung.** Variante 2.

**Begründung.** Eine Prüfung, die man einschalten muss, ist an dem Tag aus, an
dem sie gebraucht wird. Der Dateiname ist die einzige vom Dateiinhalt
**unabhängige** Aussage darüber, was die Datei zeigen soll — genau deshalb
taugt er als Prüfgröße. Zusätzlich schlägt ein wiederkehrender SHA256 Alarm.

**Revisionspunkt.** `test_gate_meldet_plz_abweichung`, `test_gate_faengt_falsche
_seite_ab` gegen `data/sample/negativ_falscher_vertical.json`. Die Negativdatei
bleibt bewusst im Repository: sie ist gültiges JSON und hätte ohne Gate
schweigend einen Median über Gebrauchtwaren geliefert.

---

## E10 {#e10}
### Selbstprüfendes Beschaffungsskript statt schriftlicher Anleitung
**Phase:** Datenzugriff

**Situation.** Nach E09 war klar: die Fehlerquelle sitzt vor der Pipeline, im
manuellen Schritt. Ein Gate, das erst hinterher ablehnt, kostet einen ganzen
Beschaffungsdurchgang.

**Alternativen.**
1. Schritt-für-Schritt-Anleitung in der Dokumentation.
2. Konsolenskript, das die Prüfungen vor dem Speichern selbst ausführt und den
   Dateinamen aus den Daten bildet.

**Entscheidung.** Variante 2 (`tools/snapshot.js`), zusätzlich zur Anleitung.

**Begründung.** Das Skript prüft genau das, was in E09 schiefging —
`verticalId`, Trefferzahl, PLZ-Anteil, URL gegen Daten — und bricht mit
benanntem Grund ab. Der Dateiname entsteht aus dem Inhalt, nicht aus dem
Gedächtnis. Damit ist die Prüfung dort, wo der Fehler entsteht, und das Gate
wird zur zweiten Verteidigungslinie statt zur ersten.

**Revisionspunkt.** Wenn wieder eine Datei am Gate scheitert, hat das Skript
seinen Zweck verfehlt — dann fehlt eine Prüfung darin.

---

## E11 {#e11}
### Allowlist statt Blocklist, durchgesetzt im Code
**Phase:** Datenschutz

**Situation.** Die Vorgabe verbietet personenbezogene Daten ausnahmslos. Die
Inseratsdaten enthalten reichlich davon, teils nicht offensichtlich:
`ORGNAME` ist formal ein Firmenname, trägt aber häufig Personennamen
(„MMI Mario Molnar Immobilienberatung", „Realbüro Dr. C. Huber"), dazu
Anbieterkennungen, Freitexte und punktgenaue Koordinaten.

**Alternativen.**
1. Blocklist: bekannte Problemfelder verwerfen.
2. Allowlist: nur ausdrücklich erlaubte Felder behalten.
3. Filterung im LLM-Prompt beschreiben.

**Entscheidung.** Variante 2, 18 erlaubte Felder in `config.PII_ERLAUBT`,
Verwerfungsgründe in `config.PII_VERWORFEN`.

**Begründung.** (1) lässt jedes neue Feld des Portals stillschweigend durch —
die Richtung ist falsch. (3) ist keine Zusicherung, sondern eine Bitte; ein
Prompt ist nicht prüfbar und nicht testbar. (2) versagt im Zweifel zur
sicheren Seite: ein unbekanntes Feld fliegt raus und fällt dadurch auf.
Behalten wird von der Anbieterseite nur `ISPRIVATE` — privat oder gewerblich
ist eine Analysegröße (der gewerbliche Median liegt 16 % über dem privaten),
und das Flag benennt niemanden.

**Revisionspunkt.** `test_kein_pii_in_bereinigten_zeilen` und die
Kontrollsuche in `clean.pii_kontrolle` als letzte Instanz vor dem Schreiben.
Ein Treffer dort ist ein Fehler, keine Warnung.

---

## E12 {#e12}
### SQLite statt MySQL-Server
**Phase:** Datenmodell

**Situation.** Ursprünglich war ein MySQL-Server angedacht.

**Alternativen.**
1. MySQL-Server.
2. SQLite als Datei im Projekt.

**Entscheidung.** Variante 2.

**Begründung.** Die Datenmengen sind klein (Hunderte Zeilen je Abruf). Ein
Server verlangt Installation, Zugangsdaten und einen laufenden Prozess — und
macht den Zustand der Datenbank zu etwas, das im Repository nicht steht. Mit
SQLite ist die Datenbank ein erzeugtes Artefakt: `python3 -m src.run` genügt,
auf jedem Rechner, ohne Zugangsdaten. Das SQL bleibt Standard-SQL; der Umzug auf
einen Server wäre eine Konfigurationsänderung.

**Preis.** Kein `PERCENTILE_CONT` (→ E16), keine parallelen Schreibzugriffe.

**Revisionspunkt.** Wenn die Datenbank mehrere Nutzer gleichzeitig bedienen
soll oder Millionen Zeilen hält.

---

## E13 {#e13}
### Faktentabelle append-only, Schlüssel (Schnappschuss, Inserat)
**Phase:** Datenmodell

**Situation.** Derselbe Inseratsschlüssel erscheint in aufeinanderfolgenden
Abrufen erneut, teils mit geändertem Preis.

**Alternativen.**
1. Primärschlüssel `ad_id`, Zeile beim Wiedersehen aktualisieren.
2. Primärschlüssel `(snapshot_id, ad_id)`, nie aktualisieren.

**Entscheidung.** Variante 2.

**Begründung.** (1) wirft genau die Information weg, die zwei der drei Analysen
tragen: Preisänderung während der Laufzeit und Inseratsdauer. Mit (2) fallen
beide als Abfrage aus den Daten heraus, ohne eigene Erhebung — und die
Inseratsdauer ist zugleich der Schätzer für die Leerstandsannahme im
Entscheidungsmodell, die bisher geraten ist.

**Bekannte Komplikation.** Ein Inserat im jüngsten Schnappschuss seiner PLZ ist
noch offen; seine Dauer ist eine Untergrenze. `v_inseratsdauer` führt deshalb
die Spalte `zensiert`. Ein Mittelwert über zensierte Fälle unterschätzt
systematisch — der Kennzahl-Kommentar sagt das.

**Revisionspunkt.** Sobald zwei Schnappschüsse derselben PLZ vorliegen, müssen
`v_preisaenderung` und `v_inseratsdauer` Zeilen liefern. Heute sind sie leer,
und das ist kein Fehler, sondern der aktuelle Stand.

---

## E14 {#e14}
### PLZ als Fremdschlüssel, Bezirksliste in der Konfiguration
**Phase:** Datenmodell

**Situation.** Das Portfolio liegt in drei Bezirken, zwei weitere dienen als
Referenz. Es sollen Bezirke hinzukommen können.

**Alternativen.**
1. Bezirk als Text in der Beobachtungszeile.
2. Tabelle `bezirk` mit PLZ als Schlüssel, Zuordnung aus `config.BEZIRKE`.

**Entscheidung.** Variante 2, Views durchgehend nach PLZ gruppiert.

**Begründung.** Ein neuer Bezirk ist damit eine Datei mehr und ein Eintrag in
der Konfiguration — kein Eingriff in Views oder Code. Zugleich wird eine
unbekannte PLZ sichtbar statt still: sie landet in `zuordnungsluecke` und wird
gezählt. Eine Textspalte hätte den Fall stumm geschluckt.

**Revisionspunkt.** `test_jede_beobachtung_haengt_an_einem_bezirk`;
`v_abdeckung` zeigt je Bezirk „noch nicht beschafft" statt gar nichts.

---

## E15 {#e15}
### Die Datenbank wird bei jedem Lauf neu gebaut
**Phase:** Datenmodell

**Situation.** Reproduzierbarkeit war Abnahmekriterium: zwei Läufe, dieselben
Zahlen.

**Alternativen.**
1. Inkrementell laden, nur neue Schnappschüsse ergänzen.
2. Datenbank löschen und aus **allen** Rohordnern neu aufbauen.

**Entscheidung.** Variante 2.

**Begründung.** Bei (1) hängt das Ergebnis von der Reihenfolge der Läufe ab,
und ein Fehler von vorgestern bleibt in der Datenbank, auch wenn der Code
repariert ist. Bei (2) ist `data/raw/` die Quelle der Wahrheit und die Datenbank
ein jederzeit verwerfbares Ergebnis. Die Kosten sind bei dieser Datenmenge
irrelevant (Laufzeit unter zwei Sekunden).

**Revisionspunkt.** `test_zweiter_lauf_liefert_dieselben_zahlen`. Bei
Datenmengen, bei denen ein Neuaufbau Minuten dauert, kippt die Abwägung —
dann braucht es (1) plus einen Prüflauf, der (2) nachrechnet.

---

## E16 {#e16}
### Median über Fensterfunktion, Fallzahl an jeder Aggregatzeile
**Phase:** Analyse

**Situation.** SQLite kennt kein `PERCENTILE_CONT` (Folge von E12).

**Alternativen.**
1. Mittelwert statt Median.
2. Aggregation in Python (pandas).
3. Median in SQL über `ROW_NUMBER()` und `COUNT()` als Fensterfunktionen.

**Entscheidung.** Variante 3.

**Begründung.** (1) ist bei Mietinseraten irreführend: einzelne möblierte
Kurzzeitangebote mit 60 €/m² ziehen den Mittelwert, nicht den Median. (2) würde
die Vorgabe brechen, dass jede Zahl der Entscheidungsvorlage aus einer
SQL-Abfrage kommt und diese nennt. (3) hält die Zahl im SQL und ist prüfbar.

**Zweite Entscheidung im selben Zug.** Jede Aggregatzeile führt ihre Fallzahl
und eine Belastbarkeitsstufe mit (n≥15 belastbar, n≥8 dünn, sonst nicht
belastbar). Ein Median über vier Inserate sieht in einer Tabelle genauso aus wie
einer über vierzig. Ohne die Fallzahl **in derselben Zeile** wird die
Unsicherheit beim Weiterverwenden abgeschnitten — besonders, wenn ein
Sprachmodell die Zeile in Prosa übersetzt.

**Revisionspunkt.** `test_median_liegt_zwischen_min_und_max`,
`test_fallzahl_steht_an_jeder_aggregatzeile`.

---

## E17 {#e17}
### Jedes Entscheidungsmodell braucht eine Gegenkraft
**Phase:** Modell

**Situation.** Im Greifenstein-Modell war die Empfehlung ausnahmslos das
größte Stauzielband — das Modell hatte keinen Grund, je etwas anderes zu sagen.
Im Mietmodell drohte dasselbe: ohne Gegenkraft ist die optimale Miete immer die
höchste.

**Alternativen.**
1. Zielgröße ohne Gegenkraft, Grenzen extern setzen.
2. Gegenkräfte ins Modell: Annahmewahrscheinlichkeit, Leerstandskosten,
   Ausfallrisiko oberhalb einer Belastungsschwelle.

**Entscheidung.** Variante 2.

**Begründung.** Ein Modell, dessen Empfehlung nicht von den Daten abhängt, ist
keine Entscheidungsunterstützung, sondern eine Meinung mit Nachkommastellen.
Erst mit Gegenkraft entsteht ein inneres Optimum — und damit überhaupt eine
Aussage, die sich mit neuen Daten ändern kann.

**Revisionspunkt.** `test_bei_kleiner_luecke_liegt_optimum_im_inneren`,
`test_grosse_luecke_fuehrt_zu_marktmiete`,
`test_umzugstraegheit_hilft_dem_vermieter`. Fällt das Optimum in allen Fällen
auf den Rand des Angebotsrasters, ist die Gegenkraft zu schwach parametrisiert.

---

## E18 {#e18}
### Portfolio-Fixpunkt mit Dämpfung statt Einmalrechnung
**Phase:** Modell

**Situation.** Wer fünfzig ähnliche Wohnungen gleichzeitig anbietet, ist sein
eigener Wettbewerber: die eigenen Angebote senken das Preisniveau, gegen das
sie gerechnet werden.

**Alternativen.**
1. Marktmiete als gegeben nehmen, Selbstkonkurrenz ignorieren.
2. Fixpunkt iterieren, bis Angebot und angenommenes Marktniveau zusammenpassen.

**Entscheidung.** Variante 2.

**Begründung.** (1) überschätzt den erzielbaren Preis genau dann, wenn viele
Verträge gleichzeitig auslaufen — also im Anwendungsfall.

**Was schiefging und wie es behoben ist.** Die erste Iteration pendelte
zwischen zwei Zuständen bis zum Abbruch nach der Höchstzahl an Runden. Mit
50/50-Dämpfung konvergiert sie in zwei Runden. Nicht-Konvergenz wird jetzt
gemeldet statt verschwiegen — ein stiller Abbruch nach `MAX_ITER` hätte ein
Zwischenergebnis als Ergebnis ausgegeben.

**Revisionspunkt.** Meldet der Lauf Nicht-Konvergenz, darf keine Vorlage
entstehen.

---

## E19 {#e19}
### PII-Logik in `clean.py`, Allowlist in `config.py` — ein Ort je Sache
**Datum:** 25.09.2026

**Situation.** Nach dem Umbau auf die vorgegebene Repository-Struktur gab es die
Allowlist zweimal: in `src/pii.py` und in `src/config.py`, mit identischem
Inhalt und zwei Prüffunktionen, die dasselbe taten.

**Alternativen.**
1. `pii.py` als Modul behalten, `config.py` importiert daraus.
2. `pii.py` auflösen: Allowlist und Verwerfungsgründe in `config.py`, Filter und
   Kontrollsuche in `clean.py` (Schritt 2, wo die Daten durchlaufen).

**Entscheidung.** Variante 2. `src/pii.py` entfernt, `redigiere_text` nach
`clean.py` übernommen.

**Begründung.** Zwei Fassungen derselben Liste laufen auseinander, sobald eine
gepflegt wird. Die Konfiguration gehört dorthin, wo auch Quellen, Bezirke und
Schwellen stehen; die Logik gehört in den Pipeline-Schritt, der sie anwendet.
`redigiere_text` bleibt, obwohl die Allowlist alle Freitextfelder verwirft — für
die unstrukturierten Quellen (Kollektivvertrags- und Gesetzestexte), die in den
LLM-Schritt gehen.

**Nebenbefund derselben Sitzung.** Gate 2 schlug bei einem eigenen technischen
Feld an: der Schnappschussname `wh_1020_…_2026-09-25T1555.json` traf das
Telefonmuster. Behoben durch Ausnahme **des Feldes** (`PII_UNVERDAECHTIG`), nicht
durch Aufweichen des Musters — ein lockereres Muster findet die echten Fälle
nicht mehr.

**Revisionspunkt.** `grep -rn "ERLAUBT" src/` darf genau eine Definition
finden.

---

## E20 {#e20}
### GitHub-Repository als gemeinsame Arbeitsfläche
**Datum:** 25.09.2026

**Situation.** Die Lehrveranstaltung verlangt ein Repository mit Historie und
Abgabe-Tags (`termin3`, `termin4`). Bisher lag das Projekt nur im
Arbeitsverzeichnis dieser Sitzung — das verfällt.

**Alternativen.**
1. Dateien als Anhang hin und her schicken, Nutzer committet selbst.
2. Repository auf GitHub, in dieser Sitzung freigegeben; ich committe und pushe
   direkt.
3. Lokales Git im Container ohne Fernkopie.

**Entscheidung.** Variante 2, mit (3) als sofortigem Zwischenschritt: das
lokale Repository ist angelegt und hat einen ersten Commit, damit die Historie
ab jetzt entsteht und nicht am Ende rekonstruiert wird.

**Begründung.** (1) erzeugt Commits ohne Bezug zu den Arbeitsschritten — genau
die „am Ende rekonstruierte" Historie, die die Bewertung abstraft. (3) allein
verfällt mit dem Container.

**Bedingung, die der Nutzer erfüllen muss.** Ein Push braucht das Repository in
den freigegebenen Quellen dieser Sitzung; die Zugangsdaten setzt der Proxy
dann selbst ein. Ein Token im Chat wäre ein Geheimnis im Klartext und wird
nicht verwendet.

**Revisionspunkt.** Wenn Commits nur zu Abgabeterminen entstehen, ist die
Historie wieder eine Rekonstruktion.

---

## E21 {#e21}
### Im Repository liegen redigierte Schnappschüsse, die Originale bleiben lokal
**Datum:** 25.09.2026

**Situation.** Unmittelbar vor dem ersten Push geprüft, was die gespeicherte
Seite eigentlich enthält. Zwei Funde: `dmpUserIdentities.wh_uuid` — eine Kennung
des Browsers, mit dem gespeichert wurde — und die vollständigen
Anbieterangaben inklusive Firmennamen mit Personennamen darin.

**Warum das dringend war.** Ein Push ist unumkehrbar. `git rm` entfernt eine
Datei aus dem Arbeitsstand, nicht aus der Historie; danach hilft nur noch
History-Rewrite, und in einem geteilten Repository auch das schlecht. Die
Vorgabe lautet: keine personenbezogenen Daten, nirgends.

**Alternativen.**
1. Repository privat halten und die Rohdatei unverändert committen.
2. Rohdaten nicht committen. Dann läuft `python3 -m src.run` im frischen Klon
   ins Leere — das Abnahmekriterium wäre nicht prüfbar.
3. Werte der nicht benötigten Felder durch `[ENTFERNT]` ersetzen, Struktur und
   Feldnamen erhalten, Originale lokal behalten.

**Entscheidung.** Variante 3 (`tools/redigiere_schnappschuss.py`).

**Begründung.** (1) verlagert eine Datenschutzfrage auf eine
Sichtbarkeitseinstellung; ein einziges Umschalten auf „public" macht sie wieder
auf, und für die Bewertung wäre ein Repository, das nur wegen seiner
Privatheit vorgabenkonform ist, keine gute Antwort. (2) kostet genau das, was
dieses Projekt auszeichnet: dass die Pipeline bei jedem nachvollziehbar läuft.
(3) behält Lauffähigkeit und Nachvollziehbarkeit und gibt nichts weiter.

Feldnamen bleiben absichtlich stehen. Sie belegen, was die Quelle liefert — und
damit, warum die Allowlist aus E11 nötig ist — ohne den Inhalt zu verbreiten.
`advertiserInfo.label` wird auf `Privat` / `[GEWERBLICH]` reduziert statt
entfernt, weil der Parser daraus eine Analysegröße gewinnt (der gewerbliche
Median liegt 16 % über dem privaten) und das Flag niemanden benennt.

**Beleg, dass nichts verlorenging.** Das Werkzeug prüft selbst, dass der Parser
aus beiden Fassungen dasselbe liest. Stärker noch: die fünf Kennzahl-CSV sind
vor und nach der Redaktion bit-identisch. Beide SHA256 stehen in
`data/raw/2026-09-25/HERKUNFT.md`.

**Preis dieser Entscheidung.** Wer die Rohdaten unabhängig nachprüfen will,
braucht das Original vom Menschen, der es gespeichert hat. Das ist der Preis,
und er wird benannt statt verschwiegen.

**Revisionspunkt.** Wenn eine neue Quelle Felder liefert, die
`tools/redigiere_schnappschuss.py` nicht kennt, werden deren Werte entfernt —
die Redaktion versagt also zur sicheren Seite. Kommt ein Feld hinzu, das die
Pipeline BRAUCHT, meldet die Selbstprüfung des Werkzeugs abweichende Lesung.

---

## E22 {#e22}
### `verticalId` ist die erste Prüfung in Gate 1
**Datum:** 25.09.2026

**Situation.** Gate 1 fing die Marktplatzdatei über Trefferzahl und
PLZ-Streuung ab — beides Indizien. Die Rubrikkennung `verticalId` lag in den
Daten, wurde aber nur vom Beschaffungsskript geprüft, nicht vom Gate.

**Alternativen.**
1. Bei den Indizien bleiben; sie haben im Vorfall funktioniert.
2. `verticalId` in den Schnappschuss aufnehmen und als erste Prüfung setzen.

**Entscheidung.** Variante 2.

**Begründung.** Die Indizien funktionierten zufällig gut: eine Marktplatzsuche
nach einem seltenen Begriff hätte eine plausible Trefferzahl und wenige PLZ —
und wäre durchgekommen. `verticalId` ist keine Ableitung, sondern die Aussage
des Portals selbst, um welche Rubrik es sich handelt. Eine Prüfung, die direkt
misst, gehört vor eine, die schließt.

**Revisionspunkt.** `test_gate_faengt_falsche_seite_ab` verlangt jetzt auch
den Befund „richtige Rubrik".

---

## E23 {#e23}
### `datenbeschaffung.md` wird die Schrittdokumentation, nicht ihr Nachbar
**Datum:** 25.09.2026

**Situation.** Die Lehrveranstaltung gibt `docs/projektdokumentation/02_schritt1_
datenzugriff.md` vor. Zum Datenzugriff existierte bereits `docs/
datenbeschaffung.md` mit Rechtslage, Vorfällen und PII-Abschnitt.

**Alternativen.**
1. Beides behalten: die Schrittdokumentation fasst zusammen und verweist.
2. Die bestehende Datei umbenennen und um das ergänzen, was der Schritt
   verlangt — Frage des Schritts, Abnahmekriterium, Quellentabelle.

**Entscheidung.** Variante 2, `git mv` samt Anpassung aller sechs Verweise.

**Begründung.** Zwei Dokumente zum selben Gegenstand laufen auseinander, sobald
eines gepflegt wird — dieselbe Erfahrung wie bei der doppelten Allowlist (E19).
Eine Zusammenfassung, die niemand nachzieht, ist schlechter als kein zweites
Dokument. `git mv` erhält zudem die Historie der Datei.

**Revisionspunkt.** Außerhalb dieses Logs darf der alte Dateiname nirgends
mehr vorkommen: `grep -rn "datenbeschaffung.md" --exclude=01_entscheidungslog.md`
bleibt leer.

---

## E24 {#e24}
### Claude bleibt Autor der Commits
**Datum:** 25.09.2026

**Situation.** Die Commits laufen auf `Claude <noreply@anthropic.com>`. Für eine
bewertete Abgabe war zu klären, wer als Autor erscheint.

**Alternativen.**
1. Der Studierende als Autor, Claude als `Co-Authored-By`. GitHub ordnet die
   Commits dann seinem Profil zu.
2. Claude als Autor, wie bisher.

**Entscheidung.** Variante 2, auf ausdrücklichen Wunsch.

**Begründung des Nutzers.** Nicht weiter ausgeführt; die Entscheidung liegt bei
ihm. Festzuhalten ist die Konsequenz: die Autorenzeile der Historie belegt
keinen eigenen Beitrag. Was von wem kam, ist stattdessen hier im
Entscheidungslog nachvollziehbar — die Themenwahl, die drei Wechsel, der
Zuschnitt auf den Vermieter, der Verzicht auf das Einkommensargument und die
Freigabe der dystopischen Prämisse sind Entscheidungen des Studierenden, nicht
Vorschläge des Modells.

**Revisionspunkt.** Umkehrbar für künftige Commits durch eine Änderung von
`user.name`/`user.email`; die bestehenden Commits blieben davon unberührt.

---

## E25 {#e25}
### `data/raw/` wird committet — begründete Abweichung von der Vorgabe
**Datum:** 25.09.2026

**Situation.** Die Vorgabe sagt zu Schritt 1: *„Im Repo danach: nichts.
`data/raw/` ist gitignored."* Im Beispielprojekt liegen die Quelldaten
stattdessen in `data/sample/` und sind committet — dort sind sie **synthetisch**
erzeugt (`src/synth/`). Unsere Schnappschüsse sind echte Marktdaten.

**Alternativen.**
1. Vorgabe wörtlich: `data/raw/` ignorieren. Dann läuft `python3 -m src.run` im
   frischen Klon ins Leere.
2. Die redigierten Schnappschüsse nach `data/sample/` verschieben, wie im
   Beispiel, und `data/raw/` ignorieren.
3. `data/raw/` mit den **redigierten** Fassungen committen, die unredigierten
   Originale ignorieren.

**Entscheidung.** Variante 3.

**Begründung.** (1) widerspricht der Vorgabe an anderer Stelle: Schritt 5
verlangt, *„das Repo in ein neues Verzeichnis zu klonen und nur der README zu
folgen"*. Ein Klon ohne Daten kann das nicht. (2) wäre die Vorgabe
buchstabengetreu, würde aber echte Daten als Beispieldaten ausweisen — im
Beispielprojekt heißt `data/sample/` „synthetisch erzeugt", und diese Bedeutung
zu überschreiben wäre eine Verschleierung der Herkunft. Der Ordnername ist eine
Aussage über die Daten.

Der Zweck des Vorgabesatzes ist erfüllt: der Grund für das Ignorieren von
`data/raw/` sind Personenbezug und Dateigröße. Beides trifft auf die redigierten
Fassungen nicht zu (E21, 494 kB). Die unredigierten Originale sind ignoriert.

**Revisionspunkt.** Landet je eine unredigierte Datei unter `data/raw/`, ist die
Entscheidung verletzt. Schutz: `tools/redigiere_schnappschuss.py` als Pflicht
vor dem Commit (CLAUDE.md, Regel 1) und die PII-Kontrolle in Gate 2.

---

## E26 {#e26}
### Die Datenbank wird committet, also darf keine Uhrzeit darin stehen
**Datum:** 25.09.2026

**Situation.** Die Vorgabe zu Schritt 3 verlangt, `data/processed/<projekt>.sqlite`
zu committen. Bisher war sie ignoriert, mit dem Argument aus E15: die Datenbank
ist ein Ergebnis, kein Quellbestand.

**Der Haken, der beim Prüfen auffiel.** `qs_befund` trug einen
`lauf_ts` aus `datetime.now()`. Eine committete Datenbank mit einer Uhrzeit darin
erzeugt bei **jedem** Lauf einen Diff — und widerlegt genau die Aussage, mit der
E15 begründet ist.

**Alternativen.**
1. Datenbank weiter ignorieren, entgegen der Vorgabe.
2. Datenbank committen und den Diff bei jedem Lauf hinnehmen.
3. Datenbank committen und die Uhrzeit entfernen: der Befund trägt den
   **Datenstand**, zu dem er gehört (`abruf_ts` des Schnappschusses).

**Entscheidung.** Variante 3. Spalte `lauf_ts` → `datenstand`.

**Begründung.** Der Nutzen der Vorgabe ist echt: wer das Repository bewertet,
kann die Datenbank mit DB Browser for SQLite öffnen, ohne etwas auszuführen.
(2) hätte diesen Nutzen mit Diff-Rauschen bezahlt und den Anspruch der
Reproduzierbarkeit unterlaufen. Der Zeitpunkt eines Qualitätsbefunds ist
inhaltlich ohnehin der Datenstand, nicht die Uhrzeit des Laufs — die Änderung
macht die Tabelle also auch richtiger.

E15 bleibt gültig: `data/raw/` ist die Quelle der Wahrheit, die Datenbank wird
bei jedem Lauf gelöscht und neu gebaut. Sie ist jetzt zusätzlich **byteweise**
dasselbe Ergebnis.

**Revisionspunkt.** `test_datenbank_ist_byteweise_reproduzierbar` baut die
Datenbank zweimal mit über einer Sekunde Abstand und vergleicht den SHA256.
Kommt je wieder ein Wert aus der Uhr in die Datenbank, fällt der Test.

---

## E27 {#e27}
### Je Aufgabe festgelegt: Programm oder Prompt
**Datum:** 09.10.2026

**Situation.** Die Vorgabe verlangt diese Festlegung ausdrücklich je Aufgabe.
Bisher stand sie verstreut in einzelnen Entscheidungen (E11, E16).

**Alternativen.**
1. Alles, was ein Sprachmodell kann, dem Modell geben — es ist schneller.
2. Alles selbst programmieren — es ist prüfbar.
3. Je Aufgabe entscheiden, nach einem Kriterium.

**Entscheidung.** Variante 3. Das Kriterium: **was prüfbar sein muss, gehört in
Code; was Sprache ist, gehört ins Modell.**

| Aufgabe | Werkzeug | Warum |
|---|---|---|
| Schnappschuss auslesen | Programm (`wh_next_data.py`) | deterministisch, testbar gegen eine eingecheckte Datei |
| Eingangsprüfung (richtige Seite?) | Programm (`validierung.py`) | eine Prüfung, die ein Modell macht, kann man nicht als Gate verwenden |
| Personenbezug entfernen | Programm (`clean.py` + Allowlist) | ein Prompt ist eine Bitte, keine Zusicherung — und nicht testbar |
| Kennzahlen rechnen | SQL (`kennzahl_*.sql`) | jede Zahl der Vorlage muss ihre Abfrage nennen können |
| Entscheidungsmodell | Programm (`entscheidung.py`) | Barwerte und Wahrscheinlichkeiten sind Arithmetik, kein Sprachproblem |
| Felder aus Kollektivvertragstexten ziehen | **Prompt** | unstrukturierter Fließtext, wechselnde Formulierungen — genau das, was ein Modell besser kann als ein regulärer Ausdruck |
| Entscheidungsvorlage formulieren | **Prompt** | Sprache. Die Zahlen kommen aus der Tabelle, der Text vom Modell |

**Begründung.** (1) verliert die Prüfbarkeit, die dieses Projekt tragen soll:
ein Modell, das den PII-Filter macht, lässt sich nicht als Gate verwenden, weil
sein Ergebnis nicht reproduzierbar ist. (2) scheitert an den
Kollektivvertragstexten — wechselnde Formulierungen („um 2,55 Prozent",
„sozial gestaffelt zwischen 3,1 und 2,7 Prozent") sind mit regulären Ausdrücken
nicht sinnvoll zu fassen, und genau dort liegt der Nutzen eines Modells.

**Revisionspunkt.** Sobald eine Zahl in der Entscheidungsvorlage steht, die
keine Abfrage nennt, ist die Grenze verletzt. Dafür ist ein Judge-Eval
vorgesehen, das prüft, dass im Text keine Zahl vorkommt, die nicht in der
Tabelle steht.

---

## E28 {#e28}
### Keine Extraktionsreferenzen ohne das Quelldokument
**Datum:** 09.10.2026

**Situation.** Deliverable 2 verlangt mindestens acht Referenzfälle für
Extraktion oder Klassifikation. Welche Fälle es sind, steht fest: die sieben
Berufsgruppen aus `config/berufsgruppen.json` plus den öffentlichen Dienst. Die
Abschlüsse stehen auf öffentlichen Seiten von ÖGB und WKO.

**Der Haken.** Mein eigener Zugriff auf diese Seiten liefert eine
**Zusammenfassung durch ein Sprachmodell**, nicht den Wortlaut der Seite. Die
Zahlen darin sind plausibel und vermutlich richtig — aber sie sind nicht der
Quelltext.

**Alternativen.**
1. Die acht Fälle aus der Modellrecherche bilden und die Quelle verlinken.
   Deliverable 2 wäre damit formal vollständig.
2. Die Fälle offen lassen, die Beschaffung dokumentieren und benennen, warum
   sie offen sind.

**Entscheidung.** Variante 2.

**Begründung.** Eine Referenzantwort aus einer Modellzusammenfassung prüft das
Modell gegen sich selbst. Genau dieser Fehler ist in einer früheren
Projektfassung passiert (E02): das Goldset war aus Suchtreffer-Ausschnitten
rekonstruiert, das Eval maß die eigene Formulierung, und die Trefferquote sah
gut aus. Denselben Fehler zweimal zu machen, nachdem er protokolliert ist, wäre
schlechter als eine offene Stelle in der Abgabe.

Es ist zudem derselbe Fall wie bei den Inseratsdaten, und die Antwort ist
dieselbe: ein Mensch speichert die Seite, die Pipeline verarbeitet sie (E06).
Die Anleitung dafür steht in `evals/references/README.md`.

**Was stattdessen geliefert wird.** Acht numerische Referenzfälle mit Herkunft,
Prüfregel, Toleranz und Unsicherheit, dazu drei ausgewiesene Handproben. Die
Extraktionsfälle gehören zu Deliverable 3, Termin 23.10.

**Revisionspunkt.** Liegt die gespeicherte Seite vor, werden die acht Fälle
wörtlich daraus erfasst — mit Fundstelle, und `rohtext` enthält den kopierten
Satz, nicht eine Nachschrift.

---

## E29 {#e29}
### Der Auftrag bleibt nach dem Pitch unverändert
**Datum:** 09.10.2026

**Situation.** Pitch im Gallery Walk am 26.09.2026. Das Feedback war
durchgehend positiv; keine Rückmeldung stellte Adressat, Entscheidung oder
Analysen in Frage.

**Alternativen.**
1. Scope oder Analysen nachschärfen, etwa eine vierte Kennzahl aufnehmen.
2. Den Auftrag unverändert lassen und die Zeit in die offenen Punkte stecken.

**Entscheidung.** Variante 2.

**Begründung.** Es gab keinen Befund, der eine Änderung verlangt hätte. Die
offenen Punkte — vier fehlende Bezirke, die Indexreihen, die
Extraktionsreferenzen (E28) — sind Datenlücken, keine Zuschnittsfragen.
Vermerkt in `00_auftrag.md` unter „Änderungen seit dem Pitch".

**Revisionspunkt.** Wenn bis Termin 4 ein Bezirk nicht beschafft werden kann,
muss Analyse 1 auf die vorhandenen Bezirke eingeschränkt werden — das wäre
dann eine Scope-Änderung mit eigenem Eintrag.

---

## E30 {#e30}
### Der Projektstand liegt entpackt im Repository, nicht als ZIP
**Datum:** 09.10.2026

**Situation.** E20 sah vor, dass die Historie ab dem ersten Commit entsteht.
Tatsächlich lag bis zum 09.10. nur ein Upload über die GitHub-Oberfläche im
Repository: `README.md` und eine ZIP-Datei mit dem Stand vom 25.09. Der
Revisionspunkt von E20 („Commits nur zu Abgabeterminen") ist damit
eingetreten, und das wird hier nicht beschönigt.

**Alternativen.**
1. ZIP belassen und nur aktualisieren.
2. ZIP entfernen, Stand entpackt committen, jede Korrektur als eigener Commit.

**Entscheidung.** Variante 2.

**Begründung.** Ein ZIP ist für die Bewertung nicht lesbar und zeigt keine
Arbeitsschritte. Die Historie vor dem 09.10. lässt sich nicht nachträglich
herstellen, ohne sie zu erfinden — deshalb steht die Abfolge der
Entscheidungen in diesem Log mit Datum, und die Historie beginnt ehrlich
mit dem Entpacken.

**Revisionspunkt.** Bis Termin 4 entsteht je abgeschlossener Arbeitseinheit
ein Commit. Liegen zwischen 9.10. und 23.10. nur Commits am Abgabetag, ist
die Entscheidung gescheitert.

---

## E31 {#e31}
### Der Studierende ist Autor der Commits, Claude Co-Autor
**Datum:** 09.10.2026 · revidiert E24

**Situation.** E24 hatte Claude als Autor festgelegt. Mit dem ersten Commit
aus der Arbeitssitzung war die Frage erneut zu entscheiden.

**Alternativen.**
1. Claude bleibt Autor (E24).
2. Der Studierende als Autor, Claude als `Co-Authored-By`.

**Entscheidung.** Variante 2, auf ausdrücklichen Wunsch des Studierenden.

**Was die Autorenzeile belegt und was nicht.** Code und Dokumentation sind
zum großen Teil von Claude formuliert. Die Autorenzeile belegt deshalb, wer
die Arbeit freigegeben und eingereicht hat, nicht wer jede Zeile geschrieben
hat. Wer was entschieden hat, steht wie bisher in diesem Log (vgl. E24).

**Revisionspunkt.** Verlangt die Lehrveranstaltung eine andere Kennzeichnung
von KI-Beiträgen, wird sie für künftige Commits übernommen.

---

## E32 {#e32}
### Alle Seiten einer PLZ an einem Tag sind ein Abruf
**Datum:** 09.10.2026

**Situation.** Am 09.10. wurde 1020 vollständig gespeichert, als Seite 1
(17:45) und Seite 2 (17:47). Die Pipeline kannte nur Schnappschüsse, also
Dateien. Folgen: Jede Seite trug eine Teilseiten-Warnung, obwohl zusammen
178 von 178 Treffern vorlagen, und `v_inseratsdauer` hielt alle 90 Inserate
von Seite 1 für verschwunden, weil Seite 2 zwei Minuten später lag.

**Alternativen.**
1. Jede Seite bleibt ein eigener Abruf; Seiten nur in Abständen von Tagen
   speichern.
2. Seiten beim Einlesen zu einer Datei zusammenfügen.
3. Seiten bleiben eigene Schnappschüsse; ein Abruf ist die Gruppe aller
   Seiten einer PLZ an einem Tag (`v_abruf`).

**Entscheidung.** Variante 3.

**Begründung.** (1) macht eine Regel aus einem Fehler. (2) verwischt die
Herkunft: Jede Datei hat ihren eigenen SHA256 und ihr eigenes Gate-Ergebnis,
eine zusammengefügte Datei hätte keines davon. (3) lässt die Faktentabelle
unverändert und definiert den Abruf dort, wo er gebraucht wird. Ein Inserat,
das zwischen zwei Seitenaufrufen die Seite wechselt, zählt in `v_angebot`
trotzdem nur einmal.

**Revisionspunkt.** `test_seiten_eines_tages_sind_ein_abruf`,
`test_zensiert_heisst_im_letzten_abruf_noch_online`. Werden je Tag zwei
Abrufe derselben PLZ gebraucht (morgens, abends), ist die Tagesgrenze zu grob.

---

## E33 {#e33}
### WG-Zimmer gehören nicht ins Wohnungsangebot
**Datum:** 09.10.2026

**Situation.** Unter den Inseraten vom 09.10. standen zwei vom Objekttyp
`Zimmer/WG`. Eines davon: 699 € für ein möbliertes Zimmer, Fläche 100 m² —
die der ganzen Wohnung. Das ergibt 6,99 €/m² im Zielsegment und zog
Minimum und erstes Quartil nach unten.

**Alternativen.**
1. Behalten: Es ist ein Mietinserat in 1020.
2. Beim Einlesen in `clean.py` verwerfen.
3. In der Faktentabelle behalten, aus `v_angebot` ausschließen, Liste mit
   Grund in der Konfiguration und in der Datenbank.

**Entscheidung.** Variante 3. Ausgeschlossen sind heute 2 Beobachtungen.

**Begründung.** (1) mischt einen Zimmerpreis mit einer Wohnungsfläche — der
Quotient misst nichts. (2) wäre ein unsichtbarer Filter: keine Zeile, kein
Zähler, kein Grund. (3) hält die Beobachtung, nennt den Grund in
`objekttyp_ausschluss` und meldet die Zahl bei jedem Lauf. Am 25.09. gab es
keine WG-Zimmer; Referenzantworten und Handproben sind unberührt.

**Revisionspunkt.** `test_wg_zimmer_sind_kein_wohnungsangebot`. Taucht ein
weiterer Objekttyp auf, dessen Fläche nicht zur Miete gehört, gehört er in
dieselbe Liste — mit eigenem Grund.

---

## E34 {#e34}
### Gemeindewohnungen im Angebot: per Prompt klassifizieren
**Datum:** 09.10.2026 · **Status: entschieden, Variante 3**

**Situation.** Am 09.10. standen mehrere Gemeindewohnungen im Angebot:
Direktvergaben von Wiener Wohnen und eine Weitergabe „mit Wohnticket", alle
privat inseriert, zu 7,50–10 €/m². Für einen institutionellen Vermieter von
Neubauwohnungen sind das keine Vergleichsmieten — sie sind reguliert und an
Zugangsvoraussetzungen gebunden. Erkennbar sind sie nur am Titel, und den
verwirft die Allowlist (E11), weil Freitexte Namen tragen können.

**Alternativen.**
1. Behalten und als bekannte Verzerrung nach unten benennen.
2. Per Schlagwort im Titel ausschließen („Gemeinde", „Wiener Wohnen",
   „Wohnticket"), bevor der Titel verworfen wird — nur das Ergebnis, ein
   Flag, geht in die Datenbank.
3. Titel per Prompt klassifizieren lassen und gegen händisch markierte Fälle
   prüfen — eine Klassifikationsaufgabe mit Referenzantworten.

**Entscheidung.** Variante 3, auf Wunsch des Studierenden. Bis die Klassifikation
läuft, gilt (1): Im Zielsegment 80–100 m² liegt nur ein Inserat unter 13 €/m²,
der Median ist davon kaum berührt. Die Referenz entsteht nach E37.

**Was die Entscheidung abhängig macht.** (2) ist schnell und prüfbar, aber
ein Schlagwort, das fehlt, lässt den Fall durch. (3) wäre die erste echte
Prompt-Aufgabe an den Inseratsdaten und würde die fehlende
Klassifikationsreferenz (E28) liefern — kostet aber händische Markierung.

**Revisionspunkt.** Zeigt ein Abruf im Zielsegment mehr als zwei
Gemeindewohnungen, ist (1) nicht mehr haltbar.

---

## E35 {#e35}
### Die Quelltextansicht ist der empfohlene Beschaffungsweg
**Datum:** 09.10.2026

**Situation.** Der erste Abruf am 09.10. lieferte zweimal die Startseite
statt der Suche (Vorfall 2 in `02_schritt1_datenzugriff.md`). Im gerenderten
HTML derselben Dateien standen die Inserate korrekt, das `__NEXT_DATA__` war
aber veraltet.

**Alternativen.**
1. Die Inserate aus dem gerenderten HTML lesen.
2. Bei `tools/snapshot.js` bleiben und die Anleitung schärfen.
3. Die Quelltextansicht (`view-source:`) als ersten Weg empfehlen,
   `snapshot.js` als Alternative mit Selbstprüfung.

**Entscheidung.** Variante 3.

**Begründung.** (1) würde Preise und Flächen aus generierten CSS-Klassen
lesen — genau das hat E07 verworfen —, und Rubrik, Trefferzahl und
Abrufzeitpunkt fehlen dort, also alles, was Gate 1 prüft. (2) verlässt sich
auf eine Anleitung, die schon einmal nicht gereicht hat (E09). Die
Quelltextansicht holt die Seite immer vom Server; der Fehler kann dort nicht
entstehen. Der Parser liest die gespeicherte Ansicht direkt. Im privaten
Fenster landen zudem keine Kontodaten in der Datei.

**Revisionspunkt.** Scheitert ein über `view-source:` gespeicherter Abruf an
Gate 1, stimmt die Begründung nicht.

---

## E36 {#e36}
### Ungemessene Abgänge zählen nicht als null Tage
**Datum:** 09.10.2026

**Situation.** Mit zwei Abrufen stand `mittel_tage_abgeschlossen` auf 0,0.
Grund: 27 Inserate waren nur am 25.09. zu sehen. Sie sind irgendwann in den
14 Tagen danach verschwunden; die Abfrage zählte sie mit 0 Tagen.

**Alternativen.**
1. So lassen und im Kommentar erklären.
2. Mittelwert nur über Inserate, die in mindestens zwei Abrufen standen und
   danach fehlen; die übrigen als `abgaenge_ungemessen` zählen.
3. Zusätzlich den Anteil der älteren Inserate ausweisen, der im jüngsten
   Abruf noch steht.

**Entscheidung.** Variante 2 und 3 zusammen.

**Begründung.** Eine unbekannte Dauer ist nicht null, und ein Mittelwert von
0,0 würde in der Vorlage als Messwert gelesen. Mit zwei Abrufen gibt es noch
keinen Abgang mit gemessener Dauer — der Mittelwert ist deshalb leer, und
`befund` sagt das. Was schon belastbar ist: 70 % der Inserate vom 25.09.
stehen am 09.10. noch. Ein typisches Inserat steht also länger als zwei
Wochen. Für die Leerstandsannahme ist das eine Untergrenze, kein Schätzwert.

**Revisionspunkt.** `test_ungemessene_abgaenge_zaehlen_nicht_als_null_tage`.
Ab dem dritten Abruf muss `mittel_tage_abgeschlossen` gefüllt sein, sonst
fehlt der Abruf oder die Abfrage ist falsch.

---

## E37 {#e37}
### Die Referenz zur Titelklassifikation markiert der Studierende selbst
**Datum:** 09.10.2026

**Situation.** Für E34 (Variante 3) braucht die Klassifikation eine
Referenzantwort, die vor dem Modell existiert. Die erste ausgefüllte Markierliste
(178 Titel) stammte, wie sich auf Nachfrage zeigte, von einem Sprachmodell. Sie
war formal einwandfrei: ad_id und Titel stimmten mit der Vorlage überein, die
Regeln waren nachvollziehbar.

**Befunde an dieser Liste.**
- Das Label „unklar" beruhte auf dem Preis (Privatanbieter unter 15 €/m²),
  nicht auf dem Titel. Ein Modell, das nur den Titel sieht, kann es nicht
  treffen.
- Nur 3 von 178 Titeln waren „ja", alle mit ausdrücklichem Stichwort
  (Gemeindebau, Wiener Wohnen, Gemeindewohnung). Eine Stichwortsuche findet
  sie alle; „immer nein" erreicht 98 % Trefferquote.
- Die Spalte „Personenname" war auf Projekt- und Firmennamen ausgeweitet,
  Blueground und Marina Tower blieben außen vor — uneinheitlich.

**Alternativen.**
1. Die Modellmarkierung als Referenz übernehmen, mit Vermerk.
2. Der Studierende markiert selbst, auf einer neuen Liste ohne Preise und
   ohne Vorbefüllung, in anderer Reihenfolge.

**Entscheidung.** Variante 2. Die Modellmarkierung bleibt außerhalb des
Repositories und dient höchstens als Testfall für den Ablauf der Auswertung —
nie als Maßstab für die Qualität eines Modells.

**Begründung.** Eine Referenz aus einer Modellmarkierung misst, wie sehr zwei
Modelle sich ähneln, nicht ob eines recht hat. Das ist derselbe Fehler wie in
E02 und E28; er ist hier bei der Prüfung aufgefallen, bevor er im Repository
stand. Die neue Liste zeigt nur den Titel, weil ein Modell später auch nur den
Titel sieht. Als zweite Spalte steht „möbliert / Kurzzeit" (optional): sie hat
deutlich mehr Treffer und ist sprachlich unschärfer — Blueground allein stellt
18 der 178 Inserate. Eine dritte Spalte „Person im Titel" bestimmt, welche
Titel ins Repository dürfen (Regel 1 in `CLAUDE.md`).

**Offen.** Wie „unklar" gewertet wird: Vorschlag ist, diese Fälle aus der
Trefferquote zu nehmen und getrennt auszuweisen.

**Revisionspunkt.** Stimmt die Markierung des Studierenden in mehr als einem
Fall nicht mit dem Titel überein, den ein zweiter Mensch lesen würde, ist die
Regel zu unscharf. Eine zweite Person für eine Stichprobe würde das messbar
machen.

