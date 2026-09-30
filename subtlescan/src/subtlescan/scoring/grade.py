"""Overall grade for the executive summary, plus roadmap bucketing and run-to-run delta."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from subtlescan.models import Effort, Finding, Severity

# Penalty points at which the score has fallen to ~37/100. Tuned so a typical SMB first
# assessment (a few criticals, a handful of highs) lands around D/F and a cleaned-up
# environment with only low findings lands at A/B.
DECAY = 120.0

GRADES: list[tuple[int, str]] = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "F")]

Bucket = Literal["week", "30d", "90d"]
BUCKET_LABELS: dict[Bucket, str] = {"week": "This week", "30d": "Next 30 days", "90d": "Next 90 days"}


@dataclass(frozen=True)
class Grade:
    score: int  # 0-100, higher is better
    letter: str
    open_count: int


def grade(findings: list[Finding]) -> Grade:
    open_findings = [f for f in findings if f.is_open]
    penalty = sum(f.score for f in open_findings)
    score = round(100 * math.exp(-penalty / DECAY))
    letter = next(letter for floor, letter in GRADES if score >= floor)
    # An open Critical caps the grade at C: a good average must not hide a live exposure.
    if letter in ("A", "B") and any(f.effective_severity is Severity.CRITICAL for f in open_findings):
        letter = "C"
    return Grade(score=score, letter=letter, open_count=len(open_findings))


def roadmap_bucket(f: Finding) -> Bucket:
    sev = f.effective_severity
    if sev is Severity.CRITICAL or (sev is Severity.HIGH and f.effort is Effort.S):
        return "week"
    if sev is Severity.HIGH or (sev is Severity.MEDIUM and f.effort is Effort.S):
        return "30d"
    return "90d"


@dataclass(frozen=True)
class Delta:
    new: int
    resolved: int
    previous_grade: Grade


def delta(current: list[Finding], previous: list[Finding]) -> Delta:
    cur = {f.id for f in current if f.is_open}
    prev = {f.id for f in previous if f.is_open}
    return Delta(new=len(cur - prev), resolved=len(prev - cur), previous_grade=grade(previous))
