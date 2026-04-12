# Bitrix24 CRM Integration — Sales Call Wizard

**Date**: 2026-03-05
**Task**: Add Bitrix24 CRM + Google Drive doc creation to Sales Call Wizard (WP page 1283)
**Status**: Built, NOT deployed (waiting on Jared's Bitrix credentials)

## What Was Built

### 1. Wizard updated: `exports/sales-call-wizard/index.html`
Three new config flags at the top of the JS block (line ~1640):
- `BITRIX_ENABLED` (bool, default false) — activates Bitrix webhook call
- `BITRIX_WEBHOOK_URL` (string) — Bitrix24 inbound webhook URL
- `GDRIVE_ENABLED` (bool, default false) — activates Google Doc creation
- `GDRIVE_API_URL` — points to `api.purebrain.ai/api/create-sales-doc` (backend needed)
- `GDRIVE_SALES_FOLDER_ID` — Google Drive folder ID for filed call docs

Three new functions:
- `buildBitrixLeadFields(data, googleDocUrl)` — maps wizard data to Bitrix CRM fields
- `createBitrixLead(data, googleDocUrl)` — POST to Bitrix webhook, returns lead ID
- `createGoogleDoc(data)` — POST to backend proxy, returns Google Doc URL

`submitCallData()` overhauled to run async pipeline:
1. Create Google Doc (if GDRIVE_ENABLED)
2. Create Bitrix lead with doc URL in COMMENTS (if BITRIX_ENABLED)
3. Always log to `api.purebrain.ai/api/log-conversation` as backup

### 2. Setup guide: `exports/sales-call-wizard/bitrix-setup-guide.md`
Full instructions for Jared to:
- Create Bitrix24 account + inbound webhook
- Get webhook URL format: `https://[domain].bitrix24.com/rest/[user_id]/[webhook_code]/`
- Activate integration by flipping config flags
- Set up Google Drive folder and backend endpoint

## Bitrix24 API Pattern
```javascript
// Webhook URL format
const url = BITRIX_WEBHOOK_URL.replace(/\/+$/, '') + '/crm.lead.add.json';

// EMAIL/PHONE are multifield arrays
fields.EMAIL = [{ VALUE: email, VALUE_TYPE: 'WORK' }];

// Lead fields used: TITLE, NAME, LAST_NAME, COMPANY_TITLE, POST, EMAIL, STATUS_ID, SOURCE_ID, COMMENTS
```

## Google Drive Pattern
- Browser calls backend proxy (NOT Google API directly — credentials must stay server-side)
- Backend uses `tools/gdrive_manager.py` pattern with OAuth token
- Returns `{ docUrl, docId }`

## Activation Checklist for Jared
1. Provide Bitrix24 webhook URL
2. ST# sets `BITRIX_ENABLED = true` + pastes URL
3. ST# deploys to WP page 1283
4. Build `api.purebrain.ai/api/create-sales-doc` endpoint (full-stack-developer)
5. Set `GDRIVE_ENABLED = true` + folder ID

## DO NOT Deploy Until
- Bitrix credentials provided AND tested locally
- Page 1283 deployment should use existing `deploy.sh` / `wp_deploy.py`
