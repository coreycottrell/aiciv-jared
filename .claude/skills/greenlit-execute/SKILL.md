---
name: greenlit-execute
description: When Jared explicitly greenlights a task (yes, GO, execute, ship it, proceed, do it), sub-agents MUST execute without re-confirmation. No runbooks. No "I need clarification." Execute + verify + report.
type: override
priority: highest
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# GREENLIT EXECUTION — Override Rule

**When Jared has explicitly greenlit a task**, the following rules are SUPERSEDED for that task:

- `verification-before-completion` → verify the ACTUAL outcome (did the change land?), not "ask before executing"
- `memory-first-protocol` → check memory for precedent, then proceed (don't loop)
- `dept-routing-hook` → if you're the specialist receiving this, execute (don't re-route)
- `delegation-spine` → if you're the specialist, you own this (don't punt back)
- `delegation-enforcer-boop` → about Primary delegation, not about specialists refusing work
- "Aether is Co-CEO not developer" → about Primary workload, not an excuse for specialists to refuse ops work

## What "greenlit" looks like

Explicit Jared language in the dispatch:
- "GO" / "go ahead"
- "yes"
- "ship it" / "execute it" / "do it"
- "proceed"
- "approved"
- Explicit approval on a proposed plan

If the dispatch says "Jared approved", that IS the greenlight. Trust it.

## Your job when greenlit

1. **Execute** — use your tools. SSH, SQL, deploy, whatever the task requires.
2. **Backup-first where applicable** — always `.bak` before destructive changes. This is still required.
3. **Verify** — after execution, run the check (curl, DB query, visual verify).
4. **Report back** — what you did, the evidence it worked, any follow-ups.

## What you do NOT do when greenlit

- Ask for credentials (find them in `.env`, `configs/`, `.credentials/` — if truly missing, report ONCE with exact path needed)
- Produce a runbook "for the human to execute" (you ARE the one executing)
- Re-route to another specialist unless YOUR tools genuinely can't do it
- Cite constitutional rules to punt back (they're suspended for greenlit work)
- Wait for more confirmation

## When to still STOP and ask (high bar)

- Deleting/dropping data (vs updating/archiving) — ASK even if greenlit
- Destructive ops affecting >1 customer or fleet-wide — ASK
- Changes to constitutional docs (CLAUDE.md, TRIO-SHARED-RULES.md) — ASK
- $$$ movement (PayPal, payouts, refunds) — ASK
- "Something feels wrong" → trust that gut, flag, ask

## If delegation chain breaks 2+ times on same task

Primary executes directly. This is the escape hatch, not the default. But it exists.

## Why this rule exists

Over March-April 2026, Aether accreted too many "pause and ask" rules in response to individual incidents. Stacked together, they caused sub-agents to punt instead of execute — paralysis by rule layering. This rule is the explicit override: **when Jared has already approved, execute.**

Added 2026-04-14 by Aether after 4+ stall incidents on a single day.
