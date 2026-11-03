from __future__ import annotations

import math
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class AnalysisResponse(ApiModel):
    document_id: str
    filename: str
    extracted_text: str
    findings: list[RiskFinding]


class DocumentUploadResponse(ApiModel):
    document_id: str
    filename: str
    created_at: str


class DocumentRecord(ApiModel):
    document_id: str
    filename: str
    created_at: str
    status: str


class CasePredictRequest(ApiModel):
    features: dict[str, float] = Field(min_length=1, max_length=100)

    @field_validator("features")
    @classmethod
    def validate_finite_features(cls, values: dict[str, float]) -> dict[str, float]:
        if any(not math.isfinite(value) for value in values.values()):
            raise ValueError("Every feature value must be finite.")
        return values


class CasePredictResponse(ApiModel):
    classes: list[str]
    probabilities: list[float]


class CasePredictStatus(ApiModel):
    available: bool
    message: str


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
