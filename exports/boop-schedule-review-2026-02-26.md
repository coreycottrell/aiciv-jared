# BOOP Schedule Review — 2026-02-26

## PROOF: Old Spam Sources ELIMINATED

### Systemd Timers: ALL REMOVED
```
BEFORE (causing spam):
- aether-boop-30min.timer   ← every 30 min!
- aether-boop-60min.timer   ← every hour!
- aether-boop-2hr.timer     ← every 2 hours
- aether-boop-4hr.timer     ← every 4 hours
- aether-boop-daily.timer   ← daily
- aether-boop-weekly.timer  ← weekly
- aether-boop-log-cleanup.timer ← daily

AFTER: ZERO systemd timers. All stopped, disabled, removed.
```

### Crontab: Fixed
```
BEFORE: 0 * * * *  (EVERY HOUR = 24 fires/day)
AFTER:  0 13,1 * * *  (8am + 8pm EST only = 2 fires/day)
```

### Script Enforcement: Hard Limit Added
```
MAX_BOOPS_PER_DAY=2
MIN_HOURS_BETWEEN_BOOPS=10
```
Even if cron fires more, the script exits early if limits are hit.

### Dead Sessions: Cleaned
```
BEFORE: 7 tmux sessions (1,2,3,5,6,8,aether-unified)
AFTER:  1 tmux session (8 — current active)
```

---

## CURRENT STATE: Only 2 Cron Jobs Remain

| Cron | What | When (UTC) | When (EST) |
|------|------|-----------|-----------|
| `autonomy_nudge.sh` | BOOP trigger | 01:00 + 13:00 | 8pm + 8am |
| `intent_engine/run_daily.sh` | Daily intent | 13:00 | 8am |

---

## PROPOSED NEW BOOP SCHEDULE

### How It Works Now
- Cron fires `autonomy_nudge.sh` at **8am EST** and **8pm EST**
- Script injects a BOOP message into tmux session
- Claude wakes up and checks `scheduled-tasks-state.json`
- Runs **max 2 tasks per BOOP cycle** (most overdue first)
- So max **4 tasks per day** (2 cycles x 2 tasks each)

### TWICE-DAILY Tasks (run at AM + PM BOOP)

| # | Task | Agent | AM Slot | PM Slot | What It Does |
|---|------|-------|---------|---------|-------------|
| 1 | email-check | human-liaison | 8:00am | 8:00pm | Check Jared's inbox |
| 2 | telegram-health | tg-bridge | 8:00am | 8:00pm | Verify bridge alive |
| 3 | engineering-flow-check | engineering-team | 8:00am | 8:00pm | Verify BUILD→SECURITY→QA→SHIP |
| 4 | delegation-enforcer | the-conductor | 8:00am | 8:00pm | Am I delegating or hoarding? |
| 5 | bsky-presence | bsky-manager | 8:00am | 8:00pm | Bluesky engagement check |
| 6 | context-window | doc-synthesizer | 8:00am | 8:00pm | Token usage monitor |
| 7 | memory-write | doc-synthesizer | 8:00am | 8:00pm | Write learnings to memory |
| 8 | content-pipeline | content-specialist | 8:00am | 8:00pm | Blog content progress |
| 9 | sales-pulse | sales-specialist | 8:00am | 8:00pm | New leads/payments check |
| 10 | sister-collective | collective-liaison | 8:00am | 8:00pm | A-C-Gee comms check |
| 11 | security-posture | security-engineer-tech | 8:00am | 8:00pm | Review new code for security |
| 12 | agent-utilization | pattern-detector | 8:00am | 8:00pm | Agent usage balance |
| 13 | capability-gap-analysis | agent-architect | 8:00am | 8:00pm | Identify capability gaps |

**Note:** With max 2 tasks per cycle, only the 2 most overdue will fire each BOOP. The rest wait for next cycle. Over a day, all 13 rotate through.

### DAILY Tasks (run once per day, checked at AM BOOP)

| # | Task | Agent | When | What It Does |
|---|------|-------|------|-------------|
| 14 | morning-consolidation | result-synthesizer | ~8am | Synthesize yesterday's learnings |
| 15 | intel-scan | web-researcher | ~8am | AI news, competitor intel |
| 16 | jared-ping | result-synthesizer | ~8am | Daily status summary to Jared |
| 17 | integration-audit | integration-auditor | ~8am | Check deliverables are discoverable |
| 18 | linkedin-pipeline | linkedin-writer | ~8am | LinkedIn content queue |
| 19 | paper-scan | web-researcher | ~8am | Daily arXiv scan |
| 20 | purebrain-metrics | data-scientist | ~8am | Business metrics dashboard |

### NIGHTLY Task

| # | Task | Agent | When | What It Does |
|---|------|-------|------|-------------|
| 21 | nightly-site-improvement | full-stack-developer | ~10pm | SEO/GEO/AIO improvements |

### WEEKLY Tasks

| # | Task | Agent | When | What It Does |
|---|------|-------|------|-------------|
| 22 | calculator-tool-discovery | web-researcher | Tuesday | Add new AI tools to calculator |
| 23 | paper-digest | web-researcher | Monday | Full paper analysis + digest |
| 24 | agent-performance-review | health-auditor | Wednesday | Agent quality review |
| 25 | strategic-alignment | strategy-specialist | Friday | Weekly vs strategy check |

### MONTHLY Tasks

| # | Task | Agent | When | What It Does |
|---|------|-------|------|-------------|
| 26 | great-health-audit | health-auditor | ~21st | Full collective health audit |
| 27 | business-model-review | strategy-specialist | ~1st | Revenue/pricing analysis |

---

## SUMMARY

| Frequency | Count | Max Fires/Day |
|-----------|-------|---------------|
| Twice-daily | 13 tasks | 2 per task (but only 2 run per cycle) |
| Daily | 7 tasks | 1 per task |
| Nightly | 1 task | 1 |
| Weekly | 4 tasks | ~0.14 |
| Monthly | 2 tasks | ~0.03 |

**Total BOOP interruptions to Jared on Telegram: 0**
BOOPs are internal — they trigger Claude to do work, not send messages to Jared.

**Total cron triggers per day: 2** (8am EST + 8pm EST)
**Total tasks that can run per day: 4** (2 per cycle x 2 cycles)

---

## QUESTIONS FOR JARED

1. **Are any of these 27 tasks unnecessary?** We can remove any you don't want.
2. **Should any tasks be MORE frequent?** (e.g., email check 3x/day?)
3. **Should any tasks be LESS frequent?** (e.g., move some twice-daily to daily?)
4. **Is the 8am + 8pm timing good?** Can shift to match your schedule better.
5. **Max 2 tasks per cycle — increase to 3?** Would clear the queue faster but takes longer per BOOP.
