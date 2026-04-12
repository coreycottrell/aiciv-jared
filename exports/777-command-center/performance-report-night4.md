# performance-optimizer: 777 Command Center - Night 4 Performance Audit

**Agent**: performance-optimizer
**Domain**: Frontend Performance Analysis
**Date**: 2026-03-24
**File audited**: `exports/777-command-center/index.html` (3,950 lines, 155KB)

---

## Baseline Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| HTML file size | 155KB (uncompressed) | Single monolithic file |
| data.json size | 21.5KB | 90 heatmap entries |
| Heatmap cells rendered | 98 (14 weeks x 7 days) | Each with 3 event listeners |
| Event listeners total | 17 addEventListener calls | Bounded and reasonable |
| Infinite CSS animations | 3 active | dotBlink, glowPulse, dotPulse |
| Chart instances | 3 | Radar, bar (proof), bar (money) |
| Auto-refresh interval | 60s | setInterval, never cleared |
| Chat history cap | 10 turns sent to API | Unbounded in-memory |

---

## Finding 1: Auto-Refresh Interval Never Cleared

**Impact: Medium**

`startAutoRefresh()` calls `setInterval` but the returned ID is discarded - it is never assigned to a variable or cleared. The interval runs forever with no cleanup path (no `clearInterval` anywhere in the codebase).

**Current code (line 2344-2371):**
```js
function startAutoRefresh() {
  setInterval(function() { ... }, 60000); // ID discarded
}
```

**Risk:** If the dashboard is embedded in a long-lived SPA or opened in multiple tabs, intervals stack. On a single-page load this is harmless - the tab's GC handles it on close - but it is sloppy and prevents future testability.

**Fix:**
```js
let _refreshTimer = null;
function startAutoRefresh() {
  if (_refreshTimer) clearInterval(_refreshTimer);
  _refreshTimer = setInterval(function() { ... }, 60000);
}
```

**Estimated effort:** 2 minutes.

---

## Finding 2: JSON.stringify for Change Detection (Expensive at Scale)

**Impact: Medium-Low (currently fine, degrades with data growth)**

Every 60-second refresh stringifies the full parsed data.json payload to compare against the previous value:

```js
const dataStr = JSON.stringify(data);
if (dataStr !== window.__lastDataStr) { ... }
```

At 21.5KB of JSON this costs roughly 0.1-0.2ms per call - negligible today. However, as `daily_pulse.heatmap` grows (currently 90 entries, unbounded), and if `proof_wall`, `gratitude`, or `achievements` arrays grow large, this comparison will become proportionally slower.

The heatmap consumer already caps at the last 91 entries (`dp.heatmap.slice(-91)`) which is correct, but the full JSON string comparison still processes the entire payload.

**Fix (minimal):** Compare only `last_updated` timestamp as a fast-path sentinel before doing the full stringify:
```js
if (data.last_updated !== window.__lastDataTimestamp) {
  // Only then do the full apply + stringify
  window.__lastDataStr = JSON.stringify(data);
  applyLiveData(data);
}
```

This turns the hot path (no change) from O(n) string comparison to O(1) string equality. The existing `window.__lastDataTimestamp` variable is already in scope (line 2340) but is not used for this purpose.

**Estimated effort:** 5 minutes.

---

## Finding 3: Heatmap Event Listeners - Three Listeners Per Cell

**Impact: Low (memory, not render speed)**

Each of the ~91 non-future heatmap cells registers 3 event listeners: `mouseenter`, `mouseleave`, `mousemove`. That is ~270 listener registrations on first render. This is fine in isolation.

The problem is there is no cleanup. If `buildHeatmap()` were ever called a second time (e.g., on a live data refresh that detects changed heatmap scores), all prior listeners would leak since the container's `innerHTML` is not cleared first. Currently `buildHeatmap()` is only called once in `initDashboard()`, so this is not an active leak - but it is one brittle step away from becoming one.

**Fix (defensive):** Use event delegation on the `#heatmap-weeks` container instead of per-cell listeners:
```js
document.getElementById('heatmap-weeks').addEventListener('mousemove', e => {
  const cell = e.target.closest('.heatmap-cell');
  if (!cell) { tooltip.style.display = 'none'; return; }
  // update tooltip from cell's data attributes
});
```

Store date/score on cells as `data-date` and `data-score` attributes during build. This replaces ~270 listeners with 1.

**Estimated effort:** 30 minutes.

---

## Finding 4: Three Perpetual CSS Animations Running at All Times

**Impact: Low (modern GPUs handle these trivially, but worth being aware of)**

Three `infinite` CSS animations run regardless of whether the relevant element is visible:

- `dotBlink` (2s) - on `.freshness-chip.fresh .freshness-dot` (green live indicator)
- `glowPulse` (2s) - on `.checklist-glow` (shown only when all checks complete)
- `dotPulse` (2s) - on `.mandala-sync-dot.live`

All three animate only `opacity` or `box-shadow`, which means they do not trigger layout (no `transform` or `width` changes). The browser compositor handles these off the main thread. They will not cause janky scrolling or frame drops.

The `loadingDots` animation (chat loading state) is also `infinite` but is only active during an active API call - acceptable.

`prefers-reduced-motion` support is already present in the CSS (line 1514) for the entrance animations - the perpetual indicator animations (`dotBlink`, `dotPulse`) are not included in that block, which is a minor accessibility gap.

**Fix (accessibility only):** Add to the `prefers-reduced-motion` block:
```css
@media (prefers-reduced-motion: reduce) {
  .freshness-chip.fresh .freshness-dot { animation: none; }
  .mandala-sync-dot.live { animation: none; }
}
```

**Estimated effort:** 3 minutes.

---

## Finding 5: Chat History Unbounded In-Memory Growth

**Impact: Low (bounded by session + UI cap prevents abuse)**

`chatHistory` array grows without a client-side cap:
```js
chatHistory.push({ role: 'user', content: text });
chatHistory.push({ role: 'assistant', content: reply });
```

The array is trimmed to 10 turns in the API payload (`chatHistory.slice(-10)`) before sending to the backend, so the server never receives more than 10 turns. But the in-memory array itself grows forever for the duration of the page session.

In practice, each entry is at most ~2000 chars (enforced by `maxlength="2000"` on the input), so 100 turns would be ~400KB of strings - negligible. The module change handler already calls `chatHistory = []` (line 3826) which resets it.

This is a theoretical rather than practical issue. The server-side limits (`MAX_MESSAGE_TURNS = 10`, `MAX_MESSAGE_CHARS = 2000`) are the real guards.

**Fix (optional, for hygiene):** Add a client-side trim after each push:
```js
chatHistory.push({ role: 'assistant', content: reply });
if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
```

**Estimated effort:** 2 minutes.

---

## Finding 6: Server-Side Rate Limit Map Never Pruned

**Impact: Low (serverless resets handle it, but a long-lived instance grows)**

In `api/chat.js` and `api/edit.js`, the `rateLimitStore` Map accumulates one entry per unique IP, with entries only replaced when the window expires and a new request arrives from that IP. There is no periodic cleanup. On serverless (Vercel), cold starts reset the Map so this is self-correcting. On a long-lived Node process it would be a gradual memory leak.

This was already flagged in `security-audit-sprint4.md` as a known trade-off. The comment in the code acknowledges it ("resets per cold start - sufficient for serverless"). No action needed for the current deployment target.

---

## Finding 7: Chart.js Loaded With `defer`, But Charts Are Initialized Inside `initDashboard()`

**Impact: Low (works correctly, but worth documenting why)**

`chart.js` is loaded with `defer` (line 10). `initDashboard()` calls `buildRadar()`, `buildProofBar()`, `buildMoneyChart()` which all instantiate `new Chart(...)`. This is safe because `initDashboard()` is only called from `loadDataAndInit()`, which is triggered either by `loadDataAndInit()` after password unlock (which happens on user interaction, well after DOM + deferred scripts are ready), or from the auto-unlock path on page load which uses a 50ms `setTimeout` that reliably fires after deferred scripts have parsed.

No bug here. However, if the auto-unlock path ever loses the setTimeout and calls `loadDataAndInit()` synchronously during DOMContentLoaded, Chart.js would not yet be available. Worth a comment in the code to prevent a future regression.

---

## Finding 8: `transition: all 0.2s` on Gate Button (Minor)

**Impact: Very Low**

`.gate-btn:hover` uses `transition: all 0.2s` (line 137). The `all` keyword forces the browser to monitor every animatable CSS property for changes, not just the ones that actually change. This is a micro-cost on hover. For a single button it is immeasurable in practice.

**Fix:** Scope the transition:
```css
.gate-btn { transition: background-color 0.2s, transform 0.2s; }
```

**Estimated effort:** 1 minute.

---

## Finding 9: `backdrop-filter: blur()` on Cards and Header

**Impact: Low (GPU-composited, but can degrade on low-end hardware)**

There are 3 instances of `backdrop-filter: blur(8px-10px)`:
- `.site-header` (sticky, always visible)
- `.card` (many instances)
- `.coach-panel` (fixed overlay)

On modern desktop/mobile GPU hardware these are composited and have no main-thread cost. On low-end Android devices or CPU-only rendering environments, each blurred layer is expensive. The sticky header is the most significant because it repaints on every scroll event.

**Fix (if mobile perf complaints arise):** Disable backdrop-filter on mobile:
```css
@media (max-width: 768px) {
  .card { backdrop-filter: none; }
  .site-header { backdrop-filter: none; background: rgba(8,10,18,0.98); }
}
```

**Estimated effort:** 5 minutes. Not recommended unless a real complaint arises.

---

## Finding 10: Google Fonts Blocks Render on First Load

**Impact: Medium (first contentful paint only)**

The Google Fonts CSS is a render-blocking request:
```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans..." rel="stylesheet">
```

Even with `preconnect` hints, the CSS request itself is synchronous and delays FCP. The password gate content will flash with system fonts for ~100-300ms on first load before fonts arrive.

This is only noticeable on the first load of the password gate. After the gate, the dashboard does not render until after user interaction (password entry), by which point fonts have long since loaded.

**Fix (optional, for polish):** Add `font-display: swap` via URL parameter - Google Fonts supports this:
```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Oswald:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

The `&display=swap` is already present in the URL. No change needed - this is already handled optimally.

---

## Summary: Priority Matrix

| # | Finding | Impact | Effort | Recommendation |
|---|---------|--------|--------|----------------|
| 1 | setInterval ID never stored/cleared | Medium | 2 min | Fix it - good hygiene |
| 2 | JSON.stringify for change detection | Medium-Low | 5 min | Fix it - future-proofs growth |
| 3 | 3 listeners per heatmap cell, no cleanup | Low | 30 min | Fix if heatmap rebuild is ever triggered more than once |
| 4 | Perpetual animations missing reduced-motion | Low | 3 min | Fix it - accessibility |
| 5 | chatHistory unbounded in memory | Low | 2 min | Optional cosmetic fix |
| 6 | Rate limit Map not pruned (serverless) | Low | N/A | Already known acceptable trade-off |
| 7 | Chart.js defer dependency on setTimeout | Very Low | N/A | Add a code comment, no code change |
| 8 | `transition: all` on gate button | Very Low | 1 min | Fix opportunistically |
| 9 | backdrop-filter on mobile | Low | 5 min | Only if mobile complaints arise |
| 10 | Google Fonts blocking | N/A | N/A | Already optimal (`display=swap`) |

---

## Quick Win Bundle (Under 15 Minutes Total)

These four changes have zero risk and collectively cover the most meaningful issues:

1. Store and clear the setInterval return value (Finding 1)
2. Use `data.last_updated` as fast-path change sentinel before JSON.stringify (Finding 2)
3. Add perpetual animations to `prefers-reduced-motion` block (Finding 4)
4. Replace `transition: all` with specific properties on gate button (Finding 8)

None of these require touching the dashboard layout, chart logic, or data pipeline.

---

## What Is Already Well-Implemented

- `defer` on Chart.js prevents parser-blocking script load
- `preconnect` hints for Google Fonts are in place
- `prefers-reduced-motion` block exists for entrance animations
- Chat API limits message history to 10 turns before sending to Anthropic
- Input `maxlength="2000"` prevents accidental huge payloads
- Data comparison before re-rendering (the JSON.stringify guard, even if improvable, is the right pattern)
- `heatmap.slice(-91)` caps the consumer even if the source array grows
- XSS protection via `escHtml()` applied consistently throughout DOM builds

---

*Audit performed: 2026-03-24 | Files: `index.html`, `api/chat.js`, `api/edit.js`, `data.json`*
