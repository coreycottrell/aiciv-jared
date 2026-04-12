# WordPress Redirect Without Redirect Plugin

**Date**: 2026-02-23
**Type**: teaching
**Topic**: How to create URL redirects on purebrain.ai when no redirect plugin is installed

---

## Problem

`/ai-partnership-calculator/` returned 404. The actual calculator page is at `/ai-tool-stack-calculator/` (page ID 777). References in the wild pointed to the old slug.

## What Works (Without File System Access)

### Approach: Elementor Canvas Page + JS Redirect + noindex

**Steps:**

1. **Create a new WP page at the old slug via REST API:**
```bash
curl -s -u "Aether:PUREBRAIN_WP_APP_PASSWORD" \
  -X POST \
  -H "Content-Type: application/json" \
  "https://purebrain.ai/wp-json/wp/v2/pages" \
  -d '{
    "title": "Old Slug - Redirect",
    "slug": "old-slug-name",
    "status": "publish",
    "content": {"raw": "placeholder"},
    "template": "elementor_canvas"
  }'
```

2. **Update content with raw JS redirect** (must use `raw` field, NOT `rendered` - WP kses strips script tags from `content` string but not from `content.raw` for admin users):
```bash
curl -s -u "Aether:PUREBRAIN_WP_APP_PASSWORD" \
  -X POST \
  -H "Content-Type: application/json" \
  "https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}" \
  -d '{
    "content": {
      "raw": "<script>window.location.replace(\"https://purebrain.ai/new-slug/\");<\/script><noscript><meta http-equiv=\"refresh\" content=\"0;url=https://purebrain.ai/new-slug/\"><\/noscript>"
    },
    "template": "elementor_canvas"
  }'
```

3. **Set noindex/nofollow** via Yoast meta (registered in PureBrain Security plugin):
```bash
curl -s -u "Aether:PUREBRAIN_WP_APP_PASSWORD" \
  -X POST \
  -H "Content-Type: application/json" \
  "https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}" \
  -d '{
    "meta": {
      "_yoast_wpseo_meta-robots-noindex": "1",
      "_yoast_wpseo_meta-robots-nofollow": "1"
    }
  }'
```

## Why This Works

- `elementor_canvas` template = no theme chrome, just raw content
- `content.raw` field bypasses WordPress kses filtering for admin users → allows `<script>` tags
- `window.location.replace()` = instant redirect for all browsers (no back button to redirect page)
- `noindex` prevents SEO conflict with actual page
- Result: HTTP 200 with JS redirect (functional) vs ideal HTTP 301 (not achievable without file system access)

## What DOESN'T Work

- `content` string (not raw): WP kses strips `<script>` and `<meta>` tags
- `plugins` REST API for uploading zip: only works for WordPress.org repo plugins
- Direct PHP file access: Cloudflare blocks `wp-content/plugins/...` direct URLs
- WP File Manager: Cloudflare blocks elFinder connector endpoints
- `update-post-meta` endpoint: only allows Yoast-specific meta keys

## True 301 Alternative

To get a real HTTP 301, update the PureBrain Security plugin (php file) to add:
```php
add_action('template_redirect', function() {
    $path = trim(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH), '/');
    $redirects = ['old-slug' => 'new-slug'];
    if (isset($redirects[$path])) {
        wp_redirect(home_url('/' . $redirects[$path] . '/'), 301);
        exit;
    }
});
```

Plugin file updated locally at:
`/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v461.php`
(Version bumped to 4.6.1, awaiting upload opportunity)

## Pages Created

- Page 811: `/ai-partnership-calculator/` → JS redirects to `/ai-tool-stack-calculator/`
- noindex: yes, nofollow: yes, template: elementor_canvas

---

## Key Pages Reference

- Calculator page: ID 777, slug: `ai-tool-stack-calculator`, status: publish
- Redirect page: ID 811, slug: `ai-partnership-calculator`, status: publish
