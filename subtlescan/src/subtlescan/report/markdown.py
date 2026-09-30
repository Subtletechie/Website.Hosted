from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, PackageLoader, StrictUndefined

from subtlescan.report.view import View


def _env() -> Environment:
    env = Environment(
        loader=PackageLoader("subtlescan.report", "templates"),
        autoescape=False,  # Markdown output
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["mdcell"] = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    return env


def render_markdown(view: View) -> str:
    return _env().get_template("report.md.j2").render(v=view)


def write_markdown(view: View, run_dir: Path) -> Path:
    out = run_dir / "report.md"
    out.write_text(render_markdown(view))
    return out
