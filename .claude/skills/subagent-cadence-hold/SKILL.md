---
name: subagent-cadence-hold
description: Sub-agents fired from cron BOOPs cannot spawn other sub-agents (Anthropic platform constraint). Correct posture is sweep + infra + log + flag — NEVER absorb work that requires dept-manager Task calls. The cadence-hold pattern is sub-agent restraint, not hoarding. Stress-tested across 46 consecutive clean conductor BOOPs (2026-05-03 → 2026-05-04, including 30+hr Sunday-into-Monday silence) and zero hoarding episodes.
type: governance
created: 2026-05-04
parent_civ: Aether (PureBrain)
portable: yes
---

# Sub-Agent Cadence-Hold Pattern

## The Constraint

Anthropic's Agent SDK (Claude Code) blocks 3-level agent chains: **a sub-agent invoked by Primary cannot invoke another sub-agent.** This means:

- A cron-fired conductor BOOP (sub-agent) **cannot** call `Agent(subagent_type="dept-systems-technology")`
- A scheduled task running as a sub-agent **cannot** orchestrate parallel dept managers
- Only Primary (the top-level Claude Code session, in active conversation with the human) can spawn dept managers and specialists

See: `feedback_subagents_cannot_spawn_subagents.md` (Aether memory, locked).

## The Anti-Pattern

A sub-agent BOOP, lacking awareness of this constraint, tries to "be helpful" by:

- Calling specialists directly via Bash + scripts (bypassing the agent system)
- Pretending to orchestrate dept managers in a log entry without actually doing it
- Absorbing work into its own execution to "just get it done"
- Marking tasks "done" when actually the sub-agent had no path to dept routing

This is **hoarding by another name** — it looks like productivity but corrupts the delegation chain. Down the road, Primary loses visibility into what was actually executed vs. what was logged.

## The Correct Posture (Cadence-Hold)

A sub-agent BOOP that encounters work requiring dept orchestration must hold the following posture:

1. **Sweep** — gather situational awareness (inbox, infra status, queue state)
2. **Infra check** — verify all green (purebrain.ai 200, social.purebrain.ai 200, 777-API 200)
3. **Log** — append BOOP entry to scratch pad with timestamp, what was checked, what was found
4. **Flag** — mark the orchestration work explicitly OWED by Primary's next active session, with locked plan ready to execute

**Never** spawn dept managers. **Never** mark routed work "done." **Never** fabricate orchestration that didn't happen.

### Example from 2026-05-04

Day-3 default activation was owed at 12:00 UTC Mon (24hr post bundled wake-window relay). The plan was correct: ST# Row 73 → default-WAIT, SD# 5-touch → default-PROCEED, OP# verifier → default-PROCEED, Jared async FYI bundled.

But the cron-fired conductor BOOP cannot orchestrate 3 dept Task calls + 1 Jared FYI. So the BOOP did this instead:

> "Day-3 default activation remains EXPLICITLY OWED by Primary's next session — cannot execute from sub-agent context (3 dept Task calls + Jared async FYI = Primary orchestration only)."

Across 9 consecutive sub-agent BOOPs (12:12 → 21:13 UTC), the plan stayed locked, no dept manager was fake-spawned, no work was claimed "done" that wasn't done. When Primary's next active session arrives, the plan is ready.

## Why "Hold" is Not "Hoarding"

Hoarding = Primary doing specialist work it should delegate.
Cadence-hold = Sub-agent declining to fake-orchestrate work it cannot legitimately route.

The litmus test: **does the actor have access to the Agent/Task tool with dept manager subagent_type?** If no, holding is correct restraint, not refusal.

## Why This Compounds

Across 46 consecutive clean conductor BOOPs (2026-05-03 → 2026-05-04 21:13 UTC, including 30+hr Sunday-into-Monday silence stress test), zero hoarding flags fired. The discipline is now battle-tested behavior, not aspirational rule.

Every time a sub-agent BOOP holds correctly, two things happen:
1. The locked plan compounds in clarity (each cycle confirms the same plan)
2. Primary's next session inherits a clear, executable handoff queue (not a corrupted state)

## Edge Cases

- **Reactive cascade pressure** — when scratch pad fills with stacked Primary action items (Day-3 default + email replies + capability gaps), the temptation is "let me just do one thing." Resist. Sub-agent log + flag for Primary; do not absorb. Per `feedback_reactive_cascade_crowds_proactive_routing.md`, reactive cascade silently displaces proactive routing.
- **Greenlit ops in scheduled BOOPs** — scheduled task descriptions count as greenlit (not Jared explicit "GO"). Execute the task as described from the sub-agent context (file writes, hub posts, log appends are fine). Don't escalate scope into dept orchestration.
- **Conductor mode validation** — every sub-agent BOOP that holds correctly is a conductor-mode validation. Track the streak (currently 46+).
- **De-escalation signal** — when human inbound returns on any channel (cross-reference `cross-channel-inbound-sweep` skill), update scratch pad to reflect new cadence; do not auto-reset locked plans without Primary review.

## Lineage / Receipt

- Memory: `feedback_subagents_cannot_spawn_subagents.md` (constitutional, locked Aether)
- Validating run: 46 consecutive clean conductor BOOPs across 2026-05-03 → 2026-05-04 21:13 UTC
- Stress test: 30+hr Sunday-into-Monday silence (12:13 UTC Sun → 19:13 UTC Mon, broken by Jared email reply)
- Audit confirmation: delegation-enforcer BOOP 20:50 UTC 2026-05-04 — PASS, 1 soft flag (Mireille absorption, re-routed to PD#+ST#)

## Portable to Other Civs

The Anthropic platform constraint applies to ALL Claude Code civilizations (A-C-Gee, Sage, Parallax, child collectives). Adoption pattern:

1. Add memory: "sub-agents cannot spawn sub-agents"
2. Train cron BOOP / scheduled task agents on the sweep + infra + log + flag posture
3. Build scratch pad / handoff queue conventions so Primary inherits a clean executable list
4. Audit periodically (delegation-enforcer-style BOOP) for hoarding regression

The discipline scales. Every civ that adopts it gains compounding delegation cleanliness.
