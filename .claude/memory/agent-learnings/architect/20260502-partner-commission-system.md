# Partner Commission System Architecture — Research + Design

**Date**: 2026-05-02  
**Type**: Operational + Teaching  
**Topic**: Two-tier partner commission system enhancement on existing referral infrastructure

## System Context

Existing referral system lives in:
- Worker: `workers/referrals-api/src/worker.js`
- D1: `purebrain-referrals` (ID: cdd9a522-f947-42a6-b9a3-c30534e02c3f)
- Binding: `env.DB`
- Auth: X-Admin-Token header or ?admin_token= query param
- Public endpoints: open (called by portal_server.py)

Existing tables: `referrers`, `referrals`, `commission_payments`, `payout_requests`, `sessions`, `password_resets`

## Enhancement Design Decisions

### Schema approach: additive-only migrations
All changes are ALTER TABLE ADD COLUMN or CREATE TABLE. No drops. This makes rollback safe — revert the Worker JS, new columns remain harmlessly in D1.

### Split config storage: JSON column on referrers
Chose `referrers.split_config TEXT` (JSON) over a separate split_config table. Rationale: split config is a rare, per-partner setting with max 3 entries. A JSON column is simpler than a join and avoids a third new table. The `commission_splits` table records EARNED splits (one row per deal), while `split_config` stores the TEMPLATE.

### Discount implementation: pricing URL param, not coupon engine
The 10% discount is implemented as a checkout URL param (`?price=discounted`) checked against Elite partner status, not a coupon code database. Avoids promo code abuse, no code management overhead. PayPal receives the discounted amount; webhook resolves product tier via a price map.

### Commission rate: computed at webhook time, not stored
Commission rate is derived from `partner_tier + total_sales` at the moment the PayPal webhook fires. Not stored in a commission_rates table. Formula: Standard=5% always, Elite=15% (0-99 sales) / 17% (100-999) / 20% (1000+).

### $35 ops fee: deducted first (constitutional)
All commission calculations: `commission_base = payment_amount - 35.00`, then `commission_value = commission_base * rate`. This was confirmed from Jared's spreadsheet and must never change.

## Key Worker File Patterns

The worker uses:
- `requireAdmin(request, env)` — checks X-Admin-Token against ADMIN_TOKENS secret (comma-separated)
- `parseBody(request)` — safe JSON parse
- `json(body, init)` — standard JSON response helper with CORS headers
- `err(status, message)` — error shorthand
- `generateToken(bytes)` — crypto random hex

New functions to add follow same pattern as existing. No framework, plain Workers API.

## Product Price Map (required for webhook)

```javascript
const PRODUCT_PRICES = [
  { tier: 'unified',   full: 1097, discounted: 987 },
  { tier: 'partnered', full: 597,  discounted: 537 },
  { tier: 'awakened',  full: 297,  discounted: 267 },
];
```

Worker must resolve incoming PayPal amount against both full and discounted prices.

## Deployment Note

Worker deploys via `wrangler deploy` (NOT `wrangler pages deploy`). The constitutional ban is on `wrangler pages deploy` which deletes pages not in local folder. Workers are a separate deploy path and are safe.

## SRS Output

Full spec written to: `/home/jared/exports/portal-files/PARTNER-COMMISSION-SRS-2026-05.md`
14 sections, ~4500 words, 2-sprint plan + cleanup sprint.
