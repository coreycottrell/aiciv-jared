# Emergency Rollback: v5.0.1 j5 CSS Hook Removal

**Date**: 2026-02-24
**Type**: operational
**Topic**: Plugin CSS rollback — j5 hook broke blog color scheme

---

## What Happened

Plugin v5.0.1 added the j5 `add_action('wp_head', ..., 99)` hook injecting a `<style id="purebrain-inline-cta-white-text-v501">` block with:

```css
html body.single-post .pb-inline-cta a { color: #ffffff !important; }
html body.single-post .entry-content a[style*="background"][style*="gradient"] { color: #ffffff !important; }
```

This broke the blog color scheme site-wide. Jared: "whatever you did here changed the color on the entire blog."

## Root Cause

The `html body.single-post .entry-content a[style*="background"][style*="gradient"]` selector was a "belt-and-suspenders" rule that matched too broadly — catching links that shouldn't have been affected and overriding their colors with `#ffffff !important`.

## Fix Applied

1. Removed the entire j5 `add_action` block (lines ~2235-2283 in the pre-rollback file)
2. Reverted version header from 5.0.2 → 5.0.0
3. Deployed via existing Playwright deploy pattern

## Deploy Script

`/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v500_rollback.py`

## Verification

Both test posts confirmed:
- `purebrain-inline-cta-white-text-v501` style block: GONE from page source
- `.pb-inline-cta a,` rule: GONE from page source
- HTTP 200 on both posts
- 4/4 checks passed on each

## Lessons

1. **Broad CSS attribute selectors are dangerous in priority-99 wp_head hooks.** The `a[style*="background"][style*="gradient"]` selector caught unintended elements.
2. **Always test color-related CSS changes visually** before deploying to production — HTTP 200 is not enough.
3. **j5 hook pattern**: When a "universal safety net" CSS rule is needed, scope it as tightly as possible — avoid broad attribute selectors.
4. **Version rollback pattern**: Removing a feature = bump version to match the last clean state. Do NOT increment version for a rollback — use the clean version number.

## Plugin File

`/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
Current version after rollback: **5.0.0**
