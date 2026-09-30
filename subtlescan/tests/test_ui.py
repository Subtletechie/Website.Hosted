from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from subtlescan import runfolder
from subtlescan.cli import app as cli
from subtlescan.demo import write_demo_runs
from subtlescan.ui.app import create_app
from subtlescan.ui.export import export_html


@pytest.fixture
def demo_run(tmp_path: Path) -> Path:
    return write_demo_runs(tmp_path / "runs")


def test_demo_has_realistic_volume(demo_run: Path) -> None:
    data = runfolder.load_run(demo_run)
    assert 25 <= len(data.findings) <= 40
    assert data.previous is not None
    assert {f.domain.value for f in data.findings} == {"identity", "network", "data", "logging", "recovery", "secrets"}


def test_export_is_self_contained(demo_run: Path, tmp_path: Path) -> None:
    html = export_html(demo_run, tmp_path / "out.html").read_text()
    assert "Content-Security-Policy" in html and "default-src 'none'" in html
    # No external resources of any kind.
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html)
    assert '<link rel="stylesheet"' not in html
    assert "Northwind Dental Group" in html
    assert "data leaves" in html or "never left" in html


def test_overrides_are_respected(demo_run: Path, tmp_path: Path) -> None:
    html = export_html(demo_run, tmp_path / "out.html").read_text()
    assert "Kiosk VM is being decommissioned" in html
    assert 'data-status="accepted_risk"' in html and 'data-status="false_positive"' in html


def test_server_renders_and_reloads_overrides(demo_run: Path) -> None:
    client = TestClient(create_app(demo_run))
    r = client.get("/")
    assert r.status_code == 200 and "Top risks" in r.text
    fid = runfolder.read_findings(demo_run)[0].id
    (demo_run / "overrides.yaml").write_text(f"{fid}:\n  status: accepted_risk\n  analyst_note: Fresh note\n")
    assert "Fresh note" in client.get("/").text
    assert client.get("/docs").status_code == 404


def test_ui_binds_localhost_only(demo_run: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}
    monkeypatch.setattr("uvicorn.run", lambda app, **kw: seen.update(kw))
    result = CliRunner().invoke(cli, ["ui", "--run", str(demo_run)])
    assert result.exit_code == 0, result.output
    assert seen["host"] == "127.0.0.1"
