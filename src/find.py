"""
Hong Kong Citation Extraction

This module provides the main function for extracting citations from text.
"""

import re
import unicodedata
from datetime import date
from typing import List, Optional

from hkeyecite.models import (
    HKCitation,
    HKNeutralCitation,
    HKReportedCitation,
    HKActionNumber,
)
from hkeyecite.reporters import get_reporter
from hkeyecite.tokenizers import (
    Token,
    TokenType,
    HKTokenizer,
    default_tokenizer,
)
from hkeyecite.regexes import (
    PIN_CITE_REGEX,
    CASE_NAME_BEFORE_CITATION,
)


_INVISIBLE_RE = re.compile(r'[\u200b-\u200f\u2028-\u202f\u2060-\u2069\u00ad\ufeff]')
_ACTION_DATE_WINDOW = 35

# Strict continuation pattern for comma/and-separated pin cite lists.
# Only matches pure numbers or ranges; any non-numeric token breaks the scan.
_PIN_CITE_LIST_CONTINUATION = re.compile(
    r"""
    (?:\s*,\s*\d+(?:(?:[\u2013-]|(?:\s+to\s+))\d+)?)*   # zero or more ", N" or ", N-M"
    (?:\s*,?\s+and\s+\d+(?:(?:[\u2013-]|(?:\s+to\s+))\d+)?)?  # optional final "and N" or ", and N"
    """,
    re.VERBOSE,
)

_MONTH_FULL_NAMES = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)
_MONTH_ABBR_NAMES = "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec"
_MONTH_NAME_PATTERN = rf"(?:{_MONTH_FULL_NAMES}|{_MONTH_ABBR_NAMES})"

_MONTH_NAMES = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

_ACTION_DATE_REGEX = re.compile(
    rf"""
    (?<!\d)
    (?:
        # Numeric: DD/MM/YYYY, DD.MM.YYYY, DD-MM-YYYY (consistent separator)
        (?P<num_day>\d{{1,2}})
        (?P<sep>[-/.])
        (?P<num_month>\d{{1,2}})
        (?P=sep)
        (?P<num_year>\d{{4}})
        |
        # Textual: 3 April 2018, 3rd April 2018, 3rd of April 2018, 3 Apr. 2018
        (?P<text_day>\d{{1,2}})
        (?:st|nd|rd|th)?
        \s+
        (?:of\s+)?
        (?P<text_month>{_MONTH_NAME_PATTERN})
        \.?,?
        \s+
        (?P<text_year>\d{{4}})
    )
    (?!\d)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _normalize_text(text: str) -> str:
    """Strip invisible Unicode characters and normalize for reliable regex matching."""
    # Strip zero-width joiners, soft hyphens, BiDi controls, BOM, etc.
    text = _INVISIBLE_RE.sub('', text)
    # NFKC: collapse fullwidth chars, ligatures, compatibility spaces
    text = unicodedata.normalize('NFKC', text)
    return text


def _normalize_reporter(code: str) -> str:
    """Normalize dotted reporter abbreviations to canonical form (e.g., H.K.L.R. -> HKLR)."""
    reporter = get_reporter(code)
    return reporter.code if reporter else code


def get_citations(
    text: str,
    tokenizer: Optional[HKTokenizer] = None,
    include_action_numbers: bool = True,
) -> List[HKCitation]:
    """
    Extract all citations from text.

    This is the main entry point for the hkeyecite library.

    Args:
        text: The text to extract citations from
        tokenizer: Optional custom tokenizer (uses default if not provided)
        include_action_numbers: Whether to include action number citations

    Returns:
        List of HKCitation objects, sorted by position in text

    Example:
        >>> from hkeyecite import get_citations
        >>> text = "See AW v Director of Immigration [2016] 2 HKC 393 at [23]"
        >>> citations = get_citations(text)
        >>> print(citations[0])
        [2016] 2 HKC 393
    """
    if tokenizer is None:
        tokenizer = default_tokenizer

    text = _normalize_text(text)
    tokens = tokenizer.tokenize(text)
    citations: List[HKCitation] = []

    for i, token in enumerate(tokens):
        citation = _token_to_citation(token, text)
        if citation is None:
            continue

        # Filter by type if requested
        if not include_action_numbers and isinstance(citation, HKActionNumber):
            continue

        # Try to extract case name for full citations
        if isinstance(citation, (HKNeutralCitation, HKReportedCitation)):
            case_name = _extract_case_name(text, token.start)
            if case_name:
                citation.metadata["case_name"] = case_name

        # Try to extract pin cite that follows the citation
        next_start = tokens[i + 1].start if i + 1 < len(tokens) else None
        pin_cite = _extract_following_pin_cite(text, token.end, next_start)
        if pin_cite:
            citation.metadata["pin_cite"] = pin_cite

        citations.append(citation)

    return citations


def _token_to_citation(token: Token, text: str) -> Optional[HKCitation]:
    """Convert a token to the appropriate citation type."""

    if token.type == TokenType.NEUTRAL_CITATION:
        return HKNeutralCitation(
            matched_text=token.text,
            span=(token.start, token.end),
            year=int(token.groups["year"]),
            court=token.groups["court"],
            number=int(token.groups["number"]),
        )

    elif token.type == TokenType.REPORTED_CITATION:
        # Determine bracket type from the matched text
        bracket_type = "square" if token.text.startswith("[") else "round"
        # Handle citations without volume (e.g., [1986] HKLR 1049)
        volume_str = token.groups.get("volume")
        return HKReportedCitation(
            matched_text=token.text,
            span=(token.start, token.end),
            year=int(token.groups["year"]),
            volume=int(volume_str) if volume_str else 0,
            reporter=_normalize_reporter(token.groups["reporter"]),
            page=int(token.groups["page"]),
            bracket_type=bracket_type,
        )

    elif token.type == TokenType.ACTION_NUMBER:
        return HKActionNumber(
            matched_text=token.text,
            span=(token.start, token.end),
            prefix=token.groups["prefix"],
            number=int(token.groups["number"]),
            year=int(token.groups["year"]),
            nearby_date=_extract_nearby_action_date(text, token.start, token.end),
        )

    return None


def _extract_nearby_action_date(text: str, citation_start: int, citation_end: int) -> Optional[str]:
    """Find the closest valid date within 35 characters of an action number."""
    search_start = max(0, citation_start - _ACTION_DATE_WINDOW)
    search_end = min(len(text), citation_end + _ACTION_DATE_WINDOW)
    left_text = text[search_start:citation_start]
    right_text = text[citation_end:search_end]

    best_date = None
    best_distance = None
    candidates = [
        (match, len(left_text) - match.end()) for match in _ACTION_DATE_REGEX.finditer(left_text)
    ] + [
        (match, match.start()) for match in _ACTION_DATE_REGEX.finditer(right_text)
    ]

    for match, distance in candidates:
        normalized = _normalize_action_date_match(match)
        if normalized is not None and (best_distance is None or distance < best_distance):
            best_date = normalized
            best_distance = distance

    return best_date


def _normalize_action_date_match(match: re.Match) -> Optional[str]:
    """
    Normalize supported nearby action dates to YYYY-MM-DD.
    Supports DD/MM/YYYY, DD.MM.YYYY, DD-MM-YYYY, and DD Month YYYY variants.
    US-style formats (e.g. MM/DD/YYYY) are not supported.
    """
    if match.group("num_day"):
        day = int(match.group("num_day"))
        month = int(match.group("num_month"))
        year = int(match.group("num_year"))
    else:
        day = int(match.group("text_day"))
        month_str = match.group("text_month").lower()
        month = _MONTH_NAMES.get(month_str)
        if month is None:
            return None
        year = int(match.group("text_year"))

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _extract_case_name(text: str, citation_start: int) -> Optional[str]:
    """
    Extract case name that appears before a citation.

    Looks for patterns like "AW v Director of Immigration" before the citation.
    """
    # Look at text before and including the citation start (to capture names ending at citation)
    search_start = max(0, citation_start - 200)
    # Include a bit after citation_start to ensure the lookahead works
    search_text = text[search_start:citation_start + 5]

    # Find the last case name pattern
    match = None
    for m in CASE_NAME_BEFORE_CITATION.finditer(search_text):
        match = m

    if match:
        case_name = match.group("case_name").strip()
        # Clean up common prefixes
        case_name = re.sub(r"^(?:see|See|SEE|cf\.?|Cf\.?|also|Also|[Ii]n)\s+", "", case_name)
        case_name = case_name.strip(" ,;:")
        if len(case_name) > 3:  # Minimum reasonable case name length (e.g., "H v X")
            return case_name

    return None


def _truncate_at_sentence_boundary(text: str) -> str:
    """Return text truncated at the first sentence or clause boundary.

    Periods in pin-cite abbreviations (p., pp., para., paras.) are
    ignored as boundaries. Semicolons are always treated as boundaries.
    """
    abbreviations = ("p.", "pp.", "para.", "paras.", "paragraph.", "paragraphs.")
    for i, char in enumerate(text):
        if char in ";?!":
            return text[:i]
        if char == ".":
            prefix = text[max(0, i - 12) : i + 1].lower()
            if any(prefix.endswith(a) for a in abbreviations):
                continue
            return text[:i]
    return text


def _extract_following_pin_cite(
    text: str, citation_end: int, next_citation_start: Optional[int] = None
) -> Optional[str]:
    """
    Extract pin cite that follows a citation.

    Looks for patterns like "[23]", "§§45-46", "para 10", or "p 10"
    in the text immediately following the citation, bounded by the
    next citation (if any) and sentence boundaries.
    """
    max_window = 50
    if next_citation_start is not None:
        max_window = min(max_window, next_citation_start - citation_end)
    if max_window <= 0:
        return None

    following_text = text[citation_end : citation_end + max_window]
    following_text = _truncate_at_sentence_boundary(following_text)
    if not following_text.strip():
        return None

    matches = list(PIN_CITE_REGEX.finditer(following_text))
    if not matches:
        return None

    # Prefer explicit pin forms over bare page/letter references when both occur.
    # Bracketed numbers are weakest — they overlap heavily with years and other citation parts.
    for key in ["para_section", "para_word", "page_ref", "para_bracket"]:
        for match in matches:
            value = match.group(key)
            if value:
                # Reject 4-digit bracketed numbers — almost always a year
                if key == "para_bracket" and re.fullmatch(r"\d{4}", value):
                    continue
                # Look for comma/and-separated continuations (e.g., "paras. 12 and 13")
                tail = following_text[match.end():]
                cont_match = _PIN_CITE_LIST_CONTINUATION.match(tail)
                if cont_match and cont_match.group(0):
                    value = value + cont_match.group(0)
                    # Normalize "and" conjunctions to comma-separated for expand_pin_cite
                    value = re.sub(r"\s*,?\s+and\s+", ", ", value)
                return value

    return None


def extract_neutral_citation(text: str) -> List[HKNeutralCitation]:
    """
    Extract only neutral citations from text.

    Convenience function for extracting just neutral citations.

    Args:
        text: The text to extract citations from

    Returns:
        List of HKNeutralCitation objects
    """
    citations = get_citations(
        text,
        include_action_numbers=False,
    )
    return [c for c in citations if isinstance(c, HKNeutralCitation)]


def extract_reported_citations(text: str) -> List[HKReportedCitation]:
    """
    Extract only reported (law report) citations from text.

    Convenience function for extracting just reported citations.

    Args:
        text: The text to extract citations from

    Returns:
        List of HKReportedCitation objects
    """
    citations = get_citations(
        text,
        include_action_numbers=False,
    )
    return [c for c in citations if isinstance(c, HKReportedCitation)]


def extract_action_numbers(text: str) -> List[HKActionNumber]:
    """
    Extract only action numbers from text.

    Convenience function for extracting just action numbers.

    Args:
        text: The text to extract citations from

    Returns:
        List of HKActionNumber objects
    """
    citations = get_citations(text)
    return [c for c in citations if isinstance(c, HKActionNumber)]
