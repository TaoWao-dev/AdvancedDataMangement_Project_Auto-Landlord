# Herkunft der Dateien vom 23.10.2026

Kollektivvertragsseiten für die Extraktion (Analyse 4, Entscheidungslog E28
und E41). Gespeichert vom Studierenden am 23.10.2026 im Browser über
`view-source:`, also ohne automatisierten Abruf (E06). Die Originale liegen
lokal unter `data/raw_original/2026-10-23/` und sind nicht im Repository;
hier steht ihre SHA256.

Aufbereitet mit:

```bash
python3 tools/kv_quellen_aufbereiten.py 2026-10-23 data/raw_original/2026-10-23/*.html
```

Jede Zeile der Textdateien beginnt mit der Zeilennummer im Originalquelltext
der Seite. Diese Nummer ist die Fundstelle in `evals/references/kv_extraktion.json`.

| Datei | Quelle | SHA256 Original | SHA256 hier | Bearbeitung |
|---|---|---|---|---|
| `kv_oegb_2026-10-23.txt` | https://www.oegb.at/themen/arbeitsrecht/kollektivvertrag/aktuelle-kollektivvertragsverhandlungen | `7dff5041a0ab23b5…` | `8df11d3d51feb273…` | Seiteninhalt ohne Autorenzeile und Navigation; 2 Kontaktmuster ersetzt |
| `kv_wko_banken-und-bankiers_2026-10-23.txt` | https://www.wko.at/kollektivvertrag/kollektivvertrag-banken-und-bankiers-2026 | `31f6f5b09244ceaf…` | `c129e509d865d229…` | nur Liste der KV-Fassungen und Geltungsdauer; 0 Kontaktmuster ersetzt |
| `kv_wko_landes-hypothekenbanken_2026-10-23.txt` | https://www.wko.at/wien/kollektivvertraege/landes-hypothekenbanken | `dfceeb0ab48bd733…` | `df5fd3bd22fc7dc7…` | nur Liste der KV-Fassungen und Geltungsdauer; 0 Kontaktmuster ersetzt |
| `kv_wko_raiffeisenbanken-raiffeisenlandesbanken_2026-10-23.txt` | https://www.wko.at/wien/kollektivvertraege/raiffeisenbanken-raiffeisenlandesbanken | `8384fc6e337d8a68…` | `f9214aefce17599d…` | nur Liste der KV-Fassungen und Geltungsdauer; 0 Kontaktmuster ersetzt |
| `kv_wko_sparkassen_2026-10-23.txt` | https://www.wko.at/wien/kollektivvertraege/sparkassen | `d8a870dd5576920b…` | `ba6638fa2a9be62d…` | nur Liste der KV-Fassungen und Geltungsdauer; 0 Kontaktmuster ersetzt |
| `kv_wko_versicherungsunternehmen_2026-10-23.txt` | https://www.wko.at/wien/kollektivvertraege/versicherungsunternehmen | `fd8bcfe4b596e51d…` | `2b7115a4aa03cd5f…` | nur Liste der KV-Fassungen und Geltungsdauer; 0 Kontaktmuster ersetzt |
| `kv_wko_volksbanken-kreditgenossenschaften_2026-10-23.txt` | https://www.wko.at/wien/kollektivvertraege/volksbanken-kreditgenossenschaften | `4d9700b5fa0f51d3…` | `c08af348a7922ec7…` | nur Liste der KV-Fassungen und Geltungsdauer; 0 Kontaktmuster ersetzt |

**Was entfernt wurde und warum.** Auf der ÖGB-Seite steht vor dem Inhalt
eine Autorenzeile mit Personennamen; sie liegt außerhalb des übernommenen
Ausschnitts (Regel 1). Zwei Webadressen im Text sind durch
`[URL ENTFERNT]` ersetzt. Die WKO-Seiten enthalten außer der Liste der
KV-Fassungen nur Navigation; die Prozentsätze stehen dort in PDFs, die nicht
gespeichert wurden.

**Was fehlt.** Für Versicherungen (Innendienst), Landes-Krankenanstalten und
Wirtschaftstreuhänder nennt keine der Seiten einen Prozentsatz für 2026. Das
ist in den Referenzen als Befund geführt, nicht als Lücke gefüllt.

## Inserate 1020 vom 23.10.2026 (dritter Abruf)

| | |
|---|---|
| Quelle | willhaben.at, Suche „Mietwohnungen Wien 1020 Leopoldstadt", `?rows=90`, Seite 1 und `&page=2` |
| Abruf | Seite 1: 23.10.2026, 16:26:53 · Seite 2: 16:27:32 — laut `searchDate` des Servers |
| Beschaffung | manuell über `view-source:`, gespeichert vom Studierenden; JSON aus der Quelltextansicht mit `src/wh_next_data.lade_rohdaten`, redigiert mit `tools/redigiere_schnappschuss.py` (Selbstprüfung: gleiche Lesung) |
| Prüfung | `verticalId` 2, `pageRequested` 1 bzw. 2, alle Inserate PLZ 1020 |
| Treffer | 174; auf den Seiten 90 + 84 = **174, vollständig** |

| Datei | SHA256 Original (Quelltextansicht) | SHA256 redigiert |
|---|---|---|
| `wh_1020_mietwohnungen_2026-10-23T1626.json` | `f70c82f50d125cbd…` | `e274c9d10c6707d5…` |
| `wh_1020_mietwohnungen_2026-10-23T1627_s2.json` | `121a1571ebeb0367…` | `30dc7cdd39023d5d…` |

Mit diesem dritten Abruf ist die Inseratsdauer erstmals messbar: Inserate,
die am 09.10. standen und am 23.10. fehlen, haben eine gemessene Dauer.
