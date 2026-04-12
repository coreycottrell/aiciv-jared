# CTA Button Orange Fix + Blue Hover — Plugin v2.5.0

**Date**: 2026-02-20
**Type**: teaching
**Topic**: CSS specificity collision between CTA button and newsletter link in .blog-cta-block

---

## Problem

The v2.4.0 plugin added a broad CSS rule to style newsletter links inside `.blog-cta-block`:

```css
body.single-post .blog-cta-block p a {
    color: #2a93c1 !important;
    text-decoration: underline !important;
    background: none !important;  /* <-- THIS WAS THE KILLER */
}
```

The CTA button (`<p><a href="...#awakening" style="background: linear-gradient(...)">`) is also a `p > a` inside `.blog-cta-block`. So `background: none !important` stripped the orange gradient background from the button, leaving it as plain unstyled blue underlined text.

## Root Cause Pattern

**CSS specificity does not distinguish between two elements with the same DOM position** (both `p > a` inside `.blog-cta-block`). When you need different styles for two sibling `<a>` elements, you must use an **attribute selector** or **class** to differentiate them.

## Solution Applied

Split the CSS rules using `href` attribute selectors:

```css
/* CTA button — links containing "awakening" */
body.single-post .blog-cta-block p a[href*="awakening"] {
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    color: #ffffff !important;
    display: inline-block !important;
    padding: 14px 32px !important;
    border-radius: 8px !important;
    /* ... */
}
body.single-post .blog-cta-block p a[href*="awakening"]:hover {
    /* BLUE hover (not orange) — Jared's preference */
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
}

/* Newsletter links — href contains subscribe/newsletter/neural-feed */
body.single-post .blog-cta-block p a[href*="subscribe"],
body.single-post .blog-cta-block p a[href*="neural-feed"] {
    background: none !important;
    color: #2a93c1 !important;
    text-decoration: underline !important;
}
```

## Verification Evidence

After deploy, `getComputedStyle()` confirmed live on purebrain.ai:

- Button: `background: rgb(241, 66, 11) linear-gradient(...)`, `color: rgb(255,255,255)`, `display: inline-block`, `padding: 14px 32px`
- Newsletter link: `background: rgba(0,0,0,0) none`, `color: rgb(42,147,193)`, `text-decoration: underline rgba(42,147,193,0.4)`

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` — version bumped to 2.5.0, section j rewritten
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v250.py` — deploy + verification script

## Key Lesson

**When two visually different elements share the same DOM structure (`p > a` inside `.some-container`), differentiate them by `href` attribute selector or add a CSS class to one of them. Never use a catch-all rule that applies `background: none !important` when one of the matched elements needs a background.**

CTA button URL pattern: `href*="awakening"`
Newsletter link URL patterns: `href*="subscribe"`, `href*="newsletter"`, `href*="neural-feed"`
