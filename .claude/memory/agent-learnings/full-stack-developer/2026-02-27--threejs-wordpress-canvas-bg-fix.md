# Three.js Canvas Background Fix for WordPress

**Date**: 2026-02-27
**Type**: teaching
**Topic**: Making Three.js fullscreen canvas backgrounds work inside WordPress/elementor_canvas pages

---

## The Problem

Three.js 3D canvas animations that work perfectly as standalone HTML files often fail silently inside WordPress. The canvas appends correctly but is invisible. Common causes:

1. **WordPress theme preloader** (`.theme-preloader`, `.loading-container`) sits at z-index 9999 blocking everything
2. **Theme body background rules** (14+ CSS rules) override `background: #0a0e1a` with white or other colors
3. **Dead importmap** — WordPress strips `<script type="importmap">` tags, breaking bare specifier imports like `import { ... } from 'three'`
4. **SiteGround Speed Optimizer / Rocket Loader** may defer script execution after DOM is already loaded, causing async IIFE to run before container exists

## The Fixes (all 4 required)

### Fix 1: WordPress Override CSS (put at top of style block, right after :root)
```css
.theme-preloader,
.theme-preloader *,
.loading-container,
.loading { display: none !important; opacity: 0 !important; visibility: hidden !important; z-index: -1 !important; }

body.starter-starter,
body.starter-starter.starter-starter,
body { background: #0a0e1a !important; background-image: none !important; background-color: #0a0e1a !important; }

body > div:not(#pb-canvas-container):not(#pb-vignette):not(#pb-loader):not(#pb-page):not(#pb-logo-bar) {
  background: transparent !important;
}
```

### Fix 2: !important on ALL canvas container CSS rules
```css
#pb-canvas-container {
  position: fixed !important;
  inset: 0 !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 0 !important;
  overflow: hidden !important;
  background: #0a0e1a !important;
  display: block !important;
}
```

### Fix 3: Script resilience — add at the TOP of the async IIFE
```javascript
(async function() {
  // Wait for DOM if not ready (SiteGround may defer)
  if (document.readyState === 'loading') {
    await new Promise(function(resolve) { document.addEventListener('DOMContentLoaded', resolve); });
  }

  // Kill preloaders immediately
  var preloaders = document.querySelectorAll('.theme-preloader, .loading-container, .loading');
  preloaders.forEach(function(el) { el.style.cssText = 'display:none!important;opacity:0!important;visibility:hidden!important;z-index:-1!important;'; });

  // Verify container
  var container = document.getElementById('pb-canvas-container');
  if (!container) { console.error('[PureBrain 3D] Container not found'); return; }

  // Force container styles inline (beats all theme CSS)
  container.style.cssText = 'position:fixed!important;top:0!important;left:0!important;width:100vw!important;height:100vh!important;z-index:0!important;overflow:hidden!important;display:block!important;background:#0a0e1a!important;';

  // NOW do the Three.js imports...
```

### Fix 4: Remove dead importmap
WordPress strips `<script type="importmap">` tags. Use dynamic `import()` directly (not bare specifiers). The file already used dynamic imports, so just remove the dead importmap block.

## Deployment Pattern

For full-page custom HTML pages:
1. Extract `<style>` block + font `<link>` tags + `<body>` content
2. Combine them: fonts + style + body content
3. Wrap in `<!-- wp:html -->...\n<!-- /wp:html -->`
4. Delete old page with `?force=true` first (avoids stale Elementor data)
5. POST new page with `"template": "elementor_canvas"`

**Page IDs shift on delete+recreate** — old ID 983 became new ID 987.

## File Location
- Source HTML: `/home/jared/projects/AI-CIV/aether/exports/purebrain-invite-only.html`
- WordPress page: `https://purebrain.ai/invitation/` (ID: 987)
