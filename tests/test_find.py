"""
Tests for hkeyecite citation extraction.

Test cases are derived from real Hong Kong judgments.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hkeyecite import get_citations
from hkeyecite.models import (
    HKNeutralCitation,
    HKReportedCitation,
    HKActionNumber,
)
from hkeyecite.find import (
    extract_neutral_citation,
    extract_reported_citations,
    extract_action_numbers,
)


class TestNeutralCitations(unittest.TestCase):
    """Tests for neutral citation extraction."""

    def test_basic_neutral_citation(self):
        """Test basic neutral citation: [YYYY] COURT NUM"""
        text = "[2024] HKCFA 1"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertIsInstance(c, HKNeutralCitation)
        self.assertEqual(c.year, 2024)
        self.assertEqual(c.court, "HKCFA")
        self.assertEqual(c.number, 1)
        self.assertEqual(c.normalized(), "[2024] HKCFA 1")

    def test_neutral_citation_hkca(self):
        """Test Court of Appeal neutral citation."""
        text = "See [2018] HKCA 14 at [23]"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertIsInstance(c, HKNeutralCitation)
        self.assertEqual(c.year, 2018)
        self.assertEqual(c.court, "HKCA")
        self.assertEqual(c.number, 14)
        self.assertEqual(c.metadata.get("pin_cite"), "23")

    def test_neutral_citation_hkcfi(self):
        """Test Court of First Instance neutral citation."""
        text = "[2021] HKCFI 1194"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertEqual(c.court, "HKCFI")
        self.assertEqual(c.number, 1194)

    def test_multiple_neutral_citation(self):
        """Test extracting multiple neutral citations from text."""
        text = """
        See [2021] HKCFI 1194 at §§12-13, upheld in [2022] HKCA 1321.
        """
        citations = extract_neutral_citation(text)

        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0].court, "HKCFI")
        self.assertEqual(citations[0].number, 1194)
        self.assertEqual(citations[1].court, "HKCA")
        self.assertEqual(citations[1].number, 1321)


class TestReportedCitations(unittest.TestCase):
    """Tests for reported (law report) citation extraction."""

    def test_hkcfar_citation(self):
        """Test HKCFAR citation with round brackets."""
        text = "(2020) 23 HKCFAR 248"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertIsInstance(c, HKReportedCitation)
        self.assertEqual(c.year, 2020)
        self.assertEqual(c.volume, 23)
        self.assertEqual(c.reporter, "HKCFAR")
        self.assertEqual(c.page, 248)
        self.assertEqual(c.bracket_type, "round")

    def test_hkc_citation(self):
        """Test HKC citation with square brackets."""
        text = "[2016] 2 HKC 393"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertIsInstance(c, HKReportedCitation)
        self.assertEqual(c.year, 2016)
        self.assertEqual(c.volume, 2)
        self.assertEqual(c.reporter, "HKC")
        self.assertEqual(c.page, 393)
        self.assertEqual(c.bracket_type, "square")

    def test_reported_citation_with_case_name(self):
        """Test reported citation with case name extraction."""
        text = "AW v Director of Immigration & Another [2016] 2 HKC 393 (CA)"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertIsInstance(c, HKReportedCitation)
        # Should extract case name
        self.assertIn("case_name", c.metadata)

    def test_hkcfar_with_pin_cite(self):
        """Test HKCFAR citation with pin cite."""
        text = "(2007) 10 HKCFAR 676 at [45]"
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertEqual(c.reporter, "HKCFAR")
        self.assertEqual(c.metadata.get("pin_cite"), "45")


class TestActionNumbers(unittest.TestCase):
    """Tests for action number extraction."""

    def test_facv_action_number(self):
        """Test CFA civil action number."""
        text = "FACV 1/2018"
        citations = extract_action_numbers(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertIsInstance(c, HKActionNumber)
        self.assertEqual(c.prefix, "FACV")
        self.assertEqual(c.number, 1)
        self.assertEqual(c.year, 2018)
        self.assertEqual(c.court, "HKCFA")

    def test_hcal_action_number(self):
        """Test High Court Administrative Law action number."""
        text = "HCAL 1756/2020"
        citations = extract_action_numbers(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertEqual(c.prefix, "HCAL")
        self.assertEqual(c.number, 1756)
        self.assertEqual(c.year, 2020)
        self.assertEqual(c.court, "HKCFI")

    def test_cacc_action_number(self):
        """Test Court of Appeal Criminal action number."""
        text = "CACC 106/2022"
        citations = extract_action_numbers(text)

        self.assertEqual(len(citations), 1)
        c = citations[0]
        self.assertEqual(c.prefix, "CACC")
        self.assertEqual(c.court, "HKCA")


class TestComplexExtractions(unittest.TestCase):
    """Tests for complex real-world citation patterns."""

    def test_real_judgment_excerpt_1(self):
        """Test extraction from real judgment text (from [2026] HKCFI 261)."""
        text = """
        the Court of Appeal held that the relevant considerations include:
        (see AW v Director of Immigration & Another [2016] 2 HKC 393 (CA) at §§23‑36,
        Thomas Lai [2014] 6 HKC 1 at §§43-45 (as also cited in AW, supra),
        and H v Director of Immigration (2020) 23 HKCFAR 248 at §§17-22
        """
        citations = get_citations(text)

        # Should find multiple citations
        self.assertGreaterEqual(len(citations), 3)

        # Check for specific citations
        courts_found = [c.court if hasattr(c, 'court') else c.reporter
                       for c in citations
                       if isinstance(c, (HKNeutralCitation, HKReportedCitation))]
        self.assertIn("HKC", courts_found)
        self.assertIn("HKCFAR", courts_found)

    def test_multiple_citation_types(self):
        """Test text with multiple citation types."""
        text = """
        In HCAL 1756/2020 [2026] HKCFI 261, the court followed
        Peter Po Fun Chan v Winnie Cheung (2007) 10 HKCFAR 676.
        See also Re Zunariyah [2018] HKCA 14 at [23]. Id. at [25].
        """
        citations = get_citations(text)

        # Should find action number, neutral citations, and reported citation
        types_found = [type(c).__name__ for c in citations]
        self.assertIn("HKActionNumber", types_found)
        self.assertIn("HKNeutralCitation", types_found)
        self.assertIn("HKReportedCitation", types_found)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def test_empty_text(self):
        """Test with empty text."""
        citations = get_citations("")
        self.assertEqual(len(citations), 0)

    def test_no_citations(self):
        """Test with text containing no citations."""
        text = "This is a test document with no legal citations."
        citations = get_citations(text)
        self.assertEqual(len(citations), 0)

    def test_partial_citation_not_matched(self):
        """Test that partial/invalid citations are not matched."""
        text = "[2024] INVALID 1"  # Not a valid court code
        citations = get_citations(text)
        # Should not match as neutral citation
        neutral = [c for c in citations if isinstance(c, HKNeutralCitation)]
        self.assertEqual(len(neutral), 0)

    def test_citation_normalization(self):
        """Test that citations are normalized correctly."""
        text = "[2024]  HKCFA   1"  # Extra whitespace
        citations = get_citations(text)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0].normalized(), "[2024] HKCFA 1")


if __name__ == "__main__":
    unittest.main()
