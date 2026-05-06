# Seminar: GraphQL + REST

Dieses Verzeichnis enthält alles für die deutschsprachige Präsentation zu:

**GraphQL + REST - API-Design, Apollo, fetch vs. axios**

Der Inhalt ist für zwei Sprecher aufgeteilt und nutzt das Projekt als durchgehendes Beispiel:

- unser FastAPI-Backend als REST- und OpenAPI-Beispiel
- den VNBdigital-GraphQL-Endpunkt als GraphQL-Beispiel
- den vorhandenen Frontend-Client als fetch-Beispiel
- axios und Apollo als Vergleichs-/Erweiterungsbeispiele

## Generieren

```bash
cd seminar
npm install
npm run build
```

Ergebnis:

- `dist/graphql-rest-api-design-vnb-atlas.pptx`
- `materials/sprecher-skript.md`
- `materials/lernmaterial.md`
- `materials/demo-ablauf.md`
- `materials/code-examples.md`
- `materials/zeitplan-und-rollen.md`
- `examples/*.json`
- `assets/screenshots/*.svg`

## Präsentation starten

Für die Live-Demo im Projektwurzelverzeichnis:

```bash
./scripts/dev.sh
```

Dann öffnen:

- Frontend: `http://127.0.0.1:5173`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Sprecheraufteilung

- Sprecher A: REST, OpenAPI, API-Design, Architekturentscheidung
- Sprecher B: Frontend-Client, fetch vs. axios, GraphQL, Apollo

Die Folien sind so angelegt, dass beide ähnlich viel Redezeit haben.
