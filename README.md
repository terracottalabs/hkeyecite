# hkeyecite

A Python library that automatically finds and extracts legal citations from Hong Kong court judgments.

Give it any block of text containing Hong Kong legal references, and it will identify and parse:

- **Neutral citations** -- e.g. `[2024] HKCFA 1`
- **Law report citations** -- e.g. `(2019) 22 HKCFAR 446`
- **Action numbers** -- e.g. `HCAL 1756/2020`

It also extracts case names (e.g. "HKSAR v Harjani") and pinpoint references (e.g. "at [45]") when present.

![Demo](https://raw.githubusercontent.com/terracottalabs/hkeyecite/main/demo.gif)

## Installation

```bash
pip install hkeyecite
```

Requires Python 3.10 or later.

## What it recognises

### Neutral citations

The format used by the Judiciary since 2018: `[Year] Court Number`

| Code | Court |
|---|---|
| `HKCFA` | Court of Final Appeal |
| `HKCA` | Court of Appeal |
| `HKCFI` | Court of First Instance |
| `HKDC` | District Court |
| `HKFC` / `HKFamC` | Family Court |
| `HKLT` / `HKLdT` | Lands Tribunal |
| `HKCT` | Competition Tribunal |
| `HKLBT` / `HKLaT` | Labour Tribunal |
| `HKSCT` | Small Claims Tribunal |
| `HKOAT` | Obscene Articles Tribunal |
| `HKCC` | Coroner's Court |
| `HKMC` / `HKMagC` | Magistrates' Courts |
| `CFA` / `CA` / `CFI` | Older alternate codes |

### Law report citations

References to published law report series: `(Year) Volume Reporter Page`

| Code | Report Series |
|---|---|
| `HKCFAR` | Hong Kong Court of Final Appeal Reports |
| `HKLRD` | Hong Kong Law Reports & Digest |
| `HKC` | Hong Kong Cases |
| `HKPLR` | Hong Kong Public Law Reports |
| `HKLR` | Hong Kong Law Reports (historical) |
| `HKCLR` | Hong Kong Criminal Law Reports |
| `HKCLRT` | Hong Kong Chinese Law Reports & Translations |

Dotted variations (e.g. `H.K.L.R.D.`, `H.K.C.F.A.R.`) are automatically normalised.

### Action numbers

Case filing references: `Prefix Number/Year`

Common prefixes include FACV, FACC (Court of Final Appeal), CACV, CACC (Court of Appeal), HCA, HCAL, HCCC (Court of First Instance), DCCJ, DCCC (District Court), and many more.

### Metadata

When a citation is preceded by a case name like `HKSAR v Harjani` or `Re Something`, it is automatically extracted. Pinpoint references that follow a citation (`at [45]`, `at para 10`, `at p. 5`) are also captured.

## API

### `get_citations(text)`

The main function. Returns a list of citations found in the text, sorted by position.

```python
from hkeyecite import get_citations

citations = get_citations(text)
```

Each citation has:
- `.matched_text` -- the original text that was matched
- `.normalized()` -- a standardised form of the citation
- `.case_name` -- the case name, if one appears before the citation
- `.pin_cite` -- the pinpoint reference (e.g. paragraph number), if one follows
- `.start`, `.end` -- character positions in the source text

Pass `include_action_numbers=False` to skip action number extraction.

### Convenience functions

```python
from hkeyecite.find import extract_neutral_citation, extract_reported_citations, extract_action_numbers

# Extract only one type
neutral = extract_neutral_citation(text)
reported = extract_reported_citations(text)
actions = extract_action_numbers(text)
```

### Court and reporter lookup

```python
from hkeyecite.courts import get_court_by_code, get_court_by_case_prefix
from hkeyecite.reporters import get_reporter

court = get_court_by_code("HKCFA")
court.name      # "Court of Final Appeal"
court.name_zh   # "終審法院"

court = get_court_by_case_prefix("FACV")
court.code      # "HKCFA"

reporter = get_reporter("HKCFAR")
reporter.name   # "Hong Kong Court of Final Appeal Reports"
```

## Limitations

- Only Hong Kong citations are supported -- UK, Australian, and other jurisdictions are not covered
- Case names in Chinese characters are not extracted
- Some older or non-standard citation formats may not be recognised

## Contributing

Pull requests are welcome. If you find a citation format that isn't recognised or have ideas for improvement, feel free to open an issue or PR.

## Acknowledgments

This project is derived from [eyecite](https://github.com/freelawproject/eyecite), a citation extraction library for US legal citations by the Free Law Project. `hkeyecite` adapts eyecite's approach for the Hong Kong jurisdiction, covering HK-specific courts, law reports, action number formats, and neutral citation conventions.

## License

BSD 2-Clause License -- see [LICENSE.txt](LICENSE.txt) for details.
