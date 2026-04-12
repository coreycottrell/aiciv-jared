# SEO Quick Fixes via WordPress REST API - purebrain.ai

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: How to implement SEO fixes (alt text, internal links, schema audit) via WP REST API

---

## What Was Done

5 SEO audit tasks implemented programmatically via REST API on purebrain.ai.

## Key Learnings

### 1. Featured Image Alt Text via Media Endpoint

WP media alt text lives on the media attachment, NOT on the post content img tag.

```python
# CORRECT: Update media attachment
requests.post(
    '/wp-json/wp/v2/media/{media_id}',
    auth=('Aether', APP_PASSWORD),
    json={'alt_text': 'Descriptive alt text here'}
)
```

The post content renders with `alt=""` unless the media attachment has alt_text set. 9/10 posts had featured images with empty alt_text despite having img tags with alt="" in rendered HTML.

### 2. Checking alt_text vs rendered HTML

The rendered HTML `alt=""` attribute reflects the media attachment's `alt_text` field.
Checking rendered HTML for `alt=""` gives FALSE NEGATIVES - you see `alt=""` and think it's empty when it's actually pulling from the media object.

Always check both:
1. `<img alt="...">` in rendered content (for inline images)
2. `GET /wp-json/wp/v2/media/{featured_media_id}` alt_text field (for featured images)

### 3. FAQ Schema Already Present

The posts already had FAQPage JSON-LD schema embedded as `<script type="application/ld+json">` in the post content. Always check rendered content for `FAQPage` before adding.

### 4. Internal Link Pattern for Blog Posts

For purebrain.ai blog posts, the CTA/footer links use UTM params with `#awakening`. When auditing cross-post links, filter OUT:
- `/?...#awakening` (homepage CTA)
- `/blog/?...` (newsletter subscribe)
- `/ai-partnership-audit/`, `/assessment/` (product pages)

Only count direct slug-to-slug links like `/why-ai-memory-changes-everything/`.

### 5. Raw Content vs Rendered Content

Posts have CSS injected as `<style>` blocks at the start of raw content. The raw content always starts with CSS noise. To find actual post text:

```python
# Skip CSS, find first h2
real_start = content['raw'].find('<h2>')
actual_content = content['raw'][real_start:]
```

Also: raw content uses unencoded chars (apostrophes as `'` not `&#8217;`) so search for the unencoded version when doing string replace.

## Files

- Report: `/home/jared/projects/AI-CIV/aether/exports/seo-quick-fixes-implemented.md`

---

**End of Memory**
