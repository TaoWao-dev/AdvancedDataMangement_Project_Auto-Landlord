"""Gespeicherte Quelltextansicht (view-source:) -> Fliesstext mit Fundstelle.

    python3 tools/quelltext_zu_text.py <gespeichert.html> <ziel.txt>

Chrome speichert die Quelltextansicht als HTML-Tabelle: jede Zeile des
Originals steht in <td class="line-content">, die Zeilennummer in
<td class="line-number" value="N">. Das Werkzeug stellt zuerst den
Originalquelltext wieder her und zieht dann den sichtbaren Text heraus -
jeden Textblock mit der Zeilennummer, in der er im Original beginnt.

Warum die Zeilennummer: eine Referenzantwort braucht eine Fundstelle, die
ein Dritter nachschlagen kann (E28). "Zeile 2412 im Quelltext der Seite vom
23.10." ist nachpruefbar; "steht irgendwo auf der WKO-Seite" ist es nicht.

Was es nicht tut: zusammenfassen, kuerzen, umformulieren. Der Text in der
Ausgabe ist zeichengenau der Text der Seite, nur ohne Markup. Skripte,
Styles und Navigation werden verworfen, weil sie kein Seiteninhalt sind.

Nur Standardbibliothek. Keine Netzverbindung - die Seite hat ein Mensch
gespeichert (E06, E35).
"""
from __future__ import annotations

import hashlib
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class _Quelltextansicht(HTMLParser):
    """Liest die Tabelle der Quelltextansicht: Zeilennummer -> Rohtext."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.zeilen: list[tuple[int, str]] = []
        self._nr: int | None = None
        self._in_inhalt = False
        self._puffer: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and a.get("class") == "line-number":
            self._nr = int(a.get("value", "0"))
        elif tag == "td" and a.get("class") == "line-content":
            self._in_inhalt, self._puffer = True, []
        elif tag == "br" and self._in_inhalt:
            pass  # leere Zeile im Original

    def handle_endtag(self, tag):
        if tag == "td" and self._in_inhalt:
            self.zeilen.append((self._nr or 0, "".join(self._puffer)))
            self._in_inhalt = False

    def handle_data(self, data):
        if self._in_inhalt:
            self._puffer.append(data)


class _Sichtbar(HTMLParser):
    """Sichtbarer Text des wiederhergestellten Originals, mit Startzeile."""

    UNSICHTBAR = {"script", "style", "noscript", "svg", "head", "template"}
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th",
             "tr", "section", "article", "br", "dt", "dd", "header", "footer"}
    NAVIGATION = {"nav"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.bloecke: list[tuple[int, str]] = []
        self._tiefe_unsichtbar = 0
        self._puffer: list[str] = []
        self._start: int | None = None

    def _abschliessen(self):
        text = re.sub(r"\s+", " ", "".join(self._puffer)).strip()
        if text:
            self.bloecke.append((self._start or 0, text))
        self._puffer, self._start = [], None

    def handle_starttag(self, tag, attrs):
        if tag in self.UNSICHTBAR or tag in self.NAVIGATION:
            self._tiefe_unsichtbar += 1
        elif tag in self.BLOCK:
            self._abschliessen()

    def handle_endtag(self, tag):
        if tag in self.UNSICHTBAR or tag in self.NAVIGATION:
            self._tiefe_unsichtbar = max(0, self._tiefe_unsichtbar - 1)
        elif tag in self.BLOCK:
            self._abschliessen()

    def handle_data(self, data):
        if self._tiefe_unsichtbar or not data.strip():
            return
        if self._start is None:
            self._start = self.getpos()[0]
        self._puffer.append(data)


def original_herstellen(gespeichert: str) -> str:
    p = _Quelltextansicht()
    p.feed(gespeichert)
    if not p.zeilen:
        raise ValueError("keine Quelltextansicht: keine Zeilen mit class=line-content")
    # Zeilennummern muessen lueckenlos aufsteigen; sonst stimmen die
    # Fundstellen nicht mit der Seite ueberein.
    nummern = [n for n, _ in p.zeilen]
    if nummern != list(range(1, len(nummern) + 1)):
        raise ValueError("Zeilennummern nicht fortlaufend - Datei unvollstaendig?")
    return "\n".join(t for _, t in p.zeilen)


def sichtbarer_text(original: str) -> list[tuple[int, str]]:
    p = _Sichtbar()
    p.feed(original)
    p.close()
    p._abschliessen()
    return p.bloecke


def quell_url(gespeichert: str) -> str:
    m = re.search(r"<!-- saved from url=\(\d+\)(\S+) -->", gespeichert)
    return m.group(1) if m else "unbekannt"


def umwandeln(quelle: Path, ziel: Path) -> dict:
    roh = quelle.read_text(encoding="utf-8")
    original = original_herstellen(roh)
    bloecke = sichtbarer_text(original)
    kopf = [
        f"# quelle_url: {quell_url(roh)}",
        f"# gespeichert_als: {quelle.name}",
        f"# sha256_gespeichert: {hashlib.sha256(roh.encode('utf-8')).hexdigest()}",
        f"# zeilen_original: {original.count(chr(10)) + 1}",
        "# Format: <Zeile im Originalquelltext>\\t<sichtbarer Text, zeichengenau>",
    ]
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text("\n".join(kopf + [f"{n}\t{t}" for n, t in bloecke]) + "\n",
                    encoding="utf-8")
    return {"bloecke": len(bloecke), "url": quell_url(roh)}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    r = umwandeln(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{r['bloecke']} Textbloecke aus {r['url']} -> {sys.argv[2]}")
