"""Hilfen, die mehrere Grader brauchen."""
from __future__ import annotations

import json
import re


def json_aus_antwort(text: str) -> dict | None:
    """Erstes JSON-Objekt aus einer Modellantwort.

    Modelle umgeben JSON gern mit Erklaerung oder ```json-Zaeunen, kleine
    lokale Modelle (Qwen3) zusaetzlich mit <think>...</think>. Das wird hier
    abgeschnitten - aber nichts wird repariert. Ungueltiges JSON ist ein
    Fehler des Modells, nicht des Graders.
    """
    if not isinstance(text, str):
        return text if isinstance(text, dict) else None
    t = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, flags=re.S)
    kandidat = m.group(1) if m else None
    if kandidat is None:
        start = t.find("{")
        if start < 0:
            return None
        tiefe = 0
        for i in range(start, len(t)):
            if t[i] == "{":
                tiefe += 1
            elif t[i] == "}":
                tiefe -= 1
                if tiefe == 0:
                    kandidat = t[start:i + 1]
                    break
    if kandidat is None:
        return None
    try:
        obj = json.loads(kandidat)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def ergebnis(ok: bool, grund: str, score: float | None = None) -> dict:
    """Format, das promptfoo als GradingResult versteht."""
    return {"pass": bool(ok), "score": float(ok if score is None else score), "reason": grund}
