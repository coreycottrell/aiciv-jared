# Memory: Blog Nav "Blog" → "Subscribe" Change (v3.7.0)

**Date**: 2026-02-21
**Type**: operational + teaching
**Topic**: Changed blog nav "Blog" link to "Subscribe" linking to #neural-feed-subscribe

---

## Summary

Changed the nav bar on blog pages and single posts from showing "BLOG" (redundant when you're already on/reading a blog post) to "SUBSCRIBE" which anchors to the subscribe section at the bottom of the blog page.

---

## Two Nav Systems on purebrain.ai

There are TWO separate nav bars on purebrain.ai blog content:

### 1. `blog2-nav` (blog listing page only - page ID 319)
- **Where**: Elementor HTML widget content embedded in page 319 (`/blog/`)
- **Class**: `<nav class="blog2-nav">`
- **Managed by**: REST API update to page content (NOT the plugin)
- **Old**: `<a href="https://purebrain.ai/blog/" class="active">Blog</a>`
- **New**: `<a href="https://purebrain.ai/blog/#neural-feed-subscribe">Subscribe</a>`
- **How to update**: `PUT /wp-json/wp/v2/pages/319` with modified `content` field
- **Auth**: Aether app password works for this REST API call

### 2. `pb-blog-nav` (single posts + category/archive pages)
- **Where**: Plugin-injected via `wp_footer` hook
- **Class**: `<div class="pb-blog-nav">`
- **Managed by**: PureBrain Security Plugin (plugin-editor.php)
- **JS variable**: `$subscribe_url = esc_url( home_url( '/blog/#neural-feed-subscribe' ) )`
- **Old**: `Blog` → `https://purebrain.ai/blog/`
- **New**: `Subscribe` → `https://purebrain.ai/blog/#neural-feed-subscribe`

---

## Subscribe Section ID

The subscribe section at the bottom of the blog page has:
```html
<section id="neural-feed-subscribe" class="nf-section" aria-label="Subscribe to The Neural Feed">
```
Located in page 319's HTML content, around line 3090+ of the raw content.
Anchor: `#neural-feed-subscribe`

---

## Plugin Changes (v3.6.0 → v3.7.0)

**File**: `tools/security/purebrain-security/purebrain-security-plugin.php`

Changed in `wp_footer` hook (around line 2868):
```php
// OLD:
$blog_url = esc_url( home_url( '/blog/' ) );
// ...
'<a href="<?php echo $blog_url; ?>">Blog</a>'

// NEW:
$subscribe_url = esc_url( home_url( '/blog/#neural-feed-subscribe' ) );
// ...
'<a href="<?php echo $subscribe_url; ?>">Subscribe</a>'
```

---

## Deployment Results

### purebrain.ai
- **blog2-nav** (page 319): Updated via REST API - VERIFIED LIVE
- **pb-blog-nav** (plugin): Updated via Playwright plugin editor - VERIFIED LIVE
- **Verification checks all passed**:
  - Subscribe text present in blog2-nav
  - `neural-feed-subscribe` href in blog2-nav
  - Old `Blog` text gone from blog2-nav
  - `class="active"` removed from nav link
  - pb-blog-nav present on single posts
  - Subscribe in pb-blog-nav
  - neural-feed-subscribe href in pb-blog-nav

### jareddsanborn.com
- **Status**: BLOCKED by GoDaddy reCAPTCHA
- **Cause**: Multiple failed login attempts triggered GoDaddy bot protection
- **Root cause**: `New1Jared88887` password showing "Invalid credentials" - may have changed
- **The pb-blog-nav shows on single posts/archives** - same Subscribe change needed
- **blog2-nav**: jareddsanborn.com blog page does NOT have a blog2-nav (different theme/structure)
- **Action needed**: Jared needs to provide current jareddsanborn.com admin password, OR wait 15-30 min for lockout to clear and retry with correct password

---

## Deploy Script

New deploy script created: `tools/security/deploy_plugin_v370.py`

---

## Key Lessons

### GoDaddy Bot Protection on jareddsanborn.com
- Multiple failed logins trigger reCAPTCHA lockout (same as purebrain.ai)
- The password `New1Jared88887` may be stale - getting "Invalid credentials"
- Lockout shows "Please verify you are human" with reCAPTCHA (not solvable by bot)
- Solution: Wait 15-30 min and retry, OR get fresh password from Jared
- LESSON: Store jareddsanborn admin password in `.env` as `WORDPRESS_ADMIN_PASSWORD`

### REST API vs Plugin Editor
- blog2-nav changes: Use REST API (fast, reliable, no Playwright needed)
- Plugin file changes: Must use Playwright plugin editor (no REST API for file edits)
- For page content changes: REST API PUT to `/wp-json/wp/v2/pages/{id}` works well

### Auth for purebrain.ai REST API
- `PUREBRAIN_WP_APP_PASSWORD` (FlFr2VOtlHiHaJWjzW96OHUJ) works for `context=edit` GET and POST updates
- Earlier test showed 401, but direct test showed it works - may have been a timing issue

---

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` (v3.7.0)
- `tools/security/deploy_plugin_v370.py` (new deploy script)
- purebrain.ai page 319 content (via REST API, not in repo)
