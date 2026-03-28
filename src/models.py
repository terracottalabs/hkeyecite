"""
Hong Kong Citation Models

This module contains data classes for representing different types
of Hong Kong legal citations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any


@dataclass
class HKCitation(ABC):
    """
    Abstract base class for all Hong Kong citations.

    Attributes:
        matched_text: The original text that was matched
        span: Tuple of (start, end) character positions in source text
        metadata: Additional extracted metadata
    """
    matched_text: str
    span: Tuple[int, int]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def start(self) -> int:
        """Start position in source text."""
        return self.span[0]

    @property
    def end(self) -> int:
        """End position in source text."""
        return self.span[1]

    @property
    def case_name(self) -> Optional[str]:
        """Case name, if extracted."""
        return self.metadata.get("case_name")

    @property
    def pin_cite(self) -> Optional[str]:
        """Pinpoint reference, if extracted."""
        return self.metadata.get("pin_cite")

    @abstractmethod
    def normalized(self) -> str:
        """Return a normalized string representation of the citation."""
        pass

    def __str__(self) -> str:
        return self.matched_text


@dataclass
class HKNeutralCitation(HKCitation):
    """
    Hong Kong neutral citation.

    Format: [YYYY] HKCOURT NUM
    Examples: [2024] HKCFA 1, [2021] HKCFI 1194

    Attributes:
        year: The year of the judgment (e.g., 2024)
        court: The court code (e.g., "HKCFA", "HKCA")
        number: The case number within that court/year (e.g., 1, 1194)
    """
    year: int = 0
    court: str = ""
    number: int = 0

    def normalized(self) -> str:
        """Return normalized neutral citation string."""
        return f"[{self.year}] {self.court} {self.number}"

    @property
    def court_name(self) -> Optional[str]:
        """Get the full court name."""
        from hkeyecite.courts import get_court_by_code
        court = get_court_by_code(self.court)
        return court.name if court else None


@dataclass
class HKReportedCitation(HKCitation):
    """
    Hong Kong reported (law report) citation.

    Format: (YYYY) VOL REPORTER PAGE  or  [YYYY] VOL REPORTER PAGE
    Examples: (2020) 23 HKCFAR 248, [2016] 2 HKC 393

    Attributes:
        year: The year of the report volume
        volume: The volume number
        reporter: The law report abbreviation (e.g., "HKCFAR", "HKC")
        page: The starting page number
        bracket_type: "round" for (), "square" for []
    """
    year: int = 0
    volume: int = 0
    reporter: str = ""
    page: int = 0
    bracket_type: str = "round"  # "round" or "square"

    def normalized(self) -> str:
        """Return normalized reported citation string."""
        vol = f"{self.volume} " if self.volume != 0 else ""
        if self.bracket_type == "square":
            return f"[{self.year}] {vol}{self.reporter} {self.page}"
        else:
            return f"({self.year}) {vol}{self.reporter} {self.page}"

    @property
    def reporter_name(self) -> Optional[str]:
        """Get the full reporter name."""
        from hkeyecite.reporters import get_reporter
        reporter = get_reporter(self.reporter)
        return reporter.name if reporter else None


@dataclass
class HKActionNumber(HKCitation):
    """
    Hong Kong case action/reference number.

    Format: PREFIX NUM/YYYY
    Examples: FACV 1/2018, HCAL 1756/2020, CACC 106/2022

    Attributes:
        prefix: The case type prefix (e.g., "FACV", "HCAL")
        number: The case number
        year: The year filed
    """
    prefix: str = ""
    number: int = 0
    year: int = 0

    def normalized(self) -> str:
        """Return normalized action number string."""
        return f"{self.prefix} {self.number}/{self.year}"

    @property
    def court(self) -> Optional[str]:
        """Get the court code for this action number."""
        from hkeyecite.courts import get_court_by_case_prefix
        court = get_court_by_case_prefix(self.prefix)
        return court.code if court else None
