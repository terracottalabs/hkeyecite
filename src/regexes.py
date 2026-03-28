"""
Hong Kong Citation Regex Patterns

This module contains all regex patterns for extracting Hong Kong legal citations.
"""

import re
from typing import Pattern

from hkeyecite.courts import NEUTRAL_CITATION_COURTS, ALL_CASE_PREFIXES
from hkeyecite.reporters import (
    ALL_REPORTER_CODES,
    ROUND_BRACKET_REPORTERS,
    SQUARE_BRACKET_REPORTERS,
    NO_VOLUME_REPORTERS,
)


# =============================================================================
# Neutral Citations: [YYYY] HKCOURT NUM
# Examples: [2024] HKCFA 1, [2023] HKCA 123, [2021] HKCFI 1194
# =============================================================================

# Build court alternation pattern
_COURTS_PATTERN = "|".join(sorted(NEUTRAL_CITATION_COURTS, key=len, reverse=True))

# Full neutral citation pattern with named groups
NEUTRAL_CITATION_REGEX = re.compile(
    rf"""
    \[(?P<year>\d{{4}})\]       # Year in square brackets: [2024]
    \s*                         # Optional whitespace
    (?P<court>{_COURTS_PATTERN})  # Court code: HKCFA, HKCA, etc.
    \s+                         # Whitespace
    (?P<number>\d+)             # Case number: 1, 123, etc.
    """,
    re.VERBOSE,
)


# =============================================================================
# Reported Citations: (YYYY) VOL REPORTER PAGE or [YYYY] VOL REPORTER PAGE
# Examples: (2020) 23 HKCFAR 248, [2016] 2 HKC 393
# =============================================================================

# Build reporter alternation pattern (escape dots in variations)
_REPORTERS_PATTERN = "|".join(
    re.escape(r) for r in sorted(ALL_REPORTER_CODES, key=len, reverse=True)
)

# Round bracket reporters: (YYYY) VOL REPORTER PAGE
REPORTED_ROUND_REGEX = re.compile(
    rf"""
    \((?P<year>\d{{4}})(?:-\d{{2,4}})?\)  # Year in round brackets: (2020) or (1997-98)
    \s+                         # Whitespace
    (?P<volume>\d+)             # Volume number: 23
    \s*                         # Optional whitespace (may be absent in OCR'd text)
    (?P<reporter>{_REPORTERS_PATTERN})  # Reporter: HKCFAR, HKLRD
    \s+                         # Whitespace
    (?P<page>\d+)               # Page number: 248
    """,
    re.VERBOSE,
)

# Square bracket reporters: [YYYY] VOL REPORTER PAGE
REPORTED_SQUARE_REGEX = re.compile(
    rf"""
    \[(?P<year>\d{{4}})\]       # Year in square brackets: [2016]
    \s*                         # Optional whitespace (may be absent in OCR'd text)
    (?P<volume>\d+)             # Volume number: 2
    \s*                         # Optional whitespace (may be absent in OCR'd text)
    (?P<reporter>{_REPORTERS_PATTERN})  # Reporter: HKC
    \s+                         # Whitespace
    (?P<page>\d+)               # Page number: 393
    """,
    re.VERBOSE,
)

# Square bracket reporters without volume: [YYYY] REPORTER PAGE (historical HKLR format)
_NO_VOL_PATTERN = "|".join(sorted(NO_VOLUME_REPORTERS, key=len, reverse=True))
REPORTED_SQUARE_NO_VOL_REGEX = re.compile(
    rf"""
    \[(?P<year>\d{{4}})\]       # Year in square brackets: [1986]
    \s+                         # Whitespace
    (?P<reporter>{_NO_VOL_PATTERN})  # Reporter without volume
    \s+                         # Whitespace
    (?P<page>\d+)               # Page number: 1049
    """,
    re.VERBOSE,
)


# =============================================================================
# Action Numbers: PREFIX NUM/YYYY
# Examples: FACV 1/2018, CACC 106/2022, HCAL 1756/2020
# =============================================================================

# Build case prefix pattern
_CASE_PREFIXES_PATTERN = "|".join(sorted(ALL_CASE_PREFIXES, key=len, reverse=True))

ACTION_NUMBER_REGEX = re.compile(
    rf"""
    (?P<prefix>{_CASE_PREFIXES_PATTERN})  # Case prefix: FACV, HCAL, etc.
    \s*                                    # Optional whitespace
    (?P<number>\d+)                        # Case number: 1, 1756
    \s*/\s*                                # Slash with optional spaces
    (?P<year>\d{{4}})                      # Year: 2018, 2020
    """,
    re.VERBOSE,
)

# Alternative format: PREFIX NUM of YYYY (less common)
ACTION_NUMBER_ALT_REGEX = re.compile(
    rf"""
    (?P<prefix>{_CASE_PREFIXES_PATTERN})  # Case prefix
    \s+                                    # Whitespace
    (?:No\.?\s*)?                          # Optional "No." or "No"
    (?P<number>\d+)                        # Case number
    \s+of\s+                               # "of"
    (?P<year>\d{{4}})                      # Year
    """,
    re.VERBOSE | re.IGNORECASE,
)


# =============================================================================
# Pin Cites: at [23], at §§23-36, at para 10
# =============================================================================

PIN_CITE_REGEX = re.compile(
    r"""
    at\s+                                  # "at "
    (?:
        \[(?P<para_bracket>\d+(?:[–-]\d+)?)\]    # [23] or [23-36]
        |
        §§?(?P<para_section>\d+(?:[–-]\d+)?)    # §23 or §§23-36
        |
        (?:para(?:graph)?s?\.?\s*)(?P<para_word>\d+(?:[–-]\d+)?)  # para 10, paras 10-15
        |
        (?:p(?:p)?\.?\s*)(?P<page_ref>\d+(?:[–-]\d+)?)  # p. 10, pp. 10-15
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)


# =============================================================================
# Case Names: Party A v Party B, Re Something
# =============================================================================

# Basic "v" or "v." pattern for case names
VERSUS_PATTERN = re.compile(
    r"\bv\.?\s+",
    re.IGNORECASE,
)

# "Re" or "In re" pattern
RE_PATTERN = re.compile(
    r"\b(?:In\s+)?[Rr]e\s+",
)

# Pattern to extract case name before a citation
# Looks for "Party v Party" or "Re Name" patterns before citations
CASE_NAME_BEFORE_CITATION = re.compile(
    r"""
    (?P<case_name>
        # Pattern 1: "Party A v Party B" or "Party A v. Party B"
        # Plaintiff can be single letter (e.g., "H" for anonymized parties)
        (?:[A-Z][A-Za-z''\-&]*(?:\s+[A-Z][A-Za-z''\-&]+)*)   # Plaintiff (cap words, first can be single letter)
        \s+v\.?\s+                                            # "v" or "v."
        (?:[A-Z][A-Za-z''\-&]+(?:\s+[A-Za-z''\-&]+)*)        # Defendant
        |
        # Pattern 2: "Re Something" or "In re Something"
        (?:In\s+)?[Rr]e\s+
        [A-Z][A-Za-z''\-\s]+
    )
    \s*,?\s*(?=\[|\()                                        # Followed by [ or ( (with optional comma)
    """,
    re.VERBOSE,
)


# =============================================================================
# Combined pattern for quick filtering
# These are strings that indicate a potential citation exists
# =============================================================================

CITATION_INDICATORS = [
    # Year patterns - most reliable indicators
    "[19", "[20",  # Neutral citations
    "(19", "(20",  # Reported citations with round brackets
    "/19", "/20",  # Action numbers (PREFIX NUM/YYYY)
    " of 19", " of 20",  # Action numbers alternate (PREFIX No. X of YYYY)
    # Court codes (for neutral citations)
    "HKCFA", "HKCA", "HKCFI", "HKDC", "HKFC", "HKLT", "HKCT",
    "HKLdT", "HKLaT", "HKMagC", "HKFamC", "HKLBT", "HKSCT", "HKOAT", "HKCC", "HKMC",
    "CFA", "CA", "CFI",  # Alternate codes
    # Reporter codes
    "HKLRD", "HKC", "HKCFAR", "HKPLR",
    # Case name indicators
    " v ", " v. ",  # Versus
]


def has_potential_citation(text: str) -> bool:
    """Quick check if text might contain a citation."""
    return any(indicator in text for indicator in CITATION_INDICATORS)
