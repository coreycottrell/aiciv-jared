# FAQ Collapse + CTA Hover Bugs - Plugin v2.3.0 Fix

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer

## Summary

Fixed two CSS/JS bugs on purebrain.ai blog posts via plugin v2.3.0 update.

## Bug 1: FAQ Not Starting Collapsed

### Root Cause

The FAQ accordion used a CSS pattern where `.faq-answer { max-height: 0 }` hides answers.
But `.faq-answer` is created by JavaScript (wrapping `<p>` tags). Before JS runs,
the `<p>` tags are direct children of `.faq-section` with no hiding CSS applied.

This means on every page load, FAQs briefly (or permanently if JS is slow/broken) show as expanded.

### Investigation

- Plugin CSS/JS WAS correctly injected (checked via style tag IDs in live HTML)
- Body class `single-post` IS present - selector worked fine
- JS selector `.single-post .post-content .faq-section` - `single-post` on body
  is a valid CSS descendant match (body has that class, so elements inside it match)
- The real issue: no CSS rule hid the raw `<p>` before JS wrapped them

### Fix Applied

Added pre-JS hiding rule:
```css
body.single-post .post-content .faq-section > p {
    overflow: hidden !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    transition: max-height 0.35s ease !important;
}
```

Added reset rule for after JS wraps them:
```css
body.single-post .post-content .faq-section .faq-answer > p {
    max-height: none !important;
    overflow: visible !important;
    margin: 0 !important;
    padding: 0 !important;
}
```

Also improved JS:
- Check `document.body.classList.contains('single-post')` directly (more reliable)
- Handle multiple `<p>` children per `.faq-section` (loop over childNodes)
- Use `readyState` check to init as early as possible (not just DOMContentLoaded)
- Increased max-height from 600px to 800px for longer answers

## Bug 2: CTA Button Goes Blank on Hover

### Root Cause

In `wp-custom-css` there's a rule:
```css
body.single-post a:hover {
    color: #f1420b !important;
}
```

This turns ALL link text orange on hover. The CTA button has:
- Background: orange gradient `linear-gradient(135deg, #f1420b 0%, #d13608 100%)`
- Text: white `color: #ffffff !important` (inline style)

When hovering, the `body.single-post a:hover { color: #f1420b !important }` overrides
the inline white text (because `!important` in stylesheet beats `!important` in inline
when both have equal specificity... actually this depends on browser cascade rules).

The button text becomes orange (#f1420b) against an orange background - invisible,
appearing as a "blank" button.

### Fix Applied

Added explicit `color: #ffffff !important` and `background` preservation to hover rule:
```css
.blog-cta-block a:hover,
body.single-post .blog-cta-block a:hover,
body.single-post .blog-cta-block p a:hover {
    box-shadow: 0 0 0 3px #2a93c1, 0 0 18px rgba(42,147,193,0.55), ... !important;
    transform: translateY(-2px) !important;
    color: #ffffff !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
}
```

The specificity of `body.single-post .blog-cta-block a:hover` (0,3,1) beats
`body.single-post a:hover` (0,2,1), so white text wins.

## Deployment Note

The server was running v2.0.0 (plugin had never been successfully updated past that).
v2.1.0 and v2.2.0 updates had been applied to local files but never deployed.
This v2.3.0 deploy pushed ALL accumulated changes since v2.0.0 to the server.

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security.php` (v2.3.0)
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v2.3.0)
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v230.py` (new deploy script)

## Verification

- v2.3.0 confirmed LIVE on purebrain.ai/ceo-vs-employee-ai-transformation-gap/
- FAQ: 6 items found, `firstIsOpen: False` (all collapsed)
- CTA: orange button with white text visible
- Pre-JS CSS active in browser CSS rules
- Screenshots: `exports/screenshots/plugin_v230_faq_live.png` + `plugin_v230_cta_hover.png`

## Teaching: CSS Pre-JS Pattern

When JS creates DOM elements that control CSS visibility, ALWAYS add a CSS rule
that hides content BEFORE the JS runs. Otherwise users see a "flash" of the
uncollapsed state on every page load.

Pattern:
1. CSS hides raw content immediately (pre-JS state)
2. JS wraps content in controlled container
3. CSS on the container manages animated visibility
4. CSS resets the inner elements to visible once inside the container

## Teaching: !important Override Chain

When multiple `!important` rules conflict:
- Winner = highest CSS specificity
- `body.single-post .blog-cta-block a:hover` (0,3,1) beats `body.single-post a:hover` (0,2,1)
- This is why scoped, specific selectors are needed to override broad generic rules
- Inline style `!important` is treated as if specificity = (1,0,0,0) but can still be
  beaten by a stylesheet `!important` with higher specificity in some browsers
