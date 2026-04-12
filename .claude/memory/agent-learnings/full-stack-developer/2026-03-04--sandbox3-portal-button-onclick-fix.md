# Sandbox-3 Portal Button Onclick Fix (v4.7)

**Date**: 2026-03-04
**Agent**: dept-systems-technology / full-stack-developer
**Type**: bugfix + gotcha
**Tags**: sandbox3, portal-button, portal-status, runPortalButtonWatcher, onclick, aiName, dynamic-name, page-1232

---

## Bug 1: Button Lit Up But Click Did Nothing

### Root Cause

`runPortalButtonWatcher()` in page 1232 had TWO structural issues:

1. **Wrong variable**: When status returned `ready: true`, the onclick handler referenced `data.portalUrl` but `data` was never defined in that scope. The validated URL was in `rawPortalUrl`.

2. **Wrong element type**: The code built a new `portalBtn` (`<a>` element) with correct `href`, `target`, `rel`, and `textContent` — but then updated the OLD `currentPlaceholder` (`<button>`) with an onclick instead of replacing it. The `<a>` element was built but never inserted into the DOM.

### Buggy Code
```javascript
currentPlaceholder.onclick = function() { window.open(data.portalUrl, '_blank'); };;
// data is undefined — should be rawPortalUrl or the portalBtn.href
// Also: currentPlaceholder was still a <button>, not the <a> element built above
```

### Fix Applied (v4.7)
```javascript
// FIX v4.7: Replace placeholder with the already-built portalBtn <a> element.
portalBtn.classList.add('ptc-portal-btn--active');
const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
if (currentPlaceholder) {
  currentPlaceholder.replaceWith(portalBtn);
}
```

The `portalBtn` `<a>` element already had:
- `href` = `rawPortalUrl` (validated against allowedDomains)
- `target` = `'_blank'`
- `rel` = `'noopener'`
- `textContent` = `Enter ${safeAiName}'s Brain Stream`

Using `replaceWith()` was the cleanest fix — no need to patch onclick on the old button.

---

## Bug 2: "Your AiCIV is ready." Hardcoded Text

### Root Cause
The chat notification message after the button activated was hardcoded:
```javascript
`<span style="color: #4caf50; font-weight: 700;">Your AiCIV is ready.</span> `
```

This should use `safeAiName` which was already sanitized at function entry.

### Fix Applied (v4.7)
```javascript
`<span style="color: #4caf50; font-weight: 700;">${safeAiName} is ready.</span> `
```

For "Keen", this now displays: "**Keen is ready.** Keen's portal is live — the button just appeared above. Let's go."

---

## Deployment

- **Page**: 1232 (pay-test-sandbox-3)
- **Elementor element**: `292c72a` (HTML widget containing full page JS)
- **Method**: `_elementor_data` update via REST API + Elementor cache clear
- **Deployed**: 2026-03-04T13:33:45
- **Verified**: All 5 checks pass (bugs removed, fixes present)

---

## Key Pattern: runPortalButtonWatcher Architecture

The function:
1. Polls `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${containerName}` every 30 seconds
2. On `status.ready === true`:
   - Creates `portalBtn` as `<a>` with validated `href`
   - Now correctly replaces placeholder with `portalBtn.replaceWith()` (v4.7 fix)
   - Sends chat notification with dynamic AI name
3. Timeout after 60 polls (30 min): shows email fallback message

## Allowed Portal URL Domains
```javascript
const allowedDomains = ['purebrain.ai', 'puremarketing.ai', 'aiciv.dev'];
```
URL must be HTTPS and match one of these exactly or as subdomain.

## safeAiName Context
- In sandbox-3, aiName comes from `window._pbState.aiName` (set during Q&A flow)
- Bypass path hardcodes `'Keen'` as `bypassName`
- `sanitizeText()` is applied at function entry to prevent XSS
