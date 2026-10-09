# Schritt 1 — Datenzugriff

**Frage dieses Schritts:** woher kommen die Daten, in welcher Form liegen sie
vor, und ist der Zugang wiederholbar?

**Abnahmekriterium:** `python3 -m src.extract` legt für jede Rohdatei einen
Provenienzeintrag mit SHA256 an und bricht ab, wenn eine Pflichtquelle fehlt.
Eine erneut verarbeitete Datei erhält denselben Zeitstempel wie beim ersten Mal
(er kommt aus den Daten, nicht von der Uhr).

## Die drei Quellen auf einen Blick

| Quelle | Form | Beschaffung | Lizenz | Pflicht | Stand |
|---|---|---|---|---|---|
| willhaben Mietinserate | JSON (`__NEXT_DATA__` einer Next.js-Suchseite) | **manuell** im Browser gespeichert | Nutzung nur als unwesentlicher Teil; robots.txt archiviert | ja | 1 von 5 Bezirken |
| Tariflohnindex | CSV, Statistik Austria OGD | automatisch, `data.statistik.gv.at` | CC-BY 4.0 | nein | noch nicht beschafft |
| VPI | CSV, Statistik Austria OGD | automatisch, `data.statistik.gv.at` | CC-BY 4.0 | nein | noch nicht beschafft |

Maschinenlesbar steht dieselbe Tabelle in `src/config.py` unter `QUELLEN` —
und zwar nur dort. Die Pipeline liest von dort, diese Datei erklärt es.

Strukturiert sind die Inserate und die Indexreihen. **Unstrukturiert** kommt im
LLM-Schritt dazu: Kollektivvertragsabschlüsse als Fließtext und die
Gesetzesmaterialien zur gedeckelten Wertsicherung. Deren Beschaffung ist in
Schritt 5 dokumentiert.

---


## Die Kurzfassung

Wir bauen **keinen** Crawler gegen willhaben. Der Abruf ist ein manueller
Arbeitsschritt, alles danach ist automatisiert, getestet und reproduzierbar.

## Was wir geprüft haben

### Gibt es eine offizielle API?

| Plattform | Befund |
|---|---|
| willhaben.at | keine öffentliche Abfrage-API. Kein Entwicklerportal, kein Partnerzugang. Es existiert `api.willhaben.at/restapi/v2/...` (steht als `selfLink` in jedem Inserat), aber die robots.txt sperrt `/restapi/` ausdrücklich. |
| ImmoScout24.at, Immowelt.at | APIs vorhanden, aber als **Einliefer**schnittstellen für Makler (OpenImmo). Keine Abfrage von Marktdaten. |
| Idealista | echte dokumentierte REST-API mit OAuth2 und kostenlosem Zugang auf Antrag — aber nur Spanien, Portugal, Italien. Für ein Wiener Portfolio nicht verwendbar. |

### Was sagt die willhaben-robots.txt?

Archiviert als `docs/willhaben_robots_2026-09-25.txt`. Der Kopf der Datei:

```
# It is expressively forbidden to use spiders, search robots or other automatic
# methods to access willhaben.at. Only if willhaben.at has given such access is
# allowed.
```

Dazu passend gesperrt: `/rest/`, `/restapi/`, `/webapi/`, `/ajax/`, `/mob/`,
`/pal/`, sowie einzelne Filterparameter, unter anderem `/*ESTATE_SIZE*` — also
genau der Flächenfilter, den wir bräuchten.

**Korrektur einer früheren Annahme.** In einem früheren Projektschritt stand
hier, die robots.txt sperre lediglich einzelne Filterparameter und erlaube den
blanken Pfad mit `?page=N`. Diese Aussage stammte aus der Dokumentation eines
Drittanbieter-Scrapers und war unvollständig: das pauschale Verbot im
Dateikopf war dort nicht erwähnt. Nach Lektüre der echten Datei ist die
Aussage falsch und die Projektentscheidung wurde geändert.

### Rechtliche Einordnung

Kein Rechtsrat, sondern die Begründung unserer Werkzeugwahl.

Ein Scraping-Verbot in AGB ist für sich genommen keine technische
Schutzmaßnahme. Die Text-und-Data-Mining-Schranke erlaubt automatisierte
Auswertung aber nur, solange der Rechteinhaber keinen **maschinenlesbaren**
Nutzungsvorbehalt erklärt hat. Genau das ist eine robots.txt: eine Datei an
einem standardisierten Ort, in maschinenlesbarer Form, mit einem
ausdrücklichen Verbot automatisierten Zugriffs.

Hinzu kommt: ein Abruf unseres Werkzeugs wurde tatsächlich blockiert. Bot-Schutz
ist vorhanden. Ihn zu umgehen wäre das Überwinden einer Zugangssicherung und
damit eine andere rechtliche Kategorie als das Abrufen einer offenen Seite.

### Konsequenz

Ein Mensch öffnet die Suchseite im Browser — normales Surfen, kein
automatisierter Zugriff — und speichert sie. Die Pipeline verarbeitet die
gespeicherte Datei.

Das kostet einen Handgriff pro Woche und Bezirk. Es kostet **nicht** die
Datenqualität: der gespeicherte Seitenquelltext enthält denselben
`__NEXT_DATA__`-Block, den ein Crawler bekommen hätte, mit allen 90 Inseraten
und dem Abrufzeitstempel des Servers.

## Ablauf der manuellen Beschaffung

Pro Bezirk und Woche:

1. Suchseite im Browser öffnen, zum Beispiel
   `willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1020-leopoldstadt?rows=90`
2. DevTools-Konsole öffnen und diesen Ausdruck ausführen — er lädt nur den
   Datenblock herunter:
   ```js
   const el = document.getElementById('__NEXT_DATA__');
   const a = document.createElement('a');
   a.href = URL.createObjectURL(new Blob([el.textContent], {type:'application/json'}));
   a.download = 'wh_1020_mietwohnungen.json';
   a.click();
   ```
   Alternativ `view-source:` aufrufen und mit Strg+S speichern — der Parser
   verarbeitet beide Formen.
3. Datei nach `data/snapshots/` legen, Benennung
   `wh_<plz>_<suche>_<datum>T<zeit>.json`
4. `python3 -m src.ingest_markt --ordner data/snapshots --plz 1020`

**Achtung, aus Erfahrung:** Prüfen, dass die Konsole auf der richtigen Seite
läuft. Siehe den nächsten Abschnitt.

## Der Vorfall, der das Gate begründet

Beim ersten Beschaffungsversuch entstanden zwei Dateien, beide benannt wie die
Mietwohnungssuche für 1020 Wien. Nur eine war es:

| Datei | verticalId | searchId | rowsFound | Inserate | PLZ |
|---|---|---|---|---|---|
| `wh_1020_mietwohnungen_2026-09-25T1555.json` | 2 (Immobilien) | 131 | 154 | 90 | alle 1020 |
| `negativ_falscher_vertical.json` | 5 (Marktplatz) | 301 | 13.353.029 | 30 | 24 verschiedene |

Die zweite Datei ist syntaktisch einwandfreies JSON derselben Struktur. Ohne
Eingangsprüfung hätte die Pipeline daraus einen Median gerechnet — über
Gebrauchtwaren aus ganz Österreich — und nichts wäre abgestürzt.

Die Datei liegt deshalb als **Negativ-Fixture** im Repository und ist Teil der
Testsuite (`test_gate_faengt_falsche_seite_ab`). Das Gate lehnt sie mit vier
Begründungen ab: unplausible Trefferzahl, keine einheitliche PLZ, falsche PLZ,
Flächenfeld zu 0 % belegt.

## Personenbezogene Daten

Die Schnappschüsse enthalten Felder mit Personenbezug. Nicht offensichtlich,
aber real: `advertiserInfo.label` und `ORGNAME` tragen Firmennamen, die häufig
Personennamen enthalten — im geprüften Schnappschuss unter anderem
„Mittelsmann Philipp Sulek GmbH", „MMI Mario Molnar Immobilienberatung",
„Realbüro Dr. C. Huber".

`src/pii.py` arbeitet deshalb als **Allowlist**: was nicht ausdrücklich
erlaubt ist, wird verworfen. Eine Blocklist wäre die falsche Richtung, weil
sie bei jedem neuen Feld von willhaben stillschweigend durchlässt.

Behalten wird nur, was die Entscheidung braucht: Miete, Fläche, Zimmer,
Stockwerk, Freifläche, PLZ, Objekttyp, Status, Abrufzeit und das Flag
privat/gewerblich. Nicht behalten werden Anbietername und -kennungen,
Inseratstitel, Freitext, Straße, Punktkoordinate und Bild-URLs.

Danach läuft eine Kontrollsuche über alle verbleibenden Werte. Ein Treffer ist
ein **Fehler**, keine Warnung — dann stimmt etwas an der Allowlist nicht.

## Drei Quellen, nicht eine

| Rolle | Quelle | Automatisierung |
|---|---|---|
| Niveau, wöchentlich | willhaben-Schnappschuss | manueller Abruf, automatisierte Verarbeitung |
| Bewegung zwischen Abrufen | VPI-Teilindex Wohnungsmieten, Statistik Austria OGD | vollautomatisch, CC-BY, ausdrücklich zur Weiterverwendung bereitgestellt |
| Unabhängige Gegenprobe | Maklerberichte (EHL, Otto, Re/Max) als PDF | LLM-Extraktion |

Fällt eine Beschaffung aus, läuft die Pipeline weiter und der
Qualitätsbericht weist aus, wie alt das Niveau ist. Der Ausfall wird sichtbar
statt still.


## Was von der gespeicherten Seite ins Repository darf

Beim Vorbereiten des ersten Git-Push fiel auf, dass eine gespeicherte
Ergebnisseite erheblich mehr enthält als die Inserate. Zwei Funde:

**`props.pageProps.searchResult.dmpUserIdentities.wh_uuid`** — eine Kennung des
Browsers, mit dem gespeichert wurde. Sie beschreibt nicht den Wohnungsmarkt,
sondern die Person am Rechner. Der Wert wird hier auch nicht in Auszügen
wiedergegeben — eine gekürzte Kennung ist immer noch eine Kennung.

**Anbieterangaben** — `ORGNAME`, `advertiserInfo.label`, `ADVERTISER_REF`,
`ORGID`, `ORG_UUID`, dazu `ADDRESS`, `COORDINATES`, `BODY_DYN`, `HEADING` und
`description`. Firmennamen tragen im Immobilienbereich häufig Personennamen.

Die Pipeline verwirft all das ohnehin — aber erst nach dem Einlesen
(Allowlist, Entscheidungslog E11). Die Rohdatei selbst trägt es weiter, und ein
Push trägt es **unwiderruflich** in die Git-Historie: ein späteres `git rm`
entfernt die Datei aus dem Arbeitsstand, nicht aus der Historie.

Konsequenz: im Repository liegt eine redigierte Fassung. `tools/redigiere_
schnappschuss.py` erhält Struktur und Feldnamen, ersetzt aber die Werte der
nicht benötigten Felder durch `[ENTFERNT]`. Feldnamen bleiben absichtlich
stehen — sie belegen, was die Quelle liefert, ohne den Inhalt zu verbreiten.

Eine Ausnahme mit Begründung: `advertiserInfo.label` wird nicht auf
`[ENTFERNT]` gesetzt, sondern auf `Privat` beziehungsweise `[GEWERBLICH]`. Der
Parser leitet daraus die Unterscheidung privat/gewerblich ab, und die ist eine
Analysegröße — der gewerbliche Median liegt 16 % über dem privaten. Die
Unterscheidung bleibt, der Name verschwindet.

**Beleg, dass die Redaktion nichts am Ergebnis ändert:** die fünf
Kennzahl-CSV sind vor und nach der Redaktion bit-identisch. Die Hashes beider
Fassungen stehen in `data/raw/2026-09-25/HERKUNFT.md`; das unveränderte
Original bleibt beim Menschen, der es gespeichert hat.
