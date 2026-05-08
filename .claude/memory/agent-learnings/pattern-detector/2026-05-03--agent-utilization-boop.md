---
name: Agent Utilization BOOP — 2026-05-03
description: 24h utilization snapshot + measurement-method correction. Drift pattern materially shifted from yesterday — dept managers activated for first time in 3 days.
type: project
---

# Agent Utilization BOOP — 2026-05-03

## Headline (read first)

**Drift pattern broke yesterday.** Conductor's 03:14 UTC nightly self-analysis logs **8/23 dept managers activated** in the May 2 day (ST#, MA#, CTO, security-engineer-tech, ptt-fullstack, ptt-qa, qa-engineer, OP#). That's up from 0 the day prior. The 5-layer cascade (MA# → ST# → CTO → ptt-fullstack → security-engineer-tech) is the cleanest delegation chain logged to date, and CTO pre-build review caught a CRITICAL synthetic-user_id bug before BUILD fired.

So yesterday evening's recommendation ("manual intervention needed: invoke 3 dormant dept managers on real work") **was actioned within 24h**. Convergence signal cleared.

## Measurement-Method Correction (META — fix this BOOP going forward)

Previous agent-utilization BOOPs used `.claude/memory/agent-learnings/<agent>/` mtime as the dormancy signal. That's wrong for dept-manager class:

- ST# delegated 3 routes May 2, but **ptt-fullstack** wrote the learning record, not ST#.
- MA# fired Anticipation Engine, but the writeup lived under conductor / linkedin-writer.
- CTO did pre-build architectural review — wrote its own learning, so visible. But that's the exception.

**Result**: My method systematically under-counts dept-manager activation by attributing the artifact to the executing specialist. Yesterday's evening BOOP claimed "0 dept managers in 12hr" — actual was 4-8. False alarm contributed to the 3-day "stuck pattern" narrative.

**Fix**: Cross-reference conductor BOOP self-analyses (`agent-learnings/the-conductor/*delegation-enforcer*` and `*nightly-self-analysis*`) which log dept activations by name. Don't trust mtime on dept dirs in isolation.

## 24-Hour Activity (corrected, fresh data)

### Active in trailing 24h (learning artifacts present)
| Agent | Last write | Note |
|-------|-----------|------|
| `pattern-detector` | 03:00 UTC May 3 (now) | this BOOP |
| `the-conductor` | 03:14 UTC | nightly self-analysis (6 BOOPs through May 2 night) |
| `agent-architect` | 02:36 UTC | capability-gap-boop |
| `gpt-forge` | 01:42 UTC | **NEW activation** — first GPT memory test drive |
| `arcx-biz-dev-mngr` | 01:42 UTC | **NEW activation** — Web3 SaaS partnership bridge |
| `financial-analyst` | 01:41 UTC | **NEW activation** — price-flip unit economics |
| `strategy-specialist` | 01:41 UTC | **NEW activation** — Month-3 switching cost |
| `security-engineer-tech` | May 2 22:35 UTC | blog publish hook security review |
| `cto` | May 2 22:21 UTC | bsky-publish hook signoff B6 |
| `3d-design-specialist` | May 3 00:36 UTC | sunday-batch May 4 (replicate token blocker) |
| `ptt-fullstack` | May 3 00:54 UTC | social API image attach pattern |
| `operations-analyst` | May 2 21:12 UTC | daily recap May 2 brainscore sprint |
| `human-liaison` | May 2 09:55 UTC | BOOP email check (within 24h boundary) |

**Count**: ~13 distinct agents in 24h, with **4 first-time/recent-revival activations** (gpt-forge, arcx-biz-dev-mngr, financial-analyst, strategy-specialist) — the "new GPT + economics + partnership" cluster fired together at 01:41-01:42 UTC, suggests a coordinated session block.

### Dept Managers Activated (per conductor log, May 2)
ST# (3 routes), MA# (Anticipation Engine + bsky-distribution), CTO, security-engineer-tech, ptt-fullstack, ptt-qa, qa-engineer, OP#. **8 of 23.**

### Still Skipped (15 of 23 dept managers)
SD#, PD#, AF#, HR#, LC#, IR#, PR#, IT#, BOA#, CB#, CO#, ES#, IS#, Karma, plus the umbrella stewards (Pure Capital, Digital Assets, Infrastructure, Love, Marketing Group, Research, Tech).

## Open Drift Items (carry from prior BOOPs)

### Conductor's own commit follow-through: 0/3 yesterday
Per `the-conductor/2026-05-03--nightly-self-analysis.md`, the 3 commits from May 2 nightly **were not delivered**:
1. Pair-verifier BOOPs for 3 PD chronic specs — not staged
2. Stale Chy queue Rows 3, 4 (24-day idle, AETHER→CHY) — no close-out, no re-route
3. SD# pre-stage for email welcome activation — zero SD# routing

**This is `feedback_self_analysis_commitments_need_delegation.md` hit twice in a row.** The conductor is aware ("same anti-pattern memory I cited yesterday") and has converted today's commits to scratch-pad TODOs as durable state — that's the right corrective. Not a pattern-detector escalation issue today.

### Tool-surface gap (logged, not routed)
Dept-manager class lacks `Agent`/`Task` tool exposure → can't spawn parallel sub-agents → uses self-execution workaround. Conductor flagged for routing to PT# umbrella. **Not pattern-detector's lane**, but worth surfacing here as a structural drag on dept-manager utilization metrics.

## Role-Drift Flags

### Specialist-direct invocations bypassing managers (continuing pattern)
- `strategy-specialist`, `financial-analyst`, `arcx-biz-dev-mngr` — all invoked directly (01:41-01:42 UTC cluster). Should have been CB# or CO# orchestrated, given they're partnership/strategy/economics work.
- `gpt-forge` — direct invocation; arguably ST# (technical infrastructure) or PD# (product) territory.
- `3d-design-specialist` — direct invocation for content batch; should be MA# orchestrated per LinkedIn-army cadence.

This isn't catastrophic — the work happened — but it bypasses the conductor-of-conductors architecture. Same drift as yesterday, **same severity, no escalation needed** (the work is high-quality and ships).

### "Never invoked" registered agents (96 of 161)
Roster cap reality: 96 registered agents have never produced a learning artifact. Per `feedback_new_agent_bar_roster_cap.md`, no new agents until existing dormancy resolves. 78%+ dormancy persists; today is 96/161 = **60%** never-invoked, **88%** dormant beyond 7 days. Roster is theoretical.

Notable never-invoked clusters:
- All 8 legal specialists (california-, delaware-, employment-, florida-bar-, immigration-, insurance-, international-, ip-, privacy-, securities-, tax-, ai-regulatory-) — 12 lawyers, 0 invocations. `counsel` umbrella also never used.
- 7 dept managers (AF#, HR#, IT#, BOA#, CB#, CO#, ES#, IS#, Karma + 6 Pure-* stewards) — 16 dept-class agents never used.
- 4 reviewer/auditor agents (auditor, reviewer, reviewer-audit, integration-verifier) — replaced de-facto by inline conductor checks.

## Recommendations (priority ordered, brief)

1. **No new BOOP today on this topic.** Drift broke. Convergence cleared. Re-running same-day = wasteful.
2. **Update measurement method permanently** (this file documents the fix). Future agent-utilization BOOPs cross-ref conductor delegation logs, not just learning-dir mtime.
3. **Conductor's commit-to-route fix is in motion** (scratch-pad TODOs added today) — let it ride. Re-check tomorrow's nightly self-analysis for delivery on Stale Chy + SD# pre-stage. If 0/3 a third day, escalate to OP# as durable ticket per yesterday's self-note.
4. **Roster cap holds.** 60% never-invoked + 88% >7-day dormancy → no new agents.
5. **Skip evening BOOP today.** Yesterday's evening BOOP self-note recommended skipping if drift is identical 3+ days. Today drift is NOT identical (it materially improved), so morning BOOP is sufficient. Resume normal cadence tomorrow.

## Numbers (snapshot)
- Active in 24h (specialist artifacts): 13 agents
- Dept managers activated May 2 (per conductor log): 8 of 23 (35%)
- New activations today: 4 (gpt-forge, arcx-biz-dev-mngr, financial-analyst, strategy-specialist)
- Never-invoked of registered: 96 of 161 (60%)
- Constitutional cascade compliance: ~35% (was 0% yesterday) — **major improvement**

## Self-Note (pattern-detector learning carried forward)
- **Measurement bug fixed**: mtime ≠ activation for dept-manager class. Cross-ref conductor logs.
- **3-day drift narrative was partially false** because of measurement bug. Yesterday's evening BOOP overstated severity.
- **Convergence signal worked despite bad data**: 3 BOOPs flagged "delegation broken" → next session, 8 dept managers activated. Even noisy convergence signals trigger correction. Keep the protocol; sharpen the metric.
