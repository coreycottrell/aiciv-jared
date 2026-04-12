# Memory: Assessment Page Orange Background - Root Cause Found (3rd Attempt Fix)

**Date**: 2026-02-20
**Type**: teaching
**Topic**: Why page 577 still showed orange after 2 previous fix attempts

---

## Problem Summary

Page 577 (https://purebrain.ai/ai-adoption-review/) showed orange/wrong background after 2 previous fix attempts. The content (text, cards) was visible but background was wrong.

## Root Cause Discovered

**The previous "fix" broke things differently:**

My 2nd attempt "fixed" the page by stripping DOCTYPE/html/head/body wrappers from the Elementor HTML widget, keeping only `<style>`, `<script>`, and body content. This was WRONG.

Evidence from comparison with working pages:
- Page 403 (ai-readiness-assessment) WORKS and uses FULL HTML document (with `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`) inside the Elementor HTML widget
- My "fix" for page 577 used clean HTML without the document wrapper
- When CSS is in a `<style>` tag inside the body context (not in `<head>`), `body { background: ... }` rules may not reliably override the theme CSS

## The Actual Fix (3 Components)

### 1. Use FULL HTML document in Elementor widget (like page 403)
The content.raw had the correct full HTML. Put it directly into the Elementor HTML widget:
```python
elementor_data = [{
    "id": "a1b2c3d4",
    "elType": "section",
    "settings": {
        "background_background": "classic",
        "background_color": "#080a12"  # KEY: Set at Elementor section level
    },
    "isInner": False,
    "elements": [{
        "id": "e5f6g7h8",
        "elType": "column",
        "settings": {
            "_column_size": 100,
            "background_background": "classic",
            "background_color": "#080a12"  # KEY: Set at column level too
        },
        "elements": [{
            "id": "i9j0k1l2",
            "elType": "widget",
            "widgetType": "html",
            "settings": {"html": FULL_HTML_WITH_DOCTYPE},
            "elements": []
        }]
    }]
}]
```

### 2. Set background_color at Elementor section AND column level
This causes Elementor to generate CSS in `post-577.css`:
```css
.elementor-577 .elementor-element.elementor-element-a1b2c3d4:not(.elementor-motion-effects-element-type-background) {
    background-color: #080a12;
}
```
This CSS overrides any theme CSS for the container elements.

### 3. Add !important to body background in the HTML widget CSS
```css
html, body {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
body {
    background: var(--bg-deep) !important;
    background-color: var(--bg-deep) !important;
}
```

## The post-577.css Problem

After previous edits, Elementor's CSS file (`/wp-content/uploads/elementor/css/post-577.css`) was returning 404. This happened because Elementor hadn't regenerated the CSS after the _elementor_data change.

After the proper fix (with section/column background colors set in Elementor JSON), Elementor regenerated post-577.css with correct dark background CSS. It now returns 200.

**Why does post-577.css matter?** Elementor generates per-page CSS from the `_elementor_data` settings. If section/column have `background_color` settings, Elementor puts them in this CSS file which loads via `<link>` in `<head>`. This is the reliable, early-loading CSS.

## Key Takeaways

1. **ALWAYS use full HTML documents in Elementor HTML widget** - just like pages 403 and 284 do. The DOCTYPE/html/head/body structure ensures CSS in `<head>` applies reliably.

2. **Set `background_background: "classic"` AND `background_color` in section/column settings** - this causes Elementor to generate proper CSS in the per-page CSS file.

3. **Add !important to body/html background CSS** - belt and suspenders approach to ensure theme can't override.

4. **Verify post-577.css returns 200 after fix** - if still 404, Elementor hasn't regenerated. Clear Elementor cache.

5. **The content.raw IS the source of truth** - the full HTML document saved there is what should go in the widget.

## Wrong Lesson from Previous Memory

Previous memory said: "Always strip document wrapper from Elementor HTML widgets - Only put `<style>`, `<script>`, and body content in the widget."

**THIS WAS WRONG.** The correct pattern is: use FULL HTML document including DOCTYPE/html/head/body, exactly like pages 403 and 284 do.

## Verification Checks (All Passed)

- elementor-template-canvas class present
- Full HTML (DOCTYPE) in Elementor widget
- dark background #080a12 in CSS
- post-577.css returns 200 (not 404)
- Section background #080a12 in post-577.css
- assessment-wrapper present
- No Elementor error state
- No WP theme header (full canvas)
- body background !important override
- Brevo integration present
- Column CSS with dark background

## Reference

- Live URL: https://purebrain.ai/ai-adoption-review/
- WP Page ID: 577
- Fixed on: 2026-02-20
