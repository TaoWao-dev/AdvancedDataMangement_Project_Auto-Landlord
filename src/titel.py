"""Merkmale, die sich aus dem Inseratstitel ableiten lassen - ohne den Titel zu behalten.

Der Titel selbst ist personenbezogen verdaechtig (E11) und wird beim
Redigieren entfernt. Was daraus als Ja/Nein-Merkmal ableitbar ist, wird DORT
berechnet, solange das Original vorliegt (tools/redigiere_schnappschuss.py),
und als Merkmal in die redigierte Datei geschrieben. Der Parser liest es von
dort; stehen dagegen noch Titel in der Datei (Original), berechnet er es selbst.

Gemeindewohnung (E34, E38)
--------------------------
Ob eine Wohnung eine Gemeindewohnung ist, laesst sich aus den gespeicherten
Daten NICHT sicher bestimmen: von 178 Titeln am 09.10. sagen es drei
ausdruecklich, bei allen anderen steht darin nichts. Dieses Merkmal heisst
deshalb `gemeinde_explizit` und bedeutet genau das, was dasteht - der Titel
NENNT es. Kein Wert heisst nicht "keine Gemeindewohnung", sondern "nicht
genannt". Ein Modell koennte daraus auch nicht mehr lesen (E37).

Bekannte Grenze: ein Titel wie "Neubau neben dem Gemeindebau" wuerde faelschlich
anschlagen. Bei drei Treffern in 178 Titeln ist das hinnehmbar und im Test
benannt; die Stichworte sind bewusst eng.
"""
from __future__ import annotations

import re

GEMEINDE_STICHWORTE = re.compile(
    r"gemeindebau|gemeindewohnung|wiener\s+wohnen|wohnticket", re.IGNORECASE)

# Wert, den die Redaktion an die Stelle des Titels setzt.
ENTFERNT = "[ENTFERNT]"


def gemeinde_explizit(titel: str | None) -> bool | None:
    """True/False, wenn ein Titel vorliegt; None, wenn er fehlt oder entfernt ist.

    None ist nicht False: "nicht pruefbar" muss vom Ergebnis "geprueft, nicht
    genannt" unterscheidbar bleiben (Luecken sichtbar machen statt fuellen).
    """
    if not titel or titel.strip() == ENTFERNT:
        return None
    return bool(GEMEINDE_STICHWORTE.search(titel))
