# Ask Aether Live Chat System — Investor Page

**Date**: 2026-03-16
**Type**: pattern
**Topic**: Client-side AI chat with two-tier response system on static CF Pages site

---

## What Was Built

Replaced a static investor inquiry form (Section 9) in `/exports/cf-pages-deploy/investors/index.html` with a live conversational AI chat window. The system is entirely client-side — no server rendering required, compatible with Cloudflare Pages static hosting.

## Architecture Decisions

### Two-Tier Response System
- **Tier 1**: Keyword-scored KB lookup, responds instantly with simulated typing animation
- **Tier 2**: Detected via keyword list (revenue, MRR, ARR, cap table, equity, shares, dilution, etc.), returns a "flagging to Jared" response + inline email capture + POSTs to `https://app.purebrain.ai/api/investor/question`

### KB Scoring (fuzzy matching)
Not exact match. For each KB entry, count how many `keys[]` strings appear as substrings of the query. Longer keys (>6 chars) score 3 points, shorter ones 2. Best score wins. This handles natural language variation without any NLP library.

### Typing Simulation
`typeText()` reveals characters one at a time at ~22ms + random 0-10ms jitter. Cursor blink indicator (unicode block char) during typing. On Tier 2, the email capture div appears after typing completes (not before — prevents layout jump during animation).

### Session Persistence
`sessionStorage.getItem/setItem('aetherChat')` stores `[{role, text}]` array. On page reload, history is replayed without animation. Suggestions panel auto-hides if >2 messages in history.

### Typing Indicator
3-dot bounce animation (separate CSS `@keyframes aetherTypeBounce`) shown for 900-1500ms random delay before Aether responds. Gives human feel.

## CSS Pattern Used
All glass-morphism cards use the same pattern as the rest of the page:
- `background: rgba(255,255,255,0.03-0.05)`
- `border: 1px solid rgba(255,255,255,0.08)`
- `backdrop-filter: blur(10px)`
- Aether messages: left blue border `3px solid rgba(42,147,193,0.5)`

## Key File
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors/index.html`
- Section 9 starts at line ~2057
- Chat styles at ~2168
- Chat engine JS (IIFE) at ~2390

## Gotchas
- `--text-dim` and `--teal` CSS variables were used in original but not defined in `:root`. Replaced with hardcoded `rgba(255,255,255,0.55)` and `var(--blue)` respectively to be safe.
- The `.contact-info` class has `align-items: center` globally — overrode to `flex-start` on the left column so text left-aligns.
- The IIFE pattern (`(function() { ... })()`) prevents any global variable pollution on a page that already has Three.js, Chart.js, and other scripts.
- Email capture only appears after Tier 2 *typing animation completes* (checked via `pendingTier2Question` state flag inside `typeText()` completion callback).

## KB Topics Covered (17 total)
PureBrain product, pricing (all 4 tiers), market opportunity, team, technology, competition, how-it-works, founding info, valuation, raise details, MAKR term sheet, revenue model, Year 1 projection, differentiators, minimum investment, ROI scenario, accredited investor eligibility.
