"""Grader fuer Analyse 5: keine Zahl in der Vorlage ohne Herkunft.

Der Revisionspunkt von E27 und E39: steht in docs/vorlage.md eine Zahl, die
in keiner Kennzahl-CSV vorkommt, ist die Grenze zwischen Programm und
Prompt verletzt. Geplant war dafuer ein LLM-Judge. Gebaut ist ein
deterministischer Abgleich, weil die Frage pruefbar ist (E27: was pruefbar
sein muss, gehoert in Code) und ein Judge-Modell selbst eine Zahl
uebersehen oder erfinden kann (E42).

Jede Zahl im Text bekommt eine Herkunft:
  kennzahl  ein Wert aus data/processed/kennzahl_*.csv, auf die im Text
            angegebene Stellenzahl gerundet (24,0 passt zu 24.01; 24,1 nicht)
  annahme   ein Parameter oder Spannenrand aus config/portfolio.json - die
            Vorlage muss die Annahmen nennen koennen, auf denen sie ruht
  konstante ein Eintrag in vorlage_konstanten.json, jeder mit Begruendung
  UNBEKANNT alles andere. Ein einziger Treffer laesst den Test scheitern.

Zitat bindet (seit 23.10., Gegenprobe an der Vorlage v1): steht im selben
Absatz oder in derselben Tabellenzeile ein Zitat [kennzahl_x], muss die Zahl
in genau dieser Datei vorkommen (oder eine benannte Annahme/Konstante sein).
Ohne diese Bindung passt fast jede kleine Zahl irgendwo: "40 der 50
Wohnungen" - verrechnet, richtig waere 30 - fand sich im Angebotsraster
und galt als belegt.

Nicht als Zahl gelesen werden Bezeichner (E39, A10, Q1, kennzahl_5),
Inhalte in `Backticks` mit Buchstaben darin, Markdown-Listennummern und
Jahreszahlen 2000-2035. Die Jahreszahl-Ausnahme ist eine bekannte Luecke:
ein erfundener Betrag von 2.030 EUR faellt nicht auf, 2030 ohne Punkt
schon gar nicht. Sie steht im Test als dokumentierter Fall.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[2]
KONSTANTEN = Path(__file__).with_name("vorlage_konstanten.json")

# Zahl im deutschen Format: 2.251.247 | 24,01 | 15 | 0,48 ; Datum separat.
DATUM = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(\d{4})(?![\d])")
ISO = re.compile(r"(?<![\d-])(\d{4})-(\d{2})-(\d{2})(?![\d])")
ZAHL = re.compile(
    r"(?<![\w.,])(-?)(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w])(\s*%)?")


def _bereinigen(text: str) -> str:
    # Bezeichner und Code zuerst entfernen, sonst wird aus 'E39' eine 39.
    text = re.sub(r"`[^`]*[A-Za-z_][^`]*`", " ", text)
    text = re.sub(r"\b[A-Za-zÄÖÜäöüß_]+[-_]?\d+[A-Za-z0-9_]*\b", " ", text)
    text = re.sub(r"(?m)^\s*\d+\.\s", " ", text)          # Listennummern
    text = re.sub(r"(?m)^#+\s*\d+(\.\d+)*\s", "# ", text)  # Abschnittsnummern
    text = re.sub(r"\]\([^)]*\)", "]", text)               # Linkziele
    return text


def zahlen_im_text(text: str) -> list[dict]:
    t = _bereinigen(text)
    gefunden = []
    for m in DATUM.finditer(t):
        gefunden.append({"roh": m.group(0), "art": "datum",
                         "wert": f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"})
    for m in ISO.finditer(t):
        gefunden.append({"roh": m.group(0), "art": "datum", "wert": m.group(0)})
    t = ISO.sub(" ", DATUM.sub(" ", t))
    for m in ZAHL.finditer(t):
        vorz, ganz, dez, prozent = m.group(1), m.group(2), m.group(3), m.group(4)
        ganz_wert = int(ganz.replace(".", ""))
        if not dez and not prozent and "." not in ganz and 2000 <= ganz_wert <= 2035:
            continue  # Jahreszahl (bekannte Luecke, siehe Modulkopf)
        wert = float(f"{ganz_wert}.{dez}" if dez else ganz_wert) * (-1 if vorz else 1)
        if dez:
            praezision = 10 ** -len(dez)
        else:
            nullen = len(str(ganz_wert)) - len(str(ganz_wert).rstrip("0"))
            # Erst ab drei Endnullen ist "rund 147.000" eine Rundung; "100"
            # ist eine Zahl, kein Hunderter-Intervall.
            praezision = 10 ** nullen if nullen >= 3 else 1
        gefunden.append({"roh": m.group(0).strip(), "art": "zahl", "wert": wert,
                         "praezision": praezision, "prozent": bool(prozent)})
    return gefunden


def quellen_laden(csv_muster: str = "data/processed/kennzahl_*.csv") -> dict:
    werte: list[tuple[float, str]] = []
    daten: dict[str, str] = {}
    for pfad in sorted(WURZEL.glob(csv_muster)):
        with open(pfad, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter=";"):
                for spalte, v in row.items():
                    if v is None or v == "":
                        continue
                    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                        daten.setdefault(v, f"{pfad.name}:{spalte}")
                        continue
                    try:
                        werte.append((float(v), f"{pfad.name}:{spalte}"))
                    except ValueError:
                        pass
    annahmen: list[tuple[float, str]] = []
    port = json.loads((WURZEL / "config" / "portfolio.json").read_text(encoding="utf-8"))
    for name, a in port["annahmen"].items():
        for w in [a["wert"]] + list(a.get("sensitivitaet", [])):
            annahmen.append((float(w), f"config/portfolio.json:{name}"))
    for a in port["angebotsraster"]["aufschlaege_pct"]:
        annahmen.append((float(a), "config/portfolio.json:angebotsraster"))
    konst = json.loads(KONSTANTEN.read_text(encoding="utf-8")) if KONSTANTEN.exists() else {"werte": []}
    konstanten = [(float(k["wert"]), f"konstante: {k['grund']}") for k in konst["werte"]
                  if not isinstance(k["wert"], str)]
    for k in konst["werte"]:
        if isinstance(k["wert"], str):
            daten.setdefault(k["wert"], f"konstante: {k['grund']}")
    return {"kennzahl": werte, "annahme": annahmen, "konstante": konstanten, "daten": daten}


def herkunft(z: dict, q: dict, zitate: set[str] | None = None) -> str | None:
    if z["art"] == "datum":
        return q["daten"].get(z["wert"])
    v, p = z["wert"], z["praezision"]
    if zitate:
        # Zitierte Datei zuerst und ausschliesslich unter den Kennzahlen;
        # Annahmen und Konstanten bleiben erlaubt.
        quellen = [("kennzahl", [(c, wo) for c, wo in q["kennzahl"]
                                 if wo.split(".csv")[0] in zitate]),
                   ("annahme", q["annahme"]), ("konstante", q["konstante"])]
    else:
        # Ohne Zitat: benannte Konstanten und Annahmen vor dem Zufallstreffer
        # in irgendeiner Spalte.
        quellen = [("konstante", q["konstante"]), ("annahme", q["annahme"]),
                   ("kennzahl", q["kennzahl"])]
    for art, liste in quellen:
        for c, wo in liste:
            if abs(c - v) <= p / 2 + 1e-9:
                return f"{art} {wo}"
            # Anteile: 0,482 in der CSV darf als 48 % im Text stehen.
            if z["prozent"] and abs(c) <= 1.5 and abs(c * 100 - v) <= p / 2 + 1e-9:
                return f"{art} {wo} (als Prozent)"
            # Anteile andersherum: 0,12 Marktrisikoabschlag als 12 %.
    return None


def bloecke(text: str) -> list[str]:
    """Absaetze; Tabellenzeilen und Listenpunkte je fuer sich."""
    out, puffer = [], []
    for zeile in text.splitlines():
        if zeile.lstrip().startswith(("|", "- ", "* ")) or re.match(r"^\s*\d+\.\s", zeile):
            if puffer:
                out.append("\n".join(puffer)); puffer = []
            out.append(zeile)
        elif not zeile.strip():
            if puffer:
                out.append("\n".join(puffer)); puffer = []
        else:
            puffer.append(zeile)
    if puffer:
        out.append("\n".join(puffer))
    return out


def pruefen(text: str, quellen: dict | None = None) -> dict:
    q = quellen or quellen_laden()
    zahlen, unbekannt, belegt = [], [], []
    for b in bloecke(text):
        zitate = set(re.findall(r"\[(kennzahl_[a-z_]+)\]", b))
        for z in zahlen_im_text(b):
            zahlen.append(z)
            h = herkunft(z, q, zitate)
            (belegt if h else unbekannt).append({**z, "herkunft": h, "zitiert": bool(zitate)})
    ok = not unbekannt
    grund = (f"{len(belegt)} Zahlen, alle belegt" if ok else
             f"{len(unbekannt)} von {len(zahlen)} Zahlen ohne Herkunft: "
             + ", ".join(sorted({u['roh'] for u in unbekannt})))
    return {"pass": ok, "score": (len(belegt) / len(zahlen)) if zahlen else 1.0,
            "reason": grund, "belegt": belegt, "unbekannt": unbekannt}


def get_assert(output, context):
    r = pruefen(output)
    return {"pass": r["pass"], "score": r["score"], "reason": r["reason"]}
