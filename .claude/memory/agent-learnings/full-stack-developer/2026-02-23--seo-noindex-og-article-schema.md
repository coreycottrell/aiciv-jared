# SEO Fixes: noindex + OG tags + Article Schema - purebrain.ai

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: noindex pages, homepage OG title/description update, Article schema description

---

## What Was Done

1. Set noindex on privacy-policy (ID 3) and terms-of-service (ID 541) via REST meta
2. Prepared plugin v4.4.0 locally with OG meta fields in allowlist (deploy blocked by CAPTCHA)
3. Audited Article schema description on all 10 posts - Yoast v27 design issue, not per-post

---

## Key Learnings

### noindex via REST Meta (Pages Only)

The plugin registers `_yoast_wpseo_meta-robots-noindex` with `show_in_rest => true` for PAGES.
Standard REST `meta` field ACCEPTS this for pages and it works:

```bash
curl -X POST -u "Aether:APP_PASS" \
  -H "Content-Type: application/json" \
  -d '{"meta":{"_yoast_wpseo_meta-robots-noindex":"1"}}' \
  "https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID"
```

The REST response `yoast_head_json.robots` still shows `index` (cached/stale response), but
Yoast `get_head` API confirms `"index": "noindex"` and live curl confirms `noindex, follow`.

### OG Title/Description for Homepage

The Yoast `og:title` and `og:description` for the homepage are stored in the yoast_indexable
TABLE, not in post meta. There is NO `_yoast_wpseo_opengraph-title` meta key set by default.

To override via post meta, need to:
1. Register `_yoast_wpseo_opengraph-title` in `register_post_meta` with `show_in_rest => true`
2. Add it to the `update-post-meta` plugin allowlist

Plugin v4.4.0 does this. Once deployed, use `update-post-meta` endpoint.

### Plugin Deploy Blocked by CAPTCHA

Multiple failed Playwright login attempts triggered GoDaddy's bot protection CAPTCHA.
CAPTCHA persists 1+ hours even after waiting 15-30 minutes.
This is IP-level rate limiting, not browser-session based.

**Prevention**: Never attempt login with wrong credentials before a real deploy. The CAPTCHA
is triggered by IP-level failure count. Even one failed attempt may trigger it if the IP
has prior history.

### Article Schema Description - Yoast v27 Design

Yoast SEO v27 Article schema does NOT include `description` field - this is intentional.
The `description` IS present in `WebPage` schema instead.
Setting `_yoast_wpseo_metadesc` does NOT add description to Article schema.

To add it, need a plugin filter:
```php
add_filter('wpseo_schema_article', function($data) {
    if (empty($data['description'])) {
        $metadesc = get_post_meta(get_the_ID(), '_yoast_wpseo_metadesc', true);
        if ($metadesc) $data['description'] = $metadesc;
    }
    return $data;
});
```

### Page IDs

- thank-you: 309 (already had noindex)
- privacy-policy: 3
- terms-of-service: 541
- homepage: 11

---

## Verification Commands

```bash
# Check noindex on any page
curl -s "https://purebrain.ai/PAGE-SLUG/" -H "User-Agent: Googlebot/2.1" | grep "meta name='robots'"

# Check OG tags
curl -s "https://purebrain.ai/" -H "User-Agent: facebookexternalhit/1.1" | grep -E "og:|twitter:"

# Yoast robots check
curl -s "https://purebrain.ai/wp-json/yoast/v1/get_head?url=URL_ENCODED" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('json',{}).get('robots',{}))"
```

---

**End of Memory**
