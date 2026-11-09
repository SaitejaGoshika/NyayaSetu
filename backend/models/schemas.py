from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskFinding(ApiModel):
    id: str
    title: str
    risk_level: RiskLevel
    legal_basis: str
    explanation: str
    match_text: str
    start: int
    end: int
    clause_index: int | None = None
    status: str | None = None
    reviewed_by: str | None = None
    what_to_ask: str | None = None
    needs_citation_check: bool = False


class AnalysisResponse(ApiModel):
    document_id: str
    filename: str
    extracted_text: str
    findings: list[RiskFinding]
    rules_version: str


class DocumentUploadResponse(ApiModel):
    document_id: str
    filename: str
    created_at: str


class DocumentRecord(ApiModel):
    document_id: str
    filename: str
    created_at: str
    status: str


class MsmeInterestRequest(BaseModel):
    amount: float = Field(gt=0)
    acceptance_date: str
    has_written_payment_period: bool = False
    written_payment_period_days: int | None = Field(default=None, ge=0, le=45)
    payment_date: str | None = None
    as_of_date: str | None = None
    bank_rate_percent: float = Field(default=6.5, ge=0)


class MsmeInterestRow(ApiModel):
    month_label: str
    days_in_month: int
    interest: float
    ending_balance: float


class MsmeInterestResponse(ApiModel):
    due_date: str
    payment_due_days: int
    days_delayed: int
    total_interest: float
    monthly_breakdown: list[MsmeInterestRow]


class SignupRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")

    display_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class AuthUser(ApiModel):
    uid: str
    email: str
    display_name: str


class AuthSessionResponse(ApiModel):
    user: AuthUser


class ApiErrorDetail(ApiModel):
    code: str
    message: str


class ApiErrorResponse(ApiModel):
    detail: ApiErrorDetail | list[dict[str, Any]]


class CompareDocumentsRequest(ApiModel):
    primary_document_id: str
    secondary_document_id: str


class ComparisonFinding(ApiModel):
    id: str
    title: str
    risk_level: RiskLevel
    legal_basis: str
    explanation: str
    match_text: str
    clause_index: int | None = None
    change_type: str


class ComparisonClause(ApiModel):
    clause_index: int
    primary_clause: str
    secondary_clause: str
    change_type: str


class CompareDocumentsResponse(ApiModel):
    primary_document_id: str
    secondary_document_id: str
    new_findings: list[ComparisonFinding]
    removed_findings: list[ComparisonFinding]
    unchanged_findings: list[ComparisonFinding]
    severity_changed: list[ComparisonFinding]
    changed_clauses: list[ComparisonClause]


class FindingExplanationRequest(ApiModel):
    finding_title: str
    finding_text: str
    document_text: str


class FindingExplanationResponse(ApiModel):
    explanation: str
    citations: list[str]
    grounded: bool
