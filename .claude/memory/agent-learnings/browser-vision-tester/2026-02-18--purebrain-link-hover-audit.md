---
type: technique
topic: purebrain.ai link and hover audit - findings and fix
date: 2026-02-18
agent: browser-vision-tester
tags: [css, purebrain, hover, audit, category-pages, magic-cursor, font-awesome]
confidence: high
---

# PureBrain Link & Hover Audit - Feb 18, 2026

## Summary

Comprehensive audit of all links on 3 pages. All links navigate correctly (200 OK, zero 404s). Issues are purely CSS/visual.

## Confirmed Issues

### 1. Post title links on category pages turn orange on hover

**Root cause**: `body.category a:hover, body.archive a:hover { color: #f1420b !important }`
in WordPress Additional CSS (`id="wp-custom-css"`) is TOO BROAD.
Catches ALL links including h2/h3 post title links.

Post titles (blue text on dark bg) should turn WHITE on hover, not orange.
Orange is readable on dark background, but it's not the intended UX.

**Fix**:
```css
body.category h2 a:hover, body.archive h2 a:hover,
body.category h3 a:hover, body.archive h3 a:hover,
body.category .post-title a:hover, body.archive .post-title a:hover,
body.category .entry-title a:hover, body.archive .entry-title a:hover {
    color: #ffffff !important;
}
```

### 2. Magic cursor visible

`.magic-cursor` element exists with `display: block; visibility: visible` on all pages.
Fix: `display: none !important`

### 3. Footer social icons - FALSE POSITIVE

Automated script flags footer social links as "blue on blue" contrast issue.
But the ICON (Font Awesome `<i>` element inside `<a>`) has `color: white`.
The `<a>` color property doesn't determine what user sees - the `<i>` color does.

**Rule**: When auditing icon links (`<a>` with `<i>` or `<svg>` inside), check the
INNER element's color, not the `<a>` element's color property.

Hover state: white icon on semi-transparent orange = READABLE (correct).

## CSS Source Structure on Category Pages

The category pages (`body.category`) use WordPress theme template (not Elementor Canvas).
CSS comes from the WordPress Customizer Additional CSS (`id="wp-custom-css"` style tag).
This is a 62KB style block on the page.

Key sections in the Additional CSS:
- "CATEGORY PAGE FIX (Feb 18)" - the broad `a:hover` rule that needs overriding
- "CATEGORY + HOVER FIX" - some post title overrides (partially working)
- The new override must come AFTER both sections to win the !important cascade

## Link Navigation Test Results

All links on all 3 pages return HTTP 200. No broken links.
- Nav links (Home, Blog, AI Assessment) - all work
- Post thumbnail image links - all work
- Post title text links - all work
- "Read More" links - all work
- Footer social icons - all work (LinkedIn, Twitter, Facebook, Instagram)
- Share buttons (javascript:void) - open social share popups (correct behavior)

## Deploy Method

Requires Playwright + CAPTCHA (WordPress Customizer login has GoDaddy security CAPTCHA).
Script: `/home/jared/projects/AI-CIV/aether/tools/deploy_link_hover_fix.py`
- Launches, gets CAPTCHA image
- Waits for answer file at `/tmp/linkfix_captcha_answer.txt`
- OR accepts answer as command line arg: `python3 deploy_link_hover_fix.py <answer>`

## Technique: Hover State CSS Inspection

```python
# Get computed color at hover state via coordinate-based element detection
page.mouse.move(x + width/2, y + height/2)
time.sleep(0.3)
hover_color = page.evaluate(f"""() => {{
    const el = document.elementFromPoint({x}, {y});
    const a = el.closest('a') || el;
    return window.getComputedStyle(a).color;
}}""")
```

## When to Apply

- Any time "links look broken" report comes in - first check if it's just hover color CSS
- Footer social icon "unreadable" complaints - check `<i>` color not `<a>` color
- Any broad CSS rule like `a:hover { color: X }` on body class - audit for over-application
