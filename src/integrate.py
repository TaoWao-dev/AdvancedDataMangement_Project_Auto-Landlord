"""Schritt 3: bereinigte Tabellen in die SQLite-Datenbank laden.

Jeder Lauf loescht die Datenbank und baut sie neu. Die Quelle der Wahrheit
ist data/raw/ - nicht die Datenbank. Das macht den zweiten Lauf identisch
zum ersten und die Datenbank jederzeit verwerfbar.

Verknuepft wird ueber die PLZ. Ein Inserat mit einer PLZ, die nicht in
config.BEZIRKE steht, bekommt keinen Bezirk zugewiesen und wird in
zuordnungsluecke gezaehlt - sichtbar statt still.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from . import clean, config as C


def verbinde(pfad: Path | None = None) -> sqlite3.Connection:
    pfad = pfad or C.DB
    pfad.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(pfad)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def neu_aufbauen(pfad: Path | None = None) -> sqlite3.Connection:
    pfad = pfad or C.DB
    pfad.unlink(missing_ok=True)
    con = verbinde(pfad)
    con.executescript((C.SQL / "schema.sql").read_text(encoding="utf-8"))
    con.executescript((C.SQL / "views.sql").read_text(encoding="utf-8"))
    con.commit()
    return con


def _qs(con, objekt, pruefung, stufe, detail, datenstand=None) -> None:
    """Befund festhalten. datenstand ist der abruf_ts des betroffenen
    Schnappschusses, NICHT die Uhrzeit des Laufs - sonst unterscheiden sich
    zwei Laeufe, und die Datenbank waere keine reine Funktion von data/raw/.
    """
    con.execute("INSERT INTO qs_befund VALUES (?,?,?,?,?)",
                (datenstand, objekt, pruefung, stufe, detail))


def ausfuehren(bereinigt: dict | None = None,
               pfad: Path | None = None) -> dict:
    bereinigt = bereinigt if bereinigt is not None else clean.ausfuehren()
    con = neu_aufbauen(pfad)

    # Bezirke zuerst: sie sind das Fremdschluesselziel der Beobachtungen.
    con.executemany(
        "INSERT INTO bezirk (plz, bezirk_nr, bezirk_name, cluster_id, rolle)"
        " VALUES (?,?,?,?,?)",
        [(b["plz"], b["bezirk_nr"], b["bezirk_name"], b["cluster_id"],
          b["rolle"]) for b in C.BEZIRKE])

    wh = bereinigt.get("willhaben", {"zeilen": [], "schnappschuesse": [],
                                     "abgelehnt": []})
    bekannte_plz = {b["plz"] for b in C.BEZIRKE}

    # Schnappschuesse
    sid_je_datei: dict[str, int] = {}
    for s in wh["schnappschuesse"]:
        if s["plz"] not in bekannte_plz:
            con.execute(
                "INSERT INTO zuordnungsluecke VALUES (?,?,?,?)",
                ("willhaben", s["plz"],
                 "PLZ nicht in config.BEZIRKE - Bezirk ergaenzen", 1))
            _qs(con, s["datei"], "PLZ bekannt", "fehler",
                f"PLZ {s['plz']} steht nicht in config.BEZIRKE",
                s.get("abruf_ts"))
            continue
        cur = con.execute(
            """INSERT INTO snapshot (datei, sha256, abruf_ts, plz,
                                     treffer_gesamt, geliefert, vollstaendig)
               VALUES (?,?,?,?,?,?,?)""",
            (s["datei"], s["sha256"], s["abruf_ts"], s["plz"],
             s["treffer_gesamt"], s["geliefert"], s["vollstaendig"]))
        sid_je_datei[s["datei"]] = cur.lastrowid
        for w in s["warnungen"]:
            _qs(con, s["datei"], w.split(":")[0], "warnung", w, s["abruf_ts"])

    # Beobachtungen
    geschrieben = verworfen_plz = 0
    for z in wh["zeilen"]:
        sid = sid_je_datei.get(z["snapshot_datei"])
        if sid is None or z["plz"] not in bekannte_plz:
            verworfen_plz += 1
            continue
        con.execute(
            """INSERT OR IGNORE INTO inserat_beobachtung
               (snapshot_id, ad_id, abruf_ts, status, plz, miete_eur,
                flaeche_m2, wohnflaeche_m2, eur_pro_m2, zimmer, stock,
                objekttyp, freiflaeche, privat, gewerblich, veroeffentlicht,
                lagequalitaet)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (sid, z["ad_id"], z["abruf_ts"], z["status"], z["plz"],
             z["miete_eur"], z["flaeche_m2"], z["wohnflaeche_m2"],
             z["eur_pro_m2"], z["zimmer"], z["stock"], z["objekttyp"],
             z["freiflaeche"],
             int(bool(z["privat"])) if z["privat"] is not None else None,
             int(bool(z["gewerblich_anbieter"]))
             if z["gewerblich_anbieter"] is not None else None,
             z["veroeffentlicht"], z["lagequalitaet"]))
        geschrieben += 1
    if verworfen_plz:
        con.execute("INSERT INTO zuordnungsluecke VALUES (?,?,?,?)",
                    ("willhaben", "-", "Inserat ohne bekannte PLZ",
                     verworfen_plz))

    # Indexreihen, soweit beschafft
    idx = (bereinigt.get("tariflohnindex", {}).get("zeilen", [])
           + bereinigt.get("vpi", {}).get("zeilen", []))
    con.executemany(
        "INSERT OR REPLACE INTO indexreihe (reihe, jahr, indexwert, quelle)"
        " VALUES (?,?,?,?)",
        [(r["reihe"], r["jahr"], r["indexwert"], r["quelle"]) for r in idx])

    # abgelehnte Dateien in den Qualitaetsbericht
    for a in wh["abgelehnt"]:
        for g in a["gruende"]:
            _qs(con, a["datei"], g.split(":")[0], "fehler", g,
                a.get("abruf_ts"))

    con.commit()

    zahlen = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("snapshot", "bezirk", "inserat_beobachtung",
                        "indexreihe", "zuordnungsluecke")}
    luecken = con.execute(
        "SELECT SUM(anzahl) FROM zuordnungsluecke").fetchone()[0] or 0

    print(f"integrate: {C.DB.name}: "
          + ", ".join(f"{t} {n}" for t, n in zahlen.items())
          + f"; Zuordnungsluecken: {luecken}")
    for r in con.execute(
            """SELECT b.plz, b.bezirk_name, b.rolle,
                      COUNT(DISTINCT s.snapshot_id) n_snap,
                      COUNT(io.ad_id) n_beob
               FROM bezirk b
               LEFT JOIN snapshot s ON s.plz = b.plz
               LEFT JOIN inserat_beobachtung io ON io.snapshot_id = s.snapshot_id
               GROUP BY b.plz ORDER BY b.plz"""):
        stand = (f"{r['n_snap']} Schnappschuss/e, {r['n_beob']} Beobachtungen"
                 if r["n_snap"] else "noch nicht beschafft")
        print(f"           {r['plz']} {r['bezirk_name']:<16} "
              f"{r['rolle']:<10} {stand}")
    return {"con": con, "zahlen": zahlen, "luecken": luecken}


if __name__ == "__main__":
    ausfuehren()
