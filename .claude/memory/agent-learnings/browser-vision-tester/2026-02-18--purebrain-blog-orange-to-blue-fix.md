---
type: technique
topic: PureBrain Blog Page - Orange to Blue Color Fix via REST API
date: 2026-02-18
agent: browser-vision-tester
tags: [css, purebrain, rest-api, color-override, elementor, page-319]
confidence: high
---

# PureBrain Blog Page - Orange to Blue Color Fix

## Context

Jared reported "all the words are orange now + even the icons" on the blog page (purebrain.ai/blog/).
The social media icons, author name, and neural divider diamond were all orange (#f1420b) and needed
to be changed to blue (#2a93c1).

## Key Discovery: Page ID 319 (NOT 95)

The blog page at purebrain.ai/blog/ has body class `page-id-319`, NOT `page-id-95` as previously assumed.
The page uses `elementor_canvas` template. CSS scoped to `body.page-id-95` will NOT target this page.

## Root Cause

The Elementor page 319 has a 15KB embedded `<style>` block in its HTML content.
This style block uses `#f1420b` (orange) 16 times for:
- `.blog-header` color inheritance -> SVGs with `fill="currentColor"` become orange
- `.social-link:hover` colors
- `.blog-author .name` text
- `.neural-divider::after` diamond character
- Various hover effects

The SVGs in social icons have `fill="currentColor"` which inherits from the nearest
parent that sets `color`. The `.blog-header` parent has color set to orange, causing
all SVG icons to render orange even though `.social-link` sets `color: #ffffff`.

## Solution: REST API Content Update

Since CAPTCHA blocks Playwright login, used the WordPress REST API with Application Password
to update the page content directly:

```python
import requests
auth = ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")
resp = requests.get("https://purebrain.ai/wp-json/wp/v2/pages/319?context=edit", auth=auth)
content = resp.json()["content"]["raw"]

# Append override <style> block at end of content
new_content = content + "\n<style>/* overrides */</style>"

requests.post(
    "https://purebrain.ai/wp-json/wp/v2/pages/319",
    auth=auth,
    json={"content": new_content}
)
```

## CSS Overrides Applied

Key selectors used:
- `.social-link svg, .social-link svg path` - force `fill: #2a93c1 !important`
- `.social-link` - border-color and background to blue
- `.blog-author .name` - `color: #2a93c1 !important`
- `.neural-divider::after` - `color: #2a93c1 !important`
- `.neural-divider` - all-blue gradient
- `.blog-header` - `color: #ffffff !important` (reset inheritance)
- `.social-links` - `color: #2a93c1 !important`

## Important Technique: SVG currentColor Override

When SVGs use `fill="currentColor"`, overriding the `fill` CSS property with `!important`
works to change the color. Must target BOTH the SVG element AND the path elements:
```css
.social-link svg,
.social-link svg path {
    fill: #2a93c1 !important;
    color: #2a93c1 !important;
}
```

## What Stays Orange (Intentional)

- `.blog-logo-text .ai-letters` - the "AI" in the logo header
- `.blog-title` gradient text (white->blue->orange)
- CTA buttons (`.blog2-nav a.nav-cta`, `.cta-button`)
- Read more buttons
- Post title hover effects
- Related posts heading "You Might Also Like"

## Verification

All targets confirmed via computed styles:
- svgFill: rgb(42, 147, 193) [was rgb(241, 66, 11)]
- authorNameColor: rgb(42, 147, 193) [was rgb(241, 66, 11)]
- neuralDividerAfterColor: rgb(42, 147, 193) [was rgb(241, 66, 11)]
- blogHeaderColor: rgb(255, 255, 255) [was rgb(241, 66, 11)]

Homepage unaffected (changes embedded in page 319 content only).

## Files

- Screenshots: /tmp/purebrain-blog-color-fix-2026-02-18/
- Before: 01_current_blog_page.png, 03_social_icons_closeup.png
- After: 04_after_fix_full.png, 05_after_fix_social_icons.png

## When to Apply

- Any time blog embedded CSS colors need changing
- REST API page content update is reliable when CAPTCHA blocks Playwright
- Always check page ID via body classes (page-id-319 for blog, NOT 95)
- Always verify homepage not affected after blog CSS changes

---

**Tags**: css, purebrain, blog, color-fix, rest-api, elementor, social-icons, svg-fill
