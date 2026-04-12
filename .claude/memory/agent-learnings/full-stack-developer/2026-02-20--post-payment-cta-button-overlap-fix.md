# Memory: Post-Payment CTA Button Overlap Fix

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: ptc-welcome-btn overlapping last chat message on pay-test pages

---

## Problem

On pay-test pages (439 + 468), the final CTA button "Keen is ready — see your next steps →"
was visually overlapping with the last chat message "This is going to be worth it."

## Root Cause

The `.ptc-welcome-btn` was appended directly to `.ptc-wrapper` (the flex column container)
after the messages list. It had only `margin: 8px 20px 24px` (8px top margin) which was
insufficient to create visual separation from the last message bubble above it.

Additionally, without `flex-shrink: 0`, the button could theoretically shrink in constrained
layouts.

## The Fix

**Changed CSS in `.ptc-welcome-btn`:**
- `margin: 8px 20px 24px` → `margin: 32px 20px 24px` (increased top margin from 8px to 32px)
- Added `flex-shrink: 0` (ensures button stays full size in flex layout)

## Exact Replacement Strings

```python
OLD_CSS = '.ptc-welcome-btn {\\n      background: linear-gradient(135deg, var(--bright-orange), #c73000);\\n      border: none;\\n      border-radius: var(--radius);\\n      color: #fff;\\n      cursor: pointer;\\n      font-size: 17px;\\n      font-weight: 700;\\n      padding: 16px 32px;\\n      margin: 8px 20px 24px;\\n      transition: opacity 0.2s, transform 0.15s;\\n      letter-spacing: 0.02em;\\n    }'

NEW_CSS = '.ptc-welcome-btn {\\n      background: linear-gradient(135deg, var(--bright-orange), #c73000);\\n      border: none;\\n      border-radius: var(--radius);\\n      color: #fff;\\n      cursor: pointer;\\n      font-size: 17px;\\n      font-weight: 700;\\n      padding: 16px 32px;\\n      margin: 32px 20px 24px;\\n      flex-shrink: 0;\\n      transition: opacity 0.2s, transform 0.15s;\\n      letter-spacing: 0.02em;\\n    }'
```

## Architecture Note

The button is created in JS (`runQuestionnaire()` function) as:
```javascript
const welcomeBtn = document.createElement('button');
welcomeBtn.className = 'ptc-welcome-btn';
welcomeBtn.textContent = `${aiName} is ready — see your next steps →`;
// actions div is cleared first, then button appended to ptc-wrapper
actions.innerHTML = '';
dom.container.appendChild(welcomeBtn);
```

The button is the last flex child of `.ptc-wrapper` (flex column), which comes after:
1. `.ptc-header` (flex-shrink: 0)
2. `.ptc-messages` (flex: 1, scrollable)
3. Cleared `.ptc-actions`

## Mirror Rule Applied

Fix applied to BOTH pages simultaneously:
- Page 468 (pay-test-sandbox)
- Page 439 (pay-test live)

## Verification

After fix: `margin: 32px 20px 24px` present on both pages, `flex-shrink: 0` present.
Elementor cache cleared after both updates.

## Status: ALREADY DEPLOYED

This fix was deployed in a previous session. When re-checking in 2026-02-20 session,
the fix was confirmed already in place on both pages 439 and 468.
The `.ptc-welcome-btn` CSS already had `margin: 32px 20px 24px` and `flex-shrink: 0`.

## Verification Gotcha

When checking with Python string search on `elem_data`, use a window of at least 400-500
characters when searching within a CSS block - a 250-char window may cut off before reaching
the margin/flex-shrink properties due to background gradient taking many characters.
