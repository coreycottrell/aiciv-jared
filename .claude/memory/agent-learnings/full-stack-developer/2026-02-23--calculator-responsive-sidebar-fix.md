# Calculator Responsive Sidebar Fix - Page 777
**Date**: 2026-02-23
**Type**: teaching
**Topic**: CSS responsive sidebar pattern for self-contained HTML pages on WordPress

## What Was Fixed
Page 777 (ai-tool-stack-calculator) had 3 issues:
1. Sidebar disappeared on mobile/tablet (display: none in 960px breakpoint)
2. Desktop sticky sidebar (was already there - position: sticky)
3. Missing PureBrain hexagon icon in nav logo

## Root Cause of Sidebar Bug
The original CSS had:
```css
@media (max-width: 960px) {
  .calc-bottom-bar { display: block; }
  .calc-sidebar { display: none; }  /* THE BUG */
  body { padding-bottom: 100px; }
}
```

The sidebar was intentionally hidden and replaced with a minimal "bottom bar" (fixed footer with just spend amount + CTA button). But Jared wants the FULL sidebar visible below categories.

## Fix Pattern
```css
@media (max-width: 960px) {
  /* Sidebar stacks BELOW categories - never hidden */
  .calc-sidebar {
    position: static; /* Remove sticky, flows normally */
    top: auto;
  }
  body { padding-bottom: 20px; }
}

/* Bottom bar hidden - full sidebar shown */
@media (max-width: 960px) {
  .calc-bottom-bar { display: none; }
}
```

The grid layout at 960px was already `grid-template-columns: 1fr` so sidebar stacks below automatically.

## Icon Embedding Pattern
PureBrain icon (2.9MB at 2100x2100) is too large for base64 inline. Solution:
```python
from PIL import Image
import base64, io
img = Image.open('purebrain-icon.png')
img_small = img.resize((28, 28), Image.LANCZOS)  # Small for nav
buf = io.BytesIO()
img_small.save(buf, format='PNG', optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
# Result: ~2500 chars (manageable inline)
```

Then in HTML:
```html
<img src="data:image/png;base64,{b64}" style="width:28px;height:28px;margin-right:8px;vertical-align:middle;flex-shrink:0;" />
```

## WordPress Deployment
- Page 777 uses single `<!-- wp:html -->` block for entire self-contained HTML
- Template: elementor_canvas
- Deploy via: `PUT /wp-json/wp/v2/pages/777` with full content wrapped in wp:html
- After deploy: `DELETE /wp-json/elementor/v1/cache`

## Magic Cursor Issue (Page 777 Specific)
The tt theme's `.tt-magic-cursor` class applies orange color globally. Override in the HTML file's CSS:
```css
body.page-id-777.tt-magic-cursor *:not(desired exceptions) {
  color: inherit;
}
```

## File Locations
- Source: `exports/ai-tool-stack-calculator-v3.html`
- Page: https://purebrain.ai/ai-tool-stack-calculator/
- WP Page ID: 777
