"""Small standalone client for VNBdigital coordinate lookups."""

from __future__ import annotations

import asyncio
import email.utils
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

import httpx

logger = logging.getLogger(__name__)

DEFAULT_VOLTAGE_TYPES = ["Niederspannung", "Mittelspannung", "Hochspannung"]
DEFAULT_REQUEST_DELAY_SECONDS = 1.5
DEFAULT_BACKOFF_MULTIPLIER_SECONDS = 600.0
DEFAULT_MAX_BACKOFF_ATTEMPTS = 5
THROTTLE_STATUS_CODES = {403, 429, 500, 502, 503, 504}

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


class BackoffExhaustedError(RuntimeError):
    """Raised when VNBdigital keeps returning throttle/server responses."""


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
        request_delay: float = DEFAULT_REQUEST_DELAY_SECONDS,
        timeout: float = 20.0,
        backoff_multiplier: float = DEFAULT_BACKOFF_MULTIPLIER_SECONDS,
        max_backoff_attempts: int = DEFAULT_MAX_BACKOFF_ATTEMPTS,
    ) -> None:
        self.api_url = api_url
        self.request_delay = max(0.0, request_delay)
        self.timeout = timeout
        self.backoff_multiplier = max(0.0, backoff_multiplier)
        self.max_backoff_attempts = max(0, max_backoff_attempts)
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
            data = await self._post_with_backoff(payload, lat, lon)
        except BackoffExhaustedError:
            raise
        except httpx.TimeoutException:
            logger.warning("VNBdigital request timed out", extra={"lat": lat, "lon": lon})
            return CoordinateLookup(lat=lat, lon=lon, operators=[], regions=[], raw_geometry=None, error="timeout")
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.warning("VNBdigital HTTP error", extra={"lat": lat, "lon": lon, "status_code": status_code})
            return CoordinateLookup(
                lat=lat,
                lon=lon,
                operators=[],
                regions=[],
                raw_geometry=None,
                error=f"http_{status_code}",
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

    async def _post_with_backoff(self, payload: dict[str, Any], lat: float, lon: float) -> dict[str, Any]:
        for attempt in range(self.max_backoff_attempts + 1):
            await self._wait_for_rate_limit()
            client = await self._get_client()
            response = await client.post(self.api_url, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code not in THROTTLE_STATUS_CODES:
                    raise
                if attempt >= self.max_backoff_attempts:
                    raise BackoffExhaustedError(
                        f"VNBdigital returned HTTP {status_code} after {attempt + 1} attempts at lat={lat} lon={lon}"
                    ) from exc
                await self._sleep_for_backoff(exc.response, attempt, lat, lon)
                continue
            return response.json()

        raise RuntimeError("unreachable VNBdigital backoff state")

    async def _sleep_for_backoff(self, response: httpx.Response, attempt: int, lat: float, lon: float) -> None:
        status_code = response.status_code
        retry_after = parse_retry_after(response.headers.get("Retry-After"))
        computed_delay = self.request_delay * self.backoff_multiplier * (2**attempt)
        delay = max(computed_delay, retry_after or 0.0)
        logger.warning(
            "VNBdigital backoff before retry",
            extra={
                "lat": lat,
                "lon": lon,
                "status_code": status_code,
                "attempt": attempt + 1,
                "max_attempts": self.max_backoff_attempts,
                "delay_seconds": round(delay, 1),
            },
        )
        await asyncio.sleep(delay)

    async def _wait_for_rate_limit(self) -> None:
        if self.request_delay <= 0:
            self._last_request_time = time.time()
            return

        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            await asyncio.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()


def parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            parsed = email.utils.parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if parsed is None:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return max(0.0, (parsed - datetime.now(UTC)).total_seconds())
