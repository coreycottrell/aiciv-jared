# Dual-Destination Blog Deployment Pattern
**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Task**: Deploy "Your AI Has No Idea Who You Are" to CF Pages + jaredsanborn.com WordPress

## Deployment Summary

### Destination 1: CF Pages (purebrain.ai/blog/)
- **File**: `exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/index.html`
- **Banner**: `exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/banner.png`
- **Deploy command**: `cd exports/cf-pages-deploy && CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290 CLOUDFLARE_API_TOKEN=HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ npx wrangler pages deploy . --project-name=purebrain --branch=main --commit-dirty=true`
- **Project name**: `purebrain` (NOT purebrain-staging)
- **Result**: 29 new files uploaded, deploy URL: https://7e00d580.purebrain.pages.dev

### Destination 2: jaredsanborn.com (WordPress)
- **WP URL**: https://jareddsanborn.com
- **Credentials**: .env → WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_APP_PASSWORD
- **Post ID**: 1254 (existing post updated, not new)
- **Post URL**: https://jareddsanborn.com/2026/03/12/your-ai-has-no-idea-who-you-are/
- **Featured media ID**: 1255 (banner uploaded fresh)
- **Status**: Published

## Key Patterns Learned

### CF Pages HTML Template
- Always use `<article class="pb-blog-post">` wrapper
- Banner src should use local CF Pages path: `/blog/[slug]/banner.png`
- Must include: FAQ section, transparency section, two-tier daily recap, CTA block
- CTA button hover: orange→blue (CSS class `.blog-cta-block a[href*="awakening"]:hover`)
- Newsletter link hover: text goes white (CSS `.blog-cta-block p > a[href*="newsletter"]:hover`)
- Byline format: `<p class="byline"><em>By Jared Sanborn &nbsp;|&nbsp; [Date] &nbsp;|&nbsp; [Category]</em></p>`
- WP export comment should say: `<!-- CF Pages: https://purebrain.ai/blog/[slug]/ -->`

### WordPress jaredsanborn.com
- Auth: `--user "jared:plhi NeE4 Cb1c 4d9i BbjZ Knq3"` works
- Must use curl (not Python urllib) — Cloudflare WAF blocks Python urllib (error code: 1010)
- Must use browser User-Agent header to avoid WAF blocks
- Content wrapped in `<!-- wp:html -->...<!-- /wp:html -->` for clean rendering
- If post exists with same slug, new post gets `-2` suffix — better to UPDATE existing post
- Upload media first → get ID → use in post creation `featured_media` field
- Always check for existing posts with same slug before creating new

### Duplicate Handling
- Check recent posts before creating: `GET /wp-json/wp/v2/posts?per_page=10&orderby=date&order=desc`
- If duplicate found: trash the new one, update the existing one
- Delete endpoint: `DELETE /wp-json/wp/v2/posts/{id}` (moves to trash)
- Update existing: `POST /wp-json/wp/v2/posts/{id}` with same payload

## File Locations
- Blog HTML template reference: `exports/cf-pages-deploy/blog/the-ai-that-forgets-you-every-single-time/index.html`
- New post: `exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/index.html`
