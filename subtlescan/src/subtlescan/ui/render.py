"""Render the dashboard. The same output serves the local UI and the offline export:
CSS, JS, logo, and data are inlined and a CSP forbids any network request."""

from __future__ import annotations

import base64
import mimetypes
from datetime import datetime
from importlib import resources
from pathlib import Path

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

from subtlescan import runfolder
from subtlescan.report.view import Brand, build_view

STATIC = resources.files("subtlescan.ui") / "static"


def _env() -> Environment:
    env = Environment(
        loader=PackageLoader("subtlescan.ui", "templates"),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["date"] = lambda d, fmt="%d %b %Y": d.strftime(fmt) if isinstance(d, datetime) else d
    return env


def _logo_data_uri(brand: Brand) -> str:
    logo = STATIC / brand.logo
    mime = mimetypes.guess_type(brand.logo)[0] or "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(logo.read_bytes()).decode()}"


def render_dashboard(run_dir: Path, *, mode: str) -> str:
    view = build_view(runfolder.load_run(run_dir))
    brand = Brand.load(Path(str(STATIC / "brand.yaml")))
    return (
        _env()
        .get_template("dashboard.html.j2")
        .render(
            v=view,
            brand=brand,
            logo=_logo_data_uri(brand),
            css=(STATIC / "app.css").read_text(),
            js=(STATIC / "app.js").read_text(),
            mode=mode,
        )
    )
