"""Erzeugt evals/references/kv_extraktion.json aus den gespeicherten KV-Seiten.

    python3 evals/erfasse_kv_referenz.py

Warum ein Skript und nicht eine handgeschriebene JSON-Datei: das Feld
`rohtext` muss woertlich aus dem Quelldokument stammen (E02, E28). Das Skript
liest den Satz aus data/raw/<datum>/kv_*.txt ueber seine Originalzeile und
bricht ab, wenn der erwartete Wortlaut dort nicht steht. Eine Nachschrift,
ein Tippfehler oder eine geaenderte Quelldatei fallen damit sofort auf.

Was das Skript NICHT kann: entscheiden, ob die erwartete Antwort richtig
gelesen ist. Die Felder unter `erwartet` sind eine Lesung des Rohtexts
(Claude, 23.10.2026) und gelten erst, wenn der Studierende sie bestaetigt
hat - dann `BESTAETIGT` unten ergaenzen und neu laufen lassen.
`von_hand_bestaetigt` wird nie aus Bequemlichkeit true.
"""
from __future__ import annotations

import json
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATUM = "2026-10-23"
OEGB = f"kv_oegb_{DATUM}.txt"
ZIEL = WURZEL / "evals" / "references" / "kv_extraktion.json"

# Fall-IDs, die der Studierende geprueft hat, mit Datum.
# 23.10.2026, Studierender nach Durchsicht der Pruefliste: "Lass einfach die
# Berufsgruppe der Wirtschaftstreuhaender aus. Der Rest der KV-Daten passt."
# Der Fall Wirtschaftstreuhaender ist deshalb entfernt (E48); die uebrigen
# sieben gelten als bestaetigt, ohne Korrektur an den erwarteten Feldern.
BESTAETIGT: dict[str, str] = {f: "2026-10-23" for f in (
    "kv_banken", "kv_versicherung_innendienst", "kv_it", "kv_elektroindustrie",
    "kv_handel_angestellte", "kv_privatkrankenanstalten", "kv_oeffentlicher_dienst")}

FRAGE = ("Welcher Kollektivvertragsabschluss gilt fuer das Jahr 2026 fuer die "
         "Reihe '{reihe}'? Antworte nur aus den beigefuegten Dokumenten.")

# Jeder Fall: Reihe aus config/berufsgruppen.json (bzw. die Vergleichsreihe),
# erwartete Antwort, und die Fundstellen als (Datei, Originalzeile, Wortlaut-Auszug).
# Der Auszug muss im Block dieser Zeile woertlich vorkommen.
FAELLE = [
    {
        "id": "kv_banken",
        "gruppe_id": "BANK",
        "reihe": "Banken und Bankiers",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 3.0, "prozent_max": 3.0,
                     "fixbetrag_eur": 5.0, "ist_prozent": None,
                     "geltungsbeginn": "2026-04-01", "bezugsgroesse": "kv_mindest",
                     "deckelung": False, "fundstelle_zeile": 1258},
        "fundstellen": [
            (OEGB, 1258, "Die kollektivvertraglichen Mindestgehälter der rund 68.000 Beschäftigten des Finanzsektors steigen um drei Prozent sowie einen Fixbetrag von fünf Euro."),
            (f"kv_wko_banken-und-bankiers_{DATUM}.txt", 415, "ab 1.4.2026"),
        ],
        "ablenker": [(OEGB, 3488, "Anhebung der Mindestgehälter um drei Prozent geeinigt")],
        "unsicherheit": "Die OeGB-Seite spricht vom 'Finanzsektor', nicht woertlich vom KV Banken und Bankiers, und nennt kein Datum. Das Datum stammt aus der WKO-Liste der KV-Fassungen (gueltig ab 1.4.2026). Der Ablenker 2025 hat denselben Prozentsatz - ein Modell kann ihn treffen und trotzdem den falschen Abschnitt gelesen haben; deshalb zaehlt die Fundstelle.",
    },
    {
        "id": "kv_versicherung_innendienst",
        "gruppe_id": "VERS",
        "reihe": "Versicherungsunternehmungen/Innendienst",
        "erwartet": {"abschluss_gefunden": False, "prozent_min": None, "prozent_max": None,
                     "fixbetrag_eur": None, "ist_prozent": None,
                     "geltungsbeginn": "2026-03-01", "bezugsgroesse": None,
                     "deckelung": None, "fundstelle_zeile": None},
        "fundstellen": [
            (f"kv_wko_versicherungsunternehmen_{DATUM}.txt", 400, "Kollektivvertrag Versicherungsunternehmen Innendienst, Angestellte, gültig ab 1.3.2026"),
        ],
        "ablenker": [(OEGB, 3623, "im Innendienst um 2,9 % plus 19,50 Euro")],
        "unsicherheit": "Fuer 2026 nennt keine Quelle einen Prozentsatz; die WKO-Liste belegt nur, dass eine Fassung ab 1.3.2026 existiert. Richtig ist: Geltungsbeginn ja, Prozentsatz nein. Wer 2,9 % nennt, hat den Abschluss 2025 uebernommen.",
    },
    {
        "id": "kv_it",
        "gruppe_id": "IT",
        "reihe": "Fachverband Unternehmensberatung, Buchhaltung und Informationstechnologie (IT-KV)",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 2.7, "prozent_max": 3.1,
                     "fixbetrag_eur": None, "ist_prozent": 2.75,
                     "geltungsbeginn": "2026-01-01", "bezugsgroesse": "kv_mindest",
                     "deckelung": False, "fundstelle_zeile": 1806},
        "fundstellen": [
            (OEGB, 1806, "Die Mindestgehälter steigen rückwirkend mit 1. 1. 2026 sozial gestaffelt zwischen 3,1 und 2,7 Prozent. Die IST-Gehaltssumme sowie Zulagen werden um 2,75 Prozent erhöht."),
        ],
        "ablenker": [(OEGB, 680, "um 3,9 Prozent"), (OEGB, 4796, "Die Mindestgehälter aller Tätigkeitsfamilien steigen um 3,2 Prozent")],
        "unsicherheit": "Gestaffelt: ein einzelner Prozentsatz ist falsch, die Spanne richtig. 3,9 % ist eine laufende Forderung fuer die naechste Runde, kein Abschluss. Die Reihe in config/berufsgruppen.json ist die Fachverbandsebene UBIT (A3); der OeGB-Text nennt die 'IT-Branche'.",
    },
    {
        "id": "kv_elektroindustrie",
        "gruppe_id": "INDUSTRIE",
        "reihe": "Elektro- u. Elektronikindustrie",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 3.0, "prozent_max": 3.0,
                     "fixbetrag_eur": None, "ist_prozent": 2.7,
                     "geltungsbeginn": "2026-05-01", "bezugsgroesse": "kv_mindest",
                     "deckelung": False, "fundstelle_zeile": 1069},
        "fundstellen": [
            (OEGB, 1054, "Mehr Geld für 60.000 Beschäftigte der Elektro- und Elektronikindustrie"),
            (OEGB, 1069, "Die Mindestlöhne und Mindestgehälter sowie die Lehrlingseinkommen werden rückwirkend mit 1. Mai 2026 um 3 Prozent erhöht. Die Ist-Einkommen steigen um bis zu 2,7 Prozent."),
        ],
        "ablenker": [(OEGB, 3022, "Die Mindestlöhne sowie Lehrlingseinkommen steigen um 3 Prozent.")],
        "unsicherheit": "Die Zuordnung von Zeile 1069 zur Elektroindustrie ergibt sich nur aus der Ueberschrift in Zeile 1054. 'bis zu 2,7 Prozent' bei den Ist-Einkommen ist eine Obergrenze, kein fester Satz.",
    },
    {
        "id": "kv_handel_angestellte",
        "gruppe_id": "HANDEL",
        "reihe": "Handelsangestellte Allgemeiner Gross- und Kleinhandel",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 2.55, "prozent_max": 2.55,
                     "fixbetrag_eur": None, "ist_prozent": None,
                     "geltungsbeginn": "2026-01-01", "bezugsgroesse": "kv_mindest",
                     "deckelung": False, "fundstelle_zeile": 2377},
        "fundstellen": [
            (OEGB, 2377, "Die Mindestgehälter der 430.000 Angestellten und 20.000 Lehrlinge im Handel steigen mit 1. Jänner 2026 um 2,55 Prozent, wobei die betragsmäßige Überzahlung aufrecht bleibt."),
        ],
        "ablenker": [(OEGB, 1911, "Lohnerhöhungen von 2,55 Prozent"), (OEGB, 683, "verlangt 3,8 Prozent mehr Gehalt")],
        "unsicherheit": "Die Handelsarbeiter haben denselben Satz, aber einen anderen KV (Zeile 1911) - nur die Fundstelle unterscheidet. 'Ueberzahlung bleibt betragsmaessig aufrecht' heisst: Ist-Gehaelter steigen nicht automatisch, deshalb ist_prozent = null.",
    },
    {
        "id": "kv_privatkrankenanstalten",
        "gruppe_id": "SPITAL",
        "reihe": "Privatkrankenanstalten",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 3.0, "prozent_max": 3.0,
                     "fixbetrag_eur": None, "ist_prozent": None,
                     "geltungsbeginn": "2026-04-01", "bezugsgroesse": None,
                     "deckelung": True, "fundstelle_zeile": 1851},
        "nicht_bewertet": ["bezugsgroesse"],
        "fundstellen": [
            (OEGB, 1851, "Ab 1. April 2026 werden die Gehälter bis zu einer Höhe von 3.750 Euro um drei Prozent erhöht"),
        ],
        "ablenker": [(OEGB, 5156, "Für 2025 ist eine Erhöhung um den Verbraucherpreisindex plus 0,45 Prozent vorgesehen.")],
        "unsicherheit": "Die Reihe in config/berufsgruppen.json heisst 'Bundeslaender - Krankenanstalten' (oeffentliche Landesspitaeler). Dazu steht in den Quellen nichts; die Privatkrankenanstalten sind die naechstliegende Reihe und hier bewusst als Ersatz gewaehlt (07_offene_punkte_lessons.md). 'Gehaelter' ohne Zusatz: ob KV- oder Ist-Gehalt gemeint ist, sagt der Text nicht - bezugsgroesse wird nicht bewertet. Ob 'bis zu 3.750 Euro' eine Deckelung oder eine Staffelung ist, ist Auslegung.",
    },
    {
        # Ergaenzt 23.10. nach E48, damit die Vorgabe von 8 Faellen erfuellt
        # ist. Der schaerfste Ablenker der Quelle: derselbe Satz wie der
        # Angestellten-KV Handel, aber ein anderer Kollektivvertrag.
        "id": "kv_handel_arbeiter",
        "gruppe_id": None,
        "reihe": "Handelsarbeiter (KV der Arbeiter:innen im Handel)",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 2.55, "prozent_max": 2.55,
                     "fixbetrag_eur": None, "ist_prozent": None,
                     "geltungsbeginn": None, "bezugsgroesse": None,
                     "deckelung": False, "fundstelle_zeile": 1911},
        "nicht_bewertet": ["bezugsgroesse"],
        "fundstellen": [
            (OEGB, 1896, "Handelsarbeiter:innen: Krisenabschluss hilft Branche auf die Sprünge"),
            (OEGB, 1911, "Der Abschluss bringt Lohnerhöhungen von 2,55 Prozent"),
        ],
        "ablenker": [(OEGB, 2377, "Die Mindestgehälter der 430.000 Angestellten und 20.000 Lehrlinge im Handel steigen mit 1. Jänner 2026 um 2,55 Prozent"),
                     (OEGB, 6136, "Die Löhne steigen um durchschnittlich 9,3 Prozent.")],
        "unsicherheit": "Der 19. Jaenner 2026 ist der Tag der Einigung, nicht der Geltungsbeginn - geltungsbeginn ist null; wer 2026-01-19 oder 2026-01-01 nennt, hat ein Datum erfunden oder uebernommen. 'Lohnerhoehungen' sagt nicht, ob KV- oder Ist-Loehne gemeint sind; bezugsgroesse wird nicht bewertet. Der Angestellten-KV (Zeile 2377) hat denselben Satz und einen Geltungsbeginn - nur die Fundstelle trennt die beiden.",
    },
    {
        "id": "kv_oeffentlicher_dienst",
        "gruppe_id": "BUND",
        "reihe": "Oeffentlicher Dienst (Bund, Vergleichsreihe)",
        "erwartet": {"abschluss_gefunden": True, "prozent_min": 3.3, "prozent_max": 3.3,
                     "fixbetrag_eur": None, "ist_prozent": None,
                     "geltungsbeginn": None, "bezugsgroesse": "gehaltsschema",
                     "deckelung": False, "fundstelle_zeile": 2782},
        "fundstellen": [
            (OEGB, 2767, "Dreijahresabschluss für den Öffentlichen Dienst"),
            (OEGB, 2782, "Die Höhe des Abschlusses für 2026 bleibt unverändert bei 3,3 %, es gibt keine Nulllohnrunden 2027 und 2028."),
        ],
        "ablenker": [(OEGB, 4464, "Im Jahr 2026 steigen die Gehälter, Zulange und Vergütungen um die rollierende Inflation plus 0,3 Prozent.")],
        "unsicherheit": "Der Text nennt das Jahr, nicht den Tag: geltungsbeginn ist null, ein Datum waere erfunden. Der Ablenker aus dem Abschluss 2025 kuendigte fuer 2026 'rollierende Inflation plus 0,3' an; der spaetere Dreijahresabschluss ersetzt das.",
    },
]


def block(datei: str, zeile: int) -> str:
    pfad = WURZEL / "data" / "raw" / DATUM / datei
    texte = [l.split("\t", 1)[1] for l in pfad.read_text(encoding="utf-8").splitlines()
             if not l.startswith("#") and l.split("\t", 1)[0] == str(zeile)]
    if not texte:
        raise SystemExit(f"Zeile {zeile} fehlt in {datei}")
    return "\n".join(texte)


def pruefen(datei: str, zeile: int, auszug: str) -> dict:
    if auszug not in block(datei, zeile):
        raise SystemExit(f"Wortlaut nicht gefunden: {datei}:{zeile}: {auszug[:60]}")
    return {"datei": f"data/raw/{DATUM}/{datei}", "zeile_original": zeile, "rohtext": auszug}


def erzeugen() -> dict:
    faelle = []
    for f in FAELLE:
        faelle.append({
            "fall_id": f["id"],
            "analyse": "4 - Fortschreibung der Einkommen je Berufsgruppe",
            "gruppe_id": f["gruppe_id"],
            "eingabe": {"reihe": f["reihe"], "frage": FRAGE.format(reihe=f["reihe"]),
                        "dokumente": "alle kv_*.txt des Abrufs " + DATUM + " (Tabelle kv_textblock)"},
            "erwartete_antwort": f["erwartet"],
            "fundstellen": [pruefen(*x) for x in f["fundstellen"]],
            "ablenker": [pruefen(*x) for x in f["ablenker"]],
            "pruefregel": "Feldvergleich je Feld (evals/graders/extraktion.py); Fall bestanden, wenn alle bewerteten Felder stimmen",
            "toleranz": "Prozentsaetze exakt (0,001), Datum exakt, Fundstelle exakt; null nur bei null",
            "herkunft": {"wer": "rohtext: Skript (woertlich, geprueft); erwartete_antwort: Lesung durch Claude",
                         "wann": DATUM, "wie": "evals/erfasse_kv_referenz.py aus data/raw/" + DATUM},
            "unsicherheit": f["unsicherheit"],
            "nicht_bewertet": f.get("nicht_bewertet", []),
            "von_hand_bestaetigt": f["id"] in BESTAETIGT,
            "bestaetigt_am": BESTAETIGT.get(f["id"]),
        })
    return {
        "_zweck": "Referenzantworten fuer die Extraktion aus KV-Texten (Analyse 4). Existieren vor dem Modell.",
        "_quelle": f"data/raw/{DATUM}/kv_*.txt",
        "_erzeugt_von": "evals/erfasse_kv_referenz.py",
        "_warnung": "Nicht von Hand bearbeiten. Bestaetigungen in BESTAETIGT im Skript eintragen.",
        "faelle": faelle,
    }


if __name__ == "__main__":
    daten = erzeugen()
    ZIEL.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = len(daten["faelle"])
    b = sum(f["von_hand_bestaetigt"] for f in daten["faelle"])
    print(f"{n} Faelle -> {ZIEL.relative_to(WURZEL)} ({b} von Hand bestaetigt)")
