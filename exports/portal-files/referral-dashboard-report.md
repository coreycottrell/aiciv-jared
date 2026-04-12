# Referral Dashboard — Production Wiring Complete

## What Was Done

### 1. Real Data Seeded
The standalone referral API database has been populated with production affiliate data:

| Affiliate | Code | Completed | Earnings | Clicks |
|-----------|------|-----------|----------|--------|
| Jared Sanborn | JAREDSB0 | 9 | $60.05 | 45 |
| Apex People | PB-AYXE | 4 | $22.80 | 28 |
| MJ S | PB-K22P | 2 | $11.40 | 15 |
| Michael Hancock | PB-MH7K | 1 | $7.45 | 8 |
| Alex Logie | PB-AL3X | 0 | $0.00 | 5 |

### 2. PayPal Payout Integration
- Users can save PayPal email from dashboard
- Payout request endpoint (minimum $25, 30-day cooldown)
- Admin approval triggers PayPal Payouts API (live credentials configured)
- Telegram notifications on payout events
- Full payout history visible in dashboard

### 3. Frontend Fixed
- All API calls unified to `surf.purebrain.ai/api/referral/*`
- Previously split between `app.purebrain.ai` (dead WP proxy) and `surf.purebrain.ai`
- Deployed to CF Pages, cache flushed

### 4. Security
- Session tokens with 7-day expiry
- Session isolation verified (Apex cannot see Jared's data)
- Rate limiting on login and tracking
- Payout requires admin approval before PayPal fires

## E2E Test Results

| Test | Result |
|------|--------|
| Login as JAREDSB0, verify 9 completed/$60.05 | PASS |
| Login as PB-AYXE, verify 4 completed/$22.80 | PASS |
| PayPal email save | PASS |
| Payout request + history | PASS |
| Session isolation (cross-user blocked) | PASS |

## Files Changed
- `exports/referral-api/referral_api.py` — added payout endpoints + PayPal integration
- `exports/referral-api/seed_referral_data.py` — new: seeds production data
- `exports/cf-pages-deploy/refer/index.html` — unified API URLs
- Server: `/opt/referral-api/referral_api.py` on 157.180.69.225 (deployed + restarted)

## How to Approve Payouts
When an affiliate requests a payout, Jared gets a Telegram notification. To approve:
```bash
curl -X POST "https://surf.purebrain.ai/api/referral/admin/payout-action" \
  -H "Content-Type: application/json" \
  -d '{"request_id":"payout-JAREDSB0-XXXXX","action":"approve","admin_token":"YOUR_TOKEN"}'
```
Or reject with `"action":"reject"`.
