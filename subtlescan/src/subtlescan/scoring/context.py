"""SMB context scoring: score = base_severity x exposure x blast_radius x data_sensitivity."""

from __future__ import annotations

import re

from subtlescan.models import Asset, Finding, Severity

BASE: dict[Severity, float] = {
    Severity.CRITICAL: 10.0,
    Severity.HIGH: 7.0,
    Severity.MEDIUM: 4.0,
    Severity.LOW: 1.5,
    Severity.INFO: 0.0,
}
EXPOSED = 1.5
ADMIN_BLAST_RADIUS = 1.5
SENSITIVE_DATA = 1.3

SENSITIVE_WORDS = ("customer", "pii", "finance", "backup", "prod")
_SENSITIVE = re.compile("|".join(SENSITIVE_WORDS), re.IGNORECASE)

# Contextual score -> severity band. Calibrated so one factor alone does not jump a band but two
# stack: High x exposed (10.5) stays High, High x exposed x sensitive (13.65) is Critical;
# Medium x exposed (6.0) stays Medium, Medium x exposed x sensitive (7.8) is High.
BANDS: list[tuple[float, Severity]] = [
    (12.0, Severity.CRITICAL),
    (6.5, Severity.HIGH),
    (3.5, Severity.MEDIUM),
    (0.01, Severity.LOW),
]


def is_sensitive(asset: Asset) -> bool:
    haystack = [asset.name, asset.resource_group or ""]
    haystack += [f"{k}={v}" for k, v in asset.tags.items()]
    return any(_SENSITIVE.search(s) for s in haystack)


def context_factors(asset: Asset) -> dict[str, float]:
    return {
        "exposure": EXPOSED if asset.properties.get("internet_exposed") else 1.0,
        "blast_radius": ADMIN_BLAST_RADIUS if asset.properties.get("admin_scope") else 1.0,
        "data_sensitivity": SENSITIVE_DATA if is_sensitive(asset) else 1.0,
    }


def band(score: float) -> Severity:
    for threshold, sev in BANDS:
        if score >= threshold:
            return sev
    return Severity.INFO


def score_finding(finding: Finding, asset: Asset | None) -> Finding:
    """Apply context. Without an asset (imported/demo findings), keep any factors already recorded."""
    factors = context_factors(asset) if asset is not None else dict(finding.score_factors)
    score = BASE[finding.severity]
    for key in ("exposure", "blast_radius", "data_sensitivity"):
        score *= factors.setdefault(key, 1.0)
    score = round(score, 2)
    # Context can only raise severity: a Critical check stays Critical even with no multipliers.
    contextual = max(band(score), finding.severity, key=lambda s: s.rank)
    return finding.model_copy(update={"score": score, "score_factors": factors, "contextual_severity": contextual})


def score_all(findings: list[Finding], assets: list[Asset]) -> list[Finding]:
    by_id = {a.id.lower(): a for a in assets}
    scored = [score_finding(f, by_id.get(f.resource_id.lower())) for f in findings]
    return sorted(scored, key=lambda f: (-f.effective_severity.rank, -f.score, f.check_id, f.resource_name))
