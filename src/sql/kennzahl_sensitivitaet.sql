-- Kennzahl 6: An welcher Annahme haengt die Empfehlung?
--
-- Die Frage: Wenn ein Parameter am unteren oder oberen Rand seiner Spanne
-- liegt (config/portfolio.json, Marktmiete: Q1 und Q3 der Kennzahlzeile) -
-- wie viele Vertraege bekommen dann ein anderes Angebot, und wohin wandert
-- der mittlere Aufschlag?
--
-- Fallstrick: 'geaendert' zaehlt jede Abweichung vom Basisaufschlag, auch
-- um eine Rasterstufe. Ein Parameter mit vielen Aenderungen ist der, den
-- man messen sollte, bevor man der Empfehlung folgt - nicht einer, der die
-- Empfehlung widerlegt.
SELECT s.parameter,
       s.rand,
       s.wert,
       COUNT(*)                                                       AS vertraege,
       SUM(COALESCE(s.aufschlag_pct, -1) <> COALESCE(e.aufschlag_pct, -1)) AS geaendert,
       SUM(s.option = 'auslaufen')                                    AS auslaufen,
       ROUND(AVG(s.aufschlag_pct), 1)                                 AS mittel_aufschlag_pct,
       ROUND((SELECT AVG(aufschlag_pct) FROM empfehlung), 1)          AS mittel_aufschlag_basis_pct
FROM empfehlung_sensitivitaet s
JOIN empfehlung e ON e.vertrag_id = s.vertrag_id
GROUP BY s.parameter, s.rand, s.wert
ORDER BY geaendert DESC, s.parameter, s.rand;
