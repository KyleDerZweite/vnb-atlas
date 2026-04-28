# VNB Atlas

Web-App und FastAPI-Backend zur Visualisierung von Verteilnetzbetreibern auf einer OpenStreetMap-basierten Karte.

Die aktuelle Datenbasis ist ein deutschlandweites VNBdigital-Koordinatenmesh mit 5-km-Aufloesung. Aus den Rasterpunkten werden approximierte Mittellinien-Polygone pro Betreiber und Spannungsebene erzeugt. Die Daten sind **nicht amtlich** und ersetzen keine offiziellen GIS-Netzgebietsgrenzen.

## Umfang

- Deutschlandweite Karten- und Suchseite mit OSM-Basemap.
- VNBdigital-Meshdaten als GeoJSON-Polygone.
- Spannungsebenen-Filter: `Niederspannung`, `Mittelspannung`, `Hochspannung`.
- Initiale Kartenansicht startet mit `Hochspannung`, weil diese Ebene deutlich weniger Flaechen rendert.
- Nieder- und Mittelspannung werden im Frontend im Hintergrund vorgeladen und gecacht.
- Bundeslandfilter fuer alle deutschen Bundeslaender.
- Suche nach Betreiber, Gebietname und Mesh-Metadaten.
- Detailbereich bei Auswahl eines Gebiets.
- Zugaengliche Ergebnisliste als Alternative zur visuellen Karte.
- FastAPI-Endpunkte fuer Coverage, Bundeslaender, Betreiber, Gebiete, Suche und Koordinaten-Lookup.

Nicht enthalten: User-Accounts, Admin-Panel, Datenbank, amtliche GIS-Daten, API-Keys oder produktive Persistenz.

## Voraussetzungen

- Python 3.12+
- Node.js 22+
- npm
- GNU Make fuer Makefile-Kommandos

## Schnellstart

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
    services/
    data/
      operators.json
      areas.geojson
      federal-states.json
    tests/
frontend/
  index.html
  map.html
  src/
  styles/
vnbdigital/
  build_tile_mesh.py
  export_backend_polygons.py
  analyze_mesh.py
scripts/
```

Die Backend-Daten sind statische JSON/GeoJSON-Dateien. Die `vnbdigital/`-Scripte erzeugen diese Dateien aus VNBdigital-Koordinatenabfragen.

## Daten-Erzeugung

Deutschlandweites 5-km-Mesh abfragen:

```bash
python -m vnbdigital.build_tile_mesh \
  --preset de \
  --spacing-km 5 \
  --output vnbdigital/output/de_5km.geojson
```

Mesh in Backend-Polygone transformieren:

```bash
python -m vnbdigital.export_backend_polygons \
  --input vnbdigital/output/de_5km.geojson \
  --clip-bbox de \
  --federal-state DE \
  --updated-at 2026-04-28
```

Verfuegbare grobe BBox-Presets:

```bash
python -m vnbdigital.build_tile_mesh --list-presets
```

Die erzeugten Polygone sind interpolierte Approximationen. Die Kanten liegen auf den Mittellinien zwischen benachbarten Meshpunkten und werden pro `Betreiber + Spannungsebene` zusammengefuehrt.

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

Gibt die Datenabdeckung je Bundesland zurueck. Da die aktuelle Basis deutschlandweit ist, sind alle deutschen Bundeslaender als `partial` markiert.

```bash
curl http://127.0.0.1:8000/api/coverage
```

### `GET /api/federal-states`

```bash
curl http://127.0.0.1:8000/api/federal-states
```

Liefert alle deutschen Bundeslaender mit `id`, `name`, `hasAreaData` und `dataStatus`.

### `GET /api/operators`

Optionale Query-Parameter: `q`, `type`, `accuracy`, `country`, `federal_state`, `coverage`, `voltage_level`.

```bash
curl "http://127.0.0.1:8000/api/operators?country=DE&federal_state=BY&voltage_level=Hochspannung"
```

### `GET /api/operators/{operator_id}`

```bash
curl http://127.0.0.1:8000/api/operators/vnbdigital-7332
```

### `GET /api/areas`

Optionale Query-Parameter:

- `bbox=minLon,minLat,maxLon,maxLat`
- `operator_id`
- `accuracy`
- `country=DE`
- `federal_state=NW`
- `voltage_level=Hochspannung`

```bash
curl "http://127.0.0.1:8000/api/areas?country=DE&federal_state=NW&voltage_level=Hochspannung"
curl "http://127.0.0.1:8000/api/areas?bbox=6.5,51.0,7.0,51.5&voltage_level=Niederspannung"
```

Antwort ist immer eine gueltige GeoJSON `FeatureCollection`.

### `GET /api/search?q=...`

Sucht in Betreibername, Gebietname und Mesh-Metadaten.

```bash
curl "http://127.0.0.1:8000/api/search?q=westnetz"
```

### `GET /api/lookup?lat=...&lon=...`

Gibt alle passenden Regionen fuer eine Koordinate zurueck. Eine Geo-Location kann mehrere Treffer haben, weil die Regionen nach Spannungsebene getrennt sind.

```bash
curl "http://127.0.0.1:8000/api/lookup?lat=51.4818445&lon=7.2162363"
```

Antwortform:

```json
{
  "match": {"area": {}, "operator": {}},
  "matches": [
    {"area": {}, "operator": {}}
  ]
}
```

`match` bleibt als Legacy-Ersttreffer erhalten; neue Clients sollten `matches` verwenden.

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
- `country`: `DE`
- `federalStates`: bei deutschlandweiter Basisschicht `["DE"]`
- `dataCoverage`: aktuell `partial`
- `mockNotice`: Legacy-Feldname fuer den Hinweistext zur Datenqualitaet

Gebiete liegen in `backend/app/data/areas.geojson` als WGS84/EPSG:4326 GeoJSON.

Wichtige Properties:

- `id`
- `name`
- `operatorId`
- `country`: `DE`
- `federalState`: bei deutschlandweiter Basisschicht `DE`
- `accuracy`: aktuell `municipality_approximation`
- `source`
- `updatedAt`
- `mockNotice`: Legacy-Feldname fuer den Hinweistext zur Datenqualitaet
- `voltageLevels`: z. B. `["Niederspannung"]`
- `voltageLevel`: skalare Spannungsebene der erzeugten Mesh-Schicht
- `vnbdigitalId`
- `samplePointCount`

## Hinweise zur Genauigkeit

- Die Daten stammen aus VNBdigital-Koordinatenabfragen.
- Die aktuelle deutschlandweite Rohauflösung ist 5 km.
- Die Polygone werden aus Rasterzellen abgeleitet und an den Mittellinien zwischen Nachbarpunkten geschnitten.
- Grenzen sind approximiert, nicht amtlich und koennen mehrere Kilometer von offiziellen Netzgebietsgrenzen abweichen.
- Offizielle GIS-Daten koennen spaeter durch Austausch von `areas.geojson`, `operators.json` und `federal-states.json` oder durch einen Importprozess angeschlossen werden.
