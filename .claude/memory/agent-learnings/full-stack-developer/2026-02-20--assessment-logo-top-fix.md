# Assessment Page Logo/Branding Fix
**Date**: 2026-02-20
**Type**: operational + teaching
**Topic**: Fixed brand logo on purebrain.ai/ai-adoption-review/ (WP page 577)

## What Was Fixed

1. **Logo position**: Was `position: fixed; bottom: 0` (footer). Changed to `position: fixed; top: 0` (header).
2. **Logo colors**: Was using nth-child CSS selectors (wrong). Replaced with explicit color classes:
   - `pb-blue` (color: #2a93c1) for PUREBR and N
   - `pb-orange` (color: #f1420b) for AI
   - `pb-white` (color: #ffffff) for .ai
3. **PureBrain icon**: Added `<img class="brand-strip__icon">` with the hexagon swirl icon.
4. **Content offset**: Added `padding-top: 52px` to `.assessment-wrapper` so content clears the fixed header.

## How Page 577 Works

- **Template**: `elementor_canvas` (full-width, no theme chrome)
- **Rendering**: `_elementor_edit_mode: builder` = Elementor renders from `_elementor_data`
- **Structure**: Single section > column > HTML widget with full `<!DOCTYPE html>` page
- **Update method**: REST API POST to `/wp-json/wp/v2/pages/577` with `meta._elementor_data`

## Icon URL

- Local: `/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png`
- WordPress: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon.png` (WP ID 591, uploaded 2026-02-20)
- Also exists: `purebrain-hexagon-icon.jpg` (WP ID 518) - JPG version

## Brand Color Rules (Brand Bible)

| Text | Color | Class |
|------|-------|-------|
| PUREBR | #2a93c1 (blue) | pb-blue |
| AI | #f1420b (orange) | pb-orange |
| N | #2a93c1 (blue) | pb-blue |
| .ai | #ffffff (white on dark) | pb-white |

## Key Patterns

- Page 577 uses raw HTML in Elementor HTML widget (NOT Elementor components)
- Always validate JSON: `json.loads(new_elem_data)` before deploying
- After deploying _elementor_data, always clear: `DELETE /elementor/v1/cache`
- Header strip: 52px height, backdrop-filter blur, z-index 1000, border-bottom subtle

## Files

- Fixed HTML: `/tmp/assessment_html_fixed.html`
- Original backup: `/tmp/assessment_elem_data_original.json`
- Live URL: https://purebrain.ai/ai-adoption-review/
