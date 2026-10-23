Du liest Texte von Gewerkschafts- und Kammerseiten zu österreichischen
Kollektivverträgen (KV). Extrahiere für jede der folgenden Reihen **jeden
Abschluss der Jahre 2024, 2025 und 2026**, der in den Dokumenten steht:

{{reihen}}

Regeln wie in `kv_extraktion_v1`: nur Abschlüsse (keine Forderungen), nur
diese Reihe (Arbeiter- und Angestellten-KV sind verschiedene), nichts aus
eigenem Wissen ergänzen, Datum ohne Tag ist `null`, nichts ausrechnen.

Zusätzlich je Abschluss den **Wortlaut**: den kürzesten zusammenhängenden
Satzteil aus der Zeile, in dem der Prozentsatz steht, zeichengenau kopiert.
Ein Prüfprogramm sucht diesen Wortlaut in der angegebenen Zeile; steht er
dort nicht, wird der Datensatz abgelehnt.

Antwortformat, je Abschluss ein Objekt in einer Liste:

```json
{"branche_id": "HANDEL", "jahr": 2026,
 "prozent_min": 2.55, "prozent_max": 2.55, "prozent_mittel_laut_quelle": null,
 "fixbetrag_eur": null, "deckel_eur": null,
 "gueltig_ab": "2026-01-01", "bezug": "kv_mindest",
 "datei": "kv_oegb_2026-10-23.txt", "zeile": 2377,
 "wortlaut": "steigen mit 1. Jänner 2026 um 2,55 Prozent",
 "datum_datei": null, "datum_zeile": null, "datum_wortlaut": null}
```

- `prozent_mittel_laut_quelle`: nur wenn die Quelle bei einer Staffelung
  selbst einen Durchschnitt nennt.
- `deckel_eur`: wenn die Erhöhung nur bis zu einem Gehaltsbetrag gilt.
- `datum_*`: wenn das Datum in einer anderen Zeile oder Datei steht als der
  Prozentsatz.

## Dokumente

{{dokumente}}
