# Blog Transparency + CTA Hover Fix — CF Pages All 24 Posts

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Status**: DEPLOYED AND VERIFIED

## Problem 1: Video Background Not Visible Through Blog Posts

### Root Cause
The blog static HTML files (CF Pages) had `html, body { background: #0a0a0f !important; }` as a COMBINED rule.
The video element sits at `z-index: -3` with `position: fixed`, but the opaque `body` background
blocked it entirely. The `article.pb-blog-post` was correctly set to `rgba(10, 15, 35, 0.40)` (semi-transparent)
but the opaque body behind it meant nothing could show through.

### Fix
Split the combined `html, body` rule into two separate rules:
- `html { background: #0a0a0f !important; }` — keeps dark background (prevents white flash, no orange leak)
- `body { background: transparent !important; }` — lets video at z-index: -3 show through body

This is analogous to the WordPress plugin fix done in v4.7.5 (2026-03-01), but for the static CF Pages files.

### Key Architecture
```
z-index stack (blog posts):
  z-index: -3 → .pb-video-bg-wrap (video, position: fixed)
  z-index: -2 → body::before (GIF overlay, on WP) OR not present (CF Pages)
  z-index: -1 → rgba dark overlay
  z-index:  1 → article.pb-blog-post (rgba(10,15,35,0.40))

html: dark (#0a0a0f) — provides fallback, prevents light bleed
body: transparent — video at -3 shows through
```

## Problem 2: CTA Button "Awaken Your AI Partner Today" Breaking on Hover

### Root Cause
`article.pb-blog-post a:hover` is a higher-specificity rule than `.pb-recap-live-cta:hover`.
The article a:hover rule applies `background: #f1420b` and `padding: 0 3px` to ALL links inside
the article container — including the CTA button. This caused:
- Orange background instead of blue on hover
- Visual shrink/resize because padding changed from `10px 24px` to `0 3px`
- Button looked broken, not blue

Specificity breakdown:
- `article.pb-blog-post a:hover` = element + class + element = higher
- `.pb-recap-live-cta:hover` = just class = lower

### Fix
Added two higher-specificity overrides AFTER the existing CTA hover block:

```css
/* CTA button specificity override — beats article.pb-blog-post a:hover */
article.pb-blog-post .pb-recap-live-cta:hover {
    background: #2a93c1 !important;
    box-shadow: 0 4px 16px rgba(42, 147, 193, 0.4) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    transform: none !important;
    padding: 10px 24px !important;
    border-bottom: none !important;
    border-radius: 7px !important;
}
/* CTA button base specificity override — beats article.pb-blog-post a */
article.pb-blog-post .pb-recap-live-cta {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-bottom: none !important;
    text-decoration: none !important;
}
```

The `!important` flags plus the higher specificity (`article.pb-blog-post .class` vs just `.class`)
ensures the CTA renders correctly with blue hover regardless of the general article link rules.

## Deployment

- Fix applied to all 24 CF Pages blog posts via Python script
- Script: `/home/jared/projects/AI-CIV/aether/tools/fix_blog_transparency_cta.py`
- Deployed via: `CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy . --project-name purebrain-staging --branch main --commit-dirty=true`
- CF Pages project: `purebrain-staging` (serves purebrain.ai + www.purebrain.ai)

## Verification (CONFIRMED LIVE)

```
curl -s -H "Cache-Control: no-cache" "https://purebrain.ai/blog/the-ai-trust-gap/" | grep 'transparent !important'
→ background: transparent !important  ✓

curl -s -H "Cache-Control: no-cache" "https://purebrain.ai/blog/the-ai-trust-gap/" | grep 'article.pb-blog-post .pb-recap-live-cta:hover'
→ article.pb-blog-post .pb-recap-live-cta:hover  ✓

curl -s -H "Cache-Control: no-cache" "https://purebrain.ai/blog/the-ai-trust-gap/" | grep 'background: #2a93c1 !important'
→ background: #2a93c1 !important  ✓
```

Second post (your-next-direct-report-wont-be-human) also confirmed. All 24 fixed.

## Note on CF Cache
`curl -s purebrain.ai/blog/...` without Cache-Control header may return CDN cached version.
Use `-H "Cache-Control: no-cache"` to bypass and confirm live content from Pages edge.

## IMPORTANT: Future Blog Template Updates
When updating the blog post HTML template:
1. Keep `html` and `body` as SEPARATE rules — NEVER combine as `html, body { background: ... }`
2. Always include the `article.pb-blog-post .pb-recap-live-cta:hover` override block
3. The script `tools/fix_blog_transparency_cta.py` can re-apply these fixes if a template reset overwrites them
