from __future__ import annotations

import json
from pathlib import Path

from conftest import fake_context

from subtlescan import runfolder
from subtlescan.pipeline import analyze, collect_azure
from subtlescan.report.markdown import write_markdown
from subtlescan.report.view import build_view


def run_pipeline(tmp_path: Path) -> Path:
    run_dir = runfolder.new_run_dir(tmp_path / "runs", "Acme Corp")
    collect_azure(run_dir, "Acme Corp", fake_context(), None)
    analyze(run_dir)
    return run_dir


def test_end_to_end_storage(tmp_path: Path) -> None:
    run_dir = run_pipeline(tmp_path)
    assert run_dir.parent.name == "acme-corp"
    findings = runfolder.read_findings(run_dir)
    by_check = {(f.check_id, f.resource_name) for f in findings}
    assert ("AZ-STG-001", "acmecustomerdata") in by_check
    assert ("AZ-STG-001", "acmeoldfiles") in by_check  # unset = allowed
    assert ("AZ-STG-003", "acmecustomerdata") in by_check
    assert not any(f.resource_name == "acmelocked" for f in findings)

    public = next(f for f in findings if f.check_id == "AZ-STG-001" and f.resource_name == "acmecustomerdata")
    # High, internet-exposed, and name matches "customer" -> Critical.
    assert public.effective_severity.value == "critical"
    for f in findings:
        assert f.business_impact and f.remediation and f.frameworks and f.effort

    report = write_markdown(build_view(runfolder.load_run(run_dir), "soc2"), run_dir).read_text()
    assert "Cloud Security Assessment: Acme Corp" in report
    assert "storage.blob_service:acmeoldfiles" in report  # coverage gap surfaced
    assert "CC6.1" in report


def test_analyze_is_rerunnable(tmp_path: Path) -> None:
    run_dir = run_pipeline(tmp_path)
    first = (run_dir / "findings.json").read_text()
    gaps = json.loads((run_dir / "coverage.json").read_text())
    analyze(run_dir)
    assert json.loads((run_dir / "findings.json").read_text()) == json.loads(first)
    assert json.loads((run_dir / "coverage.json").read_text()) == gaps


def test_no_secret_values_or_external_state(tmp_path: Path) -> None:
    run_dir = run_pipeline(tmp_path)
    assert {p.name for p in run_dir.iterdir()} <= {
        "run.json",
        "inventory.json",
        "coverage.json",
        "findings.json",
        "report.md",
        "log.jsonl",
    }


def test_end_to_end_identity(tmp_path: Path) -> None:
    run_dir = run_pipeline(tmp_path)
    findings = runfolder.read_findings(run_dir)
    got = {f.check_id: f for f in findings}
    expected = {
        "ENTRA-ID-002",
        "ENTRA-ID-003",
        "ENTRA-ID-004",
        "ENTRA-ID-005",
        "ENTRA-ID-006",
        "ENTRA-ID-007",
        "ENTRA-ID-008",
        "ENTRA-APP-001",
        "ENTRA-APP-002",
        "AZ-IAM-001",
    }
    assert expected <= set(got)
    assert "ENTRA-ID-001" not in got  # an MFA-for-admins policy is enforced
    assert got["ENTRA-ID-008"].resource_name == "it.admin@acme.com"
    assert got["ENTRA-ID-003"].evidence["usersWithoutMfa"] == 2  # front.desk + it.admin; not the guest or leaver
    assert got["AZ-IAM-001"].resource_name == "github-deploy-prod"
    assert got["ENTRA-APP-002"].resource_name == "HR Sync"
    assert got["ENTRA-APP-001"].resource_name == "HR Sync"
    # Blast radius: an app that can read every mailbox is scored as admin-level.
    assert got["ENTRA-APP-002"].score_factors["blast_radius"] == 1.5
