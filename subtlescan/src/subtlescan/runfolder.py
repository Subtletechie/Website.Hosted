"""Run folder I/O. Every pipeline stage reads and writes JSON here so stages can re-run alone.

runs/<client>/<timestamp>/
  run.json          run metadata
  inventory.json    normalized assets (collect)
  coverage.json     coverage gaps (collect + checks)
  findings.json     scored findings (checks + scoring)
  overrides.yaml    consultant status / analyst_note per finding id (hand-edited)
  log.jsonl         structured log
  report.md         rendered report
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import TypeAdapter

from subtlescan.models import Asset, CoverageGap, Finding, Run, Status

RUN_FILE = "run.json"
INVENTORY_FILE = "inventory.json"
COVERAGE_FILE = "coverage.json"
FINDINGS_FILE = "findings.json"
OVERRIDES_FILE = "overrides.yaml"
LOG_FILE = "log.jsonl"

_TS_FORMAT = "%Y-%m-%dT%H%M%SZ"
_SLUG = re.compile(r"[^a-z0-9-]+")

_assets = TypeAdapter(list[Asset])
_gaps = TypeAdapter(list[CoverageGap])
_findings = TypeAdapter(list[Finding])


def slugify(client: str) -> str:
    slug = _SLUG.sub("-", client.lower()).strip("-")
    if not slug:
        raise ValueError(f"client name {client!r} has no usable characters")
    return slug


def new_run_dir(root: Path, client: str, now: datetime | None = None) -> Path:
    stamp = (now or datetime.now(UTC)).strftime(_TS_FORMAT)
    path = root / slugify(client) / stamp
    path.mkdir(parents=True, exist_ok=False)
    return path


def _write(path: Path, data: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def write_run(run_dir: Path, run: Run) -> None:
    _write(run_dir / RUN_FILE, run.model_dump_json(indent=2).encode())


def read_run(run_dir: Path) -> Run:
    return Run.model_validate_json((run_dir / RUN_FILE).read_bytes())


def write_inventory(run_dir: Path, assets: list[Asset]) -> None:
    _write(run_dir / INVENTORY_FILE, _assets.dump_json(assets, indent=2))


def read_inventory(run_dir: Path) -> list[Asset]:
    return _assets.validate_json((run_dir / INVENTORY_FILE).read_bytes())


def write_coverage(run_dir: Path, gaps: list[CoverageGap]) -> None:
    _write(run_dir / COVERAGE_FILE, _gaps.dump_json(gaps, indent=2))


def read_coverage(run_dir: Path) -> list[CoverageGap]:
    path = run_dir / COVERAGE_FILE
    return _gaps.validate_json(path.read_bytes()) if path.exists() else []


def write_findings(run_dir: Path, findings: list[Finding]) -> None:
    _write(run_dir / FINDINGS_FILE, _findings.dump_json(findings, indent=2))


def read_findings(run_dir: Path) -> list[Finding]:
    """Findings as stored by the pipeline, before consultant overrides."""
    return _findings.validate_json((run_dir / FINDINGS_FILE).read_bytes())


def read_overrides(run_dir: Path) -> dict[str, dict[str, Any]]:
    path = run_dir / OVERRIDES_FILE
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping of finding id -> {{status, analyst_note}}")
    return {str(k): (v or {}) for k, v in data.items()}


def apply_overrides(findings: list[Finding], overrides: dict[str, dict[str, Any]]) -> list[Finding]:
    out = []
    for f in findings:
        o = overrides.get(f.id)
        if o:
            f = f.model_copy(
                update={
                    "status": Status(o.get("status", f.status)),
                    "analyst_note": o.get("analyst_note", f.analyst_note),
                }
            )
        out.append(f)
    return out


def previous_run_dir(run_dir: Path) -> Path | None:
    """The most recent earlier run for the same client that has findings, if any."""
    siblings = sorted(
        p for p in run_dir.parent.iterdir() if p.is_dir() and p.name < run_dir.name and (p / FINDINGS_FILE).exists()
    )
    return siblings[-1] if siblings else None


@dataclass
class RunData:
    """Everything the report and UI need, with overrides applied."""

    path: Path
    run: Run
    findings: list[Finding]
    coverage: list[CoverageGap]
    previous: list[Finding] | None


def load_run(run_dir: Path) -> RunData:
    run_dir = run_dir.resolve()
    if not (run_dir / FINDINGS_FILE).exists():
        raise FileNotFoundError(f"{run_dir} has no {FINDINGS_FILE}; run `subtlescan scan` first")
    findings = apply_overrides(read_findings(run_dir), read_overrides(run_dir))
    prev_dir = previous_run_dir(run_dir)
    previous = apply_overrides(read_findings(prev_dir), read_overrides(prev_dir)) if prev_dir else None
    return RunData(
        path=run_dir,
        run=read_run(run_dir),
        findings=findings,
        coverage=read_coverage(run_dir),
        previous=previous,
    )


def dump_json(path: Path, data: Any) -> None:
    _write(path, json.dumps(data, indent=2, default=str).encode())
