# Project context: AI tools for ASIC design verification

## Audience and scope

This project targets **design verification (DV) engineers** working on complex SoC/IP blocks in a **UVM + SystemVerilog** flow. Tools are scoped as **small MVPs** (roughly days to two weeks each), runnable as **CLI or lightweight web UI**, optionally wired to **Cursor Agent SDK** or a **local/team LLM API**—not full EDA-vendor integrations in v1.

## Assumed workflow

| Area | Assumption |
|------|------------|
| Language / methodology | SystemVerilog, UVM 1.2-ish; constrained-random + directed tests; scoreboards and predictors where applicable |
| Assertions | SVA bound in RTL and/or bind modules; simulators report assertion messages in logs |
| Regression | Farm runs (LSF/Slurm/custom); per-test logs, `sim.log`, `xrun.log`, `vcs.log`, etc.; nightly and pre-submit smoke |
| Coverage | **URG** (or vendor-equivalent) HTML/text exports; functional covergroups in TB + optional code coverage signoff |
| Debug | Verdi/SimVision for waves; many failures triaged **without** opening waves first |
| Tracking | Jira / Bugzilla / internal tracker for bugs and known issues; Confluence/wiki or markdown runbooks |
| RTL handoff | Specs (PDF/markdown), interface documents (AXI, APB, custom), sometimes spreadsheet signal lists |
| Team size | **8–25 DV engineers** per block/cluster; 1–3 TB owners; 1 verification lead; shared regression pool |
| Data sensitivity | RTL and customer specs may be **confidential**; logs often contain hierarchical paths and internal codenames |

## Typical pain points (why AI helpers help)

- Regression **volume**: hundreds of failing seeds/logs per day; redundant root causes.
- **Coverage closure**: reading URG tables and cross gaps is slow; leads need concise gap narratives for reviews.
- **Knowledge scatter**: fixes and known issues live in chat, wiki, and closed tickets—hard to match a new signature.
- **TB churn**: new interfaces mean repetitive UVM agent/sequence scaffolding.
- **Assertion work**: translating English rules into SVA with correct clock/reset and signal naming.

## Non-goals for this toolset (program level)

- Replacing the simulator, formal tools, or coverage database.
- Auto-generating or modifying **released RTL** without human review.
- Mandatory cloud upload of proprietary RTL (v1 should support **local-only** inference).

## Open questions for wang yun

1. **Primary simulator** for v1 samples: **Synopsys VCS** (default `dv-triage --simulator vcs` and `dv_triage/presets/vcs.yaml`). Xcelium/Questa remain future presets; use `--simulator generic` for mixed legacy logs without VCS message IDs.
2. **Coverage signoff**: URG-only, or also Verdi coverage / EMI? Required report format?
3. **LLM policy**: On-prem (vLLM/Ollama), Cursor-only, or approved enterprise API? Any hard ban on external APIs?
4. **Wiki / known-issue source**: Confluence, GitLab wiki, plain git markdown, or ticket export only?
5. **Interface doc standard**: Word/PDF, internal markdown template, or IP-XACT / SystemRDL exports?
6. **Languages**: CLI/docs in English only, or bilingual (EN/ZH) UI for the team?
7. **Integration priority**: Standalone CLI first, or Slack/Teams bot on the regression channel?
8. **Golden data**: Can we use **sanitized** sample logs and URG snippets from a past project for evals?

## Local deploy path (Windows)

**Canonical directory on wang yun's machine:** `D:\work\tools`

- New tools, docs, and export bundles should target this tree (`dv-tools\`, `docs\`, future tools as sibling folders).
- Cloud agents write to **Project Context** first; sync to `D:\work\tools` via `media/install-to-D-work-tools.ps1` or a connected self-hosted worker when available.

## Related documents

- [DV AI tools roadmap](./dv-ai-tools-roadmap.md) — index and build order.