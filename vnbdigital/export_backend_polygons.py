"""Export VNBdigital mesh data as approximate backend polygons.

The mesh points are converted into rectangular cells whose edges sit halfway
between neighboring mesh points. Cells are grouped by operator and voltage
level, then dissolved into Polygon/MultiPolygon geometries.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

from .bbox_presets import resolve_bbox_preset

DEFAULT_INPUT = "vnbdigital/output/nrw_vnb_mesh.geojson"
DEFAULT_OPERATORS_OUTPUT = "backend/app/data/operators.json"
DEFAULT_AREAS_OUTPUT = "backend/app/data/areas.geojson"
DEFAULT_FEDERAL_STATES = "backend/app/data/federal-states.json"
DEFAULT_CLIP_BBOX = "6.15,50.55,9.45,52.50"
SOURCE_LABEL = "VNBdigital Koordinaten-Mesh, 10-km-Raster, approximierte Mittellinien-Polygone"
DATA_NOTICE = (
    "VNBdigital-Meshdaten / nicht amtliche GIS-Grenzen. "
    "Polygone sind aus Rasterpunkten interpoliert und ersetzen keine offiziellen Netzgebietsgrenzen."
)
VOLTAGE_ORDER = {"Niederspannung": 0, "Mittelspannung": 1, "Hochspannung": 2}


@dataclass(frozen=True)
class OperatorVoltageKey:
    operator_id: str
    operator_name: str
    vnb_id: str
    voltage_level: str


@dataclass
class ExportConfig:
    input_path: Path
    operators_output: Path
    areas_output: Path
    federal_states_path: Path
    clip_bbox: tuple[float, float, float, float]
    federal_state: str
    updated_at: str
    overlay_inputs: list[Path]
    overlay_clip_bboxes: list[tuple[float, float, float, float]]
    overlay_federal_states: list[str]


@dataclass
class PolygonLayer:
    operators: dict[str, dict[str, Any]]
    voltage_levels_by_operator: dict[str, set[str]]
    features: list[dict[str, Any]]
    coverage_geometry: Any


def slugify(value: str) -> str:
    slug = value.casefold()
    slug = slug.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "unknown"


def operator_id(vnb_id: str, name: str) -> str:
    if vnb_id:
        return f"vnbdigital-{slugify(vnb_id)}"
    return f"vnbdigital-{slugify(name)}"


def parse_bbox(raw_bbox: str) -> tuple[float, float, float, float]:
    try:
        raw_bbox = resolve_bbox_preset(raw_bbox)
    except ValueError:
        pass
    west, south, east, north = [float(part.strip()) for part in raw_bbox.split(",")]
    if west >= east or south >= north:
        raise ValueError("bbox must satisfy west < east and south < north")
    return west, south, east, north


def load_feature_collection(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{path} is not a GeoJSON FeatureCollection")
    return data


def rounded(value: float) -> float:
    return round(float(value), 6)


def midpoint_edges(values: list[float], clip_min: float, clip_max: float) -> dict[float, tuple[float, float]]:
    sorted_values = sorted({rounded(value) for value in values})
    edges: dict[float, tuple[float, float]] = {}
    for index, value in enumerate(sorted_values):
        if index == 0:
            lower = clip_min
        else:
            lower = (sorted_values[index - 1] + value) / 2

        if index == len(sorted_values) - 1:
            upper = clip_max
        else:
            upper = (value + sorted_values[index + 1]) / 2

        edges[value] = (max(clip_min, lower), min(clip_max, upper))
    return edges


def build_point_cells(
    mesh_features: list[dict[str, Any]],
    clip_bbox: tuple[float, float, float, float],
) -> dict[tuple[float, float], Any]:
    west, south, east, north = clip_bbox
    points_by_lat: dict[float, list[float]] = defaultdict(list)
    lat_values: list[float] = []

    for feature in mesh_features:
        properties = feature.get("properties") or {}
        lat = properties.get("lat")
        lon = properties.get("lon")
        if not isinstance(lat, int | float) or not isinstance(lon, int | float):
            continue
        lat_key = rounded(lat)
        lon_key = rounded(lon)
        lat_values.append(lat_key)
        points_by_lat[lat_key].append(lon_key)

    lat_edges = midpoint_edges(lat_values, south, north)
    cells: dict[tuple[float, float], Any] = {}
    for lat, lon_values in points_by_lat.items():
        lon_edges = midpoint_edges(lon_values, west, east)
        south_edge, north_edge = lat_edges[lat]
        for lon in lon_values:
            west_edge, east_edge = lon_edges[lon]
            if west_edge < east_edge and south_edge < north_edge:
                cells[(lat, lon)] = box(west_edge, south_edge, east_edge, north_edge)
    return cells


def voltage_sort_key(voltage: str) -> tuple[int, str]:
    return VOLTAGE_ORDER.get(voltage, 99), voltage


def clean_geometry(geometry: Any) -> Any:
    if geometry.is_empty:
        return geometry
    cleaned = geometry.buffer(0)
    return cleaned if not cleaned.is_empty else geometry


def export_polygon_layer(
    mesh: dict[str, Any],
    clip_bbox: tuple[float, float, float, float],
    updated_at: str,
    federal_state: str,
) -> PolygonLayer:
    mesh_features = list(mesh.get("features") or [])
    cells_by_point = build_point_cells(mesh_features, clip_bbox)
    clip_geometry = box(*clip_bbox)
    coverage_geometry = clean_geometry(unary_union(list(cells_by_point.values())).intersection(clip_geometry))

    operators_by_id: dict[str, dict[str, Any]] = {}
    voltage_levels_by_operator: dict[str, set[str]] = defaultdict(set)
    cells_by_operator_voltage: dict[OperatorVoltageKey, list[Any]] = defaultdict(list)
    sample_point_count_by_operator_voltage: dict[OperatorVoltageKey, int] = defaultdict(int)

    for feature in mesh_features:
        properties = feature.get("properties") or {}
        lat = properties.get("lat")
        lon = properties.get("lon")
        if not isinstance(lat, int | float) or not isinstance(lon, int | float):
            continue
        cell = cells_by_point.get((rounded(lat), rounded(lon)))
        if cell is None:
            continue

        for operator in properties.get("operators") or []:
            vnb_id = str(operator.get("vnbId") or "")
            name = str(operator.get("name") or "Unbekannter VNB")
            op_id = operator_id(vnb_id, name)
            voltage_levels = [str(level) for level in operator.get("voltageTypes") or []]

            operators_by_id.setdefault(
                op_id,
                {
                    "id": op_id,
                    "name": name,
                    "type": "VNB",
                    "website": "",
                    "parentCompany": None,
                    "description": f"Aus VNBdigital-Koordinatenmesh abgeleiteter Betreiber-Datensatz fuer {name}.",
                    "voltageLevels": [],
                    "country": "DE",
                    "federalStates": [federal_state],
                    "dataCoverage": "partial",
                    "mockNotice": DATA_NOTICE,
                },
            )

            for voltage_level in voltage_levels:
                voltage_levels_by_operator[op_id].add(voltage_level)
                key = OperatorVoltageKey(op_id, name, vnb_id, voltage_level)
                cells_by_operator_voltage[key].append(cell)
                sample_point_count_by_operator_voltage[key] += 1

    area_features: list[dict[str, Any]] = []
    for key, cells in sorted(
        cells_by_operator_voltage.items(),
        key=lambda item: (voltage_sort_key(item[0].voltage_level), item[0].operator_name.casefold()),
    ):
        op_id = key.operator_id
        name = key.operator_name
        vnb_id = key.vnb_id
        voltage_level = key.voltage_level
        dissolved = clean_geometry(unary_union(cells).intersection(clip_geometry))
        if dissolved.is_empty:
            continue
        area_features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"mesh-{slugify(federal_state)}-{op_id}-{slugify(voltage_level)}",
                    "name": f"{name} ({voltage_level})",
                    "operatorId": op_id,
                    "country": "DE",
                    "federalState": federal_state,
                    "accuracy": "municipality_approximation",
                    "source": SOURCE_LABEL,
                    "updatedAt": updated_at,
                    "mockNotice": DATA_NOTICE,
                    "places": [f"VNBdigital Mesh {voltage_level}"],
                    "postalCodes": [],
                    "voltageLevels": [voltage_level],
                    "voltageLevel": voltage_level,
                    "vnbdigitalId": vnb_id,
                    "samplePointCount": sample_point_count_by_operator_voltage[key],
                },
                "geometry": mapping(dissolved),
            }
        )

    return PolygonLayer(
        operators=operators_by_id,
        voltage_levels_by_operator=voltage_levels_by_operator,
        features=area_features,
        coverage_geometry=coverage_geometry,
    )


def subtract_coverage(features: list[dict[str, Any]], coverage_geometry: Any) -> list[dict[str, Any]]:
    if coverage_geometry.is_empty:
        return features

    clipped_features = []
    for feature in features:
        geometry = clean_geometry(shape(feature["geometry"]).difference(coverage_geometry))
        if geometry.is_empty:
            continue
        clipped_feature = json.loads(json.dumps(feature))
        clipped_feature["geometry"] = mapping(geometry)
        clipped_features.append(clipped_feature)
    return clipped_features


def merge_polygon_layers(base_layer: PolygonLayer, overlay_layers: list[PolygonLayer]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    overlay_coverage = unary_union([layer.coverage_geometry for layer in overlay_layers if not layer.coverage_geometry.is_empty])
    features = subtract_coverage(base_layer.features, overlay_coverage)
    for layer in overlay_layers:
        features.extend(layer.features)

    operators_by_id: dict[str, dict[str, Any]] = {}
    voltage_levels_by_operator: dict[str, set[str]] = defaultdict(set)

    for layer in [base_layer, *overlay_layers]:
        for op_id, operator in layer.operators.items():
            existing = operators_by_id.setdefault(op_id, json.loads(json.dumps(operator)))
            existing_states = set(existing["federalStates"])
            existing_states.update(operator["federalStates"])
            existing["federalStates"] = sorted(existing_states)
            voltage_levels_by_operator[op_id].update(layer.voltage_levels_by_operator[op_id])

    for op_id, operator in operators_by_id.items():
        operator["voltageLevels"] = sorted(voltage_levels_by_operator[op_id], key=voltage_sort_key)

    operators = sorted(operators_by_id.values(), key=lambda operator: operator["name"].casefold())
    features = sorted(
        features,
        key=lambda feature: (
            voltage_sort_key(feature["properties"].get("voltageLevel", "")),
            feature["properties"].get("operatorId", ""),
            feature["properties"].get("federalState", ""),
        ),
    )
    return operators, {"type": "FeatureCollection", "features": features}


def export_backend_data(
    mesh: dict[str, Any],
    clip_bbox: tuple[float, float, float, float],
    updated_at: str,
    federal_state: str = "NW",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    layer = export_polygon_layer(mesh, clip_bbox, updated_at, federal_state)
    return merge_polygon_layers(layer, [])


def update_federal_states(path: Path) -> None:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as file:
        states = json.load(file)
    for state in states:
        if state.get("id") == "NW":
            state["hasAreaData"] = True
            state["dataStatus"] = "partial"
    write_json(path, states)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def validate_area_geometries(areas: dict[str, Any]) -> None:
    for feature in areas["features"]:
        geometry = shape(feature["geometry"])
        if geometry.is_empty or not geometry.is_valid:
            raise ValueError(f"Invalid geometry for {feature['properties']['id']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export VNBdigital mesh as approximate backend polygons.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="input VNBdigital mesh GeoJSON")
    parser.add_argument(
        "--overlay-input",
        action="append",
        default=[],
        help="higher-resolution mesh GeoJSON that supersedes the base input; can be repeated",
    )
    parser.add_argument("--operators-output", default=DEFAULT_OPERATORS_OUTPUT, help="backend operators.json path")
    parser.add_argument("--areas-output", default=DEFAULT_AREAS_OUTPUT, help="backend areas.geojson path")
    parser.add_argument("--federal-states", default=DEFAULT_FEDERAL_STATES, help="backend federal-states.json path")
    parser.add_argument("--clip-bbox", default=DEFAULT_CLIP_BBOX, help="base clipping bbox or preset name")
    parser.add_argument(
        "--overlay-clip-bbox",
        action="append",
        default=[],
        help="overlay clipping bbox or preset name; repeat once per --overlay-input",
    )
    parser.add_argument("--federal-state", default="NW", help="federalState property for the base input")
    parser.add_argument(
        "--overlay-federal-state",
        action="append",
        default=[],
        help="federalState property for overlay input; repeat once per --overlay-input",
    )
    parser.add_argument("--updated-at", default=datetime.now(UTC).date().isoformat(), help="updatedAt date")
    return parser


def export_config_from_args(args: argparse.Namespace) -> ExportConfig:
    if len(args.overlay_clip_bbox) not in {0, len(args.overlay_input)}:
        raise ValueError("--overlay-clip-bbox must be omitted or repeated once per --overlay-input")
    if len(args.overlay_federal_state) not in {0, len(args.overlay_input)}:
        raise ValueError("--overlay-federal-state must be omitted or repeated once per --overlay-input")

    return ExportConfig(
        input_path=Path(args.input),
        operators_output=Path(args.operators_output),
        areas_output=Path(args.areas_output),
        federal_states_path=Path(args.federal_states),
        clip_bbox=parse_bbox(args.clip_bbox),
        federal_state=args.federal_state,
        updated_at=args.updated_at,
        overlay_inputs=[Path(input_path) for input_path in args.overlay_input],
        overlay_clip_bboxes=[
            parse_bbox(raw_bbox) for raw_bbox in (args.overlay_clip_bbox or [args.clip_bbox] * len(args.overlay_input))
        ],
        overlay_federal_states=args.overlay_federal_state or [args.federal_state] * len(args.overlay_input),
    )


def build_layers(config: ExportConfig) -> tuple[PolygonLayer, list[PolygonLayer]]:
    base_mesh = load_feature_collection(config.input_path)
    base_layer = export_polygon_layer(base_mesh, config.clip_bbox, config.updated_at, config.federal_state)

    overlay_layers = []
    for index, overlay_input in enumerate(config.overlay_inputs):
        overlay_mesh = load_feature_collection(overlay_input)
        overlay_layers.append(
            export_polygon_layer(
                overlay_mesh,
                config.overlay_clip_bboxes[index],
                config.updated_at,
                config.overlay_federal_states[index],
            )
        )
    return base_layer, overlay_layers


def run_export(config: ExportConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_layer, overlay_layers = build_layers(config)
    operators, areas = merge_polygon_layers(base_layer, overlay_layers)
    validate_area_geometries(areas)
    write_json(config.operators_output, operators)
    write_json(config.areas_output, areas)
    update_federal_states(config.federal_states_path)
    return operators, areas


def main() -> None:
    config = export_config_from_args(build_parser().parse_args())
    operators, areas = run_export(config)
    print(f"operators: {len(operators)}")
    print(f"area features: {len(areas['features'])}")
    print(f"updated: {config.operators_output}, {config.areas_output}, {config.federal_states_path}")


if __name__ == "__main__":
    main()
