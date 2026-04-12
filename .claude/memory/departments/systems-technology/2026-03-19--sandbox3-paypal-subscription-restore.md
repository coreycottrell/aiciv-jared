# Sandbox-3 PayPal Subscription Restore

**Date**: 2026-03-19
**Type**: operational
**Topic**: Restoring sandbox plan IDs after backup restore wiped them to empty strings

## What Happened

After a backup restore of sandbox-3, the `PLAN_IDS` block was reset to empty strings:
```javascript
var PLAN_IDS = {
  Awakened:  '',
  Partnered: '',
  Unified:   '',
};
```
Empty strings = one-time $149 payment mode instead of subscription billing.

## The Fix

Replace with the sandbox subscription plan IDs from `config/paypal_sandbox_plans.json`:
```javascript
var PLAN_IDS = {
  Awakened:  'P-9KA28683EF7622051NGLUFJY',
  Bonded:    'P-1JL98851AU229172RNGLUFJY',
  Partnered: 'P-6JY35646YA5259513NGLUFKA',
  Unified:   'P-6DU61407NY0900135NGLUFKI',
};
```

**File**: `exports/cf-pages-deploy/pay-test-sandbox-3/index.html` line ~14279

## Key Verification Points

1. `PAYPAL_CLIENT_ID` must be `AYTFob...` (PAYPAL_SANDBOX_CLIENT_ID from .env) — NOT the live `AWgWNl...` key
2. Plan IDs start with `P-` and belong to the PayPal sandbox environment
3. Source of truth for plan IDs: `config/paypal_sandbox_plans.json`
4. Source of truth in memory: `.claude/memory/departments/systems-technology/2026-03-11--wp-entity-encoding-ampersand-fix-pattern.md`

## Deploy Command

```bash
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
```

## Anti-Pattern: Backup Restores Wipe Plan IDs

When restoring from backup, always check PLAN_IDS block — backups may have been taken when the page was in one-time payment mode or initial build state.
