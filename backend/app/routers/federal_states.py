from fastapi import APIRouter

from app.schemas import FederalState
from app.services.coverage_service import get_federal_states

router = APIRouter(prefix="/api/federal-states", tags=["federal-states"])


@router.get("", response_model=list[FederalState])
def federal_states() -> list[FederalState]:
    return get_federal_states()
