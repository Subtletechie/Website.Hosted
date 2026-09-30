"""Demo runs for developing and presenting the UI without a live tenant. All data is fictional."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from subtlescan import __version__, runfolder
from subtlescan.models import CoverageGap, Finding, Provider, Run, finding_id
from subtlescan.scoring import score_finding

PREVIOUS_RUN_OFFSET = timedelta(days=45)


def _resource_id(resource: str, subscription: str, tenant: str) -> tuple[str, str, str, Provider]:
    """-> (resource_id, name, type, provider)"""
    head, _, rest = resource.partition("/")
    if head == "entra":
        kind, _, name = rest.partition("/")
        return f"tenants/{tenant}/{kind}/{name}", name, f"entra.{kind}", Provider.ENTRA
    if head == "sub":
        return f"/subscriptions/{rest}", rest, "azure.subscription", Provider.AZURE
    ns, rtype, name = rest.split("/")
    rid = f"/subscriptions/{subscription}/resourceGroups/{head}/providers/{ns}/{rtype}/{name}"
    return rid, name, f"azure.{rtype}", Provider.AZURE


def _load() -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load((resources.files(__package__) / "findings.yaml").read_text())
    return data


def demo_findings(previous: bool) -> list[Finding]:
    data = _load()
    sub, tenant = data["subscriptions"][0], data["tenant"]
    out: list[Finding] = []
    for raw in data["findings"]:
        if (previous and raw.get("prev") is False) or (not previous and raw.get("fixed")):
            continue
        rid, name, rtype, provider = _resource_id(raw["resource"], sub, tenant)
        f = Finding(
            id=finding_id(raw["check_id"], rid),
            check_id=raw["check_id"],
            title=raw["title"],
            severity=raw["severity"],
            provider=provider,
            domain=raw["domain"],
            resource_id=rid,
            resource_name=name,
            resource_type=rtype,
            scope=tenant if provider is Provider.ENTRA else sub,
            evidence=raw.get("evidence", {}),
            business_impact=raw["business_impact"],
            remediation=raw["remediation"],
            terraform_fix=raw.get("terraform_fix"),
            frameworks=raw.get("frameworks", {}),
            effort=raw["effort"],
            score_factors=raw.get("factors", {}),
        )
        out.append(score_finding(f, None))
    ids = {f.check_id: f.id for f in out}
    for f in out:
        if f.check_id.startswith("COMBO-"):
            raw = next(r for r in data["findings"] if r["check_id"] == f.check_id)
            f.related_findings = [ids[c] for c in raw.get("related", []) if c in ids]
    return sorted(out, key=lambda f: (-f.effective_severity.rank, -f.score))


def _write(root: Path, when: datetime, previous: bool) -> Path:
    data = _load()
    run_dir = runfolder.new_run_dir(root, data["client"], when)
    findings = demo_findings(previous)
    run = Run(
        client=data["client"],
        provider=Provider.AZURE,
        started_at=when,
        finished_at=when + timedelta(minutes=6),
        tool_version=__version__,
        tenant_id=data["tenant"],
        scopes=data["subscriptions"],
        services_scanned=["storage", "network", "compute", "keyvault", "sql", "web", "monitor", "recovery", "entra"],
        asset_count=data["asset_count"],
        finding_count=len(findings),
    )
    runfolder.write_run(run_dir, run)
    runfolder.write_inventory(run_dir, [])
    runfolder.write_findings(run_dir, findings)
    runfolder.write_coverage(run_dir, [CoverageGap.model_validate(g) for g in data["coverage"]])
    if not previous:
        by_check = {f.check_id: f.id for f in findings}
        overrides = {by_check[c]: o for c, o in data["overrides"].items() if c in by_check}
        (run_dir / runfolder.OVERRIDES_FILE).write_text(
            "# Consultant overrides: finding id -> status (open | accepted_risk | false_positive) + analyst_note\n"
            + yaml.safe_dump(overrides, sort_keys=False, width=100)
        )
    return run_dir


def write_demo_runs(root: Path, now: datetime | None = None) -> Path:
    """Write a previous and a current demo run. Returns the current run folder."""
    now = (now or datetime.now(UTC)).replace(microsecond=0)
    _write(root, now - PREVIOUS_RUN_OFFSET, previous=True)
    return _write(root, now, previous=False)
