"""CLI for dv-triage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional

import typer

from dv_triage.cluster import cluster_records, delta_vs_baseline
from dv_triage.parser import parse_options, scan_directory
from dv_triage.report import clusters_to_dict, write_json_report, write_markdown_report

app_triage = typer.Typer(no_args_is_help=True, help="Regression log triage (Tool 01)")


@app_triage.command("scan")
def scan(
    log_dir: Annotated[Path, typer.Argument(help="Directory tree containing .log / .log.gz")],
    out: Annotated[Path, typer.Option("--out", help="JSON report path")] = Path("report.json"),
    markdown: Annotated[
        Optional[Path], typer.Option("--markdown", help="Optional Markdown report")
    ] = None,
    redact: Annotated[
        Optional[str], typer.Option("--redact", help="Hierarchy prefix to redact")
    ] = None,
    similarity: Annotated[
        float,
        typer.Option(
            "--similarity",
            help="Reserved for MinHash LSH (v1 uses exact normalized hash)",
        ),
    ] = 1.0,
    baseline: Annotated[
        Optional[Path],
        typer.Option("--baseline", help="Prior signatures.json for delta"),
    ] = None,
    simulator: Annotated[
        str,
        typer.Option(
            "--simulator",
            help="Log preset: vcs (Synopsys VCS, default) or generic",
        ),
    ] = "vcs",
    include_warnings: Annotated[
        bool,
        typer.Option(
            "--include-warnings",
            help="Include VCS Warning-[...] and UVM_WARNING as triage events",
        ),
    ] = False,
) -> None:
    """Scan logs, cluster failures, write reports."""
    if not log_dir.is_dir():
        raise typer.BadParameter(f"Not a directory: {log_dir}")
    if simulator not in ("vcs", "generic"):
        raise typer.BadParameter("--simulator must be 'vcs' or 'generic'")
    if similarity < 1.0:
        typer.echo(
            typer.style(
                "Note: similarity < 1.0 requires optional datasketch; using exact hash in v1.",
                fg=typer.colors.YELLOW,
            )
        )
    opts = parse_options(simulator=simulator, include_warnings=include_warnings)
    records = scan_directory(log_dir, opts=opts)
    clusters = cluster_records(records, redact_prefix=redact)
    meta: dict = {
        "log_dir": str(log_dir.resolve()),
        "total_failures": len(records),
        "similarity_threshold": similarity,
        "simulator": simulator,
        "include_warnings": include_warnings,
    }
    if baseline and baseline.is_file():
        prev = json.loads(baseline.read_text(encoding="utf-8"))
        sigs = {c["signature_hash"] for c in prev.get("clusters", [])}
        if "signatures" in prev:
            sigs = set(prev["signatures"])
        meta["delta"] = delta_vs_baseline(clusters, sigs)
    data = clusters_to_dict(clusters, meta)
    write_json_report(out, data)
    typer.echo(f"Wrote {out} ({len(clusters)} clusters, {len(records)} events)")
    if markdown:
        write_markdown_report(markdown, clusters, meta)
        typer.echo(f"Wrote {markdown}")


@app_triage.command("export-signatures")
def export_signatures(
    report: Annotated[Path, typer.Argument(help="report.json from scan")],
    out: Annotated[Path, typer.Option("--out")] = Path("signatures.json"),
) -> None:
    """Export signature hashes for next-run baseline."""
    data = json.loads(report.read_text(encoding="utf-8"))
    sigs = [c["signature_hash"] for c in data.get("clusters", [])]
    out.write_text(json.dumps({"signatures": sigs}, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Wrote {out} ({len(sigs)} signatures)")


def main() -> None:
    app_triage()


if __name__ == "__main__":
    main()