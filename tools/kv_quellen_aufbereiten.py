"""Gespeicherte KV-Seiten -> redigierte Textdateien in data/raw/<datum>/.

    python3 tools/kv_quellen_aufbereiten.py <datum> <gespeichert.html> [...]

Gleiche Logik wie bei den Inseraten (E06, E21): ein Mensch speichert die
Seite mit view-source:, die Originale bleiben lokal (data/raw_original/,
gitignored), ins Repository kommt eine beschnittene, redigierte Fassung mit
der SHA256 des Originals in HERKUNFT.md.

Beschnitten wird auf den Seiteninhalt, nicht auf "das Relevante":

  oegb   alles ab "Hier findest du aktuelle KV-Abschluesse" bis vor
         "Wichtige Links". Darin stehen auch die Abschluesse 2025 und 2024
         und die laufenden Forderungen - absichtlich, denn genau das muss
         das Modell auseinanderhalten. Vorher steht die Autorenzeile der
         Seite; sie ist ein Personenname und bleibt draussen (Regel 1).
  wko    die Zeilen mit "gueltig ab" (die Liste der KV-Fassungen) und die
         Geltungsdauer. Der Rest der WKO-Seiten ist Navigation; die
         Prozentsaetze stehen in PDFs, die nicht gespeichert wurden.

Danach laeuft clean.redigiere_text ueber jeden Block. Ein Treffer bricht
nicht ab, er wird ersetzt und gezaehlt - wie in Gate 2.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
sys.path.insert(0, str(WURZEL / "tools"))

from quelltext_zu_text import original_herstellen, quell_url, sichtbarer_text  # noqa: E402
from src.clean import redigiere_text  # noqa: E402

OEGB_START = "Hier findest du aktuelle KV-Abschlüsse"
OEGB_ENDE = "Wichtige Links"


def kurzname(url: str) -> tuple[str, str]:
    if "oegb.at" in url:
        return "oegb", "oegb"
    m = re.search(r"wko\.at/(?:wien/)?(?:kollektivvertraege|kollektivvertrag)/([^/?#]+)", url)
    if not m:
        raise ValueError(f"unbekannte Quelle: {url}")
    slug = re.sub(r"^kollektivvertrag-", "", m.group(1))
    slug = re.sub(r"-20\d\d$", "", slug)
    return "wko", slug


def beschneiden(art: str, bloecke: list[tuple[int, str]]) -> list[tuple[int, str]]:
    if art == "oegb":
        start = next(i for i, (_, t) in enumerate(bloecke) if t.startswith(OEGB_START))
        ende = next(i for i, (_, t) in enumerate(bloecke) if t == OEGB_ENDE)
        return bloecke[start:ende]
    behalten = []
    for i, (n, t) in enumerate(bloecke):
        if "gültig ab" in t:
            behalten.append((n, t))
        elif t.rstrip(":") == "Geltungsdauer" and i + 1 < len(bloecke):
            behalten += [(n, t), bloecke[i + 1]]
    return behalten


def aufbereiten(datum: str, quelle: Path) -> dict:
    roh = quelle.read_text(encoding="utf-8")
    url = quell_url(roh)
    art, slug = kurzname(url)
    bloecke = beschneiden(art, sichtbarer_text(original_herstellen(roh)))
    treffer: list[str] = []
    sauber = []
    for n, t in bloecke:
        t2, tr = redigiere_text(t)
        treffer += tr
        sauber.append((n, t2))
    name = f"kv_{art}_{datum}.txt" if art == "oegb" else f"kv_{art}_{slug}_{datum}.txt"
    ziel = WURZEL / "data" / "raw" / datum / name
    ziel.parent.mkdir(parents=True, exist_ok=True)
    kopf = [f"# quelle_url: {url}",
            f"# abruf: {datum}, manuell im Browser (view-source:) gespeichert",
            f"# sha256_original: {hashlib.sha256(roh.encode('utf-8')).hexdigest()}",
            "# Format: <Zeile im Originalquelltext>\\t<sichtbarer Text>",
            f"# beschnitten: {'Seiteninhalt ohne Autorenzeile und Navigation' if art == 'oegb' else 'nur Liste der KV-Fassungen und Geltungsdauer'}",
            f"# redigiert: {len(treffer)} Kontaktmuster ersetzt"]
    ziel.write_text("\n".join(kopf + [f"{n}\t{t}" for n, t in sauber]) + "\n", encoding="utf-8")
    return {"datei": name, "url": url, "bloecke": len(sauber), "redigiert": len(treffer),
            "sha256_original": hashlib.sha256(roh.encode("utf-8")).hexdigest(),
            "sha256_redigiert": hashlib.sha256(ziel.read_bytes()).hexdigest()}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    for p in sys.argv[2:]:
        r = aufbereiten(sys.argv[1], Path(p))
        print(f"{r['datei']}: {r['bloecke']} Bloecke, {r['redigiert']} redigiert, "
              f"Original {r['sha256_original'][:12]}…")
