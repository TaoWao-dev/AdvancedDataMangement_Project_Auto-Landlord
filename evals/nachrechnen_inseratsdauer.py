"""Zweitimplementierung fuer Analyse 3 mit zwei Abrufen (Stand 09.10.2026).

    python3 evals/nachrechnen_inseratsdauer.py

05_schritt4 hatte eine Referenz fuer den Zwei-Abruf-Stand fuer Deliverable 3
angekuendigt. Dieses Skript liest die redigierten Rohdateien direkt - ohne
src/, ohne Datenbank, ohne SQL -, sammelt je Abruftag die Inseratskennungen
und zaehlt mit Mengenoperationen. Die View rechnet mit GROUP BY und
Fensterfunktionen; stimmen beide ueberein, ist das eine echte Kreuzprobe.

Abruftag ist der Name des Rohordners (data/raw/<datum>/), nicht der
Zeitstempel im JSON - noch ein Unterschied zum Weg der Pipeline.
"""
from __future__ import annotations

import json
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "evals" / "references" / "inseratsdauer_zwei_abrufe.json"
PLZ = "1020"


DATENSTAND = ["2026-09-25", "2026-10-09"]   # der Stand, den die Referenz beschreibt


def ids_je_tag(stand: list[str] | None) -> dict[str, set[str]]:
    tage: dict[str, set[str]] = {}
    for datei in sorted((WURZEL / "data" / "raw").glob(f"*/wh_{PLZ}_*.json")):
        if stand is not None and datei.parent.name not in stand:
            continue
        d = json.loads(datei.read_text(encoding="utf-8"))
        ads = d["props"]["pageProps"]["searchResult"]["advertSummaryList"]["advertSummary"]
        tage.setdefault(datei.parent.name, set()).update(str(a["id"]) for a in ads)
    return tage


def rechnen(stand: list[str] | None = DATENSTAND) -> dict:
    """stand=None: alle Rohordner (fuer den Test gegen den aktuellen Stand)."""
    tage = ids_je_tag(stand)
    reihenfolge = sorted(tage)
    letzter = tage[reihenfolge[-1]]
    alle = set().union(*tage.values())
    aeltere = set().union(*(tage[t] for t in reihenfolge[:-1]))
    einmal = {i for i in alle if sum(i in s for s in tage.values()) == 1}
    return {
        "abrufe": len(reihenfolge),
        "inserate": len(alle),
        "davon_zensiert": len(letzter),
        "abgaenge_ungemessen": len((alle - letzter) & einmal),
        "anteil_aeltere_noch_online": round(len(aeltere & letzter) / len(aeltere), 2),
        "auswertbar": False,
    }


if __name__ == "__main__":
    r = rechnen()
    fall = {
        "fall_id": "inseratsdauer_zwei_abrufe",
        "eingabe": {"abfrage": "src/sql/kennzahl_inseratsdauer.sql", "filter": {"plz": PLZ},
                    "datenstand": DATENSTAND},
        "erwartete_antwort": {k: v for k, v in r.items() if k != "abrufe"},
        "pruefregel": "exakter Vergleich; Anteil auf 0,01",
        "toleranz": {"anteil_aeltere_noch_online": 0.01},
        "herkunft": {"wer": "Zweitimplementierung (Claude), Pruefung durch den Studierenden ausstehend",
                     "wann": "2026-10-23",
                     "wie": "evals/nachrechnen_inseratsdauer.py: Mengen der Inseratskennungen je Rohordner, ohne src/ und SQL"},
        "von_hand_bestaetigt": False,
        "unsicherheit": "Mit zwei Abrufen ist keine Dauer messbar: wer am 25.09. stand und am 09.10. fehlt, ist irgendwann dazwischen verschwunden. 'auswertbar' muss false bleiben; ein Mittelwert waere erfunden (E36). Belastbar ist nur der Anteil der aelteren Inserate, die noch online sind - eine Untergrenze fuer die Leerstandsdauer, kein Schaetzwert.",
    }
    ZIEL.write_text(json.dumps({
        "_zweck": "Referenz fuer Analyse 3 mit zwei Abrufen. Existiert vor jedem Modell.",
        "_quelle": "data/raw/2026-09-25/, data/raw/2026-10-09/ (wh_1020_*.json)",
        "_erzeugt_von": "evals/nachrechnen_inseratsdauer.py",
        "_warnung": "Nicht von Hand bearbeiten.",
        "faelle": [fall]}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{r} -> {ZIEL.relative_to(WURZEL)}")
