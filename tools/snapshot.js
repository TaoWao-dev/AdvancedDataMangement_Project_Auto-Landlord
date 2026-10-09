// Selbstpruefender Schnappschuss-Helfer fuer willhaben-Bezirkssuchen.
//
// In die DevTools-Konsole einfuegen und Enter. Der Schnipsel laedt die Datei
// nur herunter, wenn die Daten tatsaechlich zur aufgerufenen URL passen.
//
// WARUM DIE PRUEFUNG NOETIG IST
// __NEXT_DATA__ ist ein statischer Script-Tag aus dem Server-Rendering. Bei
// einer client-seitigen Navigation innerhalb der Next.js-App bleibt er auf
// dem Stand der ZUERST vom Server gelieferten Seite. Wer willhaben oeffnet
// und sich dann zur Bezirkssuche durchklickt, liest die alte Seite aus -
// gleiche Datei, gleicher Zeitstempel, falscher Inhalt. Genau das ist in
// diesem Projekt dreimal passiert (siehe docs/projektdokumentation/02_schritt1_datenzugriff.md).
//
// Abhilfe: die Bezirks-URL in die Adresszeile einfuegen und Enter druecken
// (volle Navigation), oder hart neu laden (Strg+Shift+R / Cmd+Shift+R).
// Danach passt __NEXT_DATA__ zur URL.

(() => {
  const el = document.getElementById('__NEXT_DATA__');
  if (!el) {
    console.error('[wh] __NEXT_DATA__ nicht gefunden. Statt dessen view-source: verwenden.');
    return;
  }

  let daten, sr;
  try {
    daten = JSON.parse(el.textContent);
    sr = daten.props.pageProps.searchResult;
  } catch (e) {
    console.error('[wh] JSON nicht lesbar:', e.message);
    return;
  }

  // Ohne searchResult ist es keine Suchergebnisseite (Startseite, Detailseite,
  // Cookie-Abfrage) - oder willhaben hat das Feld umbenannt. Beides soll mit
  // Namen gemeldet werden, nicht als TypeError ein paar Zeilen weiter unten.
  if (!sr) {
    const keys = Object.keys((daten.props && daten.props.pageProps) || {});
    console.error('%c[wh] ABGEBROCHEN - keine Suchergebnisseite',
      'font-weight:bold;color:#A83E27');
    console.error('   . URL: ' + location.href);
    console.error('   . Next.js-Seite: ' + daten.page);
    console.error('   . pageProps enthaelt: ' + (keys.join(', ') || '(nichts)'));
    console.info('%cDie Bezirkssuche direkt aufrufen (URL eintippen, Enter), z. B.\n'
      + 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien/wien-1020-leopoldstadt?rows=90\n'
      + 'Steht dort trotzdem kein searchResult, hat sich die Seitenstruktur geaendert.',
      'color:#2A6058');
    return;
  }

  // PLZ aus der aufgerufenen URL, z. B. .../wien/wien-1020-leopoldstadt
  const urlPlz = (location.pathname.match(/wien-(\d{4})-/) || [])[1]
              || (location.pathname.match(/(?:^|\/)(\d{4})(?:$|\/)/) || [])[1];

  const ads = (sr.advertSummaryList && sr.advertSummaryList.advertSummary) || [];
  const plzListe = ads.map((a) => {
    const at = (a.attributes && a.attributes.attribute) || [];
    const f = at.find((x) => x.name === 'POSTCODE');
    return f && f.values && f.values[0];
  }).filter(Boolean);

  const zaehler = {};
  plzListe.forEach((p) => { zaehler[p] = (zaehler[p] || 0) + 1; });
  const haeufigste = Object.keys(zaehler).sort((a, b) => zaehler[b] - zaehler[a])[0];
  const anteil = plzListe.length ? zaehler[haeufigste] / plzListe.length : 0;

  const probleme = [];
  if (sr.verticalId !== 2) {
    probleme.push('verticalId ' + sr.verticalId + ' statt 2 (Immobilien)');
  }
  if (sr.rowsFound > 100000) {
    probleme.push('rowsFound ' + sr.rowsFound.toLocaleString('de-AT')
      + ' - eine Gesamtliste, keine Bezirkssuche');
  }
  if (anteil < 0.9) {
    probleme.push('nur ' + Math.round(anteil * 100) + ' % der Inserate in '
      + haeufigste + ' - keine einheitliche PLZ');
  }
  if (urlPlz && haeufigste && urlPlz !== haeufigste) {
    probleme.push('URL sagt ' + urlPlz + ', Daten sagen ' + haeufigste);
  }
  if (!ads.length) {
    probleme.push('keine Inserate enthalten');
  }

  if (probleme.length) {
    console.error('%c[wh] ABGEBROCHEN - die Daten passen nicht zur URL',
      'font-weight:bold;color:#A83E27');
    probleme.forEach((p) => console.error('   . ' + p));
    console.info('%cVermutlich haelt __NEXT_DATA__ noch die zuerst geladene Seite.\n'
      + 'Die Bezirks-URL in die Adresszeile einfuegen, Enter druecken, dann erneut ausfuehren.\n'
      + 'Alternativ: view-source:' + location.href, 'color:#2A6058');
    return;
  }

  // Dateiname aus den Daten selbst, nicht aus dem Gedaechtnis
  // JJJJ-MM-TTTHHMM: 15 Zeichen, sonst fehlen die Minuten und Seite 1 und 2
  // derselben Stunde bekommen denselben Namen.
  const ts = (sr.searchDate || new Date().toISOString())
    .replace(/[+Z].*$/, '').replace(/:/g, '').slice(0, 15);
  const seite = new URLSearchParams(location.search).get('page');
  const name = 'wh_' + haeufigste + '_mietwohnungen_' + ts
    + (seite && seite !== '1' ? '_s' + seite : '') + '.json';

  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([el.textContent], { type: 'application/json' }));
  a.download = name;
  a.click();

  console.info('%c[wh] ' + name, 'font-weight:bold;color:#2A6058');
  console.info('   PLZ ' + haeufigste + ' . ' + ads.length + ' von '
    + sr.rowsFound + ' Treffern . ' + sr.searchDate);
  if (sr.rowsFound > sr.rowsReturned) {
    console.warn('   Teilseite: ' + sr.rowsReturned + ' von ' + sr.rowsFound
      + '. Fuer den ganzen Bezirk ?rows=90 und weitere Seiten (?page=2 ...) speichern.');
  }
})();
