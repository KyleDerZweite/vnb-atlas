from typing import TypedDict

from app.domain import Accuracy, CountryCode, DataCoverage, DataStatus, OperatorType


class OperatorRecord(TypedDict):
    id: str
    name: str
    type: OperatorType
    website: str
    parentCompany: str | None
    description: str
    voltageLevels: list[str]
    country: CountryCode
    federalStates: list[str]
    dataCoverage: DataCoverage
    mockNotice: str


class AreaPropertiesRecord(TypedDict):
    id: str
    name: str
    operatorId: str
    country: CountryCode
    federalState: str
    accuracy: Accuracy
    source: str
    updatedAt: str
    mockNotice: str
    places: list[str]
    postalCodes: list[str]
    voltageLevels: list[str]


class FederalStateRecord(TypedDict):
    id: str
    name: str
    hasAreaData: bool
    dataStatus: DataStatus
