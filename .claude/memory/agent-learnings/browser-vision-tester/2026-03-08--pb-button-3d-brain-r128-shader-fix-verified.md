# Memory: index-3d Three.js r128 + nodeColor Shader Fix Verification

**Date**: 2026-03-08
**Type**: technique + pattern
**Topic**: Verified r160→r128 CDN downgrade + attribute rename fix for purebrain-site index-3d page

---

## Task Summary

QA audit of https://purebrain-site.vercel.app/index-3d after two bug fixes:
1. Three.js CDN changed from r160 (deprecated non-module global build) to r128 (last proper global build on cdnjs)
2. Shader attribute renamed from `vec3 color` (WebGL reserved name conflict) to `vec3 nodeColor`

---

## Verification Results

### THREE.js Load
- THREE.REVISION = "128" (correct, r128 confirmed loaded)
- `window.THREE` defined = true
- `canvas-bg` element found in DOM

### WebGL Status
- Context: WebGL 2.0 / OpenGL ES 3.0 (Chromium SwiftShader headless)
- GLSL version: WebGL GLSL ES 3.00
- Center pixel: R=0, G=0, B=0, A=255 → NOT blank (alpha=255 means rendered content, pure transparent would be A=0)
- No shader compilation errors in console

### Console Errors
- JS errors: 0
- Page errors: 0
- WebGL performance warnings: 4 (GPU stall ReadPixels — headless Chromium artifact, NOT a real error)
- No shader/attribute/THREE errors whatsoever

### Visual State (Screenshots)
- Hero section: 3D brain renders visibly — icosahedral low-poly mesh with blue tones, particle connections visible, dark background
- Scrolled 1000px: Content sections fully visible, horizontal scroll ticker for specialist agents (MEDIA MANAGEMENT, RESEARCH & ANALYSIS, etc.), "An AI That Becomes Yours" section with 3-column feature cards
- Scrolled 2500px: Chat demo section visible, "Three Layers. Each Impossible Without The One Below." heading visible — no blank/black sections

### Canvas Info
- ID: canvas-bg
- Width: 1440, Height: 900 (matches viewport)
- offsetWidth/offsetHeight: 1440x900
- Note: `visible: False` from Playwright's `offsetParent` check — this is because canvas is position:fixed/absolute bg, not because it's hidden. Visual confirms it renders.

---

## Key Patterns

### r128 vs r160 on cdnjs
- r128 = last Three.js build that ships a proper global (`window.THREE`) UMD build on cdnjs
- r160 = ships only ES module builds, no global — breaks any script that does `new THREE.Scene()`
- cdnjs URL pattern: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`

### Shader Reserved Name Conflict
- WebGL GLSL reserves `color` as a built-in varying in some implementations
- Renaming `attribute vec3 color` → `attribute vec3 nodeColor` avoids silent shader compilation failure
- Evidence: zero shader errors after rename

### Headless WebGL "ReadPixels GPU stall" warnings
- These are normal in headless Chromium with SwiftShader
- NOT a sign of rendering failure
- Appear whenever any code does gl.readPixels() (including THREE internals for picking/debug)

---

## Files
- Screenshots: /tmp/brain-audit/ (01-hero-state.png, 02-scrolled-1000.png, 03-scrolled-2500.png)
- Source: /home/jared/projects/AI-CIV/aether/purebrain-site/public/index-3d.html
