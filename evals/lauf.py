"""Die Eval-Suite ohne Node: dieselben Testfaelle, dieselben Grader.

    python3 evals/lauf.py                     # alles, was laufen kann
    python3 evals/lauf.py sql vorlage         # nur diese Tasks
    EVAL_BASE_URL=http://localhost:1234/v1 EVAL_MODELL=qwen/qwen3-8b \
        python3 evals/lauf.py kv_extraktion moebliert

Warum es diesen Laeufer neben promptfoo gibt: die Pipeline laeuft mit der
Standardbibliothek, ohne Installation (CLAUDE.md). Die Suite soll das auch
koennen - und in der Arbeitssitzung, in der sie gebaut wurde, waren weder
npm noch PyPI erreichbar (E42). promptfoo bleibt der vorgesehene Weg fuer die
Modelllaeufe (evals/*.yaml); beide lesen evals/tests/*.json und rufen
evals/graders/*.py. Es gibt keinen zweiten Massstab.

Ergebnisse: evals/results/<zeitpunkt>.json (bleibt lokal, gitignored) und
eine Tabelle auf der Konsole: Trefferquote je Task, getrennt nach
bestaetigten und unbestaetigten Referenzen, Modell, Zeit, Anfragen, Token,
Kosten. Ein Task ohne erreichbares Modell steht als "nicht gelaufen" da,
nicht als 0 %.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EVALS = Path(__file__).resolve().parent
WURZEL = EVALS.parent
sys.path.insert(0, str(WURZEL))

TASKS = {
    # task: (Testdatei, Provider, Prompt)
    "sql": ("kennzahlen.json", "sql", None),
    "vorlage": ("vorlage.json", "datei", None),
    "kv_extraktion": ("kv_extraktion.json", "modell", "prompts/kv_extraktion_v1.md"),
    "moebliert": ("moebliert.json", "modell", "prompts/moebliert_v1.md"),
    # Die gespeicherte Zeitreihen-Extraktion (Claude, Sitzung 23.10.) gegen
    # dieselben Referenzen - ohne erneuten Modellaufruf (E45).
    "kv_extraktion_gespeichert": ("kv_extraktion.json", "extrakt", "prompts/kv_zeitreihe_v1.md"),
}

# Gepinnt: Modellname und Stand. Wer ein anderes Modell nimmt, setzt
# EVAL_MODELL - und der Name landet im Ergebnis, nicht in einer Erinnerung.
MODELL_STANDARD = "qwen/qwen3-8b"
MODELL_STAND = "2026-10-23"
BASE_STANDARD = "http://localhost:1234/v1"      # LM Studio


def _var(wert):
    if isinstance(wert, str) and wert.startswith("file://"):
        return (EVALS / wert[len("file://"):]).read_text(encoding="utf-8")
    return wert


def prompt_rendern(pfad: str, vars_: dict) -> str:
    text = (WURZEL / pfad).read_text(encoding="utf-8")
    for k, v in vars_.items():
        if isinstance(v, (str, int, float)):
            text = text.replace("{{" + k + "}}", str(_var(v)))
    return text


def modell_aufrufen(prompt: str) -> tuple[str, dict]:
    base = os.environ.get("EVAL_BASE_URL", BASE_STANDARD).rstrip("/")
    modell = os.environ.get("EVAL_MODELL", MODELL_STANDARD)
    kopf = {"Content-Type": "application/json"}
    if os.environ.get("EVAL_API_KEY"):
        kopf["Authorization"] = "Bearer " + os.environ["EVAL_API_KEY"]
    body = json.dumps({"model": modell, "temperature": 0, "seed": 20261023,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body, headers=kopf)
    with urllib.request.urlopen(req, timeout=600) as r:
        antwort = json.loads(r.read())
    text = antwort["choices"][0]["message"]["content"]
    return text, antwort.get("usage", {})


def modell_erreichbar() -> bool:
    base = os.environ.get("EVAL_BASE_URL", BASE_STANDARD).rstrip("/")
    try:
        urllib.request.urlopen(base + "/models", timeout=3)
        return True
    except (urllib.error.URLError, OSError, ValueError):
        return False


def grader(test: dict):
    name = test["assert"][0]["value"].split("/")[-1].removesuffix(".py")
    return importlib.import_module(f"evals.graders.{name}")


def task_laufen(task: str) -> dict:
    datei, provider, prompt = TASKS[task]
    tests = json.loads((EVALS / "tests" / datei).read_text(encoding="utf-8"))
    info = {"task": task, "faelle": len(tests), "modell": None, "anfragen": 0,
            "token": 0, "kosten_eur": 0.0, "sekunden": 0.0, "ergebnisse": []}
    if not tests:
        return info | {"status": "keine Faelle (Referenz fehlt)"}
    if provider == "modell":
        if not modell_erreichbar():
            return info | {"status": "nicht gelaufen: kein Modell erreichbar "
                                     f"({os.environ.get('EVAL_BASE_URL', BASE_STANDARD)})"}
        info["modell"] = f"{os.environ.get('EVAL_MODELL', MODELL_STANDARD)} (Stand {MODELL_STAND})"
    else:
        info["modell"] = {"extrakt": "Claude Opus 5.5, gespeicherte Ausgabe von kv_zeitreihe_v1 (23.10.2026)",
                          "sql": "SQL (src/sql/kennzahl_*.sql)",
                          "datei": "docs/vorlage.md (Ausgabe von prompts/vorlage_v2.md)"}[provider]
    start = time.monotonic()
    for t in tests:
        v = {k: _var(x) for k, x in t["vars"].items()}
        if provider == "sql":
            from evals.providers import sql_kennzahl
            ausgabe = sql_kennzahl.ausfuehren(v)
        elif provider == "extrakt":
            from evals.providers import extrakt
            ausgabe = extrakt.ausfuehren(t["description"])
            if ausgabe is None:
                info["ergebnisse"].append({"fall": t["description"], "pass": True, "score": 1.0,
                                           "grund": "Branche nicht in der Zeitreihe - nicht gewertet",
                                           "gewertet": False, "bestaetigt": False, "ausgabe": None})
                continue
            v = dict(v, nicht_bewertet=list(v.get("nicht_bewertet", [])) + ["ist_prozent"])
        elif provider == "datei":
            from evals.providers import datei
            ausgabe = datei.ausfuehren(v)
        else:
            ausgabe, usage = modell_aufrufen(prompt_rendern(prompt, t["vars"]))
            info["anfragen"] += 1
            info["token"] += int(usage.get("total_tokens", 0))
        r = grader(t).get_assert(ausgabe, {"vars": v})
        info["ergebnisse"].append({"fall": t["description"], "pass": r["pass"],
                                   "score": round(r["score"], 3), "grund": r["reason"],
                                   "gewertet": r.get("gewertet", True),
                                   "bestaetigt": t["metadata"].get("von_hand_bestaetigt", False),
                                   "ausgabe": ausgabe if provider == "modell" else None})
    info["sekunden"] = round(time.monotonic() - start, 2)
    return info | {"status": "gelaufen"}


def quote(ergebnisse: list[dict], nur_bestaetigt: bool | None = None) -> str:
    e = [x for x in ergebnisse if x["gewertet"]
         and (nur_bestaetigt is None or x["bestaetigt"] == nur_bestaetigt)]
    if not e:
        return "-"
    n = sum(x["pass"] for x in e)
    return f"{n}/{len(e)} ({100 * n / len(e):.0f} %)"


def main(argv: list[str]) -> int:
    auswahl = argv or list(TASKS)
    lauf = {"zeitpunkt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tasks": [task_laufen(t) for t in auswahl]}
    erg = EVALS / "results"
    erg.mkdir(exist_ok=True)
    ziel = erg / f"{lauf['zeitpunkt'].replace(':', '')}.json"
    ziel.write_text(json.dumps(lauf, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{'Task':<14} {'gesamt':<14} {'bestaetigt':<14} {'unbestaetigt':<14} "
          f"{'Anfr.':>5} {'Token':>7} {'Zeit s':>7}  Modell / Status")
    for t in lauf["tasks"]:
        e = t["ergebnisse"]
        print(f"{t['task']:<14} {quote(e):<14} {quote(e, True):<14} {quote(e, False):<14} "
              f"{t['anfragen']:>5} {t['token']:>7} {t['sekunden']:>7}  "
              f"{t['modell'] or ''} {'' if t['status'] == 'gelaufen' else '- ' + t['status']}")
        for x in e:
            if not x["pass"]:
                print(f"    ROT  {x['fall']}: {x['grund'][:160]}")
    print(f"\nKosten: 0 EUR (lokales Modell bzw. SQL). Ergebnis: {ziel.relative_to(WURZEL)}")
    gelaufen = [x for t in lauf["tasks"] for x in t["ergebnisse"]]
    return 0 if all(x["pass"] for x in gelaufen) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
