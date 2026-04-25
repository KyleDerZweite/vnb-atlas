"""Reusable rough bbox presets for VNBdigital mesh builds.

Values use the CLI format west,south,east,north. They are intentionally rough
working boxes, not official administrative boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BBoxPreset:
    name: str
    code: str
    bbox: str
    aliases: tuple[str, ...] = ()


CANONICAL_PRESETS: tuple[BBoxPreset, ...] = (
    BBoxPreset("Deutschland", "DE", "5.80,47.20,15.10,55.10", ("de", "germany")),
    BBoxPreset("Baden-Wuerttemberg", "BW", "7.45,47.50,10.50,49.85", ("bw", "baden-wuerttemberg")),
    BBoxPreset("Bayern", "BY", "8.95,47.25,13.95,50.60", ("by", "bayern")),
    BBoxPreset("Berlin", "BE", "13.05,52.30,13.80,52.70", ("be", "berlin")),
    BBoxPreset("Brandenburg", "BB", "11.25,51.35,14.80,53.60", ("bb", "brandenburg")),
    BBoxPreset("Bremen", "HB", "8.45,52.95,9.05,53.65", ("hb", "bremen")),
    BBoxPreset("Hamburg", "HH", "9.70,53.35,10.35,53.75", ("hh", "hamburg")),
    BBoxPreset("Hessen", "HE", "7.75,49.35,10.25,51.75", ("he", "hessen")),
    BBoxPreset("Mecklenburg-Vorpommern", "MV", "10.55,53.05,14.45,54.70", ("mv", "mecklenburg-vorpommern")),
    BBoxPreset("Niedersachsen", "NI", "6.60,51.25,11.70,53.95", ("ni", "niedersachsen")),
    BBoxPreset("Nordrhein-Westfalen", "NW", "6.15,50.55,9.45,52.50", ("nw", "nrw", "nordrhein-westfalen")),
    BBoxPreset("Rheinland-Pfalz", "RP", "6.05,48.95,8.60,50.95", ("rp", "rheinland-pfalz")),
    BBoxPreset("Saarland", "SL", "6.30,49.10,7.40,49.65", ("sl", "saarland")),
    BBoxPreset("Sachsen", "SN", "11.80,50.15,15.10,51.70", ("sn", "sachsen")),
    BBoxPreset("Sachsen-Anhalt", "ST", "10.55,50.90,13.25,53.10", ("st", "sachsen-anhalt")),
    BBoxPreset("Schleswig-Holstein", "SH", "8.25,53.35,11.35,55.10", ("sh", "schleswig-holstein")),
    BBoxPreset("Thueringen", "TH", "9.85,50.15,12.70,51.70", ("th", "thueringen")),
)


BBOX_PRESETS: dict[str, str] = {
    alias: preset.bbox
    for preset in CANONICAL_PRESETS
    for alias in (preset.code.casefold(), *preset.aliases)
}


def resolve_bbox_preset(name: str) -> str:
    try:
        return BBOX_PRESETS[name.casefold()]
    except KeyError as exc:
        available = ", ".join(sorted(BBOX_PRESETS))
        raise ValueError(f"Unknown bbox preset {name!r}. Available presets: {available}") from exc


def iter_display_presets() -> tuple[BBoxPreset, ...]:
    return CANONICAL_PRESETS
