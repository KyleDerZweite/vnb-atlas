from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lookup_inside_area() -> None:
    response = client.get("/api/lookup", params={"lat": 51.23, "lon": 6.78})
    assert response.status_code == 200
    body = response.json()
    assert body["match"] is not None
    assert body["match"]["operator"]["id"] == "vnbdigital-153"
    assert [match["area"]["properties"]["voltageLevel"] for match in body["matches"]] == [
        "Niederspannung",
        "Mittelspannung",
        "Hochspannung",
    ]


def test_lookup_outside_area() -> None:
    response = client.get("/api/lookup", params={"lat": 55.5, "lon": 15.5})
    assert response.status_code == 200
    assert response.json() == {"match": None, "matches": []}
