"""
Hong Kong Citation Extraction

This module provides the main function for extracting citations from text.
"""

import re
import unicodedata
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

    for token in tokens:
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
        pin_cite = _extract_following_pin_cite(text, token.end)
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
        )

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


def _extract_following_pin_cite(text: str, citation_end: int) -> Optional[str]:
    """
    Extract pin cite that follows a citation.

    Looks for patterns like "at [23]" or "at §§45-46" after the citation.
    """
    # Look at text after the citation (up to 50 chars)
    following_text = text[citation_end:citation_end + 50]

    # Check for pin cite immediately following
    match = PIN_CITE_REGEX.match(following_text.lstrip())
    if match:
        # Get the actual pin cite value from the matched groups
        for key in ["para_bracket", "para_section", "para_word", "page_ref"]:
            if match.group(key):
                return match.group(key)

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
