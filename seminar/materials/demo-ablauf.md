# Demo-Ablauf

## Vorbereitung

```bash
./scripts/dev.sh
```

## REST-Demo

1. Öffne `http://127.0.0.1:8000/docs`.
2. Führe `GET /api/operators` mit `q=westnetz` aus.
3. Führe `GET /api/areas` mit `country=DE`, `federal_state=NW`, `voltage_level=Hochspannung` aus.
4. Führe `GET /api/lookup` mit `lat=51.4818445`, `lon=7.2162363` aus.
5. Öffne `http://127.0.0.1:8000/openapi.json`.

## Frontend-Demo

1. Öffne `http://127.0.0.1:5173`.
2. Zeige Suche, Karte und Filter.
3. Öffne `frontend/src/api-client.ts` und erkläre den fetch-Wrapper.

## GraphQL/Apollo-Demo

1. Öffne `vnbdigital/simple_client.py`.
2. Zeige die Query `COORDINATES_QUERY`.
3. Erkläre Variablen: `coordinates`, `filter`, `voltageTypes`.
4. Zeige `materials/code-examples.md` für Apollo.
