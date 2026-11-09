from __future__ import annotations

import difflib
import json
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.models.schemas import (
    CompareDocumentsRequest,
    CompareDocumentsResponse,
    ComparisonClause,
    ComparisonFinding,
)
from backend.services.analyzer import split_clauses
from backend.services.database import get_db

router = APIRouter(prefix="/api")


def _finding_signature(finding: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(finding.get("title", "")),
        str(finding.get("match_text", "")).strip(),
        int(finding.get("start", 0)),
        int(finding.get("end", 0)),
    )


def _comparison_entry(finding: dict[str, Any], change_type: str) -> ComparisonFinding:
    risk_level = finding.get("riskLevel") or finding.get("risk_level") or "low"
    return ComparisonFinding(
        id=str(finding.get("id", "unknown")),
        title=str(finding.get("title", "")),
        risk_level=risk_level,
        legal_basis=str(finding.get("legalBasis") or finding.get("legal_basis") or ""),
        explanation=str(finding.get("explanation", "")),
        match_text=str(finding.get("matchText") or finding.get("match_text") or ""),
        clause_index=finding.get("clauseIndex") if "clauseIndex" in finding else finding.get("clause_index"),
        change_type=change_type,
    )


@router.post("/compare", response_model=CompareDocumentsResponse)
def compare_documents(
    payload: CompareDocumentsRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> CompareDocumentsResponse:
    uid = str(current_user["uid"])
    primary = db.execute(
        "SELECT document_id, filename FROM documents WHERE document_id = ? AND owner_uid = ?",
        (payload.primary_document_id, uid),
    ).fetchone()
    secondary = db.execute(
        "SELECT document_id, filename FROM documents WHERE document_id = ? AND owner_uid = ?",
        (payload.secondary_document_id, uid),
    ).fetchone()
    if primary is None or secondary is None:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "The requested document was not found."})

    primary_analysis = db.execute(
        "SELECT extracted_text, findings_json FROM analyses WHERE document_id = ? AND owner_uid = ? ORDER BY created_at DESC LIMIT 1",
        (payload.primary_document_id, uid),
    ).fetchone()
    secondary_analysis = db.execute(
        "SELECT extracted_text, findings_json FROM analyses WHERE document_id = ? AND owner_uid = ? ORDER BY created_at DESC LIMIT 1",
        (payload.secondary_document_id, uid),
    ).fetchone()
    if primary_analysis is None or secondary_analysis is None:
        raise HTTPException(status_code=404, detail={"code": "analysis_not_found", "message": "No analysis is available for one of the selected documents."})

    primary_findings = json.loads(primary_analysis["findings_json"])
    secondary_findings = json.loads(secondary_analysis["findings_json"])
    primary_by_key = {_finding_signature(finding): finding for finding in primary_findings}
    secondary_by_key = {_finding_signature(finding): finding for finding in secondary_findings}

    new_findings = []
    removed_findings = []
    unchanged_findings = []
    severity_changed = []
    seen: set[tuple[str, str, int, int]] = set()

    for key in sorted(set(primary_by_key) | set(secondary_by_key)):
        primary_finding = primary_by_key.get(key)
        secondary_finding = secondary_by_key.get(key)
        if primary_finding is None and secondary_finding is not None:
            new_findings.append(_comparison_entry(secondary_finding, "new"))
            seen.add(key)
        elif secondary_finding is None and primary_finding is not None:
            removed_findings.append(_comparison_entry(primary_finding, "removed"))
            seen.add(key)
        elif primary_finding is not None and secondary_finding is not None:
            primary_risk = (primary_finding.get("riskLevel") or primary_finding.get("risk_level") or "low")
            secondary_risk = (secondary_finding.get("riskLevel") or secondary_finding.get("risk_level") or "low")
            if primary_risk == secondary_risk:
                unchanged_findings.append(_comparison_entry(secondary_finding, "unchanged"))
            else:
                severity_changed.append(_comparison_entry(secondary_finding, "severity_changed"))
            seen.add(key)

    primary_clauses = split_clauses(str(primary_analysis["extracted_text"]))
    secondary_clauses = split_clauses(str(secondary_analysis["extracted_text"]))
    comparator = difflib.SequenceMatcher(None, primary_clauses, secondary_clauses)
    changed_clauses: list[ComparisonClause] = []
    for tag, i1, i2, j1, j2 in comparator.get_opcodes():
        if tag == "equal":
            continue
        primary_slice = "\n".join(primary_clauses[i1:i2]) if i2 > i1 else ""
        secondary_slice = "\n".join(secondary_clauses[j1:j2]) if j2 > j1 else ""
        clause_index = max(i1, j1, 0)
        changed_clauses.append(
            ComparisonClause(
                clause_index=clause_index,
                primary_clause=primary_slice,
                secondary_clause=secondary_slice,
                change_type=tag,
            )
        )

    return CompareDocumentsResponse(
        primary_document_id=payload.primary_document_id,
        secondary_document_id=payload.secondary_document_id,
        new_findings=new_findings,
        removed_findings=removed_findings,
        unchanged_findings=unchanged_findings,
        severity_changed=severity_changed,
        changed_clauses=changed_clauses,
    )
