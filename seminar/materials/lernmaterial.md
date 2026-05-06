# Lernmaterial: GraphQL + REST im VNB Atlas

## Kurzfassung

Unser Projekt nutzt zwei API-Welten sinnvoll kombiniert: VNBdigital wird als externe GraphQL-Datenquelle verwendet, während unser eigenes FastAPI-Backend eine stabile REST-API für das Frontend bereitstellt.

## REST im Projekt

- API-Dokumentation: `http://127.0.0.1:8000/docs`
- Maschinenlesbares Schema: `http://127.0.0.1:8000/openapi.json`
- Wichtige Endpunkte: `/api/operators`, `/api/areas`, `/api/search`, `/api/lookup`

## GraphQL im Projekt

Die Datei `vnbdigital/simple_client.py` enthält die GraphQL-Query gegen VNBdigital. Sie fragt Daten für Koordinaten ab und nutzt Variablen für Filter wie Spannungsebenen.

## fetch vs. axios

`fetch` ist im Browser eingebaut und reicht für kleine API-Clients gut aus. axios bietet mehr Komfort bei Fehlerbehandlung, Timeouts, Interceptors und zentraler Konfiguration.

## Apollo

Apollo Client ist ein spezialisierter GraphQL-Client. Er verwaltet Query-Ausführung, Cache, Loading-Status und Fehlerzustände. Apollo wäre sinnvoll, wenn unser Frontend direkt GraphQL konsumieren würde.

## Wichtigster Projektbefund

`/api/areas` sollte ein konkretes Pydantic-Response-Model erhalten, damit OpenAPI die GeoJSON-Struktur genauer dokumentiert.
