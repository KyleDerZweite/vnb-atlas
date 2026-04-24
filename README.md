# NRW VNB Atlas

Lokales MVP fuer eine Web-App, die Verteilnetzbetreiber in Nordrhein-Westfalen auf einer OpenStreetMap-basierten Karte visualisiert. Das Projekt nutzt FastAPI, HTML/CSS/TypeScript und Leaflet.

> Wichtig: Alle gelieferten Flaechen und Betreiberbeziehungen sind Mock-Daten / nicht amtlich. Die Grenzen zeigen keine echten VNB-Zustaendigkeiten.

## Umfang

- Landing Page mit Hinweis auf Mock-Daten.
- Karten- und Suchseite mit OSM-Basemap.
- Mock-VNB-Gebiete als GeoJSON-Polygone.
- Suche nach Ort, PLZ oder Betreibername.
- Filter nach Betreiber und Datenqualitaet.
- Detailbereich bei Auswahl eines Gebiets.
- Zugaengliche Ergebnisliste als Alternative zur visuellen Karte.
- FastAPI-Endpunkte fuer Betreiber, Gebiete, Suche und Koordinaten-Lookup.

Nicht enthalten: User-Accounts, Admin-Panel, Datenbank, echte VNB-Integration, bundesweite Karte, Scraping oder API-Keys.

## Voraussetzungen

- Python 3.12+
- Node.js 22+
- npm
- GNU Make

## Schnellstart nach dem Klonen

Ein einzelner Befehl richtet Backend und Frontend ein und startet beide im Dev-Modus mit Reload:

```bash
./scripts/dev.sh
```

Unter Windows:

```powershell
.\scripts\dev.ps1
```

Falls PowerShell-Scripte durch die lokale Execution Policy blockiert werden:

```cmd
scripts\dev.bat
```

Das Script:

- erstellt `backend/.venv`, falls noch nicht vorhanden,
- installiert Python-Abhängigkeiten inklusive Test-Dependencies,
- installiert npm-Abhängigkeiten,
- startet FastAPI mit `uvicorn --reload`,
- startet Vite mit Hot Reload,
- beendet Backend und Frontend gemeinsam bei `Ctrl+C`.

Alternativ:

```bash
make dev
```

Danach:

- Frontend: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000`
- OpenAPI: `http://127.0.0.1:8000/docs`

## Manuelle Installation

```bash
make install
```

## Manuell lokal starten

Backend:

```bash
make dev-backend
```

Frontend:

```bash
make dev-frontend
```

Danach:

- Frontend: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000`
- OpenAPI: `http://127.0.0.1:8000/docs`

## Tests

```bash
make test
```

Einzeln:

```bash
make test-backend
make typecheck
```

## Architektur

```text
backend/
  app/
    main.py
    routers/
    services/
    data/operators.json
    data/areas.geojson
    tests/
frontend/
  index.html
  map.html
  src/
  styles/main.css
scripts/
  import_gis_placeholder.py
```

Das Backend laedt JSON/GeoJSON-Dateien aus `backend/app/data/`. Die Services kapseln Datenzugriff, Suche, BBox-Filter und Punkt-in-Polygon-Lookup. Das Frontend nutzt nur die REST-Endpunkte und haelt keine Betreiberliste fest im Code, abgesehen von UI-Fallbacks fuer leere Auswahlwerte.

## API

### `GET /health`

```bash
curl http://127.0.0.1:8000/health
```

Antwort:

```json
{"status":"ok","service":"nrw-vnb-atlas"}
```

### `GET /api/operators`

Optionale Query-Parameter: `q`, `type`, `accuracy`.

```bash
curl "http://127.0.0.1:8000/api/operators?q=westnetz"
```

### `GET /api/operators/{operator_id}`

```bash
curl http://127.0.0.1:8000/api/operators/westnetz-mock
```

### `GET /api/areas`

Optionale Query-Parameter:

- `bbox=minLon,minLat,maxLon,maxLat`
- `operator_id`
- `accuracy`

```bash
curl "http://127.0.0.1:8000/api/areas?bbox=6.5,51.0,7.0,51.45"
```

Antwort ist eine GeoJSON `FeatureCollection`. Jedes Feature enthaelt `properties.mockNotice`.

### `GET /api/search?q=...`

Sucht in Betreibername, Gebietname, Mock-Orten und Mock-PLZ.

```bash
curl "http://127.0.0.1:8000/api/search?q=40213"
```

### `GET /api/lookup?lat=...&lon=...`

Gibt das Mock-Gebiet fuer Koordinaten zurueck oder `{"match":null}`.

```bash
curl "http://127.0.0.1:8000/api/lookup?lat=51.23&lon=6.78"
```

## Datenmodell

Operatoren liegen in `backend/app/data/operators.json`.

Wichtige Felder:

- `id`
- `name`
- `type`: `VNB`, `ÜNB` oder `UNKNOWN`
- `website`
- `parentCompany`
- `description`
- `voltageLevels`
- `mockNotice`

Gebiete liegen in `backend/app/data/areas.geojson` als WGS84/EPSG:4326 GeoJSON.

Wichtige Properties:

- `id`
- `name`
- `operatorId`
- `accuracy`: `mock`, `municipality_approximation`, `verified`
- `source`
- `updatedAt`
- `mockNotice`
- `places`
- `postalCodes`

## Spaetere GIS-Integration

Echte GIS-Daten koennen spaeter durch Austausch von `backend/app/data/areas.geojson` und `backend/app/data/operators.json` oder durch einen Importprozess angeschlossen werden. Der API-Contract ist auf GeoJSON FeatureCollections ausgelegt.

Der Platzhalter:

```bash
python scripts/import_gis_placeholder.py
```

dokumentiert den erwarteten Importweg: Shapefile oder GeoJSON lesen, nach EPSG:4326 transformieren, Betreiber auf `operatorId` mappen, GeoJSON validieren und in das interne Format schreiben.

## Accessibility

- Semantische Struktur mit `header`, `nav`, `main`, `section`, `aside`, `footer`.
- Pro Seite genau eine `h1`.
- Skip-Link.
- Labels fuer Formularfelder.
- Suche nur per Enter oder Button, keine Autocomplete-Requests.
- Sichtbare Fokuszustaende.
- Kartenbereich mit Beschreibung.
- Ergebnisliste als voll nutzbare Alternative zur visuellen Karte.
- Statusmeldungen in `role="status"` / `aria-live`.
- Detailpanel ist programmatisch fokussierbar.
- Informationen werden nicht nur ueber Farbe vermittelt.

## Annahmen

- Das Repository war leer und durfte neu strukturiert werden.
- Leaflet ist die einzige Kartenbibliothek.
- Die Geometrie-Operationen sind fuer kleine Mock-Polygone bewusst simpel selbst implementiert.
- Frontend laeuft lokal auf Port `5173`, Backend auf Port `8000`.
- Keine externen API-Keys, keine Secrets, kein Scraping.
