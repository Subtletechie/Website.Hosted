from __future__ import annotations

from conftest import storage_asset

from subtlescan.models import Domain, Effort, Finding, Provider, Severity, Status
from subtlescan.scoring import delta, grade, roadmap_bucket, score_finding


def finding(sev: Severity = Severity.HIGH, effort: Effort = Effort.S, fid: str = "X-1", **kw: object) -> Finding:
    return Finding(
        id=fid,
        check_id="X",
        title="t",
        severity=sev,
        provider=Provider.AZURE,
        domain=Domain.DATA,
        resource_id="r",
        resource_name="r",
        resource_type="t",
        scope="s",
        business_impact="b",
        remediation="r",
        effort=effort,
        **kw,
    )


def test_context_multipliers_stack() -> None:
    plain = score_finding(finding(), storage_asset("plain"))
    assert plain.score == 7.0 and plain.contextual_severity is Severity.HIGH

    exposed = score_finding(finding(), storage_asset("plain", internet_exposed=True))
    assert exposed.score == 10.5 and exposed.contextual_severity is Severity.HIGH

    exposed_sensitive = score_finding(finding(), storage_asset("customerexports", internet_exposed=True))
    assert exposed_sensitive.score == 13.65 and exposed_sensitive.contextual_severity is Severity.CRITICAL


def test_context_never_lowers_severity() -> None:
    assert score_finding(finding(Severity.CRITICAL), None).contextual_severity is Severity.CRITICAL


def test_sensitivity_from_tags() -> None:
    a = storage_asset("x")
    a.tags = {"data": "PII"}
    assert score_finding(finding(Severity.MEDIUM), a).score_factors["data_sensitivity"] == 1.3


def test_grade_bounds_and_critical_cap() -> None:
    assert grade([]).letter == "A" and grade([]).score == 100
    one_crit = score_finding(finding(Severity.CRITICAL), None)
    assert grade([one_crit]).letter == "C"  # score alone would be B
    many = [score_finding(finding(Severity.HIGH, fid=f"X-{i}"), None) for i in range(20)]
    assert grade(many).letter == "F"


def test_accepted_risk_excluded_from_grade() -> None:
    f = score_finding(finding(Severity.CRITICAL), None).model_copy(update={"status": Status.ACCEPTED_RISK})
    assert grade([f]).score == 100


def test_roadmap_buckets() -> None:
    assert roadmap_bucket(score_finding(finding(Severity.CRITICAL, Effort.L), None)) == "week"
    assert roadmap_bucket(score_finding(finding(Severity.HIGH, Effort.S), None)) == "week"
    assert roadmap_bucket(score_finding(finding(Severity.HIGH, Effort.L), None)) == "30d"
    assert roadmap_bucket(score_finding(finding(Severity.MEDIUM, Effort.M), None)) == "90d"


def test_delta() -> None:
    a, b, c = (score_finding(finding(fid=i), None) for i in ("a", "b", "c"))
    d = delta([a, b], [b, c])
    assert (d.new, d.resolved) == (1, 1)
