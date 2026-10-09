# Referenzantworten

Sie existieren **vor** dem Modell. Was hier steht, ist der Maßstab, an dem
später gemessen wird — nicht das Ergebnis einer Messung.

## Was da ist

| Datei | Fälle | Analyse | Entstehung |
|---|---:|---|---|
| `marktniveau.json` | 4 | Preisniveau je Größenklasse (1020, 25.09.2026) | `evals/nachrechnen_marktniveau.py` |
| `anbietertyp.json` | 2 | privat gegen gewerblich im Zielsegment | dito |
| `abdeckung_und_dauer.json` | 2 | Bezirksabdeckung; Inseratsdauer als Nicht-Ergebnis | dito |
| `handproben.json` | 3 | die von Hand nachzurechnenden Werte | dito |

`nachrechnen_marktniveau.py` ist eine **Zweitimplementierung**: sie liest
`data/raw/.../wh_*.json` direkt, ohne `src/clean.py`, ohne die Views und ohne
SQL. Stimmen beide Wege überein, ist das eine echte Kreuzprobe. Dieselbe
Funktion zweimal aufzurufen wäre keine.

Neu erzeugen:

```bash
python3 evals/nachrechnen_marktniveau.py
python3 tests/test_pipeline.py          # prueft SQL gegen diese Referenzen
```

## Was fehlt: die acht Extraktionsfälle

Die Vorgabe verlangt für Extraktion mindestens acht Fälle. Welche Fälle es
sind, steht fest — die sieben Berufsgruppen aus `config/berufsgruppen.json`
plus der öffentliche Dienst als Vergleichsreihe. Zu extrahieren ist je
Kollektivvertrag: **Prozentsatz, Geltungsbeginn, Bezugsgröße** (KV-Mindestlohn
oder Ist-Lohn) **und Deckelung**.

Was fehlt, ist das Quelldokument im Wortlaut.

**Warum nicht einfach recherchiert.** Ein Modellzugriff auf die ÖGB- und
WKO-Seiten liefert eine Zusammenfassung, nicht den Seitentext. Referenzantworten
daraus zu bilden heißt, das Modell gegen sich selbst zu prüfen. Genau das ist in
einer früheren Projektfassung passiert (Entscheidungslog E02): das Goldset war
aus Suchtreffer-Ausschnitten rekonstruiert, die Trefferquote sah gut aus und
bedeutete nichts.

**Beschaffung, gleiche Logik wie bei den Inseraten** — ein Mensch speichert, die
Pipeline verarbeitet:

1. `https://www.oegb.at/themen/arbeitsrecht/kollektivvertrag/aktuelle-kollektivvertragsverhandlungen`
   im Browser öffnen.
2. Als **Text** speichern (Strg+S, „Nur Text") oder `view-source:` davorsetzen
   und den Quelltext speichern.
3. Ablegen als `data/raw/<datum>/kv_oegb_<datum>.txt`.
4. Für die beiden Reihen, die dort fehlen oder unklar sind, dasselbe mit der
   jeweiligen WKO-Seite, benannt `kv_wko_<branche>_<datum>.txt`.
5. `python3 -m src.run` — `clean.kollektivvertrag()` liest `kv_*.txt`, sobald
   die Quelle in `config.QUELLEN` eingetragen ist.

Danach werden die acht Fälle **wörtlich aus der gespeicherten Datei** erfasst,
mit Fundstelle (Datei und Zeile), und als `kv_extraktion.json` abgelegt. Das
Feld `rohtext` enthält den kopierten Satz, nicht eine Nachschrift.

Bis dahin liegt hier keine Datei mit Platzhaltern. Eine leere Referenzdatei
sieht aus wie Arbeit und ist keine.

## Regeln für jede Referenz

- `eingabe`, `erwartete_antwort`, `pruefregel`, `toleranz`, `herkunft`
  (wer, wann, wie) und `unsicherheit` sind Pflicht. Ein Test prüft das
  (`test_referenzen_tragen_herkunft_und_unsicherheit`).
- `von_hand_bestaetigt` ist `false`, solange niemand nachgerechnet hat.
  Es wird nicht aus Bequemlichkeit `true`.
- Wo „richtig" unsicher ist, steht das im Feld `unsicherheit` — nicht in einer
  Fußnote, die beim Auswerten keiner liest.
- Eine Referenz darf verlangen, dass **nichts** behauptet wird. Der Fall
  `inseratsdauer_nicht_messbar` ist bestanden, wenn die Abfrage ihre
  Unauswertbarkeit meldet.
