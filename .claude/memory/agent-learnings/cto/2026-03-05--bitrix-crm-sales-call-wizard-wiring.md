# Bitrix CRM Wiring — Sales Call Wizard

**Date**: 2026-03-05
**Type**: operational
**Agent**: cto

## Task
Wire Bitrix24 CRM into the Sales Call Wizard at https://purebrain.ai/sales-playbook/live-call/ (WP page 1283, Elementor canvas).

## What Exists
The wizard at `exports/sales-call-wizard/index.html` already had full Bitrix + GDrive integration code (functions `buildBitrixLeadFields`, `createBitrixLead`, `createGoogleDoc`) — just guarded by `false` flags.

## 4 Config Changes Required
Lines 1648, 1649, 1657, 1659 in index.html:
- `BITRIX_ENABLED`: false → true
- `BITRIX_WEBHOOK_URL`: placeholder → `https://puremarketing.bitrix24.com/rest/1/d1azasrcgghsy27v/`
- `GDRIVE_ENABLED`: false → true
- `GDRIVE_SALES_FOLDER_ID`: empty → `1KetwS3uHPEKJZfwV5XQM1hsW6OOw9JqT`

## Webhook Verification
`GET https://puremarketing.bitrix24.com/rest/1/d1azasrcgghsy27v/crm.lead.fields`
- HTTP 200 OK
- 90+ lead fields returned
- Webhook is live and authenticated

## WordPress Deployment Notes
- Page 1283 uses `elementor_canvas` template
- MUST update `meta._elementor_data` (not `post_content`)
- Use `requests` library (not urllib — Cloudflare 403s urllib)
- Auth: WP user "Aether", app password from PUREBRAIN_WP_APP_PASSWORD in .env
- Clear cache after: `DELETE https://purebrain.ai/wp-json/elementor/v1/cache`

## Data Flow After Wiring
On "Save Call Record":
1. GDrive: POST to `api.purebrain.ai/api/create-sales-doc` → Google Doc in folder `1KetwS3uHPEKJZfwV5XQM1hsW6OOw9JqT`
2. Bitrix: POST to webhook `/crm.lead.add.json` → Lead created with full step notes + Doc URL in COMMENTS
3. PureBrain log: POST to `api.purebrain.ai/api/log-conversation` (always runs as backup)

## Deployment Script
`/home/jared/projects/AI-CIV/aether/tools/do_bitrix_patch_and_deploy.py`
Run: `python3 /home/jared/projects/AI-CIV/aether/tools/do_bitrix_patch_and_deploy.py`
