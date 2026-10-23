"""Provider: die gespeicherte LLM-Extraktion als Modellantwort fuer die 8 Referenzfaelle.

Die Zeitreihen-Extraktion (data/extrakt/kv_erhoehungen_*.json,
prompts/kv_zeitreihe_v1.md) beantwortet fuer fuenf Branchen auch die
Referenzfrage "Abschluss 2026". Dieser Provider uebersetzt den Datensatz
2026 einer Branche in das Antwortformat von kv_extraktion_v1. Fuer Faelle,
deren Branche die Zeitreihe nicht abdeckt (Versicherung, Wirtschaftstreu-
haender, oeffentlicher Dienst), liefert er keine Antwort - sie werden als
"nicht gewertet" gefuehrt, nicht als falsch und nicht als richtig.

ist_prozent fragt der Zeitreihen-Prompt nicht ab; das Feld wird fuer diesen
Provider nicht bewertet (evals/lauf.py). Das ist eine Einschraenkung des
Laufs, steht in 06 und im Ergebnis.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))

from src import kv_extrakt  # noqa: E402

BRANCHE_FUER_FALL = {"kv_banken": "BANK", "kv_it": "IT", "kv_elektroindustrie": "INDUSTRIE",
                     "kv_handel_angestellte": "HANDEL", "kv_privatkrankenanstalten": "SPITAL"}


def ausfuehren(fall_id: str) -> str | None:
    b = BRANCHE_FUER_FALL.get(fall_id)
    if b is None:
        return None
    ds = json.loads(kv_extrakt.neueste_datei().read_text(encoding="utf-8"))["erhoehungen"]
    d = next((x for x in ds if x["branche_id"] == b and x["jahr"] == 2026), None)
    if d is None:
        return json.dumps({"abschluss_gefunden": False})
    return json.dumps({
        "abschluss_gefunden": True, "prozent_min": d["prozent_min"], "prozent_max": d["prozent_max"],
        "fixbetrag_eur": d["fixbetrag_eur"], "ist_prozent": None, "geltungsbeginn": d["gueltig_ab"],
        "bezugsgroesse": d["bezug"], "deckelung": d["deckel_eur"] is not None,
        "fundstelle_zeile": d["zeile"]})


def call_api(prompt, options, context):
    return {"output": ausfuehren(context.get("test", {}).get("description", "")) or ""}
