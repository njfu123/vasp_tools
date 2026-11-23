# Tool spec: URG / coverage report Q&A and gap summarizer

**Rank:** 2 · **Build first:** yes

## Pain point & users

| Role | Pain |
|------|------|
| **DV engineer** | URG HTML is huge; hard to answer “what’s still missing for this feature?” |
| **Verification lead** | Needs **closure narrative** for weekly reviews without manually clicking every hole. |
| **TB owner** | Wants cross-coverage gap list tied to covergroup names for backlog prioritization. |

## Inputs / outputs

| Inputs | Outputs |
|--------|---------|
| URG **HTML** tree or unified `session.xml` / text `.ucdb` export (site-dependent) | **Gap summary** markdown: top uncovered bins/crosses, by hierarchy or testbench region |
| Optional: `coverage goals` YAML (target % per covergroup) | Natural-language **Q&A** with citations to covergroup/bin names (no invented bins) |
| Optional: feature list markdown | “Suggested next tests” bullet list (heuristic + LLM), clearly labeled as proposals |

**Concrete inputs:** `urgReport/dashboard.html`, `urgReport/modinfo.txt`, or exported CSV from urg.  
**Concrete outputs:** `gaps_2026-11-22.md`, `answers.json` with `{question, answer, citations[]}`.

## MVP feature list

**In scope (v1)**

- Parse URG/modinfo **text-first** (HTML table → structured records via BeautifulSoup).
- Build in-memory index: `covergroup`, `bin`, `count`, `goal`, `uncovered` flags.
- Deterministic **gap report**: sort by (goal miss, uncovered crosses, low hit count).
- Q&A: retrieve relevant records (keyword + embed optional); LLM answers **only from retrieved rows**.
- CLI: `dv-cov ingest ./urgReport --ask "Which AXI crosses are below 90%?"`

**Out of scope (v1)**

- Writing back to UCDB or rerunning urg.
- Code coverage path analysis (toggle, FSM) unless present in same export.
- Auto-marking coverpoints waived in tool (track waiver file read-only).

## Suggested stack

| Layer | Choice |
|-------|--------|
| Ingest | Python + BeautifulSoup/lxml; fallback CSV importer |
| Index | SQLite or `duckdb` for queryable coverage facts |
| Q&A | RAG over structured rows (no free-form chunk hallucination); OpenAI-compatible or local LLM |
| UI (optional) | Minimal Streamlit or markdown-only for v1 |

EDA APIs (Verdi COV, IMC): **optional later** if HTML export is insufficient.

## Success metrics

| Metric | Target |
|--------|--------|
| Ingest time | **&lt; 2 min** for typical block URG dump |
| Q&A grounding | **100%** of cited bin/cross names exist in index (automated check) |
| Gap summary usefulness | Lead rates **≥ 4/5** vs manual URG review (pilot) |
| Time saved | **1–2 hours/week** during closure phase per lead |

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Hallucinated coverage % | Answers must include citation IDs; validator rejects unknown names |
| HTML layout changes between URG versions | Version probe + parser tests on 2 URG versions |
| Misinterpretation of crossed bins | Show raw hit/goal table alongside summary |
| Proprietary metrics leaving site | Local DB + local LLM; no upload mode default |