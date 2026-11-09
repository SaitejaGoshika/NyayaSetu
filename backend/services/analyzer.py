from __future__ import annotations

import re
from typing import TypedDict

from backend.models.schemas import RiskFinding, RiskLevel
from backend.services.rules import RULES, RULES_VERSION

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
_NUMBER_WORDS = sorted([*_TENS, *(f"{tens} {one}" for tens in _TENS for one in _ONES)], key=len, reverse=True)
_NUMBER_PATTERN = "|".join(re.escape(value).replace(r"\ ", r"[\s-]+") for value in _NUMBER_WORDS)
_DURATION_PATTERN = re.compile(
    rf"\b(?P<amount>\d{{1,4}}|{_NUMBER_PATTERN})(?:\s*\(\s*(?P<alt>\d{{1,4}})\s*\))?\s*(?:(?:calendar|working|business)\s+)?(?P<unit>days?|weeks?|months?)\b",
    flags=re.IGNORECASE,
)
_NET_PATTERN = re.compile(
    rf"\bnet\s*[- ]?\s*(?P<amount>\d{{1,4}}|{_NUMBER_PATTERN})\b",
    flags=re.IGNORECASE,
)
_PAYMENT_PATTERN = re.compile(r"\b(?:payment|payments|payable|invoice|invoices|settle|settlement|due|pay|paid|paying|pays)\b", re.IGNORECASE)
_CLAUSE_PATTERN = re.compile(r"[^.!?;\n]+(?:[.!?;]|$)")
_NEGATIVE_CONTEXT = re.compile(r"\b(?:terminate|termination|notice|warranty|validity|cure)\b", re.IGNORECASE)
_PAYMENT_EXPLANATION = (
    "For a qualifying micro or small enterprise supplier, the agreed payment period cannot exceed 45 days "
    "from acceptance or deemed acceptance under Sections 15-16 of the MSMED Act, 2006. Confirm supplier "
    "eligibility, the applicable start date, and the complete clause with qualified counsel."
)


def _duration_days(value: str) -> int | None:
    normalized = value.strip().lower().replace("-", " ").replace("(", "").replace(")", "")
    if not normalized:
        return None
    if normalized.isdigit():
        return int(normalized)
    if normalized in _TENS:
        return _TENS[normalized]
    if normalized in _ONES:
        return _ONES[normalized]
    parts = normalized.split()
    if len(parts) == 2 and parts[0] in _TENS and parts[1] in _ONES:
        return _TENS[parts[0]] + _ONES[parts[1]]
    return None


def _duration_in_days(amount: str, unit: str) -> int | None:
    value = _duration_days(amount)
    if value is None:
        return None
    unit_l = unit.lower()
    if unit_l.startswith("day"):
        return value
    if unit_l.startswith("week"):
        return value * 7
    if unit_l.startswith("month"):
        return value * 30
    return None


def _text_span_in_clause(clause: str, match: re.Match[str]) -> tuple[int, int]:
    start = clause.find(match.group(0))
    if start < 0:
        return (0, len(clause))
    return (start, start + len(match.group(0)))


def _negative_window(clause: str, start: int, end: int) -> bool:
    window = clause[max(0, start - 45) : min(len(clause), end + 45)]
    return bool(_NEGATIVE_CONTEXT.search(window))


def _normalize_amount_words(value: str) -> str:
    return value.strip().lower().replace("-", " ")


def _payment_duration_candidates(clause: str) -> list[tuple[str, int, int, int]]:
    candidates: list[tuple[str, int, int, int]] = []
    for match in _DURATION_PATTERN.finditer(clause):
        alt = match.group("alt")
        amount = alt or match.group("amount")
        unit = match.group("unit")
        duration_days = _duration_in_days(amount, unit)
        if duration_days is None:
            continue
        start, end = _text_span_in_clause(clause, match)
        if _negative_window(clause, start, end):
            continue
        candidates.append((match.group(0).strip(), duration_days, start, end))
    for match in _NET_PATTERN.finditer(clause):
        amount = match.group("amount")
        duration_days = _duration_days(amount)
        if duration_days is None:
            continue
        start, end = _text_span_in_clause(clause, match)
        if _negative_window(clause, start, end):
            continue
        candidates.append((match.group(0).strip(), duration_days, start, end))
    deduped: list[tuple[str, int, int, int]] = []
    for candidate in sorted(candidates, key=lambda item: item[2]):
        if not deduped:
            deduped.append(candidate)
            continue
        previous_text, previous_days, previous_start, previous_end = deduped[-1]
        if candidate[2] <= previous_end + 8 and abs(candidate[1] - previous_days) <= 1:
            merged_text = clause[previous_start : candidate[3]]
            deduped[-1] = (merged_text.strip(), candidate[1], previous_start, candidate[3])
        else:
            deduped.append(candidate)
    return deduped


def split_clauses(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    blocks = [segment.strip() for segment in re.split(r"\n\s*\n+", text) if segment.strip()]
    if not blocks:
        return [text.strip()]
    clauses: list[str] = []
    for block in blocks:
        subclauses = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", block)
        for subclause in subclauses:
            cleaned = subclause.strip()
            if cleaned:
                clauses.append(cleaned)
    return clauses or blocks


def _assign_clause_indices(text: str, findings: list[RiskFinding]) -> None:
    clauses = split_clauses(text)
    clause_ranges: list[tuple[int, int]] = []
    cursor = 0
    for clause in clauses:
        start = text.find(clause, cursor)
        if start < 0:
            start = cursor
        end = start + len(clause)
        clause_ranges.append((start, end))
        cursor = end
    for finding in findings:
        best_index = None
        best_overlap = -1
        for index, (start, end) in enumerate(clause_ranges):
            overlap = min(finding.end, end) - max(finding.start, start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_index = index
        if best_index is not None:
            finding.clause_index = best_index


def _payment_findings(text: str) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    search_start = 0
    while search_start < len(text):
        clause_match = _CLAUSE_PATTERN.search(text, search_start)
        if clause_match is None:
            break
        clause = clause_match.group(0).strip()
        clause_start = clause_match.start()
        if not _PAYMENT_PATTERN.search(clause):
            search_start = clause_match.end()
            continue
        for idx, (match_text, duration_days, local_start, local_end) in enumerate(_payment_duration_candidates(clause), start=1):
            if duration_days <= 45:
                continue
            findings.append(
                RiskFinding(
                    id=f"msme-payment-{len(findings) + 1}",
                    title="Payment term may exceed 45 days",
                    risk_level=RiskLevel.HIGH,
                    legal_basis="MSMED Act, 2006, Sections 15-16",
                    explanation=_PAYMENT_EXPLANATION,
                    match_text=match_text,
                    start=clause_start + local_start,
                    end=clause_start + local_end,
                )
            )
        search_start = clause_match.end()
    return findings


def _sort_findings(findings: list[RiskFinding]) -> list[RiskFinding]:
    severity_order = {RiskLevel.HIGH: 0, RiskLevel.MEDIUM: 1, RiskLevel.LOW: 2}
    return sorted(findings, key=lambda finding: (severity_order.get(finding.risk_level, 99), finding.start, finding.end, finding.id))


def _rule_occurrence_ids(text: str) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    counts: dict[str, int] = {}
    for rule in RULES:
        if rule.id == "msme-payment":
            continue
        rule_id = rule.id
        for match in re.finditer(rule.patterns[0] if len(rule.patterns) == 1 else "|".join(f"(?:{pattern})" for pattern in rule.patterns), text, flags=re.IGNORECASE | re.DOTALL):
            counts[rule_id] = counts.get(rule_id, 0) + 1
            findings.append(
                RiskFinding(
                    id=f"{rule_id}-{counts[rule_id]}",
                    title=rule.title,
                    risk_level=RiskLevel(rule.severity),
                    legal_basis=rule.legal_basis,
                    explanation=rule.explanation,
                    match_text=match.group(0).strip(),
                    start=match.start(),
                    end=match.end(),
                    status=rule.status,
                    reviewed_by=rule.reviewed_by,
                    what_to_ask=rule.what_to_ask,
                    needs_citation_check=rule.needs_citation_check,
                )
            )
    return findings


def analyze_text(text: str) -> list[RiskFinding]:
    findings = _payment_findings(text)
    findings.extend(_rule_occurrence_ids(text))
    _assign_clause_indices(text, findings)
    return _sort_findings(findings)
