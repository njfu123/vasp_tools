"""Normalize log lines into failure fingerprints."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Timestamps: HH:MM:SS, ns/ps/fs times, ISO-ish dates
_TIME_PATTERNS = [
    re.compile(r"\b\d{1,2}:\d{2}:\d{2}(?:\.\d+)?\b"),
    re.compile(r"\b\d+\s*(?:ns|ps|fs|us|ms)\b", re.I),
    re.compile(r"\b@?\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?\b"),
    re.compile(r"\bUVM\s+Info\s+[^:]+:\s*\d+\s*:\s*", re.I),
    re.compile(r"\b(?:simulation|elab)\s+time\s*[:=]\s*\d+", re.I),
]

_VCS_TIME_PATTERNS = [
    re.compile(r"\bTime:\s*\d+(?:\.\d+)?(?:\s*(?:ns|ps|fs|us|ms))?\b", re.I),
    re.compile(r"\bat\s+time\s+\d+(?:\.\d+)?(?:\s*(?:ns|ps|fs|us|ms))?\b", re.I),
    re.compile(r'\bFile\s+"[^"]*"\s+Line\s+\d+\b', re.I),
    re.compile(r'\bFile\s+\S+\s+Line\s+\d+\b', re.I),
    re.compile(r"\bModule:\s*\S+", re.I),
    re.compile(r"\bScope:\s*\S+", re.I),
    re.compile(r"\bRegion:\s*\S+", re.I),
    re.compile(r"\bvcs_sim_time\s*[=:]\s*\d+", re.I),
    re.compile(r"\bOffending\s+\w+:\s*\S+", re.I),
    re.compile(r"\boffending\s+expression:\s*.+", re.I),
]

_SEED_PID = [
    re.compile(r"\b(?:seed|SEED|random seed)\s*[=:]\s*\d+\b", re.I),
    re.compile(r"\bUVM\s+random\s+seed\s*[=:]\s*\d+\b", re.I),
    re.compile(r"\brandom\s+seed\s+used\s*=\s*\d+\b", re.I),
    re.compile(r"\b(?:pid|PID)\s*[=:]\s*\d+\b", re.I),
    re.compile(r"\+ntb_random_seed=\d+", re.I),
    re.compile(r"\b-sv_seed\s+\d+\b"),
]

_LINE_NUM = re.compile(r":\d+:\s*")
_TEST_NAME = re.compile(r"\b(?:Running test|test)\s+\S+\b", re.I)


def normalize_line(line: str, *, simulator: str = "vcs") -> str:
    """Strip volatile tokens from a single line."""
    s = line.strip()
    if not s:
        return ""
    for pat in _TIME_PATTERNS:
        s = pat.sub("<T>", s)
    if simulator == "vcs":
        for pat in _VCS_TIME_PATTERNS:
            s = pat.sub("<T>", s)
    for pat in _SEED_PID:
        s = pat.sub("<SEED>", s)
    s = _LINE_NUM.sub(":<N>: ", s)
    s = _TEST_NAME.sub("test <T>", s)
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_signature(text: str, *, simulator: str = "vcs") -> str:
    """Build a stable fingerprint from multi-line failure text."""
    lines = [normalize_line(ln, simulator=simulator) for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


@dataclass(frozen=True)
class FailureRecord:
    kind: str
    raw_excerpt: str
    normalized: str
    source_file: str
    line_no: int | None = None


def redact_hierarchy(text: str, prefix: str | None) -> str:
    if not prefix:
        return text
    return text.replace(prefix, "<REDACTED>")


def owner_tag_from_signature(sig: str, kind: str) -> str:
    """Heuristic owner tags: assertion, UVM, timeout, VCS/SNPS, etc."""
    upper = sig.upper()
    if kind == "timeout" or "SIMULATION TIMEOUT" in upper or "TIME LIMIT EXCEEDED" in upper:
        return "timeout"
    if kind.startswith("vcs"):
        if "DPI" in upper or "SNPS" in upper or "SNPS-DPI" in upper:
            return "dpi"
        if "ASSERT" in upper or "OFFENDING" in upper or "SVA" in upper:
            return "assertion"
        if kind == "vcs_warning":
            return "vcs"
        return "vcs"
    if "SVA" in upper or "ASSERT" in upper or kind == "sva":
        return "assertion"
    if "UVM" in upper or kind.startswith("uvm"):
        return "uvm"
    if "DPI" in upper or "DPI" in kind:
        return "dpi"
    if "PLI" in upper:
        return "pli"
    if "XPROP" in upper or "X-PROP" in upper:
        return "xprop"
    return "other"