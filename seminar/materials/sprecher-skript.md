# Sprecher-Skript

## Folie 1: GraphQL + REST

**Sprecher:** A+B

Beide Sprecher eröffnen kurz: Ziel ist kein abstrakter Vergleich, sondern ein konkreter Blick auf unser Projekt und seine API-Entscheidungen.

Kernaussagen:
- Seminar mit Live-Demo
- Projektbezug: FastAPI-Backend, VNBdigital GraphQL, TypeScript-Frontend

## Folie 2: Lernziele

**Sprecher:** A

Sprecher A setzt den Rahmen. Wichtig: Wir beantworten nicht nur 'was ist besser', sondern 'wo passt was'.

Kernaussagen:
- REST-Endpunkte als bewusstes API-Design lesen und testen
- OpenAPI als automatisch erzeugten Vertrag verstehen
- fetch und axios praktisch vergleichen
- GraphQL und Apollo anhand von VNBdigital einordnen
- Architekturentscheidung erklären: GraphQL upstream, REST downstream

## Folie 3: Projektkontext

**Sprecher:** B

Sprecher B erklärt das Projekt fachlich: Karte, Betreiber, Spannungsebenen und warum ein eigenes Backend sinnvoll ist.

Kernaussagen:
- Frontend zeigt Verteilnetzbetreiber auf einer Leaflet-Karte
- Backend liefert Operatoren, Gebiete, Suche, Lookup und Coverage
- Datenquelle: VNBdigital-Koordinatenabfragen über GraphQL
- Backend transformiert externe Daten in eigene REST-Ressourcen

## Folie 4: Architekturüberblick

**Sprecher:** A

Sprecher A nutzt die Grafik: GraphQL ist die Quellseite, REST ist unser Produktvertrag für die UI.

Kernaussagen:
- Siehe Vergleich/Tabelle auf der Folie.

## Folie 5: REST in unserem Backend

**Sprecher:** A

Sprecher A zeigt, dass REST nicht nur HTTP ist, sondern ein Vertrag aus Ressourcen, Parametern und Antwortformen.

Kernaussagen:
- Ressourcenorientierte Endpunkte: /api/operators, /api/areas, /api/search, /api/lookup
- GET-only API mit Query-Parametern für Filter
- Pydantic-Modelle beschreiben viele Antworttypen
- FastAPI erzeugt daraus Dokumentation und OpenAPI-Schema

## Folie 6: OpenAPI sichtbar

**Sprecher:** A

Sprecher A führt live /docs vor. Danach kann /openapi.json geöffnet werden, um zu zeigen, dass die Doku maschinenlesbar ist.

Kernaussagen:
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json
- ReDoc: http://127.0.0.1:8000/redoc
- Nützlich für Tests, Doku, Client-Generierung und Reviews

## Folie 7: Schema-Qualität: wichtiger Befund

**Sprecher:** A

Sprecher A erklärt ehrlich die Schwäche. Das ist gut für API-Design: Schema-Qualität ist Teil der Wartbarkeit.

Kernaussagen:
- Die meisten Endpunkte haben Pydantic response_model
- /api/areas liefert aktuell dict[str, Any]
- Dadurch erscheint die Antwort in OpenAPI nur als generisches Objekt
- Verbesserung: AreaFeatureCollection als Pydantic-Modell ergänzen

## Folie 8: Live-Demo REST

**Sprecher:** A

Sprecher A macht die erste Live-Interaktion. Falls das Netzwerk egal ist: diese REST-Demo läuft lokal aus statischen Daten.

Kernaussagen:
- Backend starten: ./scripts/dev.sh
- Swagger UI öffnen und Endpunkte ausführen
- Operator-Suche: westnetz
- Gebiete filtern: DE, NW, Hochspannung
- Lookup per Koordinate: Bochum-Beispiel

## Folie 9: Frontend-Client heute: fetch

**Sprecher:** B

Sprecher B übernimmt mit dem Frontend. fetch ist nicht schlecht, aber etwas niedriger level.

Kernaussagen:
- Native Browser-API, keine zusätzliche Dependency
- Projekt nutzt zentralen fetchJson-Wrapper
- response.ok und Fehlertexte werden manuell behandelt
- Rückgabewert wird in TypeScript gecastet

## Folie 10: Alternative: axios

**Sprecher:** B

Sprecher B zeigt nicht 'axios ist immer besser', sondern wann es komfortabler wird.

Kernaussagen:
- Eigene Instanz mit baseURL und Standard-Headern
- JSON wird automatisch verarbeitet
- response.data ist der zentrale Rückgabewert
- Interceptors eignen sich für Auth, Logging, Retry und Fehlernormierung

## Folie 11: fetch vs. axios

**Sprecher:** B

Sprecher B führt die Tabelle durch. Für unser Projekt reicht fetch; bei wachsender API kann axios den Client ordnen.

Kernaussagen:
- Siehe Vergleich/Tabelle auf der Folie.

## Folie 12: GraphQL-Grundidee

**Sprecher:** B

Sprecher B wechselt zum zweiten API-Paradigma. Fokus auf Datenform und Client-Bedürfnisse.

Kernaussagen:
- Ein Endpoint, Query beschreibt die benötigten Felder
- Client kann verschachtelte Daten gezielt anfordern
- Schema definiert Typen, Queries, Mutations und Inputs
- Stark bei flexiblen Datenbedürfnissen und UI-Komposition

## Folie 13: VNBdigital GraphQL

**Sprecher:** B

Sprecher B zeigt die echte Projektquery aus vnbdigital/simple_client.py, aber gekürzt für die Folie.

Kernaussagen:
- Projekt nutzt den öffentlichen GraphQL-Endpunkt von VNBdigital
- Query fragt Koordinate, Regionen und VNBs ab
- Variablen steuern Koordinate, Spannungsebenen und Filter
- Ergebnisse werden offline zu Mesh- und Polygon-Daten verarbeitet

## Folie 14: Apollo im GraphQL-Client

**Sprecher:** B

Sprecher B erklärt Apollo als spezialisierten Client, nicht als Server-Technologie.

Kernaussagen:
- Apollo Client verwaltet Queries, Variablen, Cache, Loading und Errors
- useQuery verbindet UI-Zustand direkt mit GraphQL-Daten
- Normalized Cache reduziert doppelte Requests
- Passt besonders gut, wenn das Frontend direkt GraphQL spricht

## Folie 15: REST und GraphQL im Vergleich

**Sprecher:** A

Sprecher A kommt zurück und ordnet ein. Wichtig: Es geht um Tradeoffs, nicht Gewinner.

Kernaussagen:
- Siehe Vergleich/Tabelle auf der Folie.

## Folie 16: Warum unser Projekt beides nutzt

**Sprecher:** A

Sprecher A liefert die Architekturbegründung: GraphQL ist Quelle, REST ist Produkt-API.

Kernaussagen:
- VNBdigital bietet flexible GraphQL-Abfragen für Koordinaten
- Unser Backend kapselt diese externe API und Datenaufbereitung
- Frontend braucht stabile, einfache, domänenspezifische Endpunkte
- REST + OpenAPI macht die lokale Demo und den Vertrag gut sichtbar

## Folie 17: API-Design-Lektionen aus dem Projekt

**Sprecher:** A

Sprecher A zieht konkrete Regeln aus dem Projekt, statt allgemeine Best Practices abstrakt zu halten.

Kernaussagen:
- Endpunkte nach UI-Use-Cases und Domänenbegriffen schneiden
- Filter explizit als Query-Parameter modellieren
- Antwortmodelle konsequent typisieren
- OpenAPI regelmäßig prüfen, nicht nur Code schreiben
- Externe APIs hinter eigener Stabilitätsschicht kapseln

## Folie 18: Live-Demo GraphQL/Apollo-Konzept

**Sprecher:** B

Sprecher B kann den echten Endpoint nennen, aber die Demo sollte nicht von externer Erreichbarkeit abhängen. Der vorbereitete Code reicht.

Kernaussagen:
- Projektquery aus vnbdigital/simple_client.py zeigen
- Variablen erklären: coordinates, filter, voltageTypes
- Apollo-Beispielcode zeigen
- Abgrenzung: In unserem Projekt läuft GraphQL derzeit nicht direkt im Browser

## Folie 19: Wann was einsetzen?

**Sprecher:** B

Sprecher B fasst die Entscheidungsmatrix zusammen.

Kernaussagen:
- REST: stabile Ressourcen, einfache HTTP-Semantik, gute Tooling-Unterstützung
- GraphQL: flexible verschachtelte Daten, viele UI-Sichten, gezielte Feldauswahl
- fetch: kleine bis mittlere Clients ohne Zusatzpaket
- axios: größere Clients mit Interceptors, Timeouts und einheitlichen Fehlern
- Apollo: GraphQL-Frontend mit Cache und Query-State

## Folie 20: Abschluss

**Sprecher:** A+B

Beide Sprecher schließen gemeinsam. Danach Q&A und bei Zeit kurze Wiederholung der Live-Demo.

Kernaussagen:
- Unser Projekt ist ein gutes Beispiel für API-Grenzen
- OpenAPI macht REST live testbar und dokumentiert
- VNBdigital zeigt GraphQL als flexible Datenquelle
- fetch, axios und Apollo sind Client-Werkzeuge für unterschiedliche Situationen
