# Blog Banner Fix — All 3 Problems Resolved

**Date**: 2026-03-18
**Type**: operational + pattern
**Agent**: full-stack-developer

## Problem Summary

Blog banners had 3 distinct issues:

### Problem 1: Distorted Banners on Individual Posts
- Root cause: Nightly job added `width="1920" height="1080"` (or other hardcoded dimensions) to `<img class="pb-post-banner">` tags
- Browser uses HTML attrs to establish aspect ratio before CSS loads → distortion
- Fix: Remove ALL `width="..."` and `height="..."` attributes from pb-post-banner imgs
- Also added `height: auto` to `.pb-post-banner {}` CSS as belt-and-suspenders
- Affected: ALL 28 post index.html files

### Problem 2: Wrong Banner Images for 2 Posts
- `pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value/banner.png` — was showing "pilot succeeding/failing" image (555KB duplicate)
- `why-95-percent-of-ai-pilots-fail/banner.png` — same wrong 555KB image
- Fix: Generated new correct banners with DALL-E 3 HD (1792x1024)
  - Pilot purgatory: dark graveyard of floating dashboard screens stuck at "In Progress"
  - 95% fail: dramatic split showing 95% failures vs 5% success contrast
- Both new banners: ~2.5-2.9MB confirming correct generation

### Problem 3: Card Thumbnail Cropping in Listing Pages
- Root cause: `.wp-block-latest-posts__featured-image` had no explicit height → `object-fit: cover` had nothing to fill
- Fix: Added `height: 220px` to container, changed img to `height: 100%; object-fit: cover; object-position: center top`
- Applied to: `/blog/index.html` listing page

## Bonus Fix: Neural Feed Wrong Extensions
- `/blog-neural-feed-memories/index.html` referenced `banner.png` for 4 posts that only have `banner.jpg`
- Fixed: teach-your-ai, the-context-tax, your-ai-has-no-memory-mine-does, your-next-direct-report-wont-be-human

## Files Changed
- `exports/cf-pages-deploy/blog/*/index.html` — ALL 28 post files (removed hardcoded dims, added height:auto CSS)
- `exports/cf-pages-deploy/blog/pilot-purgatory-*/banner.png` — replaced with new DALL-E generated image
- `exports/cf-pages-deploy/blog/why-95-percent-*/banner.png` — replaced with new DALL-E generated image
- `exports/cf-pages-deploy/blog/index.html` — fixed card thumbnail CSS
- `exports/cf-pages-deploy/blog-neural-feed-memories/index.html` — fixed 4 wrong banner extensions

## Deploy
- Deployed to `purebrain-staging` CF Pages
- CF cache purged for `purebrain.ai` (zone: 49400cad1527af716705f6cb8c22bb65)
- Deployment URL: https://ba7c337b.purebrain-staging.pages.dev

## Patterns for Future
- Never add hardcoded width/height HTML attributes to banner imgs — CSS only
- Check banner file sizes: under 500KB almost always wrong/placeholder
- When nightly job runs, must NOT add dimension attributes to existing pb-post-banner imgs
- DALL-E 3 HD at 1792x1024 produces good 16:9 banners (~2-3MB)
- OpenAI API key is OPENAI_API_KEY in .env (NOT GOOGLE_API_KEY which is commented out)
