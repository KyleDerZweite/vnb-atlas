# Talk-Plan

## Thema

**API Schema Design + REST: Live-Interaktion mit OpenAPI, fetch vs. axios**

Das Projekt **Deutschland VNB Atlas** dient als Showcase-Referenz. Die Präsentation soll zuerst die allgemeinen Konzepte erklären und danach zeigen: "So sieht das in einem echten Projekt aus."

## Ziel

Die Zuhörer sollen am Ende verstehen:

- was ein API-Schema ist und warum es wichtig ist
- wie REST-APIs strukturiert werden
- wie OpenAPI/Swagger eine REST-API dokumentierbar und testbar macht
- wie eine Live-Interaktion mit einer API abläuft
- wie `fetch` und `axios` REST-APIs konsumieren
- wann `fetch` reicht und wann `axios` Vorteile bringt

## Zielzeit

Empfohlen: **25 bis 30 Minuten** plus Fragen.

## Sprecheraufteilung

### Sprecher A: API-Design, REST, OpenAPI

Redezeit: ca. 13 bis 15 Minuten.

Themen:

- Motivation: Warum API-Schema-Design?
- REST-Grundlagen
- Ressourcen, Endpunkte, Statuscodes, Query-Parameter
- OpenAPI/Swagger als Vertrag und Live-Testoberfläche
- Live-Demo im VNB Atlas Backend
- Einordnung: Was ist im Projekt gut sichtbar, was könnte verbessert werden?

### Sprecher B: Client-Zugriff, fetch vs. axios

Redezeit: ca. 12 bis 15 Minuten.

Themen:

- Wie Frontends REST-APIs konsumieren
- `fetch` als Browser-Standard
- Fehlerbehandlung mit `fetch`
- `axios` als komfortablere Client-Bibliothek
- Vergleich `fetch` vs. `axios`
- Projektbezug: aktueller VNB Atlas Frontend-Client nutzt `fetch`

## Grober Ablauf

1. Einstieg und Zielbild
2. API-Schema-Design allgemein
3. REST als API-Stil
4. OpenAPI und Swagger UI
5. Live-Demo REST API
6. Client-Perspektive: API-Aufruf im Frontend
7. fetch im Detail
8. axios im Detail
9. fetch vs. axios Vergleich
10. Projekt-Showcase und Fazit

## Übergänge

Übergang A zu B:

> "Wir haben jetzt gesehen, wie eine REST-API entworfen, beschrieben und live getestet werden kann. Als nächstes schauen wir auf die andere Seite: Wie konsumiert ein Frontend diese API?"

Übergang B zu A oder gemeinsames Fazit:

> "Damit haben wir beide Seiten gesehen: die API als Vertrag und den Client als Nutzer dieses Vertrags. Am Projekt sieht man gut, warum saubere Schemas und ein zentraler API-Client zusammengehören."
