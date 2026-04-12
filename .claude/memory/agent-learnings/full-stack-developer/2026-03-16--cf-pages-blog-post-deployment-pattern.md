# CF Pages Blog Post Deployment Pattern
**Date**: 2026-03-16
**Type**: operational
**Topic**: Adding a new blog post to the CF Pages static site

## What Was Done
Deployed "The AI That Knows You Before You Even Speak" (March 15, 2026) to the CF Pages static site.

## Files Created/Modified
1. **New blog post**: `exports/cf-pages-deploy/blog/the-ai-that-knows-you-before-you-even-speak/index.html`
2. **Banner**: `exports/cf-pages-deploy/blog/the-ai-that-knows-you-before-you-even-speak/banner.jpg` (copied from portal_uploads)
3. **Blog index updated**: `exports/cf-pages-deploy/blog/index.html` — new `<li>` inserted as FIRST item in the `<ul class="wp-block-latest-posts__list">` on line 817
4. **Memories page updated**: `exports/cf-pages-deploy/blog-neural-feed-memories/index.html` — new `nfm-card` block inserted before the "March 12, 2026" card

## Key Patterns
- Template lives at: `exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/index.html`
- Blog index posts list is a single `<ul>` tag on line 817 — all `<li>` items are inline, insert new post by prepending to the `<ul>` opening tag match
- Memories page uses `.nfm-card` pattern with `nfm-card-image-wrap`, `nfm-card-body`, `nfm-card-date`, `nfm-card-title`, `nfm-card-cta` structure
- Banner images referenced as relative `banner.jpg` (not absolute path) in the blog post itself
- OG image uses absolute URL: `https://purebrain.ai/blog/[slug]/banner.jpg`
- Microsoft Clarity ID: `viy9bnc56x` — must be in `<head>` of every post
- FAQ section uses `.pb-faq-section` with accordion JS (`pbToggleFaq`)
- Daily Recap block frozen table + live loader from `/blog/daily-recap.json`
- Transparency section at bottom of article

## Source Files
- Blog post markdown: `portal_uploads/from-portal/portal_20260315_162207_the-ai-that-knows-you-before-you-speak-blog-post.md`
- Banner source: `portal_uploads/from-portal/portal_20260315_162207_the-ai-that-knows-you-before-you-speak-blog-post-Newslettersize.jpg`
