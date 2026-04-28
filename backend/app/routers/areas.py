from typing import Any

from fastapi import APIRouter, Query

from app.domain import Accuracy, CountryCode, VoltageLevel
from app.services.data_service import list_enriched_area_features
from app.services.geo_service import parse_bbox

router = APIRouter(prefix="/api/areas", tags=["areas"])


@router.get("")
def list_areas(
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    operator_id: str | None = Query(default=None, max_length=80),
    accuracy: Accuracy | None = Query(default=None),
    country: CountryCode | None = Query(default=None),
    federal_state: str | None = Query(default=None, min_length=2, max_length=2),
    voltage_level: VoltageLevel | None = Query(default=None),
) -> dict[str, Any]:
    parsed_bbox = parse_bbox(bbox) if bbox else None
    return {
        "type": "FeatureCollection",
        "features": list_enriched_area_features(
            bbox=parsed_bbox,
            operator_id=operator_id,
            accuracy=accuracy,
            country=country,
            federal_state=federal_state,
            voltage_level=voltage_level,
        ),
        "mockNotice": "Deutschlandweite VNBdigital-Meshdaten / nicht amtliche GIS-Grenzen.",
    }
