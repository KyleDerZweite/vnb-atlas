# Deutschland VNB Atlas Backend

FastAPI-Backend fuer das Deutschland VNB Atlas MVP. Die Anwendung ist deutschlandweit ausgelegt; befuellte GIS-/Mockdaten gibt es im MVP nur fuer Nordrhein-Westfalen.

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
