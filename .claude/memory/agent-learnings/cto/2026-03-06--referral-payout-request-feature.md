# Referral Payout Request Feature — Plugin v2.1.0

**Date**: 2026-03-06
**Type**: operational
**Topic**: Added website-side payout request UI + WP REST endpoints to referral plugin

## What Was Built

Extended `tools/security/purebrain-referral/purebrain-referral-system.php` from v2.0.0 to v2.1.0.

### New Constants
- `PB_PAYOUT_REQUESTS_FILE` — points to `/home/jared/purebrain_portal/payout-requests.jsonl` (shared with portal server)
- `PB_PAYOUT_MIN_AMOUNT` — $25 minimum
- `PB_PAYOUT_COOLDOWN_DAYS` — 30 day cooldown between requests
- `PB_TG_SEND_SH` — path to `tools/tg_send.sh`

### New REST Endpoints
Both registered under namespace `pb-referral/v1`:
- `POST /wp-json/pb-referral/v1/payout-request` — validates earnings, cooldown, writes to shared JSONL, notifies Jared via Telegram
- `GET /wp-json/pb-referral/v1/payout-history?referral_code=XXX` — reads from shared JSONL, filters by code, returns clean array

### Dashboard Shortcode Changes
The `[pb_referral_dashboard]` shortcode now renders two additional sections after the referral history table:

1. **"Request Payout" section** (shown when `earnings >= $25`):
   - PayPal email field
   - Amount field (min=$25, max=available balance)
   - Submit button (green, #1a7a50 themed)
   - Inline validation (amount range, email format)
   - Success state after submission
   - Payout history table (pulls from new `/payout-history` endpoint)

2. **"Payout locked" notice** (shown when `earnings < $25`):
   - Tells user how much more they need

### Shared Storage Design
The JSONL file at `/home/jared/purebrain_portal/payout-requests.jsonl` is shared between:
- Portal server (Python/Starlette) — reads/writes directly
- WordPress plugin (PHP) — reads/writes via `file_get_contents` + `file_put_contents`

Entry schema matches portal server exactly (request_id, referral_code, paypal_email, amount, status, created_at, created_at_ts, paid_at, notes). Added `source: "website"` field to distinguish origin.

### Telegram Notification Pattern
wp_remote_post with `blocking: false` — fire-and-forget, does NOT block the HTTP response.
Reads bot token from `/home/jared/projects/AI-CIV/aether/config/telegram_config.json`.

## Security Notes
- Rate limited: 2 payout requests per IP per hour (WP transient)
- Input validation: referral_code regex, email validation, amount bounds
- Earnings verification against WP DB before writing
- Cooldown check against existing JSONL entries
- NOT in security plugin — lives in referral plugin only (per SECURITY PLUGIN ISOLATION rule)

## File Path
`/home/jared/projects/AI-CIV/aether/tools/security/purebrain-referral/purebrain-referral-system.php`

## Gotchas
- The `payout-requests.jsonl` directory (`/home/jared/purebrain_portal/`) must already exist — plugin does NOT auto-create it
- wp_remote_post blocking:false requires WordPress HTTP API to be available (always is on front-end requests)
- JSONL file uses LOCK_EX on file_put_contents to prevent race conditions from simultaneous writes
