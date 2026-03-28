"""
Evaluation Dataset for hkeyecite

This module contains manually annotated test cases for evaluating
the citation extraction accuracy of hkeyecite.

Each test case includes:
- text: The input text
- expected: List of expected citation dictionaries
"""

from typing import List, Dict, Any, TypedDict


class ExpectedCitation(TypedDict, total=False):
    """Expected citation annotation."""
    type: str  # "neutral", "reported", "action"
    text: str  # The expected matched text
    year: int
    court: str  # For neutral citations
    number: int  # For neutral citations
    volume: int  # For reported citations
    reporter: str  # For reported citations
    page: int  # For reported citations
    prefix: str  # For action numbers
    case_name: str  # Optional - expected case name
    pin_cite: str  # Optional - expected pin cite


class TestCase(TypedDict):
    """A single evaluation test case."""
    id: str
    description: str
    text: str
    expected: List[ExpectedCitation]


# =============================================================================
# EVALUATION DATASET
# =============================================================================

EVAL_DATASET: List[TestCase] = [
    # -------------------------------------------------------------------------
    # Basic Neutral Citations
    # -------------------------------------------------------------------------
    {
        "id": "neutral_001",
        "description": "Basic HKCFA neutral citation",
        "text": "[2024] HKCFA 1",
        "expected": [
            {"type": "neutral", "text": "[2024] HKCFA 1", "year": 2024, "court": "HKCFA", "number": 1}
        ]
    },
    {
        "id": "neutral_002",
        "description": "HKCA neutral citation with pin cite",
        "text": "[2018] HKCA 14 at [23]",
        "expected": [
            {"type": "neutral", "text": "[2018] HKCA 14", "year": 2018, "court": "HKCA", "number": 14, "pin_cite": "23"}
        ]
    },
    {
        "id": "neutral_003",
        "description": "HKCFI neutral citation",
        "text": "[2021] HKCFI 1194",
        "expected": [
            {"type": "neutral", "text": "[2021] HKCFI 1194", "year": 2021, "court": "HKCFI", "number": 1194}
        ]
    },
    {
        "id": "neutral_004",
        "description": "HKDC neutral citation",
        "text": "[2025] HKDC 84",
        "expected": [
            {"type": "neutral", "text": "[2025] HKDC 84", "year": 2025, "court": "HKDC", "number": 84}
        ]
    },
    {
        "id": "neutral_005",
        "description": "HKFC neutral citation",
        "text": "[2025] HKFC 203",
        "expected": [
            {"type": "neutral", "text": "[2025] HKFC 203", "year": 2025, "court": "HKFC", "number": 203}
        ]
    },
    {
        "id": "neutral_006",
        "description": "HKCT neutral citation",
        "text": "[2025] HKCT 3",
        "expected": [
            {"type": "neutral", "text": "[2025] HKCT 3", "year": 2025, "court": "HKCT", "number": 3}
        ]
    },
    {
        "id": "neutral_007",
        "description": "HKLdT (Lands Tribunal) neutral citation",
        "text": "[2025] HKLdT 58",
        "expected": [
            {"type": "neutral", "text": "[2025] HKLdT 58", "year": 2025, "court": "HKLdT", "number": 58}
        ]
    },
    {
        "id": "neutral_008",
        "description": "HKMagC (Magistrates Court) neutral citation",
        "text": "[2023] HKMagC 9",
        "expected": [
            {"type": "neutral", "text": "[2023] HKMagC 9", "year": 2023, "court": "HKMagC", "number": 9}
        ]
    },

    # -------------------------------------------------------------------------
    # Neutral Citations with Case Names
    # -------------------------------------------------------------------------
    {
        "id": "neutral_name_001",
        "description": "Neutral citation with case name (Party v Party)",
        "text": "AW v Director of Immigration [2016] HKCA 123",
        "expected": [
            {"type": "neutral", "text": "[2016] HKCA 123", "year": 2016, "court": "HKCA", "number": 123,
             "case_name": "AW v Director of Immigration"}
        ]
    },
    {
        "id": "neutral_name_002",
        "description": "Neutral citation with Re case name",
        "text": "Re Zunariyah [2018] HKCA 14",
        "expected": [
            {"type": "neutral", "text": "[2018] HKCA 14", "year": 2018, "court": "HKCA", "number": 14,
             "case_name": "Re Zunariyah"}
        ]
    },
    {
        "id": "neutral_name_003",
        "description": "HKSAR case",
        "text": "HKSAR v Wong Tak Keung [2024] HKCFA 1",
        "expected": [
            {"type": "neutral", "text": "[2024] HKCFA 1", "year": 2024, "court": "HKCFA", "number": 1,
             "case_name": "HKSAR v Wong Tak Keung"}
        ]
    },
    {
        "id": "neutral_name_004",
        "description": "Single letter anonymized party",
        "text": "H v Director of Immigration [2020] HKCFA 5",
        "expected": [
            {"type": "neutral", "text": "[2020] HKCFA 5", "year": 2020, "court": "HKCFA", "number": 5,
             "case_name": "H v Director of Immigration"}
        ]
    },

    # -------------------------------------------------------------------------
    # Reported Citations (Square Brackets)
    # -------------------------------------------------------------------------
    {
        "id": "reported_sq_001",
        "description": "HKC reported citation",
        "text": "[2016] 2 HKC 393",
        "expected": [
            {"type": "reported", "text": "[2016] 2 HKC 393", "year": 2016, "volume": 2, "reporter": "HKC", "page": 393}
        ]
    },
    {
        "id": "reported_sq_002",
        "description": "HKC with case name and (CA) suffix",
        "text": "AW v Director of Immigration & Another [2016] 2 HKC 393 (CA)",
        "expected": [
            {"type": "reported", "text": "[2016] 2 HKC 393", "year": 2016, "volume": 2, "reporter": "HKC", "page": 393,
             "case_name": "AW v Director of Immigration & Another"}
        ]
    },

    # -------------------------------------------------------------------------
    # Reported Citations (Round Brackets)
    # -------------------------------------------------------------------------
    {
        "id": "reported_rd_001",
        "description": "HKCFAR reported citation",
        "text": "(2020) 23 HKCFAR 248",
        "expected": [
            {"type": "reported", "text": "(2020) 23 HKCFAR 248", "year": 2020, "volume": 23, "reporter": "HKCFAR", "page": 248}
        ]
    },
    {
        "id": "reported_rd_002",
        "description": "HKCFAR with case name and pin cite",
        "text": "H v Director of Immigration (2020) 23 HKCFAR 248 at \u00a7\u00a717-22",
        "expected": [
            {"type": "reported", "text": "(2020) 23 HKCFAR 248", "year": 2020, "volume": 23, "reporter": "HKCFAR", "page": 248,
             "case_name": "H v Director of Immigration", "pin_cite": "17-22"}
        ]
    },
    {
        "id": "reported_rd_003",
        "description": "HKCFAR with full case name",
        "text": "Peter Po Fun Chan v Winnie Cheung (2007) 10 HKCFAR 676",
        "expected": [
            {"type": "reported", "text": "(2007) 10 HKCFAR 676", "year": 2007, "volume": 10, "reporter": "HKCFAR", "page": 676,
             "case_name": "Peter Po Fun Chan v Winnie Cheung"}
        ]
    },
    {
        "id": "reported_rd_004",
        "description": "HKLRD reported citation",
        "text": "(2015) 18 HKLRD 350",
        "expected": [
            {"type": "reported", "text": "(2015) 18 HKLRD 350", "year": 2015, "volume": 18, "reporter": "HKLRD", "page": 350}
        ]
    },

    # -------------------------------------------------------------------------
    # Action Numbers
    # -------------------------------------------------------------------------
    {
        "id": "action_001",
        "description": "FACV action number",
        "text": "FACV 1/2018",
        "expected": [
            {"type": "action", "text": "FACV 1/2018", "prefix": "FACV", "number": 1, "year": 2018}
        ]
    },
    {
        "id": "action_002",
        "description": "HCAL action number",
        "text": "HCAL 1756/2020",
        "expected": [
            {"type": "action", "text": "HCAL 1756/2020", "prefix": "HCAL", "number": 1756, "year": 2020}
        ]
    },
    {
        "id": "action_003",
        "description": "CACC action number",
        "text": "CACC 106/2022",
        "expected": [
            {"type": "action", "text": "CACC 106/2022", "prefix": "CACC", "number": 106, "year": 2022}
        ]
    },
    {
        "id": "action_004",
        "description": "DCCC action number",
        "text": "DCCC 123/2024",
        "expected": [
            {"type": "action", "text": "DCCC 123/2024", "prefix": "DCCC", "number": 123, "year": 2024}
        ]
    },

    # -------------------------------------------------------------------------
    # Complex Cases (Multiple Citations)
    # -------------------------------------------------------------------------
    {
        "id": "complex_001",
        "description": "Multiple citations in paragraph (from real judgment)",
        "text": "See AW v Director of Immigration & Another [2016] 2 HKC 393 (CA) at \u00a7\u00a723-36, and H v Director of Immigration (2020) 23 HKCFAR 248 at \u00a7\u00a717-22",
        "expected": [
            {"type": "reported", "text": "[2016] 2 HKC 393", "reporter": "HKC", "case_name": "AW v Director of Immigration & Another"},
            {"type": "reported", "text": "(2020) 23 HKCFAR 248", "reporter": "HKCFAR", "case_name": "H v Director of Immigration", "pin_cite": "17-22"}
        ]
    },
    {
        "id": "complex_002",
        "description": "Neutral citations in sequence",
        "text": "See [2021] HKCFI 1194 at \u00a7\u00a712-13, upheld in [2022] HKCA 1321",
        "expected": [
            {"type": "neutral", "court": "HKCFI", "number": 1194},
            {"type": "neutral", "court": "HKCA", "number": 1321}
        ]
    },
    {
        "id": "complex_003",
        "description": "Action number followed by neutral citation",
        "text": "In HCAL 1756/2020 [2026] HKCFI 261",
        "expected": [
            {"type": "action", "prefix": "HCAL", "number": 1756},
            {"type": "neutral", "court": "HKCFI", "number": 261}
        ]
    },

    # -------------------------------------------------------------------------
    # Pin Cite Variations
    # -------------------------------------------------------------------------
    {
        "id": "pin_001",
        "description": "Pin cite with square brackets",
        "text": "[2024] HKCFA 1 at [23]",
        "expected": [
            {"type": "neutral", "pin_cite": "23"}
        ]
    },
    {
        "id": "pin_002",
        "description": "Pin cite with section symbol",
        "text": "[2024] HKCFA 1 at \u00a745",
        "expected": [
            {"type": "neutral", "pin_cite": "45"}
        ]
    },
    {
        "id": "pin_003",
        "description": "Pin cite with double section (range)",
        "text": "[2024] HKCFA 1 at \u00a7\u00a723-36",
        "expected": [
            {"type": "neutral", "pin_cite": "23-36"}
        ]
    },
    {
        "id": "pin_004",
        "description": "Pin cite with 'para'",
        "text": "[2024] HKCFA 1 at para 10",
        "expected": [
            {"type": "neutral", "pin_cite": "10"}
        ]
    },

    # -------------------------------------------------------------------------
    # Edge Cases / Negative Cases
    # -------------------------------------------------------------------------
    {
        "id": "edge_001",
        "description": "Non-citation text should not match",
        "text": "This is a regular sentence with no citations.",
        "expected": []
    },
    {
        "id": "edge_002",
        "description": "Year in brackets that is not a citation",
        "text": "The incident occurred in [2020].",
        "expected": []
    },
    {
        "id": "edge_003",
        "description": "Invalid court code should not match as HK neutral",
        "text": "[2024] INVALID 123",
        "expected": []
    },

    # -------------------------------------------------------------------------
    # Real Judgment Excerpts
    # -------------------------------------------------------------------------
    {
        "id": "real_001",
        "description": "From [2026] HKCFI 261 - multiple citations with case names",
        "text": """the Court of Appeal held that the relevant considerations include:
(i) the length of the delay; (ii) the explanation for the delay;
(see AW v Director of Immigration & Another [2016] 2 HKC 393 (CA) at \u00a7\u00a723\u201136,
Thomas Lai [2014] 6 HKC 1 at \u00a7\u00a743-45 (as also cited in AW, supra),
and H v Director of Immigration (2020) 23 HKCFAR 248 at \u00a7\u00a717-22, 36-44;
see also Re Hariatiningsih [2021] HKCFI 1194 at \u00a7\u00a712-13, 16-19 citing the aforesaid,
upheld in [2022] HKCA 1321).""",
        "expected": [
            {"type": "reported", "reporter": "HKC", "year": 2016},
            {"type": "reported", "reporter": "HKC", "year": 2014},
            {"type": "reported", "reporter": "HKCFAR", "year": 2020},
            {"type": "neutral", "court": "HKCFI", "year": 2021},
            {"type": "neutral", "court": "HKCA", "year": 2022}
        ]
    },
]


def get_eval_dataset() -> List[TestCase]:
    """Return the evaluation dataset."""
    return EVAL_DATASET


def get_test_case(test_id: str) -> TestCase:
    """Get a specific test case by ID."""
    for case in EVAL_DATASET:
        if case["id"] == test_id:
            return case
    raise ValueError(f"Test case not found: {test_id}")
