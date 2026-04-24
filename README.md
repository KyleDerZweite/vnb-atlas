# Deutschland VNB Atlas

Lokales MVP fuer eine deutschlandweit ausgelegte Web-App zur Visualisierung von Verteilnetzbetreibern auf einer OpenStreetMap-basierten Karte. Der MVP enthaelt aktuell nur GIS-/Mock-Gebietsdaten fuer Nordrhein-Westfalen.

> Wichtig: MVP-Datenabdeckung: NRW. Alle gelieferten Flaechen und Betreiberbeziehungen sind Mock-Daten / nicht amtlich. Es gibt keine erfundenen VNB-Grenzen fuer andere Bundeslaender.

## Umfang

- Landing Page mit deutschlandweiter Zielbeschreibung und NRW-Pilotdaten-Hinweis.
- Karten- und Suchseite mit OSM-Basemap, Startansicht Deutschland.
- NRW-Mock-VNB-Gebiete als GeoJSON-Polygone.
- Bundeslandfilter mit NRW als einzigem befuelltem Pilotdatensatz.
- Suche nach Ort, PLZ oder Betreibername, deutschlandfaehig ausgelegt.
- Filter nach Betreiber und Datenqualitaet.
- Detailbereich bei Auswahl eines Gebiets.
- Zugaengliche Ergebnisliste als Alternative zur visuellen Karte.
- FastAPI-Endpunkte fuer Coverage, Bundeslaender, Betreiber, Gebiete, Suche und Koordinaten-Lookup.

Nicht enthalten: User-Accounts, Admin-Panel, Datenbank, echte VNB-Integration, befuellte Daten ausserhalb NRW, Scraping oder API-Keys.

## Voraussetzungen

- Python 3.12+
- Node.js 22+
- npm
- GNU Make fuer Makefile-Kommandos

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

Das Script erstellt `backend/.venv`, installiert Python- und npm-Abhaengigkeiten, startet FastAPI mit `uvicorn --reload`, startet Vite mit Hot Reload und beendet beide Prozesse gemeinsam bei `Ctrl+C`.

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
      coverage.py
      federal_states.py
    services/
      coverage_service.py
      data_service.py
      geo_service.py
    data/
      operators.json
      areas.geojson
      federal-states.json
    tests/
frontend/
  index.html
  map.html
  src/
  styles/main.css
scripts/
  dev.sh
  dev.ps1
  dev.bat
  import_gis_placeholder.py
```

Die Architektur ist nicht auf NRW festgelegt. `federal-states.json` beschreibt bundesweite Datenabdeckung; `areas.geojson` enthaelt im MVP nur NRW-Features. Weitere Bundeslaender koennen spaeter durch neue Features mit `country` und `federalState` ergaenzt werden, ohne das Frontend neu aufzubauen.

## API

### `GET /health`

```bash
curl http://127.0.0.1:8000/health
```

Antwort:

```json
{"status":"ok","service":"vnb-atlas"}
```

### `GET /api/coverage`

Gibt die Datenabdeckung je Land und Bundesland zurueck.

```bash
curl http://127.0.0.1:8000/api/coverage
```

Im MVP hat `NW` `hasAreas=true` und `status=mock`; alle anderen Bundeslaender haben `hasAreas=false` und `status=not_available`.

### `GET /api/federal-states`

```bash
curl http://127.0.0.1:8000/api/federal-states
```

Liefert alle deutschen Bundeslaender mit `id`, `name`, `hasAreaData` und `dataStatus`.

### `GET /api/operators`

Optionale Query-Parameter: `q`, `type`, `accuracy`, `country`, `federal_state`, `coverage`.

```bash
curl "http://127.0.0.1:8000/api/operators?country=DE&federal_state=NW&coverage=mock"
```

Fuer Bundeslaender ohne Daten wird eine leere Liste geliefert.

### `GET /api/operators/{operator_id}`

```bash
curl http://127.0.0.1:8000/api/operators/westnetz-mock
```

### `GET /api/areas`

Optionale Query-Parameter:

- `bbox=minLon,minLat,maxLon,maxLat`
- `operator_id`
- `accuracy`
- `country=DE`
- `federal_state=NW`

```bash
curl "http://127.0.0.1:8000/api/areas?country=DE&federal_state=NW"
curl "http://127.0.0.1:8000/api/areas?country=DE&federal_state=BY"
```

Antwort ist immer eine gueltige GeoJSON `FeatureCollection`. Fuer nicht befuellte Bundeslaender ist `features` leer.

### `GET /api/search?q=...`

Sucht in Betreibername, Gebietname, Mock-Orten und Mock-PLZ. Die Suche ist fuer deutschlandweite Daten vorbereitet, findet im MVP aber nur NRW-Mockdaten.

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
- `country`: aktuell `DE`
- `federalStates`: z. B. `["NW"]`
- `dataCoverage`: `none`, `mock`, `partial`, `verified`
- `mockNotice`

Gebiete liegen in `backend/app/data/areas.geojson` als WGS84/EPSG:4326 GeoJSON.

Wichtige Properties:

- `id`
- `name`
- `operatorId`
- `country`: aktuell `DE`
- `federalState`: z. B. `NW`
- `accuracy`: `mock`, `municipality_approximation`, `verified`
- `source`
- `updatedAt`
- `mockNotice`
- `places`
- `postalCodes`

Bundeslaender liegen in `backend/app/data/federal-states.json`.

## Spaetere GIS-Integration

Echte GIS-Daten koennen spaeter durch Austausch von `backend/app/data/areas.geojson`, `backend/app/data/operators.json` und `backend/app/data/federal-states.json` oder durch einen Importprozess angeschlossen werden. Der API-Contract ist auf deutschlandweite GeoJSON FeatureCollections ausgelegt.

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

- Die Anwendung heisst Deutschland VNB Atlas und ist deutschlandweit ausgelegt.
- Im MVP ist NRW der einzige befuellte Pilotdatensatz.
- Leaflet ist die einzige Kartenbibliothek.
- Die Geometrie-Operationen sind fuer kleine Mock-Polygone bewusst simpel selbst implementiert.
- Frontend laeuft lokal auf Port `5173`, Backend auf Port `8000`.
- Keine externen API-Keys, keine Secrets, kein Scraping.
- Keine gefaelschten Deutschland-Grenzen oder VNB-Zustaendigkeiten ausserhalb NRW.
