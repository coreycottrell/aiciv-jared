# Plugin v4.7.2.1 Reactivation Plan — ST# Task

**Date**: 2026-02-28
**Type**: planning + gotcha documentation
**Agent**: dept-systems-technology

## Summary

Researched plugin version history and created a safe reactivation plan for PureBrain Security v4.7.2.1.

## What v4.7.2.1 Is

v4.7.2 with exactly one change: the entire **n2 SESSION TIMER FIX block** removed.

That block contained:
- CSS: `.session-timer.active { display: none !important; }` — the rule that broke bypass flow
- CSS: `.session-timer.active.pb-timer-ready { display: flex !important; }`
- CSS: `#sessionNote { display: none !important; }`
- JS: click listener on `#seeWhatBtn` adding `.pb-timer-ready` and `.pb-note-ready`

Line count: v4.7.2 = 5086 lines, v4.7.2.1 = 5027 lines (59 lines removed, exactly the n2 block).

## Plugin Version Chain

v4.7.0 (PayPal CSP fix) -> v4.7.1 (PayPal routing fix) -> v4.7.2 (sandbox override) -> v4.7.3 (discover button UX + extended timer fix) — v4.7.3 BROKE bypass

v4.7.2.1 = v4.7.2 minus the timer CSS block only

## Verification Commands

Pre-activation checks:
```bash
# Confirm problematic CSS absent
grep -c "session-timer.active" exports/purebrain-security-plugin-v4721.php
# Expected: 0

# Confirm critical sections present
grep -c "pb-paypal-routing-fix\|pb-sandbox-override\|pb-bypass-override" exports/purebrain-security-plugin-v4721.php
# Expected: 3
```

## Risk Level

LOW. This is a subtraction, not an addition. Everything in v4.7.2 that was working is preserved.

Only UX side effect: session timer may appear earlier in conversation (before Discover button click), since the hide-until-clicked mechanism was removed.

## Plan Location

`/home/jared/projects/AI-CIV/aether/to-jared/plugin-reactivation-plan.md`

## Key Lesson

The `display: none !important` approach for hiding elements is permanently dangerous — it breaks any bypass flow that touches those same elements. Future timer/visibility UX should use opacity, visibility, or JS-only toggles. NEVER CSS `display: none !important` on elements that might be in the bypass critical path.
