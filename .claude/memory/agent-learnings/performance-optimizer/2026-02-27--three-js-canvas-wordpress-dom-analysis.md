# Three.js Canvas WordPress DOM Analysis

**Date**: 2026-02-27
**Topic**: WebGL Canvas Not Rendering on purebrain.ai/invitation/ (WordPress)
**Type**: Technical Debugging
**Confidence**: High (DOM verified), Low (root cause requires browser inspection)

---

## Summary

Analyzed the live purebrain.ai/invitation/ page to identify why the Three.js canvas renders locally but NOT on WordPress.

**Result**: DOM structure is CORRECT. No CSS properties breaking position:fixed detected. Root cause is likely JavaScript-related (canvas not created, WebGL context failure, or script timing issue).

---

## DOM Structure Analysis

### Current Nesting (Verified)

```
<body class="wp-singular page-template elementor_canvas page-id-979 tt-magic-cursor demo-1 ...">
  ├─ <div class="theme-preloader">  ← Artistics theme
  │  └─ <div class="loading-container">
  │     ├─ <div class="loading"></div>
  │     └─ <div id="loading-icon">...</div>
  │  </div>
  │
  ├─ <div id="magic-cursor">        ← Artistics theme
  │  └─ <div id="ball"></div>
  │
  ├─ <div id="pb-loader">            ← Our code: position: fixed; inset: 0; z-index: 999
  │
  ├─ <div id="pb-canvas-container">  ← CANVAS TARGET: position: fixed; inset: 0; z-index: 0
  │
  ├─ <div id="pb-vignette">          ← Vignette overlay: position: fixed; z-index: 1
  │
  ├─ <nav id="pb-logo-bar">          ← Header (no explicit position)
  │
  └─ <div id="pb-page">              ← Content: position: relative; z-index: 2
```

### CSS Properties Analysis (All Checked)

Properties that break `position: fixed` (all NEGATIVE):
- ✓ `overflow`: NOT on theme-preloader, magic-cursor, or ancestors
- ✓ `transform`: NOT on wrappers (would create new stacking context)
- ✓ `filter`: NOT on wrappers
- ✓ `contain`: NOT present
- ✓ `will-change`: NOT present
- ✓ `clip-path`: NOT present

**Verdict**: Theme wrapper divs do NOT break position:fixed.

### Z-Index Stack (Correct)

```
z-index: 0   - #pb-canvas-container (THREE.JS CANVAS)
z-index: 1   - #pb-vignette (overlay on canvas)
z-index: 2   - #pb-page (content scrolls over)
z-index: 999 - #pb-loader (loading screen)
```

This is correct layering. Canvas should render behind vignette, which should be behind page content.

---

## Root Cause: Likely JavaScript, Not DOM

The DOM analysis shows **no blocking CSS properties**. The problem is almost certainly:

1. **Canvas element not created** - The `#pb-canvas-container` div exists, but the `<canvas>` child element may not be inserted by JavaScript
2. **Three.js script fails to load** - WordPress script dependencies/GTM delays may prevent Three.js execution
3. **WebGL context creation fails** - Check browser console for "WebGL not supported" or similar
4. **Canvas size = 0x0** - Computed width/height might be wrong
5. **Script timing** - Theme preloader or GTM scripts running before Three.js code initializes

---

## Browser Inspection Commands

To debug live, run in console on https://purebrain.ai/invitation/:

```javascript
// Check container and children
const container = document.getElementById('pb-canvas-container');
console.log('Container found:', !!container);
console.log('Canvas child:', container.children.length > 0 ? container.children[0].tagName : 'NONE');

// Check computed styles
const cs = window.getComputedStyle(container);
console.log('Computed position:', cs.position);
console.log('Computed size:', cs.width, 'x', cs.height);
console.log('Computed z-index:', cs.zIndex);

// Check for script errors
console.log('Errors in console above? ↑ Look for THREE or WebGL errors');

// Check parent context
const parent = container.parentElement;
const pcs = window.getComputedStyle(parent);
console.log('Parent creates stacking context (transform/filter):',
  pcs.transform !== 'none' || pcs.filter !== 'none');
```

---

## Local vs. WordPress Differences

**Why it works locally**:
- Plain HTML + CSS + JS
- No theme divs (no theme-preloader, no magic-cursor)
- No GTM script delays
- No Elementor interference

**Why it might fail on WordPress**:
- Artistics theme adds pre-render divs
- Google Tag Manager loads scripts asynchronously
- WordPress enqueues scripts in specific order
- Elementor canvas template may modify DOM after load
- Theme JavaScript (magic cursor) might run before Three.js

---

## Next Steps (For Full-Stack Developer or Browser Testing)

1. **Open browser DevTools** on purebrain.ai/invitation/
2. **Check Console tab** - any JavaScript errors? WebGL warnings?
3. **Check Elements tab** - is the `<canvas>` element present inside #pb-canvas-container?
4. **Inspect #pb-canvas-container** - Computed styles tab shows position: fixed applied?
5. **Profile Network tab** - Is Three.js script loading? When does it load?
6. **Run console commands** above to get diagnostic data

---

## Performance Implications

- **Does NOT affect page load time** - Three.js canvas is background render, not critical path
- **If canvas missing, UX degrades** - No visual interest, just text on dark background
- **No performance regression** - DOM structure is lean, z-index stack is logical

---

## Files & References

- Page: https://purebrain.ai/invitation/ (Page ID: 979)
- Page template: elementor_canvas
- Theme: Artistics
- Canvas CSS: Inlined in `<style>` tag, ~line 2599-2610
- Scripts: Includes GTM, Google Tag Manager, theme JS, and custom Three.js init code

---

## Key Findings Summary

| Finding | Status |
|---------|--------|
| DOM nesting correct? | ✓ YES |
| CSS breaking position:fixed? | ✓ NO |
| Z-index stack logical? | ✓ YES |
| Root cause identified? | ✗ NO (need browser inspection) |
| Fix recommendation | Run console diagnostics, check for JS errors |

---

## Related Issues

- Blog styling conflicts (CSS cascade)
- WordPress plugin interference (GTM, analytics)
- Elementor canvas template effects on custom HTML
- Theme preloader blocking early scripts

---

**Next Session**: If root cause still unclear, invoke `browser-vision-tester` to visually inspect the page and check console logs.
