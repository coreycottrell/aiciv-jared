# Blog CTA Hover Fix - All 24 Posts

**Date**: 2026-03-12
**Type**: bug fix + deployment
**Agent**: dept-systems-technology

## Problem

Two hover states broken on all blog post CTA sections at purebrain.ai:
1. "Start Your AI Partnership" orange button - stays orange on hover (should go blue #2a93c1)
2. "subscribe to our newsletter" link text - stays blue on hover (should go white)

## Root Cause Discovery

### Architecture Context
Blog posts on purebrain.ai are served as **static HTML from Cloudflare Pages** (project: `purebrain-staging`), NOT from WordPress. The WordPress security plugin's `wp_head` hook CSS never runs on these pages.

Blog post files are at:
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/{slug}/index.html`

### Why Previous CSS Didn't Work
Previous CSS (`CTA BUTTON HOVER: orange -> blue`) existed in the static files but was insufficient:
- Button has inline `background: linear-gradient(135deg,#f1420b 0%,#d13608 100%)` — needed `background-color` + `background-image` BOTH explicitly set with !important
- Newsletter link has inline `color:#2a93c1 !important` — needed `-webkit-text-fill-color` override too
- Missing `transition` on default state meant no smooth color animation

## Fix Applied

Replaced old CSS block with stronger version in all 24 blog post HTML files:

### Button hover (orange → blue):
```css
.blog-cta-block a[href*="awakening"]:hover {
    background-color: #2a93c1 !important;
    background-image: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 24px rgba(42, 147, 193, 0.5), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
    /* + text-decoration, border-bottom, padding, border-radius all !important */
}
```

### Newsletter link hover (→ white text):
```css
.blog-cta-block p > a[href*="newsletter"]:hover {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    /* + background: transparent, no padding, no border-radius */
}
```

## Files Changed

All 24 files under:
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/*/index.html`

## Deployment

Deployed to CF Pages project `purebrain-staging` via wrangler.
- Run 1: 24 files uploaded (23 blog posts fixed)
- Run 2: 1 file uploaded (last blog post - `your-ai-resets-to-zero-every-morning`)
- Both deployments uploaded to live `purebrain.ai` domain

## Verification

```
curl purebrain.ai/blog/your-ai-resets-to-zero-every-morning/
→ "CTA BUTTON DEFAULT STATE" found in CSS: TRUE
→ "NEWSLETTER SUBSCRIBE LINK HOVER: text goes WHITE" found: TRUE
```

## Key Patterns Learned

1. **CF Pages = static HTML** — WordPress plugin CSS hooks NEVER apply to CF Pages served blog posts
2. **Inline gradient override** — Must set `background-color`, `background-image`, AND `background` shorthand separately with `!important` to reliably override inline `background: linear-gradient(...)` on hover
3. **`-webkit-text-fill-color`** — Required alongside `color` to override inline color in Safari/Chrome
4. **Selector location** — Hover CSS is in the transparency `<style id="pb-transparency-styles">` block injected at end of each blog post (around line 1394)
