#!/usr/bin/env python3
"""
Evaluation Script for hkeyecite

Run this script to evaluate the citation extraction accuracy against
the annotated evaluation dataset.

Usage:
    python -m hkeyecite.evaluation.run_eval
"""

import sys
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from hkeyecite import get_citations
from hkeyecite.models import (
    HKNeutralCitation,
    HKReportedCitation,
    HKActionNumber,
)
try:
    from eval_dataset import get_eval_dataset, TestCase, ExpectedCitation
except ModuleNotFoundError:
    from tests.eval_dataset import get_eval_dataset, TestCase, ExpectedCitation


@dataclass
class EvalResult:
    """Result of evaluating a single test case."""
    test_id: str
    passed: bool
    expected_count: int
    found_count: int
    matched: int
    missed: List[str]
    extra: List[str]
    details: str


def get_citation_type(citation) -> str:
    """Get the type string for a citation."""
    if isinstance(citation, HKNeutralCitation):
        return "neutral"
    elif isinstance(citation, HKReportedCitation):
        return "reported"
    elif isinstance(citation, HKActionNumber):
        return "action"
    return "unknown"


def citation_matches_expected(citation, expected: ExpectedCitation) -> bool:
    """Check if a citation matches an expected annotation."""
    ctype = get_citation_type(citation)

    # Type must match
    if ctype != expected.get("type"):
        return False

    # Check specific fields based on type
    if ctype == "neutral":
        if "court" in expected and citation.court != expected["court"]:
            return False
        if "year" in expected and citation.year != expected["year"]:
            return False
        if "number" in expected and citation.number != expected["number"]:
            return False

    elif ctype == "reported":
        if "reporter" in expected and citation.reporter != expected["reporter"]:
            return False
        if "year" in expected and citation.year != expected["year"]:
            return False
        if "volume" in expected and citation.volume != expected["volume"]:
            return False
        if "page" in expected and citation.page != expected["page"]:
            return False

    elif ctype == "action":
        if "prefix" in expected and citation.prefix != expected["prefix"]:
            return False
        if "number" in expected and citation.number != expected["number"]:
            return False
        if "year" in expected and citation.year != expected["year"]:
            return False

    # Check optional metadata
    if "pin_cite" in expected:
        actual_pin = citation.metadata.get("pin_cite", "")
        if actual_pin != expected["pin_cite"]:
            return False

    if "case_name" in expected:
        actual_name = citation.metadata.get("case_name", "")
        # Case name matching is fuzzy - just check if expected is contained
        if expected["case_name"] not in actual_name and actual_name not in expected["case_name"]:
            # Allow partial matches
            expected_parts = expected["case_name"].split(" v ")
            if len(expected_parts) == 2:
                if expected_parts[0] not in actual_name and expected_parts[1] not in actual_name:
                    return False

    return True


def evaluate_test_case(test_case: TestCase) -> EvalResult:
    """Evaluate a single test case."""
    text = test_case["text"]
    expected_list = test_case["expected"]

    # Extract citations
    citations = get_citations(text)

    # Match expected to found
    matched = 0
    missed = []
    matched_citations = set()

    for expected in expected_list:
        found_match = False
        for i, citation in enumerate(citations):
            if i in matched_citations:
                continue
            if citation_matches_expected(citation, expected):
                matched += 1
                matched_citations.add(i)
                found_match = True
                break

        if not found_match:
            missed.append(str(expected))

    # Find extra citations (not in expected)
    extra = []
    for i, citation in enumerate(citations):
        if i not in matched_citations:
            extra.append(f"{get_citation_type(citation)}: {citation.matched_text}")

    passed = (matched == len(expected_list) and len(extra) == 0)

    details = f"Expected {len(expected_list)}, found {len(citations)}, matched {matched}"

    return EvalResult(
        test_id=test_case["id"],
        passed=passed,
        expected_count=len(expected_list),
        found_count=len(citations),
        matched=matched,
        missed=missed,
        extra=extra,
        details=details
    )


def run_evaluation(verbose: bool = True) -> Tuple[int, int, List[EvalResult]]:
    """
    Run the full evaluation.

    Returns:
        Tuple of (passed_count, total_count, results)
    """
    dataset = get_eval_dataset()
    results = []
    passed = 0

    if verbose:
        print("=" * 70)
        print("HKEYECITE EVALUATION")
        print("=" * 70)
        print()

    for test_case in dataset:
        result = evaluate_test_case(test_case)
        results.append(result)

        if result.passed:
            passed += 1
            if verbose:
                print(f"✓ {result.test_id}: {test_case['description']}")
        else:
            if verbose:
                print(f"✗ {result.test_id}: {test_case['description']}")
                print(f"  {result.details}")
                if result.missed:
                    print(f"  Missed: {result.missed}")
                if result.extra:
                    print(f"  Extra: {result.extra}")

    if verbose:
        print()
        print("=" * 70)
        print(f"RESULTS: {passed}/{len(dataset)} tests passed ({100*passed/len(dataset):.1f}%)")
        print("=" * 70)

    return passed, len(dataset), results


def run_single_test(test_id: str):
    """Run a single test case for debugging."""
    try:
        from eval_dataset import get_test_case
    except ModuleNotFoundError:
        from tests.eval_dataset import get_test_case

    test_case = get_test_case(test_id)
    print(f"Test: {test_id}")
    print(f"Description: {test_case['description']}")
    print(f"Text: {test_case['text'][:100]}...")
    print()

    citations = get_citations(test_case["text"])
    print(f"Found {len(citations)} citations:")
    for i, c in enumerate(citations):
        print(f"  {i+1}. {get_citation_type(c)}: {c.matched_text}")
        if c.metadata:
            for k, v in c.metadata.items():
                if k != "refers_to":
                    print(f"      {k}: {v}")

    print()
    print(f"Expected {len(test_case['expected'])} citations:")
    for exp in test_case["expected"]:
        print(f"  - {exp}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate hkeyecite")
    parser.add_argument("--test", "-t", help="Run a single test by ID")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    args = parser.parse_args()

    if args.test:
        run_single_test(args.test)
    else:
        run_evaluation(verbose=not args.quiet)
