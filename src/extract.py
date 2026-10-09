"""Schritt 1: Rohdaten nach data/interim/ kopieren, Provenienz schreiben.

Die Rohdateien unter data/raw/<datum>/ werden nie veraendert. Dieses Modul
kopiert sie und schreibt provenienz.json: je Datei Name, Groesse, SHA256,
Quelle, Abrufordner. Damit ist jede spaetere Zahl auf eine konkrete Datei
zurueckfuehrbar.

Der SHA256 hat einen zweiten Zweck: er faengt dieselbe Datei unter zwei Namen
ab. Genau das ist in diesem Projekt passiert, dreimal (siehe
docs/projektdokumentation/01_entscheidungslog.md, E-07).
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import config as C


def sha256(pfad: Path) -> str:
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for blk in iter(lambda: f.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def quelle_fuer(name: str) -> str | None:
    """Ordnet eine Datei anhand des Namensmusters einer Quelle zu."""
    for quelle, cfg in C.QUELLEN.items():
        if fnmatch.fnmatch(name, cfg["muster"]):
            return quelle
    return None


def ausfuehren(nur_neuester: bool = False) -> dict:
    """Kopiert alle Rohordner nach interim und schreibt die Provenienz.

    nur_neuester=True verarbeitet nur den juengsten Ordner - fuer schnelle
    Testlaeufe. Der Regelfall ist False: die Datenbank wird aus der ganzen
    Historie gebaut.
    """
    C.INTERIM.mkdir(parents=True, exist_ok=True)
    ordner = [C.neuester_rohordner()] if nur_neuester else C.alle_rohordner()
    if not ordner:
        raise SystemExit(f"keine Rohordner unter {C.RAW}")

    eintraege, je_quelle, ohne_zuordnung = [], {}, []
    gesehen_sha: dict[str, str] = {}

    for ord_ in ordner:
        abrufdatum = ord_.name
        for datei in sorted(ord_.iterdir()):
            if not datei.is_file() or datei.name.startswith("."):
                continue
            # Begleitdokumentation im Rohordner (HERKUNFT.md) ist Beleg, nicht
            # Datenquelle. Sie gehoert dorthin, weil sie die Dateien neben ihr
            # beschreibt - aber sie soll nicht als unzugeordnete Quelle gemeldet
            # werden.
            if datei.suffix.lower() == ".md":
                continue
            quelle = quelle_fuer(datei.name)
            if quelle is None:
                ohne_zuordnung.append(f"{abrufdatum}/{datei.name}")
                continue

            h = sha256(datei)
            ziel = C.INTERIM / abrufdatum / datei.name
            ziel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(datei, ziel)

            eintrag = {
                "quelle": quelle,
                "abrufdatum": abrufdatum,
                "datei": datei.name,
                "pfad_roh": str(datei.relative_to(C.WURZEL)),
                "pfad_interim": str(ziel.relative_to(C.WURZEL)),
                "bytes": datei.stat().st_size,
                "sha256": h,
                "form": C.QUELLEN[quelle]["form"],
                "beschaffung": C.QUELLEN[quelle]["beschaffung"],
                "lizenz": C.QUELLEN[quelle]["lizenz"],
            }
            if h in gesehen_sha:
                eintrag["warnung"] = (
                    f"byteweise identisch mit {gesehen_sha[h]} - typisch fuer "
                    f"ein nicht neu geladenes __NEXT_DATA__")
            else:
                gesehen_sha[h] = f"{abrufdatum}/{datei.name}"

            eintraege.append(eintrag)
            je_quelle[quelle] = je_quelle.get(quelle, 0) + 1

    fehlend = [q for q, cfg in C.QUELLEN.items()
               if cfg["pflicht"] and not je_quelle.get(q)]
    if fehlend:
        raise SystemExit(f"Pflichtquelle(n) fehlen: {', '.join(fehlend)}")

    provenienz = {
        "projekt": C.PROJEKT,
        "erstellt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rohordner": [o.name for o in ordner],
        "dateien": eintraege,
        "je_quelle": je_quelle,
        "ohne_zuordnung": ohne_zuordnung,
    }
    (C.INTERIM / "provenienz.json").write_text(
        json.dumps(provenienz, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"extract: {len(eintraege)} Datei(en) aus {len(ordner)} Rohordner(n)"
          f" -> data/interim/")
    for q, n in sorted(je_quelle.items()):
        print(f"         {q}: {n}")
    for e in eintraege:
        if "warnung" in e:
            print(f"         WARNUNG {e['abrufdatum']}/{e['datei']}: {e['warnung']}")
    if ohne_zuordnung:
        print(f"         keiner Quelle zugeordnet: {', '.join(ohne_zuordnung)}")
    return provenienz


if __name__ == "__main__":
    ausfuehren()
