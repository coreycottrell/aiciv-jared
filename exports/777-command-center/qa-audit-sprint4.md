# 777 Command Center — QA Audit Report (Sprint 4)

**File audited:** `exports/777-command-center/index.html`
**Data file:** `exports/777-command-center/data.json`
**Audit date:** 2026-03-21
**Auditor:** PTT QA (Aether)
**File size:** 3,912 lines

---

## Summary

| Severity  | Count |
|-----------|-------|
| BLOCKER   | 3     |
| MAJOR     | 9     |
| MINOR     | 8     |
| COSMETIC  | 5     |
| **Total** | **25** |

---

## BLOCKER

### B-01 — Entire script block is duplicated (lines ~2007–2400 duplicated at ~2400–2670)

**Location:** `<script>` block, lines 2007–3912
**Description:** The entire first half of the JS — `loadDataAndInit`, `startAutoRefresh`, `showDataSourceChip`, `updateFreshnessChip`, `setFreshnessOffline`, `timeSince`, `applyLiveData`, the two `pwBtn.addEventListener` / `pwInput.addEventListener` bindings, and the auto-unlock IIFE — appears **twice** in full. The sample data variables (`dailyScores`, `sevenFs`, `goals`, `contacts`, `eulogies`, `microLaws`, `monthlyCounts`, `recentTasks`) and `generateScores` function are also declared twice with `let`, which is a **SyntaxError** in strict mode and causes `Identifier has already been declared` in modern browsers.

**Impact:** Page will throw a JavaScript SyntaxError on load in any browser enforcing ES6 block scoping. The dashboard will never render after authentication. This is the most critical bug in the file.

**Evidence:**
- `function applyLiveData` declared once (line 2165), then the identical block appears again starting at line 2403.
- `let dailyScores = generateScores(91)` appears at both line 2310 and line 2548/2551 — `let` redeclaration in the same scope is illegal.
- `pwBtn.addEventListener` called at lines 2274 and 2512 — double-binding causes double event firing.
- Auto-unlock IIFE runs twice (lines 2278 and 2516).

**Fix:** Remove the entire duplicate block. The canonical block runs from line 2007 to approximately line 2395. Everything from line 2396 to 2670 (up through `let recentTasks = [...]`) is a verbatim duplicate and should be deleted. Keep only the one `generateScores` call that initializes the variables, which the later code relies on.

---

### B-02 — `data.json` `proof_wall.monthly` key mismatch

**Location:** `applyLiveData()`, line 2499; `data.json`, line 433
**Description:** The JS reads `pw.monthly` to populate `monthlyCounts` (`if (pw.monthly && pw.monthly.length)`), but `data.json` names this array `monthly_2026`. The `__LIVE_DATA__` blob (line 1764) also uses `monthly_2026`. Because the key never matches, `monthlyCounts` always falls back to the hardcoded sample data (Oct–Mar), even when live data is loaded.

**Impact:** The Proof Wall bar chart always shows stale/fake monthly counts regardless of live data.

**Fix:** Change the JS read to `pw.monthly_2026 || pw.monthly` (to handle both formats), or rename the JSON key to `monthly` consistently.

---

### B-03 — Password stored and compared in plaintext client-side

**Location:** Line 2009: `const PASSWORD = '777grind';`
**Description:** The gate password is hardcoded in the HTML source. Anyone who opens DevTools or views source can read it immediately. `localStorage.setItem('777_unlocked', '1')` also means any script on the page can set this flag and bypass the gate entirely.

**Impact:** The password gate provides zero security. Any motivated person bypasses it in under 10 seconds.

**Fix:** For a personal single-user dashboard this may be acceptable as a deterrent, not a security control. If real protection is needed, move auth server-side. At minimum, hash the password and compare against a stored hash rather than comparing plaintext. Remove the hardcoded value from the bundle.

---

## MAJOR

### M-01 — `buildTodayRing()` uses hardcoded score 11 instead of live data

**Location:** `buildTodayRing()`, lines 2780–2782
**Description:** `const score = 11; const max = 15;` — these values are hardcoded. The ring chart never reflects the actual `daily_pulse.today.score` or `daily_pulse.today.max` values from `applyLiveData`. The header chip and checklist correctly use live values, but the canvas ring does not.

**Impact:** The prominent ring always shows 11/15 regardless of the actual score.

**Fix:** Read from `dailyScores[dailyScores.length - 1]` or expose the live score via a module-level variable that `buildTodayRing()` can consume.

---

### M-02 — `seven_fs.current` uses `career` key; JS maps `friends` instead

**Location:** `applyLiveData()`, line 2211; `data.json` / `__LIVE_DATA__`
**Description:** The live data provides `seven_fs.current.career` as one of the 7 F's, but the JS mapping array is `['faith', 'family', 'friends', 'fellowship', 'fun', 'fitness', 'finance']`. There is no `career` key in that array. Conversely, `friends` is in the JS array but not in the live data object.

**Impact:** The `career` score from live data is silently dropped. `friends` always falls back to `5` (the default). The radar chart and detail bars show incorrect values.

**Fix:** Reconcile the key names. Either update `data.json` to use `friends` instead of `career`, or add `career` to the JS mapping and remove `friends`.

---

### M-03 — Race condition: `buildScoreQuestions` may fire before checklist container exists

**Location:** `loadDataAndInit()`, lines 2345–2350; `initDashboard()`, lines 2688–2692
**Description:** `applyLiveData` stores questions in `window.__pendingScoreQuestions`. The `loadDataAndInit` flow calls `applyLiveData` first, then `initDashboard`, with the pending questions check at lines 2345–2350 (inside `loadDataAndInit`'s `.then()`) happening before `buildDailyChecklist()` (which creates the container) has run. The check at lines 2688–2692 inside `initDashboard` is correct, but the earlier check at line 2345 fires when the DOM container `checklist-items` does not yet exist.

**Impact:** When `__LIVE_DATA__` is present and the page loads cold, `buildScoreQuestions` may be called with a null `container`, silently no-ops (guarded by `if (!container) return`), then the `null` check at line 2692 also finds it consumed already and skips it. Result: live score questions are silently lost and the local DAILY_HABITS checklist renders instead.

**Fix:** Remove the premature check in `loadDataAndInit` (lines 2347–2350). Rely only on the check inside `initDashboard` after `buildDailyChecklist()` has run.

---

### M-04 — `monthlyCounts` field name conflict: `monthly` vs `monthly_2026` (see B-02)

Already covered in B-02. Listed here to flag that `applyLiveData` also never reads `proof_wall.by_year`, so the year-by-year bar chart (`buildProofBar`) always uses the 6-month sample array and never shows the 2019–2026 annual breakdown from live data.

**Fix:** After resolving B-02, consider adding a branch to switch the bar chart between monthly and annual views based on which data is available.

---

### M-05 — `dotPulse` keyframe animation name collision

**Location:** Lines 1313 (`@keyframes dotPulse`) and 1690 (`@keyframes dotPulse`)
**Description:** The keyframe name `dotPulse` is declared twice. The first (lines 1313–1316) animates opacity 1→0.4→1. The second (lines 1690–1694) uses `content:` property changes for the loading dots ellipsis effect. The second declaration overwrites the first in all browsers.

**Impact:** The `mandala-sync-dot.live` pulsing animation becomes a content animation (no visible effect on a background-color element), breaking the live sync dot visual feedback.

**Fix:** Rename one of the two animations. Suggested: `dotBlink` for the sync dot (already used correctly in `.freshness-chip.fresh .freshness-dot` at line 1227) and `loadingDots` for the coach panel loading indicator.

---

### M-06 — `card-animate` CSS class declared twice with conflicting definitions

**Location:** Lines 1004–1007 and lines 1507–1510
**Description:** `.card-animate` is defined at line 1004 with `animation: cardIn 0.5s ease forwards; opacity: 0;` and again identically at line 1507. While functionally harmless (identical rules), it signals a copy-paste artifact that may indicate a larger structural issue. The `prefers-reduced-motion` override at line 1513 overrides the second declaration but not the first in terms of source order.

**Fix:** Remove the duplicate definition at lines 1507–1510. The `@media (prefers-reduced-motion: reduce)` block already references `.card-animate` correctly.

---

### M-07 — Tooltip position not clamped to viewport

**Location:** `buildHeatmap()`, lines 2758–2768; `buildRelationshipRing()`, lines 2260–2268
**Description:** Tooltip positioning uses raw `e.pageX + 12` and `e.pageY - 32` without any viewport edge detection. On small screens or when hovering near the right or bottom edge, the tooltip overflows the viewport and is clipped or invisible.

**Impact:** On mobile or at 768px breakpoint, heatmap and relationship ring tooltips can appear off-screen.

**Fix:** Add viewport-aware clamping. After setting `left` and `top`, check against `window.innerWidth - tooltip.offsetWidth` and `window.innerHeight - tooltip.offsetHeight` and adjust.

---

### M-08 — `auto-refresh` fires even when `__LIVE_DATA__` is the source

**Location:** `startAutoRefresh()`, line 2067; `initDashboard()`, line 2672
**Description:** `startAutoRefresh` always calls `fetch('data.json?v=...')` regardless of whether the page is running from `__LIVE_DATA__` or a live server. When hosted as a static file on CF Pages without a `data.json` endpoint returning dynamic data, every 60-second fetch results in either a 404 or returning the cached static `data.json`. This generates unnecessary network traffic and the `catch` path calls `setFreshnessOffline()`, falsely marking data as offline even though `__LIVE_DATA__` was successfully loaded.

**Fix:** Skip the auto-refresh fetch loop when running in static mode (i.e., when `data.json` is a static file and no server-side update mechanism exists). Or gate it: `if (window.__LIVE_DATA__ && window.__LIVE_DATA__.source !== 'live') return;` at the top of `startAutoRefresh`.

---

### M-09 — `goals.top77` from live data is loaded but never rendered

**Location:** `applyLiveData()`, line 2224; `buildGoalMountain()`, entire function
**Description:** `data.json` and `__LIVE_DATA__` both contain a `goals.top77` array (99 entries in live data). `applyLiveData` never reads or stores `top77`. `buildGoalMountain` only renders `infinite`, `yearly`, `monthly`, `weekly`, and `daily`. The top-77 goals list — one of the most detailed pieces of goal data in the JSON — is silently ignored.

**Impact:** The Goal Mountain only shows sample goals even when live data contains real goal data with `progress` values.

**Fix:** Either add a `top77` tier to the Goal Mountain, or store `goals.top77` and use it to populate `goals.yearly` when `goals.yearly` is absent.

---

## MINOR

### N-01 — Streak values are hardcoded HTML, not driven by `data.json`

**Location:** Lines 1830–1863 (streak HTML markup); `data.json` `daily_pulse.streaks: {}`
**Description:** The 5 streak items (5AM Club: 14, Daily Reading: 21, Prayer & Bible: 30, Exercise: 7, Gratitude Log: 45) are hardcoded in the HTML markup. `data.json.daily_pulse.streaks` is an empty object `{}`. There is no code path that reads streaks from data and updates the DOM elements. The Quick Stats "Best Streak: 45d" is also hardcoded at line 3347.

**Fix:** Either populate `streaks` in `data.json` and add JS to read and render them, or document that these are intentionally static.

---

### N-02 — `heatmap-cell` tooltip hardcodes `/15` max score

**Location:** `buildHeatmap()`, line 2760
**Description:** Tooltip innerHTML reads `Score: ${score}/15`. When live data loads with `daily_pulse.today.max = 20` (as in `__LIVE_DATA__`), the heatmap cells still show `/15` max, which is incorrect.

**Fix:** Store the live max score in a module-level variable (e.g., `let dailyMax = 15`) and update it in `applyLiveData`. Use it in the tooltip.

---

### N-03 — `coach-messages` container not scrolled to bottom on first open

**Location:** AI Coach IIFE, `addMessage()` function (line 3801)
**Description:** `messagesEl.scrollTop = messagesEl.scrollHeight` is called after each message append. However on first open there is no initial welcome message and the scroll is not reset. If the user has scrolled up in a previous session and re-opens the panel, the view is not restored to the bottom.

**Fix:** Add `messagesEl.scrollTop = messagesEl.scrollHeight` inside the `fab.addEventListener('click', ...)` handler when `isOpen` becomes true.

---

### N-04 — `buildDailyChecklist` glow reads `DAILY_HABITS.length` (always 7) not actual question count

**Location:** `buildDailyChecklist()`, line 3451
**Description:** The glow message reads "All 7 Complete" and `glowEl.style.display = done === total` where `total = DAILY_HABITS.length = 7`. When `buildScoreQuestions` replaces the checklist with 20 live questions, the glow still checks `done === total` using the old 7-item DAILY_HABITS count via `updateCount()`. The outer glow function is not replaced.

**Impact:** With 20 live questions, the "Legendary Day" glow fires when only 7 of 20 questions are completed.

**Fix:** In `buildScoreQuestions`, call `glowEl.style.display = (doneCount === total && total > 0) ? 'block' : 'none'` directly rather than relying on the inner `updateCount` closure.

---

### N-05 — `buildSparklines` uses hardcoded fake data for Streak Score and Weekly Avg

**Location:** `buildSparklines()`, lines 2831–2833
**Description:** The "Streak Score" sparkline uses hardcoded `[14,14,15,16,17,20,21]` and "Weekly Avg" uses `[8,9,8,10,9,11,10]`. These are not derived from live data or localStorage.

**Fix:** Compute these from `dailyScores`: last 7 days for the 7-day chart, rolling 7-day average for the weekly avg chart.

---

### N-06 — `data-source-chip` and `freshness-chip-wrap` initially hidden via inline style but visibility toggled in JS

**Location:** Lines 1804 and 1805 (HTML); `showDataSourceChip()` line 2098
**Description:** Both elements use `display:none` as inline style. `showDataSourceChip` calls `chip.style.display = 'block'` which works, but creates a specificity pattern where inline style overrides any CSS class attempting to hide them again (e.g., in print media or responsive rules). Print CSS at line 1755 uses `display:none !important` which catches this correctly but is fragile.

**Fix:** Use a CSS class (e.g., `.visible`) to control visibility rather than inline `display` toggling.

---

### N-07 — `legacy.eulogies` from `__LIVE_DATA__` is never applied

**Location:** `applyLiveData()`, line 2261; `buildEulogies()`
**Description:** `applyLiveData` reads `data.legacy.vision` but never reads `data.legacy.eulogies`. The `eulogies` module-level array is always the hardcoded sample (Lily, Melanie, Business Partner, Mentee). The live data contains real eulogy text from family, friend, and business_partner perspectives.

**Fix:** In `applyLiveData`, map `data.legacy.eulogies` to the `eulogies` array and call `buildEulogies()` to re-render.

---

### N-08 — `card-title-dot` inside checklist header uses both a class and redundant inline styles

**Location:** Line 1869
**Description:** The checklist header dot uses both `class="card-title-dot orange"` and inline `style="width:6px;height:6px;border-radius:50%;background:var(--orange);display:inline-block;flex-shrink:0;"`. The inline styles duplicate what `.card-title-dot` and `.card-title-dot.orange` already define in CSS, creating a maintenance hazard.

**Fix:** Remove the inline style; rely on the CSS classes.

---

## COSMETIC

### C-01 — `header-score-chip` initialized with hardcoded `TODAY: 11/15`

**Location:** Line 1803
**Description:** The chip shows `TODAY: 11/15` until `applyLiveData` updates it. On first paint this is misleading.

**Fix:** Initialize to `TODAY: —/—` or an empty state, then let the data loader populate it.

---

### C-02 — `ring-max` label in HTML hardcodes `/15`

**Location:** Line 1818: `<div class="ring-max">/15</div>`
**Description:** Same as N-02 but in the HTML markup. When max is 20, the ring label still shows `/15`.

**Fix:** Update this element in the same code path that updates the ring score.

---

### C-03 — 9 `onmouseover`/`onmouseout` inline event handlers on exercise module links

**Location:** Lines 1630–1663 (exercise module cards) and lines 1730–1776 (thinking exercise cards)
**Description:** Hover effects are implemented via inline `onmouseover` and `onmouseout` style mutations. This mixes presentation logic into HTML, is harder to override with CSS, and prevents respecting `prefers-reduced-motion`.

**Fix:** Move hover effects to CSS `:hover` rules. These cards already have a `.card` hover rule pattern established.

---

### C-04 — `checklist-glow` text is hardcoded "All 7 Complete" but count varies

**Location:** Line 1875
**Description:** The glow text hardcodes "7" but when live data loads 20 questions, the count is wrong.

**Fix:** Set the glow text dynamically based on `DAILY_HABITS.length` or the live questions count.

---

### C-05 — `qs-streak` value hardcoded to `45` in buildQuickStats, never computed

**Location:** `buildQuickStats()`, line 3347: `const bestStreak = 45;`
**Description:** Best streak is hardcoded. No computation from `dailyScores` is performed.

**Fix:** Compute the longest consecutive non-zero streak from `dailyScores` and use that value.

---

## Data Flow Summary

| Data path | Status |
|---|---|
| `__LIVE_DATA__` → heatmap | Working |
| `__LIVE_DATA__` → today score chip | Working |
| `__LIVE_DATA__` → checklist questions | Broken (race condition, B-01 duplicate binding) |
| `__LIVE_DATA__` → 7 F's radar | Partial (career/friends key mismatch, M-02) |
| `__LIVE_DATA__` → proof wall monthly chart | Broken (key mismatch B-02) |
| `__LIVE_DATA__` → proof wall total count | Working |
| `__LIVE_DATA__` → today ring canvas | Broken (hardcoded, M-01) |
| `__LIVE_DATA__` → eulogies | Missing (N-07) |
| `__LIVE_DATA__` → micro laws | Not consumed (data.json has them, JS uses static array) |
| `localStorage` → mandala progress | Working |
| `localStorage` → checklist state | Working |
| 60s auto-refresh | Fires unnecessarily in static mode (M-08) |

---

## Performance Notes

- The `__LIVE_DATA__` inline script block is approximately 8KB of JSON embedded in the HTML. This is a reasonable tradeoff for avoiding a fetch on load but adds to initial parse time.
- 14 weeks of heatmap cells = 98 DOM nodes created on every `buildHeatmap()` call. This is acceptable but `buildHeatmap` is called once and never torn down, so repeated calls (if the page is ever reinitialised) would append duplicate cells.
- Chart.js 4.4.0 loaded from CDN without a SRI hash. If the CDN is unavailable, all charts fail silently.
- `backdrop-filter: blur(8px)` on every `.card` element (and the header) can cause GPU compositing layer pressure on mid-range mobile. Acceptable for a personal dashboard, but worth noting.

---

## Accessibility Summary

- Password input has no `<label>` element — relies on visual `.gate-label` div. Screen readers will not associate the label. **Add `<label for="pw-input">`.**
- `.check-item` divs are not `<button>` or `role="checkbox"` elements. Keyboard users cannot tab to them or toggle them with Space/Enter.
- Heatmap cells have `cursor:pointer` and mouse events but no keyboard focus or `role` attribute. Screen readers cannot access the heatmap data.
- `.f-item` details toggle on click but have no `aria-expanded` or `role="button"` attribution.
- Relationship ring SVG nodes have tooltip on mouse but no `<title>` element inside the SVG for screen readers.
- Color contrast: `--text-muted: #4a5570` on `--bg3: #111729` is approximately 2.8:1 — below WCAG AA 4.5:1 for body text.

---

## Highest-Priority Fix Order

1. **B-01** — Remove the duplicate JS block. This is a SyntaxError that breaks the entire page.
2. **B-02** — Fix `monthly_2026` key mismatch so the Proof Wall bar chart gets live data.
3. **M-03** — Fix the race condition so live score questions render correctly.
4. **M-01** — Wire `buildTodayRing()` to the actual live score.
5. **M-02** — Fix the `career`/`friends` key mismatch in 7 F's.
6. **M-05** — Rename the duplicate `dotPulse` keyframe.
7. **N-07** — Apply live eulogy data from `__LIVE_DATA__`.
