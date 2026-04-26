import copy
import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.domain import Accuracy, DataCoverage, OperatorType, SearchMatchedField, VoltageLevel, VOLTAGE_PRIORITY
from app.models import OperatorRecord
from app.schemas import SearchResult
from app.services.geo_service import BBox, bbox_intersects, geometry_bbox, point_in_geometry

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


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
    voltage_level: VoltageLevel | None = None,
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
        if voltage_level and voltage_level not in operator["voltageLevels"]:
            continue
        if matching_operator_ids is not None and operator["id"] not in matching_operator_ids:
            continue
        if normalized_query and normalized_query not in normalize(
            " ".join([operator["name"], operator["description"], operator.get("parentCompany") or ""])
        ):
            continue
        operators.append(operator)
    return operators


def filter_raw_area_features(
    bbox: BBox | None = None,
    operator_id: str | None = None,
    accuracy: Accuracy | None = None,
    country: str | None = None,
    federal_state: str | None = None,
    voltage_level: VoltageLevel | None = None,
) -> list[dict[str, Any]]:
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
        if voltage_level and voltage_level not in properties.get("voltageLevels", []):
            continue
        if bbox and not bbox_intersects(geometry_bbox(feature["geometry"]), bbox):
            continue

        features.append(feature)
    return features


def enrich_area_feature(feature: dict[str, Any], operators_by_id: dict[str, OperatorRecord] | None = None) -> dict[str, Any]:
    operators = operators_by_id or {operator["id"]: operator for operator in load_operators()}
    enriched = copy.deepcopy(feature)
    properties = enriched["properties"]
    properties["operatorName"] = operators[properties["operatorId"]]["name"]
    enriched["bbox"] = list(geometry_bbox(enriched["geometry"]))
    return enriched


def list_enriched_area_features(
    bbox: BBox | None = None,
    operator_id: str | None = None,
    accuracy: Accuracy | None = None,
    country: str | None = None,
    federal_state: str | None = None,
    voltage_level: VoltageLevel | None = None,
) -> list[dict[str, Any]]:
    operators_by_id = {operator["id"]: operator for operator in load_operators()}
    return [
        enrich_area_feature(feature, operators_by_id)
        for feature in filter_raw_area_features(
            bbox=bbox,
            operator_id=operator_id,
            accuracy=accuracy,
            country=country,
            federal_state=federal_state,
            voltage_level=voltage_level,
        )
    ]


def search_all(query: str) -> list[SearchResult]:
    normalized_query = normalize(query)
    operators_by_id = {operator["id"]: operator for operator in load_operators()}
    results = _operator_search_results(normalized_query)

    for feature in list_enriched_area_features():
        results.extend(_area_search_results(feature, operators_by_id, normalized_query))

    return results


def _operator_search_results(normalized_query: str) -> list[SearchResult]:
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
    return results


def _area_search_results(
    feature: dict[str, Any],
    operators_by_id: dict[str, OperatorRecord],
    normalized_query: str,
) -> list[SearchResult]:
    properties = feature["properties"]
    operator = operators_by_id[properties["operatorId"]]
    results: list[SearchResult] = []

    if normalized_query in normalize(properties["name"]):
        results.append(_area_result(properties, operator["name"], "area"))

    results.extend(
        _named_area_results(
            properties=properties,
            operator_name=operator["name"],
            values=properties["places"],
            matched_field="place",
            normalized_query=normalized_query,
        )
    )
    results.extend(
        _named_area_results(
            properties=properties,
            operator_name=operator["name"],
            values=properties["postalCodes"],
            matched_field="postalCode",
            normalized_query=normalized_query,
        )
    )
    return results


def _named_area_results(
    properties: dict[str, Any],
    operator_name: str,
    values: list[str],
    matched_field: SearchMatchedField,
    normalized_query: str,
) -> list[SearchResult]:
    seen: set[tuple[str, SearchMatchedField, str]] = set()
    results: list[SearchResult] = []
    for value in values:
        key = (properties["id"], matched_field, value)
        if normalized_query in normalize(value) and key not in seen:
            seen.add(key)
            results.append(_area_result(properties, operator_name, matched_field, value))
    return results


def find_areas_for_point(lat: float, lon: float) -> list[dict[str, Any]]:
    matches = []
    for feature in list_enriched_area_features():
        if point_in_geometry(lon=lon, lat=lat, geometry=feature["geometry"]):
            matches.append(feature)
    return sorted(matches, key=_area_sort_key)


def find_area_for_point(lat: float, lon: float) -> dict[str, Any] | None:
    matches = find_areas_for_point(lat=lat, lon=lon)
    return matches[0] if matches else None


def _area_sort_key(feature: dict[str, Any]) -> tuple[int, str, str]:
    properties = feature["properties"]
    voltage_priority = min(
        (VOLTAGE_PRIORITY.get(level, 99) for level in properties.get("voltageLevels", [])),
        default=99,
    )
    return voltage_priority, properties["operatorName"], properties["id"]


def normalize(value: str | None) -> str:
    if not value:
        return ""
    value = (
        value.strip()
        .casefold()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _area_result(
    properties: dict[str, Any],
    operator_name: str,
    matched_field: SearchMatchedField,
    label: str | None = None,
) -> SearchResult:
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
        if geometry.get("type") not in {"Point", "Polygon", "MultiPolygon"}:
            raise ValueError("areas.geojson features must be Point, Polygon or MultiPolygon")
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
            "voltageLevels",
        }
        missing = required - set(properties)
        if missing:
            raise ValueError(f"areas.geojson feature is missing properties: {sorted(missing)}")
