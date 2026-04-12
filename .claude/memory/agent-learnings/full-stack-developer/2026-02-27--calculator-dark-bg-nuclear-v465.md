# Calculator Page 777 Dark Background - Nuclear Fix v4.6.5

**Date**: 2026-02-27
**Type**: gotcha + fix  
**Agent**: dept-systems-technology / full-stack-developer

## The Persistent Problem

Page 777 (AI Tool Stack Calculator) showed orange background despite:
- Previous fix: `body { background: #080a12 !important }` deployed in page content CSS
- That fix WAS verified present in the rendered HTML (style block at byte 94796)
- CSS analysis confirmed no `body { background: orange }` rule anywhere

## Root Cause Investigation

Extensive analysis revealed:
1. The fix CSS IS in the page content (in WP body, after `</head>`)
2. External Artistics theme sets `body { background-color: var(--e-global-color-black) }` - resolves to #000000 (black), NOT orange
3. No orange body background exists in ANY CSS rule
4. The orange "background" is likely either:
   a. A visual element covering the page (preloader flash, magic cursor ball)
   b. Theme JS running AFTER CSS and overriding computed styles
   c. The CSS fix in page body (style block) being overridden by theme JS

## The Nuclear 3-Layer Fix (Plugin v4.6.5)

Added to `purebrain-security-plugin-v465.php`:

**Layer 1 - wp_head priority 1 (fires FIRST, position byte ~190 in rendered HTML):**
```css
#pb-calc-dark-bg-layer1
body.page-id-777 { background: #080a12 !important; }
```

**Layer 2 - wp_head priority 999 (fires LAST, after ALL CSS including Additional CSS + Elementor):**
```css
#pb-calc-dark-bg-layer2
body.page-id-777,
body.page-id-777.elementor-default,
body.page-id-777.elementor-template-canvas,
body.page-id-777.wp-theme-artistics,
body.page-id-777.tt-magic-cursor,
html body.page-id-777 { background: #080a12 !important; }
body.page-id-777::before, body.page-id-777::after { display: none !important; }
```

**Layer 3 - JS via wp_head priority 999 (runs at DOMContentLoaded, load, +500ms, +1500ms):**
```javascript
b.style.setProperty('background', '#080a12', 'important');
b.style.setProperty('background-color', '#080a12', 'important');
```

## Critical PHP Lesson

When using `echo '...';` in PHP with single quotes, ALL single quotes inside the string must be escaped as `\'`. For JavaScript inside PHP echo strings, this is error-prone.

**Solution**: Use `?> ... <?php` (inline HTML output) for any content with single quotes.

```php
// WRONG - PHP syntax error:
echo '<script>b.style.setProperty('background', '#080a12');</script>';

// CORRECT - use PHP template mode:
?>
<script>b.style.setProperty('background', '#080a12', 'important');</script>
<?php
```

## Deployment

- Plugin file: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v465.php`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v465_dark_bg.py`
- Deployed via WP Plugin Editor (Playwright)
- Verified: All 3 layers present in live page
- Layer 1 position: byte 190 (well inside `<head>`)
- Layer 1 BEFORE `</head>` (byte 94319): CONFIRMED

## Verification Results

```
[PASS] Layer1 CSS present - pb-calc-dark-bg-layer1 in HEAD at byte 190
[PASS] Layer2 CSS present - pb-calc-dark-bg-layer2 in HEAD (priority 999)
[PASS] Layer3 JS present  - pb-calc-dark-bg-js in HEAD with applyDarkBg()
[PASS] applyDarkBg function
[PASS] #080a12 bg present
```

## For Future Reference

When a body background fix via page content CSS isn't working:
1. Add CSS fix to PLUGIN (not page content) - plugin fires in WP HEAD
2. Use BOTH priority 1 (early) AND priority 999 (late) wp_head hooks
3. Add JS layer with setProperty + delays to cover theme JS that runs after load
4. Always test PHP syntax with single-quote content using `?> ... <?php` pattern
5. is_page(777) to scope fix to ONLY page 777 - no collateral impact
