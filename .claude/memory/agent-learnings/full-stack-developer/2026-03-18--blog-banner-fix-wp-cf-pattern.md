---
date: 2026-03-18
agent: full-stack-developer
type: teaching
topic: Blog banner fix - WP featured images via CF Pages
---

# Blog Banner Fix: WordPress Featured Images via CF Pages

## Context
All blog posts on purebrain.ai are now served from CF Pages (not WordPress directly). The WordPress REST API is completely blocked by Cloudflare - all requests to /wp-json/ return the CF Pages homepage HTML.

## Key Data Sources

**For post -> featured_media_id mapping:**
`/home/jared/projects/AI-CIV/aether/exports/purebrain-site-repo/data/posts.json`
- Has `featured_media` field for each post
- Was exported when WP API was accessible

**For media_id -> image URL mapping:**
`/home/jared/projects/AI-CIV/aether/exports/purebrain-site-repo/assets/media-manifest.json`
- Has full URLs including `sizes.full` for original size
- 86 media items as of export date

**Local WP image mirror:**
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/wp-content/uploads/`
- Mirrors the actual WP uploads directory
- Use this to copy images locally without downloading

## CF Access Pattern
- wp-content/uploads direct image URLs ARE accessible (return image/jpeg, image/png etc)
- /wp-json/* is BLOCKED - returns HTML homepage
- Cannot use WP REST API through CF at all

## Banner Fix Pattern

1. Load posts.json to get slug -> featured_media_id
2. Load media-manifest.json to get media_id -> source_url
3. Find image in local WP mirror at: exports/cf-pages-deploy/wp-content/uploads/YYYY/MM/filename
4. MD5 compare with current banner - only copy if different
5. If extension changes (.png -> .jpg), update HTML references (3 places in each post HTML: img src, og:image, twitter:image)
6. Also update og:image:type (image/png -> image/jpeg)
7. Update blog/index.html listing page references
8. Update blog-neural-feed-memories/index.html references
9. Remove old wrong-extension banner files

## Posts Fixed in this Session
- 52-billion-ai-agents-market-is-not-the-story: banner.png -> banner.jpg (correct WP featured image)
- most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2: banner.png -> banner.jpg (Enterprise-ready.jpg)
- the-ai-trust-gap: banner.png -> banner.jpg (trust-gap-blog-banner-jared.jpg)
- why-95-percent-of-ai-pilots-fail: banner.png updated to correct WP version

## Newer Posts (not in posts.json cache)
For posts published after the purebrain-site-repo export, use locally generated banners:
- exports/overnight-content/ - prompting-is-dead-banner.png
- exports/overnight-blog/ - the-ai-that-knows-you-before-you-speak-banner.png
- exports/blog-images/ - why-enterprises, why-your-ai-should-have-a-name
- exports/graphics/ - what-i-named-my-ai

## Deployment
```bash
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
```

## Cache Purge
Use global API key (not CF_PAGES_TOKEN) to get zone ID and purge:
```python
CF_EMAIL="jared@puretechnology.nyc"
CF_GLOBAL_KEY = from .env CF_GLOBAL_API_KEY
# Get zone: GET /zones?name=purebrain.ai with X-Auth-Email/X-Auth-Key
# Purge: POST /zones/{id}/purge_cache with {"purge_everything":true}
```
Zone ID for purebrain.ai: 49400cad1527af716705f6cb8c22bb65
