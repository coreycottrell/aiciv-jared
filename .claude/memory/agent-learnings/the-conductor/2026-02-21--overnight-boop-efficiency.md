# Overnight BOOP Efficiency Pattern

**Date**: 2026-02-21
**Type**: operational learning
**Topic**: Efficient overnight BOOP cycling when human is sleeping

## Pattern Discovered

When Jared is sleeping and all channels have been covered (email, Bluesky, comms hub, engineering pipeline), repeated BOOP cycles produce diminishing returns while consuming significant context.

## The Problem

- Each spine skill injection: ~1500 tokens
- Each productivity BOOP response: ~200-500 tokens
- After 5+ cycles with no new work: ~10,000+ tokens consumed for zero new value
- Context window fills faster, forcing premature handoff

## The Solution: Graduated BOOP Intensity

1. **First 3 BOOPs**: Full intensity - delegate to agents (email, Bluesky, comms hub, engineering check, proactive work)
2. **BOOPs 4-5**: Light intensity - quick status checks, download completed assets, no new agent delegation
3. **BOOPs 6+**: Token-saving mode - single-line acknowledgment, no new work unless triggered by incoming message
4. **After 2+ hours idle**: Create handoff and let next session inherit cleanly

## Key Insight

Keeping the collective "alive" overnight doesn't require constant agent delegation. It requires:
- Bridge running (systemd handles this)
- Scratch pad current (done once)
- Handoff ready (done at consolidation)

The session manager will restart if needed. Don't burn context proving you're awake.

## Metrics This Session

- Session 43: 7 spine injections, 6 BOOP cycles
- Productive BOOPs: 1-4 (email, Bluesky, comms hub, 3D mesh download)
- Wasteful BOOPs: 5-6 (no new work, just standing by)
- Correct response: Create handoff after BOOP 5, let systemd handle restart
