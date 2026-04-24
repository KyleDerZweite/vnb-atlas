"""Build a coarse NRW VNB mesh from VNBdigital coordinate lookups."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .simple_client import DEFAULT_VOLTAGE_TYPES, CoordinateLookup, SimpleVNBDigitalClient

DEFAULT_BBOX = "6.15,50.55,9.45,52.50"
DEFAULT_OUTPUT = "vnbdigital/output/nrw_vnb_mesh.geojson"
KM_PER_DEGREE_LAT = 111.32


def parse_bbox(raw_bbox: str) -> tuple[float, float, float, float]:
    try:
        west, south, east, north = [float(part.strip()) for part in raw_bbox.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("bbox must use numeric west,south,east,north values") from exc

    if west >= east or south >= north:
        raise argparse.ArgumentTypeError("bbox must satisfy west < east and south < north")
    if not (-180 <= west <= 180 and -180 <= east <= 180):
        raise argparse.ArgumentTypeError("bbox longitude values must be between -180 and 180")
    if not (-90 <= south <= 90 and -90 <= north <= 90):
        raise argparse.ArgumentTypeError("bbox latitude values must be between -90 and 90")
    return west, south, east, north


def generate_mesh_points(
    bbox: tuple[float, float, float, float],
    spacing_km: float,
) -> list[tuple[float, float]]:
    if spacing_km <= 0:
        raise ValueError("spacing_km must be greater than zero")

    west, south, east, north = bbox
    points: list[tuple[float, float]] = []
    lat_step = spacing_km / KM_PER_DEGREE_LAT
    lat = south

    while lat <= north + 1e-12:
        lon_step = spacing_km / (KM_PER_DEGREE_LAT * max(math.cos(math.radians(lat)), 0.000001))
        lon = west
        while lon <= east + 1e-12:
            points.append((round(lat, 6), round(lon, 6)))
            lon += lon_step
        lat += lat_step

    return points


def load_existing_features(output_path: Path) -> list[dict[str, Any]]:
    if not output_path.exists():
        return []

    with output_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{output_path} is not a GeoJSON FeatureCollection")
    return list(data.get("features") or [])


def coordinate_key(lat: float, lon: float) -> str:
    return f"{lat:.6f},{lon:.6f}"


def feature_key(feature: dict[str, Any]) -> str | None:
    properties = feature.get("properties") or {}
    lat = properties.get("lat")
    lon = properties.get("lon")
    if lat is None or lon is None:
        coordinates = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coordinates) < 2:
            return None
        lon, lat = coordinates[0], coordinates[1]
    return coordinate_key(float(lat), float(lon))


def lookup_to_feature(
    lookup: CoordinateLookup,
    query_voltage_types: list[str],
    only_nap: bool,
    queried_at: str,
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "lat": lookup.lat,
        "lon": lookup.lon,
        "queryVoltageTypes": query_voltage_types,
        "onlyNap": only_nap,
        "operatorCount": len(lookup.operators),
        "operators": [
            {
                "vnbId": operator.vnb_id,
                "name": operator.name,
                "voltageTypes": operator.voltage_types,
                "types": operator.types,
                "bbox": operator.bbox,
                "layerUrl": operator.layer_url,
            }
            for operator in lookup.operators
        ],
        "regions": lookup.regions,
        "source": "vnbdigital",
        "queriedAt": queried_at,
    }
    if lookup.error:
        properties["error"] = lookup.error
    if lookup.raw_geometry is not None:
        properties["rawGeometry"] = lookup.raw_geometry

    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lookup.lon, lookup.lat]},
        "properties": properties,
    }


def write_feature_collection(output_path: Path, features: list[dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"type": "FeatureCollection", "features": features}
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


async def build_mesh(args: argparse.Namespace) -> None:
    bbox = parse_bbox(args.bbox)
    points = generate_mesh_points(bbox, args.spacing_km)
    output_path = Path(args.output)
    features: list[dict[str, Any]] = []
    completed_keys: set[str] = set()

    if args.resume:
        features = load_existing_features(output_path)
        completed_keys = {key for feature in features if (key := feature_key(feature))}

    pending_points = [(lat, lon) for lat, lon in points if coordinate_key(lat, lon) not in completed_keys]
    if args.limit is not None:
        pending_points = pending_points[: args.limit]

    logging.info(
        "Starting NRW mesh build: total=%s pending=%s existing=%s output=%s",
        len(points),
        len(pending_points),
        len(features),
        output_path,
    )

    async with SimpleVNBDigitalClient(request_delay=args.request_delay, timeout=args.timeout) as client:
        for index, (lat, lon) in enumerate(pending_points, start=1):
            logging.info("Lookup %s/%s lat=%s lon=%s", index, len(pending_points), lat, lon)
            lookup = await client.lookup_coordinates(
                lat=lat,
                lon=lon,
                voltage_types=args.voltage_types,
                only_nap=args.only_nap,
            )
            queried_at = datetime.now(UTC).isoformat()
            features.append(lookup_to_feature(lookup, args.voltage_types, args.only_nap, queried_at))

    write_feature_collection(output_path, features)
    logging.info("Wrote %s features to %s", len(features), output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a coarse NRW VNB mesh via VNBdigital.")
    parser.add_argument("--bbox", default=DEFAULT_BBOX, help="west,south,east,north; default: %(default)s")
    parser.add_argument("--spacing-km", type=float, default=10.0, help="mesh spacing in kilometers")
    parser.add_argument("--voltage-types", nargs="+", default=DEFAULT_VOLTAGE_TYPES, help="VNBdigital voltageTypes")
    parser.add_argument("--only-nap", action="store_true", help="set VNBdigital filter.onlyNap=true")
    parser.add_argument("--request-delay", type=float, default=1.0, help="seconds between API requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="request timeout in seconds")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="output GeoJSON path")
    parser.add_argument("--resume", action="store_true", help="skip points already present in output")
    parser.add_argument("--limit", type=int, help="limit new lookups for smoke runs")
    parser.add_argument("--verbose", action="store_true", help="enable debug logging")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(build_mesh(args))


if __name__ == "__main__":
    main()
