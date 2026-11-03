from __future__ import annotations

import re
from typing import TypedDict

from backend.models.schemas import RiskFinding, RiskLevel


class Rule(TypedDict):
    pattern: str
    title: str
    risk_level: str
    legal_basis: str
    explanation: str


RULES: list[Rule] = [
    {
        "pattern": r"\b(?:lock[- ]?in period|minimum commitment|early termination fee|termination penalty)\b",
        "title": "Lock-in or exit-cost clause",
        "risk_level": "medium",
        "legal_basis": "Indian Contract Act, 1872, including Sections 27 and 74 where applicable",
        "explanation": "This wording may constrain exit or impose a termination amount. Enforceability depends on the clause, consideration, facts, and applicable law; review the duration and calculation method.",
    },
    {
        "pattern": r"\b(?:at its sole discretion|without cause|without assigning any reason)\b.{0,120}\b(?:terminate|suspend|cancel)\b|\b(?:terminate|suspend|cancel)\b.{0,120}\b(?:at its sole discretion|without cause|without assigning any reason)\b",
        "title": "One-sided termination right",
        "risk_level": "medium",
        "legal_basis": "Indian Contract Act, 1872; interpretation depends on the full agreement",
        "explanation": "The clause appears to give one party a broad exit right. Compare notice, cure periods, accrued payment, and termination rights for both parties.",
    },
    {
        "pattern": r"\b(?:GSTIN|GST registration|input tax credit|tax invoice|goods and services tax)\b",
        "title": "GST compliance reference",
        "risk_level": "low",
        "legal_basis": "Central Goods and Services Tax Act, 2017, including Sections 16 and 31 where applicable",
        "explanation": "The agreement references GST or tax documentation. Verify GSTIN details, invoice requirements, tax allocation, and input tax credit conditions with a qualified tax professional.",
    },
]

_ONES = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}
_TENS = {
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
_NUMBER_WORDS = sorted(
    [*_TENS, *(f"{tens} {one}" for tens in _TENS for one in _ONES)],
    key=len,
    reverse=True,
)
_NUMBER_PATTERN = "|".join(re.escape(value).replace(r"\ ", r"[\s-]+") for value in _NUMBER_WORDS)
_DURATION_PATTERN = re.compile(
    rf"\b(?P<amount>\d{{1,4}}|{_NUMBER_PATTERN})\s*(?:(?:calendar|working|business)\s+)?days?\b",
    flags=re.IGNORECASE,
)
_PAYMENT_PATTERN = re.compile(r"\b(?:payment|payments|payable|invoice|invoices|settle|settlement)\b", re.IGNORECASE)
_CLAUSE_PATTERN = re.compile(r"[^.!?;\n]+(?:[.!?;]|$)")
_PAYMENT_EXPLANATION = (
    "For a qualifying micro or small enterprise supplier, the agreed payment period cannot exceed 45 days "
    "from acceptance or deemed acceptance under Sections 15-16 of the MSMED Act, 2006. Confirm supplier "
    "eligibility, the applicable start date, and the complete clause with qualified counsel."
)


def _duration_days(value: str) -> int:
    normalized = value.strip().lower().replace("-", " ")
    if normalized.isdigit():
        return int(normalized)
    parts = normalized.split()
    return _TENS[parts[0]] + (_ONES[parts[1]] if len(parts) == 2 else 0)


def _payment_findings(text: str) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    for clause in _CLAUSE_PATTERN.findall(text):
        if not _PAYMENT_PATTERN.search(clause):
            continue
        for duration in _DURATION_PATTERN.finditer(clause):
            if _duration_days(duration.group("amount")) <= 45:
                continue
            findings.append(
                RiskFinding(
                    id=f"msme-payment-{len(findings) + 1}",
                    title="Payment term may exceed 45 days",
                    risk_level=RiskLevel.HIGH,
                    legal_basis="MSMED Act, 2006, Sections 15-16",
                    explanation=_PAYMENT_EXPLANATION,
                    match_text=clause.strip(),
                )
            )
    return findings


def analyze_text(text: str) -> list[RiskFinding]:
    findings = _payment_findings(text)
    for index, rule in enumerate(RULES, start=1):
        match = re.search(rule["pattern"], text, flags=re.IGNORECASE | re.DOTALL)
        if match is None:
            continue
        findings.append(
            RiskFinding(
                id=f"rule-{index}",
                title=rule["title"],
                risk_level=RiskLevel(rule["risk_level"]),
                legal_basis=rule["legal_basis"],
                explanation=rule["explanation"],
                match_text=match.group(0).strip(),
            )
        )
    return findings
