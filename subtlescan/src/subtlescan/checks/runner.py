"""Run registered checks over an inventory and turn hits into full findings."""

from __future__ import annotations

from subtlescan.checks.registry import CheckSpec, Hit, checks_for
from subtlescan.collectors.base import CollectContext
from subtlescan.frameworks import mappings_for
from subtlescan.inventory import Inventory
from subtlescan.library import LibraryEntry, load_library
from subtlescan.models import Finding, GapReason, Provider, finding_id
from subtlescan.runlog import log


def run_checks(inv: Inventory, providers: set[Provider], ctx: CollectContext) -> list[Finding]:
    library = load_library()
    findings: list[Finding] = []
    for spec in (c for p in sorted(providers) for c in checks_for(p)):
        entry = library.get(spec.id)
        if entry is None:
            raise KeyError(f"check {spec.id} has no library/*.yaml entry")
        try:
            hits = spec.fn(inv)
        except Exception as exc:  # noqa: BLE001 - one broken check must not sink the run
            ctx.gap("*", f"check:{spec.id}", GapReason.ERROR, f"{type(exc).__name__}: {exc}")
            continue
        log.info("%s: %d finding(s)", spec.id, len(hits), extra={"event": "check", "check_id": spec.id})
        findings.extend(_to_finding(spec, h, entry) for h in hits)
    return findings


def _to_finding(spec: CheckSpec, hit: Hit, entry: LibraryEntry) -> Finding:
    resource = hit.resource
    return Finding(
        id=finding_id(spec.id, resource.id),
        check_id=spec.id,
        title=entry.title,
        severity=spec.severity,
        provider=spec.provider,
        domain=spec.domain,
        resource_id=resource.id,
        resource_name=hit.name or resource.name,
        resource_type=resource.type,
        scope=resource.scope,
        evidence=hit.evidence,
        business_impact=entry.business_impact.strip(),
        remediation=entry.remediation.strip(),
        terraform_fix=entry.terraform_fix.strip() if entry.terraform_fix else None,
        frameworks=mappings_for(spec.id),
        effort=entry.effort,
    )
