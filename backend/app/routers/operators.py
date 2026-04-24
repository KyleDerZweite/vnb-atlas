from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas import Operator
from app.services.data_service import (
    filter_operators,
    get_operator,
    parse_accuracy,
    parse_coverage,
    parse_operator_type,
)

router = APIRouter(prefix="/api/operators", tags=["operators"])


@router.get("", response_model=list[Operator])
def list_operators(
    q: str | None = Query(default=None, max_length=80),
    type: Literal["VNB", "ÜNB", "UNKNOWN"] | None = Query(default=None),
    accuracy: Literal["mock", "municipality_approximation", "verified"] | None = Query(default=None),
    country: Literal["DE"] | None = Query(default=None),
    federal_state: str | None = Query(default=None, min_length=2, max_length=2),
    coverage: Literal["none", "mock", "partial", "verified"] | None = Query(default=None),
) -> list[Operator]:
    return [
        Operator.model_validate(operator)
        for operator in filter_operators(
            q=q,
            operator_type=parse_operator_type(type),
            accuracy=parse_accuracy(accuracy),
            country=country,
            federal_state=federal_state,
            coverage=parse_coverage(coverage),
        )
    ]


@router.get("/{operator_id}", response_model=Operator)
def operator_detail(operator_id: str) -> Operator:
    operator = get_operator(operator_id)
    if operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return Operator.model_validate(operator)
