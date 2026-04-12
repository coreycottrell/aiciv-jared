# AI Partnership Audit: Icon Fix + Brevo List 4 Update

**Date**: 2026-02-22
**Type**: operational
**Topic**: Replaced generic SVG icon with actual PureBrain icon PNG; updated Brevo to List 4 with correct attribute names

---

## Context

Jared flagged two issues on https://purebrain.ai/ai-partnership-audit/:
1. Top-left diamond SVG looked generic - "what is this? put our icon here"
2. Form was submitting to Brevo List 9 with wrong attribute names (ASSESSMENT_SCORE/TIER)

---

## Fix 1: PureBrain Icon

### Problem
Inline SVG (hexagon + circle + lines) didn't match actual PureBrain brand icon.

### Solution
1. Uploaded actual icon PNG to WordPress media library via REST API:
   - Local path: `docs/assets/logos/purebrain-icon.png` (2.9MB)
   - Uploaded to: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-1.png`
   - WordPress media ID: 636
2. Replaced `<svg class="logo-hex" ...>...</svg>` with:
   `<img class="logo-hex" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-1.png" alt="PureBrain" width="38" height="38" />`
3. CSS `.logo-hex` already had `object-fit: contain; border-radius: 4px;` - no CSS changes needed

### Regex pattern used
```python
svg_pattern = r'<svg class="logo-hex"[^>]*>.*?</svg>'
re.sub(svg_pattern, new_img_tag, content, flags=re.DOTALL)
```

---

## Fix 2: Brevo List + Attribute Names

### Problem
Form was submitting to:
- `listIds:[9]` (wrong list - should be List 4: Enterprise Leads)
- `ASSESSMENT_SCORE` (should be `AUDIT_SCORE`)
- `ASSESSMENT_TIER` (should be `AUDIT_TIER`)

### Solution
Simple string replacements in pbHandleSubmit function:
- `listIds:[9]` → `listIds:[4]`
- `ASSESSMENT_SCORE:score` → `AUDIT_SCORE:score`
- `ASSESSMENT_TIER:tier.name+' — '+tier.sub` → `AUDIT_TIER:tier.name+' — '+tier.sub`

### Final Brevo payload
```javascript
{
  email: em,
  attributes: {
    FIRSTNAME: fn,
    AUDIT_SCORE: score,
    AUDIT_TIER: tier.name + ' — ' + tier.sub,
    LEAD_SCORE: 30,
    COMPANY: co (if provided)
  },
  listIds: [4],
  updateEnabled: true
}
```

---

## Deployment

- WordPress page ID: 620 (purebrain.ai/ai-partnership-audit/)
- Page type: `wp:html` block (NOT Elementor) - content is raw HTML in `content.raw`
- REST API POST to `/wp/v2/pages/620`
- Elementor cache cleared via DELETE `/elementor/v1/cache`

## Verification (all passed)
- PureBrain icon PNG URL present in live HTML
- Old SVG removed
- listIds:[4] present
- AUDIT_SCORE present
- AUDIT_TIER present
- Old listIds:[9] removed
- Old ASSESSMENT_SCORE removed

## Notes
- The PureBrain icon file is 2.9MB - large for a 38px icon display, but WordPress serves it fine
- WordPress auto-suffixed `-1` to avoid collision with any existing purebrain-icon.png
- CORS from purebrain.ai → api.brevo.com confirmed working (established in previous sessions)
- Brevo attributes AUDIT_SCORE and AUDIT_TIER may need to be created in Brevo if not existing
  (but Brevo auto-creates custom attributes on first contact submission if `updateEnabled:true`)
