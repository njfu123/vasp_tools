"""Parse simulation logs for failure patterns."""

from __future__ import annotations

import gzip
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from dv_triage.normalizer import FailureRecord, normalize_signature

UVM_FATAL = re.compile(
    r"UVM_(?:FATAL|ERROR|WARNING)\s+.*",
    re.I,
)
UVM_STAR = re.compile(r"^\s*\*\*\s+UVM\s+.*", re.I)
SVA_FAIL = re.compile(
    r"(?:Assertion\s+.*failed|SVA\s+.*(?:failed|violation)|\*\*\s*Error:.*assert|offending\s+(?:signal|expression))",
    re.I,
)
TIMEOUT = re.compile(r"SIMULATION\s+TIMEOUT|TIME\s+LIMIT\s+EXCEEDED|Simulation\s+timeout", re.I)
XPROP = re.compile(r"XPROP|X-PROP|X\s+propagation", re.I)

VCS_ERROR_ID = re.compile(r"Error-\[[^\]]+\]", re.I)
VCS_WARNING_ID = re.compile(r"Warning-\[[^\]]+\]", re.I)
VCS_RUNTIME_ERROR = re.compile(
    r"^\s*(?:\*\*\*?\s*)?Error:\s+(?!.*\bUVM\b)",
    re.I,
)

CONTEXT_BEFORE = 2
CONTEXT_AFTER = 18

_DEFAULT_PRESET_DIR = Path(__file__).resolve().parent / "presets"


@dataclass
class ParseOptions:
    simulator: str = "vcs"
    include_warnings: bool = False
    _extra_patterns: list[tuple[re.Pattern[str], str]] = field(
        default_factory=list, repr=False
    )


def load_simulator_preset(simulator: str) -> dict[str, Any]:
    path = _DEFAULT_PRESET_DIR / f"{simulator}.yaml"
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_options(
    simulator: str = "vcs",
    include_warnings: bool = False,
) -> ParseOptions:
    opts = ParseOptions(simulator=simulator, include_warnings=include_warnings)
    if simulator != "vcs":
        return opts
    preset = load_simulator_preset("vcs")
    for entry in preset.get("extra_patterns") or []:
        kind = entry.get("kind", "vcs_error")
        regex = entry.get("regex")
        if regex:
            opts._extra_patterns.append((re.compile(regex), kind))
    return opts


def _lines_for_signature(
    lines: list[str], trigger_idx: int, *, simulator: str = "vcs"
) -> list[str]:
    """Lines used for fingerprint (exclude unrelated preamble)."""
    out = [lines[trigger_idx]]
    tail_pat = (
        r"UVM_|mismatch|failed|violation|TIMEOUT|X-?PROP|Error-\[|Warning-\[|Error:|offending"
        if simulator == "vcs"
        else r"UVM_|mismatch|failed|violation|TIMEOUT|X-?PROP"
    )
    for j in range(trigger_idx + 1, min(len(lines), trigger_idx + 8)):
        if _classify_line(lines[j], ParseOptions(simulator=simulator)) or re.search(
            tail_pat, lines[j], re.I
        ):
            out.append(lines[j])
    return out


def _is_warning_kind(kind: str) -> bool:
    return kind in ("vcs_warning", "uvm_warning")


def _classify_line(line: str, opts: ParseOptions) -> str | None:
    if TIMEOUT.search(line):
        return "timeout"
    if opts.simulator == "vcs":
        for pat, kind in opts._extra_patterns:
            if pat.search(line):
                return kind
        if VCS_ERROR_ID.search(line):
            return "vcs_error"
        if SVA_FAIL.search(line):
            return "sva"
        if VCS_RUNTIME_ERROR.search(line):
            return "vcs_error"
        if VCS_WARNING_ID.search(line):
            return "vcs_warning"
    if UVM_FATAL.search(line):
        m = re.search(r"UVM_(FATAL|ERROR|WARNING)", line, re.I)
        return f"uvm_{m.group(1).lower()}" if m else "uvm"
    if UVM_STAR.search(line):
        if re.search(r"error|fatal|warning|violation", line, re.I):
            return "uvm_star"
        return None
    if SVA_FAIL.search(line):
        return "sva"
    if XPROP.search(line):
        return "xprop"
    return None


def _test_name_from_path(path: Path) -> str:
    stem = path.name
    if stem.endswith(".log.gz"):
        return stem[: -len(".log.gz")]
    if stem.endswith(".log"):
        return stem[: -len(".log")]
    return stem


def read_log_lines(path: Path) -> list[str]:
    if path.suffix == ".gz" or path.name.endswith(".log.gz"):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def extract_failures_from_lines(
    lines: list[str],
    source_file: str,
    *,
    opts: ParseOptions | None = None,
) -> list[FailureRecord]:
    if opts is None:
        opts = ParseOptions()
    records: list[FailureRecord] = []
    i = 0
    while i < len(lines):
        kind = _classify_line(lines[i], opts)
        if kind is None:
            i += 1
            continue
        if _is_warning_kind(kind) and not opts.include_warnings:
            i += 1
            continue
        start = max(0, i - CONTEXT_BEFORE)
        end = min(len(lines), i + CONTEXT_AFTER)
        excerpt_lines = lines[start:end]
        raw = "".join(excerpt_lines)
        sig_lines = _lines_for_signature(lines, i, simulator=opts.simulator)
        normalized = normalize_signature("".join(sig_lines), simulator=opts.simulator)
        if not normalized:
            i += 1
            continue
        records.append(
            FailureRecord(
                kind=kind,
                raw_excerpt=raw,
                normalized=normalized,
                source_file=source_file,
                line_no=i + 1,
            )
        )
        i = end
    return records


def iter_log_files(log_dir: Path) -> list[Path]:
    found: list[Path] = []
    for p in sorted(log_dir.rglob("*")):
        if not p.is_file():
            continue
        name = p.name.lower()
        if name.endswith(".log") or name.endswith(".log.gz"):
            found.append(p)
    return found


def scan_directory(
    log_dir: Path,
    *,
    opts: ParseOptions | None = None,
) -> list[FailureRecord]:
    if opts is None:
        opts = ParseOptions()
    all_records: list[FailureRecord] = []
    for path in iter_log_files(log_dir):
        rel = str(path.relative_to(log_dir))
        test_name = _test_name_from_path(path)
        lines = read_log_lines(path)
        for rec in extract_failures_from_lines(lines, rel, opts=opts):
            all_records.append(
                FailureRecord(
                    kind=rec.kind,
                    raw_excerpt=rec.raw_excerpt,
                    normalized=rec.normalized,
                    source_file=f"{test_name}@{rec.source_file}",
                    line_no=rec.line_no,
                )
            )
    return all_records