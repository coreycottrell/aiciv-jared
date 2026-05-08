# 2026-05-05 -- Nightly SEO: og:image, canonical, description shipping

**Type**: operational
**Agent**: seo-specialist
**BOOP**: nightly-site-improvement (autonomous)

## What Shipped

13 sitemap-indexed pages corrected to staging (deploy `51e8ed48.purebrain-staging.pages.dev`):

### Group A: Replaced wp-content og:image / twitter:image with canonical /og-image.png (4 pages, 15 meta tag replacements)
- `/why-purebrain/` (2 refs replaced)
- `/compare/` (6 refs replaced — had 3 duplicate sets from WordPress yoast export)
- `/refer-and-earn/` (2 refs)
- `/pure-brain-agentic-ai-partner/` (5 refs)

### Group B: Injected missing og:image, canonical, description (9 pages)
- `/about-aether/`, `/get-started/`, `/partners/`, `/ai-tool-stack-calculator/`,
  `/ai-readiness-assessment/`, `/governance/`, `/developers/`, `/cost-comparison/`,
  `/mission-vision-values/`

All injections placed immediately after `<head>` tag, marked with comment
`<!-- SEO nightly: og:image / canonical / description added 2026-05-05 -->`.

## Why This Moves the Needle

- **Social/AI preview now works** on these pages (broken wp-content paths returned 404
  on social link unfurls, killing CTR from LinkedIn/Twitter shares)
- **Canonical URLs prevent duplicate content** signals (pages with no canonical were
  letting query-string variations dilute ranking)
- **Meta descriptions filled** so SERP snippets aren't auto-generated badly
- All using `https://purebrain.ai/og-image.png` (53KB, lives at deploy root, returns 200)

## What Was Skipped (Constitutional)

- `/awakened/`, `/partnered/`, `/unified/`, `/insiders/` — payment pages with wp-content
  og:image still broken. Need payment guard analysis before touching. **Worth fixing
  next** — they're high-traffic conversion pages and currently break social previews.
- Investor codes/gift pages — FROZEN
- Did NOT touch design/copy/layout

## Files Changed

13 index.html files in `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/`.
Backup at `/tmp/seo-backup-2026-05-05/` (kept for rollback).

Helper script: `/tmp/seo_nightly_fix.py` (idempotent — safe to re-run; uses regex
that only targets meta tags with og:image or twitter:image properties).

## Worth Jared's Review Tomorrow (LARGER)

Payment page og:image fix (`/awakened/`, `/partnered/`, `/unified/`, `/insiders/`)
- ALL still have broken wp-content `Pure-Brain-Vid-3.gif` or
  `cropped-cropped-MA1.BI...png` references
- Social shares of these pages currently show no preview image
- These ARE the pages people land on from referrals → conversion impact
- Change is metadata-only (no payment logic touched) BUT payment guard rule
  requires explicit signoff. Recommend running these through a payment-focused
  diff review before deploy to staging.

## Verification

```
curl -s "https://51e8ed48.purebrain-staging.pages.dev/why-purebrain/" \
  | grep og:image
# => <meta property="og:image" content="https://purebrain.ai/og-image.png" />

curl -s -o /dev/null -w "%{http_code}\n" \
  "https://51e8ed48.purebrain-staging.pages.dev/og-image.png"
# => 200
```

Deploy ID: `51e8ed48-c79f-445f-9dc7-c74b0c5de69a`
Staging: `https://51e8ed48.purebrain-staging.pages.dev`
Production: NOT pushed (BOOP scope = staging only)
