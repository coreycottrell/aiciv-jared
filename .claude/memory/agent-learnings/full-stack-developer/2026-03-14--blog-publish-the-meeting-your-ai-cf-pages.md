# Blog Publish: The Meeting Your AI Should Already Know About (CF Pages)

**Date**: 2026-03-14
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: CF Pages blog post deployment - full flow

## Published URLs

- **purebrain.ai**: https://purebrain.ai/blog/the-meeting-your-ai-should-already-know-about/
- **jareddsanborn.com**: https://jareddsanborn.com/2026/03/14/the-meeting-your-ai-should-already-know-about/

## Root Slug Redirect

- `/the-meeting-your-ai-should-already-know-about/` → 301 → `/blog/the-meeting-your-ai-should-already-know-about/`

## Critical Architecture Fact (PERMANENT LOCK)

**purebrain.ai WordPress REST API (/wp-json/) is BLOCKED by Cloudflare WAF.**

ALL requests to `https://purebrain.ai/wp-json/` return homepage HTML (200 status but text/html content type). This includes GET and POST on all endpoints - posts, media, pages, plugins. This is because CF Pages serves everything via the static file deployment and the `/*` catch-all in `_redirects`.

**The CF Pages static deployment IS the purebrain.ai blog publication.**

This was also documented in `publish_your_ai_has_no_idea.py` (2026-03-12 deployment).

## Deployment Flow

1. Build static HTML → `exports/cf-pages-deploy/blog/{slug}/index.html`
2. Copy banner → `exports/cf-pages-deploy/blog/{slug}/banner.png`
3. Add redirect entry to `exports/cf-pages-deploy/_redirects`
4. Deploy via: `CLOUDFLARE_API_TOKEN=CF_PAGES_TOKEN npx wrangler pages deploy exports/cf-pages-deploy --project-name=purebrain-staging --branch=main`
5. Purge CF cache using `CF_GLOBAL_API_KEY` (not CF_PAGES_TOKEN — that token has no zone access)
6. Publish to jareddsanborn.com WP API (works fine)

## Tokens

- **CF_PAGES_TOKEN** (in .env): Used for wrangler pages deploy
- **CF_GLOBAL_API_KEY** (in .env): Used for cache purge (zone API access)
- Zone ID for purebrain.ai: `49400cad1527af716705f6cb8c22bb65`

## JDS Publish Details

- Post ID: 1260
- Media ID: 1259
- Categories: AI Insights (9), AI Partnership (22)
- Auth: user=jared, WORDPRESS_APP_PASSWORD from .env

Note: A duplicate post (ID 1262, slug -2) was created by running the script twice. Deleted via `DELETE /wp-json/wp/v2/posts/1262?force=true`.

## CF Pages HTML Format

- Full standalone HTML with CSS, nav, banner img, pb-blog-post article
- CSS extracted from reference: `exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/index.html`
- Includes: FAQ accordion, transparency block, CTA block, daily recap section
- Script reference: `tools/publish_the_meeting_your_ai.py`

## Verification (All Pass)

- [x] HTTP 200 on purebrain.ai CF Pages URL
- [x] `pb-blog-post` wrapper present
- [x] Title present
- [x] Briefing Tax section present
- [x] Banner referenced
- [x] FAQ section present
- [x] CTA block present
- [x] Root slug 301 redirect working
- [x] JDS post 200
- [x] CF cache purged

---

**End of Memory**
