from typing import Any

from fastapi import HTTPException

BBox = tuple[float, float, float, float]
Point = tuple[float, float]


def parse_bbox(raw_bbox: str) -> BBox:
    try:
        values = tuple(float(part.strip()) for part in raw_bbox.split(","))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="bbox must contain numbers") from exc

    if len(values) != 4:
        raise HTTPException(status_code=400, detail="bbox must be minLon,minLat,maxLon,maxLat")

    min_lon, min_lat, max_lon, max_lat = values
    if min_lon >= max_lon or min_lat >= max_lat:
        raise HTTPException(status_code=400, detail="bbox min values must be smaller than max values")
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise HTTPException(status_code=400, detail="bbox longitude must be between -180 and 180")
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise HTTPException(status_code=400, detail="bbox latitude must be between -90 and 90")
    return min_lon, min_lat, max_lon, max_lat


def geometry_bbox(geometry: dict[str, Any]) -> BBox:
    points = list(_iter_points(geometry))
    if not points:
        raise ValueError("Geometry has no coordinates")

    lons = [point[0] for point in points]
    lats = [point[1] for point in points]
    return min(lons), min(lats), max(lons), max(lats)


def bbox_intersects(left: BBox, right: BBox) -> bool:
    left_min_lon, left_min_lat, left_max_lon, left_max_lat = left
    right_min_lon, right_min_lat, right_max_lon, right_max_lat = right
    return not (
        left_max_lon < right_min_lon
        or right_max_lon < left_min_lon
        or left_max_lat < right_min_lat
        or right_max_lat < left_min_lat
    )


def point_in_geometry(lon: float, lat: float, geometry: dict[str, Any]) -> bool:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    if geometry_type == "Polygon":
        return point_in_polygon((lon, lat), coordinates)
    if geometry_type == "MultiPolygon":
        return any(point_in_polygon((lon, lat), polygon) for polygon in coordinates)
    return False


def point_in_polygon(point: Point, rings: list[list[list[float]]]) -> bool:
    if not rings:
        return False

    outer = [(coord[0], coord[1]) for coord in rings[0]]
    if not _point_in_ring(point, outer):
        return False

    holes = [[(coord[0], coord[1]) for coord in ring] for ring in rings[1:]]
    return not any(_point_in_ring(point, hole) for hole in holes)


def _point_in_ring(point: Point, ring: list[Point]) -> bool:
    x, y = point
    inside = False
    if len(ring) < 4:
        return False

    previous_x, previous_y = ring[-1]
    for current_x, current_y in ring:
        if _point_on_segment(point, (previous_x, previous_y), (current_x, current_y)):
            return True

        crosses = (current_y > y) != (previous_y > y)
        if crosses:
            intersection_x = (previous_x - current_x) * (y - current_y) / (previous_y - current_y) + current_x
            if x < intersection_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def _point_on_segment(point: Point, start: Point, end: Point) -> bool:
    x, y = point
    x1, y1 = start
    x2, y2 = end
    cross = (y - y1) * (x2 - x1) - (x - x1) * (y2 - y1)
    if abs(cross) > 1e-10:
        return False
    return min(x1, x2) - 1e-10 <= x <= max(x1, x2) + 1e-10 and min(y1, y2) - 1e-10 <= y <= max(y1, y2) + 1e-10


def _iter_points(geometry: dict[str, Any]):
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    if geometry_type == "Polygon":
        for ring in coordinates:
            for lon, lat in ring:
                yield lon, lat
    elif geometry_type == "MultiPolygon":
        for polygon in coordinates:
            for ring in polygon:
                for lon, lat in ring:
                    yield lon, lat
