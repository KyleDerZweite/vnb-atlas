import copy
import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.models import Accuracy, DataCoverage, OperatorRecord, OperatorType
from app.schemas import SearchResult
from app.services.geo_service import BBox, bbox_intersects, geometry_bbox, point_in_geometry

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def parse_operator_type(value: str | None) -> OperatorType | None:
    if value is None:
        return None
    return value  # FastAPI already validated the literal.


def parse_accuracy(value: str | None) -> Accuracy | None:
    if value is None:
        return None
    return value  # FastAPI already validated the literal.


def parse_coverage(value: str | None) -> DataCoverage | None:
    if value is None:
        return None
    return value  # FastAPI already validated the literal.


@lru_cache
def load_operators() -> list[OperatorRecord]:
    with (DATA_DIR / "operators.json").open(encoding="utf-8") as file:
        return json.load(file)


@lru_cache
def load_areas() -> dict[str, Any]:
    with (DATA_DIR / "areas.geojson").open(encoding="utf-8") as file:
        data = json.load(file)
    _validate_feature_collection(data)
    return data


def get_operator(operator_id: str) -> OperatorRecord | None:
    return next((operator for operator in load_operators() if operator["id"] == operator_id), None)


def filter_operators(
    q: str | None = None,
    operator_type: OperatorType | None = None,
    accuracy: Accuracy | None = None,
    country: str | None = None,
    federal_state: str | None = None,
    coverage: DataCoverage | None = None,
) -> list[OperatorRecord]:
    normalized_query = normalize(q)
    matching_operator_ids = None
    if accuracy:
        matching_operator_ids = {
            feature["properties"]["operatorId"]
            for feature in load_areas()["features"]
            if feature["properties"]["accuracy"] == accuracy
        }

    operators = []
    for operator in load_operators():
        if operator_type and operator["type"] != operator_type:
            continue
        if country and operator["country"] != country:
            continue
        if federal_state and federal_state not in operator["federalStates"]:
            continue
        if coverage and operator["dataCoverage"] != coverage:
            continue
        if matching_operator_ids is not None and operator["id"] not in matching_operator_ids:
            continue
        if normalized_query and normalized_query not in normalize(
            " ".join([operator["name"], operator["description"], operator.get("parentCompany") or ""])
        ):
            continue
        operators.append(operator)
    return operators


def filter_area_features(
    bbox: BBox | None = None,
    operator_id: str | None = None,
    accuracy: Accuracy | None = None,
    country: str | None = None,
    federal_state: str | None = None,
) -> list[dict[str, Any]]:
    operators_by_id = {operator["id"]: operator for operator in load_operators()}
    features = []

    for feature in load_areas()["features"]:
        properties = feature["properties"]
        if operator_id and properties["operatorId"] != operator_id:
            continue
        if country and properties["country"] != country:
            continue
        if federal_state and properties["federalState"] != federal_state:
            continue
        if accuracy and properties["accuracy"] != accuracy:
            continue
        if bbox and not bbox_intersects(geometry_bbox(feature["geometry"]), bbox):
            continue

        enriched = copy.deepcopy(feature)
        enriched["properties"]["operatorName"] = operators_by_id[properties["operatorId"]]["name"]
        enriched["bbox"] = list(geometry_bbox(enriched["geometry"]))
        features.append(enriched)
    return features


def search_all(query: str) -> list[SearchResult]:
    normalized_query = normalize(query)
    operators_by_id = {operator["id"]: operator for operator in load_operators()}
    results: list[SearchResult] = []

    for operator in load_operators():
        haystack = normalize(" ".join([operator["name"], operator["description"], operator.get("parentCompany") or ""]))
        if normalized_query in haystack:
            results.append(
                SearchResult(
                    type="operator",
                    label=operator["name"],
                    operatorId=operator["id"],
                    operatorName=operator["name"],
                    matchedField="operator",
                )
            )

    seen_place_matches: set[tuple[str, str, str]] = set()
    for feature in filter_area_features():
        properties = feature["properties"]
        operator = operators_by_id[properties["operatorId"]]
        if normalized_query in normalize(properties["name"]):
            results.append(_area_result(properties, operator["name"], "area"))

        for place in properties["places"]:
            key = (properties["id"], "place", place)
            if normalized_query in normalize(place) and key not in seen_place_matches:
                seen_place_matches.add(key)
                results.append(_area_result(properties, operator["name"], "place", place))

        for postal_code in properties["postalCodes"]:
            key = (properties["id"], "postalCode", postal_code)
            if normalized_query in normalize(postal_code) and key not in seen_place_matches:
                seen_place_matches.add(key)
                results.append(_area_result(properties, operator["name"], "postalCode", postal_code))

    return results


def find_area_for_point(lat: float, lon: float) -> dict[str, Any] | None:
    for feature in filter_area_features():
        if point_in_geometry(lon=lon, lat=lat, geometry=feature["geometry"]):
            return feature
    return None


def normalize(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value.strip().casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _area_result(properties: dict[str, Any], operator_name: str, matched_field: str, label: str | None = None) -> SearchResult:
    return SearchResult(
        type="postalCode" if matched_field == "postalCode" else "place" if matched_field == "place" else "area",
        label=label or properties["name"],
        operatorId=properties["operatorId"],
        operatorName=operator_name,
        areaId=properties["id"],
        areaName=properties["name"],
        accuracy=properties["accuracy"],
        matchedField=matched_field,
    )


def _validate_feature_collection(data: dict[str, Any]) -> None:
    if data.get("type") != "FeatureCollection":
        raise ValueError("areas.geojson must be a FeatureCollection")
    for feature in data.get("features", []):
        geometry = feature.get("geometry", {})
        if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            raise ValueError("areas.geojson features must be Polygon or MultiPolygon")
        geometry_bbox(geometry)
        properties = feature.get("properties", {})
        required = {
            "id",
            "name",
            "operatorId",
            "country",
            "federalState",
            "accuracy",
            "source",
            "updatedAt",
            "mockNotice",
            "places",
            "postalCodes",
        }
        missing = required - set(properties)
        if missing:
            raise ValueError(f"areas.geojson feature is missing properties: {sorted(missing)}")
