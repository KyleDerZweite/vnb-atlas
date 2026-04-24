from typing import Any, Literal

from fastapi import APIRouter, Query

from app.services.data_service import filter_area_features, parse_accuracy
from app.services.geo_service import parse_bbox

router = APIRouter(prefix="/api/areas", tags=["areas"])


@router.get("")
def list_areas(
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    operator_id: str | None = Query(default=None, max_length=80),
    accuracy: Literal["mock", "municipality_approximation", "verified"] | None = Query(default=None),
) -> dict[str, Any]:
    parsed_bbox = parse_bbox(bbox) if bbox else None
    return {
        "type": "FeatureCollection",
        "features": filter_area_features(
            bbox=parsed_bbox,
            operator_id=operator_id,
            accuracy=parse_accuracy(accuracy),
        ),
        "mockNotice": "Mock-Daten / nicht amtlich. Grenzen zeigen keine echten VNB-Zustaendigkeiten.",
    }
