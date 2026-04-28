from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FEDERAL_STATE_COUNT = 16
AVAILABLE_STATE_STATUS = "partial"


def test_coverage_marks_all_states_as_available_from_germany_baseline() -> None:
    response = client.get("/api/coverage")
    assert response.status_code == 200
    body = response.json()
    assert body["country"] == "DE"
    assert all(state["hasAreas"] is True for state in body["federalStates"].values())
    assert all(state["status"] == AVAILABLE_STATE_STATUS for state in body["federalStates"].values())


def test_federal_states_lists_all_german_states() -> None:
    response = client.get("/api/federal-states")
    assert response.status_code == 200
    states = response.json()
    assert len(states) == FEDERAL_STATE_COUNT
    assert all(state["hasAreaData"] for state in states)
