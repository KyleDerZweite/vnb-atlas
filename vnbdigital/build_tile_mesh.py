"""Build VNBdigital coordinate meshes for rough bboxes or tiled regions."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .bbox_presets import iter_display_presets, resolve_bbox_preset
from .simple_client import DEFAULT_VOLTAGE_TYPES, CoordinateLookup, SimpleVNBDigitalClient

DEFAULT_PRESET = "nrw"
DEFAULT_OUTPUT = "vnbdigital/output/{preset}_{spacing_slug}km.geojson"
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


def generate_tiles(
    bbox: tuple[float, float, float, float],
    tile_size_km: float,
) -> list[tuple[float, float, float, float]]:
    if tile_size_km <= 0:
        raise ValueError("tile_size_km must be greater than zero")

    west, south, east, north = bbox
    lat_step = tile_size_km / KM_PER_DEGREE_LAT
    tiles: list[tuple[float, float, float, float]] = []
    tile_south = south

    while tile_south < north - 1e-12:
        tile_north = min(north, tile_south + lat_step)
        center_lat = (tile_south + tile_north) / 2
        lon_step = tile_size_km / (KM_PER_DEGREE_LAT * max(math.cos(math.radians(center_lat)), 0.000001))
        tile_west = west
        while tile_west < east - 1e-12:
            tile_east = min(east, tile_west + lon_step)
            tiles.append((round(tile_west, 6), round(tile_south, 6), round(tile_east, 6), round(tile_north, 6)))
            tile_west += lon_step
        tile_south += lat_step

    return tiles


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
    tile_id: str | None = None,
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
    if tile_id:
        properties["tileId"] = tile_id
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


def spacing_slug(spacing_km: float) -> str:
    return f"{spacing_km:g}".replace(".", "p")


def default_output_path(preset: str | None, spacing_km: float) -> str:
    preset_name = preset or "custom"
    return DEFAULT_OUTPUT.format(preset=preset_name, spacing_slug=spacing_slug(spacing_km))


def resolve_bbox(args: argparse.Namespace) -> tuple[str | None, tuple[float, float, float, float]]:
    if args.bbox:
        return None, parse_bbox(args.bbox)
    try:
        return args.preset, parse_bbox(resolve_bbox_preset(args.preset))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def load_completed_keys(output_path: Path, resume: bool) -> tuple[list[dict[str, Any]], set[str]]:
    if not resume:
        return [], set()
    features = load_existing_features(output_path)
    return features, {key for feature in features if (key := feature_key(feature))}


def select_pending_points(
    points: list[tuple[float, float]],
    completed_keys: set[str],
    limit: int | None,
) -> list[tuple[float, float]]:
    pending_points = [(lat, lon) for lat, lon in points if coordinate_key(lat, lon) not in completed_keys]
    return pending_points[:limit] if limit is not None else pending_points


async def collect_lookup_features(
    pending_points: list[tuple[float, float]],
    args: argparse.Namespace,
    tile_id: str | None = None,
) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
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
            features.append(lookup_to_feature(lookup, args.voltage_types, args.only_nap, queried_at, tile_id=tile_id))
    return features


async def query_points(
    points: list[tuple[float, float]],
    output_path: Path,
    args: argparse.Namespace,
    tile_id: str | None = None,
) -> None:
    features, completed_keys = load_completed_keys(output_path, args.resume)
    pending_points = select_pending_points(points, completed_keys, args.limit)

    logging.info(
        "Starting mesh build: total=%s pending=%s existing=%s output=%s",
        len(points),
        len(pending_points),
        len(features),
        output_path,
    )

    features.extend(await collect_lookup_features(pending_points, args, tile_id=tile_id))

    write_feature_collection(output_path, features)
    logging.info("Wrote %s features to %s", len(features), output_path)


async def build_single_mesh(args: argparse.Namespace) -> None:
    preset, bbox = resolve_bbox(args)
    output = args.output or default_output_path(preset, args.spacing_km)
    points = generate_mesh_points(bbox, args.spacing_km)
    await query_points(points, Path(output), args)


async def build_tiled_mesh(args: argparse.Namespace) -> None:
    preset, bbox = resolve_bbox(args)
    tiles = generate_tiles(bbox, args.tile_size_km)
    output_dir = Path(args.output_dir or f"vnbdigital/output/tiles/{preset or 'custom'}_{spacing_slug(args.spacing_km)}km")
    logging.info("Building %s tiles into %s", len(tiles), output_dir)

    for index, tile_bbox in enumerate(tiles, start=1):
        tile_id = f"tile-{index:04d}"
        output_path = output_dir / f"{tile_id}.geojson"
        points = generate_mesh_points(tile_bbox, args.spacing_km)
        logging.info("Tile %s/%s bbox=%s points=%s", index, len(tiles), tile_bbox, len(points))
        await query_points(points, output_path, args, tile_id=tile_id)
        if args.limit is not None:
            break


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build VNBdigital coordinate meshes by bbox, preset or tiles.")
    parser.add_argument("--preset", default=DEFAULT_PRESET, help="bbox preset name; use --list-presets to inspect")
    parser.add_argument("--bbox", help="west,south,east,north; overrides --preset")
    parser.add_argument("--list-presets", action="store_true", help="print available bbox presets and exit")
    parser.add_argument("--spacing-km", type=float, default=10.0, help="mesh spacing in kilometers")
    parser.add_argument("--tile-size-km", type=float, help="if set, split bbox into tile outputs of roughly this size")
    parser.add_argument("--voltage-types", nargs="+", default=DEFAULT_VOLTAGE_TYPES, help="VNBdigital voltageTypes")
    parser.add_argument("--only-nap", action="store_true", help="set VNBdigital filter.onlyNap=true")
    parser.add_argument("--request-delay", type=float, default=1.0, help="seconds between API requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="request timeout in seconds")
    parser.add_argument("--output", help="single output GeoJSON path")
    parser.add_argument("--output-dir", help="tile output directory when --tile-size-km is set")
    parser.add_argument("--resume", action="store_true", help="skip points already present in output")
    parser.add_argument("--limit", type=int, help="limit new lookups; in tiled mode only runs first limited tile")
    parser.add_argument("--verbose", action="store_true", help="enable debug logging")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.list_presets:
        for preset in iter_display_presets():
            print(f"{preset.name} ({preset.code}): {preset.bbox}")
        return

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.tile_size_km:
        asyncio.run(build_tiled_mesh(args))
    else:
        asyncio.run(build_single_mesh(args))


if __name__ == "__main__":
    main()
