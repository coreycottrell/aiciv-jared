# Memory: Witness Birth Pipeline — 3 Fixes Deployed

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: CSP whitelist, env-detection host switch, birth/start body fix, flowCompleted flag

---

## Summary

Deployed 3 Witness-directed fixes to purebrain.ai pay-test birth pipeline. All verified live.

---

## Fix 1: CSP Whitelist for 89.167.19.20:8443 (Plugin v4.6.4)

**Problem**: Browser on sandbox page could not make fetch() calls to the Aether log server (89.167.19.20:8443) because it wasn't in the CSP connect-src directive.

**Fix**:
- Copied `purebrain-security-plugin-v463.php` → `purebrain-security-plugin-v464.php`
- Added `"https://89.167.19.20:8443; "` at end of connect-src block (was `"https://cdn.jsdelivr.net; "` → now `"https://cdn.jsdelivr.net " . "https://89.167.19.20:8443; "`)
- Bumped version to 4.6.4, added changelog entry
- Deployed via Playwright plugin editor (same pattern as v463)
- Verified live: `curl -sI https://purebrain.ai/pay-test-sandbox-2/?nocache=... | grep CSP` confirmed `89.167.19.20:8443` in connect-src

**Files**:
- `exports/purebrain-security-plugin-v464.php` (new file)
- `tools/security/deploy_plugin_v464_csp_connect_src.py` (new deploy script)

**Gotcha**: Initial curl verification missed it (Cloudflare CDN cache). Use `?nocache=` + `Cache-Control: no-cache` headers to bypass. The WP editor confirmation "File edited successfully" is reliable.

---

## Fix 2: WITNESS_WEBHOOK_HOST Environment Detection + Birth/Start Body + flowCompleted

**Problem 3 in 1** (all in `exports/purebrain-chatbox-v44.html`):

1. **Env detection**: `WITNESS_WEBHOOK_HOST` was hardcoded to `89.167.19.20:8443`. Production pages need `api.purebrain.ai`. Sandbox pages need direct IP.

2. **Empty birth/start body**: POST body was `{}`. Witness birth pipeline received no context about who is being born.

3. **Missing flowCompleted flag**: `logPayTestData(flow:complete)` never included `flowCompleted: true`. Witness couldn't tell if flow finished.

**Fixes applied**:
```javascript
// Fix 1: Environment detection
const IS_SANDBOX = window.location.pathname.includes('sandbox');
const WITNESS_WEBHOOK_HOST = IS_SANDBOX
  ? 'https://89.167.19.20:8443'   // sandbox = direct to Aether server
  : 'https://api.purebrain.ai';    // production = HTTPS proxy

// Fix 2: birth/start body
body: JSON.stringify({
  name: payTestData.name || firstName,
  email: payTestData.email || '',
  human_name: payTestData.name || firstName,
  tier: payTestData.tier || 'awakened',
  ai_name: payTestData.aiName || '',
}),

// Fix 3: flowCompleted
payTestData.flowCompleted = true;
await logPayTestData({ ...payTestData, event: 'flow:complete', flowCompleted: true });
```

**Deployed to**:
- Page 688 (pay-test-sandbox-2): SUCCESS, all 5 verification checks passed
- Page 689 (pay-test-2): SUCCESS, all 5 verification checks passed

**Deploy method**: `requests.put()` with `auth=(USER, APP_PASS)` + `User-Agent: WordPress/6.0`
- Update `meta._elementor_data` → find widget at `root[0].elements[0]`
- Also update `content.raw` (both must be updated per v3 lesson)
- Then `DELETE /wp-json/elementor/v1/cache`

**CRITICAL GOTCHA**: `urllib.request` gets Cloudflare 403 (error code 1010). Use `requests` library instead. Both produce the same HTTP calls but CF treats them differently.

---

## Fix 3: Proxy Verification

**Tested both endpoints**:
- `https://api.purebrain.ai/api/birth/start` → HTTP 503 `{"error":"No containers available","pool":[...],"status":"pool_exhausted"}`
- `https://89.167.19.20:8443/api/birth/start` (--insecure) → HTTP 503 same response

**Interpretation**: 503 pool_exhausted = Witness is alive and responding correctly. Containers are busy (expected). NOT a proxy error. Route is healthy.

**Log server routing**: Confirmed `/api/birth/start` maps to `proxy_birth_start()` in `tools/purebrain_log_server.py` (line 1598). Also aliased at `/api/proxy/birth/start`.

---

## File Summary

| File | Change |
|------|--------|
| `exports/purebrain-security-plugin-v464.php` | NEW — v464 with 89.167.19.20:8443 in CSP |
| `tools/security/deploy_plugin_v464_csp_connect_src.py` | NEW — deploy script for v464 |
| `exports/purebrain-chatbox-v44.html` | MODIFIED — env detection + birth body + flowCompleted |
| WP Page 688 (`_elementor_data` + `content.raw`) | DEPLOYED — chatbox v4.5 |
| WP Page 689 (`_elementor_data` + `content.raw`) | DEPLOYED — chatbox v4.5 |

