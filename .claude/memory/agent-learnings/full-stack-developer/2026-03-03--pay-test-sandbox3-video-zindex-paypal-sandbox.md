# pay-test-sandbox-3: Video Z-Index Fix + PayPal Sandbox Fix

**Date**: 2026-03-03
**Page**: https://purebrain.ai/pay-test-sandbox-3/ (WP Page ID: 1232)
**Type**: bug-fix, paypal-sandbox

---

## What Was Fixed

### Fix 1: Brain Video Hidden Behind Body Background

**Root cause**: The page HTML contained:
```css
body {
    font-family: var(--font-body);
    background: var(--black);  /* #000000 - SOLID BLACK */
    ...
}
```

The `.video-background` div had `z-index: -1` (position: fixed). A solid body background at z-index 0 paints OVER anything at z-index -1, hiding the video completely.

**Fix applied**: Changed `background: var(--black)` to `background: transparent` in the body CSS rule inside the page HTML.

**Pattern learned**: When a fixed-position video background is at z-index: -1, the body's own background-color must be transparent (or the body must not have a background). The video at z-index: -1 is painted behind the browser stacking context of the body element's background fill.

### Fix 2: PayPal Live URLs Replaced with Sandbox

**Live URLs found**:
- Client ID: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
- SDK: `https://www.paypal.com/sdk/js`
- Form action: `https://www.paypal.com/cgi-bin/webscr`

**Replaced with sandbox**:
- Client ID: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`
- SDK: `https://www.sandbox.paypal.com/sdk/js`
- Form action: `https://www.sandbox.paypal.com/cgi-bin/webscr`

**Credential source**: `/home/jared/projects/AI-CIV/aether/.env` (PAYPAL_SANDBOX_CLIENT_ID)

---

## Deployment Pattern

Page 1232 is an Elementor page with a single HTML widget (id: `292c72a`) that contains the ENTIRE page as a self-contained HTML document (DOCTYPE, head, body). This is unusual — the HTML widget IS the whole page.

```bash
# Deploy: PATCH the _elementor_data meta field
AUTH=$(echo -n "Aether:APP_PASSWORD" | base64 -w 0)
curl -X PATCH "https://purebrain.ai/wp-json/wp/v2/pages/1232" \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  --data @/tmp/payload.json

# MUST clear Elementor cache after:
curl -X DELETE "https://purebrain.ai/wp-json/elementor/v1/cache" \
  -H "Authorization: Basic $AUTH"
```

---

## Important Notes

- The HTML content in widget `292c72a` is 438k chars — the entire page
- `developer.paypal.com` references are documentation links — do NOT change those
- `www.paypalobjects.com` is CDN for PayPal button images — NOT a payment URL, do NOT change
- After Elementor cache clear, HTTP 200 = success (empty body is expected)
- `context=edit` is REQUIRED when GETting to see `_elementor_data` in meta
