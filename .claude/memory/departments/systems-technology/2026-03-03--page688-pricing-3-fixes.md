# Page 688 Pricing Section - 3 Critical Fixes
**Date**: 2026-03-03
**Type**: gotcha + fix pattern
**Agent**: dept-systems-technology

## Context
Pay-Test-Sandbox-2 (page 688) pricing section had 3 bugs Jared reported from a screenshot.

## The 3 Issues and Root Causes

### Issue 1: Awakened Button Text Showing Dynamic Name
**Symptom**: Button shows "Activate Keen Now" instead of "CLAIM THIS SPOT"
**Root cause**: `showPricing()` JS function dynamically sets `proCta.textContent`:
```javascript
document.getElementById('proCta').textContent = hasName
    ? `Activate ${aiName} Now`
    : 'Activate Now';
```
**Fix**: Hardcode to static text:
```javascript
document.getElementById('proCta').textContent = 'CLAIM THIS SPOT';
```

### Issue 2: Awakened PayPal Charging $79 Instead of $149
**Symptom**: Clicking "CLAIM THIS SPOT" opens PayPal at $79
**Root cause**: The `PRICES` object in the PayPal modal JS had wrong amount:
```javascript
var PRICES = {
    Awakened:  '79.00',   // WRONG - should be 149.00
    Bonded:    '149.00',
    ...
```
**IMPORTANT**: There are TWO PRICES blocks in the page - one is a template with empty strings `''`,
the other is the real one with values. Make sure to only match the one with `'79.00'`.
**Fix**: `Awakened: '149.00'`

### Issue 3: Feature Text Shows "Keen has a permanent home..." etc.
**Symptom**: Pricing features show the user's AI name dynamically
**Root cause**: Features use `<span class="ai-name-dynamic">Your AI</span>` which gets replaced
by `updateAllDynamicNames(aiName)` - this function replaces ALL `.ai-name-dynamic` spans including
those in pricing features.
**Fix**: Remove the `ai-name-dynamic` class from pricing feature spans - replace with static "Your AI":
```html
<!-- Before -->
<span class="ai-name-dynamic">Your AI</span> has a permanent home
<!-- After -->
Your AI has a permanent home
```

## Technique Used
- Fetch `_elementor_data` via `GET /wp-json/wp/v2/pages/688?context=edit`
- All HTML is in widget ID `292c72a` under `settings.html`
- The raw `_elementor_data` is a JSON string - quotes are escaped as `\"`
- Apply fixes to the raw string using `str.replace()`
- Push back via `POST /wp-json/wp/v2/pages/688` with body `{"meta": {"_elementor_data": "..."}}`
- Clear cache: `DELETE /wp-json/elementor/v1/cache`
- Verify by re-fetching `_elementor_data` from API (not from rendered page - page 688 is password-protected)

## Verification Method
Cannot verify from rendered HTML (page is password-protected to unauthenticated curl).
Must verify by re-fetching `_elementor_data` via authenticated API and parsing the widget HTML.

## Auth
- User: Aether
- App Password: ZGuh 1W8k WpWM c9iy kqyd buPr
- Always include: `-H "User-Agent: Mozilla/5.0 (compatible; Aether/1.0)"` (Cloudflare blocks without it)
