# Share Button CSS Cascade Conflict - purebrain.ai Blog Posts

**Date**: 2026-02-24
**Type**: gotcha
**Agent**: browser-vision-tester
**Topic**: Two competing share button systems causing CSS cascade conflict on blog posts

## Context

Testing /your-next-direct-report-wont-be-human/ and similar blog posts on purebrain.ai.
The page has two share button systems:
1. Custom `pt-social-share` div (pill-shaped buttons - CORRECT design)
2. Theme's `post-social-sharing` div with `ul/li` structure (blue circles - WRONG, should be hidden)

## Discovery

The CSS plugin hides `.post-social-sharing` with `display: none !important` early in the stylesheet.
BUT later in the SAME stylesheet, a "styled share buttons" block re-applies `display: flex !important`
to `.post-social-sharing` because it's included in a grouped selector rule.

CSS cascade: later rule wins. The blue circle theme bar re-appears.

## Root Cause

The "social share styling" block uses overly broad selectors that accidentally match
the element being hidden. The hide rule comes BEFORE the styling rule in the CSS file,
so the styling rule wins via cascade order (last declaration wins when specificity is equal).

## Fix Pattern

Add a FINAL OVERRIDE block at the very end of the plugin CSS, after all other rules:

```css
/* FINAL OVERRIDE - must be last in file */
div.post-social-sharing,
.post-social-sharing ul,
.single-post .post-social-sharing {
    display: none !important;
    visibility: hidden !important;
}
```

The `pt-social-share` class is safe - it does NOT match `.post-social-sharing` selectors.

## CTA Button Finding

The `Start Your AI Partnership` button (.cta-btn) has correct white text:
- Inline style: `color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;`
- Class CSS: `color: #ffffff !important` with orange gradient background

If text appears dark: add higher-specificity rule:
```css
body.single-post .blog-cta-block .cta-btn {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
```

## ai-website-execution Page Finding

/ai-website-execution/ is a fully populated Elementor canvas page (148kb HTML).
OR sections, Awaken buttons, and dark backgrounds all confirmed in source HTML.
If a user sees white page: it is CDN/JS cache issue, not missing content.
Fix: Clear Cloudflare cache for that specific URL + regenerate Elementor CSS.

## When to Apply

- Any time share buttons appear as circles instead of pills on blog posts
- Any time a hide rule seems to not be working in the plugin CSS
- CSS cascade conflicts: check if a LATER rule is overriding the hide

## Tags

css-cascade, share-buttons, blog-post, plugin-css, hide-override
