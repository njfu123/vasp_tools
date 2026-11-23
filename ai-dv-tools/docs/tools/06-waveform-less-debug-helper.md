# Tool spec: Waveform-less debug helper (X-prop, assertion, TB messages)

**Rank:** 6 · **Build first:** no

## Pain point & users

| Role | Pain |
|------|------|
| **DV engineer** | Failure log shows X-prop or assert message; opening waves is slow for “obvious” config issues. |
| **TB owner** | Wants checklist: env cfg, sequence order, known race windows. |
| **Junior DV** | Needs guided next steps without Verdi license contention. |

## Inputs / outputs

| Inputs | Outputs |
|--------|---------|
| Single `sim.log` excerpt or Tool 01 cluster snippet | `debug_plan.md`: hypotheses ranked, **non-wave** checks (verbosity, config, test variant) |
| Optional: `uvm_config_db` dump from log (`+UVM_CONFIG_DB_TRACE`) | Pointers to relevant covergroup / test name if mentioned in log |
| Optional: DUT parameter header snippet (non-RTL body) | Explicit “open wave if…” threshold |

## MVP feature list

**In scope (v1)**

- Rule-based triggers for X-prop, `assert control`, UVM phase objections, timeout.
- LLM narrates **only** steps grounded in matched rules + log lines.
- Library of ~20 common patterns (YAML rules editable by team).

**Out of scope (v1)**

- VCD/FSDB parsing.
- Automatic `uvm_hdl` peek or sim replay.

## Suggested stack

Python; YAML rule engine + small LLM for formatting; pairs with Tool 01 output.

## Success metrics

- **≥ 40%** of sampled failures: first suggested check identifies issue without waves (pilot labeling).
- Plan generation **&lt; 5 s**.

## Risks

- Overconfident diagnosis → label output as hypotheses; link to playbook Tool 03.
- Misses need-waves cases → always include escalation step.