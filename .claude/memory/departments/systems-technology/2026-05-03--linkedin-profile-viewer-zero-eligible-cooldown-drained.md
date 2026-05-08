# LinkedIn Profile Viewer — "0 from 0 eligible" Diagnostic

**Date**: 2026-05-03
**Trigger**: ST# urgent investigation, both 5/3 morning and afternoon batches returned `Selected 0 profiles from 0 eligible`
**Status**: Root cause confirmed, NO FIX shipped yet (diagnose-only BOOP per Jared)

## TL;DR

The script is healthy. The sheet is healthy. Auth is healthy. The 7-day cooldown filter (`REVISIT_COOLDOWN_DAYS = 7`) drained the eligible pool because daily visit throughput (80/day across 3 batches) exceeds the rate at which the 111-profile pool can recycle through the cooldown window.

## Symptoms

- `tools/linkedin_profile_viewer.py --batch morning|afternoon` both log:
  `Selected 0 profiles from 0 eligible (batch size: 30)`
- Yesterday (5/2) all 3 batches ran successfully (24/30, 22/30, 12/12)
- Evening 5/2 already showed strain: `Selected 12 profiles from 12 eligible (batch size: 20)`

## Investigation Method

1. Probed Sheets API metadata — tab `Profile Views` exists, 544 rows × 12 cols, healthy
2. Read header + first 5 rows — structure matches code expectations exactly
3. Read full A2:L1000 range — 111 active data rows
4. Reproduced `read_profile_list()` and `select_profiles()` filter pipeline locally
5. Stepped each filter:
   - `premium == "YES"`: 111/111 pass
   - `url.startswith("http")`: 111/111 pass
   - `last_visited != today`: 111/111 pass
   - `NOT (last_visited > 2026-04-26)`: **0/111 pass** ← here

## Root Cause

**File**: `tools/linkedin_profile_viewer.py:187-188`

```python
if p["last_visited"] and p["last_visited"] > cooldown_cutoff:
    continue
```

- Today (UTC): `2026-05-03`
- Cooldown cutoff: `2026-04-26` (today − 7 days)
- All 111 profiles were last-visited between `2026-04-28` and `2026-05-02`
- 100% blocked by cooldown filter
- Pool drained by recent batch operations

## Last-Visited Distribution (5/3)

| Date | Count |
|------|-------|
| 2026-05-02 | 41 |
| 2026-05-01 | 45 |
| 2026-04-30 | 17 |
| 2026-04-28 | 8 |

## Why It Was Hidden Until Today

- 5/2 evening batch already showed depletion (12 eligible vs 20 batch size)
- Overnight, no new profiles were discovered
- Cooldown cutoff advances 1 day per day; pool of "eligible" shrinks until empty

## Three Fix Options (route to MA#/PD#, not pure ST#)

1. **Discovery-first (recommended)**: Expand pool via `--discover` mode to 300-500 profiles
2. **Tighten cooldown**: 7 → 3 days (one-line config; acceptable per LinkedIn norms)
3. **Throttle daily volume**: 80/day → 40/day (config change)

**Recommendation**: Option 1 primary + Option 2 as bridge. Don't tighten cooldown alone — same ICP seeing daily visits from one viewer = footprint risk.

## Diagnostic Pattern (reusable for future agents)

For any "Selected 0 from 0 eligible" symptom on a sheet-driven script:

1. Probe sheet metadata first (tab existence, row count) — confirms hypotheses 1+2+4
2. Read header + first 5 rows raw — confirms structure
3. Reproduce filter pipeline step-wise locally — pinpoints which filter drops to 0
4. Check date-windowed filters against current date — common drift source

**Counterintuitive teaching**: When throughput approaches pool size × (1/cooldown_days), the system goes from "working great" to "0 eligible" overnight, with no warning. Build a leading-indicator alert: alert when `eligible < 1.5x batch_size` so the pool gets refilled BEFORE it drains.

## Files Referenced

- Script: `/home/jared/projects/AI-CIV/aether/tools/linkedin_profile_viewer.py`
- Filter logic: lines 168-198 (`select_profiles`)
- Read logic: lines 112-143 (`read_profile_list`)
- Log: `/home/jared/projects/AI-CIV/aether/logs/linkedin_profile_viewer.log`
- Sheet: `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4` tab `Profile Views`

## Verification BOOP Recommendation

Per `feedback_routed_items_need_verification_boop.md`, when fix is shipped a separate verifier (operations-analyst) should confirm next-day batch shows `eligible > 0` and at least one successful visit logged.
