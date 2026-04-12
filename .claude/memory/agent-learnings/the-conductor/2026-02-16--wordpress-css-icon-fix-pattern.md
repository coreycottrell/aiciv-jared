# WordPress CSS Icon Fix Pattern

**Date**: 2026-02-16
**Context**: Fixing purebrain.ai icon styling (orange icons on light orange → white icons on solid orange)

## The Pattern

When icons appear wrong (wrong color combo), the fix is usually:
1. **Identify the CSS class** - Use browser dev tools to find exact class names
2. **Check computed styles** - See what's actually being applied
3. **Apply via WordPress Customizer** - Appearance > Customize > Additional CSS

## Key Classes for purebrain.ai

```css
/* Icon boxes with orange styling */
.feature-card__icon--orange {
    background: rgb(241, 66, 11) !important;  /* Solid orange */
    color: #ffffff !important;                 /* White text/icons */
}

.feature-card__icon--orange svg,
.feature-card__icon--orange svg path {
    color: #ffffff !important;
    fill: #ffffff !important;
}

.value-card__icon--orange {
    background: rgb(241, 66, 11) !important;
    color: #ffffff !important;
}

.value-card__icon--orange svg,
.value-card__icon--orange svg path {
    color: #ffffff !important;
    fill: #ffffff !important;
}
```

## Learning: SVG Icons Need Multiple Selectors

SVG icons can inherit color from:
- Parent element's `color` property
- SVG element's `fill` attribute
- Path element's `fill` attribute

To ensure white icons: target both the SVG element AND its path children.

## Tool Created

`tools/wp_fix_icon_css.py` - Playwright script for WordPress CSS injection via Customizer

## WordPress Credentials (purebrain.ai)

- Username: `Purebrain@puremarketing.ai`
- App Password: `FlFr 2VOt lHiH aJWj zW96 OHUJ`
- Note: Must click "Log in with username and password" first (GoDaddy default is SSO)

## Tags

#wordpress #css #icons #purebrain #styling #browser-vision-tester
