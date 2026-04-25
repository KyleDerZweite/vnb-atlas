"""Analyze VNBdigital mesh GeoJSON output."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_INPUT = "vnbdigital/output/nrw_vnb_mesh.geojson"
DEFAULT_OUTPUT_DIR = "vnbdigital/output/analysis"
UNKNOWN_VOLTAGE = "UNKNOWN"


def load_feature_collection(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{path} is not a GeoJSON FeatureCollection")
    return data


def coordinate_key(feature: dict[str, Any]) -> str:
    properties = feature.get("properties") or {}
    lat = properties.get("lat")
    lon = properties.get("lon")
    if lat is None or lon is None:
        coordinates = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coordinates) < 2:
            return "unknown"
        lon, lat = coordinates[0], coordinates[1]
    return f"{float(lat):.6f},{float(lon):.6f}"


def operator_key(operator: dict[str, Any]) -> tuple[str, str]:
    return str(operator.get("vnbId") or ""), str(operator.get("name") or "")


def analyze(features: list[dict[str, Any]]) -> dict[str, Any]:
    operator_points: Counter[tuple[str, str]] = Counter()
    operator_voltage_points: Counter[tuple[str, str, str]] = Counter()
    voltage_points: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()
    query_voltage_types: Counter[str] = Counter()
    operator_point_keys: dict[tuple[str, str], set[str]] = defaultdict(set)
    operator_voltage_point_keys: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    operator_bboxes: dict[tuple[str, str], list[float]] = {}
    empty_features: list[dict[str, Any]] = []
    multi_operator_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []

    for feature in features:
        properties = feature.get("properties") or {}
        point_key = coordinate_key(feature)
        lat = properties.get("lat")
        lon = properties.get("lon")
        operators = properties.get("operators") or []

        for voltage_type in properties.get("queryVoltageTypes") or []:
            query_voltage_types[str(voltage_type)] += 1

        if properties.get("error"):
            error_counts[str(properties["error"])] += 1
        if not operators:
            empty_features.append(feature)
        if len(operators) > 1:
            multi_operator_features.append(feature)

        for operator in operators:
            vnb_id, name = operator_key(operator)
            op_key = (vnb_id, name)
            operator_point_keys[op_key].add(point_key)

            if isinstance(lat, int | float) and isinstance(lon, int | float):
                bbox = operator_bboxes.setdefault(op_key, [float(lon), float(lat), float(lon), float(lat)])
                bbox[0] = min(bbox[0], float(lon))
                bbox[1] = min(bbox[1], float(lat))
                bbox[2] = max(bbox[2], float(lon))
                bbox[3] = max(bbox[3], float(lat))

            voltage_types = operator.get("voltageTypes") or [UNKNOWN_VOLTAGE]
            for voltage_type in voltage_types:
                voltage = str(voltage_type)
                voltage_points[voltage] += 1
                operator_voltage_point_keys[(vnb_id, name, voltage)].add(point_key)
                normalized_rows.append(
                    {
                        "lat": lat,
                        "lon": lon,
                        "voltageType": voltage,
                        "vnbId": vnb_id,
                        "operatorName": name,
                    }
                )

    for op_key, point_keys in operator_point_keys.items():
        operator_points[op_key] = len(point_keys)
    for op_voltage_key, point_keys in operator_voltage_point_keys.items():
        operator_voltage_points[op_voltage_key] = len(point_keys)

    return {
        "featureCount": len(features),
        "emptyFeatures": empty_features,
        "multiOperatorFeatures": multi_operator_features,
        "errorCounts": dict(error_counts),
        "queryVoltageTypes": dict(query_voltage_types),
        "operatorPoints": operator_points,
        "operatorVoltagePoints": operator_voltage_points,
        "voltagePoints": voltage_points,
        "operatorBboxes": operator_bboxes,
        "normalizedRows": normalized_rows,
    }


def feature_collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": features}


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_analysis(analysis: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    operator_rows = []
    for (vnb_id, name), point_count in analysis["operatorPoints"].most_common():
        voltage_counts = {
            voltage: count
            for (voltage_vnb_id, voltage_name, voltage), count in analysis["operatorVoltagePoints"].items()
            if voltage_vnb_id == vnb_id and voltage_name == name
        }
        operator_rows.append(
            {
                "vnbId": vnb_id,
                "operatorName": name,
                "pointCount": point_count,
                "voltageTypes": ",".join(sorted(voltage_counts)),
                "niederspannungPoints": voltage_counts.get("Niederspannung", 0),
                "mittelspannungPoints": voltage_counts.get("Mittelspannung", 0),
                "hochspannungPoints": voltage_counts.get("Hochspannung", 0),
                "unknownVoltagePoints": voltage_counts.get(UNKNOWN_VOLTAGE, 0),
                "meshBbox": json.dumps(analysis["operatorBboxes"].get((vnb_id, name)), ensure_ascii=False),
            }
        )

    operator_voltage_rows = [
        {
            "vnbId": vnb_id,
            "operatorName": name,
            "voltageType": voltage,
            "pointCount": count,
        }
        for (vnb_id, name, voltage), count in analysis["operatorVoltagePoints"].most_common()
    ]

    voltage_rows = [
        {"voltageType": voltage, "operatorPointCount": count}
        for voltage, count in analysis["voltagePoints"].most_common()
    ]

    summary = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "featureCount": analysis["featureCount"],
        "emptyPointCount": len(analysis["emptyFeatures"]),
        "multiOperatorPointCount": len(analysis["multiOperatorFeatures"]),
        "operatorCount": len(analysis["operatorPoints"]),
        "errorCounts": analysis["errorCounts"],
        "queryVoltageTypes": analysis["queryVoltageTypes"],
        "voltagePointCounts": dict(analysis["voltagePoints"]),
        "topOperators": operator_rows[:25],
    }

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "empty_points.geojson", feature_collection(analysis["emptyFeatures"]))
    write_json(output_dir / "multi_operator_points.geojson", feature_collection(analysis["multiOperatorFeatures"]))
    write_csv(
        output_dir / "operators.csv",
        operator_rows,
        [
            "vnbId",
            "operatorName",
            "pointCount",
            "voltageTypes",
            "niederspannungPoints",
            "mittelspannungPoints",
            "hochspannungPoints",
            "unknownVoltagePoints",
            "meshBbox",
        ],
    )
    write_csv(
        output_dir / "operator_voltage.csv",
        operator_voltage_rows,
        ["vnbId", "operatorName", "voltageType", "pointCount"],
    )
    write_csv(output_dir / "voltage_summary.csv", voltage_rows, ["voltageType", "operatorPointCount"])
    write_csv(
        output_dir / "point_operator_voltage.csv",
        analysis["normalizedRows"],
        ["lat", "lon", "voltageType", "vnbId", "operatorName"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze VNBdigital mesh GeoJSON output.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="input mesh GeoJSON path")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="directory for analysis outputs")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    data = load_feature_collection(input_path)
    analysis = analyze(list(data.get("features") or []))
    write_analysis(analysis, output_dir)

    print(f"features: {analysis['featureCount']}")
    print(f"operators: {len(analysis['operatorPoints'])}")
    print(f"empty points: {len(analysis['emptyFeatures'])}")
    print(f"multi-operator points: {len(analysis['multiOperatorFeatures'])}")
    print(f"output: {output_dir}")


if __name__ == "__main__":
    main()
