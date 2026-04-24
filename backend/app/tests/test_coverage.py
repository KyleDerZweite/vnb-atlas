from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_coverage_marks_nw_as_only_available_state() -> None:
    response = client.get("/api/coverage")
    assert response.status_code == 200
    body = response.json()
    assert body["country"] == "DE"
    assert body["federalStates"]["NW"]["hasAreas"] is True
    assert body["federalStates"]["NW"]["status"] == "mock"
    assert body["federalStates"]["BY"]["hasAreas"] is False
    assert body["federalStates"]["BY"]["status"] == "not_available"


def test_federal_states_lists_all_german_states() -> None:
    response = client.get("/api/federal-states")
    assert response.status_code == 200
    states = response.json()
    assert len(states) == 16
    assert any(state["id"] == "NW" and state["hasAreaData"] for state in states)
