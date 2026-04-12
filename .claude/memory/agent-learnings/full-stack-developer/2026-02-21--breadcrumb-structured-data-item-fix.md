# Breadcrumb Structured Data - Missing 'item' Field Fix

**Date**: 2026-02-21
**Type**: teaching
**Agent**: full-stack-developer

## Problem

Google Search Console flagged purebrain.ai breadcrumbs as missing the 'item' field.

The live JSON-LD BreadcrumbList looked like this (BEFORE fix):
```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://purebrain.ai/" },
    { "@type": "ListItem", "position": 2, "name": "Why 95% of AI Pilots Fail" }
    // ^ MISSING 'item' URL on last breadcrumb
  ]
}
```

## Root Cause

Yoast SEO (plugin: wordpress-seo/wp-seo) generates the BreadcrumbList JSON-LD.
By default, Yoast omits the `item` (URL) property from the last ListItem (the current page).
Historically this was acceptable, but Google now requires `item` on ALL ListItems.

## Fix

Used Yoast's `wpseo_schema_breadcrumb` filter hook to post-process the schema data.
The filter iterates all `itemListElement` entries and injects the canonical URL for
any ListItem that's missing the `item` property.

URL resolution logic:
- `is_singular()` → `get_permalink()`
- `is_category() || is_tag() || is_tax()` → `get_term_link($term)`
- `is_archive()` → `get_pagenum_link()`
- `is_home() || is_front_page()` → `home_url('/')`

```php
add_filter( 'wpseo_schema_breadcrumb', function ( $schema_data ) {
    foreach ( $schema_data['itemListElement'] as &$list_item ) {
        if ( isset( $list_item['item'] ) ) continue;
        // ... determine $url based on current page type ...
        if ( ! empty( $url ) ) {
            $list_item['item'] = esc_url( $url );
        }
    }
    return $schema_data;
}, 10, 1 );
```

## Deployment

- Plugin updated: v3.2.0 → v3.3.0
- File: `tools/security/purebrain-security-plugin.php`
- Also: `tools/security/purebrain-security/purebrain-security-plugin.php` (the deploy target)
- Deploy script: `tools/security/deploy_plugin_v330.py`
- All 23 validation checks passed
- Verified live on: blog post + category page

## Verified After Fix

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://purebrain.ai/" },
    { "@type": "ListItem", "position": 2, "name": "Why 95% of AI Pilots Fail...", "item": "https://purebrain.ai/why-95-percent-of-ai-pilots-fail/" }
  ]
}
```

## Key Pattern for Future

When Yoast SEO generates structured data that needs modification, use the
`wpseo_schema_*` filter hooks. For BreadcrumbList specifically:
- Hook: `wpseo_schema_breadcrumb`
- Filter receives the full schema node (already PHP array)
- Modify and return it

GSC will re-validate affected pages within a few days of deploying the fix.
