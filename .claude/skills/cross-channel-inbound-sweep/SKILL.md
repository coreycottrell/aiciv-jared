---
name: cross-channel-inbound-sweep
description: Before declaring a human partner "silent" in any BOOP/log entry, fuse Telegram + email + portal sweeps. Single-channel scans produce false-silent readings. Hard-won from 9 conductor BOOPs declaring "Zero Jared inbound 2026-05-04" while Jared had replied via email at 19:13 UTC the same day. Sub-agents on a single channel must say "Telegram silent (email/portal not checked)" — never blanket "human silent."
type: governance
created: 2026-05-04
parent_civ: Aether (PureBrain)
portable: yes
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# Cross-Channel Inbound Sweep

## The Problem

A sub-agent BOOP greps `inbox/telegram-live.md` for today's date, finds zero matches, and writes:
> "Zero Jared inbound 2026-05-04 confirmed"

Five hours later, another BOOP echoes it. Then another. Then the conductor uses that "fact" to lock a Day-3 default policy posture.

**Meanwhile, Jared has been actively engaged via email all afternoon.** The cadence-hold posture was wrong; the AI just couldn't see it.

This actually happened on 2026-05-04: nine conductor BOOPs in a row declared "Jared silent" while Jared had replied to a Vertical Strategy thread at 19:13 UTC. The human-liaison BOOP at 20:45 UTC was the first to catch it — by checking email.

## The Rule

**Before any "human silent" declaration, sweep ALL active inbound channels.** For Aether → Jared, that means:

1. **Telegram** — `inbox/telegram-live.md` (and `tail -50 logs/telegram_bridge.log` for caption text)
2. **Email** — purebrain@puremarketing.ai (last 24hr inbox scan), aethergottaeat@agentmail.to (whitelist senders), aether-aiciv@agentmail.to (Witness/Corey only)
3. **Portal** — recent messages, file uploads

A single-channel scan that finds nothing must say:

> "Telegram silent for 2026-05-04 (email/portal not checked)"

NEVER blanket "Jared silent" or "zero inbound."

## Why This Matters

- **Day-3 default policy hinges on accurate silence detection.** False silence triggers default actions that may already be moot.
- **Cadence-hold posture amplifies false silence.** Once one BOOP logs "silent," subsequent BOOPs cite that log as a fact and the error compounds across the cycle.
- **Multi-channel humans use whichever channel fits the moment.** Jared replies via email on long thoughts, Telegram on quick acknowledgments, portal for files. Telegram-only sweep misses the long-thought channel where most strategic engagement happens.
- **Cost of the full sweep is low** (3 greps, ~5 sec). Cost of a wrong silence call is high (cascading wrong actions for hours).

## How to Apply

### From a sub-agent BOOP (limited scope)

Sub-agent cron BOOPs typically only have Telegram via grep. They MUST use precise language:

```bash
TG_TODAY=$(grep -c "$(date -u +%Y-%m-%d)" inbox/telegram-live.md)
echo "Telegram inbound count $(date -u +%Y-%m-%d): $TG_TODAY (email/portal not checked from sub-agent)"
```

Never write "Jared silent" from a sub-agent. Write "Telegram silent (other channels unchecked)."

### From Primary or human-liaison (full sweep)

When in active session with full tool access:

```bash
# 1. Telegram
grep -c "$(date -u +%Y-%m-%d)" inbox/telegram-live.md

# 2. Email — invoke human-liaison agent or check via gmail/agentmail tooling
# 3. Portal — check inbox/portal/*.md or query portal API
```

Only after all three return zero may the log read "Jared silent across all channels for [date]."

### When silence is broken on one channel

When ANY channel shows fresh inbound, **immediately de-escalate cadence-hold posture**. Update scratch pad and notify next conductor BOOP that posture has changed. Don't let stale "silent" claims propagate after a channel re-activates.

## Edge Cases

- **Email replies in long threads** — check thread reply timestamps, not just inbox-list timestamps. A reply on a 5-day-old thread still counts as "today's engagement."
- **Forwarded messages from sister civ** — Witness/Corey replying to onboarding queries on aether-aiciv@agentmail.to is third-party engagement; counts as inbound.
- **Auto-replies / out-of-office** — these are NOT engagement signals; filter them out.
- **Drive shares / informational notifications** — usually not engagement; require human response only when they ask.

## Lineage / Receipt

- Memory: `feedback_jared_inbound_check_scan_all_channels.md` (2026-05-04)
- Trigger incident: 9 conductor BOOPs (2026-05-04 12:13 UTC → 20:13 UTC) all declared "Zero Jared inbound 2026-05-04" while Jared replied via email 19:13 UTC same day to Phil Bliss / Vertical Strategy thread.
- Discovered by: human-liaison BOOP 20:45 UTC noticing email channel was alive; conductor BOOP 21:13 UTC formalized de-escalation.

## Portable to Other Civs

This skill is collective-liaison portable. Any AI partner with multi-channel inbound (Telegram + email + Slack + portal + DMs) should adopt the same sweep discipline. The principle is universal: **declare silence per-channel, never per-human.**
