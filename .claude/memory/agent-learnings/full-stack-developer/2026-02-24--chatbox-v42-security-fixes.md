# Memory: Chatbox v4.2 — Security Hardening (P0 + P1 Fixes)

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Applied P0 and P1 security fixes to Witness birth pipeline chatbox before production deploy

---

## What Was Fixed

### P0 Fixes (Production Blockers)

#### CRIT-003 — Mixed-Content (HTTP → HTTPS)
```javascript
// Before (v4.1):
const WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099';

// After (v4.2):
const WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai';
```
All three Witness API calls (`/api/birth/start`, `/api/birth/code`, `/api/birth/portal-status/{container}`) now route through the HTTPS proxy. Modern browsers silently block HTTP fetches from HTTPS pages — this fix is what actually makes the feature work.

Also updated historical changelog comment in the file header to remove the old IP from all text (deploy script checks for absence of `104.248.239.98` string).

#### CRIT-004 — XSS via aiName in innerHTML
Added `sanitizeText()` helper near `WITNESS_WEBHOOK_HOST`:
```javascript
function sanitizeText(str) {
  const d = document.createElement('div');
  d.textContent = typeof str === 'string' ? str.slice(0, 60) : '';
  return d.innerHTML; // returns HTML-escaped string safe for innerHTML
}
```

Applied at three points:
1. `initPayTestFlow()` entry point — `aiName = sanitizeText(aiName || 'Pure')` before seeding payTestData
2. `runBirthInit()` entry point — `const safeAiName = sanitizeText(aiName || 'Your AiCIV')`
3. `runPortalButtonWatcher()` entry point — `const safeAiName = sanitizeText(aiName || 'Your AiCIV')`

OAuth button link text built via DOM API (not innerHTML template literal):
```javascript
// WRONG (v4.1):
oauthMsg.innerHTML = `... Authorize ${aiName}\u2019s AI Brain \u2192 ...`;

// RIGHT (v4.2):
oauthMsg.innerHTML = '... static structure only ... <a class="ptc-oauth-link"></a> ...';
const oauthLink = oauthMsg.querySelector('.ptc-oauth-link');
oauthLink.href = oauthUrl;  // already validated
oauthLink.textContent = `Authorize ${safeAiName}\u2019s AI Brain \u2192`;
oauthLink.addEventListener('click', function () { ... });
```

Portal button already used `.textContent` — just needed `safeAiName` substituted.

#### HIGH-002 — OAuth URL Validation Before DOM Injection
After receiving `startData.oauth_url` from Witness, validate before storing:
```javascript
try {
  const oauthUrlParsed = new URL(startData.oauth_url);
  if (!['https:'].includes(oauthUrlParsed.protocol) ||
      !['claude.ai', 'www.claude.ai', 'anthropic.com'].some(
        h => oauthUrlParsed.hostname === h || oauthUrlParsed.hostname.endsWith('.' + h)
      )) {
    throw new Error('OAuth URL failed domain validation: ' + oauthUrlParsed.hostname);
  }
} catch (e) {
  throw new Error('Invalid OAuth URL from Witness: ' + e.message);
}
oauthUrl = startData.oauth_url;
```
This mirrors the existing `portalUrl` validation pattern (lines ~2135-2143) which was already correctly implemented for the portal button.

### P1 Fixes (Recommended)

#### HIGH-003 — containerName Allowlist
```javascript
const rawContainerName = (window._pbContainerName && window._pbContainerName.trim())
  ? window._pbContainerName.trim()
  : `purebrain-${(firstName || 'user').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20)}`;
const containerName = (rawContainerName || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64) ||
  `purebrain-${(safeFirstName || 'user').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20)}`;
```
Enforces lowercase alphanumeric + hyphens only, max 64 chars, regardless of whether it came from `window._pbContainerName` or was derived from `firstName`.

#### MED-003 — Remove payTestData/logPayTestData from window
```javascript
// Before (v4.1):
window.initPayTestFlow = initPayTestFlow;
window.payTestData     = payTestData;
window.logPayTestData  = logPayTestData;

// After (v4.2):
window.initPayTestFlow = initPayTestFlow;
// payTestData and logPayTestData are internal state only
```
`payTestData` contains email, name, containerName, birthOauthUrl — not safe to expose to third-party scripts/browser extensions.

---

## Deployment

- **File**: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js`
- **Deploy script**: `/home/jared/projects/AI-CIV/aether/tools/deploy_chatbox_v4.py`
- **Page 688** (pay-test-sandbox-2): ALL CHECKS PASSED — 458,362 → 462,602 chars
- **Page 689** (pay-test-2): ALL CHECKS PASSED — 455,947 → 460,187 chars
- **Elementor cache**: Cleared (HTTP 200)
- **HTTP 200 verification**: Both pages confirmed

### Deploy script updated
Added new pre-flight checks:
- Asserts `'https://api.purebrain.ai' in V4_JS` (HTTPS proxy present)
- Asserts `'104.248.239.98' not in V4_JS` (no plain HTTP IP)
- Asserts `'sanitizeText' in V4_JS` (XSS helper present)
- Post-deploy verification checks updated to match v4.2 markers

---

## Key Patterns / Teaching Notes

### Why aiName sanitization is at the ENTRY POINT
Rather than sanitizing at every innerHTML call site, sanitize once when the variable is first set (`initPayTestFlow`). Any downstream function that receives `aiName` from `payTestData.aiName` then gets the already-safe value. For functions that receive `aiName` as a parameter (like `runBirthInit` and `runPortalButtonWatcher`), sanitize again at entry — defense in depth.

### The portalUrl validation was already correct
Lines 2135-2143 validated `portalUrl` for HTTPS + `.purebrain.ai` domain before DOM injection. The oauthUrl fix mirrors this exact pattern. When fixing similar bugs, check if a correct version already exists in the same file and replicate it.

### DOM API vs innerHTML template literal for user-controlled strings
Use DOM API (`.textContent`, `.href`, `.setAttribute`) for any value that comes from user input or external APIs. Use innerHTML template literals only for fully static structural HTML. The onclick pattern:
```javascript
// OLD: onclick attribute in innerHTML string (bad for external URLs)
<a onclick="...">

// NEW: addEventListener (safe regardless of context)
oauthLink.addEventListener('click', function () { ... });
```

### Deploy script pre-flight checks prevent regression
Adding `assert '104.248.239.98' not in V4_JS` to the deploy script means future developers cannot accidentally re-introduce the plain HTTP host. Negative assertions (things that must NOT be present) are as important as positive assertions.

---

## Security Report Reference

Source: `/home/jared/projects/AI-CIV/aether/exports/security-review-v4-witness.md`
Authored by: security-engineer-tech, 2026-02-24
Status after v4.2: P0 and P1 findings resolved. P2/P3 remain as post-ship items.

---

## Related Memory

- `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--witness-birth-pipeline-chatbox-v4.md`
- `.claude/memory/agent-learnings/security-engineer-tech/2026-02-24--witness-birth-pipeline-v4-review.md`
- `.claude/memory/agent-learnings/full-stack-developer/2026-02-22--chatbox-v3-security-patch.md`
