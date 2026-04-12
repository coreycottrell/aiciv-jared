# PureBrain migrate page (ID 800) logo fix

**Date**: 2026-02-23
**Type**: operational + teaching
**Topic**: Fixed broken SVG logo on https://purebrain.ai/migrate/ - replaced generic SVG with proper PureBrain icon

---

## What Was Fixed

The logo section had a hand-crafted inline SVG (a generic blue hexagon with a white circle) instead of the actual PureBrain hexagon swirl icon.

**Before** (broken):
```html
<!-- Inline SVG hex orb logo -->
<svg class="logo-hex" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="orbGrad" cx="40%" cy="35%" r="65%">...
  </radialGradient>
  </defs>
  <polygon points="19,2 35,11 35,27 19,36 3,27 3,11" fill="url(#orbGrad)" .../>
  <polygon points="19,7 30,13.5 30,26.5 19,33 8,26.5 8,13.5" fill="none" .../>
  <circle cx="19" cy="19" r="5" fill="white" opacity="0.9"/>
</svg>
```

**After** (fixed):
```html
<!-- PureBrain icon (hexagon swirl) -->
<img class="logo-hex" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon.png" alt="PureBrain icon" style="width:38px;height:38px;object-fit:contain;"/>
```

The `.logo-hex` CSS class already sets `width: 38px; height: 38px;` so the img tag inherits sizing correctly. Added `object-fit: contain` inline for safety.

---

## Page 800 Structure

- **URL**: https://purebrain.ai/migrate/
- **WP ID**: 800
- **Template**: `elementor_canvas`
- **Elementor mode**: `builder`
- **Content**: Single HTML widget inside Elementor (like pages 577, 620, etc.)
- **HTML widget content size**: ~91.9KB

---

## Deployment Steps

1. GET `/wp-json/wp/v2/pages/800?context=edit` → extract `_elementor_data`
2. Parse elementor JSON → walk to HTML widget → update `settings.html`
3. Replace SVG with `<img>` tag pointing to WP uploaded icon
4. POST back to `/wp-json/wp/v2/pages/800` with updated `meta._elementor_data`
5. DELETE `/wp-json/elementor/v1/cache`

---

## Icon Asset URLs

- Local: `/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png`
- WordPress CDN: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon.png` (WP ID 591)
- WordPress thumbnail: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-300x300.png`

---

## Key Pattern

When a page has a hand-rolled SVG "approximation" of the PureBrain icon, always replace with the actual icon PNG from WordPress media library. The SVG was visually wrong - a simple flat hexagon with a white dot vs the distinctive blue/orange spiral swirl.

Logo text color split: `PUREBR` = blue (#2a93c1), `AI` = orange (#f1420b), `N` = blue (#2a93c1).
