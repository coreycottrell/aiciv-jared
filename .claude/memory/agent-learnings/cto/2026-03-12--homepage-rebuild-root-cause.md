# Homepage Rebuild: Root Cause Analysis & Fix Architecture

**Date**: 2026-03-12
**Type**: operational + teaching
**Topic**: Why pay-test-2 works and homepage breaks - CSS merge fix

## Root Cause: Dual HTML Document Structure

The `exports/cf-pages-deploy/index.html` homepage file has a TWO-DOCUMENT problem:
- Lines 1-11: Minimal HTML5 wrapper (`<!DOCTYPE html><html><head>...</head><body style="background:#080a12">`)
- Line 12 onward: Embedded WP-export with its own complete HTML document

The browser renders the OUTER document (lines 1-11) and treats the inner WP-export HTML
as body content. The outer `<body>` doesn't have `page-id-11` or `home` class, so the
nuclear anti-orange-flash CSS Layer 4 (which makes body transparent for video) doesn't fire.

pay-test-2 works because it has a SINGLE document structure: the full WP-export directly.

## The CSS Version Gap

pay-test-2 has:
- `pb-magic-cursor-body-fix` v4.8.0 (empty placeholder comment)
- `pb-video-handler-css` v1.3.0 (hides living-background unconditionally on mobile)
- `cf-pages-flash-fix` at top of `<head>` (kills orange flash early)

Homepage has:
- `pb-magic-cursor-body-fix` v4.9.0 NUCLEAR (multi-layer body bg fix)
- `pb-video-handler-css` v1.4.0 + v1.5.0 (iOS video fallback, only hides when playing)
- NO `cf-pages-flash-fix` (removed/missing)

## The Fix: Merge Strategy

Start with pay-test-2 as the base (single document structure = working video hero).
Apply two CSS upgrades from the homepage:
1. Replace `pb-magic-cursor-body-fix` v4.8.0 → v4.9.0 nuclear (handles video page transparency)
2. Replace `pb-video-handler-css` v1.3.0 → v1.4.0/v1.5.0 (iOS improvements)
3. Update title/meta for homepage SEO

The resulting file is identical to pay-test-2 in structure (so it works) but has the
latest CSS fixes (so video and mobile display correctly).

## Build Script

`/home/jared/projects/AI-CIV/aether/tools/build_homepage_test.py`

Execution:
```bash
cd /home/jared/projects/AI-CIV/aether
python3 tools/build_homepage_test.py
```

Output: `exports/cf-pages-deploy/homepage-test/index.html`

## Deploy Command

```bash
cd /home/jared/projects/AI-CIV/aether
CLOUDFLARE_API_TOKEN="HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_" \
CLOUDFLARE_ACCOUNT_ID="d526a3e9498dd167509003004df03290" \
npx wrangler pages deploy exports/cf-pages-deploy \
  --project-name=purebrain-staging \
  --branch=main \
  --commit-dirty=true
```

## Key Lesson for Future

When doing CF Pages static exports, always use pay-test-2 as the template because:
1. It has the `cf-pages-flash-fix` early in `<head>`
2. It's a single document (not embedded)
3. The body classes (`page-id-689`) work correctly for CSS targeting

When CSS versions diverge between pages, check:
- Does the body have the right class for CSS targeting?
- Is the `cf-pages-flash-fix` present at the top?
- Is the file a single document or an embedded document?
