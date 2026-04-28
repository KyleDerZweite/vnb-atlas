# Deutschland VNB Atlas Backend

FastAPI-Backend fuer den Deutschland VNB Atlas.

Die API liefert statische Betreiber- und Gebietsdaten aus `app/data/`. Die aktuelle Datenbasis ist ein deutschlandweites VNBdigital-Koordinatenmesh mit daraus erzeugten approximierten Polygonen. Die Daten sind nicht amtlich.

## Start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

OpenAPI ist unter `http://localhost:8000/docs` verfuegbar.

## Tests

```bash
pytest
```

## Wichtige Endpunkte

- `GET /api/coverage`
- `GET /api/federal-states`
- `GET /api/operators`
- `GET /api/areas`
- `GET /api/search`
- `GET /api/lookup`

`/api/areas` und `/api/operators` unterstuetzen `voltage_level=Niederspannung|Mittelspannung|Hochspannung`.
