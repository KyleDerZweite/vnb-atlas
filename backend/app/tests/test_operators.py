from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_operators() -> None:
    response = client.get("/api/operators")
    assert response.status_code == 200
    operators = response.json()
    assert len(operators) == 5
    assert all("Mock" in operator["name"] for operator in operators)


def test_filter_operators_by_query_and_accuracy() -> None:
    response = client.get("/api/operators", params={"q": "westnetz", "accuracy": "municipality_approximation"})
    assert response.status_code == 200
    operators = response.json()
    assert [operator["id"] for operator in operators] == ["westnetz-mock"]


def test_operator_detail_not_found() -> None:
    response = client.get("/api/operators/unknown")
    assert response.status_code == 404
