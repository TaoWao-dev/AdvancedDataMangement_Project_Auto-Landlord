# Herkunft der Schnappschüsse vom 09.10.2026

| | |
|---|---|
| Quelle | willhaben.at, Suche „Mietwohnungen Wien 1020 Leopoldstadt", `?rows=90`, Seite 1 und `&page=2` |
| Abruf | Seite 1: 09.10.2026, 17:45:35 · Seite 2: 17:47:50 — laut `searchDate` des Servers |
| Beschaffung | manuell durch einen Menschen, über die Quelltextansicht des Browsers (`view-source:`), gespeichert und mit `__NEXT_DATA__` extrahiert |
| Treffer der Suche | 178 |
| Auf den Seiten | 90 + 88 = **178, vollständig**. Keine Überschneidung zwischen den Seiten. |

Erster vollständiger Bezirk des Projekts. Der Abruf vom 25.09. war eine
Teilseite (90 von 154).

## Wie die Dateien entstanden sind

Der erste Versuch an diesem Tag schlug fehl, und zwar genau so wie in E09
beschrieben: Seite im Browser gespeichert, nachdem zur Suche **geklickt**
statt die URL geladen worden war. Beide gespeicherten Dateien enthielten im
`__NEXT_DATA__` byteweise dieselbe Startseite (`page: /iad`) — mit dem
Nutzer-Feed und den Profildaten des angemeldeten Kontos. Sie wurden nicht
verwendet und nicht aufbewahrt. `tools/snapshot.js` brach daran mit einem
TypeError ab; seitdem meldet es den Grund (Commit `b388e47`).

Der zweite Versuch über `view-source:` lieferte frisches `__NEXT_DATA__`, weil
die Quelltextansicht die Seite immer neu vom Server holt. Chrome speichert
diese Ansicht als HTML-Tabelle mit escaptem Quelltext; das JSON wurde daraus
zurückgewonnen und mit den Prüfungen aus `snapshot.js` kontrolliert
(`verticalId` 2, alle Inserate PLZ 1020, `pageRequested` 1 bzw. 2).

## Zwei Fassungen je Datei

Hier liegen redigierte Fassungen. Die Originale enthalten Anbieterangaben und
eine Browserkennung und bleiben lokal.

| Datei | SHA256 Original (nur lokal) | SHA256 redigiert (hier) |
|---|---|---|
| `wh_1020_mietwohnungen_2026-10-09T1745.json` | `17211d69eed07d231518a4894cb3c83864a9add02e9412d6e9fb1767708fcc88` | `966e46652fa2f1dadb2151a19920830d1e86140f2c529ce4fa83b200eea78a14` |
| `wh_1020_mietwohnungen_2026-10-09T1747_s2.json` | `7c3e891d1643f7c8723a4b5f94aa89a11d8611c82d19b9ce0ee75b9adc340e80` | `4a339d5a388f872b0fbf9ccade3cb20bb2428cfb2e32358ca47d622ecf09ccfb` |

Die SHA256 der Originale beziehen sich auf das extrahierte JSON, nicht auf die
gespeicherte HTML-Datei.

Redigiert mit `tools/redigiere_schnappschuss.py`. Das Werkzeug meldet für
beide Dateien `gleiche_lesung: True`: Der Parser liest aus Original und
redigierter Fassung dieselben Inserate, Trefferzahlen und Abrufzeitpunkte.
Je Datei wurden 40 Attributwerte entfernt.

**Neu redigiert am 10.10.2026 (E38).** Die Redaktion schreibt seitdem je
Inserat `titel_merkmale.gemeinde_explizit` — ein Ja/Nein, das vor dem
Entfernen des Titels berechnet wird (3 Treffer, alle auf Seite 2). Die
SHA256 der Originale sind unverändert, die der redigierten Fassungen sind
neu. Der übrige Inhalt ist gleich: der Vergleich beider Fassungen ohne das
neue Feld ergibt Gleichheit. Die Schlüsselreihenfolge ist jetzt sortiert, ein
zweiter Lauf liefert byteweise dieselbe Datei.
