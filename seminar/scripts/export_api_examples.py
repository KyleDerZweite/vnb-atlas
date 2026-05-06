from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
OUT = Path(__file__).resolve().parents[1] / "examples"

sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def write_json(name: str, data: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    client = TestClient(app)

    examples = {
        "health.json": client.get("/health").json(),
        "operators_westnetz.json": client.get("/api/operators", params={"q": "westnetz"}).json(),
        "areas_hochspannung_nw.json": client.get(
            "/api/areas",
            params={"country": "DE", "federal_state": "NW", "voltage_level": "Hochspannung"},
        ).json(),
        "lookup_bochum.json": client.get("/api/lookup", params={"lat": 51.4818445, "lon": 7.2162363}).json(),
        "search_westnetz.json": client.get("/api/search", params={"q": "westnetz"}).json(),
    }

    for name, payload in examples.items():
        write_json(name, payload)

    openapi = app.openapi()
    write_json("openapi.json", openapi)

    route_summary = {
        "title": openapi["info"]["title"],
        "version": openapi["info"]["version"],
        "openapi": openapi["openapi"],
        "paths": sorted(openapi["paths"].keys()),
        "areas_response_schema": openapi["paths"]["/api/areas"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"],
    }
    write_json("openapi_summary.json", route_summary)


if __name__ == "__main__":
    main()
