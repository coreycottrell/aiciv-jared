# Pricing Button Dynamic AI Name Revert — Page 688

**Date**: 2026-03-03
**Agent**: dept-systems-technology
**Page**: 688 (pay-test-sandbox-2)
**Status**: DEPLOYED AND VERIFIED (8/8 checks PASS)

## Task

Revert incorrect hardcoding of "CLAIM THIS SPOT" button text on pricing section. All three paid tier buttons (Awakened, Partnered, Unified) should dynamically update to `Activate [AI NAME] Now` when the user has chosen an AI name. Enterprise stays static: "LET'S TALK".

## Root Cause of Bug

Previous deployment hardcoded `document.getElementById('proCta').textContent = 'CLAIM THIS SPOT'` in `showPricing()` instead of using the dynamic pattern.

## All 6 Changes Made

### 1. showPricing() JS function - proCta reverted
Old:
```js
// 4. CTA button: "Activate Nova Now"
document.getElementById('proCta').textContent = 'CLAIM THIS SPOT';
```

New:
```js
// 4. CTA buttons: "Activate [AI NAME] Now" for all 3 paid tiers
document.getElementById('proCta').textContent = hasName ? `Activate ${aiName} Now` : 'Activate Your AI Now';
document.getElementById('partnerCta').textContent = hasName ? `Activate ${aiName} Now` : 'Activate Your AI Now';
document.getElementById('unifiedCta').textContent = hasName ? `Activate ${aiName} Now` : 'Activate Your AI Now';
```

### 2. HTML proCta button - static text changed
- Was: `CLAIM THIS SPOT`
- Now: `Activate Your AI Now` (JS will override this when pricing shows)

### 3. HTML Partnered button - id added + static text changed
- Added `id="partnerCta"` (required for JS to target it)
- Was: `GET STARTED`
- Now: `Activate Your AI Now`

### 4. HTML Unified button - id added + static text changed
- Added `id="unifiedCta"` (required for JS to target it)
- Was: `GET STARTED`
- Now: `Activate Your AI Now`

### 5 & 6. Feature text spans - ai-name-dynamic class restored
Two spans inside Awakened tier feature list:
- `<span style="display:inline">Your AI has a permanent home...` → wrapped inner "Your AI" with `<span class="ai-name-dynamic">Your AI</span>`
- `<span style="display:inline">Your AI inherits wisdom...` → same pattern

## How Dynamic Names Work on This Page

- `updateAllDynamicNames(aiName)` — updates ALL `.ai-name-dynamic` elements
- Called in `showPricing()` and on state change
- The `hasName` check: `const hasName = aiName && aiName !== 'PURE BRAIN';`
- When user has named their AI (e.g., "Keen"): buttons say "Activate Keen Now"
- When no name: buttons say "Activate Your AI Now"

## Deployment Notes

- `_elementor_data` length: 492,610 chars post-deploy
- Delta: +448 chars from original 492,162 (adding IDs + restoring classes)
- Elementor cache cleared via DELETE /elementor/v1/cache
- Script: `/tmp/fix_button_text_688.py`

## Key Pattern for Future Pricing Button Updates

When any button needs dynamic AI name text in showPricing():
1. Give the button an `id` in the HTML
2. In `showPricing()`, use: `document.getElementById('btnId').textContent = hasName ? \`Activate ${aiName} Now\` : 'Activate Your AI Now';`
3. Set static fallback in HTML button text to 'Activate Your AI Now'

Enterprise button pattern (static, no ID needed):
```html
<button class="pricing-card__cta pricing-card__cta--orange" onclick="openWaitlistModal('Enterprise')">
    LET'S TALK
</button>
```
