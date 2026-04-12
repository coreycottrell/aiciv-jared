# Blog Post Template - 4 Site-Wide Changes Deployment

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Status**: COMPLETE - Committed, ready for CF Pages deployment

---

## What Was Done

Applied 4 site-wide changes to all 24 CF Pages blog posts and the pb-blog-styling WP plugin.

## Architecture Discovery

Blog posts on purebrain.ai are served from **CF Pages static HTML files**, NOT directly from WordPress.
- Each blog post = `/exports/cf-pages-deploy/blog/{slug}/index.html`
- Each file is self-contained with all CSS inlined
- Comment marker: `<!-- Blog Post Styling - injected 2026-03-12 -->`
- The WP plugin (pb-blog-styling.php) is a secondary system for WP-served pages

## Changes Applied (All 24 Posts + WP Plugin)

### Change 1: Blog Content Background → 60% Opacity
- CSS target: `article.pb-blog-post` (CF Pages) / `.post-content` (WP plugin)
- Changed: `rgba(10, 15, 35, 0.55)` → `rgba(10, 15, 35, 0.60)`
- WP plugin updated from 0.43 to 0.60

### Change 2: Background Video Layer
- Video URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/PureResearch.ai-1.mp4`
- Element: `<div class="pb-video-bg-wrap">` with `<video autoplay muted loop playsinline>`
- CSS: `z-index: -3`, `opacity: 0.18`, fixed position, covers viewport
- GIF remains active via `body::before` (GIF is still a good fallback)
- `prefers-reduced-motion: reduce` hides video for accessibility
- WP plugin injects via `wp_body_open` hook

### Change 3: Collapsible FAQ Section
- New format: `<div class="pb-faq-section" id="pb-faq-section">`
- Accordion: `aria-expanded`, `aria-controls`, JS toggle with close-others behavior
- Per-post FAQs: 24 unique FAQ sets, 4-5 questions each, curated from post content
- JSON-LD schema: `FAQPage` with `Question` + `Answer` entities (AEO/GEO compliant)
- Position: between social share buttons and CTA block
- Old WP format (`faq-section pb-faq-section`) was replaced with new collapsible format on 2 posts

### Change 4: Daily Recap Transparency Section
- HTML ID: `pb-transparency-section`
- Shows: Aether authorship, publisher, platform, editorial review status
- Design: Dark panel with left blue border, pulsing dot, stat cards
- Contact links: `jared@puretechnology.nyc` and link to awakening page
- Position: after CTA block, inside article

## Edge Cases Handled

1. **pilot-purgatory**: Old format with no `<article>` tag and no CTA block. FAQ + transparency inserted before `</body>`.
2. **the-ai-trust-gap**: Had old-format FAQ (`faq-section pb-faq-section`). Old format replaced with new collapsible.
3. **your-next-direct-report**: Had old-format FAQ. New FAQ inserted before CTA (old was in different position).

## Files Modified

- `exports/cf-pages-deploy/blog/{24 slugs}/index.html` - All 24 blog posts
- `tools/security/pb-blog-styling/pb-blog-styling.php` - WP plugin v1.1.0 → v1.2.0
- `tools/security/update_blog_posts_4changes.py` - Update script (idempotent)

## Git Commit

`c6573b8a` - "Add 4 site-wide blog post template changes to all 24 CF Pages blog posts"

## Next Step

Push to remote and Cloudflare Pages will auto-deploy. The CF Pages project auto-deploys on git push.

## Verification

24/24 posts verified with:
- [PASS] opacity=True (60%)
- [PASS] video=True (video element + correct URL)
- [PASS] faq=True (id="pb-faq-section" present)
- [PASS] trans=True (pb-transparency-section present)

## Key Pattern

To apply these changes to future blog posts:
```bash
python3 tools/security/update_blog_posts_4changes.py
```
Script is idempotent - safe to re-run. It skips posts where changes are already present.
To add FAQ data for a new post, add an entry to `POST_FAQS` dict in the script.
