# Aether Website Analysis - Price + PayPal Live Update

**Date**: 2026-02-23
**Type**: operational
**Topic**: Netlify site price change ($97 -> $47) + live PayPal integration

## What Was Done

Updated https://aether-website-analysis.netlify.app/ with two changes:
1. Changed price from $97 to $47 across all references
2. Swapped PayPal sandbox client (`sb`) for live client ID from PAYPAL_CLIENT_ID in .env

## Source File Location

`/home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis/index.html`

This is the canonical source. All future edits go here, then redeploy.

## Price References That Were Changed (7 locations)

1. `<meta name="description">` - meta tag text
2. `<meta property="og:description">` - OG tag text
3. Hero subtitle text "for just $47."
4. Form card price tag `<sup>$</sup>47`
5. Success panel order details `$47.00`
6. Pricing section big price `<sup>$</sup>47`
7. CTA button text "Get My Report — $47"
8. PayPal `createOrder` value: `'47.00'`
9. Order record `amount: '47.00'`

## PayPal Integration

- **Before**: `client-id=sb` (sandbox)
- **After**: `client-id=AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI` (live)
- Live client ID is stored as `PAYPAL_CLIENT_ID` in `.env`
- This is the live PayPal associated with support@puremarketing.ai

## Deploy Command

```bash
NETLIFY_TOKEN=$(python3 -c "from dotenv import load_dotenv; import os; load_dotenv('/home/jared/projects/AI-CIV/aether/.env'); print(os.getenv('NETLIFY_AUTH_TOKEN'))")
cd /home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis
npx netlify-cli deploy --prod --dir=. --site=a2c983c3-f430-460d-9db4-f5c393fbf00a --auth=$NETLIFY_TOKEN
```

## Verification

Confirmed via `curl` on live URL - all $47 prices and live PayPal SDK loading correctly.
