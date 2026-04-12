# Memory: WordPress Blog Wrapper Class Fix - pb-blog-post vs pb-blog-content

**Date**: 2026-02-26
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: WordPress blog content wrapper class mismatch causing broken CSS

---

## The Problem

Blog posts published with `<!-- wp:html -->` wrapping a `<div class="pb-blog-content">` lose ALL blog CSS:
- H2 headings lose spacing
- Bullet lists revert to browser defaults
- HRs use wrong color
- Links use wrong color
- Content goes full-width instead of 760px centered

## Root Cause

The theme's blog CSS is scoped to `.post-content` and `.pb-blog-post` selectors, NOT `.pb-blog-content`.

**Broken wrapper**: `<div class="pb-blog-content">`
**Correct wrapper**: `<article class="pb-blog-post">`

## The Fix

1. Get raw post content via `GET /wp-json/wp/v2/posts/{id}?context=edit`
2. Replace `<div class="pb-blog-content">` with `<article class="pb-blog-post">`
3. Add `</article>` before `<!-- /wp:html -->` at the end (or before end of raw if no wp:html block)
4. Push via `POST /wp-json/wp/v2/posts/{id}` with `json={'content': fixed_content}`

## JDS vs purebrain.ai Difference

- **purebrain.ai**: Raw content has `<!-- wp:html -->` block wrappers
- **jareddsanborn.com**: Raw content is bare HTML without block wrappers

For JDS, no `<!-- /wp:html -->` to deal with - just strip trailing whitespace and append `\n</article>`.

## Verification Checklist

```python
rendered = post['content']['rendered']
assert 'pb-blog-post' in rendered
assert 'pb-blog-content' not in rendered
# Then fetch live page:
assert '<article class="pb-blog-post"' in live_html
assert r.status_code == 200
assert 'pt-social-share' in live_html   # footer present
assert 'blog-cta-block' in live_html    # CTA present
```

## Post IDs Fixed This Session

- purebrain.ai: post ID 966 (slug: the-first-90-days-of-an-ai-partnership)
- jareddsanborn.com: post ID 1210 (same slug)

## Key Files

- Blog footer template: `.claude/skills/wordpress-publishing/blog-footer-template.html`
- Footer uses `{slug}` placeholder for UTM tracking links
