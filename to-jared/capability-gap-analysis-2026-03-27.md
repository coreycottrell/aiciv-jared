# Capability Gap Analysis — March 27, 2026

## Summary
89 agents, 128 skills. Delegation trajectory improving (6.5 → 9.0 peak). But gaps exist in synthesis, underutilized agents, and missing capabilities for current work patterns.

---

## GAP 1: BOOP Output Synthesis (HIGH PRIORITY)
**Pattern**: 28 BOOPs fire daily but nobody weaves their outputs together. Each BOOP runs independently — no cross-department synthesis pass.
**Evidence**: Self-analyses on Mar 26 AND Mar 27 both identify this same gap.
**Proposal**: Add a `boop-synthesizer` scheduled task that invokes `result-synthesizer` after batch BOOP runs (e.g., after every 5 BOOPs complete). Produces a daily narrative from scattered BOOP outputs.
**Impact**: Transforms 28 isolated data points into one coherent daily brief.

## GAP 2: Underutilized Agents (MEDIUM)
**Zero-invocation agents** (last 7 days):
- `data-engineer` — no data pipeline work happening
- `data-scientist` — no analytics/modeling work
- `ai-ml-engineer` — no ML work despite AI company
- `genealogist` — lineage tracking dormant
- `health-auditor` — collective health audits not running
- `capability-curator` — skills lifecycle not actively managed

**These agents exist but have no triggering work patterns.** Not necessarily a problem — they're specialists waiting for their domain. But `health-auditor` and `capability-curator` should be running periodically.

**Proposal**:
- Add `health-auditor` to monthly BOOP schedule (collective health audit)
- Add `capability-curator` to biweekly BOOP (skill freshness check)
- `data-scientist` should be invoked for BOOP analytics (which BOOPs produce value?)

## GAP 3: No CF Pages Deploy Specialist (HIGH)
**Pattern**: CF Pages deploys are the #1 infrastructure action (every blog, every site change). Currently handled by `ptt-fullstack` or `dept-systems-technology` generically.
**Evidence**: Deploy command appears 5+ times across scratch pad, MEMORY.md, and handoffs. Cache flush rules, staging vs production, wrangler config — all require specific knowledge.
**Proposal**: Not a new agent — but a `cf-pages-deploy` **skill** that encapsulates: deploy command, cache flush, staging target (`purebrain-staging` not `purebrain`), post-deploy verification. Auto-granted to `ptt-fullstack` and `devops-engineer`.

## GAP 4: No Automated Quality Gate for BOOP Outputs (MEDIUM)
**Pattern**: BOOPs produce files (blog packages, reports, analyses) but nothing verifies quality before delivery to portal.
**Evidence**: Mar 27 self-analysis: "no quality verification pass — no result-synthesizer or integration-auditor confirming output quality."
**Proposal**: Add a `boop-qa-gate` step in the BOOP executor that runs `qa-engineer` or `integration-auditor` on any file deliverables before portal delivery.

## GAP 5: Scratch Pad Staleness (LOW but recurring)
**Pattern**: Scratch pad goes stale for days (currently 6 days stale — last updated Mar 21).
**Evidence**: Mar 27 self-analysis identifies this explicitly.
**Proposal**: Add scratch-pad freshness check to `morning-consolidation-boop`. If scratch pad >2 days old, auto-update with current state from git log + recent handoffs.

---

## Agents That Could Be More Active

| Agent | Current State | Should Be Used For |
|-------|--------------|-------------------|
| `data-scientist` | Dormant | BOOP effectiveness analytics, conversion funnel analysis |
| `health-auditor` | Dormant | Monthly collective health audit |
| `capability-curator` | Dormant | Biweekly skill freshness + dedup check |
| `genealogist` | Dormant | Agent lineage tracking (89 agents — who spawned who?) |
| `ai-ml-engineer` | Dormant | Portal AI quality, onboarding AI behavior improvements |

---

## No New Agents Recommended

89 agents is substantial. The gap is not in agent count but in:
1. **Synthesis** across existing outputs (result-synthesizer needs scheduled invocation)
2. **Quality gates** on automated outputs (existing QA agents need integration into BOOP pipeline)
3. **Utilization** of dormant specialists (scheduled triggers, not new agents)

**The right move is activating what we have, not adding more.**
