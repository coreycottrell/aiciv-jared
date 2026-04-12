# Bitrix24 CRM Integration — Setup Guide
## Sales Call Wizard (purebrain.ai/sales-playbook/live-call/)

**Status**: Code is built and merged into the wizard. Waiting on credentials below to go live.

---

## What Gets Built Once You Activate This

When a sales rep clicks "Complete & Save Call" in the wizard:

1. **Google Doc created** — Full call record with notes from all 8 steps, timestamped, filed in your Sales Calls folder in Google Drive
2. **Bitrix24 lead created** — Contact info, company, outcome, and full call notes pushed as a new CRM lead
3. **Google Doc URL embedded in the Bitrix lead** — So anyone in Bitrix can click through to the full call transcript
4. **PureBrain log saved** — Always fires as a backup record

---

## Step 1: Set Up Your Bitrix24 Account

If you don't have a Bitrix24 account yet:
1. Go to [bitrix24.com](https://www.bitrix24.com) and sign up for a free or paid account
2. Choose a subdomain — e.g. `puretechnology.bitrix24.com`
3. Complete initial setup

If you already have an account, skip to Step 2.

---

## Step 2: Create a Bitrix24 Inbound Webhook

This is the key credential. An inbound webhook gives the wizard permission to create CRM leads.

1. Log in to your Bitrix24 account
2. Go to: **Applications** (left sidebar) → **Integrations** → **Inbound webhook**
   - Direct URL: `https://YOUR-DOMAIN.bitrix24.com/devops/edit/connector/inbound`
3. Click **"Add webhook"**
4. Under **Permissions**, check the box for **crm** (this allows lead creation)
5. Click **Save**
6. Copy the webhook URL — it looks like:
   ```
   https://puretechnology.bitrix24.com/rest/1/abc123xyz456def/
   ```
   Keep this private — treat it like a password.

---

## Step 3: Activate in the Wizard

Open the wizard HTML file:
```
/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html
```

Find the CONFIG section near line 1640 and make these two changes:

**Change 1:** Set the webhook URL:
```javascript
// BEFORE:
const BITRIX_WEBHOOK_URL = 'https://YOUR-DOMAIN.bitrix24.com/rest/USER_ID/WEBHOOK_CODE';

// AFTER (your actual URL):
const BITRIX_WEBHOOK_URL = 'https://puretechnology.bitrix24.com/rest/1/abc123xyz456def';
```

**Change 2:** Enable Bitrix:
```javascript
// BEFORE:
const BITRIX_ENABLED = false;

// AFTER:
const BITRIX_ENABLED = true;
```

Then redeploy the wizard to WordPress (page 1283) using the existing deploy scripts.

---

## Step 4: Set Up Google Drive Integration

This requires a backend endpoint at `api.purebrain.ai/api/create-sales-doc`. This is a server-side call (not browser-side) because Google Docs API requires OAuth credentials that should never be in the browser.

### What the backend endpoint receives (POST JSON):
```json
{
  "title": "Acme Corp — Sales Call — 3/5/2026",
  "prospectName": "Jane Smith",
  "prospectEmail": "jane@acme.com",
  "prospectCompany": "Acme Corp",
  "prospectRole": "CEO",
  "outcome": "closed",
  "duration": "42:17",
  "timestamp": "2026-03-05T14:30:00.000Z",
  "stepsVisited": [1, 2, 3, 4, 5, 6, 7, 8],
  "steps": [
    { "label": "Opening & Prospect Info", "notes": "Great rapport. Warm intro from Corey..." },
    { "label": "Problem & Pain Discovery", "notes": "Currently using ChatGPT but no memory..." }
  ],
  "folderId": "YOUR_GOOGLE_DRIVE_FOLDER_ID"
}
```

### What the backend must return:
```json
{
  "docUrl": "https://docs.google.com/document/d/DOCUMENT_ID/edit",
  "docId": "DOCUMENT_ID"
}
```

### Google Drive Folder Setup:
1. Create a folder in Google Drive called **"Sales Calls"** (or use an existing folder)
2. Get the folder ID from the URL: `https://drive.google.com/drive/folders/THIS_IS_THE_ID`
3. Paste the folder ID into the wizard config:
   ```javascript
   const GDRIVE_SALES_FOLDER_ID = 'PASTE_FOLDER_ID_HERE';
   ```

### Enable Google Drive after backend is live:
```javascript
const GDRIVE_ENABLED = true;
```

---

## Step 5: Test the Integration

### Test Bitrix only (Phase 1 — recommended first):
1. Set `BITRIX_ENABLED = true` with your webhook URL
2. Keep `GDRIVE_ENABLED = false`
3. Open the wizard locally (or deploy to WP staging)
4. Fill in a test call with:
   - Prospect Name: Test User
   - Email: test@example.com
   - Company: Test Company
   - Outcome: Follow-Up Scheduled
5. Click "Complete & Save Call" → "Save Call Record"
6. Check your Bitrix24 CRM → Leads — a new lead should appear within seconds
7. Confirm the lead contains the call notes in the Comments field

### Verify Bitrix lead looks correct:
- Lead title: `Test Company — Sales Call — [today's date]`
- Contact name: Test User
- Company: Test Company
- Email: test@example.com
- Comments: Full call notes block + "OUTCOME: Follow-Up Scheduled"

---

## What Data Goes Into Bitrix

| Bitrix Field | Source |
|---|---|
| TITLE | "[Company] — Sales Call — [Date]" |
| NAME | First name (parsed from full name) |
| LAST_NAME | Last name (parsed from full name) |
| COMPANY_TITLE | Company name from wizard |
| POST | Role/title from wizard |
| EMAIL | Email from modal (WORK type) |
| STATUS_ID | "NEW" (always starts as new lead) |
| SOURCE_ID | "CALL" |
| COMMENTS | Full notes from all 8 steps + Google Doc URL |
| OPENED | "Y" (visible to all users) |

---

## Credentials Summary — What Jared Needs to Provide

| Item | Where to Paste | Status |
|---|---|---|
| Bitrix24 subdomain | `BITRIX_WEBHOOK_URL` in wizard config | Needed |
| Bitrix24 webhook code | `BITRIX_WEBHOOK_URL` in wizard config | Needed |
| Bitrix24 user ID | `BITRIX_WEBHOOK_URL` in wizard config | Needed |
| Google Drive Sales Calls folder ID | `GDRIVE_SALES_FOLDER_ID` in wizard config | Needed |
| Backend endpoint (api.purebrain.ai) | Built by full-stack-developer | Needed |

---

## Files

| File | Purpose |
|---|---|
| `exports/sales-call-wizard/index.html` | Wizard with Bitrix integration code (inactive until credentials set) |
| `exports/sales-call-wizard/bitrix-setup-guide.md` | This document |
| `tools/gdrive_manager.py` | Existing GDrive manager (can be adapted for the backend endpoint) |

---

## Next Steps After Jared Provides Credentials

1. Jared provides: Bitrix24 webhook URL
2. ST# activates Bitrix: set `BITRIX_ENABLED = true`, paste webhook URL
3. ST# deploys updated wizard to WP page 1283
4. Test with a real call
5. Separately: build `api.purebrain.ai/api/create-sales-doc` endpoint (full-stack-developer)
6. Once backend is live: set `GDRIVE_ENABLED = true` + `GDRIVE_SALES_FOLDER_ID`
7. Full end-to-end test: call → Google Doc → Bitrix lead → doc URL in Bitrix

---

*Built by dept-systems-technology — 2026-03-05*
*DO NOT DEPLOY wizard to WordPress until Bitrix credentials are provided and tested.*
