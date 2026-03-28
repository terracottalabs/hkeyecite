"""
Hong Kong Law Reports Definitions

This module contains definitions for all Hong Kong law reports
used in reported citations.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Reporter:
    """Represents a Hong Kong law report series."""
    code: str  # Abbreviation (e.g., "HKLRD")
    name: str  # Full name
    name_zh: Optional[str] = None  # Chinese name
    year_format: str = "round"  # "round" for (YYYY), "square" for [YYYY]
    has_volume: bool = True  # Whether citations include volume number
    start_year: Optional[int] = None  # First year of publication
    variations: Tuple[str, ...] = ()  # Alternative abbreviations


# Hong Kong Law Reports & Digest
HKLRD = Reporter(
    code="HKLRD",
    name="Hong Kong Law Reports & Digest",
    name_zh="香港法律報告及摘錄",
    year_format="round",
    has_volume=True,
    start_year=1997,
    variations=("HKLRd", "H.K.L.R.D."),
)

# Hong Kong Cases
HKC = Reporter(
    code="HKC",
    name="Hong Kong Cases",
    name_zh="香港案例",
    year_format="square",
    has_volume=True,
    start_year=1842,
    variations=("H.K.C.",),
)

# Hong Kong Court of Final Appeal Reports
HKCFAR = Reporter(
    code="HKCFAR",
    name="Hong Kong Court of Final Appeal Reports",
    name_zh="終審法院案例彙編",
    year_format="round",
    has_volume=True,
    start_year=1997,
    variations=("H.K.C.F.A.R.",),
)

# Hong Kong Public Law Reports
HKPLR = Reporter(
    code="HKPLR",
    name="Hong Kong Public Law Reports",
    year_format="square",
    has_volume=True,
    start_year=1991,
)

# Hong Kong Law Reports (historical, pre-HKLRD)
HKLR = Reporter(
    code="HKLR",
    name="Hong Kong Law Reports",
    year_format="square",
    has_volume=False,
    start_year=1905,
    variations=("H.K.L.R.",),
)

# Hong Kong Criminal Law Reports
HKCLR = Reporter(
    code="HKCLR",
    name="Hong Kong Criminal Law Reports",
    year_format="square",
    has_volume=False,
)

# Hong Kong Chinese Law Reports & Translations
HKCLRT = Reporter(
    code="HKCLRT",
    name="Hong Kong Chinese Law Reports & Translations",
    year_format="square",
    has_volume=False,
    start_year=1995,
)

# All reporters dictionary for lookup
HK_REPORTERS = {
    "HKLRD": HKLRD,
    "HKC": HKC,
    "HKCFAR": HKCFAR,
    "HKPLR": HKPLR,
    "HKLR": HKLR,
    "HKCLR": HKCLR,
    "HKCLRT": HKCLRT,
}

# Build lookup including variations
REPORTER_LOOKUP = {}
for reporter in HK_REPORTERS.values():
    REPORTER_LOOKUP[reporter.code] = reporter
    for variation in reporter.variations:
        REPORTER_LOOKUP[variation] = reporter


def get_reporter(code: str) -> Optional[Reporter]:
    """Get reporter by code or variation."""
    return REPORTER_LOOKUP.get(code)


# All reporter codes (for regex building)
ALL_REPORTER_CODES = tuple(REPORTER_LOOKUP.keys())

# Reporters that use round brackets for year: (YYYY)
ROUND_BRACKET_REPORTERS = tuple(
    r.code for r in HK_REPORTERS.values() if r.year_format == "round"
)

# Reporters that use square brackets for year: [YYYY]
SQUARE_BRACKET_REPORTERS = tuple(
    r.code for r in HK_REPORTERS.values() if r.year_format == "square"
)

# Reporters without volume numbers: [YYYY] REPORTER PAGE
NO_VOLUME_REPORTERS = tuple(
    r.code for r in HK_REPORTERS.values() if not r.has_volume
)
