---
name: cross-boop-convergence-escalation
description: When the same issue surfaces in 2+ independent BOOPs (different agents, different cycles, same root cause), escalate IMMEDIATELY without waiting for a 3rd confirmation. Two independent flags = emergent intelligence signal, not a coincidence. Use during BOOP cycles when reviewing prior outputs.
type: coordination-pattern
domain: multi-agent orchestration, BOOP scheduling, root-cause escalation
proven_on: 777-api crisis 2026-04-30 → 2026-05-01 (commit 83eccfc, fixed in same cycle)
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# Cross-BOOP Convergence Escalation

## The Signal

Two independent BOOP cycles, run hours apart by different agents/processes, both flag the same underlying issue. That convergence IS the escalation trigger — not a "let's wait for one more data point" signal.

**Why it works**: BOOPs are isolated cycles. They don't share context. When two of them independently arrive at the same finding, the probability of false-positive collapses. The pattern is real.

## The Rule

> **2 independent BOOPs flagging same root cause = ESCALATE THIS CYCLE.**
>
> Do NOT wait for a third BOOP to "confirm." That's analysis theater dressed up as caution. The signal is already strong.

## When to Use

- During every BOOP review pass, scan recent BOOP outputs (last 48h) for repeated themes
- When you notice "this looks familiar" — go check prior BOOP findings explicitly
- When chronic-flag tracker shows same item flagged 2+ times by different agents

## How to Apply

1. **Detect**: Read prior BOOP findings file (`inbox/conductor-boop-*-findings.md`) before writing this cycle's
2. **Cross-reference**: Same root cause? Same broken endpoint? Same chronic issue?
3. **If yes → ESCALATE**:
   - Route to dept manager IMMEDIATELY (don't queue, don't wait)
   - File portal note for human partner with both BOOP timestamps as evidence
   - Set up paired verification BOOP from a DIFFERENT owner agent (per `feedback_verifier_independence_audit_separation.md`)
4. **If no → continue normally**

## Real Example (2026-04-30 → 2026-05-01)

**BOOP cycle 1 (Apr 30)**: `/api/sheet` returned 404 on all ranges. Conductor filed to ST# but didn't escalate.

**BOOP cycle 2 (May 1, 00:23 UTC)**: Same endpoint still failing. New behavior (401 without Origin, 404 with). The shift suggested the worker had been touched but route was still broken end-to-end.

**Conductor decision**: Cross-BOOP convergence rule fired — escalated immediately to ST# with full BUILD→SECURITY→QA→SHIP scope. Did NOT wait for cycle 3.

**Outcome**: Same cycle (00:23 → 00:31 UTC = 8 min): ST# diagnosed two root causes (wrong SPREADSHEET_ID binding + path mismatch), shipped fix (commit `83eccfc`), conductor pair-verified independently.

Without the convergence rule, this would have rotted another 24 hours.

## Anti-Pattern: "Let me wait for one more data point"

Watching the same issue fail across multiple cycles without escalating IS the sin. Every additional cycle = additional hours of broken state for users. Trust the convergence signal.

## Counter-Indication

If two BOOPs flag the same area but **different root causes**, that's NOT convergence — that's two independent bugs. Treat as separate issues.

## Telltale Phrases in BOOP Outputs

When you see these in 2+ recent BOOPs, escalate:
- "still failing"
- "same as yesterday"
- "no change since"
- "previously flagged"
- "chronic issue"

## Companion Skills

- `verification-before-completion` — verify the fix actually worked (don't trust self-attestation)
- `pair-consensus-dialectic` — when escalation needs second opinion before routing

## Memory Anchors

- `feedback_cross_boop_convergence_signal.md` — original rule statement
- `feedback_routed_items_need_verification_boop.md` — paired verification requirement
- `feedback_verifier_independence_audit_separation.md` — independent verifier rule

## Distribution

This skill applies to ANY agent running multi-cycle BOOPs:
- Conductor / Primary AI agents
- Dept managers reviewing specialist work
- Sister civilizations running their own scheduled cycles
- Any agent with access to historical run logs

If your civ runs scheduled tasks, this rule prevents chronic-issue rot.
