from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from subtlescan import runfolder
from subtlescan.runlog import attach_run_log, console, log, setup_console

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Read-only cloud security assessment.")

RunOpt = Annotated[
    Path,
    typer.Option(
        "--run", help="Run folder, e.g. runs/acme/2026-09-30T120000Z", exists=True, file_okay=False, resolve_path=True
    ),
]


class CliProvider(StrEnum):
    azure = "azure"
    aws = "aws"


class ReportFormat(StrEnum):
    md = "md"
    pdf = "pdf"


@app.callback()
def _main(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False) -> None:
    setup_console(verbose)


def _require_azure(provider: CliProvider) -> None:
    if provider is not CliProvider.azure:
        console.print("[yellow]AWS support is planned (build step 7); only --provider azure works today.[/]")
        raise typer.Exit(2)


@app.command("connect-check")
def connect_check(
    provider: Annotated[CliProvider, typer.Option()] = CliProvider.azure,
    tenant: Annotated[str | None, typer.Option(help="Entra tenant id")] = None,
    subscription: Annotated[list[str] | None, typer.Option(help="Limit to these subscription ids")] = None,
) -> None:
    """Verify credentials and read permissions. Lists coverage gaps; writes nothing."""
    _require_azure(provider)
    from subtlescan.collectors.azure import collect_all
    from subtlescan.collectors.azure.context import AzureContext

    ctx = AzureContext.live(tenant)
    subs = ctx.discover_subscriptions(subscription)
    assets = collect_all(ctx) if subs else []
    table = Table(title="Visible subscriptions")
    table.add_column("Subscription")
    for s in subs:
        table.add_row(s)
    console.print(table)
    console.print(f"Read {len(assets)} resource(s) across enabled collectors.")
    if not ctx.gaps:
        console.print("[green]All collectors have the permissions they need.[/]")
        return
    gaps = Table(title="Coverage gaps")
    for col in ("Scope", "Service", "Reason", "Detail"):
        gaps.add_column(col)
    for g in ctx.gaps:
        gaps.add_row(g.scope, g.service, g.reason.label, g.detail)
    console.print(gaps)
    if not subs:
        raise typer.Exit(1)


@app.command()
def scan(
    client: Annotated[str, typer.Option(help="Client name, used for the run folder")],
    provider: Annotated[CliProvider, typer.Option()] = CliProvider.azure,
    tenant: Annotated[str | None, typer.Option(help="Entra tenant id")] = None,
    subscription: Annotated[list[str] | None, typer.Option(help="Limit to these subscription ids")] = None,
    out: Annotated[Path, typer.Option(help="Root folder for runs")] = Path("runs"),
) -> None:
    """Collect, check, score, and write a Markdown report into a new run folder."""
    _require_azure(provider)
    from subtlescan.collectors.azure.context import AzureContext
    from subtlescan.pipeline import analyze, collect_azure

    run_dir = runfolder.new_run_dir(out, client)
    handler = attach_run_log(run_dir)
    try:
        log.info("run folder: %s", run_dir, extra={"event": "start", "client": client})
        collect_azure(run_dir, client, AzureContext.live(tenant), subscription)
        analyze(run_dir)
        path = _write_report(run_dir, None)
    finally:
        log.removeHandler(handler)
        handler.close()
    console.print(f"[green]Done.[/] Report: {path}\nNext: subtlescan ui --run {run_dir}")


@app.command()
def analyze(run: RunOpt) -> None:
    """Re-run checks and scoring over an existing inventory (no cloud calls)."""
    from subtlescan.pipeline import analyze as do_analyze

    do_analyze(run)
    console.print(f"Report: {_write_report(run, None)}")


def _write_report(run_dir: Path, framework: str | None) -> Path:
    from subtlescan.report.markdown import write_markdown
    from subtlescan.report.view import build_view

    return write_markdown(build_view(runfolder.load_run(run_dir), framework), run_dir)


@app.command()
def report(
    run: RunOpt,
    framework: Annotated[str | None, typer.Option(help="soc2, cis_azure, nist_csf, iso27001, hipaa")] = None,
    format: Annotated[ReportFormat, typer.Option("--format")] = ReportFormat.md,
) -> None:
    """Render the report from an existing run folder without rescanning."""
    if format is ReportFormat.pdf:
        console.print("[yellow]PDF output is planned (build step 6). Use --format md for now.[/]")
        raise typer.Exit(2)
    try:
        path = _write_report(run, framework)
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(2) from exc
    console.print(f"Report: {path}")


@app.command()
def ui(
    run: RunOpt,
    port: Annotated[int, typer.Option()] = 8765,
) -> None:
    """Serve the dashboard on 127.0.0.1 for screen-sharing. Never binds other interfaces."""
    import uvicorn

    from subtlescan.ui.app import create_app

    console.print(f"Dashboard: http://127.0.0.1:{port}  (Ctrl+C to stop)")
    uvicorn.run(create_app(run), host="127.0.0.1", port=port, log_level="warning")


@app.command()
def export(
    run: RunOpt,
    out: Annotated[Path | None, typer.Option(help="Output file (default: <run>/dashboard.html)")] = None,
) -> None:
    """Write the dashboard as one self-contained, offline HTML file to send to the client."""
    from subtlescan.ui.export import export_html

    path = export_html(run, out or run / "dashboard.html")
    console.print(f"Exported: {path}")


@app.command()
def demo(
    out: Annotated[Path, typer.Option(help="Root folder for runs")] = Path("runs"),
) -> None:
    """Write a realistic fake run (with a previous run for deltas) to demo the UI without a tenant."""
    from subtlescan.demo import write_demo_runs

    current = write_demo_runs(out)
    console.print(f"Demo run: {current}\nTry: subtlescan ui --run {current}")


if __name__ == "__main__":
    app()
