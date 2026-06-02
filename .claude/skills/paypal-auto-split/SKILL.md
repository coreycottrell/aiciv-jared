---
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# PayPal Auto-Split Payout System

**Status**: Active (Constitutional)
**Owner**: dept-accounting-finance
**Last Verified**: 2026-04-07
**Reference**: `feedback_paypal_auto_split_constitutional.md`

---

## Overview

Automated revenue split system for Pure Technology / AICIV partnership payments. When a customer pays via PayPal, the system automatically logs the payment, calculates the split, and (after approval) fires a PayPal Payout to Corey.

## Split Formula (Constitutional -- Do Not Modify)

```
Gross Payment
- $35 AICIV Ops Fee (fixed)
- 5% Referral Fee (of gross)
= Net After Fees
--> 60% to Corey (weaver.aiciv@gmail.com)
--> 40% to Pure Tech (Jared)
```

**Approval requirement**: Manual approval required for each payout UNTIL 20 successful payouts have been completed. After 20 perfect transactions, payouts auto-fire without approval.

## Architecture

```
PayPal Payment Event
  |
  v
PayPal Webhook (PAYMENT.SALE.COMPLETED)
  |
  v
https://portal.purebrain.ai/paypal/webhook
  |  (Cloudflare tunnel -> nginx:8099 -> Flask:8960)
  v
paypal_auto_split.py (webhook handler)
  |
  +-- Verifies PayPal webhook signature (if PAYPAL_WEBHOOK_ID set)
  +-- Calculates split ($35 ops -> 5% referral -> 60/40)
  +-- Logs to Google Spreadsheet (Payout Tracker tab)
  +-- Checks auto-approve threshold (20 successful payouts)
  |
  +-- IF auto-approve enabled (20+ sent):
  |     Fires PayPal Payout API immediately
  |     Sends Telegram confirmation
  |
  +-- IF manual approval required (<20 sent):
        Writes portal notification
        Sends Telegram alert to Jared
        Waits for: python3 tools/paypal_auto_split.py --approve --row N
```

## Components

### 1. Webhook Listener (Flask on port 8960)
- **Process**: systemd service `paypal-webhook.service`
- **Port**: 8960
- **External URL**: `https://portal.purebrain.ai/paypal/webhook`
- **Health check**: GET `/paypal/webhook` returns `{"status":"ok"}`
- **Systemd**: `sudo systemctl status paypal-webhook`

### 2. Split Calculator
- Built into `tools/paypal_auto_split.py`
- Function: `calculate_split(gross: float) -> dict`

### 3. Google Spreadsheet Logger
- Spreadsheet ID: `1bmmO2FVxZdAcYewPFNu6DbHZzh9AAojHUsWgofv6tqQ`
- Tab: "Payout Tracker"
- Data starts at row 8 (rows 1-7 are summary + headers)

### 4. Notification System
- Portal: writes to `exports/portal-files/payout-notification.txt`
- Telegram: sends directly to Jared (chat_id 548906264)

### 5. PayPal Payout API
- Live endpoint: `https://api-m.paypal.com/v1/payments/payouts`
- Sandbox available with `--sandbox` flag
- Recipient: `weaver.aiciv@gmail.com`

## Credentials Location

All in `/home/jared/projects/AI-CIV/aether/.env`:
- `PAYPAL_CLIENT_ID` -- Live PayPal client ID
- `PAYPAL_SECRET` -- Live PayPal secret
- `PAYPAL_SANDBOX_CLIENT_ID` -- Sandbox client ID
- `PAYPAL_SANDBOX_SECRET` -- Sandbox secret
- `PAYPAL_WEBHOOK_ID` -- (NEEDS TO BE SET) For signature verification

Google Sheets auth: `.credentials/oauth-token.json`
Telegram config: `config/telegram_config.json`

## CLI Commands

```bash
# Show current payout status
python3 tools/paypal_auto_split.py --status

# Show financial summary
python3 tools/paypal_auto_split.py --summary

# Manually add a payment (when webhook misses)
python3 tools/paypal_auto_split.py --add-payment \
  --customer "Customer Name" --tier "Awakened" --amount 149

# Approve and fire a payout
python3 tools/paypal_auto_split.py --approve --row 8

# Setup/reformat the spreadsheet tab
python3 tools/paypal_auto_split.py --setup-sheet

# Run webhook listener manually (for debugging)
python3 tools/paypal_auto_split.py --webhook
```

## Verification Checklist

```bash
# 1. Webhook listener running?
sudo systemctl status paypal-webhook

# 2. Health endpoint responding?
curl -s http://localhost:8960/paypal/webhook

# 3. External URL accessible?
curl -s https://portal.purebrain.ai/paypal/webhook

# 4. Spreadsheet connection working?
python3 tools/paypal_auto_split.py --status

# 5. PayPal credentials valid?
python3 -c "import sys; sys.path.insert(0,'.'); from tools.paypal_auto_split import get_paypal_token; print('OK:', len(get_paypal_token()))"

# 6. Check logs
tail -20 logs/paypal_auto_split.log
```

## Manual Trigger (When Webhook Fails)

```bash
python3 tools/paypal_auto_split.py --add-payment \
  --customer "Name" --tier "Awakened" --amount 149 --notes "Manual entry"
python3 tools/paypal_auto_split.py --approve --row <ROW>
```

## Auto-Approve Threshold

- Threshold: 20 successful "Sent" payouts
- Checked on each webhook event
- After threshold: payouts fire automatically
- Telegram still notifies on auto-approved payouts

## Tier Mapping

| Amount | Tier |
|--------|------|
| $149/$197 | Awakened |
| $499/$579 | Partnered |
| $999/$1,089 | Unified |
| Other | Enterprise |

## Infrastructure Files

- Script: `tools/paypal_auto_split.py`
- Systemd: `/etc/systemd/system/paypal-webhook.service`
- Nginx: `/etc/nginx/conf.d/purebrain-main.conf` (location /paypal/webhook)
- Cloudflare: `/etc/cloudflared/config.yml` (paypal.purebrain.ai entry)
- Logs: `logs/paypal_auto_split.log`, `logs/paypal_webhook_service.log`
- Config: `config/paypal_plans.json`, `config/paypal_sandbox_plans.json`

## TODO (Requires Jared)

1. **Set PAYPAL_WEBHOOK_ID in .env** from PayPal Developer Dashboard > Webhooks
   - Create webhook URL: `https://portal.purebrain.ai/paypal/webhook`
   - Subscribe to: `PAYMENT.SALE.COMPLETED`
   - Copy Webhook ID to .env

2. **Verify Cloudflare redirect** -- paypal.purebrain.ai redirects to ai-civ.com.
   Webhook works via portal.purebrain.ai/paypal/webhook as workaround.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Webhook not receiving | `sudo systemctl status paypal-webhook` + check PayPal config |
| Spreadsheet auth fails | `python3 tools/gdrive_oauth_setup.py` |
| PayPal auth fails | Check .env PAYPAL_CLIENT_ID and PAYPAL_SECRET |
| Payout fails | Check PayPal balance + logs |
| Service crashed | `sudo systemctl restart paypal-webhook` |

---

**Constitutional. Split formula and approval flow require Jared's explicit approval to change.**
