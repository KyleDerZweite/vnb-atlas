# Projekt-Referenz: VNB Atlas als Showcase

Das Projekt ist ein Beispiel, nicht die Hauptgeschichte der Präsentation.

Die allgemeine Aussage lautet:

> REST-APIs werden durch gutes Schema-Design verständlicher und wartbarer. OpenAPI macht diesen Vertrag sichtbar. Frontends brauchen dann einen sauberen Client, zum Beispiel mit `fetch` oder `axios`.

Der VNB Atlas zeigt diese Punkte konkret.

## Backend

FastAPI App:

```text
backend/app/main.py
```

Wichtige Eigenschaften:

- FastAPI erzeugt OpenAPI automatisch.
- CORS ist für das lokale Frontend konfiguriert.
- Router werden modular eingebunden.

Wichtige Endpunkte:

```text
GET /health
GET /api/coverage
GET /api/federal-states
GET /api/operators
GET /api/operators/{operator_id}
GET /api/areas
GET /api/search
GET /api/lookup
```

## OpenAPI

Bei laufendem Backend:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
http://127.0.0.1:8000/redoc
```

Guter Showcase:

- `/api/operators` zeigt Query-Parameter und typisierte Antworten.
- `/api/lookup` zeigt validierte Koordinatenparameter.
- `/api/areas` zeigt einen Verbesserungsfall, weil die Antwort aktuell nur als generisches Objekt im Schema erscheint.

## Frontend

API-Client:

```text
frontend/src/api-client.ts
```

Guter Showcase:

- `API_BASE_URL`
- zentraler `fetchJson<T>` Wrapper
- manuelle `response.ok` Prüfung
- `ApiError`
- Funktionen für konkrete API-Use-Cases

## Gute Formulierung für die Präsentation

> Wir nutzen jetzt unser Projekt nur als Beispiel. Die Prinzipien sind allgemeiner: Ein Backend sollte seine API als Schema beschreiben, OpenAPI macht REST live testbar, und das Frontend sollte API-Zugriffe zentral kapseln.

## Verbesserungsmöglichkeit im Projekt

Für `/api/areas` wäre ein konkretes Response Model sinnvoll, zum Beispiel ein `AreaFeatureCollection`-Modell. Dadurch wäre das OpenAPI-Schema aussagekräftiger und besser als API-Vertrag nutzbar.
