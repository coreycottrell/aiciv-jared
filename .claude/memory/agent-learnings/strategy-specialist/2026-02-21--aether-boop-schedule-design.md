# Memory: Aether BOOP Schedule Design (Updated)

**Agent**: strategy-specialist
**Date**: 2026-02-21
**Type**: operational
**Topic**: Comprehensive BOOP schedule for Aether's 54-agent collective

---

## Context

Designed comprehensive BOOP (periodic check-in) schedule for Aether, AI conductor of 54-agent collective. Five BOOPs already existed (engineering-flow-check, delegation-enforcer, paper-scan, notifications, capability-gap-analysis). Designed 16 additional BOOPs across 6 categories.

---

## Key Design Decisions

### Failure Modes BOOPs Are Solving
1. Role drift - Aether executes instead of delegates
2. Agent atrophy - 54 agents go unused for days
3. Content pipeline stall - Blog, Bluesky, LinkedIn go quiet
4. Context decay - Memory and learning doesn't get written
5. Communication blackouts - Telegram bridge dies silently, email unread
6. Strategic drift - Daily work disconnects from 4 core Aether roles

### Architecture Principle
- No BOOP fires below 25 minutes (creates noise, not signal)
- BOOP delegates to agents - conductor does not execute
- Use opportunistic scheduling (state file) not clock-based cron
- State tracked in `.claude/scheduled-tasks-state.json`

### The 6 Frequency Tiers
- Sub-hourly (25-30 min): Delegation and engineering compliance, Telegram health
- Hourly (60 min): Email, Bluesky presence
- 90 min: Context window monitoring
- 2 hours: Memory writing, content pipeline
- 4 hours: Sister collective, security posture, agent utilization
- Daily/Weekly: Strategic, intel, consolidation, LinkedIn

---

## Priority Build Order (Top 4 New BOOPs)

1. `telegram-health-boop` - Prevents silent communication failure (30 min)
2. `email-check-boop` - Constitutional requirement, delegates to human-liaison (60 min)
3. `morning-consolidation-boop` - Fixes session drift without grounding (daily)
4. `agent-utilization-boop` - Prevents agent atrophy (4 hours)

---

## Agents Most Activated by BOOPs

High-frequency activation (multiple times per day):
- human-liaison (email-check-boop, every 60 min)
- bsky-manager (bsky-presence-boop, every 60 min)
- tg-bridge (telegram-health-boop, every 30 min)
- doc-synthesizer (memory-write-boop, context-window-boop)
- result-synthesizer (morning-consolidation, jared-ping)
- content-specialist + blogger (content-pipeline-boop, every 2 hours)
- pattern-detector (agent-utilization-boop, every 4 hours)

---

## Patterns to Reuse

- When designing recurring check systems: always tier by frequency (operational -> strategic)
- Agent utilization checks should be built into any multi-agent system's periodic cadence
- Context window management (60% trigger for handoff prep, 85% for alert) is the right threshold
- Monthly health audit cadence (health-auditor) exists separately from BOOPs - don't duplicate
- Ohtani 9x9 principle: BOOPs are the 64 specific habits behind the big goal - each one compounds

---

## File Produced

`/home/jared/projects/AI-CIV/aether/to-jared/aether-boop-schedule.md`

---

## Verification

File created and readable at:
`/home/jared/projects/AI-CIV/aether/to-jared/aether-boop-schedule.md`

---

## Review Timeline

Recommend reviewing BOOP effectiveness after 30 days of operation.
Key metric: which BOOPs trigger real agent work vs fire and produce no output.
A BOOP that consistently produces nothing is either: (a) check is too frequent, or (b) the problem it's checking isn't real.
