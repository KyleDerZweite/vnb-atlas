from typing import Literal

Accuracy = Literal["mock", "municipality_approximation", "verified"]
CountryCode = Literal["DE"]
DataCoverage = Literal["none", "mock", "partial", "verified"]
DataStatus = Literal["mock", "partial", "verified", "not_available"]
OperatorType = Literal["VNB", "ÜNB", "UNKNOWN"]
SearchMatchedField = Literal["operator", "area", "place", "postalCode"]
SearchResultType = Literal["operator", "area", "place", "postalCode"]
VoltageLevel = Literal["Niederspannung", "Mittelspannung", "Hochspannung"]

VOLTAGE_LEVELS: tuple[VoltageLevel, ...] = ("Niederspannung", "Mittelspannung", "Hochspannung")
VOLTAGE_PRIORITY: dict[VoltageLevel, int] = {
    "Niederspannung": 0,
    "Mittelspannung": 1,
    "Hochspannung": 2,
}
