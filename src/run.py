"""Die Pipeline. Ein Aufruf, vier Schritte, dieselben Zahlen bei jedem Lauf.

    python -m src.run

Ablauf:

    Schritt 1  extract    data/raw/<datum>/ -> data/interim/ + provenienz.json
    Schritt 2  clean      je Quelle eine saubere Tabelle, PII hier entfernt
               GATE 1     Eingangspruefung je Schnappschuss
               GATE 2     PII-Kontrolle
    Schritt 3  integrate  Datenbank loeschen, Schema anlegen, laden, verknuepfen
    Schritt 4  derive     alle kennzahl_*.sql -> data/processed/*.csv
               GATE 3     Plausibilitaet der Kennzahlen

Reproduzierbarkeit: die Datenbank wird bei jedem Lauf aus ALLEN Rohordnern
neu gebaut. data/raw/ ist die Quelle der Wahrheit, die Datenbank ist ein
Ergebnis und jederzeit verwerfbar. Deshalb meldet der zweite Lauf dieselben
Zahlen wie der erste.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

from . import clean, config as C, derive, extract, integrate


def kopf(nr: str, titel: str) -> None:
    print(f"\n{'─' * 72}\n{nr}  {titel}\n{'─' * 72}")


def gate(name: str, ok: bool, detail: str = "") -> None:
    print(f"\n  GATE {name}: {'bestanden' if ok else 'NICHT BESTANDEN'} {detail}")
    if not ok:
        print("  Abbruch. Es wird keine Entscheidungsvorlage erzeugt.")
        sys.exit(2)


def hauptlauf() -> int:
    start = datetime.now(timezone.utc)
    print(f"mietportfolio · Lauf {start.isoformat(timespec='seconds')}")

    kopf("Schritt 1", "Datenzugriff")
    prov = extract.ausfuehren()

    kopf("Schritt 2", "Auslesen und normalisieren")
    bereinigt = clean.ausfuehren()
    wh = bereinigt["willhaben"]

    gate("1", wh["zahlen"]["schnappschuesse"] > 0,
         f"({wh['zahlen']['schnappschuesse']} Schnappschuss/e aufgenommen, "
         f"{wh['zahlen']['abgelehnt']} abgelehnt)")
    gate("2", True, "(PII-Kontrolle in clean.willhaben, bricht dort ab)")

    kopf("Schritt 3", "Zusammenführen und ablegen")
    res = integrate.ausfuehren(bereinigt)
    con = res["con"]

    kopf("Schritt 4", "Abfragen und Kennzahlen")
    kennzahlen = derive.ausfuehren(con)

    kopf("GATE 3", "Plausibilität der Kennzahlen")
    pruef = []

    fehler_sql = [k for k in kennzahlen if "fehler" in k]
    pruef.append(("alle Abfragen laufen", not fehler_sql,
                  ", ".join(k["name"] for k in fehler_sql)))

    n = con.execute("SELECT COUNT(*) FROM inserat_beobachtung").fetchone()[0]
    pruef.append(("Beobachtungen vorhanden", n > 0, f"{n}"))

    # eur_pro_m2 des Portals muss zu Miete/Flaeche passen. Weicht es ab,
    # bedeutet ein Feld etwas anderes als angenommen.
    abw = con.execute(
        """SELECT COUNT(*) FROM inserat_beobachtung
           WHERE eur_pro_m2 IS NOT NULL AND miete_eur IS NOT NULL
             AND flaeche_m2 > 0
             AND ABS(miete_eur / flaeche_m2 - eur_pro_m2) > 0.02"""
    ).fetchone()[0]
    pruef.append(("Portal-€/m² stimmt mit Miete/Fläche", abw == 0,
                  f"{abw} Abweichung(en)"))

    # Median darf nicht ausserhalb von Min und Max liegen
    kaputt = con.execute(
        """SELECT COUNT(*) FROM v_marktniveau
           WHERE median_eur_m2 < min_eur_m2 OR median_eur_m2 > max_eur_m2"""
    ).fetchone()[0]
    pruef.append(("Median zwischen Min und Max", kaputt == 0, f"{kaputt}"))

    # Jede Beobachtung haengt an einem Bezirk (Fremdschluessel)
    waise = con.execute(
        """SELECT COUNT(*) FROM inserat_beobachtung io
           LEFT JOIN bezirk b ON b.plz = io.plz WHERE b.plz IS NULL"""
    ).fetchone()[0]
    pruef.append(("jede Beobachtung hat einen Bezirk", waise == 0, f"{waise}"))

    for name, ok, detail in pruef:
        print(f"  {'ok    ' if ok else 'FEHLER'} {name} {detail}")
    gate("3", all(ok for _, ok, _ in pruef))

    kopf("Zusammenfassung", "")
    print(f"  Rohordner       : {', '.join(prov['rohordner'])}")
    print(f"  Dateien         : {len(prov['dateien'])}")
    print(f"  Schnappschüsse  : {wh['zahlen']['schnappschuesse']} aufgenommen, "
          f"{wh['zahlen']['abgelehnt']} abgelehnt")
    print(f"  Beobachtungen   : {res['zahlen']['inserat_beobachtung']}")
    print(f"  Zuordnungslücken: {res['luecken']}")
    print(f"  Kennzahl-CSV    : {sum(1 for k in kennzahlen if 'fehler' not in k)}")
    print(f"  Datenbank       : data/processed/{C.DB.name}")

    warn = con.execute(
        "SELECT COUNT(*) FROM qs_befund WHERE stufe = 'warnung'").fetchone()[0]
    if warn:
        print(f"\n  {warn} Warnung(en) im Qualitätsbericht:")
        for r in con.execute(
                "SELECT objekt, pruefung, detail FROM qs_befund"
                " WHERE stufe = 'warnung'"):
            print(f"    {r['objekt']}: {r['detail']}")

    dauer = (datetime.now(timezone.utc) - start).total_seconds()
    print(f"\n  Laufzeit: {dauer:.1f} s")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(hauptlauf())
