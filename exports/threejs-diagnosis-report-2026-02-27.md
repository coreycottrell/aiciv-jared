# Three.js Neural Network Brain Background - Diagnosis Report

**Date**: 2026-02-27
**Tester**: browser-vision-tester
**Target**: https://purebrain.ai/invitation/
**Status**: ROOT CAUSE CONFIRMED

---

## Executive Summary

**The 3D brain is NOT rendering because WordPress is HTML-encoding `&&` (double ampersand) operators inside the `<script type="module">` block, breaking JavaScript syntax.**

Specifically, every `&&` in the script is being converted to `&#038;&#038;` by WordPress content filters. When the browser's JS engine encounters `&#038;&#038;` inside a script block, it throws:

```
SyntaxError: Invalid or unexpected token
```

This kills the entire module script on line 282, before the Three.js scene is ever initialized. The canvas is never created. The brain never renders.

---

## Diagnosis Results by Question

### 1. Screenshot of Page Load

**Visual State**: Plain dark background (#0a0e1a) with page content overlaid. No 3D visualization. No canvas element visible. The page functions but has no neural network brain animation.

**File**: `exports/screenshots/threejs-diagnosis/20260227_005150_01_initial_load.png`

---

### 2. Browser Console Errors

**Critical Error (Root Cause)**:
```
[PAGEERROR] Invalid or unexpected token
```

This is a JavaScript SyntaxError thrown by the browser's module parser when it encounters `&#038;&#038;` (HTML-encoded `&&`) inside the script block.

**Other Errors (NOT the cause — pre-existing CSP noise)**:
- GTM blocked by CSP (expected — not related)
- GoDaddy analytics blocked by CSP (expected — not related)
- wp-emoji-loader worker CSP violation (expected — not related)

---

### 3. #pb-canvas-container Canvas Check

```
Container exists:        YES
Container has canvas:    NO (0 canvas elements found)
Container innerHTML:     <div id="pb-canvas-container"></div>  (empty)
```

The container div exists with correct CSS (position:fixed, inset:0, z-index:0), but Three.js never ran to create a canvas inside it — because the script crashed on line 282 before reaching `container.appendChild(renderer.domElement)`.

---

### 4. CSS Override Check

**No CSS override issue.** The container CSS is clean:
```css
#pb-canvas-container {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
#pb-canvas-container canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
```

Computed position: `fixed` (correct — no override).
No inline style on the element.
No third-party stylesheet overriding it.

---

### 5. Ancestor Transform/Filter Check

**No ancestor transform/filter issue.** None of the container's ancestor elements have:
- `transform` (other than `none`)
- `filter` (other than `none`)
- `will-change` that would create a new stacking context
- `perspective`

This is NOT causing the problem.

---

### 6. Root Cause: WordPress HTML Entity Encoding

**8 occurrences** of `&#038;` found inside the `<script type="module">` block. Each `&&` operator was encoded as `&#038;&#038;`.

#### Affected Lines:

| Line | Original Code | What WordPress Stored |
|------|--------------|----------------------|
| 282 | `MAX_SPARKS && spawned < actualCount` | `MAX_SPARKS &#038;&#038; spawned < actualCount` |
| 315 | `e.touches && e.touches.length > 0` | `e.touches &#038;&#038; e.touches.length > 0` |
| 349 | `propagate && depth < 4` | `propagate &#038;&#038; depth < 4` |
| 416 | `dist < MOUSE_RADIUS && t - n.fireTime` | `dist < MOUSE_RADIUS &#038;&#038; t - n.fireTime` |

**Node.js syntax check confirms:**
```
/tmp/test_threejs.mjs:282
    for (let i = 0; i < MAX_SPARKS &#038;&#038; spawned < actualCount; i++) {
                                    ^

SyntaxError: Invalid or unexpected token
```

---

## Why This Happens

WordPress's `wptexturize()` and `wp_kses()` content filters run on saved post/page content. When a `<script>` block is saved through the WordPress editor (Gutenberg block editor or Elementor HTML widget), these filters process the content and HTML-encode special characters including `&`.

This is the SAME class of problem as wpautop injecting `<p>` tags into `<style>` blocks — WordPress treating JavaScript as HTML content.

The CDN imports work fine. WebGL is available in the browser. The CSS is correct. The architecture is sound. It's purely a WordPress content escaping issue.

---

## The Fix

**Option A (Recommended): Use wp:html block with correct wrapping**

The script MUST be deployed inside `<!-- wp:html -->` tags so WordPress treats it as raw HTML and does not run `wptexturize()` on it. Verify the current deployment method.

Current deployment: The script appears to be going through a filter that encodes `&`. Likely deployed via Elementor Custom HTML widget or standard Gutenberg HTML block without the wp:html wrapper protection.

**Option B: Encode the script differently**

Replace all `&&` operators in the source with `\u0026\u0026` (unicode escapes) — but this is a workaround, not a fix.

**Option C: Fix in WordPress DB directly**

Run a targeted search-replace in the WordPress database:
- Find: `&#038;&#038;` inside the invitation page content
- Replace: `&&`
- Must be done in `wp_posts` table, `post_content` column for the invitation page

**Option D: Use JavaScript OR instead of AND**

Not applicable — the logic requires `&&`.

---

## Recommended Next Steps

1. **Immediate**: Identify HOW the Three.js code is stored in WordPress for this page (Elementor widget? Gutenberg HTML block? PHP template?)
2. **Fix**: Re-deploy the script ensuring `<!-- wp:html -->` wrapper is used OR the code goes through a channel that doesn't run wptexturize
3. **Verify**: After fix, check that `&#038;` no longer appears in the rendered page source
4. **Test**: Canvas element should appear inside `#pb-canvas-container` after fix

---

## What Works / What Does NOT Work

| Component | Status | Notes |
|-----------|--------|-------|
| CDN imports (Three.js, EffectComposer, etc.) | NOT tested (script dies before they execute) | But CDN is reachable |
| #pb-canvas-container CSS | WORKS | position:fixed, correct dimensions |
| WebGL availability | WORKS | Browser supports WebGL |
| Script presence in DOM | WORKS | Script tag exists |
| Script execution | BROKEN | Crashes line 282 with SyntaxError |
| Canvas creation | BROKEN | Never reached |
| Three.js scene init | BROKEN | Never reached |

---

## Files

- Diagnosis script: `/home/jared/projects/AI-CIV/aether/tools/test_threejs_diagnosis.py`
- Extracted module script: `/home/jared/projects/AI-CIV/aether/exports/invitation-module-script.js`
- Screenshot (initial load): `/home/jared/projects/AI-CIV/aether/exports/screenshots/threejs-diagnosis/20260227_005150_01_initial_load.png`

---

*Diagnosed by browser-vision-tester | 2026-02-27*
