# CTO Memory: Phase 3a Referral Payout System — Manual Bridge Implementation

**Date**: 2026-03-06
**Type**: operational
**Agent**: cto
**Confidence**: high
**Tags**: referral-system, payout, phase3a, portal, fastapi, starlette

---

## What Was Built

Phase 3a of the PureBrain referral payout system — the Manual Bridge.

Allows referral earners to request payouts via the portal UI. Jared gets a Telegram notification and processes manually via PayPal.com. No PayPal API required.

---

## Files Changed

### `/home/jared/purebrain_portal/portal_server.py`
Complete rewrite with Phase 3a additions. Key changes:

**New constants (lines 45-47)**:
- `PAYOUT_REQUESTS_FILE = SCRIPT_DIR / "payout-requests.jsonl"`
- `PAYOUT_MIN_AMOUNT = 25.0`
- `PAYOUT_COOLDOWN_DAYS = 30`

**New helper functions**:
- `_send_telegram_notification(message)` — calls tg_send.sh
- `_read_payout_requests()` — reads payout-requests.jsonl
- `_write_payout_request(entry)` — appends to payout-requests.jsonl

**New endpoint functions**:
- `api_referral_payout_request` — POST /api/referral/payout-request
- `api_referral_payout_history` — GET /api/referral/payout-history
- `api_admin_payout_mark_paid` — POST /api/admin/payout/mark-paid

**New routes (added after `/api/portal/owner`)**:
```python
Route("/api/referral/payout-request", endpoint=api_referral_payout_request, methods=["POST"]),
Route("/api/referral/payout-history", endpoint=api_referral_payout_history),
Route("/api/admin/payout/mark-paid", endpoint=api_admin_payout_mark_paid, methods=["POST"]),
```

### `/home/jared/purebrain_portal/portal-pb-styled.html`
Apply via `_patch_phase3a_html.py`. Key additions:

- `#ref-payout-section` — payout section block (injected after `#ref-loading`)
- `#payout-modal` — modal for PayPal email + amount entry
- `loadPayoutState(referralCode, earnings)` — called from `loadReferrals()` after earnings load
- `openPayoutModal()` / `closePayoutModal()` — modal control
- `submitPayoutRequest()` — POSTs to `/api/referral/payout-request`
- `renderPayoutHistory(requests)` — renders payout history list

### `/home/jared/purebrain_portal/payout-requests.jsonl`
Created automatically on first payout request. Schema:
```json
{
  "request_id": "payout-CODE-1741234567",
  "referral_code": "REF123",
  "paypal_email": "user@paypal.com",
  "amount": 50.00,
  "status": "pending",
  "created_at": "2026-03-06T...",
  "created_at_ts": 1741234567.0,
  "paid_at": null,
  "notes": ""
}
```

---

## Security Rules Applied

- Minimum $25 payout threshold
- 30-day cooldown between requests per referral code
- Email format validation server-side
- Balance validated against WP endpoint (soft check — WP unreachable = allow, Jared verifies)
- `mark-paid` requires Bearer token auth (same as all portal endpoints)
- No auto-payment — 100% manual Jared approval before money moves

---

## Deployment

### Apply HTML changes + restart:
```bash
cd /home/jared/purebrain_portal
bash deploy_phase3a.sh
```

Or manually:
```bash
python3 _patch_phase3a_html.py
pkill -f portal_server.py; sleep 2
nohup python3 portal_server.py >> /tmp/portal_server.log 2>&1 &
```

---

## Admin Usage (mark a payout as paid)

After Jared sends money via PayPal manually:
```bash
TOKEN=$(cat /home/jared/purebrain_portal/.portal-token)
curl -s -X POST http://localhost:8097/api/admin/payout/mark-paid \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"request_id": "payout-REF123-1741234567", "notes": "PayPal TX: ABC123"}'
```

---

## Phase 3b (Next)

After PayPal Payouts API approval:
- Add `POST /api/admin/process-payouts` to portal_server.py
- Reads all pending requests, batches to PayPal Payouts API
- Auto-marks as paid on success

Apply for PayPal Payouts API: developer.paypal.com → My Account → Payouts → Enable

---

## Architecture Decision

Portal stores payout requests locally in JSONL (not in WordPress). Reason: portal_server.py already owns the auth layer and Telegram notification. WordPress proxy is read-only for earnings validation. This keeps the payout system lightweight and independent of WP plugin updates.
