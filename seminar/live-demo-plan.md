# Live-Demo-Plan

Die Demo nutzt den VNB Atlas nur als Showcase für allgemeine REST- und API-Client-Konzepte.

## Vorbereitung

Im Projektwurzelverzeichnis:

```bash
./scripts/dev.sh
```

Danach verfügbar:

- Frontend: `http://127.0.0.1:5173`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Demo 1: Swagger UI als Live-API-Oberfläche

Sprecher: A

1. `http://127.0.0.1:8000/docs` öffnen.
2. Kurz zeigen: Endpunkte, Parameter, Response Models.
3. `GET /health` ausführen.
4. `GET /api/operators` ausführen mit:

```text
q = westnetz
```

5. `GET /api/areas` ausführen mit:

```text
country = DE
federal_state = NW
voltage_level = Hochspannung
```

6. `GET /api/lookup` ausführen mit:

```text
lat = 51.4818445
lon = 7.2162363
```

Erklären:

- Swagger UI macht Schema und Live-Test sichtbar.
- Query-Parameter sind Teil des API-Designs.
- Antwortdaten zeigen, ob das Schema verständlich genug ist.

## Demo 2: OpenAPI JSON als maschinenlesbarer Vertrag

Sprecher: A

1. `http://127.0.0.1:8000/openapi.json` öffnen.
2. `paths` suchen.
3. Einen Endpunkt wie `/api/operators` zeigen.
4. Danach `/api/areas` zeigen.

Wichtiger Hinweis:

`/api/areas` ist aktuell im Schema weniger präzise, weil der Endpunkt im Code `dict[str, Any]` zurückgibt. Das ist ein gutes Beispiel dafür, dass OpenAPI-Qualität von guten Response Models abhängt.

## Demo 3: Frontend-Client mit fetch

Sprecher: B

Datei öffnen:

```text
frontend/src/api-client.ts
```

Zeigen:

- `API_BASE_URL`
- `fetchJson<T>`
- `response.ok`
- `ApiError`
- `getOperators`
- `getAreas`
- `lookup`

Erklären:

- Der Wrapper verhindert Wiederholung.
- Komponenten müssen HTTP-Details nicht selbst kennen.
- Typen helfen beim Entwickeln, validieren aber nicht automatisch Runtime-Daten.

## Demo 4: hypothetische axios-Version

Sprecher: B

Code aus `code-examples.md` zeigen.

Vergleichspunkte:

- `axios.create`
- `baseURL`
- `params`
- `response.data`
- `timeout`
- Interceptors als Erweiterungspunkt

## Fallback ohne laufenden Server

Falls der Server nicht läuft:

- Code in `backend/app/main.py` zeigen.
- Router in `backend/app/routers/` zeigen.
- `frontend/src/api-client.ts` zeigen.
- Beispiel-cURL-Aufrufe aus dieser Datei verwenden.
