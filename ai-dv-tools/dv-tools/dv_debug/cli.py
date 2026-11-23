"""CLI for dv-debug."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from dv_debug.engine import load_excerpt_from_triage, load_rules, match_rules, render_debug_plan
from dv_triage.parser import read_log_lines

app_debug = typer.Typer(no_args_is_help=True, help="Waveform-less debug helper (Tool 06)")


@app_debug.command("list-rules")
def list_rules(
    rules: Annotated[
        Optional[Path], typer.Option("--rules", help="Custom YAML rules")
    ] = None,
    simulator: Annotated[
        str,
        typer.Option("--simulator", help="Merge VCS rules when vcs (default)"),
    ] = "vcs",
) -> None:
    """Print rule ids from the YAML library."""
    for r in load_rules(rules, simulator=simulator):
        typer.echo(f"{r['id']}: {r['title']}")


@app_debug.command("plan")
def plan(
    log: Annotated[
        Optional[Path], typer.Option("--log", help="Single sim log file")
    ] = None,
    from_triage: Annotated[
        Optional[Path], typer.Option("--from-triage", help="Tool 01 report.json")
    ] = None,
    cluster: Annotated[
        Optional[str], typer.Option("--cluster", help="Cluster id e.g. C3")
    ] = None,
    rules: Annotated[
        Optional[Path], typer.Option("--rules", help="Custom YAML rules")
    ] = None,
    out: Annotated[Path, typer.Option("--out")] = Path("debug_plan.md"),
    llm: Annotated[bool, typer.Option("--llm", help="Optional LLM narration")] = False,
    simulator: Annotated[
        str,
        typer.Option("--simulator", help="Merge VCS rules when vcs (default)"),
    ] = "vcs",
) -> None:
    """Generate debug_plan.md from log or triage cluster excerpt."""
    if llm:
        raise typer.BadParameter("LLM narration not configured in v1 (omit --llm).")
    if from_triage:
        if not cluster:
            raise typer.BadParameter("--cluster required with --from-triage")
        excerpt, hint = load_excerpt_from_triage(from_triage, cluster)
        source = hint
    elif log:
        if not log.is_file():
            raise typer.BadParameter(f"Log not found: {log}")
        lines = read_log_lines(log)
        excerpt = "".join(lines[-200:]) if len(lines) > 200 else "".join(lines)
        source = str(log)
    else:
        raise typer.BadParameter("Provide --log or --from-triage with --cluster")

    rule_list = load_rules(rules, simulator=simulator)
    matches = match_rules(excerpt, rule_list)
    md = render_debug_plan(excerpt, matches, source)
    out.write_text(md, encoding="utf-8")
    typer.echo(f"Wrote {out} ({len(matches)} rule(s) matched)")


def main() -> None:
    app_debug()


if __name__ == "__main__":
    main()