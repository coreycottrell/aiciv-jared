# Security Plugin v2.4.0: Nav Menu + Newsletter Link Fix

**Date**: 2026-02-20
**Type**: operational + teaching
**Topic**: WordPress plugin deploy - navbar injection on blog posts and category pages

---

## What Was Done

Updated `tools/security/purebrain-security-plugin.php` from v2.3.0 to v2.4.0 with three changes:

1. **Nav menu (Home | Blog | AI Assessment)** injected into top navbar on:
   - Single blog posts (`is_single()`)
   - Category/archive/tag pages (`is_category() || is_archive() || is_tag()`)
   - Replaced old "← All Posts" category-only link
   - CSS: `.pb-blog-nav` class, right-aligned (margin-left: auto), pipe separator, brand blue hover
   - Responsive: hidden <480px, smaller font 481-767px

2. **Newsletter/CTA paragraph link fix**: `.blog-cta-block p a` uses `#2a93c1` base, `#ffffff` on hover
   - Root cause: generic `body.single-post a:hover { color: #f1420b }` was overriding ALL links

3. **Version bumped** to 2.4.0

---

## Key Technical Decisions

### CSS class name: `.pb-blog-nav` (not `.blog-nav-links`)
- The old `.blog-nav-links` class was in WordPress Additional CSS
- New `.pb-blog-nav` lives entirely in the plugin - no dependency on Additional CSS
- Self-contained is better: plugin works standalone

### Two hooks: wp_head (CSS) + wp_footer (JS)
- CSS goes in `wp_head` so styles are available when DOM renders
- JS goes in `wp_footer` to ensure navbar DOM exists before injection
- Both hooks check `is_single() || is_category() || is_archive() || is_tag()`

### /blog/ page is NOT a category page
- purebrain.ai/blog/ is a static WordPress page (ID 319, Elementor-built)
- It does NOT trigger `is_archive()` or `is_category()`
- Real category pages: `/category/for-teams/`, etc.
- The Elementor /blog/ page has its own header - our injection not needed there

### Newsletter link specificity
- Must use `!important` on `.blog-cta-block p a` rules
- The `body.single-post .blog-cta-block a:hover` rule (for the CTA button) is broader
- Paragraph links need their OWN specific rules to override the button rules

---

## Deploy Pattern

- Deploy script: `tools/security/deploy_plugin_v240.py`
- Uses `PUREBRAIN_WP_PASSWORD` env var (not `PUREBRAIN_WP_APP_PASSWORD`)
- CodeMirror setValue() is the primary method; textarea fallback if CM fails
- Validation checks: version string + key CSS class names present before deploy
- GoDaddy cache flush via `/wp-admin/options-general.php?wpaas_action=flush_cache`
- Verification: HTTP GET to blog post, check for key strings in HTML

---

## Deployment Result

- Plugin saved successfully via CodeMirror
- Cache flushed via GoDaddy flush_cache nonce URL
- Verified live: all 5 checks passed on blog post
- Nav confirmed working on `/category/for-teams/` (real category page)
- Screenshots: `exports/screenshots/plugin_v240_*.png`

---

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (updated to v2.4.0)
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v240.py` (new deploy script)
