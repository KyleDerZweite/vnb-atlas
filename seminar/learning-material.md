# Lernmaterial

## API Schema Design

Ein API-Schema beschreibt eine Schnittstelle strukturiert und maschinenlesbar. Es beantwortet Fragen wie:

- Welche Endpunkte gibt es?
- Welche Parameter akzeptieren sie?
- Welche Daten werden zurückgegeben?
- Welche Statuscodes und Fehler sind möglich?
- Welche Felder sind Pflichtfelder?
- Welche Datentypen werden erwartet?

Ein gutes Schema hilft mehreren Gruppen:

- Backend-Entwickler prüfen, ob die API konsistent ist.
- Frontend-Entwickler sehen, welche Daten verfügbar sind.
- Tester können API-Fälle systematisch ableiten.
- Tools können Dokumentation oder Clients generieren.

## REST

REST ist ein API-Stil, bei dem Ressourcen über URLs erreichbar sind und HTTP-Methoden die Aktion ausdrücken.

Typische Beispiele:

```text
GET /api/operators
GET /api/operators/{operator_id}
GET /api/areas?country=DE
```

Wichtige Designfragen:

- Welche Ressourcen gibt es?
- Welche Filter braucht der Client?
- Wie sehen Fehlerantworten aus?
- Werden große Listen paginiert?
- Sind Antwortmodelle stabil?

## OpenAPI

OpenAPI ist ein Standardformat zur Beschreibung von REST-APIs. FastAPI kann OpenAPI automatisch aus Routen, Parametern und Pydantic-Modellen erzeugen.

Typische URLs in FastAPI:

```text
/docs
/redoc
/openapi.json
```

OpenAPI ist nützlich für:

- interaktive Dokumentation
- API-Reviews
- automatisierte Tests
- Client-Generierung
- Kommunikation zwischen Backend und Frontend

## fetch

`fetch` ist die native Browser-API für HTTP-Requests.

Vorteile:

- keine Dependency
- Browser-Standard
- gut für einfache API-Clients

Nachteile:

- 4xx/5xx werfen nicht automatisch Fehler
- JSON muss explizit gelesen werden
- Timeout braucht `AbortController`
- zentrale Features wie Interceptors müssen selbst gebaut werden

## axios

axios ist eine HTTP-Client-Bibliothek.

Vorteile:

- zentrale Instanzen mit `baseURL`
- automatische JSON-Verarbeitung
- `response.data`
- `timeout` Option
- Interceptors für Auth, Logging, Retry und Fehlerbehandlung

Nachteile:

- zusätzliche Dependency
- nicht immer nötig
- eigenes Verhalten muss verstanden werden

## Entscheidungshilfe

`fetch` passt gut, wenn:

- die API überschaubar ist
- keine zentrale Auth-/Retry-Logik nötig ist
- ein kleiner Wrapper ausreicht

axios passt gut, wenn:

- viele Endpunkte konsumiert werden
- einheitliche Fehlerbehandlung wichtig ist
- Timeouts, Interceptors oder zentrale Konfiguration gebraucht werden
- mehrere Teams am Client arbeiten

## Projektbezug

Im VNB Atlas sieht man:

- FastAPI erzeugt OpenAPI automatisch.
- Swagger UI macht die API live testbar.
- Das Frontend nutzt einen zentralen `fetch`-Wrapper.
- Die REST-API ist ein gutes Beispiel für API-Schema-Design.
- `/api/areas` zeigt, warum präzise Response Models wichtig sind.
