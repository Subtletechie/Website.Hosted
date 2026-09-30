from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, Field

from subtlescan.models.enums import Domain, Effort, Provider, Severity, Status


def finding_id(check_id: str, resource_id: str) -> str:
    """Stable id so overrides and run-to-run deltas survive rescans."""
    digest = hashlib.sha256(f"{check_id}|{resource_id.lower()}".encode()).hexdigest()[:10]
    return f"{check_id}-{digest}"


class Finding(BaseModel):
    id: str
    check_id: str
    title: str
    severity: Severity  # base severity from the check
    provider: Provider
    domain: Domain
    resource_id: str
    resource_name: str
    resource_type: str
    scope: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    business_impact: str
    remediation: str
    terraform_fix: str | None = None
    frameworks: dict[str, list[str]] = Field(default_factory=dict)
    effort: Effort
    source: str = "subtlescan"
    related_findings: list[str] = Field(default_factory=list)

    # Set by scoring.
    score: float = 0.0
    contextual_severity: Severity | None = None
    score_factors: dict[str, float] = Field(default_factory=dict)

    # Set by consultant overrides (runs/.../overrides.yaml).
    status: Status = Status.OPEN
    analyst_note: str | None = None

    @property
    def effective_severity(self) -> Severity:
        return self.contextual_severity or self.severity

    @property
    def is_open(self) -> bool:
        return self.status is Status.OPEN
