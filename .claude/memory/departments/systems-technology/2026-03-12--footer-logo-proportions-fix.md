# Footer Logo Proportions Fix
**Date**: 2026-03-12
**Type**: bug-fix
**Pages Affected**: 7 (pay-test-sandbox-3, pay-test-2, pay-test-awakened, pay-test-partnered, pay-test-unified, insiders, invitation)

---

## Root Cause

The Pure Technology footer logo (side-by-side horizontal logo image) had TWO conflicting CSS definitions for `.footer__logo` in the same `<style>` block:

1. **First definition (inner scoped block)**: `height: 40px; width: 240px;`
   - WRONG: forced 6:1 ratio on a 2:1 image = heavily squished/stretched
2. **Second definition (override)**: `height: 100px; width: auto;`
   - OK aspect ratio but 100px is too tall for a footer logo
   - This was the "winning" rule due to CSS cascade order

Image actual dimensions: 2560x1250px (2.048:1 aspect ratio)
Image URL: `https://purebrain.ai/wp-content/uploads/2026/02/MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png`

## Fix Applied

Changed `.footer__logo` CSS in both definitions to:
```css
.footer__logo {
    height: 36px;
    width: auto;
}
```

Result: 36px tall × ~74px wide, correct 2.048:1 ratio, clean footer size.

## Files Modified

**Source files** (purebrain-site/public):
- `purebrain-site/public/pay-test-sandbox-3/index.html`
- `purebrain-site/public/pay-test-2/index.html`

**Deploy files** (exports/cf-pages-deploy):
- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html`
- `exports/cf-pages-deploy/pay-test-2/index.html`
- `exports/cf-pages-deploy/pay-test-awakened/index.html`
- `exports/cf-pages-deploy/pay-test-partnered/index.html`
- `exports/cf-pages-deploy/pay-test-unified/index.html`
- `exports/cf-pages-deploy/insiders/index.html`

Note: `invitation/index.html` has text-only footer (no image logo) — no fix needed.

## Deployment

```bash
cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy
CLOUDFLARE_API_TOKEN=HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ npx wrangler pages deploy . --project-name=purebrain-staging --commit-dirty=true
```

Deployed to: https://630273fd.purebrain-staging.pages.dev
Production: purebrain.ai (CF Pages auto-routes staging to production)

## Verification

All 6 pages verified live with `height: 36px; width: auto;` after deployment.

## Pattern Learned

When a footer logo image looks squished/stretched, ALWAYS check:
1. Are there multiple `.footer__logo` CSS definitions?
2. Does width have a fixed pixel value while height is different?
3. The LAST definition in the CSS cascade wins

The fix is always: `height: [target]px; width: auto;` to preserve aspect ratio.
