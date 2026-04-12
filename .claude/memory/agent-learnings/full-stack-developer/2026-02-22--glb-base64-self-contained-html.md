# GLB + HDR Base64 Self-Contained HTML

**Date**: 2026-02-22
**Type**: teaching
**Topic**: Embedding binary GLB and HDR assets into HTML as base64 data URIs for file:// protocol use

## Problem

Three.js GLTFLoader and RGBELoader use `fetch()` internally. `fetch()` fails on `file://` protocol due to CORS restrictions, even for local relative paths. This means any HTML file that loads `.glb` or `.hdr` files via relative paths CANNOT be opened by double-clicking in a browser.

## Solution Pattern

Embed all binary assets as base64 in a `<script>` (non-module) block that runs before the module code. Convert base64 to Blob Object URLs at load time. Pass Object URLs to the loaders instead of file paths.

### Key Implementation Steps

1. **Non-module script before the module script** - must expose data as `window` globals because ES modules cannot import from preceding inline scripts by variable reference alone.

2. **b64ToObjectURL helper**:
```javascript
function b64ToObjectURL(b64, mimeType) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  const blob = new Blob([bytes], { type: mimeType });
  return URL.createObjectURL(blob);
}
```

3. **Correct MIME types**:
   - GLB files: `model/gltf-binary`
   - RGBE/HDR files: `image/x-rgbe`

4. **Delete base64 strings after Blob creation** to free memory - the Blob holds a reference internally.

5. **Python build script** to do the embedding (files are too large for manual copy-paste):
```python
import base64
b64 = base64.b64encode(open('file.glb', 'rb').read()).decode('ascii')
```

## File Sizes (reference)
- glass-orb preview GLB: 684KB raw → 912KB base64
- glass-orb refined GLB: 1.7MB raw → 2.3MB base64
- poly_haven_studio_1k.hdr: 1.6MB raw → 2.2MB base64
- Total self-contained HTML: 5.22MB

## Files
- Source HTML: `docs/from-telegram/gleb-meshy-showcase-day2-fixed.html`
- Output: `exports/gleb-meshy-showcase-day2-selfcontained.html`
- GLB models: `exports/3d-models/glass-orb-*.glb`
- HDR: `exports/3d-assets/poly_haven_studio_1k.hdr`

## Gotchas
- The HDRI already had an error fallback to `RoomEnvironment` in the original file. Still worth embedding it so the full quality rendering works offline.
- Object URLs are valid for the lifetime of the document, no cleanup needed for single-page use.
- `atob()` is synchronous and can block briefly for large files (2MB base64 = ~1.5MB binary) - acceptable for a showcase file.
