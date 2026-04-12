# Plugin v5.1.3: pb-inline-cta CSS moved to wp_footer

**Date**: 2026-02-24
**Type**: teaching + operational
**Topic**: CTA button text still orange after inline style fixes — wp_footer vs wp_head load order

---

## Problem

Jared reported CTA button near "This is what AI partnership looks like..." text showed orange text on orange button (invisible). Plugin v5.1.2 already had inline `color: #ffffff !important` on the button.

## Investigation Findings

1. **Server HTML was correct** - all three CTA buttons had white color inline styles
2. **pb-inline-cta button was missing `!important` on `-webkit-text-fill-color`**
   - `style="...-webkit-text-fill-color: #ffffff;"` ← no !important
   - CSS rule `#pb-agent-manager-post a { color: #f1420b !important }` (specificity 1,0,1) was winning
3. **pb-inline-cta-template-lock CSS was in wp_head at priority 100** but wp-custom-css (Additional CSS) fires AFTER priority-100 wp_head hooks
4. **Cloudflare was serving cached page** (cf-cache-status: HIT, age: 142s) but the cached version ALSO had correct HTML - issue was browser cache

## Fixes Applied

### Fix 1: Added !important to -webkit-text-fill-color in post 879 content
```
-webkit-text-fill-color: #ffffff; → -webkit-text-fill-color: #ffffff !important;
```
Deployed via REST API with `--data-urlencode` (never Python json.dumps for !important).

### Fix 2: Plugin v5.1.3 - Moved pb-inline-cta CSS to wp_footer priority 5
```php
// BEFORE (v5.0.5):
add_action('wp_head', function() { ... style block ... }, 100);

// AFTER (v5.1.3):
add_action('wp_footer', function() { ... style block ... }, 5);
```
wp_footer fires AFTER ALL wp_head CSS including Additional CSS.
Also added `:hover`, `:active`, `:focus` states with !important.

## Key Rules

1. **wp-custom-css (Additional CSS) fires AFTER wp_head priority 100**
   For CSS that must beat Additional CSS: use `wp_footer`, not `wp_head`.

2. **-webkit-text-fill-color needs !important when ANY CSS targets element**
   Even `color: #ffffff !important` inline won't protect text rendering if a CSS rule
   has `-webkit-text-fill-color: orange !important`.

3. **When fix is deployed but user still sees bug: check browser cache first**
   Ask user to hard-refresh (Ctrl+Shift+R / Cmd+Shift+R).

## Verification

7/7 live checks passed after deployment.

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` v5.1.2 → v5.1.3
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v513_purebrain.py` (new)
- Post 879 content: `-webkit-text-fill-color: #ffffff !important` added
