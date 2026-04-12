---
type: technique
topic: PureBrain Blog Loader CSS Fix - Awaiken Theme
date: 2026-02-17
agent: browser-vision-tester
tags: [css, preloader, purebrain, awaiken-theme, branding]
confidence: high
---

# PureBrain Blog Loader CSS Fix

## Context

The purebrain.ai/blog page shows a loading animation with GREEN/LIME colored arcs that don't match the brand colors (ORANGE #f1420b, BLUE #2a93c1).

## Discovery

The Awaiken WordPress theme uses this preloader HTML structure:
```html
<div class="theme-preloader">
    <div class="loading-container">
        <div class="loading"></div>
        <div id="loading-icon"><img src="..."></div>
    </div>
</div>
```

The `.loading` div is a CSS-only spinner using `border-color` to create the arc animation. The default green color comes from the theme's core CSS.

## Solution

Target the specific selector `.theme-preloader .loading-container .loading` with brand colors:

```css
/* THE SPINNER ARC - ORANGE + BLUE */
.theme-preloader .loading-container .loading {
    border-width: 4px !important;
    border-style: solid !important;
    border-color: transparent #f1420b transparent #2a93c1 !important;
    border-radius: 50% !important;
}
```

The `border-color` shorthand sets: top, right, bottom, left.
- `transparent` (top) - no arc
- `#f1420b` (right) - ORANGE arc
- `transparent` (bottom) - no arc
- `#2a93c1` (left) - BLUE arc

## Key Insight

Generic preloader selectors like `.theme-preloader .spinner` don't work because the Awaiken theme uses `.loading` class instead of `.spinner`. Always inspect the actual HTML structure before writing CSS.

## WordPress CAPTCHA Challenge

The purebrain.ai WordPress login has a CAPTCHA that changes each page load. Automated scripts cannot reliably solve it. Manual login is required, or use:
1. WordPress REST API with Application Password
2. Session cookies from a manual login

## Files

- CSS file: `/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css`
- Screenshot evidence: `/home/jared/projects/AI-CIV/aether/sandbox/blog-loader-fix/01_initial_load.png`

## Future Application

When theming WordPress preloaders:
1. Inspect the actual HTML structure (not assumptions)
2. Check theme-specific class names
3. Use high-specificity selectors with `!important`
4. Test by capturing screenshots during page load (before `display: none` is applied)
