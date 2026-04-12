# Memory: Chatbox v4.4 — Witness Direct IP Replaced by HTTPS Proxy

**Date**: 2026-02-25
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Switched all birth API calls from direct Witness HTTP IP to server-side HTTPS proxy. Container name restored to dynamic allocation.

---

## Problem Solved

v4.3.x chatbox called Witness directly at `http://104.248.239.98:8099`. This caused:
1. **Mixed-content error**: HTTPS page (purebrain.ai) calling an HTTP endpoint — blocked by browsers
2. **CORS**: IP:port endpoint not configured for purebrain.ai origin

## Solution

Changed `WITNESS_WEBHOOK_HOST` to `https://89.167.19.20:8443` — our HTTPS VPS that already has proxy endpoints built in `tools/purebrain_log_server.py`.

All 3 birth endpoint fetch calls go through the same constant, so one line change covers all three:
- `${WITNESS_WEBHOOK_HOST}/api/birth/start` → routes via `/api/proxy/birth/start`
- `${WITNESS_WEBHOOK_HOST}/api/birth/code` → routes via `/api/proxy/birth/code`
- `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${container}` → routes via `/api/proxy/birth/portal-status/{container}`

---

## 4 Code Changes Made

### Change 1: WITNESS_WEBHOOK_HOST constant
```javascript
// Before:
const WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099';

// After:
const WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443';
```

### Change 2: Dynamic container name (removed hardcoded 'aiciv-07')
```javascript
// Before (v4.3.2 E2E test workaround):
window._pbContainerName = 'aiciv-07';
const containerName = 'aiciv-07';
payTestData.containerName = containerName;

// After (v4.4 — dynamic):
const containerName =
  (window._pbContainerName && /^[a-z0-9-]{1,64}$/.test(window._pbContainerName))
    ? window._pbContainerName
    : ('purebrain-' + firstName.toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20));
payTestData.containerName = containerName;
```

The code at lines ~10232-10238 already handled the server-authoritative override:
```javascript
if (startData.container && typeof startData.container === 'string') {
  const serverContainerName = startData.container.toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
  if (serverContainerName) {
    payTestData.containerName = serverContainerName; // server is authoritative
  }
}
```
This was already present in v4.3.x — the /start response `container` field overwrites payTestData.containerName with the server's choice.

### Change 3: /start POST body — auto-allocate
```javascript
// Before:
body: JSON.stringify({ container: containerName }),

// After:
body: JSON.stringify({}), // v4.4: auto-allocate — server returns authoritative container name
```

### Change 4: /code uses payTestData.containerName
```javascript
// Before (used local const 'aiciv-07'):
body: JSON.stringify({ container: containerName, auth_code: trimmedCode }),

// After (uses the authoritative name from /start response):
body: JSON.stringify({ container: payTestData.containerName, auth_code: trimmedCode }),
```

---

## Output File

- **Path**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-chatbox-v44.html`
- **Format**: Full page HTML wrapped in `<!-- wp:html -->` tags
- **Size**: ~433KB (430KB HTML + 1.7KB new JS)
- **Status**: NOT deployed — file prepared for review only

---

## Proxy URL Reference

| Old (broken on HTTPS) | New (via proxy) |
|---|---|
| `http://104.248.239.98:8099/api/birth/start` | `https://89.167.19.20:8443/api/proxy/birth/start` |
| `http://104.248.239.98:8099/api/birth/code` | `https://89.167.19.20:8443/api/proxy/birth/code` |
| `http://104.248.239.98:8099/api/birth/portal-status/{c}` | `https://89.167.19.20:8443/api/proxy/birth/portal-status/{c}` |

---

## Container Name Flow (v4.4)

1. `runBirthInit()` called with `firstName` from Q1
2. `containerName` resolved: `window._pbContainerName` (if valid) OR `purebrain-{firstName}`
3. `payTestData.containerName = containerName` (initial value)
4. POST `{}` to `/api/proxy/birth/start`
5. Response: `{ status: 'url_ready', oauth_url: '...', container: 'aiciv-XX' }`
6. `payTestData.containerName = 'aiciv-XX'` (server overrides with authoritative name)
7. `/birth/code` sends `{ container: payTestData.containerName, auth_code: '...' }`
8. `/portal-status` polls `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${payTestData.containerName}`

---

## Verification: All 22 checks passed

- wp:html wrapper present
- DOCTYPE html present
- Chat Flow v4.4 header and changelog present
- New proxy host (89.167.19.20:8443) present
- Old IP absent from executable code (only in changelog comments)
- All 3 endpoints route through WITNESS_WEBHOOK_HOST
- Hardcoded aiciv-07 absent from executable code
- Dynamic container resolution present
- Auto-allocate /start body (sends {})
- /birth/code uses payTestData.containerName
- Security patches intact: sanitizeText, no sk-ant-, no old fallback msg

---

## Related Memory

- `2026-02-25--witness-birth-proxy-endpoints.md` (proxy endpoints built in purebrain_log_server.py)
- `2026-02-24--chatbox-v433-birth-ux-fixes.md` (v4.3.3 changes that v4.4 builds on)
- `2026-02-24--chatbox-v432-manual-birth-aiciv07.md` (why aiciv-07 was hardcoded — now removed)
- `2026-02-24--chatbox-v42-dual-storage-deploy-pattern.md` (deploy pattern when deploying)
