# Memory: Blog Category Nav Link - Plugin v2.2.0

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Adding "← All Posts" blog navigation link on category/archive pages

---

## Problem

Category pages like `/category/for-teams/` and `/category/for-individuals/` had no
navigation link back to the main blog at `/blog/`. Users landing on a category page
had no easy path back to the full blog listing.

## The CSS Was Already There

The `.blog-nav-links` CSS class was already in WordPress Additional CSS (from Feb 18):
```css
.blog-nav-links {
    display: flex !important;
    align-items: center !important;
    margin-left: auto !important;  /* right-aligns in navbar */
    font-size: 14px !important;
    font-weight: 400 !important;
    letter-spacing: 0.5px !important;
}
.blog-nav-links a {
    color: rgba(255,255,255,0.7) !important;
    text-decoration: none !important;
    padding: 4px 10px !important;
    transition: color 0.2s ease !important;
}
.blog-nav-links a:hover {
    color: #f1420b !important;
}
```

But no HTML element with that class was being injected - hence nothing was visible.

## The Fix

Added section `k)` to the PureBrain security plugin (v2.2.0):

```php
add_action( 'wp_footer', function () {
    if ( ! ( is_category() || is_archive() || is_tag() ) ) {
        return;
    }
    $blog_url = esc_url( home_url( '/blog/' ) );
    ?>
<script id="purebrain-category-blog-nav">
(function() {
    'use strict';
    document.addEventListener('DOMContentLoaded', function() {
        var container = document.querySelector('nav.navbar .container');
        if (!container) return;
        if (document.querySelector('.blog-nav-links')) return;

        var nav = document.createElement('div');
        nav.className = 'blog-nav-links';
        nav.innerHTML = '<a href="<?php echo $blog_url; ?>">&#8592; All Posts</a>';
        container.appendChild(nav);
    });
})();
</script>
    <?php
} );
```

## Why JS Injection (not PHP)

The navbar HTML is rendered by the WordPress theme. We can't easily inject PHP into the
`nav.navbar .container` element. JavaScript DOM manipulation via `wp_footer` hook is the
cleanest approach - runs after DOM is ready, won't break if navbar structure changes.

## Deployment

- Plugin updated to v2.2.0
- Deployed via Playwright (WP Plugin Editor)
- GoDaddy cache flushed
- Verified live: `document.querySelector('.blog-nav-links')` returns the injected element
- Visual screenshot confirms "← All Posts" visible in top-right of navbar

## Key Learning: PHP is_category() Check

Use `is_category() || is_archive() || is_tag()` to scope the injection correctly.
- `is_category()` - category pages (/category/*)
- `is_archive()` - date archives, author archives
- `is_tag()` - tag pages

The `wp_footer` hook fires on every page, so the PHP conditional is essential.

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` v2.2.0
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` (synced)
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip` (repackaged)

## Deploy Script

`/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v220.py`

## Screenshot

`/home/jared/projects/AI-CIV/aether/exports/screenshots/plugin_v220_category_live.png`
Shows "← All Posts" in top-right corner of the For Teams category page.
