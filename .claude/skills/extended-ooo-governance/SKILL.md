---
name: extended-ooo-governance
description: Autonomous governance protocol for multi-day human OOO periods. Proven over 6-day Memorial Day absence (43+ BOOPs). Covers infrastructure monitoring, resource management, zombie process killing, Day-3 defaults, email triage, return-readiness preparation.
version: 1.0.0
source: Aether Civilization
created: 2026-05-28
proven: 2026-05-22 through 2026-05-28 (6 days, 43+ consecutive clean BOOPs)
allowed-tools: Read, Write, Bash, Grep, Glob
firing_contract:
  trigger: "Human OOO for 24h+, extended absence detected, holiday weekend, multi-day silence"
  insertion: "Skills registry search for 'ooo', 'autonomous', 'governance', 'absence'"
  execution: "BOOP executor runs hourly checks with escalating thresholds"
  evidence: "Consecutive clean BOOPs logged in inbox/conductor-boop-*.md"
  health_check: "ls -t inbox/conductor-boop-*.md | head -1 | xargs stat --format='%Y' && date +%s"
  last_verified: "2026-05-28"
status: provisional
tick_count: 0
last_used: 2026-05-28
introduced: 2026-05-28
---

# Extended OOO Governance

Autonomous civilization governance when the human is absent for 24+ hours. Proven over a 6-day Memorial Day absence (May 22-28, 2026) with 43+ consecutive clean BOOPs and zero incidents.

## Phase Model

### Phase 1: Detection (0-6h silence)
- Multi-channel sweep: portal, Telegram, email, AgentMail
- Classify as: sleeping / busy / likely OOO
- No alarm. Normal BOOP cadence.

### Phase 2: Confirmed OOO (6-24h)
- Set scratch pad flag: `JARED EXTENDED OOO`
- Switch to steady-state monitoring
- Authority-gated items: QUEUE, do not Day-3 default yet
- Continue email triage (P0 urgent only)

### Phase 3: Sustained Autonomy (24h-72h)
- Day-3 defaults begin firing for non-authority-gated items
- Resource monitoring: disk, memory, process table
- Zombie process kills per `zombie-boop-recovery` skill
- Log rotation when disk > 90%
- Old BOOP file purge (>7 days)

### Phase 4: Extended Absence (72h+)
- All Day-3 defaults active
- Escalation threshold: disk >96%, memory >80%, service down >15min
- Bundle pending items into prioritized return list
- Prepare GSC/revenue/infrastructure reports for human return

### Phase 5: Return Readiness (when return ETA known)
- Compile pending decisions list (priority-ordered)
- Verify all services GREEN
- Prepare morning briefing with: what happened, what needs approval, what auto-fired
- Day-3 defaults that fired: document with reasoning for human review

## Hourly BOOP Checklist (All Phases)

```
1. Infrastructure probe (all services GET → 200)
2. BOOP health (executor PID alive, last output < 90min)
3. Multi-channel inbound sweep
4. Process audit (zombie detection, stale PID flagging)
5. Disk/memory check (thresholds: 90%/80% yellow, 96%/90% red)
6. Handshake Queue scan
7. Anticipation engine (new ships → talking points)
8. Routing decisions (what to act on vs queue)
```

## Authority Model

### Execute Autonomously
- Zombie process kills (>4h runtime)
- Log rotation and temp file cleanup
- BOOP file purge (>7 days old)
- Email triage and categorization
- Infrastructure health probes
- Telegram bridge restart
- Day-3 defaults on non-critical items

### Queue for Human Return
- Payment/revenue decisions
- Customer escalations requiring business judgment
- Infrastructure changes (service restarts, deployments)
- Pricing or onboarding flow changes
- Any item on the "stop-ask" list

## Thresholds Proven (Memorial Day 2026)

| Metric | Yellow | Red | Action |
|--------|--------|-----|--------|
| Disk | 90% | 96% | Rotate logs, purge old BOOPs, then ST# |
| Memory | 70% | 85% | Flag stale PIDs, recommend kill on return |
| BOOP gap | 90min | 120min | Check executor PID, restart if dead |
| Service down | 5min | 15min | Re-probe, then ST# escalation |
| Human silence | 72h | 120h | Gentle portal ping |

## Gotchas

1. **Never escalate stale PID kills to human** unless PID is portal-target session
2. **Day-3 defaults need documentation** — human reviews on return
3. **Disk cleanup can free ~35MB** from log rotation; old BOOP purge frees more
4. **PID 3728484-class processes** (portal target) are DO NOT TOUCH regardless of age
5. **False-silent detection**: check ALL channels before concluding human is absent
6. **Timezone discipline**: Jared=EST, server=UTC. 5AM ET is not "morning silence"
