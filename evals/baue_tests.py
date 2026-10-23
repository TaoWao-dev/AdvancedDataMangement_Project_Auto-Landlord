"""Testfaelle der Suite aus den Referenzen erzeugen.

    python3 -m src.run && python3 evals/baue_tests.py

Die Referenzen (evals/references/) sind der Massstab; die Testdateien
(evals/tests/) sind nur ihre Uebersetzung in das Format, das promptfoo und
evals/lauf.py lesen. Wer einen Fall aendern will, aendert die Referenz.

Zusaetzlich entsteht der Kontext, den das Modell sieht (evals/kontext/):
die KV-Textbloecke und die Kennzahltabellen - beide aus der Datenbank bzw.
den Kennzahl-CSV, also aus derselben Pipeline, nicht aus einer Abkuerzung.
Context Engineering heisst hier: das Modell bekommt die ganze Seite mit
allen Jahrgaengen, nicht einen vorgefilterten Absatz. Vorfiltern waere
Extraktion durch den Filter, und die Referenz wuerde den Filter messen.
"""
from __future__ import annotations

import csv
import json
import sqlite3
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
REF = WURZEL / "evals" / "references"
TESTS = WURZEL / "evals" / "tests"
KONTEXT = WURZEL / "evals" / "kontext"
sys.path.insert(0, str(WURZEL))

from src import config as C  # noqa: E402

GRADER = "file://graders/{}.py"


def _assert(grader: str) -> list[dict]:
    return [{"type": "python", "value": GRADER.format(grader)}]


def kennzahlen_tests() -> list[dict]:
    tests = []
    # marktniveau filtert selbst nach abruf_datum und laeuft deshalb auf dem
    # vollen Datenstand - so zeigt der Test, dass der Abruf vom 09.10. die
    # Werte vom 25.09. nicht veraendert. Die uebrigen Referenzen haben keinen
    # Datumsfilter und beschreiben den Stand vom 25.09.; sie laufen gepinnt.
    for datei, stand, auswertung in (("marktniveau.json", None, None),
                                      ("anbietertyp.json", ["2026-09-25"], None),
                                      ("abdeckung_und_dauer.json", ["2026-09-25"], "auto"),
                                      ("inseratsdauer_zwei_abrufe.json",
                                       ["2026-09-25", "2026-10-09"], "auto")):
        for fall in json.loads((REF / datei).read_text(encoding="utf-8"))["faelle"]:
            erwartet = {k: v for k, v in fall["erwartete_antwort"].items() if k != "begruendung"}
            art = None
            if auswertung == "auto":
                art = "abdeckung" if "abdeckung" in fall["eingabe"]["abfrage"] else "inseratsdauer"
            tol = fall.get("toleranz") or {}
            tests.append({
                "description": fall["fall_id"],
                "vars": {"abfrage": fall["eingabe"]["abfrage"], "filter": fall["eingabe"].get("filter", {}),
                         "datenstand": stand, "auswertung": art, "erwartet": erwartet,
                         "toleranz": max(tol.values()) if tol else 0.01},
                "metadata": {"task": "sql", "referenz": f"evals/references/{datei}",
                             "von_hand_bestaetigt": fall.get("von_hand_bestaetigt", False)},
                "assert": _assert("sql_referenz"),
            })
    return tests


def kv_kontext(con: sqlite3.Connection) -> str:
    teile = []
    for (datei, url) in con.execute(
            "SELECT DISTINCT datei, quelle_url FROM kv_textblock ORDER BY datei"):
        teile.append(f"### Dokument: {datei}\nQuelle: {url}\n")
        teile += [f"[Z {z}] {t}" for z, t in con.execute(
            "SELECT zeile_original, text FROM kv_textblock WHERE datei = ? ORDER BY block_nr",
            (datei,))]
        teile.append("")
    return "\n".join(teile)


def kv_tests() -> list[dict]:
    ref = json.loads((REF / "kv_extraktion.json").read_text(encoding="utf-8"))
    out = []
    for fall in ref["faelle"]:
        nicht = ["bezugsgroesse"] if fall["fall_id"] == "kv_privatkrankenanstalten" else []
        out.append({
            "description": fall["fall_id"],
            "vars": {"reihe": fall["eingabe"]["reihe"],
                     "dokumente": "file://kontext/kv_dokumente.txt",
                     "erwartet": fall["erwartete_antwort"], "nicht_bewertet": nicht},
            "metadata": {"task": "kv_extraktion", "referenz": "evals/references/kv_extraktion.json",
                         "von_hand_bestaetigt": fall["von_hand_bestaetigt"]},
            "assert": _assert("extraktion"),
        })
    return out


def moebliert_tests() -> list[dict]:
    pfad = REF / "moebliert.json"
    if not pfad.exists():
        return []
    ref = json.loads(pfad.read_text(encoding="utf-8"))
    return [{"description": f["fall_id"],
             "vars": {"titel": f["eingabe"]["titel"], "erwartet": f["erwartete_antwort"]},
             "metadata": {"task": "moebliert", "referenz": "evals/references/moebliert.json",
                          "von_hand_bestaetigt": f.get("von_hand_bestaetigt", True)},
             "assert": _assert("klassifikation")} for f in ref["faelle"]]


def vorlage_kontext() -> tuple[str, str]:
    tabellen = []
    for pfad in sorted(C.PROCESSED.glob("kennzahl_*.csv")):
        with open(pfad, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f, delimiter=";"))
        tabellen.append(f"### {pfad.stem}\n" + "\n".join(";".join(r) for r in rows))
    port = json.loads((WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    annahmen = "\n".join(f"- {k}: {v['wert']} (Spanne {v.get('sensitivitaet')}) - {v.get('begruendung', '')}"
                         for k, v in port["annahmen"].items())
    return "\n\n".join(tabellen), annahmen


def vorlage_tests() -> list[dict]:
    return [
        {"description": "vorlage_jede_zahl_mit_herkunft", "vars": {"pfad": "docs/vorlage.md"},
         "metadata": {"task": "vorlage", "referenz": "data/processed/kennzahl_*.csv", "von_hand_bestaetigt": True},
         "assert": _assert("zahlen_herkunft")},
        {"description": "vorlage_pflichten", "vars": {"pfad": "docs/vorlage.md"},
         "metadata": {"task": "vorlage", "referenz": "prompts/vorlage_v1.md (Gliederung)", "von_hand_bestaetigt": True},
         "assert": _assert("vorlage_pflichten")},
    ]


def schreiben(name: str, daten) -> None:
    (TESTS / name).write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    TESTS.mkdir(parents=True, exist_ok=True)
    KONTEXT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(C.DB)
    (KONTEXT / "kv_dokumente.txt").write_text(kv_kontext(con), encoding="utf-8")
    con.close()
    k, a = vorlage_kontext()
    (KONTEXT / "vorlage_kennzahlen.txt").write_text(k + "\n", encoding="utf-8")
    (KONTEXT / "vorlage_annahmen.txt").write_text(a + "\n", encoding="utf-8")
    for name, tests in (("kennzahlen.json", kennzahlen_tests()), ("kv_extraktion.json", kv_tests()),
                        ("moebliert.json", moebliert_tests()), ("vorlage.json", vorlage_tests())):
        schreiben(name, tests)
        print(f"evals/tests/{name}: {len(tests)} Testfall/-faelle")
