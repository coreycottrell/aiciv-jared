# Memory: Pay-Test Chatbox - Desktop Height, Auto-Scroll, Logo Fixes

**Date**: 2026-02-20
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: Three chatbox UX fixes on pay-test pages (439 + 468)

---

## What Was Fixed

### 1. Chatbox Desktop Height (Too Small)
**Root cause**: `#pay-test-post-payment` container (created dynamically in JS) had `padding: 15%` inline style.
- 15% padding on ALL sides = 30% total buffer top+bottom, 30% horizontal
- This is the fixed overlay div (position: fixed, 100vw x 100vh)
- **Fix**: Changed `'padding: 15%',` → `'padding: 7.5% 12%',`
- Result: ~15% buffer top+bottom, ~24% horizontal (narrower sides look better)

**Location in JS** (~line 402100 in HTML widget): Look for `launchPostPaymentFlow` function

### 2. Auto-Scroll (Responses Appearing Below Input)
**Root cause**: `.ptc-messages` (flex: 1) was missing `min-height: 0`
- CSS Flexbox gotcha: without `min-height: 0`, flex items won't shrink below content size
- The scrollable container can't properly bound itself → content overflows → messages appear below viewport
- **Fix**: Added `min-height: 0;` to `.ptc-messages` CSS rule (after `flex: 1;`)
- The `scrollBottom()` function was already correct (scrollTop = scrollHeight)

**Location**: `.ptc-messages` CSS block at ~position 352293 in HTML

### 3. Logo Letter Spacing (PUREBR AI N weird spacing)
**Root cause**: `.ptc-header__brand` had `gap: 2px` between flex items
- The PUREBRAIN logo is rendered as 3 `<span>` elements in a flex container
- `gap: 2px` between spans + no explicit `letter-spacing: 0` = visible gaps
- **Fix**: Changed `gap: 2px` → `gap: 0` + added `letter-spacing: 0` to all three spans

**Location**: `.ptc-header__brand` CSS at ~position 361200 in HTML

---

## Architecture Notes

- Both pages (439=pay-test, 468=pay-test-sandbox) share IDENTICAL HTML widget code
- The ptc widget is self-contained: `initPayTestFlow(chatContainer, aiName, tier)`
- Container chain: `#pay-test-post-payment` (fixed overlay) → `.ptc-outer-shell` → `.ptc-wrapper` → `.ptc-messages` (scrollable)
- `.ptc-outer-shell` has `padding: 24px 32px` on desktop (px-based, fine)
- Mobile layout already worked correctly - NEVER touched mobile CSS

## Key Strings for Future Fixes

```
# FIX 1 - padding (in JS array)
old: "'padding: 15%',"
new: "'padding: 7.5% 12%',"

# FIX 2 - logo gap (in CSS)
old: "gap: 2px;\n    }\n\n    .ptc-header__brand-blue  { color: #2a93c1; }"
new: "gap: 0;\n      letter-spacing: 0;\n    }\n\n    .ptc-header__brand-blue  { color: #2a93c1; letter-spacing: 0; }"

# FIX 3 - messages scroll (in CSS)
old: "flex: 1;\n      overflow-y: auto;\n      padding: 20px 24px 16px;"
new: "flex: 1;\n      min-height: 0;\n      overflow-y: auto;\n      padding: 20px 24px 16px;"
```

## Deployment Pattern

1. Fetch via WP REST API: `GET /wp-json/wp/v2/pages/{ID}?context=edit`
2. Parse `meta._elementor_data` as JSON
3. Find `widgetType == 'html'` → `settings.html`
4. String replace in HTML
5. Validate with `json.dumps(parsed)` then `json.loads()`
6. POST back: `POST /wp-json/wp/v2/pages/{ID}` with `{"meta": {"_elementor_data": new_str}}`
7. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`
8. Verify by re-fetching and checking strings

## CSS Flexbox Scroll Gotcha (IMPORTANT)

**The min-height: 0 pattern for flex scroll containers:**
```css
.flex-parent {
  display: flex;
  flex-direction: column;
  height: 100%;  /* or fixed height */
}

.scrollable-child {
  flex: 1;
  min-height: 0;  /* CRITICAL - without this, child won't shrink */
  overflow-y: auto;
}
```
Without `min-height: 0`, the flex child won't shrink below its content height → overflow goes outside the bounds → scrollTop doesn't work properly.
