"""Provider, der eine Datei aus dem Repository als Modellausgabe liefert.

Fuer die Vorlage: docs/vorlage.md ist die Ausgabe eines Modells (Prompt
prompts/vorlage_v1.md). Die Suite prueft die Datei, die im Repository
steht - nicht eine neu erzeugte, die niemand gelesen hat.
"""
from __future__ import annotations

from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]


def ausfuehren(vars_: dict) -> str:
    return (WURZEL / vars_["pfad"]).read_text(encoding="utf-8")


def call_api(prompt, options, context):
    return {"output": ausfuehren(context["vars"])}
