# SEO/OG Meta Tag Audit — purebrain.ai
**Date**: 2026-03-13
**Department**: dept-marketing-advertising (CMO)
**Scope**: All CF Pages deploy HTML files

---

## Findings Summary

### Pages with ZERO OG/meta tags (CF Pages served)
- `/why-purebrain/` — PRIMARY target, completely missing
- `/refer/` — missing all tags
- `/refer-and-earn/` — missing all tags
- `/brainiac-mastermind-training/` — missing all tags
- `/blog/` (index) — missing all tags
- All 25 blog posts — missing og:image, most missing descriptions

### Pages with wrong/broken OG tags
- `/` (homepage) — og:image was a GIF (Pure-Brain-Vid-3.gif, 480x270) — bad for social
- `/insiders/` — inheriting wrong homepage title/desc
- `/pay-test-2/` — inheriting wrong homepage title/desc
- `/pay-test-sandbox-3/` — inheriting wrong homepage title/desc
- `/compare/` — had good tags but og:image pointed to wp-content path (CF intercepts)

### Root cause
CF Pages intercepts ALL paths including wp-content/uploads/. WordPress OG images are
served via wp-content paths which return HTML instead of images when accessed through CF.
The correct approach: use purebrain-homepage-og.jpg which IS in cf-pages-deploy under
wp-content/uploads/2026/02/ — so CF Pages serves it correctly.

---

## What Was Fixed

**Script created**: `/home/jared/projects/AI-CIV/aether/tools/fix_og_tags.py`

**35 files fixed**:
- 10 key pages (homepage, why-purebrain, compare, refer, refer-and-earn, insiders, pay-test-2, pay-test-sandbox-3, brainiac-mastermind-training, blog index)
- 25 blog posts (all with local banner.png as og:image, curated descriptions)

**OG Image strategy**:
- Core pages: `purebrain-homepage-og.jpg` (1200x627, confirmed valid, served by CF)
- Blog posts: `/blog/{slug}/banner.png` (each post has its own banner locally)

**Tags injected per page**: og:title, og:description, og:url, og:type, og:site_name,
og:image (with width/height), twitter:card, twitter:site, twitter:title,
twitter:description, twitter:image, meta:description, canonical

---

## Deployment
- CF Pages deploy: uploaded 35 files to purebrain-staging
- CF cache purged: success (zone 49400cad)

---

## Remaining WP-only pages (not in CF Pages — cannot fix here)
- `/blog/` posts served from WordPress directly (not in cf-pages-deploy)
- Need Yoast SEO configuration on WP side for those
- Action: Configure Yoast with proper OG image for every WP-only blog post

---

## Key Learnings
1. Always use absolute URLs for og:image — relative paths fail on social crawlers
2. og:image must be a static file path CF Pages serves directly — NOT wp-content via proxy
3. When multiple og:image tags exist, social crawlers use the FIRST occurrence — inject before WP tags
4. Blog posts benefit most from unique og:image per post (uses local banner.png)
5. `fix_og_tags.py` is idempotent — can be re-run safely, removes old injected block first
