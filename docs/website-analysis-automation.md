# PureBrain Website Analysis — Automated Delivery Pipeline

**Created**: 2026-02-24
**Author**: full-stack-developer
**Status**: Implemented — Brevo delivery template pending creation

---

## Overview

This document describes the end-to-end automated delivery pipeline for the PureBrain Website Analysis product sold at `https://purebrain.ai/ai-website-analysis/`.

**Customer journey (automated):**

```
Customer sees sales page
         ↓
Clicks pricing button → PayPal modal opens
         ↓
Pays via PayPal SDK (client-side capture)
         ↓
Browser calls /api/verify-payment (server confirms with PayPal API)
         ↓
Telegram alert fires → Jared sees purchase in real-time
         ↓
Aether generates the report HTML (browser-vision-tester + web-researcher)
         ↓
Aether runs deliver_report() → WordPress page created + email sent
         ↓
Customer receives email with link + password
         ↓
Customer reads their password-protected report
```

---

## Current Payment Setup

### Sales Page
- **URL**: `https://purebrain.ai/ai-website-analysis/` (to be created)
- **Payment page reference**: `/ai-website-execution/` (page 826) — uses identical PayPal SDK integration
- **PayPal Client ID**: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI` (live, from `.env`)
- **Payment model**: One-time capture via PayPal JS SDK

### How PayPal Works on This Site

The sales page uses the **PayPal JS SDK Smart Buttons** (Approach A):

1. Customer clicks "Get My Analysis" button → modal opens
2. PayPal SDK renders the gold Pay button inside the modal
3. Customer completes PayPal checkout (stays on-page, no redirect)
4. `onApprove` fires → browser calls `actions.order.capture()`
5. After capture, JavaScript calls `POST https://api.purebrain.ai/api/verify-payment` with the order ID
6. Server independently confirms the payment with PayPal's API
7. Browser redirects customer to thank-you page

### Verify-Payment Endpoint

**Already implemented** in `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`

- **Endpoint**: `POST https://api.purebrain.ai/api/verify-payment`
- **Input**: `{ "order_id": "PAYPAL-ORDER-ID", "tier": "standard" }`
- **Actions on verified payment**:
  - Logs to `logs/purebrain_payments.jsonl`
  - Sends Telegram notification to Jared
  - Sends Brevo confirmation email to buyer
  - Returns verification status to browser

### PayPal Webhook (Secondary Safety Net)

**Already implemented** in `purebrain_log_server.py`

- **Endpoint**: `POST https://api.purebrain.ai/api/paypal-webhook`
- **Event**: `PAYMENT.CAPTURE.COMPLETED`
- **Setup required**: Register in PayPal Developer Dashboard (see `.env` comment for instructions)
- **Status**: `PAYPAL_WEBHOOK_ID` in `.env` is currently empty — webhook events still logged but signature not verified

---

## Delivery Script

### Location
`/home/jared/projects/AI-CIV/aether/tools/website_analysis_delivery.py`

### What It Does

| Step | Action |
|------|--------|
| 1 | Generates a secure 12-character password (`xxxx-xxxx-xxxx` format) |
| 2 | Transforms the report HTML for WordPress (scopes CSS, adds dark override, wraps in `wp:html`) |
| 3 | Creates a published, password-protected WordPress page on `purebrain.ai` |
| 4 | Clears Elementor cache so the page is immediately accessible |
| 5 | Upserts a Brevo contact for the customer |
| 6 | Sends the delivery email via Brevo transactional API |
| 7 | Sends Jared a Telegram alert with the URL and password |
| 8 | Logs everything to `logs/website_analysis_deliveries.jsonl` |

### Usage

**Test mode (no real customer):**
```bash
cd /home/jared/projects/AI-CIV/aether
python3 tools/website_analysis_delivery.py --test
```

**Manual delivery:**
```bash
python3 tools/website_analysis_delivery.py \
  --email "jane@acmecorp.com" \
  --name "Jane Smith" \
  --company "Acme Corp" \
  --report-file "exports/client-marketing/report-acme.html" \
  --order-id "PAYPAL-ORDER-ID" \
  --tier "website-analysis-standard"
```

**From Python (e.g. called by the log server or Aether):**
```python
from tools.website_analysis_delivery import deliver_report

result = deliver_report(
    customer_email="jane@acmecorp.com",
    customer_name="Jane Smith",
    company_name="Acme Corp",
    report_html=html_string,
    order_id="PAYPAL-ORDER-ID",
    tier="website-analysis-standard",
)

if result['success']:
    print(f"Report live at: {result['page_url']}")
    print(f"Password: {result['report_password']}")
```

### Return Value

```python
{
    "success": True,
    "page_id": 892,
    "page_url": "https://purebrain.ai/website-analysis-acme-corp/",
    "report_password": "a7kf-m2nq-r9xd",
    "email_sent": True,
    "errors": []
}
```

---

## Report HTML Format

### Source
Reports are built as standalone HTML files following the same visual language as the DuckDive example:
- **Template**: `exports/website-analysis-report-duckdive.html`
- **Client reports**: `exports/client-marketing/[client-name]/report.html`

### Key Variables to Personalize
When generating a report, replace these in the HTML:

| Placeholder | Replace with |
|------------|-------------|
| `DuckDive` / site name | Customer's company name |
| `duckdive.io` / domain | Customer's domain |
| `70` (overall score) | Actual computed score |
| Per-dimension scores | Real analysis data |
| Recommendations list | Actual findings |
| Date | Delivery date |

### WordPress Conversion (Automatic)
The `_prepare_report_html()` function in the delivery script handles:
1. Extracting the `<style>` block
2. Extracting body content
3. Prepending the dark theme override (prevents WordPress orange/theme pollution)
4. Wrapping in `<div id="pb-report-{company-slug}">` for CSS specificity
5. Wrapping everything in `<!-- wp:html --> ... <!-- /wp:html -->` (critical — prevents `wpautop` from destroying CSS)

---

## Brevo Email Template

### Current Status
A dedicated report delivery template needs to be created in Brevo.

Currently using Template 11 (the PureBrain Welcome email) as a placeholder.

### Template to Create

**Template name**: `PureBrain - Website Analysis - Report Ready`
**From**: `hello@purebrain.ai` / PureBrain
**Reply-to**: `hello@purebrain.ai`

**Subject**: `Your Website Analysis Report is Ready — {{ params.COMPANY_NAME }}`

**Body** (customize in Brevo WYSIWYG):

```
Hi {{ params.FIRSTNAME }},

Your website analysis for {{ params.COMPANY_NAME }} is complete.

Here is your private report:

  [ACCESS YOUR REPORT]
  {{ params.REPORT_URL }}

  Password: {{ params.REPORT_PASSWORD }}

Your report covers 9 dimensions of website performance — SEO, GEO, AIO,
content quality, technical health, user experience, conversion, authority,
and engagement.

Save both the URL and password somewhere safe. This page is private to you.

If you have questions or want to discuss the findings, reply to this email
or book a call at https://purebrain.ai/call

Best,
The PureBrain Team

Order reference: {{ params.ORDER_ID }}
```

### Setup Steps

1. Go to https://app.brevo.com/transactional/template/list
2. Create new template with the content above
3. Save and note the template ID (shown in the URL and template list)
4. Add to `.env`:
   ```
   BREVO_REPORT_DELIVERY_TEMPLATE_ID=XX
   ```
5. Restart the log server: `pkill -f purebrain_log_server && nohup python3 tools/purebrain_log_server.py >> logs/purebrain_log_server.log 2>&1 &`

---

## Delivery Workflow in Practice

### When a New Order Comes In

**What happens automatically:**
1. PayPal capture fires
2. Browser calls `/api/verify-payment`
3. Jared gets Telegram alert: "NEW WEBSITE ANALYSIS PURCHASE"
4. Customer gets a holding email (template 11 as placeholder currently)
5. Order is logged to `logs/purebrain_payments.jsonl`

**What Jared or Aether does next (manual step currently):**
1. Run the website analysis for the customer (browser-vision-tester agent + Aether analysis)
2. Generate the report HTML
3. Save to `exports/client-marketing/[company-slug]/report.html`
4. Run the delivery script:
   ```bash
   python3 tools/website_analysis_delivery.py \
     --email "customer@email.com" \
     --name "Customer Name" \
     --company "Company Name" \
     --report-file "exports/client-marketing/company-name/report.html" \
     --order-id "PAYPAL-ORDER-ID"
   ```
5. Customer gets the real delivery email with URL and password

### Future: Fully Automated Delivery

When the report generation process is automated:

1. PayPal webhook fires `PAYMENT.CAPTURE.COMPLETED`
2. `paypal_webhook` endpoint in log server calls `deliver_from_paypal_webhook()`
3. This logs a delivery intent to `logs/website_analysis_deliveries.jsonl`
4. Aether's overnight automation picks up pending deliveries
5. Runs analysis, generates report, calls `deliver_report()` directly

---

## File Structure

```
tools/
  website_analysis_delivery.py     ← Main delivery script (NEW)
  purebrain_log_server.py          ← Flask API server (has verify-payment endpoint)

logs/
  website_analysis_deliveries.jsonl  ← Delivery log (created on first delivery)
  purebrain_payments.jsonl           ← Payment verification log

exports/
  website-analysis-report-duckdive.html  ← Example/template report
  client-marketing/
    [company-name]/
      report.html                    ← Client-specific reports

config/
  post_purchase_brevo_config.json    ← Brevo customer list IDs

docs/
  website-analysis-automation.md    ← This document
```

---

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `PUREBRAIN_WP_USER` | `.env` | WordPress username (Aether) |
| `PUREBRAIN_WP_APP_PASSWORD` | `.env` | WordPress application password |
| `BREVO_API_KEY` | `.env` | Brevo API key for email |
| `BREVO_REPORT_DELIVERY_TEMPLATE_ID` | `.env` | Brevo template ID (create and set this) |
| `PAYPAL_CLIENT_ID` | `.env` | PayPal live client ID |
| `PAYPAL_SECRET` | `.env` | PayPal live secret |
| `PAYPAL_WEBHOOK_ID` | `.env` | PayPal webhook ID (register and set this) |

---

## WordPress Page Details

| Setting | Value |
|---------|-------|
| Site | `purebrain.ai` |
| Status | `publish` (password-protected = only accessible with password) |
| Template | `elementor_canvas` (full-width, no nav/footer) |
| Slug pattern | `website-analysis-{company-slug}` |
| Title pattern | `Website Analysis Report — {Company Name}` |
| Password | Randomly generated `xxxx-xxxx-xxxx` format |

### Example URLs
- DuckDive: `https://purebrain.ai/website-analysis-duckdive/` (password: generated)
- Acme Corp: `https://purebrain.ai/website-analysis-acme-corp/` (password: generated)

---

## Security Notes

1. **Passwords are never stored in plain text in WordPress** — WordPress hashes them internally
2. **Passwords ARE logged** to `logs/website_analysis_deliveries.jsonl` so Aether can resend if email fails
3. **The delivery log contains PII** — do not commit it to git (already in `.gitignore`)
4. **Each customer gets a unique password** — compromise of one doesn't expose others
5. **Pages are indexed as private** — WordPress sets `noindex` on password-protected pages automatically
6. **Report URLs are not publicly guessable** — slugs include company name but pages require password

---

## Troubleshooting

### "WP_APP_PASSWORD not configured"
Check `.env` for `PUREBRAIN_WP_APP_PASSWORD`. If missing, regenerate in WordPress:
Admin → Users → Aether profile → Application Passwords

### "Brevo email failed"
1. Check `BREVO_API_KEY` is set in `.env`
2. Check the template ID exists in Brevo: https://app.brevo.com/transactional/template/list
3. Check `logs/purebrain_emails.jsonl` for error details

### WordPress page returns 422
The slug already exists. Either delete the old page or pass a unique company name variation.

### Page looks broken after delivery
1. Verify the HTML is wrapped in `<!-- wp:html -->` (the script does this automatically)
2. Clear Cloudflare cache: Cloudflare dashboard → Caching → Purge Everything
3. Check the page template is `elementor_canvas` (not the default template)

### Log server timeout / 502 error
The log server accumulates CLOSE_WAIT connections. Restart it:
```bash
pkill -f purebrain_log_server
nohup python3 /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py >> /home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log 2>&1 &
```

---

## Next Steps Checklist

- [ ] Create the Brevo delivery email template (see template content above)
- [ ] Set `BREVO_REPORT_DELIVERY_TEMPLATE_ID` in `.env`
- [ ] Register PayPal webhook in developer dashboard (URL: `https://api.purebrain.ai/api/paypal-webhook`)
- [ ] Set `PAYPAL_WEBHOOK_ID` in `.env`
- [ ] Create the `/ai-website-analysis/` sales page on purebrain.ai (adapt from `/ai-website-execution/`)
- [ ] Run `python3 tools/website_analysis_delivery.py --test` to verify the pipeline works
- [ ] Do a real end-to-end test: buy a test analysis, generate a report, run deliver_report(), confirm email arrives

---

**End of document**
