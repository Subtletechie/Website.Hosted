"""One view model for the Markdown report, the local UI, and the static export."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from subtlescan.frameworks import Framework, load_frameworks
from subtlescan.models import CoverageGap, Domain, Finding, Run, Severity, Status
from subtlescan.runfolder import RunData
from subtlescan.scoring import BUCKET_LABELS, Delta, Grade, delta, grade, roadmap_bucket

SEVERITIES = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]


@dataclass
class Brand:
    name: str = "Subtletech"
    accent: str = "#2563eb"
    logo: str = "logo.svg"
    tagline: str = "Cloud Security Assessment"
    contact: str = ""

    @classmethod
    def load(cls, path: Path) -> Brand:
        data = yaml.safe_load(path.read_text()) if path.exists() else {}
        return cls(**{k: str(v) for k, v in (data or {}).items() if k in cls.__dataclass_fields__})


@dataclass
class View:
    run: Run
    findings: list[Finding]
    open_findings: list[Finding]
    coverage: list[CoverageGap]
    grade: Grade
    severity_counts: dict[Severity, int]
    domain_counts: dict[Domain, int]
    top_risks: list[Finding]
    delta: Delta | None
    roadmap: dict[str, list[Finding]]
    frameworks: dict[str, Framework]
    selected_framework: Framework | None
    domains: list[Domain] = field(default_factory=lambda: list(Domain))
    statuses: list[Status] = field(default_factory=lambda: list(Status))
    severities: list[Severity] = field(default_factory=lambda: list(SEVERITIES))
    bucket_labels: dict[str, str] = field(default_factory=lambda: dict(BUCKET_LABELS))


def build_view(data: RunData, framework: str | None = None) -> View:
    frameworks = load_frameworks()
    if framework is not None and framework not in frameworks:
        raise ValueError(f"unknown framework {framework!r}; choose from {', '.join(sorted(frameworks))}")
    findings = sorted(data.findings, key=lambda f: (-f.effective_severity.rank, -f.score, f.title))
    open_findings = [f for f in findings if f.is_open]
    counts = Counter(f.effective_severity for f in open_findings)
    roadmap: dict[str, list[Finding]] = {b: [] for b in BUCKET_LABELS}
    for f in open_findings:
        roadmap[roadmap_bucket(f)].append(f)
    return View(
        run=data.run,
        findings=findings,
        open_findings=open_findings,
        coverage=data.coverage,
        grade=grade(findings),
        severity_counts={s: counts.get(s, 0) for s in SEVERITIES},
        domain_counts={d: sum(1 for f in open_findings if f.domain is d) for d in Domain},
        top_risks=open_findings[:5],
        delta=delta(findings, data.previous) if data.previous is not None else None,
        roadmap=roadmap,
        frameworks=frameworks,
        selected_framework=frameworks[framework] if framework else None,
    )
