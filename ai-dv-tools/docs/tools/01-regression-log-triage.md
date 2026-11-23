# Tool spec: Regression / sim log triage & root-cause clustering

**Rank:** 1 · **Build first:** yes

## Pain point & users

| Role | Pain |
|------|------|
| **DV engineer** | Opens dozens of failing logs after nightly; same UVM_ERROR/assertion failure repeats under different seeds. |
| **TB owner** | Needs a ranked list of **unique failure modes** before diving into waves. |
| **Verification lead** | Wants a morning brief: top clusters, affected tests, likely component (TB vs DUT vs env). |

## Inputs / outputs

| Inputs | Outputs |
|--------|---------|
| Directory of `*.log` (or gzipped logs) from one regression drop | `triage_report.md` / JSON: clusters with labels, member tests, exemplar log excerpt |
| Optional: `tests.xml` or Makefile test list | Suggested **owner tag** (assertion, UVM, timeout, PLI, DPI) |
| Optional: prior `signatures.json` from last run | **Delta**: new clusters vs yesterday |
| | Copy-paste summary for Slack/email (≤ 30 lines) |

**Concrete example input:** `nightly_2026-11-22/job_*/sim.log`  
**Concrete example output:** Cluster `C3: uvm_test_top.env.sb mismatch [ADDR]` — 42 tests, first seen line 18432 in `uart_rand_003.log`.

## MVP feature list

**In scope (v1)**

- Parse common patterns: UVM_FATAL/ERROR/WARNING, `** UVM `, SVA severity, `SIMULATION TIMEOUT`, assertion name + hierarchy.
- Normalize lines (strip timestamps, seed, pid) to build **failure fingerprints**.
- Hierarchical clustering or MinHash on fingerprints; cap ~50 clusters with counts.
- Emit one **representative snippet** per cluster (configurable line window).
- CLI: `dv-triage scan ./logs --out report.json`

**Explicitly out of scope (v1)**

- Automatic root-cause fix or RTL patch.
- Correlation with git commits or waveform DB.
- Live streaming from farm (batch directory only).
- Perfect parser for every vendor encrypted binary log.

## Suggested stack

| Layer | Choice |
|-------|--------|
| Runtime | Python 3.11+ CLI (`typer` or `click`) |
| Parsing | Regex + optional `structlog` line tokenizer; plugin hook per simulator flavor |
| Clustering | `datasketch` MinHash LSH or simple hash-map on normalized signature |
| LLM (optional v1.1) | Summarize cluster label in plain English from snippet only (local API) |
| Distribution | pip package or repo script; Cursor Agent SDK wrapper for “triage this folder” |

EDA vendor APIs: **not required** for MVP.

## Success metrics

| Metric | Target (v1) |
|--------|-------------|
| Time to first triage view | **&lt; 5 min** for 500 logs on a laptop (no GPU) |
| Cluster purity | **≥ 80%** manual review: same cluster = same underlying issue (sample 20 clusters) |
| Parser recall | Catch **≥ 90%** of UVM_ERROR/FATAL and SVA failures in pilot logs |
| User time saved | **30–60 min/day** per engineer on heavy regression days (self-reported) |

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Mis-clustering unlike failures | Show exemplar diff; adjustable similarity threshold; human-merge CLI |
| Log formats differ by site | Ship 2–3 presets (Xcelium/VCS); document custom regex YAML |
| LLM invents root cause | v1 is **non-LLM** clustering; LLM only names clusters from text evidence |
| Confidential paths in reports | `--redact` hierarchy prefix; offline-only processing |