"""Tests for parser and normalizer."""

from __future__ import annotations

from pathlib import Path

import pytest

from dv_triage.normalizer import normalize_line, normalize_signature, owner_tag_from_signature
from dv_triage.parser import extract_failures_from_lines, parse_options, scan_directory
from dv_triage.cluster import cluster_records


def test_normalize_line_strips_time_and_seed():
    a = "UVM_ERROR @ 12:34:56 seed=12345 pid=99 mismatch"
    b = "UVM_ERROR @ 99:88:77 seed=54321 pid=11 mismatch"
    assert normalize_line(a) == normalize_line(b)


def test_normalize_vcs_volatile_tokens():
    a = (
        'Error-[X] foo Time: 1200 ns File "rtl/a.sv" Line 88 Module: m Scope: s '
        "at time 1200 ns vcs_sim_time=1200 +ntb_random_seed=999"
    )
    b = (
        'Error-[X] foo Time: 9999 ns File "rtl/b.sv" Line 12 Module: x Scope: y '
        "at time 9999 ns vcs_sim_time=9999 +ntb_random_seed=111"
    )
    assert normalize_line(a, simulator="vcs") == normalize_line(b, simulator="vcs")


def test_normalize_signature_multiline():
    text = "line1 seed=1\nline2 @ 100ns\n"
    sig = normalize_signature(text)
    assert "seed" not in sig.lower() or "<SEED>" in sig


def test_owner_tag_uvm():
    assert owner_tag_from_signature("UVM_ERROR foo", "uvm_error") == "uvm"


def test_owner_tag_vcs_assertion():
    assert owner_tag_from_signature("Assertion failed offending", "vcs_error") == "assertion"


def test_owner_tag_vcs_dpi():
    assert owner_tag_from_signature("SNPS-DPI-404", "vcs_error") == "dpi"


def test_owner_tag_timeout():
    assert owner_tag_from_signature("SIMULATION TIMEOUT", "timeout") == "timeout"


def test_extract_uvm_error():
    lines = [
        "info\n",
        "UVM_ERROR env.sb [ADDR] bad\n",
        "tail\n",
    ]
    recs = extract_failures_from_lines(lines, "t.log")
    assert len(recs) >= 1
    assert recs[0].kind == "uvm_error"


def test_extract_vcs_error_msg_id():
    lines = [
        "header\n",
        "Error-[TCHK_TSETUP] tb.clk (setup violation)\n",
        "  Time: 100 ns\n",
    ]
    recs = extract_failures_from_lines(lines, "v.log", opts=parse_options(simulator="vcs"))
    assert any(r.kind == "vcs_error" for r in recs)


def test_extract_vcs_assertion():
    lines = [
        "*** Error: Assertion tb.a failed at time 5000 ns\n",
        "offending expression: ready\n",
    ]
    recs = extract_failures_from_lines(lines, "v.log", opts=parse_options(simulator="vcs"))
    assert recs
    assert recs[0].kind in ("vcs_error", "sva")


def test_vcs_warnings_excluded_by_default():
    lines = ["Warning-[TFWIDT] width mismatch\n", "done\n"]
    recs = extract_failures_from_lines(lines, "w.log", opts=parse_options(simulator="vcs"))
    assert recs == []


def test_vcs_warnings_included_when_flag():
    lines = ["Warning-[TFWIDT] width mismatch\n"]
    recs = extract_failures_from_lines(
        lines,
        "w.log",
        opts=parse_options(simulator="vcs", include_warnings=True),
    )
    assert len(recs) == 1
    assert recs[0].kind == "vcs_warning"


def test_generic_ignores_vcs_error_id():
    lines = ["Error-[TCHK] foo\n"]
    recs = extract_failures_from_lines(lines, "g.log", opts=parse_options(simulator="generic"))
    assert recs == []


def test_scan_fixtures_multiple_clusters_generic():
    root = Path(__file__).resolve().parents[1] / "fixtures" / "sample_logs"
    records = scan_directory(root, opts=parse_options(simulator="generic"))
    clusters = cluster_records(records)
    assert len(clusters) >= 2
    tags = {c.owner_tag for c in clusters}
    assert "uvm" in tags or "assertion" in tags


def test_scan_vcs_fixtures():
    root = Path(__file__).resolve().parents[1] / "fixtures" / "sample_logs_vcs"
    records = scan_directory(root, opts=parse_options(simulator="vcs"))
    kinds = {r.kind for r in records}
    assert "vcs_error" in kinds or "uvm_error" in kinds
    clusters = cluster_records(records)
    assert len(clusters) >= 2