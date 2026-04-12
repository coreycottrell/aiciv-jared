# CTO Memory: pay-test-2 Live PayPal Clone from sandbox-3
**Date**: 2026-03-10
**Type**: operational
**Topic**: Cloning sandbox-3 (page 1013) → pay-test-2 (page 689) with live PayPal

## What Was Done

Cloned pay-test-sandbox-3 (page 1013) to pay-test-2 (page 689) by replacing
the sandbox PayPal client ID with the live client ID.

## Key Facts

### PayPal Client IDs (from .env)
- **SANDBOX**: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`
- **LIVE**: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`

Both stored in `/home/jared/projects/AI-CIV/aether/.env` as:
- `PAYPAL_SANDBOX_CLIENT_ID`
- `PAYPAL_CLIENT_ID` (the live one)

### Page IDs
- sandbox-3: page 1013 (`/pay-test-sandbox-3/`)
- pay-test-2: page 689 (`/pay-test-2/`)

### Where the Client ID Lives in the HTML
- File: `purebrain-site/public/pay-test-sandbox-3/index.html` line 11451
- Variable: `var PAYPAL_CLIENT_ID = '...';`
- The PayPal SDK URL is built dynamically: `https://www.paypal.com/sdk/js?client-id=` + variable
- No `sandbox.paypal.com` URLs — SDK always points to `www.paypal.com` (good design)
- Only ONE occurrence of the sandbox client ID in the entire file

### WordPress Deployment Pattern
- Pages use `<!-- wp:html -->` wrapper at line 1
- Deploy via `content` field in REST API (NOT `_elementor_data`)
- Template must be `elementor_canvas`
- Auth: user=Aether, password from `PUREBRAIN_WP_APP_PASSWORD` in .env
- Cache clear: `DELETE https://purebrain.ai/wp-json/elementor/v1/cache`

## Deployment Scripts Created
- `/home/jared/projects/AI-CIV/aether/tools/cto_deploy_live_paypal.py` — Python version
- `/home/jared/projects/AI-CIV/aether/tools/cto_deploy_curl.sh` — Shell + Python hybrid

## Steps to Execute
```bash
cd /home/jared/projects/AI-CIV/aether
python3 tools/cto_deploy_live_paypal.py
```

OR:
```bash
bash /home/jared/projects/AI-CIV/aether/tools/cto_deploy_curl.sh
```

## Pattern: Sandbox → Live Promotion
1. Check `.env` for both `PAYPAL_CLIENT_ID` (live) and `PAYPAL_SANDBOX_CLIENT_ID`
2. Local source file: `purebrain-site/public/pay-test-sandbox-3/index.html`
3. Single `sed` or Python `.replace()` call does the job
4. Deploy as `content` field to WordPress (not elementor_data — these pages use raw HTML)
5. Template: `elementor_canvas`
6. Clear Elementor cache after deploy
7. Verify via re-fetch GET with `context=edit`
