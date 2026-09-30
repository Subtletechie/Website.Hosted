"""Pipeline stages. Each one reads/writes the run folder so it can be re-run on its own.

collect -> inventory.json + coverage.json
analyze -> findings.json (checks, then scoring)
report  -> report.md (see subtlescan.report)
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from subtlescan import __version__, runfolder
from subtlescan.checks.runner import run_checks
from subtlescan.collectors.azure import COLLECTORS, collect_all
from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.base import CollectContext
from subtlescan.inventory import Inventory
from subtlescan.models import Provider, Run
from subtlescan.runlog import log
from subtlescan.scoring import score_all


def collect_azure(run_dir: Path, client: str, ctx: AzureContext, subscriptions: list[str] | None) -> Run:
    run = Run(
        client=client,
        provider=Provider.AZURE,
        started_at=datetime.now(UTC),
        tool_version=__version__,
        tenant_id=ctx.tenant_id,
    )
    subs = ctx.discover_subscriptions(subscriptions)
    log.info("scanning %d subscription(s)", len(subs), extra={"event": "scope", "subscriptions": subs})
    inv = Inventory(collect_all(ctx) if subs else [])
    inv.save(run_dir)
    runfolder.write_coverage(run_dir, ctx.gaps)
    run.scopes = subs
    run.services_scanned = list(COLLECTORS)
    run.asset_count = len(inv)
    runfolder.write_run(run_dir, run)
    return run


def analyze(run_dir: Path) -> Run:
    run = runfolder.read_run(run_dir)
    inv = Inventory.load(run_dir)
    # Re-running analyze must not duplicate check-stage gaps from a previous analyze.
    collect_gaps = [g for g in runfolder.read_coverage(run_dir) if not g.service.startswith("check:")]
    ctx = CollectContext(provider=run.provider, gaps=collect_gaps)
    findings = score_all(run_checks(inv, run.provider, ctx), inv.assets)
    runfolder.write_findings(run_dir, findings)
    runfolder.write_coverage(run_dir, ctx.gaps)
    run.finding_count = len(findings)
    run.finished_at = datetime.now(UTC)
    runfolder.write_run(run_dir, run)
    log.info("%d finding(s), %d coverage gap(s)", len(findings), len(ctx.gaps), extra={"event": "analyze"})
    return run
