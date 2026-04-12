# Three.js Neural Network Not Rendering in WordPress — Root Cause + Fix

**Date**: 2026-02-27
**Type**: teaching
**Agent**: full-stack-developer
**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v463.php`

---

## The Bug

Three.js neural network background on `https://purebrain.ai/invitation/` was NOT rendering. The script was confirmed present in page source, `#pb-canvas-container` div was present, CSS was present. Worked as a local file. Failed on WordPress.

## Root Cause: CSP connect-src vs script-src distinction

**The critical distinction**:
- `<script src="...">` tag loading = governed by `script-src` CSP directive
- `await import('...')` (dynamic import) = governed by `connect-src` CSP directive

Our Three.js code used this pattern:
```js
(async function() {
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js');
  const { EffectComposer } = await import('https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/...');
  // ...
})()
```

The CSP had `https://cdn.jsdelivr.net` in `script-src` (allows `<script src>` tags) but NOT in `connect-src`. Dynamic imports use the fetch mechanism, governed by `connect-src`. Result: all `await import()` calls failed silently, Three.js never initialized.

## The Fix

Add `https://cdn.jsdelivr.net` to `connect-src` in the CSP security plugin.

**File changed**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v463.php`

**Plugin version**: v4.6.2 → v4.6.3

**Diff in connect-src**:
```
// BEFORE (v4.6.2):
. "connect-src 'self' ...https://*.wonderpush.com; "

// AFTER (v4.6.3):
. "connect-src 'self' ...https://*.wonderpush.com "
. "https://cdn.jsdelivr.net; "
```

## Deploy Pattern

1. Edit plugin PHP file in `exports/purebrain-security-plugin-v{N}.php`
2. Run deploy script with Playwright: `python3 tools/security/deploy_plugin_v463_csp_connect_src.py`
3. Touch the page via REST API to invalidate Cloudflare cache: `POST /wp-json/wp/v2/pages/{id}` with `status: publish`
4. Verify: `curl -sI https://purebrain.ai/invitation/ | grep content-security-policy`

## Diagnostic Method

```bash
# Check CSP headers
curl -sI https://purebrain.ai/invitation/ 2>&1 | grep content-security-policy

# Parse specific directives
curl -si https://purebrain.ai/invitation/ | python3 -c "
import sys
csp = sys.stdin.read()
for d in ['script-src', 'connect-src']:
    idx = csp.find(d)
    if idx >= 0:
        print(csp[idx:csp.find(';', idx)])
"
```

## Additional Context

- The importmap (`<script type="importmap">`) in the source file is stripped by WordPress from `<head>` when placed in `wp:html` body content - but it doesn't matter since our code uses full URLs in `await import()`, not bare specifiers.
- Cloudflare CDN caches the ENTIRE response including HTTP headers. To test new CSP: touch the page via REST API first, then add `?nocache=1` or wait for CF to re-validate.
- `cf-cache-status: MISS` = fresh from origin, `HIT` = cached (but cached copy now has new headers after plugin update propagated).

## Rule Going Forward

**When using `dynamic import()` from external CDN in WordPress:**
- The CDN domain must be in BOTH `script-src` AND `connect-src`
- `script-src` = for `<script src="...">` loading
- `connect-src` = for `import()`, `fetch()`, `XMLHttpRequest`, `WebSocket`

Plugin: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v463.php`
Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v463_csp_connect_src.py`
