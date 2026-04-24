from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lookup_inside_area() -> None:
    response = client.get("/api/lookup", params={"lat": 51.23, "lon": 6.78})
    assert response.status_code == 200
    body = response.json()
    assert body["match"] is not None
    assert body["match"]["area"]["properties"]["id"] == "mock-duesseldorf"
    assert body["match"]["operator"]["id"] == "sw-duesseldorf-netz-mock"


def test_lookup_outside_area() -> None:
    response = client.get("/api/lookup", params={"lat": 52.5, "lon": 9.5})
    assert response.status_code == 200
    assert response.json() == {"match": None}
