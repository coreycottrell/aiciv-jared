# Blog Post Duplicate Section Fix - teach-your-ai

**Date**: 2026-03-07
**Type**: gotcha
**Topic**: WordPress theme shows title+date AND article had h1+Published on = visible duplication

## Root Cause

The PureBrain.ai WordPress theme renders a `page-header-box` that shows:
- `<h1 class="text-anime">` with the post title
- Date and category meta via `post-single-meta`

When the article content ALSO contains an `<h1>` and `<p>Published on: ...</p>` line, users see both rendered on the page = duplicated title and date.

## Correct Blog Post Structure

Post 1378 (52-billion, correct): starts with `<h2>` subtitle, no h1, no Published on line
Post 1423 (teach-your-ai, was broken): had `<h1>` + Published on line = duplicate

**Correct article content pattern:**
```html
<!-- wp:html -->
<article class="pb-blog-post">
[optional <style>...</style>]
<p>First paragraph...</p>  <!-- or <h2> subtitle -->
<hr>
...sections...
</article>
<!-- /wp:html -->
```

**Do NOT put inside article:**
- `<h1>` title (theme already renders it in page-header-box)
- `<p><strong>Published on</strong>: ...</p>` line (theme renders date/meta)

## Fix Applied

- Post ID: 1423 on purebrain.ai
- Removed `<h1>Teach Your AI...</h1>` from article content
- Removed `<p><strong>Published on</strong>:...</p>` from article content
- Removed leading `<hr>` that was separating removed Published on from intro
- Content now starts directly with first body paragraph
- Auth: PUREBRAIN_WP_USER / PUREBRAIN_WP_APP_PASSWORD (NOT WORDPRESS_USER/APP_PASSWORD)

## Auth Pattern

```python
wp_user = os.getenv('PUREBRAIN_WP_USER')  # purebrain@puremarketing.ai
wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
# WORDPRESS_USER returns 401 for edit context - use PUREBRAIN_WP_USER
```

## Cache Behavior

- After REST API update, Cloudflare/WP cache serves old content
- Adding `?nocache=1` query string bypasses cache to verify
- `DELETE /elementor/v1/cache` clears Elementor cache (even for non-Elementor posts)
- No Cloudflare API credentials in .env - purge not available programmatically
- Cache expires naturally within minutes

## Going Forward

All new blog posts should NOT include h1 or Published on line in article content.
The theme handles title and date display in the page-header-box section.
