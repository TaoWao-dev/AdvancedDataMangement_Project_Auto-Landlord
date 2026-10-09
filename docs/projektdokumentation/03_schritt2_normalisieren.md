# Schritt 2 — Auslesen und normalisieren

**Frage dieses Schritts:** je Quelle eine saubere Tabelle — gleiche Typen,
gleiche Schreibweisen, keine Duplikate, keine Personenspalten.

**Abnahmekriterium:** `python3 -m src.run` läuft zweimal durch und meldet beide
Male dieselben Zahlen. Geprüft am 9.10.2026, zusätzlich als Test
(`test_zweiter_lauf_liefert_dieselben_zahlen`, `test_datenbank_ist_byteweise_
reproduzierbar`).

## Die Zahlen aus dem Lauf

Wörtlich aus der Ausgabe von `python3 -m src.run`, Lauf vom 9.10.2026 mit
beiden Abrufen (25.09. und 09.10.):

```
extract: 3 Datei(en) aus 2 Rohordner(n) -> data/interim/
         willhaben: 3
clean willhaben: 3 Schnappschuss/e aufgenommen, 0 abgelehnt, 268 Inserate;
                 1 ohne Flaeche, 14 reserviert, 1 unvollstaendige(r) Abruf(e);
                 1 Feld(er) als PII verworfen (seo_url)
clean tariflohnindex: keine Datei vorhanden - uebersprungen
clean vpi: keine Datei vorhanden - uebersprungen
```

| Quelle | gelesen | aufgenommen | abgelehnt | geändert | fehlend | PII-Felder verworfen |
|---|---:|---:|---:|---:|---:|---:|
| willhaben | 268 Beobachtungen aus 3 Dateien | 268 | 0 | Zeitstempel-Versatz aller 3 Dateien (`+0200` → `+02:00`), sonst kein Wert | 1 ohne Fläche | 13 Feldnamen, davon 1 im Parser belegt (`seo_url`) |
| Tariflohnindex | — | — | — | — | **ganze Quelle** | — |
| VPI | — | — | — | — | **ganze Quelle** | — |

Zur Spalte „geändert": korrigiert wird **ein** Format, kein Wert. willhaben
schreibt den Zeitzonenversatz ohne Doppelpunkt; SQLite liest das nicht, und
jede Inseratsdauer war deshalb still leer (Korrektur `c679e95`, gefunden erst
mit dem zweiten Abruf). Zahlen werden umgewandelt (Text → Zahl), aber nichts
wird geglättet, ersetzt oder geschätzt. Ein fehlender Wert bleibt `NULL`.

**Duplikate:** innerhalb eines Abrufs keine — 90 verschiedene `ad_id` am
25.09., 178 am 09.10., Seite 1 und 2 ohne Überschneidung. Über die Abrufe
hinweg sind Wiederholungen gewollt: 268 Beobachtungen von 205 Inseraten, 63
davon an beiden Tagen. Die Faktentabelle ist append-only (E13), weil genau
daraus Preisänderung und Inseratsdauer messbar werden. Sollte ein Inserat
doch auf zwei Seiten desselben Abrufs stehen, zählt `v_angebot` es einmal
(E32).

**Ausgeschlossen:** 2 Beobachtungen vom Typ `Zimmer/WG` (E33). Sie bleiben in
der Faktentabelle und fehlen nur im Angebot; `integrate` meldet die Zahl bei
jedem Lauf.

## Qualitätsbericht, sechs Fragen je Quelle

### willhaben Mietinserate (1020 Wien, 25.09.2026, 15:55)

| Frage | Befund | Konsequenz |
|---|---|---|
| **Vollständig?** | **Nein.** 90 von 154 Treffern — die gespeicherte Seite zeigt die erste Seite der Suche. Vier von fünf Bezirken fehlen ganz. | Warnung im Qualitätsbericht, nicht Abbruch. Der Median beschreibt die erste Seite, nicht den Markt — das steht im Kennzahl-Kommentar und in jeder Auswertung dabei. `v_abdeckung` weist die vier fehlenden Bezirke als „noch nicht beschafft" aus. |
| **Korrekt?** | Kreuzprobe bestanden: das vom Portal gelieferte `PRICE/SQUARE_METER` stimmt in allen 86 prüfbaren Fällen mit `PRICE / ESTATE_SIZE` überein (Abweichung < 0,02). Der Größengradient — kleinere Wohnungen teurer pro m² — entspricht der Literatur. | Als Test festgeschrieben (`test_eur_pro_m2_des_portals_stimmt_mit_eigener_rechnung`) und als Gate-3-Prüfung. Ändert das Portal eine Feldbedeutung, fällt der Test, nicht die Zahl. |
| **Konsistent?** | `ISPRIVATE` und `advertiserInfo.label` widersprechen sich in **0 von 90** Fällen. Alle 90 Inserate tragen dieselbe PLZ. | Die Unterscheidung privat/gewerblich ruht damit auf zwei übereinstimmenden Feldern. Die PLZ-Einheitlichkeit ist Gate-1-Prüfung mit Schwelle 90 %. |
| **Aktuell?** | Abruf 25.09.2026, 15:55 — Zeitstempel aus der Serverantwort (`searchDate`), nicht von der Uhr des Rechners. Zum Abgabetag ist der Stand **14 Tage alt**. | Für ein Inseratsportal ist das grenzwertig: Angebote wechseln wöchentlich. Jede Kennzahl trägt `abruf_datum` in der Zeile. Vor der Entscheidungsvorlage gehört ein frischer Schnappschuss her. |
| **Wem gehört sie?** | willhaben internet service GmbH & Co KG. Keine offene API, `robots.txt` untersagt automatisierten Zugriff. | Manuelle Beschaffung durch einen Menschen, automatisierte Verarbeitung danach (E06). Die `robots.txt` ist als `docs/willhaben_robots_2026-09-25.txt` archiviert. |
| **Woher kommt sie?** | `__NEXT_DATA__` einer serverseitig gerenderten Next.js-Suchseite, im Browser gespeichert. SHA256 beider Fassungen in `data/raw/2026-09-25/HERKUNFT.md`. | Provenienz je Datei in `data/interim/provenienz.json`. Ein wiederkehrender SHA256 löst eine Warnung aus — genau der Fall, der dreimal passiert ist (E09). |

### willhaben Mietinserate (1020 Wien, 09.10.2026, 17:45 und 17:47)

| Frage | Befund | Konsequenz |
|---|---|---|
| **Vollständig?** | **Ja.** Seite 1 mit 90 und Seite 2 mit 88 Inseraten, zusammen 178 von 178 Treffern, ohne Überschneidung. Vier Bezirke fehlen weiterhin. | Seiten eines Tages gelten als ein Abruf (`v_abruf`, E32); die Teilseiten-Warnung fällt nur für vollständige Abrufe weg. |
| **Korrekt?** | Kreuzprobe Portal-€/m² gegen Miete/Fläche: 178 von 178 prüfbar, 0 Abweichungen. **Aber:** zwei WG-Zimmer (Zimmerpreis auf Wohnungsfläche, bis 6,99 €/m²) und mehrere Gemeindewohnungen (Direktvergaben, 7,50–10 €/m²). | WG-Zimmer ausgeschlossen (E33). Gemeindewohnungen sind am Titel erkennbar, den die Allowlist verwirft — **offene Entscheidung** (E34). |
| **Konsistent?** | `ISPRIVATE` und `advertiserInfo.label` widersprechen sich in 0 von 178 Fällen. Alle 178 Inserate PLZ 1020. | wie am 25.09. |
| **Aktuell?** | Abruf 09.10.2026, laut `searchDate`. | Der Abgabestand ist am Tag der Abgabe aktuell. Der Vergleich mit dem 25.09. ist durch dessen Teilseite verzerrt: Der Median im Zielsegment sinkt von 26,67 auf 24,01 €/m², aber am 25.09. fehlen 64 von 154 Inseraten. Kein Markttrend ablesbar. |
| **Wem gehört sie?** | wie am 25.09. | — |
| **Woher kommt sie?** | gespeicherte `view-source:`-Ansicht, `__NEXT_DATA__` daraus extrahiert. Erster Versuch lieferte die Startseite (Vorfall 2 in `02_schritt1_datenzugriff.md`). | SHA256 beider Fassungen in `data/raw/2026-10-09/HERKUNFT.md`. |

### Tariflohnindex und VPI (Statistik Austria, OGD)

| Frage | Befund | Konsequenz |
|---|---|---|
| Vollständig? | **Nicht beschafft.** `clean` meldet „keine Datei vorhanden — übersprungen". | `indexreihe` ist leer, und der Test erlaubt das ausdrücklich für genau diese Tabelle, mit Begründung im Code. Die Fortschreibung der Mieten und Einkommen ist damit heute **nicht** datengestützt. |
| Korrekt / konsistent | offen | Vor der Verwendung: Reihennamen zeichengenau gegen die amtliche Klassifikation abgleichen. `config/berufsgruppen.json` trägt die erwarteten Namen und den Hinweis dazu. |
| Aktuell | offen | — |
| Wem gehört sie? | Statistik Austria, CC-BY 4.0 | automatisierter Abruf erlaubt — anders als bei der Inseratsquelle |
| Woher? | `data.statistik.gv.at` | `QUELLEN` in `src/config.py`, `pflicht: false` |

**Der wichtigste bekannte Mangel dieser Quelle** steht schon fest, bevor sie da
ist: Der Tariflohnindex misst **Mindestlöhne nach Kollektivvertrag**, nicht
Ist-Löhne einschließlich Überzahlung. Bei IT-Berufen — 24 % des unterstellten
Portfolios — ist er deshalb eine Untergrenze, im öffentlichen Dienst ein guter
Schätzer. Der Unschärfegrad steht je Berufsgruppe in
`config/berufsgruppen.json` und gehört in die Entscheidungsvorlage.

## Die Umwandlungsentscheidungen

Sie stehen zusammen am Anfang von `src/clean.py`, weil eine falsch entschiedene
Umwandlung unauffällig aussieht: keine Zeile fällt aus, die Zahl ist nur falsch.

| Funktion | Entscheidung | Was sonst passiert wäre |
|---|---|---|
| `to_number` | Ein Punkt gilt **nur** dann als Tausendertrenner, wenn im selben Wert auch ein Komma vorkommt. | willhaben liefert `24.791666` als Dezimalpunkt. Das übliche `.replace(".", "")` hätte daraus 24 791 666 gemacht — ein Wert, der jeden Median zerlegt, ohne eine Fehlermeldung auszulösen. |
| `to_number` | Nachgestelltes Minus (`0,76-`) wird als negativ gelesen. | In österreichischen Abrechnungen übliche Schreibweise für Abzüge; sonst wäre der Wert verworfen worden. |
| `to_date` | **Tag zuerst.** `04.06.2025` ist der 4. Juni. | Monat zuerst ergäbe den 6. April — ein Fehler, der nur bei Tagen über 12 auffällt und sich bis dahin leise in jede Zeitreihe schreibt. |
| `normalize_plz` | vierstellige Zahl aus dem Feld, sonst `NULL` | Ein Text wie „1020 Wien, Leopoldstadt" wäre als Schlüssel unbrauchbar und hätte jede Gruppierung gesprengt. |
| Lückenwerte | `-777`, `-999`, `-9999` und `#BEZUG!`, `-`, leer werden zu `NULL` | Behördliche Datensätze kodieren Lücken als Zahlen. Ungeprüft wäre −999 € als Miete in den Mittelwert gewandert. |

## Die PII-Entscheidung

**Allowlist, nicht Blocklist. Im Code, nicht im Prompt.**

| | |
|---|---|
| Stelle im Code | `src/config.py` → `PII_ERLAUBT` (18 Felder) und `PII_VERWORFEN` (13 Felder mit Begründung); angewandt in `src/clean.py` → `drop_pii()` |
| Letzte Kontrolle | `src/clean.py` → `pii_kontrolle()`, sucht Kontaktmuster in **allen** Werten vor dem Schreiben. Ein Treffer ist ein Fehler, keine Warnung — dann stimmt die Allowlist nicht. |
| Verworfen werden | `ORGNAME`, `advertiserInfo`, `ORGID`, `ORG_UUID`, `ADVERTISER_REF`, `seo_url`, `BODY_DYN`, `description`, `HEADING`, `COORDINATES`, `ADDRESS`, `ALL_IMAGE_URLS`, `MMO` |
| Behalten wird von der Anbieterseite | **nur** `ISPRIVATE` — privat oder gewerblich ist eine Analysegröße (der gewerbliche Median liegt 16 % über dem privaten) und benennt niemanden |

**Warum Allowlist:** eine Blocklist lässt jedes neue Feld der Quelle
stillschweigend durch. Die Richtung ist falsch. Mit einer Allowlist fällt ein
unbekanntes Feld heraus und wird dabei gezählt — es fällt also auf.

**Warum nicht im Prompt:** ein Prompt ist eine Bitte, keine Zusicherung, und
nicht testbar. Die Allowlist hat zwei Tests (`test_allowlist_verwirft_
anbieterdaten`, `test_kein_pii_in_bereinigten_zeilen`) und einen, der die
gebaute Datenbank auf verbotene Spaltennamen prüft.

**Zwei Vorfälle, die hierher gehören.**

Erstens ein **Fehlalarm**: Gate 2 schlug beim eigenen Schnappschussnamen an
(`wh_1020_mietwohnungen_2026-09-25T1555.json` traf das Telefonmuster). Behoben
durch Ausnahme des **Feldes** (`PII_UNVERDAECHTIG`), nicht durch Lockern des
Musters — ein lockeres Muster findet die echten Fälle nicht mehr.

Zweitens ein **Fund außerhalb der Tabellen**: die gespeicherte Seite enthält
`dmpUserIdentities.wh_uuid`, eine Kennung des Browsers, mit dem gespeichert
wurde. Die Pipeline liest sie nie — aber die Rohdatei trägt sie weiter, und eine
Git-Historie ist unumkehrbar. Konsequenz: `tools/redigiere_schnappschuss.py`
reduziert die Datei vor dem Commit; Feldnamen bleiben, Werte nicht benötigter
Felder werden `[ENTFERNT]`. Beleg, dass dabei kein Ergebnis verlorenging: die
fünf Kennzahl-CSV sind vor und nach der Redaktion bit-identisch (E21).

## Zwei Dinge, die hier bewusst nicht passieren

**Keine Ausreißerbereinigung.** Im Zielsegment steht ein Inserat mit
37,04 €/m², im Segment 50–80 m² eines mit 7,51 €/m². Beides bleibt drin.
Statt zu löschen weist die Auswertung Median und Quartile aus — der Median ist
gegen Ausreißer robust, und ein gelöschter Ausreißer ist eine Entscheidung, die
später niemand mehr sieht.

**Keine Imputation.** Die Wohnung ohne Flächenangabe fehlt in allen
flächenbezogenen Kennzahlen und wird in der Fallzahl mitgezählt: 90 Inserate,
86 in der Analysebasis (3 reserviert, 1 ohne Fläche). Die Differenz ist
nachvollziehbar statt weggerechnet.
