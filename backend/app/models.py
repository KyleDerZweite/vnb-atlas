from typing import Literal, TypedDict


OperatorType = Literal["VNB", "ÜNB", "UNKNOWN"]
Accuracy = Literal["mock", "municipality_approximation", "verified"]
DataCoverage = Literal["none", "mock", "partial", "verified"]
DataStatus = Literal["mock", "partial", "verified", "not_available"]


class OperatorRecord(TypedDict):
    id: str
    name: str
    type: OperatorType
    website: str
    parentCompany: str | None
    description: str
    voltageLevels: list[str]
    country: Literal["DE"]
    federalStates: list[str]
    dataCoverage: DataCoverage
    mockNotice: str


class AreaPropertiesRecord(TypedDict):
    id: str
    name: str
    operatorId: str
    country: Literal["DE"]
    federalState: str
    accuracy: Accuracy
    source: str
    updatedAt: str
    mockNotice: str
    places: list[str]
    postalCodes: list[str]


class FederalStateRecord(TypedDict):
    id: str
    name: str
    hasAreaData: bool
    dataStatus: DataStatus
