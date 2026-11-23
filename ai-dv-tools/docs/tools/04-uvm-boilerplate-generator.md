# Tool spec: UVM sequence/agent boilerplate from interface doc

**Rank:** 4 · **Build first:** no

## Pain point & users

| Role | Pain |
|------|------|
| **TB owner** | New APB/AXI/custom interface → days of copy-paste agent/seq/driver/seq_item. |
| **DV engineer** | Wants consistent naming and `uvm_config_db` patterns. |
| **Lead** | Wants generated code to follow team style guide. |

## Inputs / outputs

| Inputs | Outputs |
|--------|---------|
| Interface spec: markdown table (signal, direction, width) or simple CSV | Zip or tree: `*_agent.sv`, `*_drv.sv`, `*_mon.sv`, `*_seq_item.sv`, `*_seq_lib.sv`, `*_pkg.sv` |
| Optional: team **style template** (Jinja) | README: integration steps + `uvm_config_db` example |
| Optional: existing agent as style reference (1 file) | Diff report vs template only |

## MVP feature list

**In scope (v1)**

- Single-clock, single-interface agent (no complex TLM passthrough).
- Deterministic Jinja generation for skeleton classes; LLM only fills **comments** and seq names from spec bullets.
- Lint pass: `verilator --lint-only` optional if available (user machine).

**Out of scope (v1)**

- Full VIP protocol compliance (e.g. AXI full VIP).
- RAL/model generation.
- Auto-connect in `env.sv` (manual instructions only).

## Suggested stack

Python + Jinja2; small LLM for naming/comment polish; output to git branch or stdout.  
IP-XACT: optional import v2.

## Success metrics

- **&gt; 50%** reduction in time to first compilable agent skeleton (measured on one new IF).
- Compile-clean on first try **≥ 60%** with user filling virtual interface hookup.
- Style template adherence **100%** for macro/structure (non-LLM parts).

## Risks

- Hallucinated UVM macros → freeze structure in templates; LLM constrained to comments/identifiers list.
- Wrong signal width → validate against input table checksum.