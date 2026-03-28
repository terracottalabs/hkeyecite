from hkeyecite import get_citations

text = """
The applicant filed HCAL 1756/2020 seeking judicial review.
In Kwok Cheuk Kin v Secretary for Constitutional and Mainland Affairs [2024] HKCFA 1,
the Court of Final Appeal cited HKSAR v Harjani (2019) 22 HKCFAR 446 at [45].
"""

for i, citation in enumerate(get_citations(text), 1):
    print()
    print(f"[{i}] {citation.matched_text}")
    if citation.case_name:
        print(f"    Case: {citation.case_name}")
    if citation.pin_cite:
        print(f"    At: [{citation.pin_cite}]")
