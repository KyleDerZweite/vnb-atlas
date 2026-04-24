from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_areas_feature_collection() -> None:
    response = client.get("/api/areas")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 5
    first_feature = body["features"][0]
    assert first_feature["type"] == "Feature"
    assert first_feature["geometry"]["coordinates"][0][0] == first_feature["geometry"]["coordinates"][0][-1]
    assert first_feature["properties"]["operatorName"]
    assert first_feature["properties"]["country"] == "DE"
    assert first_feature["properties"]["federalState"] == "NW"


def test_areas_filters_by_bbox_and_operator() -> None:
    response = client.get("/api/areas", params={"bbox": "6.50,51.00,7.00,51.45", "operator_id": "sw-duesseldorf-netz-mock"})
    assert response.status_code == 200
    body = response.json()
    assert [feature["properties"]["id"] for feature in body["features"]] == ["mock-duesseldorf"]


def test_areas_rejects_invalid_bbox() -> None:
    response = client.get("/api/areas", params={"bbox": "7,51,6,50"})
    assert response.status_code == 400


def test_areas_filters_by_country_and_federal_state() -> None:
    response = client.get("/api/areas", params={"country": "DE", "federal_state": "NW"})
    assert response.status_code == 200
    assert len(response.json()["features"]) == 5


def test_areas_for_state_without_data_returns_empty_feature_collection() -> None:
    response = client.get("/api/areas", params={"country": "DE", "federal_state": "BY"})
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert body["features"] == []
