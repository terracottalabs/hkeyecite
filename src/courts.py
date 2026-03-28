"""
Hong Kong Court Definitions

This module contains definitions for all Hong Kong courts and tribunals
that use neutral citations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Court:
    """Represents a Hong Kong court or tribunal."""
    code: str  # Neutral citation code (e.g., "HKCFA")
    name: str  # Full name
    name_zh: Optional[str] = None  # Chinese name
    level: int = 0  # Hierarchy level (higher = more senior)
    case_prefixes: tuple = ()  # Action number prefixes used by this court


# Court of Final Appeal
HKCFA = Court(
    code="HKCFA",
    name="Court of Final Appeal",
    name_zh="終審法院",
    level=100,
    case_prefixes=("FACV", "FACC", "FAMV", "FAMC", "FAMP"),
)

# Court of Final Appeal (alternate code - older format)
CFA = Court(
    code="CFA",
    name="Court of Final Appeal",
    name_zh="終審法院",
    level=100,
    case_prefixes=(),
)

# Court of Appeal
HKCA = Court(
    code="HKCA",
    name="Court of Appeal of the High Court",
    name_zh="高等法院上訴法庭",
    level=90,
    case_prefixes=("CACV", "CACC", "CAAR", "CASJ", "CAQL", "CAAG", "CAMP"),
)

# Court of Appeal (alternate code - older format)
CA = Court(
    code="CA",
    name="Court of Appeal of the High Court",
    name_zh="高等法院上訴法庭",
    level=90,
    case_prefixes=(),
)

# Court of First Instance (High Court)
HKCFI = Court(
    code="HKCFI",
    name="Court of First Instance of the High Court",
    name_zh="高等法院原訟法庭",
    level=80,
    case_prefixes=(
        # Civil matters
        "HCA", "HCAL", "HCAJ", "HCAD", "HCB", "HCCL", "HCCW", "HCSD",
        "HCBI", "HCCT", "HCMC", "HCMP", "HCCM", "HCPI", "HCBD", "HCBS",
        "HCSN", "HCCD", "HCZZ", "HCMH", "HCIP", "HCRE",
        # Criminal & appeal cases
        "HCCC", "HCMA", "HCLA", "HCIA", "HCSA", "HCME", "HCOA", "HCUA",
        "HCED", "HCAA", "HCCP",
        # Probate matters
        "HCAP", "HCAG", "HCCA", "HCEA", "HCRC", "HCCI", "HCCV",
    ),
)

# Court of First Instance (alternate code - older format)
CFI = Court(
    code="CFI",
    name="Court of First Instance of the High Court",
    name_zh="高等法院原訟法庭",
    level=80,
    case_prefixes=(),
)

# District Court
HKDC = Court(
    code="HKDC",
    name="District Court",
    name_zh="區域法院",
    level=60,
    case_prefixes=(
        "DCCJ", "DCCC", "DCDT", "DCTC", "DCEC", "DCEO", "DCMA", "DCMP",
        "DCOA", "DCPI", "DCPA", "DCSA", "DCZZ", "DCSN",
    ),
)

# Family Court
HKFC = Court(
    code="HKFC",
    name="Family Court",
    name_zh="家事法庭",
    level=55,
    case_prefixes=("FCMC", "FCJA", "FCMP", "FCAD", "FCRE"),
)

# Also uses HKFamC in some citations
HKFamC = Court(
    code="HKFamC",
    name="Family Court",
    name_zh="家事法庭",
    level=55,
    case_prefixes=(),
)

# Lands Tribunal
HKLT = Court(
    code="HKLT",
    name="Lands Tribunal",
    name_zh="土地審裁處",
    level=50,
    case_prefixes=(
        "LDPA", "LDPB", "LDPD", "LDPE", "LDRT", "LDNT", "LDLA", "LDRA",
        "LDBG", "LDGA", "LDLR", "LDHA", "LDBM", "LDDB", "LDDA", "LDMT",
        "LDCS", "LDRW", "LDMR", "LDMP",
    ),
)

# Labour Tribunal
HKLBT = Court(
    code="HKLBT",
    name="Labour Tribunal",
    name_zh="勞資審裁處",
    level=40,
    case_prefixes=("LBTC",),
)

# Small Claims Tribunal
HKSCT = Court(
    code="HKSCT",
    name="Small Claims Tribunal",
    name_zh="小額錢債審裁處",
    level=30,
    case_prefixes=("SCTC",),
)

# Competition Tribunal
HKCT = Court(
    code="HKCT",
    name="Competition Tribunal",
    name_zh="競爭事務審裁處",
    level=70,
    case_prefixes=("CTAR", "CTEA", "CTA", "CTMP"),
)

# Obscene Articles Tribunal
HKOAT = Court(
    code="HKOAT",
    name="Obscene Articles Tribunal",
    name_zh="淫褻物品審裁處",
    level=35,
    case_prefixes=("OATD",),
)

# Coroner's Court
HKCC = Court(
    code="HKCC",
    name="Coroner's Court",
    name_zh="死因裁判法庭",
    level=45,
    case_prefixes=("CCDI",),
)

# Magistrates' Courts (Criminal)
HKMC = Court(
    code="HKMC",
    name="Magistrates' Courts",
    name_zh="裁判法院",
    level=20,
    case_prefixes=(
        # Eastern Magistrates' Court
        "ESCC", "ESS",
        # Fanling Magistrates' Courts
        "FLCC", "FLS",
        # Kowloon City Magistrates' Court
        "KCCC", "KCS",
        # Kwun Tong Magistrates' Courts
        "KTCC", "KTS",
        # Shatin Magistrates' Courts
        "STCC", "STMP", "STS",
        # Tuen Mun Magistrates' Court
        "TMCC", "TMS",
        # West Kowloon Magistrates' Courts
        "WKCC", "WKS",
    ),
)

# Magistrates' Courts (new neutral citation format)
HKMagC = Court(
    code="HKMagC",
    name="Magistrates' Courts",
    name_zh="裁判法院",
    level=20,
    case_prefixes=(),
)

# Lands Tribunal (alternate neutral citation code)
HKLdT = Court(
    code="HKLdT",
    name="Lands Tribunal",
    name_zh="土地審裁處",
    level=50,
    case_prefixes=(),
)

# Labour Tribunal (alternate code)
HKLaT = Court(
    code="HKLaT",
    name="Labour Tribunal",
    name_zh="勞資審裁處",
    level=40,
    case_prefixes=(),
)

# All courts dictionary for lookup
HK_COURTS = {
    # Primary codes (modern format)
    "HKCFA": HKCFA,
    "HKCA": HKCA,
    "HKCFI": HKCFI,
    "HKDC": HKDC,
    "HKFC": HKFC,
    "HKFamC": HKFamC,
    "HKLT": HKLT,
    "HKLdT": HKLdT,
    "HKLBT": HKLBT,
    "HKLaT": HKLaT,
    "HKSCT": HKSCT,
    "HKCT": HKCT,
    "HKOAT": HKOAT,
    "HKCC": HKCC,
    "HKMC": HKMC,
    "HKMagC": HKMagC,
    # Alternate codes (older format sometimes seen)
    "CFA": CFA,
    "CA": CA,
    "CFI": CFI,
}

# Build reverse lookup: case prefix -> court
CASE_PREFIX_TO_COURT = {}
for court in HK_COURTS.values():
    for prefix in court.case_prefixes:
        CASE_PREFIX_TO_COURT[prefix] = court


def get_court_by_code(code: str) -> Optional[Court]:
    """Get court by neutral citation code."""
    return HK_COURTS.get(code)


def get_court_by_case_prefix(prefix: str) -> Optional[Court]:
    """Get court by action number prefix."""
    return CASE_PREFIX_TO_COURT.get(prefix)


# All neutral citation court codes (for regex building)
NEUTRAL_CITATION_COURTS = tuple(HK_COURTS.keys())

# All case prefixes (for regex building)
ALL_CASE_PREFIXES = tuple(CASE_PREFIX_TO_COURT.keys())
