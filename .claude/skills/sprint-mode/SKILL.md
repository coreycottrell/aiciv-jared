---
name: sprint-mode
description: Use on intensive build days as a lean BOOP variant that skips fleet health, registry, and scheduled-task checks, loading grounding docs only to save time.
status: provisional
tick_count: 0
last_used: 2026-05-22
introduced: 2026-05-22
---
# Sprint Mode

**Purpose**: Lean BOOP variant for intensive build days. Skip fleet health, registry, scheduled tasks. Grounding docs only — every minute counts.

**Origin**: Imported from Tether CIV (2026-05-21). Adapted for Aether's BOOP cadence.

**Version**: 1.0.0
**Tags**: operations, efficiency, build-day
**Triggers**: "sprint mode", "build day", "lean boop"

## When to Use

- Jared explicitly says "build day" or "sprint"
- Shipping deadline within 24h
- Single large feature needs uninterrupted focus
- After morning relay is done and no P0 blockers remain

## Sprint BOOP (replaces standard BOOP)

1. **Read ONLY**: CLAUDE.md + scratch-pad (2 min max)
2. **Check ONLY**: Telegram inbound + portal messages (30 sec)
3. **Skip**: Fleet health, Hetzner monitor, registry checks, scheduled tasks, hub scan, email sweep
4. **Execute**: The build task at hand
5. **Log**: One-line scratch-pad update when done

## Exit Sprint Mode

- Any P0 inbound from Jared
- Build task complete
- 4+ hours elapsed (return to standard BOOP)
- Any production alert (site down)

## Integration

- Announce sprint mode in portal: "Entering sprint mode — [task]. Standard monitoring paused."
- Set `sprint_mode: true` in scratch-pad header
- Clear sprint mode at end: remove from scratch-pad, run one full standard BOOP

## Gotchas

- NEVER sprint through a Jared message — always respond
- Sprint mode does NOT mean ignoring security alerts
- Maximum 4 hours — after that, situational awareness decays
