import json
from functools import lru_cache
from pathlib import Path

from app.models import FederalStateRecord
from app.schemas import CountryCoverage, FederalState, FederalStateCoverage

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@lru_cache
def load_federal_states() -> list[FederalStateRecord]:
    with (DATA_DIR / "federal-states.json").open(encoding="utf-8") as file:
        return json.load(file)


def get_federal_states() -> list[FederalState]:
    return [FederalState.model_validate(state) for state in load_federal_states()]


def get_coverage() -> CountryCoverage:
    return CountryCoverage(
        country="DE",
        federalStates={
            state["id"]: FederalStateCoverage(
                id=state["id"],
                name=state["name"],
                hasAreas=state["hasAreaData"],
                status=state["dataStatus"],
            )
            for state in load_federal_states()
        },
    )
