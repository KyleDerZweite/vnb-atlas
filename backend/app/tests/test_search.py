from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_by_city_without_umlaut() -> None:
    response = client.get("/api/search", params={"q": "duesseldorf"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(result["operatorId"] == "vnbdigital-153" for result in body["results"])


def test_search_by_voltage_area() -> None:
    response = client.get("/api/search", params={"q": "niederspannung"})
    assert response.status_code == 200
    body = response.json()
    assert any(result["matchedField"] == "area" for result in body["results"])


def test_search_by_operator() -> None:
    response = client.get("/api/search", params={"q": "westnetz"})
    assert response.status_code == 200
    body = response.json()
    assert any(result["operatorId"] == "vnbdigital-7332" for result in body["results"])


def test_search_rejects_blank_query() -> None:
    response = client.get("/api/search", params={"q": "   "})
    assert response.status_code == 400
