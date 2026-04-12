# Newsletter Link Orange Hover - Plugin v2.7.0

**Date**: 2026-02-20
**Type**: operational
**Agent**: full-stack-developer

## Task
Add orange mini-button hover effect to the newsletter/subscribe link in .blog-cta-block on blog posts.

## What Changed

### CSS: Default state (prevents layout jump)
```css
body.single-post .blog-cta-block p a[href*="subscribe"],
... {
    padding: 3px 0 !important;          /* was: padding: 0 !important */
    border-radius: 5px !important;       /* was: border-radius: 0 !important */
    transition: color 0.2s ease, text-decoration-color 0.2s ease, background 0.2s ease, padding 0.15s ease !important;
    /* was: transition: color 0.2s ease, text-decoration-color 0.2s ease !important; */
}
```

### CSS: Hover state (orange button effect)
```css
body.single-post .blog-cta-block p a[href*="subscribe"]:hover, ... {
    color: #ffffff !important;
    text-decoration: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    padding: 3px 10px !important;
    border-radius: 5px !important;
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
}
```

## Key Pattern: Invisible Padding Prevents Layout Jump

When switching from `padding: 0` to `padding: 3px 10px` on hover, text jumps.
Fix: Set default state to `padding: 3px 0` (matches vertical but no horizontal).
On hover, horizontal padding adds the "pill" effect without vertical movement.

This same technique applies any time you want to add side-padding on hover without causing the element's line height to shift.

## Deployment

- Plugin version bumped: 2.6.0 → 2.7.0
- Deploy script: `tools/security/deploy_plugin_v270.py`
- All 14 pre-deploy validation checks passed
- All 8 live verification checks passed
- GoDaddy cache flush found and executed automatically

## Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php`
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v270.py` (new)
