from typing import Any, Literal

from pydantic import BaseModel, Field

from app.domain import Accuracy, CountryCode, DataCoverage, DataStatus, OperatorType, SearchMatchedField, SearchResultType


class Operator(BaseModel):
    id: str
    name: str
    type: OperatorType
    website: str
    parentCompany: str | None = None
    description: str
    voltageLevels: list[str]
    country: CountryCode
    federalStates: list[str]
    dataCoverage: DataCoverage
    mockNotice: str


class AreaProperties(BaseModel):
    id: str
    name: str
    operatorId: str
    operatorName: str
    country: CountryCode
    federalState: str
    accuracy: Accuracy
    source: str
    updatedAt: str
    mockNotice: str
    places: list[str]
    postalCodes: list[str]
    voltageLevels: list[str] = Field(default_factory=list)
    voltageLevel: str | None = None
    vnbdigitalId: str | None = None
    samplePointCount: int | None = None


class AreaFeature(BaseModel):
    type: Literal["Feature"]
    properties: AreaProperties
    geometry: dict[str, Any]
    bbox: list[float] | None = None


class SearchResult(BaseModel):
    type: SearchResultType
    label: str
    operatorId: str
    operatorName: str
    areaId: str | None = None
    areaName: str | None = None
    accuracy: Accuracy | None = None
    matchedField: SearchMatchedField


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


class LookupMatch(BaseModel):
    area: AreaFeature
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
    dataStatus: DataStatus


class FederalStateCoverage(BaseModel):
    id: str
    name: str
    hasAreas: bool
    status: DataStatus


class CountryCoverage(BaseModel):
    country: CountryCode
    federalStates: dict[str, FederalStateCoverage]
