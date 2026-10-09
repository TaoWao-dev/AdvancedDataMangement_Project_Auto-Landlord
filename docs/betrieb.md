# Betriebshandbuch (Entwurf)

Stand 9.10.2026. Entwurf für Deliverable 2; die vollständige Fassung mit allen
sieben Abschnitten gehört zu Deliverable 3.

## 1 Starten

```bash
git clone <repo> && cd <repo>
python3 -m src.run                 # vier Schritte, drei Gates, unter 1 s
python3 tests/test_pipeline.py     # 32 Tests
python3 tests/test_modell.py       # 26 Tests
```

Keine Installation, kein Netz, keine Zugangsdaten: die Pipeline läuft mit der
Standardbibliothek. `requirements.txt` nennt nur `pandas` — und das nur für
eigene Auswertungen, nicht für den Lauf. Erfolg erkennt man an `GATE 3:
bestanden` und fünf Zeilen `derive:`.

Ergebnis: `data/processed/mietportfolio.sqlite` (committet, mit *DB Browser for
SQLite* öffenbar) und `data/processed/kennzahl_*.csv`.

## 2 Neue Daten einspielen

1. Schnappschuss beschaffen: Bezirks-URL **vollständig neu laden** (URL
   eintippen, Enter — nicht durchklicken), dann `tools/snapshot.js` in der
   Browserkonsole ausführen. Das Skript prüft sich selbst und benennt die Datei
   aus den Daten: `wh_<plz>_<suche>_<datum>.json`.
2. Datei nach `data/raw_original/` legen (wird nicht committet).
3. Redigieren: `python3 tools/redigiere_schnappschuss.py data/raw_original/<datei> data/raw/<datum>/<datei>`
4. `python3 -m src.run`. Neuer Bezirk? Zusätzlich einen Eintrag in
   `config.BEZIRKE`. Mehr ist nicht zu tun — die Views gruppieren nach PLZ.
5. `python3 tests/test_pipeline.py`, dann committen. Die Kennzahl-CSV und die
   Datenbank gehören mit in den Commit.

Ein zweiter Schnappschuss derselben PLZ macht `v_preisaenderung` und
`v_inseratsdauer` erstmals nicht leer — das ist Analyse 3.

## 3 Bekannte Schwächen

| Schwäche | Wirkung | Woran man es merkt |
|---|---|---|
| **Ein Bezirk von fünf beschafft** | zwei der drei Portfolio-Cluster haben keine Marktmiete | `v_cluster_marktmiete` zeigt `kein Schnappschuss`; `v_abdeckung` nennt die Bezirke |
| **Teilseite: 90 von 154 Treffern** | der Median beschreibt die erste Suchergebnisseite, nicht den Markt | Warnung im Qualitätsbericht bei jedem Lauf |
| **Nur ein Zeitpunkt** | Inseratsdauer und Preisänderung nicht messbar; die Leerstandsannahme bleibt geraten | `kennzahl_inseratsdauer.csv` hat `anteil_zensiert` = 1 |
| **Indexreihen nicht beschafft** | Mieten und Einkommen sind nicht fortgeschrieben | `clean` meldet „keine Datei vorhanden"; `indexreihe` hat 0 Zeilen |
| **Tariflohnindex misst Mindestlöhne** | bei IT-Berufen (24 % des Portfolios) ist die Fortschreibung eine Untergrenze | `config/berufsgruppen.json`, Feld `unschaerfe` |
| **Daten 14 Tage alt** | Inseratsangebote wechseln wöchentlich | `abruf_datum` in jeder Kennzahlzeile |
| **pytest hier nicht installierbar** | Tests laufen über den eingebauten Läufer am Dateiende | `python3 -m pytest` schlägt fehl, `python3 tests/test_pipeline.py` nicht |
| **Beschaffung ist manuell** | nicht automatisierbar, solange die `robots.txt` das untersagt | bewusst so (Entscheidungslog E06) |

## 4 Wenn etwas hängt

| Meldung | Ursache | Behebung |
|---|---|---|
| `kein Datumsordner unter data/raw` | Rohdaten fehlen | Ordner `data/raw/<JJJJ-MM-TT>/` anlegen und redigierte Datei hineinlegen |
| `GATE 1 NICHT BESTANDEN … verticalId = 5` | falsche Seite gespeichert (Marktplatz statt Immobilien) | Bezirks-URL vollständig neu laden, `tools/snapshot.js` erneut |
| `PLZ wie erwartet: Dateiname sagt 1100, Daten sagen 1020` | `__NEXT_DATA__` hält die zuvor geladene Seite | dito — der häufigste Fehler, dreimal passiert |
| `sha256 schon aufgenommen` | dieselbe Datei unter neuem Namen | nicht erneut speichern, sondern neu laden |
| `GATE 2` bricht ab | ein Feld trägt Kontaktmuster | nicht das Muster lockern, sondern die Allowlist in `config.py` prüfen |

Mehr Fälle, sobald sie auftreten — `docs/troubleshooting.md` ist dafür
vorgesehen und bislang leer, weil es noch keine weiteren gibt.
