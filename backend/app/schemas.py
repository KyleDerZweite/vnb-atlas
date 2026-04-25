from typing import Any, Literal

from pydantic import BaseModel, Field


class Operator(BaseModel):
    id: str
    name: str
    type: Literal["VNB", "ÜNB", "UNKNOWN"]
    website: str
    parentCompany: str | None = None
    description: str
    voltageLevels: list[str]
    country: Literal["DE"]
    federalStates: list[str]
    dataCoverage: Literal["none", "mock", "partial", "verified"]
    mockNotice: str


class AreaProperties(BaseModel):
    id: str
    name: str
    operatorId: str
    operatorName: str
    country: Literal["DE"]
    federalState: str
    accuracy: Literal["mock", "municipality_approximation", "verified"]
    source: str
    updatedAt: str
    mockNotice: str
    places: list[str]
    postalCodes: list[str]
    voltageLevels: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    type: Literal["operator", "area", "place", "postalCode"]
    label: str
    operatorId: str
    operatorName: str
    areaId: str | None = None
    areaName: str | None = None
    accuracy: Literal["mock", "municipality_approximation", "verified"] | None = None
    matchedField: str


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


class LookupMatch(BaseModel):
    area: dict[str, Any]
    operator: Operator


class LookupResponse(BaseModel):
    match: LookupMatch | None = None
    matches: list[LookupMatch] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str = Field(examples=["vnb-atlas"])


class FederalState(BaseModel):
    id: str
    name: str
    hasAreaData: bool
    dataStatus: Literal["mock", "partial", "verified", "not_available"]


class FederalStateCoverage(BaseModel):
    id: str
    name: str
    hasAreas: bool
    status: Literal["mock", "partial", "verified", "not_available"]


class CountryCoverage(BaseModel):
    country: Literal["DE"]
    federalStates: dict[str, FederalStateCoverage]
