---
title: HANDOFF — Routed Items Status Verification BOOP (Proposal)
date: 2026-04-29
from: dept-corporate-org (CO#)
to: jared
type: governance-proposal
status: AWAITING APPROVAL — do not modify scheduled-tasks-state.json until Jared signs off
---

# Routed Items Status Verification BOOP — Proposal

## FIRST THING

Jared, read sections **The Ask**, **What Already Exists**, and **Recommendation**. The BOOP is already registered and ran its first backfill today. The decision in front of you is **owner & escalation policy**, not "should we build this." Two questions for you at the bottom — one-word answers move this to live.

---

## The Ask (from the conductor's BOOP routing)

The Apr 29 nightly self-analysis flagged a real organizational gap:

> 6 items routed Apr 28 evening (Fleet Grounding → ST#, Lyra affiliate kit → ST#, Mireille scheduler → ST#, Brevo DKIM → IT#, Morphe trio reconnect → IT#, Thread Mark cleanup → external). **None had a confirmed status update 24h later.** Routes become void if not verified.

The conductor routed to CO# (corporate process design): **propose a daily verification BOOP that closes the loop on routed items**.

Without this loop, the dept-manager-delegation BOOP is write-only and "analysis theater" creeps from agent-level up to org-level.

---

## What Already Exists (don't rebuild)

When CO# went to spec this, the BOOP **was already registered** in `.claude/scheduled-tasks-state.json` under the name `routed-items-status-verification`. First run executed today and produced the backfill at `logs/routed-items-status/2026-04-29.md`.

Current registered definition:

```json
{
  "name": "routed-items-status-verification",
  "frequency": "daily",
  "last_run": "2026-04-29T00:00:00Z",
  "status": "active",
  "category": "quality",
  "agent": "the-conductor",
  "schedule_slot": "Daily ~13:00 UTC (09:00 EST), post-morning-pulse",
  "description": "Daily verification BOOP - close the loop on routed items. Read last 7 days of logs/nightly-self-analysis/*.md, extract all routed items (ST#, MA#, SD#, PD#, OP#, CO#, LC#, AF#, HR#, PR#, IR#, IT#, PT#, PMG# tags), verify each against existing surfaces (git log, portal_server.log, agent memories, file mtimes) - NO new infrastructure, no spreadsheet. Status states: SHIPPED/IN-PROGRESS/BLOCKED/UNVERIFIED/DROPPED. Auto-escalate per feedback_execute_authority_greenlit_tasks.md: IN-PROGRESS >3d -> direct Primary execution; BLOCKED no-escalation -> Primary; UNVERIFIED >=3d -> mark DROPPED + Primary direct hit. Output: logs/routed-items-status/YYYY-MM-DD.md (table, <=30 lines). Notify portal+telegram ONLY if escalations exist (no quiet-day noise). Update .claude/scratch-pad.md under RECENT BOOPS. Pairs with dept-manager-delegation BOOP (route-side); this is the read/verify-side."
}
```

The first artifact (today's backfill) is solid — table format, per-item detail, escalation thresholds documented, all 6 Apr 28 items captured at `UNVERIFIED, day 1, no auto-escalation yet`.

So the question isn't "should we build this" — it's **"is this version of it the right one?"**

---

## What's Strong About the Current Definition

1. **Pairs explicitly with `dept-manager-delegation` BOOP** — route-side and verify-side are identified as a pair. Symmetry.
2. **No new infrastructure** — reads existing surfaces (git log, portal log, agent memories, file mtimes) instead of building a tracker DB. Constitutional fit with "nothing in containers" / "build software not state."
3. **Quiet-day discipline** — only notifies portal/Telegram if escalations exist. Avoids notification fatigue.
4. **Concrete escalation rules with day thresholds** — IN-PROGRESS >3d, UNVERIFIED ≥3d, BLOCKED with no escalation → all trigger direct Primary execution per the greenlit-execute authority memory.
5. **Bounded output** — table ≤30 lines, scratchpad update, log persisted by date. No sprawl.

## What's Weak / Open Questions

**1. Owner: `the-conductor` is doing the verifying on items it (likely) routed.**

This is the constitutional smell. The route-side BOOP is owned by the-conductor. The verify-side BOOP is also owned by the-conductor. Self-marking homework. CO#'s recommendation: move ownership to **`operations-analyst`** under `dept-operations-planning` (OP#).

Rationale:
- `operations-analyst` manifest literally says: *"Process audit and optimization across all departments... Bottleneck identification and resolution... if it's not written down, it doesn't exist."* Exact fit.
- Independence from the routing function = real audit, not self-attestation.
- Keeps the-conductor focused on active conducting, not verifying its own homework.

**2. Cadence timing.**

Currently scheduled 13:00 UTC (09:00 EST). The conductor's BOOP `dept-manager-delegation` fires 3x daily at ~06:00 / ~14:00 / ~22:00 UTC. Conductor's ask was "30min after dept-manager-delegation fires." If we're verifying routes from yesterday's nightly self-analysis (which writes ~03:00), verifying once daily at 13:00 UTC catches:
- Yesterday's nightly self-analysis (03:00) — items have ~10h to ship
- Yesterday afternoon's 14:00 dept-manager-delegation — items have ~23h
- Yesterday evening's 22:00 dept-manager-delegation — items have ~15h

That's reasonable. CO# recommends **keeping daily cadence** rather than adding 3x daily noise. Daily-table-with-3-day-thresholds is the right granularity. Dept managers are not building hourly.

**3. What counts as a "routed item"?**

Currently spec parses ST#/MA#/SD#/etc tags from `nightly-self-analysis/*.md`. But routes also happen via:
- Direct dept-manager invocations (Agent tool calls — captured where?)
- Telegram threads with Jared (`tg_send.sh` history)
- Handshake Queue (`/home/aiciv/shared/handshake-queue.md`)
- Portal messages

CO# recommends **scope discipline** — V1 only reads `logs/nightly-self-analysis/*.md` and the dept-manager-delegation BOOP outputs. Don't try to scrape the whole org in V1. Expand sources only if items are getting missed.

**4. Stop condition.**

Spec says "item resolved → drop from tracker; item abandoned with reason → drop with note." But there's no explicit dropped-items archive. CO# recommends:
- Resolved items: log final SHIPPED status one last day, then drop
- DROPPED items (≥3d UNVERIFIED): log final DROPPED status with reason note + direct-Primary-action note, then drop
- Both cases: a one-line entry per drop in `logs/routed-items-status/_archive.md` for trend analysis (which dept manager has highest drop rate, etc.)

---

## Recommendation (3 changes to the existing BOOP)

| # | Change | Reason |
|---|--------|--------|
| 1 | Owner: `the-conductor` → **`operations-analyst`** (under OP#) | Independent audit. Constitutional smell of self-marking. |
| 2 | Add stop-condition archive: append final state to `logs/routed-items-status/_archive.md` before dropping | Trend tracking on drop rates per dept manager |
| 3 | V1 scope: only `nightly-self-analysis/*.md` + `dept-manager-delegation` outputs as input sources | Discipline — don't scrape the whole org until V1 proves it works |

**No change to**: cadence (daily 13:00 UTC), output path, escalation thresholds, quiet-day discipline, table format. Those are all sound.

---

## Proposed Updated BOOP Definition (ready to drop into `.claude/scheduled-tasks-state.json`)

```json
"routed-items-status-verification": {
  "name": "routed-items-status-verification",
  "frequency": "daily",
  "last_run": "2026-04-29T00:00:00Z",
  "status": "active",
  "category": "quality",
  "agent": "operations-analyst",
  "owner_dept": "dept-operations-planning",
  "schedule_slot": "Daily ~13:00 UTC (09:00 EST), post-morning-pulse",
  "description": "Daily routed-items verification. Owner: operations-analyst (independent audit, not self-attestation). V1 SCOPE: read last 7 days of logs/nightly-self-analysis/*.md AND dept-manager-delegation BOOP outputs. Extract all routed items (ST#, MA#, SD#, PD#, OP#, CO#, LC#, AF#, HR#, PR#, IR#, IT#, PT#, PMG# tags). Verify each against existing surfaces (git log, portal_server.log, agent memories, file mtimes) - NO new infrastructure, no spreadsheet. Status states: SHIPPED/IN-PROGRESS/BLOCKED/UNVERIFIED/DROPPED. Auto-escalate per feedback_execute_authority_greenlit_tasks.md: IN-PROGRESS >3d -> direct Primary execution; BLOCKED with no escalation -> Primary; UNVERIFIED >=3d -> mark DROPPED + Primary direct hit. STOP CONDITION: SHIPPED items log one final day then drop; DROPPED items get final entry with reason + Primary-action note. Both append one-line summary to logs/routed-items-status/_archive.md before dropping (for trend tracking on dept drop rates). Output: logs/routed-items-status/YYYY-MM-DD.md (table, <=30 lines). Notify portal+telegram ONLY if escalations exist (no quiet-day noise). Update .claude/scratch-pad.md under RECENT BOOPS. Pairs with dept-manager-delegation BOOP (route-side); this is the independent read/verify-side."
}
```

---

## Two Questions for Jared

**Q1: Owner.** `the-conductor` (status quo, already running) OR `operations-analyst` under OP# (CO# recommended, independent audit)?

**Q2: V1 scope.** OK with V1 reading only `nightly-self-analysis` + `dept-manager-delegation` BOOP outputs — and expanding source coverage only if we observe items being missed? Or do you want broader scope (Handshake Queue, Telegram threads, portal messages) from day one?

One-word answers fine. Once you respond, CO# updates `.claude/scheduled-tasks-state.json` (or leaves it status-quo) and writes the change to memory.

---

## Files / Paths

- This proposal: `/home/jared/projects/AI-CIV/aether/to-jared/HANDOFF-2026-04-29-routed-items-verification-boop.md`
- Existing BOOP definition: `/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json` (key: `routed-items-status-verification`)
- First backfill artifact: `/home/jared/projects/AI-CIV/aether/logs/routed-items-status/2026-04-29.md`
- Source self-analysis (the gap that flagged it): `/home/jared/projects/AI-CIV/aether/logs/nightly-self-analysis/2026-04-29.md`
- Pair BOOP (route-side): `dept-manager-delegation` (8h cadence, the-conductor)
- Recommended owner manifest: `/home/jared/projects/AI-CIV/aether/.claude/agents/operations-analyst.md`
- OP# parent dept: `/home/jared/projects/AI-CIV/aether/.claude/agents/dept-operations-planning.md`
- Constitutional reference: `feedback_execute_authority_greenlit_tasks.md` (escalation rules)
- Constitutional reference: `feedback_analysis_theater_anti_pattern.md` (the gap this closes)
- Constitutional reference: `feedback_self_analysis_commitments_need_delegation.md` (why this proposal exists at all)

---

## Implementation Steps (after Jared approves)

1. **CO# updates** `.claude/scheduled-tasks-state.json` with the agreed owner + scope changes (ST# touches the JSON if file edit needed; CO# handles the policy decision).
2. **CO# writes a memory** at `.claude/memory/agent-learnings/dept-corporate-org/2026-04-29--routed-items-verification-policy.md` capturing the design decision and reasoning.
3. **OP# (if owner change approved)** briefs `operations-analyst` on the role: read-side independent auditor, paired with dept-manager-delegation, escalation rules, output path.
4. **Tomorrow's first BOOP run** (Apr 30, 13:00 UTC) is the live test — same 6 items from Apr 28, now at day 2, watch for any approaching the 3-day escalation threshold.
5. **Within 7 days** CO# checks: did any item get caught + escalated? Did any get dropped silently? Did the BOOP catch routes not surfaced in nightly-self-analysis (gap in V1 scope)? Iterate.

---

## Dependencies

- **OP# (dept-operations-planning)**: receives owner role for `operations-analyst` if Q1 = operations-analyst.
- **The Conductor**: gives up ownership of verify-side if Q1 = operations-analyst (still owns route-side via `dept-manager-delegation`). Cleaner separation.
- **No infrastructure dependency** — uses existing surfaces (git log, portal log, agent memories, file mtimes). No DB, no spreadsheet, no new container.

---

## CO# Sign-off

Process design rationale recorded. Awaiting Jared's two answers to move this to live.

— dept-corporate-org (CO#)
2026-04-29
