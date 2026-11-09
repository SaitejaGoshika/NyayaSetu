from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

RULES_PATH = Path(__file__).resolve().parents[1] / "rules" / "contract_rules.yaml"


class RuleExample(BaseModel):
    text: str
    expected: bool = True


class RuleDefinition(BaseModel):
    id: str
    title: str
    category: str
    severity: str
    patterns: list[str] = Field(default_factory=list)
    legal_basis: str
    explanation: str
    what_to_ask: str
    status: str = "draft"
    reviewed_by: str | None = None
    reviewed_on: str | None = None
    needs_citation_check: bool = True
    examples_positive: list[str] = Field(default_factory=list)
    examples_negative: list[str] = Field(default_factory=list)

    def matches(self, text: str) -> bool:
        if not self.patterns:
            return False
        return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in self.patterns)


def load_rules() -> list[RuleDefinition]:
    if not RULES_PATH.exists():
        raise FileNotFoundError(f"Rules file not found: {RULES_PATH}")
    with RULES_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, list):
        raise ValueError("Rule file must contain a list of rules.")
    return [RuleDefinition.model_validate(item) for item in payload]


RULES = load_rules()
RULES_VERSION = "2026-11-09-rules-v1"
