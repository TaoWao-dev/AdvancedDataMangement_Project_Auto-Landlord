"""Eingangspruefung fuer Schnappschuesse.

Anlass sind zwei echte Vorfaelle in diesem Projekt
--------------------------------------------------
**Vorfall 1 - falsche Seite.** Beim Beschaffen entstanden Dateien, benannt wie
die Mietwohnungssuche fuer einen Wiener Bezirk. Ihr Inhalt war die
Marktplatz-Gesamtliste:

    wh_1020_mietwohnungen_2026-09-25T1555.json
        verticalId 2 (Immobilien), searchId 131,
        rowsFound 154, 90 Inserate, alle PLZ 1020        -> richtig

    negativ_falscher_vertical.json
        verticalId 5 (Marktplatz), searchId 301,
        rowsFound 13.353.029, 30 Inserate, 24 PLZ        -> falsche Seite

Beide sind syntaktisch einwandfreies JSON derselben Struktur. Ohne Pruefung
haette die Pipeline aus der zweiten brav einen Median gerechnet - ueber
Gebrauchtwaren aus ganz Oesterreich - und nichts waere abgestuerzt.

**Vorfall 2 - dieselbe Datei unter drei Namen.** Spaeter kamen Dateien fuer
1010 und 1030 dazu. Beide waren byteweise identisch mit der falschen Datei
von oben, gleicher SHA256, gleiches searchDate.

Ursache: __NEXT_DATA__ ist ein statischer Script-Tag aus dem
Server-Rendering. Bei client-seitiger Navigation innerhalb der Next.js-App
bleibt er auf dem Stand der zuerst vom Server gelieferten Seite. Wer sich zur
Bezirkssuche durchklickt statt die URL neu zu laden, liest immer dieselbe
alte Seite aus.

Daraus folgen die Pruefungen unten und der selbstpruefende Helfer in
tools/snapshot.js, der den Abruf abbricht, statt eine falsche Datei zu
erzeugen.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

VERTICAL_IMMOBILIEN = 2
RE_PLZ_DATEINAME = re.compile(r"(?:^|[_-])(\d{4})(?:[_-]|$)")


@dataclass
class Befund:
    stufe: str      # fehler | warnung | ok
    pruefung: str
    detail: str


def plz_aus_dateiname(pfad: Path | str) -> str | None:
    """Liest die erwartete PLZ aus dem Dateinamen.

    Konvention: wh_<plz>_<suche>_<datum>.json

    Damit ist die Pruefung der Vorgabewert und nicht eine Option, die man
    vergessen kann. Genau dieses Vergessen hat Vorfall 2 durchgelassen,
    solange --plz nicht mitgegeben wurde.
    """
    m = RE_PLZ_DATEINAME.search(Path(pfad).stem)
    return m.group(1) if m else None


def pruefe(schnappschuss, erwartete_plz: str | None = None,
           min_inserate: int = 20) -> list[Befund]:
    """Prueft einen geparsten Schnappschuss.

    erwartete_plz: aus dem Dateinamen oder der Konfiguration. Wird sie
    uebergeben, muss die Mehrheit der Inserate sie tragen.
    """
    b: list[Befund] = []
    s = schnappschuss
    ins = s.inserate

    if not ins:
        b.append(Befund("fehler", "Inserate vorhanden",
                        "der Schnappschuss enthaelt keine Inserate"))
        return b

    # 0 Die richtige Rubrik? verticalId 2 ist Immobilien, 5 der Marktplatz.
    #   Das ist die direkteste Aussage darueber, ob die Datei ueberhaupt
    #   Wohnungen zeigt - deshalb steht sie vor allem anderen.
    if s.vertical_id is None:
        b.append(Befund("warnung", "richtige Rubrik",
                        "verticalId fehlt in der Datei"))
    elif s.vertical_id != 2:
        b.append(Befund("fehler", "richtige Rubrik",
                        f"verticalId = {s.vertical_id}, erwartet 2 "
                        f"(Immobilien). 5 waere der Marktplatz - dann ist "
                        f"eine andere Seite gespeichert worden."))
    else:
        b.append(Befund("ok", "richtige Rubrik", "verticalId 2 (Immobilien)"))

    # 1 Plausibilitaet der Trefferzahl. 13 Mio. ist die Marktplatz-Gesamtliste,
    #   eine Bezirkssuche liegt im dreistelligen Bereich.
    if s.treffer_gesamt > 100_000:
        n = f"{s.treffer_gesamt:,}".replace(",", ".")
        b.append(Befund("fehler", "Trefferzahl plausibel",
                        f"rowsFound = {n} - das ist keine Bezirkssuche, "
                        f"sondern eine Gesamtliste. Falsche Seite gespeichert?"))
    else:
        b.append(Befund("ok", "Trefferzahl plausibel",
                        f"rowsFound = {s.treffer_gesamt}"))

    # 2 Kommen alle Inserate aus derselben PLZ?
    plz_liste = [i.plz for i in ins if i.plz]
    if plz_liste:
        haeufigste = max(set(plz_liste), key=plz_liste.count)
        anteil = plz_liste.count(haeufigste) / len(plz_liste)
        if anteil < 0.9:
            b.append(Befund("fehler", "einheitliche PLZ",
                            f"nur {anteil:.0%} der Inserate liegen in "
                            f"{haeufigste}; {len(set(plz_liste))} PLZ insgesamt "
                            f"- vermutlich keine Bezirkssuche"))
        else:
            b.append(Befund("ok", "einheitliche PLZ",
                            f"{anteil:.0%} in {haeufigste}"))
        if erwartete_plz and haeufigste != erwartete_plz:
            b.append(Befund("fehler", "PLZ wie erwartet",
                            f"Dateiname sagt {erwartete_plz}, Daten sagen "
                            f"{haeufigste}. Haelt __NEXT_DATA__ noch eine "
                            f"frueher geladene Seite? Bezirks-URL neu laden."))
        elif erwartete_plz:
            b.append(Befund("ok", "PLZ wie erwartet", erwartete_plz))
    else:
        b.append(Befund("fehler", "einheitliche PLZ",
                        "kein Inserat traegt eine Postleitzahl"))

    # 3 Sind die Felder da, die wir brauchen?
    for name, n in (("Miete", sum(1 for i in ins if i.miete_eur)),
                    ("Flaeche", sum(1 for i in ins if i.flaeche_m2))):
        q = n / len(ins)
        b.append(Befund("fehler" if q < 0.5 else "warnung" if q < 0.9 else "ok",
                        f"Feldabdeckung {name}",
                        f"{n} von {len(ins)} ({q:.0%})"))

    # 4 Genug Faelle fuer eine Aussage?
    b.append(Befund("fehler" if len(ins) < min_inserate else "ok",
                    "Fallzahl",
                    f"{len(ins)} Inserate, Mindestzahl {min_inserate}"))

    # 5 Deckt die Seite alle Treffer ab?
    if not s.vollstaendig:
        b.append(Befund("warnung", "Vollstaendigkeit",
                        f"{s.geliefert} von {s.treffer_gesamt} Treffern auf "
                        f"dieser Seite. Der Median beschreibt die erste Seite, "
                        f"nicht den Markt - weitere Seiten speichern."))
    else:
        b.append(Befund("ok", "Vollstaendigkeit",
                        f"alle {s.treffer_gesamt} Treffer enthalten"))

    return b


def pruefe_gegen_bestand(con, schnappschuss, sha256: str) -> list[Befund]:
    """Prueft einen Schnappschuss gegen die schon aufgenommenen.

    Faengt Vorfall 2 ab: derselbe Inhalt unter einem neuen Namen. Der
    Eindeutigkeitsindex auf sha256 verhindert das Schreiben ohnehin, aber ein
    stummes "uebersprungen" erklaert dem Benutzer nicht, was schiefgelaufen
    ist - und ohne Erklaerung speichert er beim naechsten Mal wieder falsch.
    """
    b: list[Befund] = []
    doppelt = con.execute(
        "SELECT datei, plz, abruf_ts FROM snapshot WHERE sha256 = ?",
        (sha256,)).fetchone()
    if doppelt:
        b.append(Befund("fehler", "Inhalt schon vorhanden",
                        f"byteweise identisch mit '{doppelt['datei']}' "
                        f"(PLZ {doppelt['plz']}, {doppelt['abruf_ts']}). "
                        f"Typisch fuer ein nicht neu geladenes "
                        f"__NEXT_DATA__ - Bezirks-URL frisch aufrufen."))
        return b

    gleiche_zeit = con.execute(
        "SELECT datei, plz FROM snapshot WHERE abruf_ts = ? AND plz <> ?",
        (schnappschuss.abruf_ts, schnappschuss.inserate[0].plz or "")).fetchone()
    if gleiche_zeit:
        b.append(Befund("warnung", "Abrufzeit schon vorhanden",
                        f"gleiches searchDate wie '{gleiche_zeit['datei']}' "
                        f"(PLZ {gleiche_zeit['plz']}). Moeglich bei zwei "
                        f"Tabs in derselben Minute, aber auch ein Hinweis "
                        f"auf eine veraltete Seite."))
    return b


def bestanden(befunde: list[Befund]) -> bool:
    return not any(x.stufe == "fehler" for x in befunde)
