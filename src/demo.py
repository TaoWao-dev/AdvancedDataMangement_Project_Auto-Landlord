"""Der Demo-Fall auf einen Blick (E44).

    python3 -m src.run            # zuerst: Datenbank und Kennzahlen
    python3 -m src.demo           # Mieterverzeichnis mit Empfehlung
    python3 -m src.demo LS-27     # ein Vertrag, Schritt fuer Schritt

Liest ausschliesslich data/processed/kennzahl_*.csv - also genau das, was
auch die Vorlage zitiert. Schreibt zusaetzlich docs/demo/mieterverzeichnis.html,
eine statische Seite fuer die Praesentation. Rechnet nichts neu.
"""
from __future__ import annotations

import csv
import html
import sys
from pathlib import Path

from . import config as C

ZIEL_HTML = C.WURZEL / "docs" / "demo" / "mieterverzeichnis.html"


def lies(name: str) -> list[dict]:
    with open(C.PROCESSED / f"{name}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def de(x: str, nach: int = 1) -> str:
    if x in ("", None):
        return "-"
    return f"{float(x):,.{nach}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tabelle(vertraege: list[dict]) -> None:
    kopf = f"{'Vertrag':<7}{'Größe':>7}{'Branche':>10}{'letzte Erh.':>12}{'Miete/m²':>9}" \
           f"{'Markt Δ':>9}{'KV Δ':>7}{'Lücke':>7}  {'Empfehlung':<16}{'neu/m²':>7}{'p':>6}"
    print(kopf)
    print("─" * len(kopf))
    for v in vertraege:
        emp = f"+{de(v['erhoehung_pct'], 0)} %" if v["empfehlung"] == "erhoehen" else "nicht erhöhen"
        print(f"{v['vertrag_id']:<7}{v['groessenklasse']:>7}{v['branche_id']:>10}"
              f"{v['letzte_anpassung']:>12}{de(v['miete_aktuell_eur_m2'], 2):>9}"
              f"{de(v['markt_veraenderung_pct']) + '%':>9}{de(v['kv_seit_anpassung_pct']) + '%':>7}"
              f"{de(v['luecke_zum_markt_pct']) + '%':>7}  {emp:<16}"
              f"{de(v['neue_miete_eur_m2'], 2):>7}{de(v['p_annahme'], 2):>6}")


def erklaeren(v: dict, kv: list[dict]) -> None:
    print(f"\nVertrag {v['vertrag_id']}: {de(v['flaeche_m2'])} m², Größenklasse {v['groessenklasse']}, "
          f"Branche {v['branche_id']}")
    print(f"  1  Miete heute            {de(v['miete_aktuell_eur'], 2)} € = {de(v['miete_aktuell_eur_m2'], 2)} €/m²,"
          f" zuletzt erhöht {v['letzte_anpassung']}")
    vor = " (Erhöhung liegt vor unserer ersten Marktbeobachtung)" if v["bezug_vor_beobachtung"] == "1" else ""
    print(f"  2  Markt seit Erhöhung    {de(v['markt_bezug_eur_m2'], 2)} → {de(v['markt_jetzt_eur_m2'], 2)} €/m²"
          f" ({de(v['markt_veraenderung_pct'])} %), Bezug {v['markt_bezug_datum']}{vor}")
    print(f"  3  Abstand zum Markt      {de(v['luecke_zum_markt_pct'])} %")
    abschl = [k for k in kv if k["branche_id"] == v["branche_id"]]
    print(f"  4  KV-Lohn der Branche    seit Erhöhung {de(v['kv_seit_anpassung_pct'], 2)} %, "
          f"seit Vertragsbeginn {de(v['kv_seit_abschluss_pct'], 2)} %")
    for k in abschl:
        ang = " (Tag nicht in der Quelle)" if k["datum_angenommen"] == "1" else ""
        deck = f", Deckel {de(k['deckel_eur'], 0)} €" if k["deckel_eur"] else ""
        print(f"       {k['jahr']}: {de(k['satz_index'], 2)} % ab {k['gueltig_ab']}{ang}{deck}"
              f"  [{k['quelle_datei']}, Zeile {k['quelle_zeile']}]")
    print(f"  5  Lohnzettel bei Abschluss Ø {de(v['gehalt_lohnzettel_eur_monat'], 0)} € brutto/Monat; "
          f"Belastungsquote heute {de(float(v['belastungsquote_jetzt']) * 100)} %")
    if v["empfehlung"] == "erhoehen":
        print(f"  ⇒  Empfehlung: um {de(v['erhoehung_pct'], 0)} % erhöhen auf {de(v['neue_miete_eur'], 2)} € "
              f"({de(v['neue_miete_eur_m2'], 2)} €/m²). Annahme wahrscheinlich zu {de(float(v['p_annahme']) * 100, 0)} %, "
              f"Belastungsquote danach {de(float(v['belastungsquote_neu']) * 100)} %, "
              f"Mehrwert über 5 Jahre {de(v['mehrwert_5j_eur'], 0)} €.")
    else:
        print("  ⇒  Empfehlung: nicht erhöhen - die Miete liegt am oder über dem Markt.")
    print("     Das Einkommen bestimmt nur, wie wahrscheinlich der Mieter annimmt - nicht die Höhe (E05, E44).")


def html_seite(vertraege: list[dict], segmente: list[dict], markt: list[dict], kv: list[dict]) -> str:
    def zeile(zellen, tag="td"):
        return "<tr>" + "".join(f"<{tag}>{html.escape(str(z))}</{tag}>" for z in zellen) + "</tr>"
    v_rows = "\n".join(zeile([
        v["vertrag_id"], v["groessenklasse"], v["branche_id"], v["letzte_anpassung"],
        de(v["miete_aktuell_eur_m2"], 2), de(v["markt_jetzt_eur_m2"], 2),
        de(v["markt_veraenderung_pct"]) + " %" + (" *" if v["bezug_vor_beobachtung"] == "1" else ""),
        de(v["kv_seit_anpassung_pct"], 2) + " %", de(v["luecke_zum_markt_pct"]) + " %",
        ("+" + de(v["erhoehung_pct"], 0) + " %") if v["empfehlung"] == "erhoehen" else "nicht erhöhen",
        de(v["neue_miete_eur_m2"], 2), de(float(v["p_annahme"]) * 100, 0) + " %"]) for v in vertraege)
    m_rows = "\n".join(zeile([m["groessenklasse"], m["abruf_datum"], m["fallzahl"], de(m["median_eur_m2"], 2),
                              m["belastbarkeit"], de(m["veraenderung_seit_erstem_abruf_pct"]) + " %"])
                       for m in markt if m["im_portfolio"] == "1")
    k_rows = "\n".join(zeile([k["branche_id"], k["jahr"], k["gueltig_ab"] + (" *" if k["datum_angenommen"] == "1" else ""),
                              de(k["satz_index"], 2) + " %", (de(k["deckel_eur"], 0) + " €") if k["deckel_eur"] else "",
                              f"Zeile {k['quelle_zeile']}"]) for k in kv)
    s_rows = "\n".join(zeile([s["groessenklasse"], s["marktmiete_eur_m2"].replace(".", ","), s["marktmiete_fallzahl"],
                              s["vertraege"], s["erhoehen"], de(s["median_erhoehung_pct"], 0) + " %",
                              de(s["mehrwert_gegen_ohne_erhoehung"], 0) + " €"]) for s in segmente)
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Mieterverzeichnis Demo</title>
<style>
:root {{ --bg:#fbfaf7; --fg:#1d1d1b; --muted:#6b6a64; --line:#dedbd2; --akzent:#9a3412; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#16161a; --fg:#ecebe6; --muted:#9a9890; --line:#33333a; --akzent:#fb923c; }} }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.45 system-ui,sans-serif; margin:0 auto; max-width:1100px; padding:24px 16px; }}
h1 {{ font-size:1.5rem; margin:0 0 4px; }} h2 {{ font-size:1.1rem; margin:28px 0 8px; }}
p.hinweis {{ color:var(--muted); margin:4px 0 12px; }}
.scroll {{ overflow-x:auto; }} table {{ border-collapse:collapse; width:100%; font-variant-numeric:tabular-nums; }}
th,td {{ border-bottom:1px solid var(--line); padding:5px 8px; text-align:right; white-space:nowrap; }}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2),th:nth-child(3),td:nth-child(3) {{ text-align:left; }}
th {{ color:var(--muted); font-weight:600; }}
</style></head><body>
<h1>Mieterverzeichnis mit Empfehlung — Demo-Fall 1020 Wien</h1>
<p class="hinweis">Synthetische Mieter, echte Marktdaten (willhaben, drei Abrufe) und extrahierte KV-Abschlüsse (ÖGB/WKO, Gate 4).
Erzeugt von <code>python3 -m src.demo</code> aus <code>data/processed/kennzahl_*.csv</code>. Keine echten Personen.</p>
<h2>Je Größenklasse</h2><div class="scroll"><table>
{zeile(["Größe", "Markt €/m²", "Fallzahl", "Verträge", "erhöhen", "Median Erhöhung", "Mehrwert 5 J."], "th")}
{s_rows}</table></div>
<h2>Je Vertrag</h2>
<p class="hinweis">* letzte Erhöhung liegt vor dem ersten Abruf (25.09.2026) — die Marktveränderung misst nur die Zeit seither.
Das Einkommen bestimmt die Annahmewahrscheinlichkeit, nicht die Höhe der Empfehlung.</p>
<div class="scroll"><table>
{zeile(["Vertrag", "Größe", "Branche", "letzte Erh.", "Miete €/m²", "Markt €/m²", "Markt Δ", "KV Δ seit Erh.", "Lücke", "Empfehlung", "neu €/m²", "Annahme"], "th")}
{v_rows}</table></div>
<h2>Marktentwicklung (14-tägige Kontrolle)</h2><div class="scroll"><table>
{zeile(["Größe", "Abruf", "Fallzahl", "Median €/m²", "Belastbarkeit", "seit erstem Abruf"], "th")}
{m_rows}</table></div>
<p class="hinweis">Der erste Abruf war eine Teilseite (90 von 154 Inseraten); ein Teil der Veränderung ist Auswahl, nicht Markt.</p>
<h2>KV-Abschlüsse je Branche (LLM-Extraktion, gegen Wortlaut geprüft)</h2><div class="scroll"><table>
{zeile(["Branche", "Jahr", "gültig ab", "Satz", "Deckel", "Fundstelle ÖGB-Seite"], "th")}
{k_rows}</table></div>
<p class="hinweis">* Tag nicht in der Quelle, gerechnet ab 1. Jänner.</p>
</body></html>
"""


def main(argv: list[str]) -> int:
    vertraege = lies("kennzahl_empfehlung_vertrag")
    kv = lies("kennzahl_kv_entwicklung")
    if argv:
        v = next((x for x in vertraege if x["vertrag_id"] == argv[0]), None)
        if v is None:
            print(f"Vertrag {argv[0]} nicht im Verzeichnis")
            return 1
        erklaeren(v, kv)
        return 0
    segmente = lies("kennzahl_empfehlung")
    for s in segmente:
        print(f"{s['groessenklasse']}: Markt {de(s['marktmiete_eur_m2'], 2)} €/m² (n={s['marktmiete_fallzahl']}, "
              f"{s['eignung']}), {s['erhoehen']} von {s['vertraege']} erhöhen, "
              f"Median {de(s['median_erhoehung_pct'], 0)} %")
    print()
    tabelle(vertraege)
    ZIEL_HTML.parent.mkdir(parents=True, exist_ok=True)
    ZIEL_HTML.write_text(html_seite(vertraege, segmente, lies("kennzahl_marktentwicklung"), kv), encoding="utf-8")
    print(f"\nSeite: {ZIEL_HTML.relative_to(C.WURZEL)}   ·   Einzelner Vertrag: python3 -m src.demo LS-27")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
