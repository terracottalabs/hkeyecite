"""
Hong Kong Citation Tokenizers

This module provides tokenization utilities for extracting citations from text.
"""

import re
from dataclasses import dataclass
from typing import List, Iterator, Tuple, Optional, Pattern
from enum import Enum, auto

from hkeyecite.regexes import (
    NEUTRAL_CITATION_REGEX,
    REPORTED_ROUND_REGEX,
    REPORTED_SQUARE_REGEX,
    REPORTED_SQUARE_NO_VOL_REGEX,
    ACTION_NUMBER_REGEX,
    ACTION_NUMBER_ALT_REGEX,
    PIN_CITE_REGEX,
    has_potential_citation,
)


class TokenType(Enum):
    """Types of tokens that can be extracted."""
    NEUTRAL_CITATION = auto()
    REPORTED_CITATION = auto()
    ACTION_NUMBER = auto()
    PIN_CITE = auto()
    TEXT = auto()  # Plain text between citations


@dataclass
class Token:
    """
    A token extracted from text.

    Attributes:
        type: The type of token
        text: The matched text
        start: Start position in source text
        end: End position in source text
        groups: Named groups from regex match
    """
    type: TokenType
    text: str
    start: int
    end: int
    groups: dict

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.text!r}, {self.start}:{self.end})"


@dataclass
class TokenExtractor:
    """
    Extracts tokens of a specific type using a regex pattern.

    Attributes:
        token_type: The type of token this extractor produces
        pattern: Compiled regex pattern
        filter_strings: Quick filter strings for efficiency
    """
    token_type: TokenType
    pattern: Pattern
    filter_strings: Tuple[str, ...] = ()

    def extract(self, text: str) -> Iterator[Token]:
        """Extract all tokens from text."""
        # Quick filter: skip if no filter strings match
        if self.filter_strings and not any(s in text for s in self.filter_strings):
            return

        for match in self.pattern.finditer(text):
            yield Token(
                type=self.token_type,
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                groups=match.groupdict(),
            )


class HKTokenizer:
    """
    Tokenizer for Hong Kong legal citations.

    Extracts all citation tokens from text using a set of extractors.
    """

    def __init__(self):
        """Initialize with default extractors."""
        self.extractors = [
            # Neutral citations: [2024] HKCFA 1
            TokenExtractor(
                token_type=TokenType.NEUTRAL_CITATION,
                pattern=NEUTRAL_CITATION_REGEX,
                filter_strings=("[19", "[20"),
            ),
            # Reported citations with round brackets: (2020) 23 HKCFAR 248
            TokenExtractor(
                token_type=TokenType.REPORTED_CITATION,
                pattern=REPORTED_ROUND_REGEX,
                filter_strings=("(19", "(20"),
            ),
            # Reported citations with square brackets: [2016] 2 HKC 393
            TokenExtractor(
                token_type=TokenType.REPORTED_CITATION,
                pattern=REPORTED_SQUARE_REGEX,
                filter_strings=("[19", "[20"),
            ),
            # Reported citations without volume: [1986] HKLR 1049
            TokenExtractor(
                token_type=TokenType.REPORTED_CITATION,
                pattern=REPORTED_SQUARE_NO_VOL_REGEX,
                filter_strings=("HKLR", "HKCLR"),
            ),
            # Action numbers: FACV 1/2018
            TokenExtractor(
                token_type=TokenType.ACTION_NUMBER,
                pattern=ACTION_NUMBER_REGEX,
                filter_strings=("/19", "/20"),
            ),
            # Action numbers alternate format: FACV No. 1 of 2018
            TokenExtractor(
                token_type=TokenType.ACTION_NUMBER,
                pattern=ACTION_NUMBER_ALT_REGEX,
                filter_strings=(" of 19", " of 20"),
            ),
        ]

    def tokenize(self, text: str) -> List[Token]:
        """
        Extract all citation tokens from text.

        Returns tokens sorted by their position in the text.
        Overlapping tokens are resolved by preferring longer matches.
        """
        if not has_potential_citation(text):
            return []

        all_tokens = []
        for extractor in self.extractors:
            all_tokens.extend(extractor.extract(text))

        # Sort by start position
        all_tokens.sort(key=lambda t: (t.start, -t.end))

        # Remove overlapping tokens (prefer longer matches)
        filtered_tokens = []
        last_end = 0
        for token in all_tokens:
            if token.start >= last_end:
                filtered_tokens.append(token)
                last_end = token.end
            elif token.end > last_end:
                # This token extends beyond the last one - check if it's better
                if len(token.text) > len(filtered_tokens[-1].text):
                    filtered_tokens[-1] = token
                    last_end = token.end

        return filtered_tokens

    def extract_pin_cites(self, text: str, after_position: int = 0) -> List[Token]:
        """
        Extract pin cite tokens from text after a given position.

        Useful for finding pin cites that follow a citation.
        """
        tokens = []
        for match in PIN_CITE_REGEX.finditer(text[after_position:]):
            # Only return if it appears shortly after the position
            if match.start() <= 5:  # Allow up to 5 chars of whitespace
                tokens.append(Token(
                    type=TokenType.PIN_CITE,
                    text=match.group(0),
                    start=after_position + match.start(),
                    end=after_position + match.end(),
                    groups=match.groupdict(),
                ))
        return tokens


# Default tokenizer instance
default_tokenizer = HKTokenizer()


def tokenize(text: str) -> List[Token]:
    """Convenience function to tokenize text with default tokenizer."""
    return default_tokenizer.tokenize(text)
