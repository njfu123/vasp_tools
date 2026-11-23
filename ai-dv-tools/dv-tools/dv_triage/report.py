"""JSON and Markdown report generation."""

from __future__ import annotations

import json
from pathlib import Path

from dv_triage.cluster import Cluster


def clusters_to_dict(clusters: list[Cluster], meta: dict | None = None) -> dict:
    body = {
        "clusters": [
            {
                "cluster_id": c.cluster_id,
                "label": c.label,
                "count": c.count,
                "test_names": c.test_names,
                "owner_tag": c.owner_tag,
                "signature_hash": c.signature_hash,
                "exemplar_snippet": c.exemplar_snippet,
                "member_sources": c.member_sources,
            }
            for c in clusters
        ]
    }
    if meta:
        body["meta"] = meta
    return body


def write_json_report(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown_report(path: Path, clusters: list[Cluster], meta: dict | None = None) -> None:
    lines = ["# Regression log triage report", ""]
    if meta:
        if "log_dir" in meta:
            lines.append(f"**Log directory:** `{meta['log_dir']}`")
        if "total_failures" in meta:
            lines.append(f"**Parsed failure events:** {meta['total_failures']}")
        if "delta" in meta:
            d = meta["delta"]
            lines.append(
                f"**Delta:** {len(d.get('new_cluster_ids', []))} new cluster(s) vs baseline"
            )
        lines.append("")
    lines.append(f"**Clusters:** {len(clusters)}")
    lines.append("")
    for c in clusters:
        tests_preview = ", ".join(c.test_names[:8])
        if len(c.test_names) > 8:
            tests_preview += f", … (+{len(c.test_names) - 8} more)"
        lines.append(f"## {c.cluster_id}: {c.label}")
        lines.append("")
        lines.append(f"- **Count:** {c.count}")
        lines.append(f"- **Owner tag:** `{c.owner_tag}`")
        lines.append(f"- **Tests:** {tests_preview}")
        lines.append("")
        lines.append("```")
        lines.append(c.exemplar_snippet.rstrip())
        lines.append("```")
        lines.append("")
    slack = _slack_summary(clusters)
    lines.append("---")
    lines.append("")
    lines.append("## Slack / email summary")
    lines.append("")
    lines.append("```")
    lines.extend(slack)
    lines.append("```")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _slack_summary(clusters: list[Cluster], max_lines: int = 30) -> list[str]:
    out = [f"Top {min(10, len(clusters))} failure clusters:"]
    for c in clusters[:10]:
        out.append(
            f"  {c.cluster_id} [{c.owner_tag}] x{c.count}: {c.label[:70]}"
        )
        if len(out) >= max_lines:
            break
    return out