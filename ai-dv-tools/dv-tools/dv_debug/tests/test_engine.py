from pathlib import Path

from dv_debug.engine import load_rules, match_rules


def test_fixture_triggers_at_least_two_rules():
    log = Path(__file__).resolve().parents[1] / "fixtures" / "multi_rule_sample.log"
    text = log.read_text(encoding="utf-8")
    rules = load_rules()
    matches = match_rules(text, rules)
    rule_ids = {m.rule_id for m in matches}
    assert len(matches) >= 2
    assert "R05" in rule_ids or "R06" in rule_ids
    assert "R07" in rule_ids or "R04" in rule_ids