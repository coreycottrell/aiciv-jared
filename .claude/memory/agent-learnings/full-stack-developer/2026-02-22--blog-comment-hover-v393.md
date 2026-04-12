# Memory: Blog Comment Section Link Hover Fix — v3.9.3

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: teaching + gotcha
**Topic**: Comment form (#respond) links outside post-content need separate CSS selectors

---

## Problem Solved

v3.9.2 CSS targeted `.post-content`, `.entry-content`, and `.elementor-widget-theme-post-content`.
The WordPress comment form (`#respond` / `.comment-respond`) is rendered OUTSIDE all of those
wrappers. So "Log out?" and "Cancel reply" links in the "Leave a Reply" section still showed
orange text on orange hover background — completely invisible.

## CSS Fix (v3.9.3)

Added new selectors covering the comment form area:

```css
/* Default state transition */
body.single-post #respond a,
body.single-post .comment-respond a,
body.single-post .logged-in-as a,
body.single-post .comment-reply-title a {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}

/* Hover: orange background, white text */
body.single-post #respond a:hover,
body.single-post .comment-respond a:hover,
body.single-post .logged-in-as a:hover,
body.single-post .comment-reply-title a:hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
```

**Note**: Nav and footer links are NOT inside `#respond`, so no additional exclusions needed for
the comment area selectors (unlike the post-content selectors which needed `:not([href*="awakening"])`).

## Deployment Results

| Site | Posts | Status |
|------|-------|--------|
| purebrain.ai | 9/9 | DB updated + live verified PASS |
| jareddsanborn.com | 10/10 | DB updated + live verified PASS |

Style block ID: `pb-link-hover-v393` (replaced `pb-link-hover-v392` in all posts)

## JDS Credentials Gotcha

The `.env` key is `WORDPRESS_USER=AetherPureBrain.ai` (NOT "jared").
Using `user=jared` returns HTTP 401 on PATCH even though GET works as "jared".
Always use `_env('WORDPRESS_USER')` for JDS write operations.

## Elementor Cache Flush Notes

- purebrain.ai Elementor cache: returned empty body (not JSON) — interpreted as error but actually flushed
- jareddsanborn.com: `/wp-json/elementor/v1/cache` returns 404 (Elementor not installed / no REST route)
  JDS uses Divi, not Elementor — no Elementor cache to flush on that site

## Files

- Deploy script: `tools/security/deploy_link_hover_v393.py`
- Old deploy script (reference): `tools/security/deploy_link_hover_v392.py`
- All 9 purebrain.ai posts: `<style id="pb-link-hover-v393">` prepended
- All 10 jareddsanborn.com posts: `<style id="pb-link-hover-v393">` prepended

## Live Verification Command

```python
import urllib.request
for url in ['https://purebrain.ai/the-ai-trust-gap/', 'https://jareddsanborn.com/the-ai-trust-gap/']:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    html = urllib.request.urlopen(req).read().decode()
    print(url, 'pb-link-hover-v393' in html, '#respond a:hover' in html)
```
