# Memory: PureBrain vs GlobalGPT (GLBGPT) Comparison Page

**Date**: 2026-03-02
**Type**: operational
**Topic**: Built and deployed honest comparison page for PureBrain vs GlobalGPT (GLBGPT)

---

## What Was Built

Self-contained HTML comparison page for PureBrain vs GlobalGPT (GLBGPT), an AI model aggregator.

**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-vs-glbgpt.html`

---

## WordPress Deployment

- **Site**: purebrain.ai
- **Page ID**: 1190
- **Slug**: `purebrain-vs-glbgpt`
- **URL**: https://purebrain.ai/purebrain-vs-glbgpt/
- **Template**: `elementor_canvas`
- **Status**: publish
- **Content size**: 38,733 chars

---

## What GlobalGPT (GLBGPT) Is

AI model aggregator — one subscription gives access to 100+ AI tools (GPT, Claude, Gemini, image gen, video). Entry-level pricing from ~$5.80/mo. Trustpilot 3.4 stars. Useful for individuals exploring AI. NOT a business partner — no memory, no persistent context, just access.

---

## Compare Hub Update (Page 752)

Two places updated in page 752 (/compare/):

### HTML Tile Added (after SiteGPT tile)
```html
<div class="tool-tile" style="--tile-color: #4A7C8E" onclick="openPanel('glbgpt')">
  <div class="tile-has-page"><span>Deep dive</span></div>
  <div class="tile-icon">🌐</div>
  <div class="tile-name">GlobalGPT (GLBGPT)</div>
  <div class="tile-tagline">100+ models vs. your AI partner</div>
  <div class="tile-cta-hint">Click to see full comparison →</div>
</div>
```

### JS TOOLS Entry Added (after sitegpt entry)
```js
glbgpt: {
  icon: '🌐', name: 'GlobalGPT (GLBGPT)', color: '#4A7C8E',
  good: { ... },
  gap: { ... },
  diff: { ... },
  deepDive: '/purebrain-vs-glbgpt/'
}
```

---

## GLBGPT Brand Color

`#4A7C8E` — muted teal. Distinct from SiteGPT (#00B4D8). Not exact brand color (trademark safety).

---

## Compare Page Content Size History

| Event | Length |
|-------|--------|
| Before this task | 65,041 |
| After GLBGPT add | 66,424 |
| Delta | +1,383 chars |

---

## Tool Colors Reference (Updated)

| Tool | Color |
|------|-------|
| SiteGPT | #00B4D8 |
| **GlobalGPT (GLBGPT)** | **#4A7C8E** |
| ChatGPT | #10a37f |
| Copilot | #0078D4 |

---

## Verification Checklist

- [x] File saved to exports/purebrain-vs-glbgpt.html
- [x] Status: publish
- [x] Template: elementor_canvas
- [x] Page ID: 1190
- [x] Content starts with `<!-- wp:html -->`
- [x] Content ends with `<!-- /wp:html -->`
- [x] Compare hub tile added (openPanel count: 1)
- [x] Compare hub JS deepDive entry added
- [x] Compare hub content: 65,041 → 66,424
- [x] Elementor cache cleared (empty response = success)
- [x] Live at https://purebrain.ai/purebrain-vs-glbgpt/
