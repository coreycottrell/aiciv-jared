# WordPress Elementor Dark Theme CSS Override Pattern

**Date**: 2026-02-18
**Type**: teaching
**Topic**: Forcing dark background on WordPress Elementor canvas pages when theme overrides inline CSS

## Problem

When using Elementor HTML widgets with inline `<style>` blocks, the WordPress Artistics theme's `body { background-color: var(--e-global-color-black) }` and other theme CSS can override inline styles. Pages would render with wrong background colors even though the inline HTML had correct CSS.

## Root Cause

The Artistics theme + Elementor kit CSS (`post-10.css`) sets body background via CSS custom properties and normal CSS rules. Inline `<style>` blocks within Elementor HTML widgets have the same specificity - but if they're rendered inside `.elementor-section`, `.elementor-container` etc., those wrapper elements have the theme's background applied.

## Solution: Critical Override Block

Add this at the TOP of the `<style>` block (before `:root` variables), to force dark background on all WordPress wrapper elements:

```css
html, body, .site, .page, #page, #content, .entry-content, main, article,
.elementor, .elementor-section, .elementor-container, .elementor-column,
.elementor-widget-wrap, .elementor-element {
    background: #0a0a0a !important;
    background-color: #0a0a0a !important;
}
body {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #0a0a0a !important;
    color: rgba(255,255,255,0.95) !important;
    min-height: 100vh !important;
}
```

This is what the reference page (`/ai-partnership-assessment/`) does that the other pages were missing.

## Cache Busting

After updating `_elementor_data` via WP REST API:

1. POST to `/wp-json/wp/v2/pages/{id}` with `{"status": "publish"}` to trigger save
2. DELETE to `/wp-json/elementor/v1/cache` to clear Elementor's CSS cache (200 = success)
3. Wait 3-5 seconds then verify with curl

The correct Elementor cache clear endpoint is `DELETE /wp-json/elementor/v1/cache` (NOT POST, NOT `/flush-css`).

## API Pattern for Updating Elementor Pages

```python
import json, requests

auth = ("Aether", "APP_PASSWORD")

# 1. Fetch current data
r = requests.get(f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit", auth=auth)
d = r.json()
ed = d['meta']['_elementor_data']
parsed = json.loads(ed)

# 2. Update HTML widget (structure: [section][column][widget].settings.html)
parsed[0]['elements'][0]['elements'][0]['settings']['html'] = new_html

# 3. Push back
requests.post(f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}",
    auth=auth, json={"meta": {"_elementor_data": json.dumps(parsed, ensure_ascii=False)}})

# 4. Bust cache
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=auth)
```

## PureBrain Design System (Reference: /ai-partnership-assessment/)

Key design tokens:
- bg: `#0a0a0a`
- card: `rgba(20,20,26,0.95)`, `border-radius: 20px`, `backdrop-filter: blur(20px)`, `border: 1px solid rgba(255,255,255,0.1)`
- heading gradient: `linear-gradient(135deg, #f1420b, #2a93c1)` with `-webkit-background-clip: text`
- button: `linear-gradient(135deg, #f1420b, #d13a0a)`, white text, `border-radius: 10px`
- orbs: Fixed position, `filter: blur(130px)`, `opacity: 0.15-0.3`, animated with `orb-float` keyframes
- fonts: Oswald (headings, uppercase), Plus Jakarta Sans (body)

## Pages Modified

- Page 403 (AI Readiness Assessment): `/ai-readiness-assessment/`
- Page 405 (AI Partnership Guide): `/ai-partnership-guide/`

Both now pass all design checks: dark bg, glassmorphism cards, gradient headings, floating orbs, preserved functionality.
