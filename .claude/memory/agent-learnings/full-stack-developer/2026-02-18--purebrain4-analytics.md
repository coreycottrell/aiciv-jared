# PureBrain 4 Analytics JS

**Date**: 2026-02-18
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Built

Complete analytics and tracking JS file for the PureBrain.ai landing page.

**Output**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-4/analytics.js`

## Property IDs

- GA4 Measurement ID: `G-86325WBT3P`
- Microsoft Clarity Project ID: `viy9bnc56x`

## Architecture

Self-contained IIFE (immediately invoked function expression) — no dependencies, ES5-compatible.

The file has 8 sections:
1. AUTO-INIT — injects GA4 and Clarity snippets if not already loaded by GTM
2. FUNNEL EVENTS — 5 public functions exposed on `window.*`
3. SCROLL DEPTH — IntersectionObserver (with fallback) for 6 key sections
4. CTA CLICK TRACKING — event delegation via document.addEventListener('click')
5. DEMO VIDEO — play / unmute / 25% / 50% / complete via timeupdate + ended events
6. EXIT INTENT — mouseleave (desktop) + visibilitychange (mobile) + pagehide
7. SESSION DURATION — setInterval heartbeat every 30s up to 5min; beforeunload total
8. DATA LAYER — every fireEvent() also pushes to window.dataLayer for GTM

## Key Patterns

**Queue flush**: If this script loads before gtag, events go into `window.__pbAnalyticsQueue`
and are flushed on `script.onload`. Prevents lost events.

**Dedup via once()**: Scroll sections and video milestones use `window.__pbFired[key]`
to prevent duplicate events. Safe across reloads.

**Exit intent gate**: Single-fire per page load (`exitIntentFired` boolean). Desktop
triggers on mouseleave with `clientY <= 15`, mobile via visibilitychange/pagehide.

**Modal wiring**: Exit intent auto-wires `[data-pb-exit="stay"]` and `[data-pb-exit="leave"]`
buttons inside `#pb-exit-modal`. No separate JS needed.

## How to Wire the Funnel Events

The 5 funnel functions are public on `window.*`:

```javascript
window.trackAwakeningStart();             // user starts chat
window.trackAINamed('Aria');              // AI declares its name
window.trackPricingRevealed('Aria');      // pricing section shown
window.trackTierSelected('Awakened', 79); // user clicks a tier
window.trackConversion('Awakened', 79);   // payment submitted
```

Call these from the PureBrain chat/UI code at the appropriate moments.

## DOM Requirements for Auto-Tracking

- Demo video: `<video id="pb-demo-video">` (or class `.pb-demo`)
- Exit modal: `<div id="pb-exit-modal">` with `[data-pb-exit="stay"]` / `[data-pb-exit="leave"]` buttons
- CTA buttons: class `.pb-cta`, `.pricing-card__cta`, `.hero__cta`, or `[data-pb-cta]` attribute
- Scroll sections: id `#hero`, `#trust`, `#how`, `#difference`, `#pricing`, or class equivalents

## What NOT To Do

- Do NOT load this file before the page DOM — use defer or place at bottom of body
- Do NOT set `DEBUG: true` in production — it writes to console on every event
- Do NOT duplicate the gtag snippet if GTM already loads it — the auto-init checks first
