# Betriebshandbuch (Entwurf)

Stand 9.10.2026. Entwurf für Deliverable 2; die vollständige Fassung mit allen
sieben Abschnitten gehört zu Deliverable 3.

## 1 Starten

```bash
git clone <repo> && cd <repo>
python3 -m src.run                 # vier Schritte, drei Gates, unter 1 s
python3 tests/test_pipeline.py     # 40 Tests
python3 tests/test_modell.py       # 26 Tests
```

Keine Installation, kein Netz, keine Zugangsdaten: die Pipeline läuft mit der
Standardbibliothek. `requirements.txt` nennt nur `pandas` — und das nur für
eigene Auswertungen, nicht für den Lauf. Erfolg erkennt man an `GATE 3:
bestanden` und fünf Zeilen `derive:`.

Ergebnis: `data/processed/mietportfolio.sqlite` (committet, mit *DB Browser for
SQLite* öffenbar) und `data/processed/kennzahl_*.csv`.

## 2 Neue Daten einspielen

1. Schnappschuss beschaffen, am sichersten im privaten Fenster über die
   Quelltextansicht: `view-source:` + Bezirks-URL mit `?rows=90` eintippen,
   Strg+S. Bei mehr als 90 Treffern dasselbe mit `&page=2`. Prüfen: die Datei
   enthält `"searchResult"`. Alternative: Seite neu laden (Strg+Shift+R),
   dann `tools/snapshot.js` in der Konsole — das Skript prüft sich selbst.
2. Datei nach `data/raw_original/` legen (wird nicht committet), Name
   `wh_<plz>_mietwohnungen_<JJJJ-MM-TT>T<hhmm>[_s<seite>].json`.
3. Redigieren: `python3 tools/redigiere_schnappschuss.py data/raw_original/<datei> data/raw/<datum>/<datei>`,
   dann SHA256 beider Fassungen in `data/raw/<datum>/HERKUNFT.md`.
4. `python3 -m src.run`. Seiten desselben Tages zählen als ein Abruf. Neuer
   Bezirk? Zusätzlich einen Eintrag in `config.BEZIRKE` — die Views gruppieren
   nach PLZ.
5. `python3 tests/test_pipeline.py`, dann committen. Die Kennzahl-CSV und die
   Datenbank gehören mit in den Commit.

Jeder weitere Abruf derselben PLZ verbessert Analyse 3: Erst wenn ein Inserat
zwischen zwei späteren Abrufen verschwindet, hat es eine gemessene Dauer.

## 3 Bekannte Schwächen

| Schwäche | Wirkung | Woran man es merkt |
|---|---|---|
| **Ein Bezirk von fünf beschafft** | zwei der drei Portfolio-Cluster haben keine Marktmiete | `v_cluster_marktmiete` zeigt `kein Schnappschuss`; `v_abdeckung` nennt die Bezirke |
| **25.09. nur Teilseite (90 von 154)** | der Vergleich mit dem vollständigen Abruf vom 09.10. ist verzerrt | Warnung im Qualitätsbericht bei jedem Lauf |
| **Zwei Zeitpunkte, 14 Tage Abstand** | Preisänderungen messbar, eine Inseratsdauer noch nicht — nur der Anteil, der nach 14 Tagen noch steht; die Leerstandsannahme bleibt geraten | `kennzahl_inseratsdauer.csv`, Spalte `befund` |
| **Indexreihen nicht beschafft** | Mieten und Einkommen sind nicht fortgeschrieben | `clean` meldet „keine Datei vorhanden"; `indexreihe` hat 0 Zeilen |
| **Tariflohnindex misst Mindestlöhne** | bei IT-Berufen (24 % des Portfolios) ist die Fortschreibung eine Untergrenze | `config/berufsgruppen.json`, Feld `unschaerfe` |
| **Gemeindewohnungen im Angebot** | Direktvergaben zu 7,50–10 €/m² sind kein Vergleichsmarkt für Neubau, nur am Titel erkennbar | Minimum der Größenklassen; offene Entscheidung E34 |
| **pytest hier nicht installierbar** | Tests laufen über den eingebauten Läufer am Dateiende | `python3 -m pytest` schlägt fehl, `python3 tests/test_pipeline.py` nicht |
| **Beschaffung ist manuell** | nicht automatisierbar, solange die `robots.txt` das untersagt | bewusst so (Entscheidungslog E06) |

## 4 Wenn etwas hängt

| Meldung | Ursache | Behebung |
|---|---|---|
| `kein Datumsordner unter data/raw` | Rohdaten fehlen | Ordner `data/raw/<JJJJ-MM-TT>/` anlegen und redigierte Datei hineinlegen |
| `GATE 1 NICHT BESTANDEN … verticalId = 5` | falsche Seite gespeichert (Marktplatz statt Immobilien) | Bezirks-URL vollständig neu laden, `tools/snapshot.js` erneut |
| `PLZ wie erwartet: Dateiname sagt 1100, Daten sagen 1020` | `__NEXT_DATA__` hält die zuvor geladene Seite | dito — der häufigste Fehler, dreimal passiert |
| `sha256 schon aufgenommen` | dieselbe Datei unter neuem Namen | nicht erneut speichern, sondern neu laden |
| `snapshot.js` meldet „keine Suchergebnisseite“, `page: /iad` | Startseite geöffnet und zur Suche geklickt (09.10.) | `view-source:` + URL verwenden |
| `GATE 2` bricht ab | ein Feld trägt Kontaktmuster | nicht das Muster lockern, sondern die Allowlist in `config.py` prüfen |

Mehr Fälle, sobald sie auftreten — `docs/troubleshooting.md` ist dafür
vorgesehen und bislang leer, weil es noch keine weiteren gibt.
