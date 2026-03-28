"""
hkeyecite - Hong Kong Legal Citation Extraction Library

A library for extracting and parsing legal citations from Hong Kong court judgments.

Usage:
    from hkeyecite import get_citations

    text = "See AW v Director of Immigration [2016] 2 HKC 393 at [23]"
    citations = get_citations(text)
"""

from hkeyecite.find import get_citations
from hkeyecite.models import (
    HKCitation,
    HKNeutralCitation,
    HKReportedCitation,
    HKActionNumber,
)
from hkeyecite.courts import HK_COURTS
from hkeyecite.reporters import HK_REPORTERS

__version__ = "0.1.1"
__all__ = [
    "get_citations",
    "HKCitation",
    "HKNeutralCitation",
    "HKReportedCitation",
    "HKActionNumber",
    "HK_COURTS",
    "HK_REPORTERS",
]
