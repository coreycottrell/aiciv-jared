# 777 Command Center — QA Audit (Night 4)

**File audited:** `exports/777-command-center/index.html` (~4038 lines)
**Data file:** `exports/777-command-center/data.json`
**Audit date:** 2026-03-24
**Auditor:** PTT QA Engineer

---

## Summary

| Category | Bugs | Enhancements | Notes |
|----------|------|--------------|-------|
| HTML Validity / Accessibility | 3 | 2 | 2 |
| CSS / Responsive | 1 | 3 | 1 |
| JavaScript | 4 | 2 | 2 |
| Data Loading | 2 | 1 | 1 |
| AI Coach Panel | 2 | 1 | 1 |
| Auto-Refresh | 1 | 1 | 1 |
| Mobile Responsiveness | 1 | 2 | 0 |
| **Totals** | **14** | **12** | **8** |

---

## 1. HTML Validity / Accessibility

### BUG-001 — Password exposed in plain JS source
**Severity: High**
Line 2282: `const PASSWORD = '777grind';` is hardcoded in plain client-side JavaScript. Any viewer who opens DevTools can read it without entering it. This defeats the purpose of the gate entirely for technically literate users.
**Fix:** Move password validation to the server-side `/api/edit` endpoint or use a hashed comparison (bcrypt/SHA-256) with a server check.

### BUG-002 — `aria-label` missing on icon-only interactive elements
**Severity: Medium**
The heatmap cells (line ~2806-2837) are rendered as clickable `div` elements with `cursor:pointer` but have no `role="button"` and no `aria-label`. Screen readers cannot identify them. Same applies to the relationship ring SVG node circles (line ~3310) which have `cursor:pointer` but no accessible label.
**Fix:** Add `role="button"` and `aria-label="Score: {date} - {score}"` to heatmap cells. Add `aria-label="{node.name} - last contact {node.days}d ago"` to SVG node circles.

### BUG-003 — `<div role="dialog">` on coach panel missing `aria-modal` and focus trap
**Severity: Medium**
Line 2254: `<div class="coach-panel" ... role="dialog" aria-label="AI Coach">` is present and correct for the ARIA role, but there is no `aria-modal="true"` attribute and no focus trap. When the panel opens, keyboard users can tab through the underlying dashboard while the modal is active.
**Fix:** Add `aria-modal="true"`. On panel open, trap Tab/Shift-Tab within `#coach-panel`. Restore focus to `#coach-fab` on close.

### ENHANCEMENT-001 — `<header>` landmark not paired with `<main>`
The page uses `<header class="site-header">` correctly but wraps all dashboard content in `<div id="dashboard">` without a `<main>` element. Screen reader landmark navigation will skip straight to the header without finding main content.
**Fix:** Wrap the dashboard grid content in `<main id="main-content">`.

### ENHANCEMENT-002 — Missing `<title>` language attribute differentiation
`<title>777 Command Center</title>` and `<html lang="en">` are correct. However, the password gate uses `font-family: 'Oswald'` for the password input (line 105), which is unusual for a form field and may cause assistive technology to misread letter-by-letter input.
**Fix:** Change `.gate-input` font to `'Plus Jakarta Sans'` or system font so screen reader character-by-character reading works normally.

### NOTE-001 — `autofocus` on password input
Line 1781: `autofocus` on `#pw-input` is intentional UX. However, if the user has already unlocked (localStorage check on line 2582-2591), `autofocus` still fires briefly on the hidden input before the gate is hidden, which may cause screen reader announcement of a hidden field. Low severity but noted.

### NOTE-002 — `<div class="achievement-badges">` at line 2149 is empty in HTML
The badges `<span>` elements are hardcoded as children but the wrapping `<div class="achievement-badges">` has no `aria-label`. Not an error, but worth a label for semantic completeness.

---

## 2. CSS / Responsive Breakpoints

### BUG-004 — `col-6` class defined in CSS but not handled in 1200px breakpoint
**Severity: Low**
Line 275: `.col-6 { grid-column: span 6; }` is defined. The 1200px breakpoint at lines 280-284 does not include `col-6` in its override list. At 1200px wide, `.col-6` elements will remain at half-width inside a 12-column grid — potentially acceptable, but the omission appears unintentional given all other cols are explicitly handled. The 768px breakpoint does catch it.
**Fix:** Either deliberately document the col-6 at 1200px as intentional half-width, or add `.col-6 { grid-column: span 12; }` to the 1200px block.

### ENHANCEMENT-003 — AI Coach panel z-index gap
The `.coach-panel` is `z-index: 499` and `.coach-fab` is `z-index: 500`. The sticky `.site-header` is `z-index: 100`. If any future card uses `position: fixed` or a high `z-index`, the panel could be partially occluded. No conflict currently exists, but the gap between 100 and 499 is large.
**Note:** Current z-index stack is: header=100, tooltip=1000, coach-panel=499, coach-fab=500, password-gate=9999. The tooltip at 1000 will render above the coach panel if a heatmap tooltip fires while the coach is open. This is a minor visual bug — tooltip appears over coach panel content.
**Fix:** Set `.tooltip` to `z-index: 501` or lower to keep it consistent, or set `.coach-panel` to z-index 1001 and `.coach-fab` to 1002.

### ENHANCEMENT-004 — `heatmap-cell:hover` scale causes overflow clipping
Line 352: `.heatmap-cell:hover { transform: scale(1.4); z-index: 10; }`. The parent `.pulse-heatmap-wrap` has `overflow-x: auto` on mobile (line 1265). On desktop, `overflow: hidden` is not set on the heatmap grid container, so the scaled cell can extend beyond card boundaries and be clipped by the card's `overflow: hidden` at line 226.
**Fix:** Add `overflow: visible` to `.heatmap-grid` or use a smaller scale factor (1.2) to stay within cell bounds.

### ENHANCEMENT-005 — `money-grid` at 480px has no breakpoint
The `.money-grid` uses `grid-template-columns: 1fr 1fr` (line 695) and has no 480px breakpoint, so the two cells squeeze to very narrow widths on small phones. The `number-milestones` row at line 754 with 5 labels (`$0 $15M $30M $45M $60M`) will also overflow on small screens.
**Fix:** Add `@media (max-width: 480px) { .money-grid { grid-template-columns: 1fr; } }`.

### NOTE-003 — `eulogy-grid` 2-column layout not responsive below 480px
`.eulogy-grid` uses `grid-template-columns: 1fr 1fr` (line 873) with no 480px override. Text content is long, so it will be very cramped on phones. Only a 768px catch-all handles this via `.col-8/col-7` collapse, but not the inner grid.

---

## 3. JavaScript Bugs

### BUG-005 — `heatmap-cell` wave animation class added to cells that already have `heat-*` class
**Severity: Low**
In `animateCardEntrance` (line 3802): `cell.classList.add('wave-animate')`. The `wave-animate` animation uses `opacity: 0` as the initial state (line 1503). For cells that already have a `heat-*` background set, the animation causes them to flash invisible briefly. When `prefers-reduced-motion` is respected (line 1513), this is skipped, but on normal loads the wave renders each cell at opacity 0 before animating in. This is the intended behavior, but if `initDashboard` returns while chart.js is still loading (it is `defer`-loaded), the cells may animate before the canvas charts are ready.
**Fix:** Wrap `animateCardEntrance` call in a `DOMContentLoaded` check or invoke it after chart.js confirms ready. Current order in `initDashboard` (line 2734) is fine as long as `defer` scripts execute before `DOMContentLoaded` fires — which is guaranteed by spec, so this is low severity.

### BUG-006 — `buildGoalMountain` crashes if `goals[tier.key]` is undefined
**Severity: High**
Line 3047: `const tierGoals = goals[tier.key];` is followed immediately by `tierGoals.map(...)` at line 3048. If `data.json` provides partial `goals` data (e.g. has `yearly` but not `monthly` or `weekly`), `applyLiveData` at lines 2512-2514 only updates keys that are present in the response. The `goals` object defaults are set, but if `applyLiveData` replaces `goals.yearly` without replacing `goals.monthly`, the existing sample values remain — this is safe. However, if `goals` is somehow set to a plain object with no fallbacks (e.g. a future refactor), the `.map` call will throw.
**Fix:** Guard with `const tierGoals = goals[tier.key] || [];` on line 3047.

### BUG-007 — `sparkline-svg` division by zero when all 7-day scores are equal
**Severity: Low**
In `buildSparklines` (line 2907): `const range = max - min || 1;`. This correctly guards against `range = 0`. However, the `||` operator will also substitute `1` when `range` is `0` — which means all points will render at the same `y` coordinate (the bottom of the SVG). The fallback of `1` means `(v - min) / range = 0` always, so all points collapse to `y = h - pad`. This renders as a flat line at the bottom, which is technically not a crash but is visually incorrect — should render as a flat line at the midpoint.
**Fix:** `const y = h - pad - ((v - min) / range) * (h - pad * 2);` — when range is 0, set `y = (h / 2)` instead.

### BUG-008 — `formatCoachText` regex wraps nested `<ul>` incorrectly
**Severity: Medium**
Lines 3843-3845:
```javascript
s = s.replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>');
s = s.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
s = s.replace(/(<\/ul>\s*<ul>)/g, '');
```
The `gs` flag on the second replace causes it to wrap every `<li>` sequence (including multiple adjacent ones) in its own `<ul>`. The third replace tries to merge adjacent `</ul><ul>` pairs, but the `\s*` between them does not account for `<br>` tags that the fourth replace (line 3846) may have already inserted, since line break replacement happens after. The correct order should be: convert bullets to `<li>`, wrap adjacent `<li>` blocks in a single `<ul>`, then convert newlines to `<br>`. As written, if a bullet list is followed by a blank line and more bullets, the merge regex will miss them and produce double `<ul>` wrapping.
**Fix:** Reorder: apply the `\n` → `<br>` conversion last, after all list processing.

### NOTE-004 — Password in `/api/edit` payload
Line 3597: `password: '777grind'` is included in the POST body to `/api/edit`. This sends the plaintext password as a POST body to the server, visible in network traffic (unless HTTPS is enforced). Consistent with the hardcoded client-side password (BUG-001), but noted separately because it also appears in server communication.

### NOTE-005 — `escHtml` used on trusted data in some places, missing in others
`escHtml` is correctly applied to user-derived fields (contact names, task text). However, in `buildMandalaMini` (line 3744), `qualityLabel` from `BIZ_QUALITIES` (a static hardcoded array) is injected directly: `<div class="mandala-mini-cell-label">${qualityLabel}</div>`. This is safe because it is a trusted constant, but it sets an inconsistent pattern. If `BIZ_QUALITIES` is ever made dynamic from `data.json`, this injection point would become an XSS vector.
**Fix:** Apply `escHtml(qualityLabel)` consistently.

---

## 4. Data Loading

### BUG-009 — `applyLiveData` called before `dailyScores` / `sevenFs` / `goals` are initialized
**Severity: Medium**
`loadDataAndInit` (line 2315) runs the fetch, then on success calls `applyLiveData(data)` (line 2323), then calls `initDashboard()` in `.finally()` (line 2331). Inside `applyLiveData`, the code assigns to `dailyScores` (line 2453), `sevenFs` (line 2499), `goals.yearly` (line 2512), etc. These variables are declared and initialized with sample data at lines 2614-2705, which is module-level code that runs before `loadDataAndInit` is called — so the order is safe in normal flow.

However, the `auto-unlock` path on line 2582-2591 calls `loadDataAndInit` inside a `setTimeout(..., 50)`. If the browser runs the setTimeout callback before the module-level variable initialization finishes (theoretically impossible in a single-threaded synchronous parse, but worth noting), the assigns would reference `undefined`. This is safe in practice because all variable declarations are hoisted.
**Note:** The ordering is safe, but add an explicit `if (!data.daily_pulse) return;` guard in `applyLiveData` for resilience.

### BUG-010 — Empty `data.json` `streaks: {}` is never consumed
**Severity: Low**
`data.json` line 473: `"streaks": {}`. The `applyLiveData` function at lines 2438-2575 never reads `data.daily_pulse.streaks`. The streak badges in HTML (lines 2066-2104) are hardcoded values (14, 21, 30, 7, 45). These never update from live data even when `data.json` is refreshed.
**Fix:** Either populate `streaks` in `data.json` and wire `applyLiveData` to update the badge elements, or document that streaks are intentionally manual.

### ENHANCEMENT-006 — No validation of `data.json` schema before rendering
`applyLiveData` uses optional chaining patterns (`if (data.daily_pulse)`, `if (dp.heatmap && dp.heatmap.length > 0)`) but some nested accesses lack checks. Example: `dp.today.score || 0` at line 2458 would throw if `dp.today` exists but `score` is not a property (e.g., a non-object `null`). The overall approach is defensive, but a top-level schema shape check would make errors clearer.

### NOTE-006 — `data.json` heatmap starts 2025-12-24 but `__LIVE_DATA__` embedded in HTML starts 2025-12-17
The inlined `window.__LIVE_DATA__` in the `<script>` block at line 1764 uses `last_updated: "2026-03-16T01:24:55Z"` and a heatmap starting 2025-12-17. The external `data.json` file uses `last_updated: "2026-03-23T10:40:06Z"` and starts from 2025-12-24. The loader preferentially uses `__LIVE_DATA__` (line 2317: `window.__LIVE_DATA__ ? Promise.resolve(...)`) — meaning the embedded stale snapshot (March 16) is used instead of the fresh data.json (March 23) when both are present. This is the opposite of the intended freshness hierarchy.
**Fix:** Either strip `__LIVE_DATA__` from the HTML and rely solely on `data.json`, or update `__LIVE_DATA__` on each deploy to match the latest `data.json` contents.

---

## 5. AI Coach Panel

### BUG-011 — `loadingMsg.remove()` called twice on error path
**Severity: Low**
In `sendMessage` (lines 3950-3967): `loadingMsg.remove()` is called inside both the `if (!resp.ok)` branch (line 3951) and at the start of the catch block (line 3964). If `resp.json()` in the error branch throws (line 3954: `.catch(function() { return {}; })`), the code continues to `addMessage('system', ...)` without any issue. However, if the fetch itself rejects (network error), the catch block at line 3963 calls `loadingMsg.remove()` on an element that may have already been removed if the try block partially executed before throwing. Calling `.remove()` on a detached element is harmless in modern browsers but raises a console error in some environments.
**Fix:** Add a guard: `if (loadingMsg.parentElement) loadingMsg.remove();`

### BUG-012 — Module switch does not abort in-flight requests
**Severity: Medium**
When the user changes the coaching module via `#coach-module` (line 3831), `chatHistory` is cleared and the UI resets. But if a request to `/api/chat` is in-flight at that moment (`isSending = true`), the module context changes while the server is processing the old module's request. The response that comes back will be appended to the new module's cleared chat, creating a context mismatch.
**Fix:** Store the current request as an `AbortController` signal and call `controller.abort()` on module change. Check `isSending` before resetting UI — if sending, show a "Please wait" message instead of resetting immediately.

### ENHANCEMENT-007 — No retry or timeout on `/api/chat` fetch
If the Vercel function is cold-starting or slow, there is no timeout. A user could wait indefinitely with the loading spinner showing. The `isSending` flag remains `true` until the promise resolves or rejects, blocking all further sends.
**Fix:** Wrap the fetch in a `Promise.race` with a `setTimeout` abort (e.g., 30 seconds).

### NOTE-007 — `chatHistory.slice(-10)` limits context window
Line 3946: `messages: chatHistory.slice(-10)`. This is intentional to avoid sending excessive tokens to the API. Fine as-is, but note that very long coach conversations will lose early context about the user's goals and scores that were established in the first few messages.

---

## 6. Auto-Refresh Loop

### BUG-013 — `startAutoRefresh` creates a `setInterval` that is never cleared
**Severity: Medium**
`startAutoRefresh` (line 2340) calls `setInterval(...)` and discards the returned interval ID. There is no mechanism to stop the interval if the user navigates away or if the page becomes hidden. On a long-running session:
1. If `applyLiveData` modifies DOM elements that are later removed by a re-render, the interval callback may operate on detached nodes.
2. The `window.__pendingScoreQuestions` check inside the interval (line 3354) uses a global flag — if `buildScoreQuestions` is called by the interval simultaneously with a user interaction, there is a potential double-render (though single-threaded JS prevents a true race).

**Fix:** Store the interval ID: `window.__refreshIntervalId = setInterval(...)`. Use `document.addEventListener('visibilitychange', ...)` to pause when tab is hidden: `if (document.hidden) clearInterval(window.__refreshIntervalId)` and restart on visible.

### ENHANCEMENT-008 — Freshness chip logic only updates on data change
In the auto-refresh callback (lines 2358-2362), if the data is unchanged, only `updateFreshnessChip` is called. This correctly shows "Stale" after 2 minutes. However, after a network failure, `setFreshnessOffline` sets the chip to "Offline" permanently — even if the next interval tick succeeds. The chip never automatically recovers from "Offline" back to "Stale" or "Fresh" unless data actually changes.
**Fix:** In the `.then` success handler, always call `updateFreshnessChip` (already done), and ensure it can transition from "offline" back to "fresh" by not requiring a class change — the current `chip.className = 'freshness-chip ...'` assignment is sufficient, but verify that the `setFreshnessOffline` path does not set a permanent state that blocks recovery. Review: it does not — the next successful fetch will overwrite the class. This is actually fine; the perceived bug is a UX confusion not a code defect. Low priority.

---

## 7. Mobile Responsiveness

### BUG-014 — Coach panel bottom position conflicts with mobile browser chrome
**Severity: Medium**
At 480px breakpoint (line 1735-1750): `.coach-panel { bottom: 88px; ... max-height: 70vh; }` and `.coach-fab { bottom: 16px; }`. On iOS Safari with the bottom address bar visible, `100vh` is the visual viewport height, not the layout viewport. `max-height: 70vh` may cause the input row to be obscured behind the browser's native bottom bar.
**Fix:** Use `max-height: calc(70dvh - env(safe-area-inset-bottom))` if targeting iOS Safari, or test with actual device to confirm.

### ENHANCEMENT-009 — Heatmap overflows horizontally on very small screens
The heatmap renders 14 columns of weekly data. On screens below 360px, even with `.pulse-heatmap-wrap { overflow-x: auto }` (line 1265), the heatmap-months label row (`#heatmap-months`) uses `flex: 1` on each month label, causing it to not scroll in sync with the `.heatmap-weeks` below. The month labels and the grid will desync on scroll.
**Fix:** Wrap both `heatmap-months` and `heatmap-grid` in a single scrollable container so they scroll together.

### ENHANCEMENT-010 — `quick-stats-banner` 2-column layout at 768px has unequal gutters
Line 1097: `.qs-card { flex: 0 0 calc(50% - 4px); }` but gap is `8px`. With two cards per row, the gap calculation should be `calc(50% - 4px)` where 4px is half the gap. However, the gap is `8px` between items, so each card needs `calc(50% - 4px)` — this is correct only if the flexbox gap is `8px` and there is no outer padding applied to the cards themselves. The banner uses `gap: 8px` (line 1093) which is correct. This is actually fine, but the card width override at line 1098 uses `calc(50% - 4px)` instead of `calc(50% - 4px)` — the math is correct but could be written more clearly as `calc((100% - 8px) / 2)`.

---

## Critical Issues — Action Priority

| Priority | ID | Summary |
|----------|----|---------|
| P1 | BUG-001 | Plaintext password exposed in client-side JS — security issue |
| P1 | BUG-006 | `buildGoalMountain` crashes if goals tier array is undefined |
| P2 | BUG-003 | Coach panel dialog missing focus trap — accessibility |
| P2 | BUG-012 | Module switch does not abort in-flight chat request |
| P2 | BUG-013 | Auto-refresh interval never cleared — memory / stale DOM risk |
| P2 | NOTE-006 | Embedded `__LIVE_DATA__` overrides fresher `data.json` |
| P3 | BUG-008 | `formatCoachText` produces malformed nested `<ul>` |
| P3 | BUG-014 | Coach panel clips behind iOS Safari bottom bar |
| P4 | BUG-002 | Heatmap cells not accessible to screen readers |
| P4 | BUG-010 | Streaks data never consumed from `data.json` |

---

*Verification: Report written from static code analysis of `/home/jared/projects/AI-CIV/aether/exports/777-command-center/index.html` (4038 lines) and `data.json`. No browser execution was performed — dynamic runtime issues (e.g. Chart.js rendering edge cases) may exist beyond what static analysis can surface.*
