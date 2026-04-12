# Blog Priority Fixes: OG Image, BlogPosting Schema, Index Rebuild, CSS Extraction

**Date**: 2026-03-21
**Type**: operational + teaching
**Topic**: 5 blog priority fixes - meta, schema, index, CSS, audio

## What Was Done

### Fix 2: OG Image Tags (7 posts)
All 7 posts missing `og:image` now have full OG image block:
```html
<meta property="og:image" content="https://purebrain.ai/blog/{slug}/banner.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:type" content="image/png" />
```
Insertion point: after `og:url` tag (fallback: before `</head>`).

### Fix 3: BlogPosting Schema (29 posts)
29 posts got full JSON-LD BlogPosting schema added. 3 posts already had it (what-i-named-my-ai, why-enterprises-are-betting-on-agentic-ai, why-your-ai-should-have-a-name).

Date mapping: Built from source markdown filenames in `purebrain-site/src/content/blog/` (YYYY-MM-DD--slug.md).
For posts without source .md files, inferred from blogger memory + context.

### Fix 4: Blog Index (11 → 32 posts)
Index uses WordPress `wp-block-latest-posts` format (NOT a custom pb-post-card format).
Each `<li>` has: featured-image div, post-title a, time element, post-excerpt div.
Script: `tools/fix_blog_index.py`
Replaced `<ul class="...wp-block-latest-posts...">` inner content.

### Fix 5: Homepage CSS Extraction
17 inline `<style>` blocks (244KB) extracted to `/style.css` (233KB external).
1 exact duplicate block removed (pb-aether-footer-v470 appeared twice).
Homepage HTML: 451KB → 212KB (53% reduction).
Link tag added: `<link rel="stylesheet" href="/style.css">` after `</title>`.
Script: `tools/extract_homepage_css.py`

### Fix 1: ElevenLabs Audio (3 of 30 posts)
ElevenLabs hit quota after 3 posts. Quota: 100,034 total, 1,663 remaining.
3 audio files generated:
- 52-billion-ai-agents-market-is-not-the-story (8.1MB)
- age-of-ai-agents-next-18-months (16.4MB)
- ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger (13.6MB)
27 posts still need audio - requires quota renewal.
Script: `tools/batch_audio_all.py`

## Key Files
- Fix script (OG + schema): `tools/blog_meta_fixes.py`
- Fix script (index): `tools/fix_blog_index.py`
- Fix script (CSS): `tools/extract_homepage_css.py`
- Audio batch script: `tools/batch_audio_all.py`
- External CSS: `exports/cf-pages-deploy/style.css`
- Blog index: `exports/cf-pages-deploy/blog/index.html`

## Patterns/Learnings

1. **Blog index format is WordPress wp-block-latest-posts** - NOT custom pb-post-card classes.
   The `<ul class="wp-block-latest-posts__list has-dates wp-block-latest-posts">` is the container.

2. **Source markdown date mapping**: `purebrain-site/src/content/blog/YYYY-MM-DD--slug.md`
   filenames are the authoritative date source for ~22 posts.

3. **Posts without source .md**: 10 posts exist only as CF Pages HTML.
   They need HTML text extraction for audio. blog_audio.py strips too aggressively from temp md.
   Better approach: write a direct HTML-to-TTS function that bypasses extract_readable_text().

4. **ElevenLabs quota**: 100K chars/month. Each post averages ~15K chars = ~6-7 posts/100K quota.
   Need ~4-5x quota renewal to cover all 27 remaining posts.

5. **CF Pages token** (CF_PAGES_TOKEN) doesn't have zone management permissions.
   Cannot purge CF zone cache - only pages cache invalidation on deploy.

## Deployment
Deployed to purebrain-staging: https://215c2187.purebrain-staging.pages.dev
