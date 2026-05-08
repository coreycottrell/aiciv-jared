# Onboarding Flow QA — Nightly E2E
**Run**: 2026-05-01 02:08 UTC
**Agent**: browser-vision-tester (BOOP scheduled task)

## 🔴 CRITICAL FINDINGS (2)

### 1. /thank-you/ returns 404 when query string present
- `GET https://purebrain.ai/thank-you/` → 200 OK (62KB)
- `GET https://purebrain.ai/thank-you/?email=X` → **404**
- `GET https://purebrain.ai/thank-you/?email=X&aiName=Y&tier=Z` → **404**
- Response headers: `cache-control: no-store` — indicates Worker/Function intercept, not static 404
- **Impact**: Every PayPal redirect lands on 404 because payment pages redirect to `/thank-you/?email=...&aiName=...&tier=...`
- **Suspected cause**: Worker route rule or `_routes.json` mismatch; magic-link Worker may be capturing query-strings on /thank-you/
- **Severity**: BLOCKS revenue confirmation for ALL paying customers

### 2. /insiders/awakened/ returns 404
- `GET https://purebrain.ai/insiders/awakened/` → **404**
- Memory shows this was supposedly fixed 2026-04-29 (`feedback_insiders_subpaths_in_payment_guard.md`)
- Either regressed or never deployed to `purebrain-production`

## 🟡 HIGH-PRIORITY (2)

### 3. /pay-test-sandbox-5/ is broken stub
- 4.9KB only — no PayPal SDK, no seed flow, no email field, no thank-you redirect, no pricing
- Either delete from production or restore proper template

### 4. /insiders/pay-test-awakened/ contaminated
- 12 GoDaddy/WordPress tracking refs (`_trfq`, `secureserver`, `wpaas`)
- No seed flow detected
- Has PayPal + thank-you redirect, but onboarding instrumentation missing

## ✅ HEALTHY (10)

| Page | PayPal | Seed | Thank-you | WP/GD | Pricing |
|------|--------|------|-----------|-------|---------|
| **purebrain.ai/** (homepage) | 9 | 12 | 14 | 0 | 8 |
| /live/ | 9 | 11 | 10 | 0 | 7 |
| /home-test/ | 9 | 12 | 14 | 0 | 8 |
| /home-test-sandbox/ | 9 | 12 | 14 | 0 | 8 |
| /home-test-live-1/ | 9 | 12 | 14 | 0 | 2 |
| /awakened/ | 9 | 11 | 10 | 0 | 3 |
| /partnered/ | 9 | 11 | 10 | 0 | 3 |
| /unified/ | 9 | 11 | 10 | 0 | 3 |
| /pay-test-sandbox-3/ | 9 | 11 | 10 | 0 | 8 |
| /insiders/ | 9 | 11 | 10 | 0 | 1 |

## Recommended Actions
1. **WTT#** — investigate `/thank-you/?<query>` 404. Likely Worker route catching query-strings. Highest severity.
2. **ST#** — verify `/insiders/awakened/` deploy state; redeploy from git if missing on `purebrain-production`.
3. **ST#** — decide fate of `/pay-test-sandbox-5/` (delete from CF Pages or restore template).
4. **ST#** — clean WP tracking from `/insiders/pay-test-awakened/`; add seed instrumentation.

## Test Methodology
- Live curl against production purebrain.ai
- Static grep for: PayPal SDK refs, send-seed/fireSeed, /thank-you redirect, GoDaddy/WP tracking, email input, pricing tokens
- 13 pages tested (per CLAUDE.md memory: 6 payment + homepage + 3 home-test + 2 insiders + insiders parent)
