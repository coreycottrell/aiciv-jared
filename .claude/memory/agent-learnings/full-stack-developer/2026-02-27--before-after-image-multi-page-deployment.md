# Before/After Image Multi-Page Deployment

**Date**: 2026-02-27
**Type**: operational
**Topic**: Uploading and deploying proof image to portfolio, homepage, and pay-test pages

---

## What Was Done

Uploaded recolored Before/After PureBrain image and deployed it across 4 pages.

### Image Upload
- File: `exports/amplify-assets/proof-purebrain-colors.png`
- Uploaded via WordPress REST API POST to `/wp-json/wp/v2/media`
- Media ID: 1049
- Final URL: `https://purebrain.ai/wp-content/uploads/2026/02/before-after-purebrain-blue-orange-scaled.png`
  - Note: WordPress auto-appended `-scaled` to the filename
- Title set: "Before and After PureBrain - Blue Orange"

### Pages Updated

| Page | ID | Change |
|------|----|--------|
| Portfolio (/portfolio/) | 1006 | Replaced `portfolio-proof-scaled.jpg` with new image URL in existing `<img>` tag |
| Homepage (/) | 11 | Inserted full-width image div before `<!-- PRICING SECTION -->` comment |
| Pay-test-sandbox-2 | 688 | Inserted full-width image div before `<!-- SOCIAL PROOF COUNTER -->` comment |
| Pay-test-2 | 689 | Inserted full-width image div before `<!-- SOCIAL PROOF COUNTER -->` comment |

### Image HTML Block Used (Homepage + Pay-test)
```html
<div style="width:100%;max-width:1100px;margin:60px auto;text-align:center;padding:0 24px;box-sizing:border-box;">
  <img src="https://purebrain.ai/wp-content/uploads/2026/02/before-after-purebrain-blue-orange-scaled.png"
       alt="Before and After PureBrain AI - Transform your business operations"
       style="width:100%;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.4);display:block;">
</div>
```

---

## Key Patterns

### WordPress Scales Uploaded Images
When uploading via REST API, WordPress may auto-scale large images and append `-scaled` to filename.
Always use the `source_url` from the upload response, not the constructed filename.

### Homepage (page 11) is Elementor
- Template: `elementor_canvas`
- Content is rendered HTML inside Elementor widget
- Raw content updates work even when rendered content doesn't show changes
- Verify via `context=edit` raw content, not rendered

### Pay-test Pages Have Same Structure as Homepage
- Both 688 and 689 have same section comments: `<!-- SOCIAL PROOF COUNTER -->` before pricing
- This is a reliable insertion anchor

### Portfolio Page Uses Different Pattern
- Image is inside existing `<div class="pb-proof-img-wrap">`
- Simple URL replacement (not insertion) was the right approach

---

## Verification Command
```python
resp = requests.get(f'{base}/pages/{page_id}?context=edit', auth=auth)
raw = resp.json().get('content', {}).get('raw', '')
assert 'before-after-purebrain-blue-orange-scaled.png' in raw
```
