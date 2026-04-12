# Homepage Hero Gap Fix

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Type**: gotcha + fix
**Status**: DEPLOYED AND VERIFIED LIVE

---

## Symptom

purebrain.ai homepage had:
- Massive empty gap above the brain image
- Brain image appearing too large and pushed down
- Content not centered vertically in the hero viewport
- Not matching pay-test-2 which looked correct

## Root Cause

Two CSS properties in the `.hero` section of `exports/cf-pages-deploy/index.html` were wrong:

**BROKEN (homepage):**
```css
.hero {
    align-items: flex-start;   /* pushed content to TOP of flex container */
    padding: 80px 24px 60px;   /* 80px top padding added to the gap */
}
```

**CORRECT (pay-test-2):**
```css
.hero {
    align-items: center;   /* centers content vertically in 100vh */
    padding: 60px 24px;    /* compact, balanced padding */
}
```

The combination of `align-items: flex-start` with `min-height: 100vh` meant the brain/content was
anchored to the top of a full-viewport-height flex container, leaving the entire bottom half empty.
The 80px top padding added further push.

## Fix Applied

Changed in `exports/cf-pages-deploy/index.html`:
- `align-items: flex-start` → `align-items: center`
- `padding: 80px 24px 60px` → `padding: 60px 24px`

## Deploy Method

```bash
CF_TOKEN=$(grep "^CF_PAGES_TOKEN=" .env | cut -d'=' -f2)
cd exports/cf-pages-deploy
CLOUDFLARE_API_TOKEN="$CF_TOKEN" npx wrangler pages deploy . --project-name purebrain-staging --branch main --commit-dirty=true
```

NOTE: Do NOT use `source .env` — the .env file has non-bash lines that cause errors.
Extract credentials with grep/cut instead.

## Verification

```bash
curl -s -H "Cache-Control: no-cache" "https://purebrain.ai/" | grep -o "align-items: flex-start"
# Returns nothing = PASS

curl -s -H "Cache-Control: no-cache" "https://purebrain.ai/" | grep -o "padding: 60px 24px"
# Returns "padding: 60px 24px" = PASS
```

## What Was NOT Changed

- Chatbox behavior: untouched
- Waitlist/pricing flow: untouched
- Video background system: untouched
- Hero HTML structure: untouched
- All other CSS: untouched

## Pattern Note

When the homepage breaks and pay-test-2 looks correct → diff the `.hero` CSS section first.
The homepage occasionally gets experimental CSS applied that breaks the base layout.
pay-test-2 is the stable reference for how the hero should look.
