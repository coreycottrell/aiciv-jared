# Memory: Assessment Page Orange Fix - Elementor HTML Widget Pattern

**Date**: 2026-02-20
**Type**: teaching
**Topic**: Fixing "all orange" WordPress pages created via REST API without valid _elementor_data

---

## The Problem

Page 577 (ai-adoption-review, https://purebrain.ai/ai-adoption-review/) showed "all orange" fallback theme after being created via REST API.

Root cause:
- Page created with `template: "elementor_canvas"` (full-width)
- Content put in `content.raw` as standalone HTML
- `_elementor_edit_mode` meta key existed (even empty string)
- `_elementor_data` was empty/0 length
- Elementor saw `elementor_canvas` + empty `_elementor_data` → showed orange fallback/error state

## Why Orange?

Elementor's orange color is its fallback/error state, NOT a WordPress theme issue. When:
1. Page uses `elementor_canvas` template
2. Elementor checks for `_elementor_data` to render
3. `_elementor_data` is empty/invalid JSON
4. Elementor renders its error/fallback state which is orange

## The Fix (Confirmed Working)

The correct pattern for pages with custom HTML on `elementor_canvas`:

```python
# Build Elementor data with HTML widget containing your full HTML
elementor_data = [
    {
        "id": "a1b2c3d4",
        "elType": "section",
        "settings": {},
        "isInner": False,
        "elements": [
            {
                "id": "e5f6g7h8",
                "elType": "column",
                "settings": {"_column_size": 100},
                "elements": [
                    {
                        "id": "i9j0k1l2",
                        "elType": "widget",
                        "widgetType": "html",
                        "settings": {
                            "html": your_full_html_content  # Can include DOCTYPE/html/head/body
                        },
                        "elements": []
                    }
                ]
            }
        ]
    }
]

elem_data_str = json.dumps(elementor_data, ensure_ascii=False)

# VALIDATE before deploying
json.loads(elem_data_str)  # Must not raise

# Deploy
payload = {
    "template": "elementor_canvas",
    "content": original_html,  # Keep in content.raw as backup
    "meta": {
        "_elementor_edit_mode": "builder",
        "_elementor_template_type": "wp-page",
        "_elementor_data": elem_data_str,
    }
}
```

## What the Elementor HTML Widget Does

- Elementor's HTML widget (`widgetType: "html"`) takes raw HTML in `settings.html`
- Elementor renders it directly without wpautop or other WP filters
- The HTML can be a full document with DOCTYPE/html/head/body - Elementor handles extraction
- This is how pages 403 (ai-readiness-assessment) and 284 (ai-partnership-assessment) work

## Other Patterns Tried (Did Not Fully Solve)

1. **Remove elementor_canvas + wp:html block**: Fixes content.raw rendering but shows WP theme header/footer (no full-width). Good for policy pages, NOT for full-screen experiences.

2. **Add !important dark theme CSS override**: Still useful as extra protection but doesn't fix the root cause (empty _elementor_data).

## Verification Checks for elementor_canvas Pages

```python
# After fixing, fetch live page and verify:
checks = [
    'elementor-template-canvas in body classes',  # NOT 'elementor-canvas', it's 'elementor-template-canvas'
    'No id="masthead" (no WP theme header)',
    'No id="colophon" (no WP theme footer)',
    'assessment-wrapper present (content rendered)',
    '#0a0a0a in CSS (dark theme)',
    'No <p><div (no wpautop mangling)',
]
```

Note: "elementor-canvas" string check fails - actual body class is "elementor-template-canvas". Don't be confused.

## Pages That Use This Pattern

- Page 403 (`ai-readiness-assessment`): section > column > HTML widget
- Page 284 (`ai-partnership-assessment`): section > column > HTML widget
- Page 577 (`ai-adoption-review`): now fixed with this pattern

## Reference Files

- Working fix: built inline via Python, not saved to separate file
- Assessment HTML source: `/home/jared/projects/AI-CIV/aether/to-jared/ai-adoption-assessment-deployed.html`
- Live URL: https://purebrain.ai/ai-adoption-review/
- WP Page ID: 577
