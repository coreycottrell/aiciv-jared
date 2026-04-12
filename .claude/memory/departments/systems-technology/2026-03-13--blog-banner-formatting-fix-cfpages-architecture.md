# Blog Banner Images + Post Formatting Fix — 2026-03-13

## Summary
Fixed two blog issues on purebrain.ai using CF Pages static file editing approach.

**Task 1 (Banners)**: Blog listing page `/blog-neural-feed-memories/` showed placeholder SVGs instead of banner images for all 25 posts. Fixed by replacing `nfm-card-image-placeholder` divs with `<img src="/blog/{slug}/banner.png">` tags directly in the static HTML.

**Task 2 (Formatting)**: 12 older blog posts rendered left-aligned/unstyled. Fixed by wrapping content in `<article class="pb-blog-post">` in each post's static HTML.

---

## CRITICAL ARCHITECTURE LESSON: Two CF Pages Projects

**purebrain.ai is served by `purebrain-staging` project, NOT `purebrain`.**

DNS (Cloudflare Zone `49400cad1527af716705f6cb8c22bb65`):
```
purebrain.ai CNAME -> purebrain-staging.pages.dev
www.purebrain.ai CNAME -> purebrain-staging.pages.dev
```

**Always deploy to `purebrain-staging`:**
```bash
cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy
CF_ACCOUNT_ID=d526a3e9498dd167509003004df03290 \
CLOUDFLARE_API_TOKEN=HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ \
npx wrangler pages deploy . --project-name=purebrain-staging --branch=main --commit-dirty=true
```

The `purebrain` project (without -staging) serves `purebrain.pages.dev` only — NOT the live domain.

---

## Fix Patterns

### Blog Listing Page Banner Images
- File: `exports/cf-pages-deploy/blog-neural-feed-memories/index.html`
- The grid uses `class="nfm-grid"` (NO id attribute) — grep for `class="nfm-grid"`
- Cards use `class="nfm-card"` anchors, each containing `class="nfm-card-image-wrap"` div
- The placeholder SVG is inside `<div class="nfm-card-image-placeholder">...</div>`
- Replace each placeholder div with: `<img src="/blog/{slug}/banner.png" alt="PureBrain Blog" class="nfm-card-banner-img" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block;">`
- `nfm-card-image-wrap` has `aspect-ratio: 16/9; overflow: hidden;` — images fill it naturally
- **Banner files**: Download from `https://purebrain.ai/blog/{slug}/banner.png` if not in local exports folder
- After replacement: exactly 1 `nfm-card-image-placeholder` remains (the CSS class definition, line ~169)

### Blog Post Formatting Wrapper
- Bad posts are missing `<article class="pb-blog-post">` wrapper
- Find content start: after `<!-- INJECTED: Post banner image -->` comment + banner img tag
- Find content end: before Aether footer / `<!-- AETHER` comment block
- Wrap: `<article class="pb-blog-post">\n[content]\n</article>`
- Good post to verify against: `/blog/your-ai-has-no-idea-who-you-are/`
- The 12 bad posts (all published before the wrapper pattern was established):
  - why-95-percent-of-ai-pilots-fail
  - your-next-direct-report-wont-be-human
  - why-ai-memory-changes-everything
  - we-both-wrote-this-post
  - why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time
  - the-ai-trust-gap
  - how-my-human-named-me-and-what-it-meant
  - the-difference-between-using-ai-and-having-an-ai-partner
  - what-i-actually-do-all-day
  - ceo-vs-employee-ai-transformation-gap
  - pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value
  - most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2

---

## WP REST API Is Blocked
- ALL requests to `https://purebrain.ai/wp-json/` return the WordPress homepage HTML
- This is GoDaddy Managed WordPress edge caching — not fixable from this server
- wp-login.php also returns homepage HTML (GoDaddy blocks direct WP admin access)
- **Never** try to fix CF Pages issues via WP REST API — edit static files directly

---

## Deploy + Cache Purge Pattern
```python
# After editing static files:
# 1. Deploy to purebrain-staging
# 2. Purge CF cache for affected URLs

import requests
CF_ZONE_ID = "49400cad1527af716705f6cb8c22bb65"
headers = {
    "X-Auth-Email": "jared@puretechnology.nyc",
    "X-Auth-Key": "251911c00fe74daedaff1133decfc3a00f66c",
    "Content-Type": "application/json",
}
requests.post(
    f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/purge_cache",
    headers=headers,
    json={"files": ["https://purebrain.ai/affected-url/"]}
)
```

---

## Verification Commands
```bash
# Banner images on listing page (should be 25)
curl -s "https://purebrain.ai/blog-neural-feed-memories/" | grep "nfm-card-banner-img" | wc -l

# pb-blog-post wrapper on a bad post (should be 1)
curl -s "https://purebrain.ai/blog/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/" | grep 'class="pb-blog-post"' | wc -l
```

---

## Script
`/home/jared/projects/AI-CIV/aether/tools/fix_blog_cfpages_v2.py` — reference implementation (note: uses wrong project name `purebrain` — update to `purebrain-staging` for future use)
