# dv_debug (Tool 06)

Rule-based waveform-less debug plan from a log excerpt or Tool 01 cluster.

## Install

Same as `dv_triage` (single `dv-tools` package).

## Usage

```bash
dv-debug plan --log sim.log --out debug_plan.md
dv-debug plan --from-triage report.json --cluster C1 --out debug_plan.md
dv-debug plan --log sim.log --rules rules/custom.yaml --out debug_plan.md
```

`--llm` is a stub in v1 and exits with "not configured".

## Rules

Edit `dv_debug/rules/default.yaml` (18 patterns: X-prop, assert, UVM phase, timeout, config_db, …).

## Example

```bash
dv-debug plan --log dv_debug/fixtures/multi_rule_sample.log --out /tmp/debug_plan.md
```

## Tests

```bash
pytest dv_debug/tests -q
```