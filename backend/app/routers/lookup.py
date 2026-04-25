from fastapi import APIRouter, HTTPException, Query

from app.schemas import LookupResponse, Operator
from app.services.data_service import find_areas_for_point, get_operator

router = APIRouter(prefix="/api/lookup", tags=["lookup"])


@router.get("", response_model=LookupResponse)
def lookup(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
) -> LookupResponse:
    matches = []
    for feature in find_areas_for_point(lat=lat, lon=lon):
        operator = get_operator(feature["properties"]["operatorId"])
        if operator is None:
            raise HTTPException(status_code=500, detail="Area references unknown operator")
        matches.append({"area": feature, "operator": Operator.model_validate(operator)})

    return LookupResponse(match=matches[0] if matches else None, matches=matches)
