"""Schritt 4: alle kennzahl_*.sql ausfuehren, Ergebnis als CSV ablegen.

Das Modell rechnet nie. Was in der Entscheidungsvorlage als Zahl steht, kommt
aus einer dieser CSV-Dateien und nennt sie als Herkunft.

Die Dateien landen in data/processed/kennzahl_<name>.csv und werden
committet - damit ist jede Zahl der Vorlage im Repo nachvollziehbar, auch
ohne die Datenbank neu zu bauen.
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from . import config as C


def abfragen() -> list[Path]:
    return sorted(C.SQL.glob("kennzahl_*.sql"))


def eine_ausfuehren(con: sqlite3.Connection, sql_pfad: Path) -> dict:
    name = sql_pfad.stem                      # kennzahl_marktniveau
    sql = sql_pfad.read_text(encoding="utf-8")
    try:
        rows = con.execute(sql).fetchall()
    except sqlite3.Error as e:
        return {"name": name, "fehler": str(e), "zeilen": 0}

    ziel = C.PROCESSED / f"{name}.csv"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with open(ziel, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        if rows:
            w.writerow(rows[0].keys())
            for r in rows:
                w.writerow([round(v, 4) if isinstance(v, float) else v
                            for v in r])
        else:
            # Kopfzeile auch bei leerem Ergebnis, damit die Datei
            # existiert und die Leere sichtbar ist
            beschreibung = con.execute(sql)
            if beschreibung.description:
                w.writerow([d[0] for d in beschreibung.description])
    return {"name": name, "zeilen": len(rows), "datei": ziel}


def ausfuehren(con: sqlite3.Connection) -> list[dict]:
    ergebnisse = []
    for pfad in abfragen():
        r = eine_ausfuehren(con, pfad)
        ergebnisse.append(r)
        if "fehler" in r:
            print(f"derive: FEHLER {r['name']}: {r['fehler']}")
        else:
            leer = "  <- leer, siehe Kommentar in der SQL-Datei" \
                   if r["zeilen"] == 0 else ""
            print(f"derive: {r['name']:<30} {r['zeilen']:>4} Zeile(n)"
                  f" -> data/processed/{r['name']}.csv{leer}")
    return ergebnisse


if __name__ == "__main__":
    con = sqlite3.connect(C.DB)
    con.row_factory = sqlite3.Row
    ausfuehren(con)
