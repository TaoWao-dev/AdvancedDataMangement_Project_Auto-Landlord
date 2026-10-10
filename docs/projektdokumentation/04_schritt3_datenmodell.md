# Schritt 3 — Datenmodell und Datenbank

**Frage dieses Schritts:** eine Tabelle je Entität, ein Schlüssel je Tabelle,
Quellen über Schlüssel verknüpft — und was keinen Partner findet, wird gezählt
statt verworfen.

**Abnahmekriterium:** `python3 tests/test_pipeline.py` ist grün (45 Tests,
darunter zweiter Lauf identisch, keine doppelten Schlüssel, alle Tabellen
vorhanden) und keine Zeile ist unerklärt ohne Zuordnung.

## Starten und prüfen

```bash
python3 -m src.run                 # baut data/processed/mietportfolio.sqlite neu
python3 tests/test_pipeline.py     # 45 Tests
sqlite3 data/processed/mietportfolio.sqlite "SELECT * FROM v_abdeckung;"
```

Die Datenbank liegt committet im Repository und lässt sich ohne Lauf mit
*DB Browser for SQLite* öffnen. Sie ist byteweise reproduzierbar: zwei Läufe
erzeugen dieselbe Datei, geprüft über SHA256 mit mehr als einer Sekunde Abstand
(`test_datenbank_ist_byteweise_reproduzierbar`). Das war nicht von Anfang an so
— siehe die Modellierungsentscheidung zu `qs_befund` weiter unten.

## Die Tabellen

| Tabelle | Primärschlüssel | Fremdschlüssel | Herkunft | Zeilen |
|---|---|---|---|---:|
| `snapshot` | `snapshot_id` (autoincrement), `sha256` UNIQUE | `plz` → `bezirk` | eine Zeile je gespeicherter Datei (Seite) | 3 |
| `bezirk` | `plz` | — | `config.BEZIRKE`, von Hand gepflegt | 5 |
| `inserat_beobachtung` | **`(snapshot_id, ad_id)`** | `snapshot_id` → `snapshot`, `plz` → `bezirk` | willhaben-Schnappschüsse | 268 (205 Inserate, 63 an beiden Tagen) |
| `indexreihe` | `(reihe, jahr)` | — | Tariflohnindex, VPI | **0** — Quelle nicht beschafft |
| `zuordnungsluecke` | — (Protokolltabelle) | — | von `integrate.py` geschrieben | **0** — keine Lücke |
| `qs_befund` | — (Protokolltabelle) | — | Gate-Befunde aus Schritt 2 | 1 (Teilseite 25.09.) |
| `objekttyp_ausschluss` | `objekttyp` | — | `config.OBJEKTTYP_AUSGESCHLOSSEN`, mit Grund (E33) | 1 (`Zimmer/WG`) |

`NOT NULL` steht dort, wo eine Zeile ohne den Wert bedeutungslos wäre:
`snapshot.sha256`, `snapshot.abruf_ts`, `inserat_beobachtung.status`,
`inserat_beobachtung.plz`. **Nicht** auf `miete_eur` oder `flaeche_m2` — ein
Inserat ohne Flächenangabe ist eine echte Beobachtung, und es soll in der
Fallzahl auftauchen, statt am Fremdschlüssel zu scheitern.

### Abruf: kein eigener Schlüssel, eine View

Ein **Abruf** sind alle Seiten einer PLZ an einem Tag (`v_abruf`, E32). Er hat
keine eigene Tabelle, weil er vollständig aus `snapshot` folgt — Schlüssel
`(plz, substr(abruf_ts, 1, 10))`. Vollständigkeit, Zensierung der
Inseratsdauer und `v_abdeckung` beziehen sich auf den Abruf, nicht auf die
Seite.

## Die Beziehungen

```
bezirk (plz) ──┬── snapshot (plz) ──── inserat_beobachtung (snapshot_id)
               └────────────────────── inserat_beobachtung (plz)
```

Die Beobachtung hängt an zwei Seiten: am Schnappschuss, aus dem sie kommt
(Herkunft), und am Bezirk, in dem die Wohnung liegt (Analyse). Beides ist
nötig — über den Schnappschuss ist jede Zeile auf eine Datei mit SHA256
zurückführbar, über den Bezirk wird sie gruppierbar.

## Zuordnungslücken

| Fall | Zahl | Was passiert |
|---|---:|---|
| Inserat mit PLZ, die nicht in `config.BEZIRKE` steht | **0** | Zeile wird nicht geschrieben, in `zuordnungsluecke` gezählt und benannt |
| Schnappschuss mit unbekannter PLZ | **0** | Datei wird nicht aufgenommen, Fehler in `qs_befund` |
| Beobachtung ohne Bezirk (Waise) | **0** | als Test und als Gate-3-Prüfung |

Null Lücken ist hier das erwartete Ergebnis und kein Verdienst: alle 90
Inserate tragen die PLZ 1020, und 1020 steht in der Konfiguration. Die Tabelle
existiert für den Tag, an dem ein Bezirk dazukommt und die Konfiguration
hinterherhängt.

## Modellierungsentscheidungen

**Der Schlüssel der Faktentabelle ist `(snapshot_id, ad_id)`, nicht `ad_id`.**
Dieselbe Anzeige erscheint in jedem Schnappschuss erneut, und das ist gewollt.
Mit `ad_id` als Schlüssel hätte man die Zeile beim Wiedersehen aktualisiert und
genau die Information weggeworfen, auf der zwei der drei Analysen beruhen:
Preisänderung während der Laufzeit und Inseratsdauer. Die Tabelle ist
append-only; nichts wird überschrieben (E13).

**Verknüpft wird über die PLZ, und die Bezirksliste steht in der
Konfiguration.** Ein Bezirk mehr ist damit eine Datei mehr plus ein
Konfigurationseintrag — kein Eingriff in Views oder Code. Eine Textspalte
„Bezirk" in der Beobachtungszeile hätte eine unbekannte PLZ stumm geschluckt;
der Fremdschlüssel macht sie sichtbar (E14).

**SQLite statt MySQL-Server.** Die Datenmengen sind klein, und ein Server macht
den Zustand der Datenbank zu etwas, das im Repository nicht steht. Mit SQLite
ist die Datenbank ein erzeugtes Artefakt: ein Befehl, kein Zugangsdatensatz.
Das SQL bleibt Standard-SQL und läuft auf MySQL 8 mit denselben Views —
Fensterfunktionen sind nötig, 5.7 genügt nicht. Der Preis: kein
`PERCENTILE_CONT`, daher Median über Fensterfunktion (E12, E16).

**`qs_befund` trägt den Datenstand, nicht die Uhrzeit des Laufs.** Die Spalte
hieß zunächst `lauf_ts` und kam aus `datetime.now()`. Das fiel auf, als die
Datenbank nach Vorgabe committet werden sollte: eine Uhrzeit darin erzeugt bei
jedem Lauf einen Diff — und widerlegt genau die Reproduzierbarkeit, mit der das
Neubauen begründet ist. Jetzt trägt der Befund den `abruf_ts` des
Schnappschusses, zu dem er gehört. Inhaltlich ist das auch richtiger: der
Zeitpunkt eines Qualitätsbefunds ist der Datenstand, nicht die Laufzeit (E26).

**Die Datenbank wird bei jedem Lauf gelöscht und neu gebaut**, aus *allen*
Rohordnern. Inkrementelles Laden hätte das Ergebnis von der Reihenfolge der
Läufe abhängig gemacht, und ein Fehler von vorgestern wäre in der Datenbank
geblieben, auch nach der Reparatur des Codes. `data/raw/` ist die Quelle der
Wahrheit, die Datenbank ein jederzeit verwerfbares Ergebnis. Laufzeit: unter
einer Sekunde (E15).

## Die Views, und warum sie so aussehen

Die Kennzahlen greifen nicht auf die Fakttabelle zu, sondern auf Views
(`src/sql/views.sql`). Drei Grundsätze:

1. **Jede Aggregatzeile führt ihre Fallzahl und eine Belastbarkeitsstufe mit**
   (n ≥ 15 belastbar, n ≥ 8 dünn, sonst nicht belastbar). Ein Median über vier
   Inserate sieht in einer Tabelle aus wie einer über vierzig; ohne die Fallzahl
   *in derselben Zeile* wird die Unsicherheit beim Weiterverwenden
   abgeschnitten — besonders, wenn ein Sprachmodell die Zeile in Prosa
   übersetzt.
2. **Gefiltert wird auf aktive Inserate.** Reservierte Objekte sind kein
   Angebot mehr und überdurchschnittlich attraktiv; sie würden den Median nach
   oben ziehen. 90 Beobachtungen, 86 in der Analysebasis: 3 reserviert, 1 ohne
   Fläche.
3. **Alles gruppiert nach PLZ**, damit ein Bezirk mehr keine Änderung an den
   Views erfordert.

`v_cluster_marktmiete` ist das Bindeglied zum Entscheidungsmodell: es braucht
je Portfolio-Cluster genau eine Marktmiete. Bezirke ohne Schnappschuss
erscheinen dort mit der Eignung `kein Schnappschuss` statt mit einer
eingesetzten Zahl — zwei der drei Cluster stehen heute so da. Das ist eine
sichtbare Lücke und als Test festgeschrieben
(`test_fehlende_bezirke_erscheinen_als_luecke_nicht_als_annahme`).

## Was in der Datenbank nicht steht

Keine Personenspalten. Von der Anbieterseite ist nur das Flag `privat` /
`gewerblich` übrig. Ein Test prüft die gebaute Datenbank gegen die Liste der
verworfenen Feldnamen (`test_keine_personenspalte_in_der_datenbank`) — er
schlägt an, sobald eine solche Spalte angelegt wird, auch wenn sie leer ist.

## Korrekturen nach dem zweiten Abruf (09.10.)

Mit einem einzigen Schnappschuss waren zwei Views fehlerhaft, ohne dass es
auffallen konnte — beide brauchen zwei Zeitpunkte, um überhaupt etwas zu
liefern. Der zweite Abruf hat sie sichtbar gemacht; jede Korrektur hat einen
Test, der vorher rot war.

| Fehler | Wirkung | Korrektur | Test |
|---|---|---|---|
| Zeitstempel `+0200` ohne Doppelpunkt; SQLite liest nur `+02:00` | `julianday()` gab NULL, jede Inseratsdauer leer | Parser normalisiert den Versatz (`c679e95`) | `test_abrufzeit_ist_fuer_sqlite_lesbar`, `test_inseratsdauer_wird_gemessen_sobald_zwei_abrufe_da_sind` |
| `v_preisaenderung` rechnete (Maximum − Minimum) / Minimum | jede Senkung erschien als Erhöhung; am 09.10. waren 6 von 10 Änderungen Senkungen | erster gegen letzten Preis, Spalten `miete_erst`, `miete_zuletzt` (`39d16f8`) | `test_preissenkung_erscheint_als_senkung` |

Dazu drei Modellierungsentscheidungen aus demselben Abruf: Abruf statt Seite
(E32, `v_abruf`), WG-Zimmer ausgeschlossen (E33, `objekttyp_ausschluss`),
ungemessene Abgänge nicht als null Tage (E36).
