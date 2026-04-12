# BOOP Scheduler Stagger Fix

**Date**: 2026-02-24
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Fixing simultaneous BOOP execution via last_run timestamp staggering

---

## Problem

All scheduled BOOPs (12 sub-hourly tasks) were firing simultaneously at 00:01-00:04 UTC because:
- The scheduler checks which tasks are overdue
- On first startup / after a reset, ALL tasks show as overdue
- The system runs ALL overdue tasks back-to-back in the same cycle

## Root Cause

`last_run` timestamps in `.claude/scheduled-tasks-state.json` were all set to nearly the same time (00:01-00:04 UTC on 2026-02-24), making every task appear overdue at the same moment.

## Fix Applied

### 1. Staggered last_run timestamps

Calculated backward from reference time `2026-02-24T00:30:00Z` to spread first-due times across 3 hours:

| Task | Freq | last_run set to | First due at |
|------|------|-----------------|--------------|
| engineering-flow-check | 30min | 00:00 | 00:30 |
| delegation-enforcer | 25min | 00:10 | 00:35 |
| telegram-health-boop | 30min | 00:15 | 00:45 |
| email-check-boop | 60min | 00:00 | 01:00 |
| bsky-presence-boop | 60min | 00:30 | 01:30 |
| context-window-boop | 90min | 23:45 (Feb 23) | 01:15 |
| memory-write-boop | 2hr | 23:00 (Feb 23) | 01:00 |
| content-pipeline-boop | 2hr | 23:30 (Feb 23) | 01:30 |
| sales-pulse-boop | 2hr | 00:00 | 02:00 |
| sister-collective-boop | 4hr | 21:00 (Feb 23) | 01:00 |
| security-posture-boop | 4hr | 22:00 (Feb 23) | 02:00 |
| agent-utilization-boop | 4hr | 23:00 (Feb 23) | 03:00 |

### 2. Added boop_rules top-level key

```json
"boop_rules": {
  "max_tasks_per_cycle": 3,
  "min_interval_between_tasks_seconds": 60,
  "priority_order": [...],
  "stagger_note": "Tasks are intentionally staggered via last_run offsets..."
}
```

### 3. Did NOT change

- Task descriptions, frequencies, agents, or categories
- Hype boop schedule arrays (acgee-hype-boop, parallax-lyra-hype-boop)
- Daily/weekly/monthly task last_run values

## File Modified

`/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json`

## Key Lesson

When resetting or initializing a BOOP scheduler, NEVER set all last_run values to the same time. Spread them across the full frequency window so tasks naturally distribute across time. The stagger should be proportional to the task frequency.
