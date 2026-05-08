# Future-dated blog posts accidentally live — archival procedure

**Date**: 2026-04-14
**Type**: operational + teaching
**Tags**: cf-pages, blog, deploy, chy-sync, cache-purge

## Problem
Two posts dated Apr 18 + Apr 19, 2026 went live while today is Apr 14.
- `the-200-month-ai-stack-that-outperforms-enterprise-solutions`
- `54-percent-ceos-ai-tearing-company-apart`

## Root Cause
1. Blog `index.html` has posts hardcoded as `<li>` entries — no date-gate filter.
2. `blog-neural-feed-memories/index.html` also lists them as `<a class="nfm-card">`.
3. Posts existed in Chy's staging (`aiciv@37.27.237.109:/home/aiciv/shared/cf-pages-deploy/`). `pre-deploy-sync.sh` rsyncs with `--update` — Chy's newer mtime OVERWRITES local archival.
4. No server-side date check anywhere.

## Fix Pattern (works)
1. `mkdir blog/_archived/` locally AND on Chy (`ssh -p 2213 aiciv@37.27.237.109`).
2. Regex-remove `<li>...slug...</li>` AND `<a href=".../slug/" class="nfm-card">...</a>` from both indices.
3. Add entries to `exports/cf-pages-deploy/_redirects` (302 to /blog/).
4. `cf-deploy.py --delete` to remove from manifest — **insufficient alone**, CF Pages may still serve.
5. **Working fix**: deploy stub `index.html` with `<meta http-equiv="refresh" content="0; url=/blog/">` + `<meta name="robots" content="noindex">` at the old slugs. Guaranteed redirect.
6. CF cache purge via zone API (zone=49400cad1527af716705f6cb8c22bb65).

## Gotcha
`cf-deploy.py --delete` removes from manifest but CF Pages directory routing may still serve. Always follow up with stub deploy for guaranteed URL control.

## Banner Brand Violation
Banners were 1792x1024 — below 2400x1260 minimum per `feedback_all_images_2k_quality_minimum.md`. Per `feedback_image_quality_sop_enforcement.md` they should be FLUX Pro + Oswald Bold + PIL, designed by `3d-design-specialist`. Source preserved in `blog/_archived/` for re-design.

## Preventive Fix (RECOMMEND DEPLOY)
Add server-side date gate:
- Option A: Cron `date-gate.py` on Chy's server pre-rsync — mv any `index.html` with `datetime` attribute > today() into `_scheduled/`.
- Option B: CF Pages Function on `/blog/[slug]/` that reads meta dateline and 404s if future.
- Option C: Add a nightly guard similar to onboarding-spec guard in `feedback_investor_gift_pages_frozen_constitutional.md` that alerts on any future-dated `datetime="2026-XX-XX"` found in deployed HTML.

Route to ptt-fullstack to implement Option C.
