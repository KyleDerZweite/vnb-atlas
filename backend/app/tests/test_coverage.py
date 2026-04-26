from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FEDERAL_STATE_COUNT = 16
AVAILABLE_STATE_ID = "NW"
AVAILABLE_STATE_STATUS = "partial"


def test_coverage_marks_nw_as_only_available_state() -> None:
    response = client.get("/api/coverage")
    assert response.status_code == 200
    body = response.json()
    assert body["country"] == "DE"
    assert body["federalStates"][AVAILABLE_STATE_ID]["hasAreas"] is True
    assert body["federalStates"][AVAILABLE_STATE_ID]["status"] == AVAILABLE_STATE_STATUS
    assert body["federalStates"]["BY"]["hasAreas"] is False
    assert body["federalStates"]["BY"]["status"] == "not_available"


def test_federal_states_lists_all_german_states() -> None:
    response = client.get("/api/federal-states")
    assert response.status_code == 200
    states = response.json()
    assert len(states) == FEDERAL_STATE_COUNT
    assert any(state["id"] == AVAILABLE_STATE_ID and state["hasAreaData"] for state in states)
