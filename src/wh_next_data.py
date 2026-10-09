"""Parser fuer willhaben-Suchseiten-Schnappschuesse.

Datenherkunft und Grenze
------------------------
Die willhaben-robots.txt (archiviert in docs/willhaben_robots_2026-09-25.txt)
verbietet im Kopfkommentar ausdruecklich jeden automatisierten Zugriff:

    "It is expressively forbidden to use spiders, search robots or other
     automatic methods to access willhaben.at."

Dieses Modul ruft deshalb NICHTS ab. Es liest ausschliesslich Dateien, die ein
Mensch im Browser geoeffnet und gespeichert hat. Der Abruf ist ein manueller
Arbeitsschritt (siehe docs/projektdokumentation/02_schritt1_datenzugriff.md), alles danach ist automatisiert
und reproduzierbar.

Technische Grundlage
--------------------
willhaben ist eine Next.js-Anwendung. Die vollstaendigen Daten aller Inserate
einer Suchseite stecken im Script-Block __NEXT_DATA__ als JSON. Der Parser
liest diese JSON-Struktur, NICHT das gerenderte DOM: die CSS-Klassennamen sind
styled-components-Hashes (Box-sc-wfmb7k-0 jiBisN) und wechseln bei jedem
Deploy.

Pfad zur Nutzlast:
    props.pageProps.searchResult.advertSummaryList.advertSummary[]

Jedes Inserat hat Felder auf oberster Ebene (id, advertStatus, description,
advertiserInfo) und eine Attributliste im Format
    {"attributes": {"attribute": [{"name": "PRICE", "values": ["1190"]}, ...]}}

Der Server liefert ausserdem searchResult.searchDate - den Zeitstempel des
Abrufs. Der wird verwendet, nicht die Uhrzeit des Parserlaufs: nur so bleibt
ein spaeter erneut verarbeiteter Schnappschuss demselben Zeitpunkt zugeordnet.

Gepruefte Feldabdeckung (Schnappschuss 1020 Wien, 25.09.2026, n=90)
-------------------------------------------------------------------
    90/90  ADID PRICE NUMBER_OF_ROOMS POSTCODE LOCATION PUBLISHED SEO_URL
           COORDINATES ISPRIVATE ORGID advertStatus
    89/90  ESTATE_SIZE PRICE/SQUARE_METER PROPERTY_TYPE RENT/PER_MONTH_LETTINGS
    64/90  FLOOR
    54/90  FREE_AREA_TYPE_NAME
    58/90  ORGNAME
Fehlende Werte werden als None uebernommen und NICHT geschaetzt.
"""
from __future__ import annotations

import hashlib
import html as _html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

NEXT_DATA_START = '{"props":{"pageProps"'
TAG = re.compile(r"<[^>]+>")


# --------------------------------------------------------------- Rohextraktion
def _json_block(text: str) -> str:
    """Schneidet das __NEXT_DATA__-Objekt heraus, klammerbalanciert.

    Ein einfaches Regex bis </script> genuegt nicht, weil im JSON selbst
    escapte Anfuehrungszeichen und Klammern vorkommen.
    """
    i = text.find(NEXT_DATA_START)
    if i < 0:
        raise ValueError(
            "__NEXT_DATA__ nicht gefunden. Wurde die Seite als HTML gespeichert? "
            "Erwartet wird der Seitenquelltext (view-source) oder der "
            "JSON-Block selbst.")
    depth, in_str, esc = 0, False, False
    for j, ch in enumerate(text[i:], start=i):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    raise ValueError("__NEXT_DATA__ unvollstaendig - Datei abgeschnitten?")


def lade_rohdaten(pfad: Path) -> dict:
    """Liest einen Schnappschuss.

    Verarbeitet drei Formen, weil im Browser verschiedene Speicherwege
    entstehen:
      * reines JSON (ueber die DevTools-Konsole heruntergeladen)
      * gespeicherter Seitenquelltext
      * gerenderte view-source-Seite (Syntax-Highlighting, HTML-escaped)
    """
    roh = pfad.read_text(encoding="utf-8", errors="replace")
    stripped = roh.lstrip()
    if stripped.startswith("{"):
        return json.loads(stripped)
    if NEXT_DATA_START in roh:
        return json.loads(_json_block(roh))
    # view-source-Variante: Tags weg, Entities dekodieren
    text = _html.unescape(TAG.sub("", roh))
    return json.loads(_json_block(text))


def sha256(pfad: Path) -> str:
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for blk in iter(lambda: f.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


# ------------------------------------------------------------------ Normierung
def _attr(advert: dict) -> dict:
    """Attributliste in ein Dict. Mehrwertige Felder bleiben Listen."""
    out = {}
    for a in advert.get("attributes", {}).get("attribute", []):
        v = a.get("values") or []
        out[a["name"]] = v[0] if len(v) == 1 else (v or None)
    return out


def _f(x) -> float | None:
    if x is None or isinstance(x, list):
        return None
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return None


def _i(x) -> int | None:
    v = _f(x)
    return None if v is None else int(v)


def _liste(x) -> list[str]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


@dataclass
class Inserat:
    ad_id: str
    abruf_ts: str            # searchDate des Servers, nicht Parserzeit
    status: str              # aktiv | reserviert | ...
    plz: str | None
    bezirk: str | None
    lage: str | None
    miete_eur: float | None          # PRICE, Bruttomiete laut Inserat
    flaeche_m2: float | None         # ESTATE_SIZE
    wohnflaeche_m2: float | None     # ESTATE_SIZE/LIVING_AREA
    eur_pro_m2: float | None         # PRICE/SQUARE_METER, vom Portal gerechnet
    zimmer: float | None
    stock: int | None
    objekttyp: str | None
    freiflaeche: list[str] = field(default_factory=list)
    privat: bool | None = None
    gewerblich_anbieter: bool | None = None
    veroeffentlicht: str | None = None
    lagequalitaet: float | None = None
    seo_url: str | None = None


@dataclass
class Schnappschuss:
    quelle: str
    abruf_ts: str
    vertical_id: int | None  # 2 = Immobilien. Die entscheidende Kennung:
                             # 5 waere der Marktplatz (Vorfall, siehe Gate 1)
    treffer_gesamt: int      # rowsFound - alles, was die Suche kennt
    geliefert: int           # rowsReturned - was auf dieser Seite steht
    angefordert: int         # rowsRequested
    ueberschrift: str | None
    inserate: list[Inserat]

    @property
    def vollstaendig(self) -> bool:
        """True, wenn die Seite alle Treffer enthaelt.

        Bei rowsFound > rowsReturned fehlen Inserate. Ein daraus gerechneter
        Median beschreibt dann nur die erste Seite, nicht den Markt - das
        muss im Qualitaetsbericht auftauchen.
        """
        return self.treffer_gesamt <= self.geliefert


def parse(pfad: Path) -> Schnappschuss:
    d = lade_rohdaten(pfad)
    try:
        sr = d["props"]["pageProps"]["searchResult"]
    except KeyError as e:
        raise ValueError(f"unerwartete JSON-Struktur, fehlend: {e}") from e

    abruf = sr.get("searchDate") or datetime.now(timezone.utc).isoformat()
    ads = sr.get("advertSummaryList", {}).get("advertSummary", []) or []

    inserate = []
    for a in ads:
        at = _attr(a)
        st = (a.get("advertStatus") or {}).get("description") or "unbekannt"
        info = a.get("advertiserInfo") or {}
        label = info.get("label")
        inserate.append(Inserat(
            ad_id=str(a.get("id") or at.get("ADID")),
            abruf_ts=abruf,
            status=st,
            plz=at.get("POSTCODE"),
            bezirk=at.get("DISTRICT"),
            lage=at.get("LOCATION"),
            miete_eur=_f(at.get("PRICE")),
            flaeche_m2=_f(at.get("ESTATE_SIZE")),
            wohnflaeche_m2=_f(at.get("ESTATE_SIZE/LIVING_AREA")),
            eur_pro_m2=_f(at.get("PRICE/SQUARE_METER")),
            zimmer=_f(at.get("NUMBER_OF_ROOMS")),
            stock=_i(at.get("FLOOR")),
            objekttyp=at.get("PROPERTY_TYPE") if isinstance(
                at.get("PROPERTY_TYPE"), str) else None,
            freiflaeche=_liste(at.get("FREE_AREA_TYPE_NAME")),
            privat=(at.get("ISPRIVATE") == "1") if at.get("ISPRIVATE") else None,
            gewerblich_anbieter=(label is not None and label != "Privat"),
            veroeffentlicht=at.get("PUBLISHED_String"),
            lagequalitaet=_f(at.get("LOCATION_QUALITY")),
            seo_url=at.get("SEO_URL"),
        ))

    return Schnappschuss(
        quelle=pfad.name,
        abruf_ts=abruf,
        vertical_id=(int(sr["verticalId"]) if str(sr.get("verticalId", "")).isdigit()
                     else None),
        treffer_gesamt=int(sr.get("rowsFound") or 0),
        geliefert=int(sr.get("rowsReturned") or len(inserate)),
        angefordert=int(sr.get("rowsRequested") or 0),
        ueberschrift=sr.get("heading"),
        inserate=inserate,
    )
