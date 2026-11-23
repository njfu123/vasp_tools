# Tool spec: SVA assertion draft assistant (English spec + signal list)

**Rank:** 5 · **Build first:** no

## Pain point & users

| Role | Pain |
|------|------|
| **DV / design** | Translating protocol rules from spec prose to SVA. |
| **TB owner** | Wants consistent `assert property` style, clock/reset listed once. |
| **Lead** | Review burden when juniors write overlapping assertions. |

## Inputs / outputs

| Inputs | Outputs |
|--------|---------|
| Rule list in English (markdown bullets) | `assertions_draft.sv` with `default clocking`, `disable iff`, property names |
| Signal list CSV: `name, width, clock_domain` | Traceability table: rule ID → property name |
| Optional: existing SVA file for style mimic | **Review checklist** markdown (reset, X-prop, overlaps) |

## MVP feature list

**In scope (v1)**

- One clock domain per run; explicit `clk`/`rst_n` from user.
- Generate **immediate-style properties** and simple sequences (`|-> ##[1:3]`).
- No editing RTL files in place—output to separate `*_sva_draft.sv`.

**Out of scope (v1)**

- Formal proof or cover property synthesis.
- Multi-clock CDC assertions.
- Binding insertion into design hierarchy (user pastes bind block).

## Suggested stack

Python CLI; LLM with **structured output** (JSON properties → templated SVA); optional Cursor command.  
Jasper/VC Formal: not in v1.

## Success metrics

- **≥ 50%** of generated properties accepted with minor edit (pilot 20 rules).
- Zero use of signals not in signal list (automated lint).
- Review time per rule **↓ 30%** vs blank-page SVA.

## Risks

- **RTL/logic hallucination** → hard constraint: whitelist signals; forbid new hierarchy.
- False confidence → banner “DRAFT — not sim/legal until reviewed”.
- X-prop / reset bugs → mandatory `disable iff (!rst_n)` template.