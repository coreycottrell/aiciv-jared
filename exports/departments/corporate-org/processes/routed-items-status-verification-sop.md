---
title: Routed Items Status Verification — BOOP SOP
department: Corporate & Organizational (CO#)
owner: the-conductor (Aether)
delegated_implementation: ST# (scheduler infra), CO# (process design)
created: 2026-04-29
status: ACTIVE — first run completed 2026-04-29 (one-time backfill); daily cadence starts 2026-04-30
parent_skill: routed-items-status-verification
---

# Routed Items Status Verification — Standard Operating Procedure

## 1. Purpose

Close the **write-only delegation queue** anti-pattern flagged in the 2026-04-29 nightly self-analysis (Sec 5: "6 items routed Apr 28 evening, no follow-up BOOP today checking … Routes become void if not verified").

This BOOP forces every routed item through a daily **read-and-verify** loop until it reaches a terminal state (shipped, dropped, or escalated).

## 2. Constitutional Anchors

- `feedback_execute_authority_greenlit_tasks.md` — Primary executes directly when delegation chain breaks 2+ times on same task.
- `feedback_analysis_theater_anti_pattern.md` — flagging without routing/verifying is theater.
- `feedback_self_analysis_commitments_need_delegation.md` — every commitment must convert to a delegated/scheduled action in the same session.

## 3. Cadence

| Setting | Value |
|---|---|
| Frequency | `daily` |
| Schedule slot | ~16:00 UTC (afternoon — gives morning routes time to land) |
| Owning agent | `the-conductor` |
| Category | `quality` |
| Override max-daily | No (counts toward the 2-per-cycle cap) |

## 4. Inputs

Each fire reads:

1. `logs/nightly-self-analysis/*.md` — last 72 hours, sections naming routes by trigger (ST#, MA#, SD#, PD#, OP#, LC#, AF#, HR#, PR#, IR#, IT#, CO#, PT#, PMG#, CB#, etc.).
2. `logs/routed-items-status/*.md` — last 7 days of prior status reports (carry-forward of still-open items).
3. `.claude/scheduled-tasks-state.json` — context on `dept-manager-delegation` cadence.
4. Portal/git/D1 surfaces for evidence (commits, deploys, spreadsheet rows, BOOP results) when verifying status claims.

## 5. Per-item Status Schema

Each item gets exactly one of:

| Status | Meaning | Verification Evidence |
|---|---|---|
| `SHIPPED` | Done, evidence verified | Commit / deploy URL / spreadsheet row / portal report |
| `IN-PROGRESS` | Acknowledged + active | Dept-manager status query response, partial commits |
| `BLOCKED` | Acknowledged + waiting on dependency | Stated blocker (creds, decision, external) |
| `UNVERIFIED` | No status from receiving dept | (Default; triggers age clock) |
| `DROPPED` | Closed without ship (with reason) | Memory note + reason |
| `ESCALATED` | Bumped to Primary direct execution | Per execute-authority rule |

## 6. Escalation Logic

Auto-escalate to Primary direct execution when:

- `UNVERIFIED` for **3+ days** AND no acknowledgement from receiving dept manager, OR
- `BLOCKED` for **2+ days** with no escalation note from the dept manager, OR
- The same item appears in **2+ consecutive** routed-items-status reports without status change.

Escalation action: Primary takes the task per `feedback_execute_authority_greenlit_tasks.md` (greenlit-execute) — no further routing loops.

## 7. Outputs

Each run produces:

1. **`logs/routed-items-status/YYYY-MM-DD.md`** — markdown table (columns: # | Item | Receiving Dept | Routed | Status | Days Open | Action) + per-item detail block + auto-escalation summary.
2. **Portal status table** — top-3 items needing attention surfaced via tg_send / portal file delivery (kept brief — no spam).
3. **Scratch-pad update** — `.claude/scratch-pad.md` "ROUTED ITEMS WATCH" section (top 5 oldest open items with dept + days-open + status).
4. **Memory write** — `.claude/memory/agent-learnings/the-conductor/YYYY-MM-DD--routed-items-status.md` (operational type) noting any patterns: chronic dept slowness, repeated escalations, dept managers consistently silent.

## 8. Telegram/Portal Reporting Rules

- ONLY report items hitting threshold (escalation, 2+ days open) — no daily noise for healthy queue.
- If queue is clean (all items SHIPPED or <2 days open), single-line summary: "Routed items: N open, 0 escalations, oldest M days."
- Per `feedback_portal_is_primary_not_telegram.md`: rich report → portal; brief signal → Telegram.

## 9. Implementation Status

| Component | Status | Location |
|---|---|---|
| Slot in `priority_order` list | DONE | `.claude/scheduled-tasks-state.json:17` |
| Slot definition | DONE | `.claude/scheduled-tasks-state.json:576-584` |
| Output directory | DONE | `logs/routed-items-status/` |
| First-run backfill | DONE | `logs/routed-items-status/2026-04-29.md` (6 items from Apr 28 logged) |
| BOOP firing infra | EXISTING | `tools/boop_executor.py` (no new script needed — generic BOOP daemon picks up the slot, prompt = description, agent = the-conductor) |
| Daily cadence active | STARTS 2026-04-30 ~16:00 UTC | first scheduled fire |

**No standalone Python script needed.** The existing `boop_executor.py` daemon reads `scheduled-tasks-state.json`, resolves `frequency: daily` + `agent: the-conductor`, builds the prompt from `description`, and fires a background Claude Code agent. The conductor agent then performs the read-verify-report-escalate loop using the inputs/outputs in this SOP.

## 10. Failure Modes & Mitigation

| Failure | Mitigation |
|---|---|
| BOOP daemon down | `aether-session.service` auto-restart + telegram alert if no fire by 18:00 UTC |
| Dept manager never responds for N days | Auto-escalation rule triggers Primary direct execution |
| Self-analysis log missing | Falls back to prior `routed-items-status/*.md` carry-forward |
| Receiving dept claims SHIPPED falsely | Verification evidence column in schema enforces proof — no "should be done" allowed (`verification-before-completion` skill) |
| Conductor agent claims UNVERIFIED for everything (lazy fire) | Cross-check: if zero status changes 3 days running, agent-architect reviews the BOOP for quality drift |

## 11. Cross-Department Dependencies

| Dept | Role |
|---|---|
| ST# | Owns multi-customer build queue items (most routes land here) |
| MA# | Owns marketing routes |
| IT# | Owns infrastructure/credential routes |
| All other dept managers | Owe status responses on items routed to them |
| CO# (this SOP) | Owns the verification process itself |
| The-conductor | Owns the daily fire and escalation decisions |

## 12. Review Cadence

CO# reviews this SOP **monthly** for:
- Threshold tuning (3-day rule still right? Faster/slower?)
- Escalation pattern audit (which depts chronically miss SLA?)
- Output noise level (portal/telegram signal vs spam)

First scheduled review: **2026-05-29**.

---

## Implementation Steps

1. **DONE — 2026-04-29 04:09 UTC**: Slot registered in `.claude/scheduled-tasks-state.json` `priority_order` + `tasks` map.
2. **DONE — 2026-04-29 04:11 UTC**: Backfill `logs/routed-items-status/2026-04-29.md` filed against the 6 Apr 28 routes.
3. **DONE — 2026-04-29 04:12 UTC**: SOP filed at `exports/departments/corporate-org/processes/routed-items-status-verification-sop.md`.
4. **PENDING — 2026-04-30 ~16:00 UTC**: First scheduled daily fire. Verify outputs match this SOP (table + per-item detail + memory write).
5. **2026-05-29**: First monthly SOP review.

## Dependencies

- ST# / IT# / MA# / SD# / PD# / OP# / LC# / AF# / HR# / PR# / IR# / CB# / PT# / PMG# dept managers all owe status responses to the-conductor when queried.
- `dept-manager-delegation` BOOP (every 8h) feeds new routes into the input pool.
- `boop_executor.py` daemon must be running for the fire to land.

## Files

- SOP: `/home/jared/projects/AI-CIV/aether/exports/departments/corporate-org/processes/routed-items-status-verification-sop.md`
- Slot definition: `/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json` (lines 17, 576-584)
- First backfill: `/home/jared/projects/AI-CIV/aether/logs/routed-items-status/2026-04-29.md`
- Output dir (ongoing): `/home/jared/projects/AI-CIV/aether/logs/routed-items-status/`
- BOOP daemon: `/home/jared/projects/AI-CIV/aether/tools/boop_executor.py`
