# Sandbox-3 Timeout Fallback Removal (v4.8)

**Date**: 2026-03-04T21:17:13
**Agent**: dept-systems-technology / full-stack-developer
**Type**: bugfix + pattern
**Tags**: sandbox3, portal-button, runPortalButtonWatcher, timeout, fallback-message, page-1232

---

## Bug: Fallback Timeout Message Should Never Appear

### Problem

After 60 polls (30 minutes), `runPortalButtonWatcher()` was showing a fallback message:
> "Your AiCIV is still finishing up. Check your email for portal access."

Jared's instruction: this message should NEVER appear. The button should just stay greyed out forever until the magic link arrives and the button lights up.

### Root Cause

Previous fix (v4.7) fixed the onclick bug and the `safeAiName` dynamic name, but left the timeout fallback intact. The fallback message was in the `if (pollCount > MAX_POLLS)` block.

### Fix Applied (v4.8)

**Removed** the DOM manipulation that replaced the placeholder with a fallback `<div>`.

**Old code (removed):**
```javascript
if (pollCount > MAX_POLLS) {
  clearInterval(intervalId);
  // Timeout fallback — show email message
  const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
  if (currentPlaceholder) {
    const fallbackMsg = document.createElement('div');
    fallbackMsg.style.cssText = 'font-size:13px; color:var(--text-muted); padding:8px 0;';
    fallbackMsg.textContent = 'Your AiCIV is still finishing up. Check your email for portal access.';
    currentPlaceholder.replaceWith(fallbackMsg);
  }
  logPayTestData({ ...payTestData, event: 'portal:timeout', containerName });
  return;
}
```

**New code (deployed):**
```javascript
if (pollCount > MAX_POLLS) {
  clearInterval(intervalId);
  // Timeout reached — button stays greyed out (no fallback message).
  // The button will remain disabled until the magic link arrives via email.
  logPayTestData({ ...payTestData, event: 'portal:timeout', containerName });
  return;
}
```

The `portal:timeout` event is still logged for debugging, but no UI change is made to the button.

---

## Status of Both Bugs After This Fix

| Bug | Status |
|-----|--------|
| Fallback timeout message appearing | FIXED (v4.8) |
| "Your AiCIV is ready" hardcoded | ALREADY FIXED (v4.7) — safeAiName in use |

---

## Deployment

- **Page**: 1232 (pay-test-sandbox-3)
- **Method**: `_elementor_data` update via REST API POST `/wp/v2/pages/1232`
- **Cache cleared**: DELETE `/elementor/v1/cache` (status 200)
- **Verified**: Re-fetched page, confirmed 'still finishing up' not present, 'button stays greyed out' comment present
- **Deployed**: 2026-03-04T21:17:13

---

## Key Pattern: Previous Fixes May Be Partial

When a previous session says "deployed and verified", always check the LIVE elementor data before assuming it's actually fixed. In this case:
- v4.7 was deployed and fixed onclick + hardcoded name
- But the timeout fallback was NOT in scope of that fix
- Jared saw it as the same bug because both involved old text

Always re-fetch `_elementor_data` fresh and grep for the exact strings before making any changes.
