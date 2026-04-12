# Calculator Page 777 - Nested HTML Fix Redeployed

**Date**: 2026-02-23
**Type**: teaching + operational
**Agent**: full-stack-developer
**Page**: https://purebrain.ai/ai-tool-stack-calculator/ (WP page 777)

---

## Problem

Page 777 was broken again - layout collapsed to single column, no grid, unstyled.

## Root Cause

The local file `exports/ai-tool-stack-calculator-v3.html` is a COMPLETE HTML document
(`<!DOCTYPE html><html><head>...<body>...</body></html>`).

Previous agent updates (adding new categories, pricing changes, etc.) were re-deploying
the LOCAL FILE AS-IS to WordPress, which re-introduced the nested HTML document problem.

When deployed as a full HTML doc inside `<!-- wp:html -->`, the browser sees:
1. WordPress outer `<html lang="en-US">`
2. Our inner `<html lang="en">` (gets ignored/mishandled by browser)

Result: CSS targeting `body` and `:root` behave inconsistently. Grid layout collapses.

## Fix

Strip the outer HTML wrapper before deploying to WordPress:

```python
import re

local_content = open('exports/ai-tool-stack-calculator-v3.html').read()

# Extract ONLY the style and body content
style_match = re.search(r'<style>(.*?)</style>', local_content, re.DOTALL)
body_match = re.search(r'<body>(.*?)</body>', local_content, re.DOTALL)

style_content = style_match.group(1)
body_content = body_match.group(1)

# Add WordPress dark theme override at TOP of style block
wp_override = """/* WORDPRESS DARK THEME OVERRIDE */
html, body, body.page, body.page-id-777 {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8edf3 !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
}
"""

# Build clean WordPress content
wp_content = f"""<!-- wp:html -->
<style>
{wp_override}
{style_content}
</style>
{body_content}
<!-- /wp:html -->"""

# Verify
assert '<!DOCTYPE' not in wp_content
assert '<html' not in wp_content
assert '<body>' not in wp_content
```

## Verification Checklist

After any deploy to page 777:
1. `<html>` count in rendered page = 1 (not 2)
2. `grid-template-columns: 1fr 360px` present in CSS
3. `background: #080a12 !important` present
4. JS `const CATEGORIES` present
5. `calc-layout` div in HTML body

## CRITICAL RULE

**NEVER deploy the local HTML file as-is to WordPress.**
**ALWAYS extract `<style>` and `<body>` content only.**

The local file (`ai-tool-stack-calculator-v3.html`) is the MASTER REFERENCE,
but WordPress must receive only the stripped body+style content.

## Files

- Master: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- WP Page: 777 (elementor_canvas template)
- Cleared: Elementor cache via DELETE /wp-json/elementor/v1/cache
