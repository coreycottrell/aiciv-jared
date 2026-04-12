# Calculator Page 777 - 3 Layout Fixes Deployed

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Black gap fix, sidebar sticky fix, mobile bottom bar fix - all verified deployed

## What Was Done

Three layout fixes for `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html` were already present in the local file (applied in a previous session). This session deployed those fixes to WordPress page 777 and verified them.

## The 3 Fixes

### Fix 1: Black gap between categories and "Full Market Breakdown"
- **Cause**: `grid-row: 1 / span 99` was creating 99 explicit grid rows in a 2-row grid
- **Fix**: Changed to `grid-row: 1 / -1` (spans to last ACTUAL row, not 99 fake rows)
- **Also**: `.calc-grand-section` uses `margin-top: 40px; padding-top: 40px` (reduced from 60px)
- **Note**: `.calc-grand-section` is OUTSIDE `.calc-layout` div - confirmed structure is correct

### Fix 2: Mobile/tablet sidebar (bottom bar)
- **Cause**: Bottom bar (`calc-bottom-bar`) was explicitly `display: none`
- **Fix**: At `max-width: 960px`, sidebar gets `display: none` and bottom bar gets `display: flex !important`
- **Body** gets `padding-bottom: 80px` to accommodate fixed bottom bar
- **Bottom bar** is a compact fixed footer with current spend amount + CTA

### Fix 3: Desktop sidebar sticky
- **CSS**: `position: sticky`, `top: calc(var(--sticky-height) + 16px)`, `align-self: start`
- **Added**: `max-height: calc(100vh - var(--sticky-height) - 32px)` + `overflow-y: auto`
- This ensures sidebar doesn't overflow viewport on short screens

## Deployment Pattern (CRITICAL - page 777)

**NEVER deploy the full HTML file as-is.** WordPress creates nested `<html>` document if you do.

Must extract ONLY style + body content:
```python
import re, base64, requests

content = open('exports/ai-tool-stack-calculator-v3.html').read()
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)

wp_override = """/* WORDPRESS DARK THEME OVERRIDE */
html, body, body.page, body.page-id-777 {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8edf3 !important;
}
"""

wp_content = f"""<!-- wp:html -->
<style>
{wp_override}
{style_match.group(1)}
</style>
{body_match.group(1)}
<!-- /wp:html -->"""

# Verify
assert '<!DOCTYPE' not in wp_content
assert '<html' not in wp_content

creds = base64.b64encode(f"Aether:{WP_PASS}".encode()).decode()
requests.put(
    "https://purebrain.ai/wp-json/wp/v2/pages/777",
    headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json",
             "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
    json={"content": wp_content, "template": "elementor_canvas"}
)

# Always clear Elementor cache after
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache",
    headers={"Authorization": f"Basic {creds}"})
```

## Verification Results

All checks passed:
- grid-row: 1 / -1 present (no span 99)
- align-self: start on sidebar
- max-height + overflow-y: auto on sidebar
- display: flex !important on bottom bar (mobile)
- padding-bottom: 80px on body (mobile)
- margin-top: 40px on grand section
- 0 `<p>` tags injected into style (no wpautop damage)
- 1 `<html>` tag on live page (no nesting)
- HTTP 200 on live page

## Files
- Source: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- WP Page: 777
- URL: https://purebrain.ai/ai-tool-stack-calculator/
