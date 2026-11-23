# Tool spec: Failure signature → known-issue / fix playbook matcher

**Rank:** 3 · **Build first:** no

## Pain point & users

| Role | Pain |
|------|------|
| **DV engineer** | Sees a familiar `UVM_ERROR` but forgets the wiki fix from six months ago. |
| **TB owner** | Maintains runbooks; tired of answering duplicate “how did we fix X?” |
| **Lead** | Wants failures linked to **ticket ID** and workaround status. |

## Inputs / outputs

| Inputs | Outputs |
|--------|---------|
| Single failure snippet or triage cluster ID from Tool 01 | Ranked **playbook hits**: title, ticket, steps, similarity score |
| Corpus: markdown/HTML wiki export, closed ticket JSON, `known_issues.yaml` | “No match” + suggest new playbook draft template |
| Optional: `signatures.json` history | Trend: signature first seen date |

## MVP feature list

**In scope (v1)**

- Ingest static corpus (git-synced markdown + YAML frontmatter).
- Embed or MinHash failure signatures; retrieve top-k.
- LLM rerank + **quote-only** extraction from matched doc (no new procedure steps in v1).
- CLI: `dv-playbook match --snippet fail.txt`

**Out of scope (v1)**

- Auto-close tickets or edit wiki.
- Real-time Confluence write API.
- Learning from sim without human-approved playbook entries.

## Suggested stack

Python CLI; `chromadb` or local sqlite-vec; optional Agent SDK tool `match_known_issue`.  
Confluence/Jira APIs: **optional v2** for auto-sync.

## Success metrics

- Top-3 contains correct playbook in **≥ 70%** of pilot failures (labeled set ≥ 50).
- **&lt; 10 s** query latency local.
- Reduce repeat Slack questions (qualitative).

## Risks

- Stale playbooks → show `last_updated` prominently.
- Wrong match causes bad fix → require score threshold; display warning under 0.6 similarity.
- Ticket text leaks PII → sanitize at ingest.