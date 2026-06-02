---
status: provisional
tick_count: 0
last_used: 2026-05-31
introduced: 2026-05-31
---
# Skill: BOOP Executor Scheduler

## Purpose

Priority-based BOOP slot allocation to prevent task starvation. When 53+ tasks compete for MAX_CONCURRENT_BOOP_AGENTS slots (default 3), lower-priority tasks get skipped indefinitely. This skill implements tiered scheduling: constitutional tasks get reserved slots, long-running tasks get timeouts, and off-peak hours get expanded capacity.

## When to Use

- performance-optimizer analyzing BOOP executor efficiency
- conductor-of-conductors detecting task skip patterns
- Any agent diagnosing why scheduled BOOPs fail to fire

## Priority Tiers

| Tier | Examples | Slot Policy |
|------|----------|-------------|
| P0 (Constitutional) | email-check, infra-health, delegation-enforcer | Reserved slot — always runs |
| P1 (Revenue) | payment-pipeline-health, onboarding-guard | Pre-empt P2 if needed |
| P2 (Operational) | conductor-of-conductors, overnight-v3 | Standard scheduling |
| P3 (Enhancement) | profile-viewing, tool-discovery, skill-sync | Best-effort, skip gracefully |

## Steps

### 1. Diagnose Current Contention

```bash
# Count active BOOP agents
pgrep -f "boop_executor" | wc -l

# Check scheduled-tasks-state.json for skip patterns
python3 -c "
import json
state = json.load(open('.claude/scheduled-tasks-state.json'))
tasks = state.get('tasks', {})
for name, t in tasks.items():
    skipped = t.get('skippedCount', 0)
    if skipped > 0:
        print(f'{name}: skipped {skipped}x')
"

# Check executor slot utilization over 24h
grep -c "Starting BOOP" logs/boop_executor.log | tail -1
grep -c "Skipping.*concurrent" logs/boop_executor.log | tail -1
```

### 2. Apply Priority-Based Scheduling

```python
PRIORITY_TIERS = {
    'P0': ['email-check-boop', 'infra-health-boop', 'delegation-enforcer-boop'],
    'P1': ['payment-pipeline-health', 'onboarding-guard-nightly'],
    'P2': ['conductor-of-conductors', 'overnight-v3-master'],
    'P3': ['profile-viewing-morning', 'nightly-tool-discovery', 'daily-hub-skill-sync']
}

TIMEOUT_OVERRIDES = {
    'email-check-boop': 90 * 60,       # 90min (was 4h default)
    'conductor-of-conductors': 45 * 60,  # 45min
    'overnight-v3-master': 120 * 60,     # 2h (legitimately long)
}

MAX_SLOTS = {
    'peak': 3,       # 12:00-00:00 UTC (Jared awake)
    'off_peak': 5,   # 00:00-12:00 UTC (overnight)
}
```

### 3. Validate Improvement

After applying changes, verify over 24h cycle:
- P0 tasks: 0 skips (was N skips)
- P3 tasks: skip rate < 20% (was 100% for some)
- No memory pressure increase (monitor with `free -h`)

## Gotchas

- Raising MAX_CONCURRENT during off-peak is safe only if disk stays <95%
- CoC hourly cadence can drop to 2h on weekends (steady state) — saves 12 slot-hours/day
- email-check 4h timeout is the #1 slot consumer — 90min timeout is aggressive but covers 95% of runs
- NEVER pre-empt P0 tasks — they are constitutional infrastructure

## Origin

Identified by agent-architect capability gap analysis 2026-05-31. Root cause: 53 tasks / 3 slots = 17.6x oversubscription. 29% of slot-hours consumed by CoC alone.
