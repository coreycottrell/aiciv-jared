# CF Pages: wp-content/uploads URLs Are Blocked

**Date**: 2026-03-13
**Type**: critical-gotcha
**Impact**: All WordPress CDN image URLs broken on purebrain.ai

---

## Root Cause

purebrain.ai is served by Cloudflare Pages (static HTML in `exports/cf-pages-deploy/`).
When blog posts were exported from WordPress, image `src` and `srcset` attributes pointed to
`https://purebrain.ai/wp-content/uploads/...`.

CF Pages intercepts ALL paths under purebrain.ai and returns the static HTML site, not the
WordPress backend. This means:
- `wp-content/uploads/` images → returns HTML (content-type: text/html) → broken images
- `wp-json/` REST API calls → returns HTML → API unusable
- The WP REST API is completely inaccessible through purebrain.ai

## Fix Pattern

All image references in CF Pages static HTML must use LOCAL paths (relative to the CF Pages deploy root):
- `/blog/[slug]/banner.png` — served directly by CF Pages
- These return `content-type: image/png` correctly

NEVER use `https://purebrain.ai/wp-content/uploads/...` in static HTML files.

## Files Fixed 2026-03-13

1. `exports/cf-pages-deploy/blog/index.html` — wp-block-latest-posts section had WP CDN URLs
2. `exports/cf-pages-deploy/blog-neural-feed-memories/index.html` — rebuilt with local paths
3. All 12 older blog posts — added `<article class="pb-blog-post">` wrapper

## Script Reference

`tools/fix_blog_banner_and_deploy.py` — contains the fix + deploy pattern for blog/index.html
`tools/fix_blog_cfpages_v2.py` — contains the fix pattern for blog-neural-feed-memories + post formatting

## Deployment Notes

- Deploy via: `cd exports/cf-pages-deploy && npx wrangler pages deploy . --project-name=purebrain --branch=main --commit-dirty=true`
- CF_ACCOUNT_ID: d526a3e9498dd167509003004df03290
- CF_API_TOKEN: HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_
- ALWAYS purge CF cache after deploy for affected URLs
- Zone ID: 49400cad1527af716705f6cb8c22bb65

## Going Forward

When publishing new blog posts to purebrain.ai:
1. Banner image must be saved as `exports/cf-pages-deploy/blog/[slug]/banner.png`
2. All HTML image references must use `/blog/[slug]/banner.png` (local path)
3. Never use wp-content/uploads URLs in any CF Pages HTML file
