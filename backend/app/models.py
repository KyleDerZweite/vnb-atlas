from typing import Literal, TypedDict


OperatorType = Literal["VNB", "ÜNB", "UNKNOWN"]
Accuracy = Literal["mock", "municipality_approximation", "verified"]


class OperatorRecord(TypedDict):
    id: str
    name: str
    type: OperatorType
    website: str
    parentCompany: str | None
    description: str
    voltageLevels: list[str]
    mockNotice: str


class AreaPropertiesRecord(TypedDict):
    id: str
    name: str
    operatorId: str
    accuracy: Accuracy
    source: str
    updatedAt: str
    mockNotice: str
    places: list[str]
    postalCodes: list[str]
