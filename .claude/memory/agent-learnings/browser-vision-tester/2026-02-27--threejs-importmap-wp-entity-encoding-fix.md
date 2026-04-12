# Memory: Three.js Neural Network Background - WP Entity Encoding + ImportMap Fix

**Date**: 2026-02-27
**Type**: technique + gotcha + pattern
**Topic**: Two-bug diagnosis: WordPress &#038; encoding breaks JS && operators + Three.js importmap required for bare specifiers

---

## Task Summary

Diagnosed why the Three.js neural network brain background on purebrain.ai/invitation/ was not rendering. Found TWO separate bugs.

---

## Bug 1: WordPress Encodes `&&` to `&#038;&#038;` Inside Scripts

### Symptom
- Browser console: `Invalid or unexpected token` (PageError)
- `#pb-canvas-container` exists but empty - no canvas element

### Root Cause
WordPress's content rendering pipeline encodes `&&` operators to `&#038;&#038;` HTML entities, even when the JavaScript is inside a `<!-- wp:html -->` block. This makes `&&` invalid JavaScript syntax.

The browser treats `&#038;` as a literal ampersand entity inside `<script>` tags but does NOT decode it before JS execution in headless Chrome/Firefox. The `&#038;` becomes an invalid token in JavaScript.

### Which `&&` Get Encoded (Pattern)
Only SOME `&&` instances get encoded - specifically those preceded by `< VARIABLE_NAME` patterns where WordPress's tag detection parser sees the `<` as an HTML tag start and then applies entity encoding to nearby `&` characters.

- `i < MAX_SPARKS && spawned` → ENCODED (the `< MAX_SPARKS` looks like a tag to WP)
- `e.touches && e.touches.length` → ENCODED
- `propagate && depth < 4` → ENCODED
- `color.r > 0.6 && color.b` → NOT ENCODED (preceded by `>`)
- `f.index === i && f.time` → NOT ENCODED (preceded by `===`)

### Fix Applied
Replace the specific `&&` instances that get encoded with semantically equivalent JavaScript that doesn't use `&`:

```javascript
// Fix 1: for loop && condition → extract as break
// BEFORE (gets encoded):
for (let i = 0; i < MAX_SPARKS && spawned < actualCount; i++) {

// AFTER:
for (let i = 0; i < MAX_SPARKS; i++) {
  if (spawned >= actualCount) break;

// Fix 2: if (a && b) → ternary
// BEFORE:
if (e.touches && e.touches.length > 0) ...

// AFTER:
if (e.touches ? e.touches.length > 0 : false) ...

// Fix 3: Similar ternary for other && patterns
if (propagate ? depth < 4 : false) ...
if (dist < MOUSE_RADIUS ? t - n.fireTime > FIRE_DURATION : false) ...
```

### Verification Method
Node.js parse test:
```bash
node --input-type=module < /path/to/script.js
```
This immediately shows `SyntaxError: Invalid or unexpected token` with the exact line number of the encoded `&#038;`.

---

## Bug 2: Three.js jsDelivr Post-Processing Modules Use Bare Specifiers

### Symptom
After fixing Bug 1:
- Canvas STILL not created
- Console: `[PureBrain 3D] Failed to load: TypeError: Failed to resolve module specifier "three"`

### Root Cause
The Three.js post-processing modules on jsDelivr (`EffectComposer.js`, `RenderPass.js`, `UnrealBloomPass.js`, `OutputPass.js`) internally import from `'three'` using a **bare specifier**:

```javascript
// Inside EffectComposer.js on jsDelivr:
import { Clock, HalfFloatType, ... } from 'three';
```

Browsers cannot resolve bare specifiers like `'three'` without an **importmap**. This fails even when your own script uses full CDN URLs - the sub-imports inside EffectComposer fail.

### Fix Applied
Add a `<script type="importmap">` BEFORE the Three.js script to resolve the bare `"three"` specifier:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
  }
}
</script>
```

This importmap works with both `<script type="module">` and `await import()` in classic scripts.

### Alternative Fix (Not Used)
Use `esm.sh` CDN which rewrites imports to use full URLs:
```
https://esm.sh/three@0.161.0/examples/jsm/postprocessing/EffectComposer
```
BUT: This requires adding `esm.sh` to the WordPress CSP `script-src` header, which is more invasive.

---

## WordPress REST API Deployment Notes

- Page ID: 979 (original) → regenerated to 983 after our update
- Auth: `Aether:FlFr2VOtlHiHaJWjzW96OHUJ` (administrator role)
- Content update via `curl -X POST` with `--data-binary @payload.json` (Python `requests` auth broke, curl worked)
- Page may regenerate with new ID when content changes; check slug to find new ID

### WP Auth Gotcha
Python `requests.post(..., auth=(user, pass))` returned 401 even with correct credentials. Using `curl -u user:pass` worked. Always verify auth with curl first.

---

## Diagnosis Script Patterns

### Check for encoded && in live page
```bash
curl -s https://site.com/page/ | grep -n '&#038;'
```

### Node.js syntax check for module scripts
```bash
python3 -c "
from playwright.async_api import async_playwright
...
# Get script.textContent, write to file
"
node --input-type=module < /tmp/script.js
```

### Check if EffectComposer CDN uses bare specifiers
```bash
curl -s https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/EffectComposer.js | head -20
```

---

## Result

Both bugs fixed. Canvas renders at 1440x900. Three.js neural network animation shows blue particle nodes and connections on dark background. Console shows `[PureBrain Neural 3D] Invite landing — initialized`.

---

## Files

- Diagnosis script: `tools/test_threejs_diagnosis.py`
- Screenshots: `exports/screenshots/threejs-debug-2026-02-27/`
- Fixed content deployed to WP page 983
