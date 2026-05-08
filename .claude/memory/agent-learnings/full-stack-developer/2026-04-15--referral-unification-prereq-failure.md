# Referral D1 Unification — Prereq Failure Before Execute

**Date**: 2026-04-15
**Agent**: full-stack-developer
**Type**: operational
**Outcome**: Punted back before any edits

## Task
Execute 1A-1D of referral D1 unification (admin→D1, portal Refer&Earn→D1, auto-provision on signup, daily reconciliation) per brief at `.claude/memory/agent-learnings/dept-systems-technology/2026-04-15--referral-unification-brief.md`.

## Why I stopped

### 1. Brief file does not exist
Searched `.claude/memory/agent-learnings/` for `*referral-unification*`, `*referral*brief*`, and `2026-04-15*` in dept-systems-technology folder. Zero matches. The delegation message summarized 4 tasks but the authoritative brief (schemas, method sigs, flag defaults, migration plan for existing 68KB of data) is missing.

### 2. Backup target in the delegation is wrong
Brief said `cp /home/jared/purebrain_portal/portal.db portal.db.bak-...`. Reality:
- `portal.db` = 0 bytes (empty stub, Apr 12)
- `referral.db` = 0 bytes (empty stub, Mar 17)
- **Actual data**: `referrals.db` (68K, Apr 14 20:08) + `clients.db` (36K, Apr 15 13:47)

Following the brief literally would back up nothing. Either ST# has stale filenames or there's a migration that already happened and the delegation hasn't been updated.

### 3. No sqlite3 on host
Can work around via Python stdlib, but flagged.

## What I verified
- `/home/jared/purebrain_portal/referrals_d1_client.py` exists (5.6KB, Apr 15 10:13)
- `custom/routes.py` shim pattern in place
- `workers/referrals-api/` exists

## Lesson for future fullstack tasks
When a greenlit task cites a brief path, verify the brief EXISTS before treating delegation message as the full spec. A summary-in-delegation is not a substitute for the brief — especially on $$$ systems (referrals = commission payments).

The execute-authority rule explicitly lists "$$$ movement" and "something feels wrong" as valid stop conditions. Both triggered here.

## Minimum-risk re-entry path (if Jared says "proceed anyway")
1. Backup the REAL files: `referrals.db` + `clients.db`
2. Implement only 1A (flag-gated admin read path)
3. Live-test + re-report before touching 1B/1C/1D

## Files NOT touched (intentional)
- `portal_server.py` (382KB — brief said don't edit directly anyway)
- `referrals_d1_client.py`
- `custom/routes.py`
- `workers/referrals-api/src/worker.js`
- No deploys, no restarts, no wrangler, no migrations
