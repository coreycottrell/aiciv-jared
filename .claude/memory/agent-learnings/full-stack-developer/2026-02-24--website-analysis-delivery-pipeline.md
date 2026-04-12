# Website Analysis Delivery Pipeline

**Date**: 2026-02-24
**Type**: teaching + operational
**Topic**: Automated delivery pipeline for PureBrain AI Website Analysis product

---

## What Was Built

Full end-to-end delivery automation for the website analysis product.

### Files Created

- **Delivery script**: `/home/jared/projects/AI-CIV/aether/tools/website_analysis_delivery.py`
- **Documentation**: `/home/jared/projects/AI-CIV/aether/docs/website-analysis-automation.md`
- **Delivery log**: `logs/website_analysis_deliveries.jsonl` (created on first delivery)

---

## Key Patterns

### PayPal Setup (on this site)
- Payment page 826 (`/ai-website-execution/`) has working PayPal SDK
- `POST /api/verify-payment` in `purebrain_log_server.py` handles server-side verification
- `POST /api/paypal-webhook` handles `PAYMENT.CAPTURE.COMPLETED` events
- `PAYPAL_WEBHOOK_ID` in `.env` still needs to be filled in (pending Jared registering it)

### WordPress Page Creation Pattern (LOCKED IN)
```python
# Required: wrap in wp:html block or wpautop destroys CSS
content = f'<!-- wp:html -->\n{fonts_html}\n<style>{dark_css}{report_css}</style>\n<div id="{wrapper_id}">{body}</div>\n<!-- /wp:html -->'

# Use elementor_canvas template for full-width pages
payload = {
    'status': 'publish',
    'password': report_password,
    'template': 'elementor_canvas',
    'content': content,
}
```

### Dark Theme Override (Required for Every Report Page)
```css
html body.page, html body {
  background-color: #0a0e1a !important;
  background: #0a0e1a !important;
}
.wp-block-html { background: #0a0e1a !important; }
[class*="magic"] { color: inherit !important; background-color: inherit !important; }
body { cursor: auto !important; }
.tt-magic-cursor, #tt-magic-cursor { display: none !important; }
```

### Password Generation
- Format: `xxxx-xxxx-xxxx` (4+4+4 segments with hyphens)
- Alphabet: lowercase + digits, excludes `0`, `o`, `i`, `l`, `1` (ambiguous)
- Uses `secrets.choice()` for cryptographic randomness

### Delivery Flow
1. `_generate_password()` → random 14-char password
2. `create_wordpress_report_page()` → new WP page, password-protected, elementor_canvas template
3. `_upsert_brevo_contact()` → background thread, non-blocking
4. `send_report_delivery_email()` → Brevo transactional with template vars
5. `_send_telegram()` → Jared alert with URL + password
6. `_log_delivery()` → JSONL record for audit trail

---

## What's Still Manual (Needs Jared to Finish)

1. **Create Brevo delivery email template** — see docs for content/variables
2. **Set `BREVO_REPORT_DELIVERY_TEMPLATE_ID`** in `.env`
3. **Register PayPal webhook** at developer.paypal.com → set `PAYPAL_WEBHOOK_ID` in `.env`
4. **Create `/ai-website-analysis/` sales page** on purebrain.ai

## How to Test

```bash
python3 /home/jared/projects/AI-CIV/aether/tools/website_analysis_delivery.py --test
```

This creates a real WP page (with a test report placeholder) and sends a real email.
Check `logs/website_analysis_deliveries.jsonl` for the result.

---

## Architecture Note: Two-Phase Delivery

The pipeline is intentionally two-phase because the report requires analysis work:

**Phase 1** (automatic, seconds after payment):
- PayPal webhook fires → Telegram alert to Jared → holding email to customer

**Phase 2** (manual for now, ~hours after payment):
- Aether runs analysis, generates report HTML
- `deliver_report()` called → WP page created → delivery email sent

Future: Phase 2 can be fully automated once report generation is scripted.
