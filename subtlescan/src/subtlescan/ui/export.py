from __future__ import annotations

from pathlib import Path

from subtlescan.ui.render import render_dashboard


def export_html(run_dir: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dashboard(run_dir, mode="export"), encoding="utf-8")
    return out
