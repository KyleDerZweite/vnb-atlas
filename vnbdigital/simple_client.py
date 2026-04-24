"""Small standalone client for VNBdigital coordinate lookups."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, ClassVar

import httpx

logger = logging.getLogger(__name__)

DEFAULT_VOLTAGE_TYPES = ["Niederspannung", "Mittelspannung", "Hochspannung"]

COORDINATES_QUERY = """
query (
  $coordinates: String
  $filter: vnb_FilterInput
  $withCoordinates: Boolean = false
) {
  vnb_coordinates(coordinates: $coordinates) @include(if: $withCoordinates) {
    geometry
    regions(filter: $filter) {
      _id
      name
      bbox
      layerUrl
    }
    vnbs(filter: $filter) {
      _id
      name
      bbox
      layerUrl
      types
      voltageTypes
    }
  }
}
"""


@dataclass
class GridOperator:
    """VNBdigital operator returned for one coordinate."""

    vnb_id: str
    name: str
    voltage_types: list[str]
    types: list[str]
    bbox: list[float] | None
    layer_url: str | None


@dataclass
class CoordinateLookup:
    """Result of one coordinate lookup."""

    lat: float
    lon: float
    operators: list[GridOperator]
    regions: list[dict[str, Any]]
    raw_geometry: dict[str, Any] | None
    error: str | None = None


class SimpleVNBDigitalClient:
    """Minimal async client for the public VNBdigital GraphQL endpoint."""

    API_URL: ClassVar[str] = "https://www.vnbdigital.de/gateway/graphql"
    HEADERS: ClassVar[dict[str, str]] = {
        "User-Agent": "Mozilla/5.0 (compatible; vnb-atlas-mesh/0.1)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.vnbdigital.de",
        "Referer": "https://www.vnbdigital.de/",
    }

    def __init__(
        self,
        api_url: str = API_URL,
        request_delay: float = 1.0,
        timeout: float = 20.0,
    ) -> None:
        self.api_url = api_url
        self.request_delay = max(0.0, request_delay)
        self.timeout = timeout
        self._last_request_time = 0.0
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> SimpleVNBDigitalClient:
        await self._get_client()
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def lookup_coordinates(
        self,
        lat: float,
        lon: float,
        voltage_types: list[str] | None = None,
        only_nap: bool = False,
    ) -> CoordinateLookup:
        """Look up VNBdigital operators for one WGS84 coordinate."""
        await self._wait_for_rate_limit()

        selected_voltage_types = voltage_types or DEFAULT_VOLTAGE_TYPES
        coordinates = f"{lat},{lon}"
        payload = {
            "query": COORDINATES_QUERY,
            "variables": {
                "coordinates": coordinates,
                "filter": {
                    "onlyNap": only_nap,
                    "voltageTypes": selected_voltage_types,
                    "withRegions": True,
                },
                "withCoordinates": True,
            },
        }

        try:
            client = await self._get_client()
            response = await client.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            logger.warning("VNBdigital request timed out", extra={"lat": lat, "lon": lon})
            return CoordinateLookup(lat=lat, lon=lon, operators=[], regions=[], raw_geometry=None, error="timeout")
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "VNBdigital HTTP error",
                extra={"lat": lat, "lon": lon, "status_code": exc.response.status_code},
            )
            return CoordinateLookup(
                lat=lat,
                lon=lon,
                operators=[],
                regions=[],
                raw_geometry=None,
                error=f"http_{exc.response.status_code}",
            )
        except Exception as exc:
            logger.warning("VNBdigital request failed", extra={"lat": lat, "lon": lon, "error": str(exc)})
            return CoordinateLookup(lat=lat, lon=lon, operators=[], regions=[], raw_geometry=None, error=str(exc))

        if "errors" in data:
            message = data["errors"][0].get("message", "graphql_error")
            logger.warning("VNBdigital GraphQL error", extra={"lat": lat, "lon": lon, "error": message})
            return CoordinateLookup(lat=lat, lon=lon, operators=[], regions=[], raw_geometry=None, error=message)

        coordinate_data = data.get("data", {}).get("vnb_coordinates") or {}
        operators = [
            GridOperator(
                vnb_id=str(vnb.get("_id", "")),
                name=vnb.get("name", ""),
                voltage_types=list(vnb.get("voltageTypes") or []),
                types=list(vnb.get("types") or []),
                bbox=vnb.get("bbox"),
                layer_url=vnb.get("layerUrl"),
            )
            for vnb in coordinate_data.get("vnbs", [])
        ]

        return CoordinateLookup(
            lat=lat,
            lon=lon,
            operators=operators,
            regions=list(coordinate_data.get("regions") or []),
            raw_geometry=coordinate_data.get("geometry"),
        )

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, headers=self.HEADERS)
        return self._client

    async def _wait_for_rate_limit(self) -> None:
        if self.request_delay <= 0:
            self._last_request_time = time.time()
            return

        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            await asyncio.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

