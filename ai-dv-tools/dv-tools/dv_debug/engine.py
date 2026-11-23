"""YAML rule engine for debug plans."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RuleMatch:
    rule_id: str
    title: str
    priority: int
    hypotheses: list[str]
    checks: list[str]
    escalate_when: list[str]
    matched_lines: list[str]


def load_rules(
    rules_path: Path | None = None,
    *,
    simulator: str = "vcs",
) -> list[dict[str, Any]]:
    rules_dir = Path(__file__).resolve().parent / "rules"
    if rules_path is None:
        rules_path = rules_dir / "default.yaml"
    raw = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    rules: list[dict[str, Any]] = list(raw.get("rules", []))
    if rules_path.name == "default.yaml" and simulator == "vcs":
        vcs_path = rules_dir / "vcs.yaml"
        if vcs_path.is_file():
            vcs_raw = yaml.safe_load(vcs_path.read_text(encoding="utf-8")) or {}
            rules.extend(vcs_raw.get("rules", []))
    return rules


def match_rules(text: str, rules: list[dict[str, Any]]) -> list[RuleMatch]:
    lines = text.splitlines()
    hits: list[RuleMatch] = []
    for rule in rules:
        patterns = [re.compile(p) for p in rule.get("match", [])]
        matched_lines: list[str] = []
        for ln in lines:
            if any(p.search(ln) for p in patterns):
                matched_lines.append(ln)
        if not matched_lines:
            continue
        hits.append(
            RuleMatch(
                rule_id=rule["id"],
                title=rule["title"],
                priority=int(rule.get("priority", 50)),
                hypotheses=list(rule.get("hypotheses", [])),
                checks=list(rule.get("checks", [])),
                escalate_when=list(rule.get("escalate_when", [])),
                matched_lines=matched_lines[:10],
            )
        )
    hits.sort(key=lambda h: (-h.priority, h.rule_id))
    return hits


def render_debug_plan(
    log_excerpt: str,
    matches: list[RuleMatch],
    source_hint: str = "",
) -> str:
    lines = [
        "# Debug plan (waveform-less)",
        "",
        "_Hypotheses only — verify before concluding root cause._",
        "",
    ]
    if source_hint:
        lines.append(f"**Source:** {source_hint}")
        lines.append("")
    lines.append("## Log excerpt")
    lines.append("")
    lines.append("```")
    excerpt = log_excerpt.strip()
    if len(excerpt.splitlines()) > 40:
        excerpt = "\n".join(excerpt.splitlines()[:40]) + "\n..."
    lines.append(excerpt)
    lines.append("```")
    lines.append("")
    if not matches:
        lines.append("## No rule matches")
        lines.append("")
        lines.append(
            "No patterns from the default rule library matched. "
            "Escalate: open waves on the failing hierarchy or expand rules YAML."
        )
        return "\n".join(lines) + "\n"

    lines.append("## Ranked hypotheses")
    lines.append("")
    for i, m in enumerate(matches[:8], start=1):
        lines.append(f"### {i}. {m.title} (`{m.rule_id}`, priority {m.priority})")
        lines.append("")
        if m.matched_lines:
            lines.append("**Matched log lines:**")
            for ml in m.matched_lines[:5]:
                lines.append(f"- `{ml.strip()[:200]}`")
            lines.append("")
        for h in m.hypotheses:
            lines.append(f"- {h}")
        lines.append("")

    lines.append("## Non-wave checks (do these first)")
    lines.append("")
    seen_checks: set[str] = set()
    for m in matches[:5]:
        for c in m.checks:
            if c in seen_checks:
                continue
            seen_checks.add(c)
            lines.append(f"- [{m.rule_id}] {c}")
    lines.append("")

    lines.append("## Escalate to waves if")
    lines.append("")
    for m in matches[:5]:
        for e in m.escalate_when:
            lines.append(f"- [{m.rule_id}] {e}")
    lines.append("")
    return "\n".join(lines) + "\n"


def load_excerpt_from_triage(report_path: Path, cluster_id: str) -> tuple[str, str]:
    import json

    data = json.loads(report_path.read_text(encoding="utf-8"))
    for c in data.get("clusters", []):
        if c.get("cluster_id") == cluster_id:
            hint = f"triage cluster {cluster_id}: {c.get('label', '')[:80]}"
            return c.get("exemplar_snippet", ""), hint
    raise ValueError(f"Cluster {cluster_id} not found in {report_path}")