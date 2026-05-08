---
title: Capability Gap Analysis BOOP — 2026-05-01 01:07 UTC
type: capability-gap-report
cadence: twice-daily (9am/9pm)
owner: agent-architect
window: 2026-04-30 01:00 UTC → 2026-05-01 01:00 UTC (24h)
---

# Capability Gap Analysis — 2026-05-01 01:07 UTC

## TL;DR

Four gaps detected. **Two have already been surfaced repeatedly to Jared and need decisions, not new agents.** Two are net-new and would benefit from skill (not agent) creation to keep the roster from bloating further.

| # | Gap | Type | Recommendation | Priority | Owner if approved |
|---|-----|------|----------------|----------|-------------------|
| 1 | IT# has no live memory destination | Structural | Pick option A/B/C (already asked) | P0 | Jared decision |
| 2 | `voice-ops-specialist` carry-forward 4+ cycles | Missing agent | Spawn after Jared review | P1 | agent-architect |
| 3 | BOOP scheduler health detection ad-hoc | Missing skill | Create skill, attach to OP# | P2 | capability-curator |
| 4 | Day-3 auto-escalation handoff procedurally fuzzy | Missing skill | Create skill for transition | P3 | capability-curator |

**No new agents proposed in this cycle.** Roster is at ~140 agents; we are saturated. Default to skills. Only Gap #2 warrants a true new agent and that one is already in carry-forward queue.

---

## Signal sources reviewed

- `logs/boop-conductor-2026-04-30-{0405,0604,0705,1710}.md` (4 conductor cycles)
- `logs/routed-items-status/2026-04-30.md` + 3 conductor pre-escalation/decision files
- `inbox/conductor-boop-2026-{04-30,05-01}-findings.md`
- 5 agent-learnings written in last 24h (4× ptt-fullstack, 1× qa-engineer)
- `.claude/scheduled-tasks-state.json` — 54 active BOOPs, fire patterns
- 140 agent manifests in `.claude/agents/` (23 dept-* managers + ~117 specialists)

---

## Gap #1 — IT# memory infrastructure missing (P0, structural)

**Symptom**: `.claude/memory/departments/dept-it-infrastructure/` does not exist. `dept-it-support/` last touched 2026-03-18 (45+ days stale). Brevo DKIM, Morphe trio reconnect, and 777-api items routed to "IT#" hit a write-only delegation chain — no specialist memory accumulates.

**Evidence**:
- `logs/routed-items-status/2026-04-30.md` line: "`dept-it-infrastructure` is uninstantiated. Two of the 6 routes (#4 Brevo DKIM, #5 Morphe trio reconnect) were sent to IT# but IT# has no live memory dir to write into."
- Carry-forward across 4 conductor cycles.

**Why this is not an agent gap**: Conductor already asked Jared `A` (re-route to dept-it-support) / `B` (spawn dept-it-infrastructure) / `C` (drop IT#, route to ST#) on 2026-04-30 13:09 UTC. Open ~12 hours.

**Recommendation**: agent-architect does not duplicate the ask. **Wait for Jared's A/B/C decision.** If `B`, agent-architect creates `dept-it-infrastructure` manager prompt next cycle (full 7-layer registration per agent-creation skill).

---

## Gap #2 — `voice-ops-specialist` agent (P1, carry-forward 4+ cycles)

**Symptom**: Voice/TTS work has no domain owner. Constitutional rule (locked 2026-04-15) bans ElevenLabs and mandates voice.purebrain.ai (Chatterbox at 37.27.237.109:8950) for ALL TTS. Per-customer voice routing is a future-state product. Currently work is ad-hoc — anyone who picks up a voice task does it.

**Evidence**:
- Carry-forward "voice-ops-specialist agent proposal review → Jared" appears across all 4 conductor cycles in last 24h.
- `project_voice_pricing_product.md` defines product but no agent owns operations.
- `feedback_voice_tts_work_filed_to_drive.md` defines filing but no operational owner.

**Recommended scope** (for Jared review):
- **Domain**: Chatterbox GPU operations, voice cloning workflows, per-customer voice_id assignment (when product launches), voice quality QA, TTS fallback logic, voice file Drive filing.
- **Skills granted**: `voice-emotion-detection`, `voice-interview-pipeline`, `script-to-speech-optimization`, plus base.
- **Reports to**: dept-systems-technology (ST#) until volume justifies its own dept.
- **Anti-scope**: Does NOT generate scripts (that's content-specialist) or design voices (that's product-development).

**Action**: Drafting proposal lives in carry-forward queue. agent-architect will not spawn until Jared explicitly approves the proposal — this is a P1 long-pending item, not an emergency.

---

## Gap #3 — BOOP scheduler health detection (P2, missing skill)

**Symptom**: `daily-morning-pulse` (last fire 2026-04-29 19:33) and `daily-eod-triangle-report` (last fire 2026-04-29 19:28) both missed their Apr-30 fire windows by >21 hours. Detection happened only because conductor's 17:10 UTC cycle manually noticed. No automated detection.

**Evidence**: `logs/boop-conductor-2026-04-30-1710.md` finding #5: "Two daily BOOPs overdue".

**Why a skill, not an agent**: We have `operations-analyst` (now owns BOOP scheduler verification per verifier-independence rule) and `aiciv-health-monitor` (for Docker fleet). Adding a 3rd health-monitoring agent = roster bloat. A skill captures the "how" and attaches to the right existing agent.

**Recommended skill**: `boop-scheduler-cadence-check`
- **Inputs**: `.claude/scheduled-tasks-state.json`, current UTC time
- **Logic**: For each task, compute expected next-fire from `cadence` + `last_run`. Flag if `now - expected_fire > 30min` (configurable).
- **Output**: Structured report — overdue list, executor PID alive check (via `pgrep boop_executor`), state file freshness check, recommended action per item.
- **Owner**: operations-analyst (OP#) — already owns BOOP cadence verification.
- **Trigger**: Attach to `engineering-flow-check` BOOP (already runs 60min cadence, OP-adjacent) OR new daily check.

**Action**: agent-architect will route this skill creation to **capability-curator** with the spec above. Capability-curator owns skill lifecycle. Estimated build: <1 day.

---

## Gap #4 — Day-3 auto-escalation handoff (P3, missing skill)

**Symptom**: Per `feedback_execute_authority_greenlit_tasks.md`, when items hit UNVERIFIED ≥3 days, "Primary direct execution authority kicks in." Today (May 1) 6 items hit that threshold simultaneously at ~16:00 UTC. Procedure for the actual handoff is undefined: does Primary auto-execute? Does verifier file a "Primary please execute" note? Does it surface to Jared first?

**Evidence**:
- `inbox/conductor-boop-2026-05-01-findings.md`: 4 of 6 items still need Jared's one-word answer for scope. If no answer, default kicks in. No skill defines the default-execution procedure.
- Multiple memory files reference the rule but none operationalize the moment of handoff.

**Why a skill**: This is procedural codification, not a new owner. The verifier (OP#) already owns the alarm. The conductor already routes. Primary already has the authority. A skill formalizes who does what at the trip moment so it doesn't re-litigate every cycle.

**Recommended skill**: `day3-auto-escalation-handoff`
- **Trigger**: Item UNVERIFIED ≥3 days at verify-BOOP fire time
- **Step 1**: Verifier files Day-3 trip notice to portal (single combined file if multiple items trip simultaneously)
- **Step 2**: Conductor next cycle picks up trip notice, decides per-item: (a) execute with stated default scope, (b) drop if no scope makes sense, (c) re-ping Jared with hard deadline if scope ambiguity blocks
- **Step 3**: Execution receipt filed to `logs/routed-items-status/` with `STATUS: PRIMARY-EXECUTED` or `DROPPED-AT-DAY-3`
- **Owner**: the-conductor (Aether) executes; operations-analyst verifies post-fact.

**Action**: Route to **capability-curator** alongside Gap #3 skill. Both are codifications of existing rules; should ship together.

---

## Roster bloat audit (informational, no action this cycle)

Not strictly a "gap," but worth surfacing: **140 agents is heavy.** Many dept managers have low BOOP attachment and weeks-stale memory dirs. Candidates for review (NOT removal — review):

- `dept-board-advisors`, `dept-karma`, `dept-pure-love`, `dept-pure-capital`, `dept-pure-digital-assets` — low recent activity. May be correct (low-cadence depts) or may indicate unused capacity.
- `dept-it-support` — last activity Mar 18. See Gap #1.
- 16+ legal sub-specialists (delaware, california, florida, immigration, securities, ip, tax, employment, etc.) — appropriate niche depth, no action.

agent-architect proposes: **add a "dept utilization" question to next agent-utilization-boop** (pattern-detector, runs 4hr cadence) so this gets ongoing attention without a new BOOP.

---

## What agent-architect will NOT do this cycle

- **Will not spawn `dept-it-infrastructure`** — Jared decision pending (option B).
- **Will not spawn `voice-ops-specialist`** — Jared review of proposal pending (carry-forward, not blocked on me).
- **Will not skip the agent-creation 7-layer registration** if/when spawning is greenlit (per agent-creation skill, this is constitutional).
- **Will not propose new agents for problems solvable by skills** — roster is saturated, default to skills.

## What's queued for handoff

Two skill creation requests routed to **capability-curator** (next dept-manager-delegation BOOP fire):

1. `boop-scheduler-cadence-check` skill spec (Gap #3 above)
2. `day3-auto-escalation-handoff` skill spec (Gap #4 above)

Both are low-effort codifications of existing patterns. Should ship in 1-2 days from cap-curator.

---

## Cycle outcome

- 0 new agents spawned (correct — saturated roster, dept-level decisions pending)
- 2 skill specs queued for capability-curator
- 1 informational finding logged (roster bloat audit)
- 0 duplicate asks to Jared (Gap #1 + Gap #2 already in conductor queue)
- 1 portal file delivered (this report)

Next capability-gap-analysis BOOP: 2026-05-01 13:00 UTC (12h cadence). Will check whether Gap #1 decision landed and whether capability-curator picked up the 2 skill specs.

---

**Owner**: agent-architect
**Cadence**: twice-daily (per `capability-gap-boop` skill)
**Pairs with**: `pattern-detector/agent-utilization-boop` (4hr cadence — utilization side), `health-auditor/great-health-audit` (collective health side)
