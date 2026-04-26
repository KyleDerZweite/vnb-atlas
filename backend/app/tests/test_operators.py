from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

GENERATED_OPERATOR_COUNT = 238
GENERATED_NW_OPERATOR_COUNT = 130
GENERATED_HOCHSPANNUNG_OPERATOR_COUNT = 44


def test_list_operators() -> None:
    response = client.get("/api/operators")
    assert response.status_code == 200
    operators = response.json()
    assert len(operators) == GENERATED_OPERATOR_COUNT
    assert all(operator["dataCoverage"] == "partial" for operator in operators)


def test_filter_operators_by_query_and_accuracy() -> None:
    response = client.get("/api/operators", params={"q": "westnetz", "accuracy": "municipality_approximation"})
    assert response.status_code == 200
    operators = response.json()
    assert [operator["id"] for operator in operators] == ["vnbdigital-7332"]


def test_filter_operators_by_country_state_and_coverage() -> None:
    response = client.get("/api/operators", params={"country": "DE", "federal_state": "NW", "coverage": "partial"})
    assert response.status_code == 200
    assert len(response.json()) == GENERATED_NW_OPERATOR_COUNT


def test_filter_operators_by_voltage_level() -> None:
    response = client.get("/api/operators", params={"voltage_level": "Hochspannung"})
    assert response.status_code == 200
    operators = response.json()
    assert len(operators) == GENERATED_HOCHSPANNUNG_OPERATOR_COUNT
    assert all("Hochspannung" in operator["voltageLevels"] for operator in operators)


def test_filter_operators_for_state_without_data_is_empty() -> None:
    response = client.get("/api/operators", params={"country": "DE", "federal_state": "BY"})
    assert response.status_code == 200
    assert response.json() == []


def test_operator_detail_not_found() -> None:
    response = client.get("/api/operators/unknown")
    assert response.status_code == 404
