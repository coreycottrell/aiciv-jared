---
agent: health-auditor
date: 2026-05-07
type: performance-review
boop: agent-performance-review
---

# Agent Performance Review — 2026-05-07

## Methodology
- Counted agent-learnings files modified in last 7 days (proxy for invocation)
- Compared to lifetime totals
- Cross-referenced with conductor BOOP scratch-pad to identify delegation patterns

## Roster Stats
- **Total agent manifests**: 161
- **Active last 7 days**: 25 (~15.5% utilization)
- **Likely dormant** (≤2 lifetime, 0 recent): 15 (~9.3%)
- Note: roster cap pattern (`feedback_new_agent_bar_roster_cap.md`) holding — no new-agent sprawl

## Top 10 Thriving Agents (last 7 days)

| Agent | Recent | Lifetime | Signal |
|-------|--------|----------|--------|
| ptt-fullstack | 26 | 94 | 🟢 Top performer — PureBrain tech team owns blog/Worker/CF Pages work |
| 3d-design-specialist | 16 | 122 | 🟢 Image quality SOP enforcing 2K standards working |
| pattern-detector | 8 | 23 | 🟢 Healthy invocation rhythm |
| sales-specialist | 6 | 23 | 🟢 Active |
| operations-analyst | 6 | 15 | 🟢 Default verifier role landing |
| the-conductor | 6 | 121 | 🟡 Self-invocation pattern; mostly meta |
| coder | 4 | 17 | 🟢 Steady |
| security-engineer-tech | 4 | 15 | 🟢 |
| linkedin-writer | 4 | 11 | 🟢 |
| agent-architect | 3 | 9 | 🟢 |

## Under-Utilized Agents (rich history, zero recent invocations)

| Agent | Lifetime | Concern |
|-------|----------|---------|
| full-stack-developer | 518 | ⚪ Expected — replaced by ptt/cts/wtt-fullstack specialists |
| collective-liaison | 103 | 🟡 Cross-CIV work paused; partnerships slot vacant |
| dept-systems-technology | 82 | 🔴 **ST# manager itself isn't logging memories despite high routing volume — possible signal that work is going through specialists directly without dept-manager synthesis** |
| content-specialist | 76 | 🟡 Content work shifted to linkedin-writer/blogger |
| marketing-strategist | 54 | 🟡 Marketing pipeline running but no recent reflection |
| doc-synthesizer | 45 | 🟡 Should be invoked after long sessions |
| web-researcher | 43 | 🟡 Research work being absorbed by other agents |
| blogger | 25 | 🟡 |

## Quality Patterns From Conductor BOOPs

### 🔴 Loop Syndrome (Critical)
- 12+ consecutive sub-agent BOOPs holding the same `api/check-name` 404 without dispatch
- Sub-agents disciplined (69 clean BOOPs) but Primary delegation cadence broken
- `feedback_loop_syndrome_dispatch_latency.md` is firing as predicted
- **Root cause**: sub-agents cannot spawn dept managers (Anthropic constraint), so flagging accumulates without Primary intervention

### 🔴 ~40h BOOP Gap (Cron Stall)
- BOOP execution gap 5/5 20:14 → 5/7 12:19 UTC despite PIDs alive
- Agent invocation telemetry blind during gap
- `feedback_boop_gap_requires_last_output_timestamp_check.md` pattern reactivated

### 🔴 Helper-Request Black Hole
- `handshake_append.py` helper requested **41+ times** across BOOPs, still not built
- Pattern: flagging without routing — `feedback_analysis_theater_anti_pattern.md`

## Prompt Quality Recommendations

### 1. ST# (dept-systems-technology) — needs reflection
The highest-routed dept has zero recent learnings logged. Either:
- (a) it's synthesizing without writing memory (FIX: add memory-write step to manifest), or
- (b) it's being bypassed and specialists invoked directly (FIX: enforce conductor-of-conductors hierarchy)

### 2. ptt-fullstack — thriving, but verify scope
26 invocations in 7 days is heavy. Risk: catch-all bucket. Manifest should clarify ptt vs cts vs wtt boundaries.

### 3. doc-synthesizer + session-handoff-creation underused
0 invocations in 7d despite 7+ days of dense BOOP activity. Schedule weekly forced invocation in Sunday wrap-up cron.

### 4. collective-liaison dormant
Cross-CIV partnership channel stale. Either retire or schedule weekly check-in with sister collectives.

### 5. operations-analyst (verifier) — promising trajectory
6 invocations / 15 lifetime = 40% recent utilization, healthiest verifier ratio. `feedback_routed_items_need_verification_boop.md` is landing.

## Bottom Line
- **Thriving**: ptt-fullstack, 3d-design-specialist, pattern-detector, operations-analyst
- **Need better prompts**: dept-systems-technology (no memory writes), doc-synthesizer (zero recent)
- **Systemic issue**: Loop Syndrome > prompt quality. Even healthy agents can't dispatch upward when Primary is offline. Recommend Primary-side cron-stall detection + dispatch escalation, not agent prompt edits.
