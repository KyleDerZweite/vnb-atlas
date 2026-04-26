from fastapi import APIRouter, HTTPException, Query

from app.domain import Accuracy, CountryCode, DataCoverage, OperatorType, VoltageLevel
from app.schemas import Operator
from app.services.data_service import filter_operators, get_operator

router = APIRouter(prefix="/api/operators", tags=["operators"])


@router.get("", response_model=list[Operator])
def list_operators(
    q: str | None = Query(default=None, max_length=80),
    type: OperatorType | None = Query(default=None),
    accuracy: Accuracy | None = Query(default=None),
    country: CountryCode | None = Query(default=None),
    federal_state: str | None = Query(default=None, min_length=2, max_length=2),
    coverage: DataCoverage | None = Query(default=None),
    voltage_level: VoltageLevel | None = Query(default=None),
) -> list[Operator]:
    return [
        Operator.model_validate(operator)
        for operator in filter_operators(
            q=q,
            operator_type=type,
            accuracy=accuracy,
            country=country,
            federal_state=federal_state,
            coverage=coverage,
            voltage_level=voltage_level,
        )
    ]


@router.get("/{operator_id}", response_model=Operator)
def operator_detail(operator_id: str) -> Operator:
    operator = get_operator(operator_id)
    if operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return Operator.model_validate(operator)
