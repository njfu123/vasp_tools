"""VCS debug rule merge smoke test."""

from pathlib import Path

from dv_debug.engine import load_rules, match_rules


def test_vcs_rules_merge_and_match_snps_error():
    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "sample_logs_vcs"
        / "snps_msg_id.log"
    )
    text = fixture.read_text(encoding="utf-8")
    rules = load_rules(simulator="vcs")
    ids = {m.rule_id for m in match_rules(text, rules)}
    assert "R19" in ids or "R02" in ids