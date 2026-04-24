from fastapi import APIRouter

from app.schemas import CountryCoverage
from app.services.coverage_service import get_coverage

router = APIRouter(prefix="/api/coverage", tags=["coverage"])


@router.get("", response_model=CountryCoverage)
def coverage() -> CountryCoverage:
    return get_coverage()
