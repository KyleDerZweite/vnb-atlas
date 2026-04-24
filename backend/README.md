# NRW VNB Atlas Backend

FastAPI-Backend fuer das NRW VNB Atlas MVP. Die Daten in `app/data/` sind Mock-Daten und nicht amtlich.

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
