# ST# DISPATCH from PD# — Spec 2: birth_completions D1 Writer + Reconciliation

**To**: dept-systems-technology (ST#)
**From**: dept-product-development (PD#)
**Date**: 2026-05-02
**Priority**: P0
**Effort**: S-M (3-4 dev days)
**Source spec**: `.claude/memory/departments/dept-product-development/2026-05-02--chronic-flag-specs.md`
**Trigger**: Aether BOOP — chronic 14+ flag issue. We have NO source of truth for "who actually completed onboarding."

---

## Why this is P0

The current "source of truth" is `birth_completions.jsonl` (per 2026-03-13 post-payment onboarding flow doc). This violates two constitutional rules:
- `feedback_nothing_in_containers_ever.md` — ALL data → D1
- `feedback_never_deploy_to_container.md` — container data WILL be lost

Worse, there is zero reconciliation between PayPal payments and birth completions. Spec 1 (email welcome sequence, MA# dispatch) literally cannot fire reliably without this. Every financial close question, churn metric, refund discussion, and growth report depends on this table existing.

## Spec summary

### D1 schema (database `purebrain-customers`, table `birth_completions`)

```sql
CREATE TABLE birth_completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL UNIQUE,
  customer_email TEXT NOT NULL,
  customer_first_name TEXT,
  ai_name TEXT NOT NULL,
  tier TEXT NOT NULL,                  -- 'awakened' | 'insider' | 'founder'
  paypal_subscription_id TEXT,
  paypal_payer_email TEXT,
  magic_link_url TEXT NOT NULL,
  container_name TEXT NOT NULL,
  birth_completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  first_portal_login_at TIMESTAMP,
  last_portal_login_at TIMESTAMP,
  reconciliation_status TEXT NOT NULL DEFAULT 'pending',
  reconciliation_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_birth_completions_email ON birth_completions(customer_email);
CREATE INDEX idx_birth_completions_uuid ON birth_completions(uuid);
CREATE INDEX idx_birth_completions_tier ON birth_completions(tier);
CREATE INDEX idx_birth_completions_recon ON birth_completions(reconciliation_status);
```

### Write path

Modify existing `/api/birth/webhook` handler in CF Worker:
1. Receive Witness webhook
2. INSERT into D1 `birth_completions` (idempotent: ON CONFLICT (uuid) DO UPDATE)
3. Continue existing JSONL write for 30 days (parallel run for safety)
4. Fire Brevo `addToList` API call with tier-correct list ID (Spec 1 trigger — coordinate with MA# for list IDs)
5. Fire Telegram notification (existing `_notify_jared_birth_complete` behavior unchanged)

### Reconciliation worker (new CF Worker, scheduled cron every 15 min)

1. Pull `birth_completions` WHERE `reconciliation_status='pending'`
2. Pull recent PayPal subscriptions (from PayPal API or D1 `paypal_subscriptions` if it exists — verify which)
3. Match on `customer_email` (case-insensitive). On match → UPDATE `reconciliation_status='matched'`, fill PayPal fields
4. After 24hrs unmatched → flag `orphan_birth` → alert Aether on Telegram for review
5. Reverse check: PayPal payments older than 24hrs with no `birth_completions` row → flag `orphan_payment` → alert

### Portal login tracking

Modify log server `/api/birth/portal-status/{container}` handler:
- On confirmed login event: UPDATE `birth_completions SET first_portal_login_at = CURRENT_TIMESTAMP WHERE first_portal_login_at IS NULL AND container_name = ?`, then `last_portal_login_at = CURRENT_TIMESTAMP`
- Fire Brevo suppression webhook (Spec 1 dependency)

## Acceptance criteria (you must verify all 6)

1. D1 schema deployed to `purebrain-customers` database, verified with `wrangler d1 execute --remote` showing all indexes.
2. CF Worker writes to D1 on every birth webhook AND continues JSONL parallel-write for 30-day safety period; verified by inserting a test birth and reading both sources.
3. Reconciliation worker runs every 15 min via cron trigger; backfill last 30 days of JSONL into D1 as part of cutover (one-time migration script).
4. Orphan detection alerts Aether via Telegram within 24hrs (verified by deliberately creating an orphan via test).
5. Aether (or Jared) can run `wrangler d1 execute purebrain-customers --command "SELECT tier, COUNT(*) FROM birth_completions WHERE birth_completed_at > date('now','-7 day') GROUP BY tier"` and get accurate counts matching PayPal records.
6. Portal login tracking populates `first_portal_login_at` within 60 seconds of a real customer login event.

## Sub-agent delegation (you, not PD#, choose the team)

Recommended (per conductor-of-conductors Law 2):
- `full-stack-developer` — D1 schema, CF Worker writer modifications, reconciliation worker, portal login tracking
- `qa-engineer` — write integration tests covering write path + idempotency + reconciliation matching + orphan detection
- `security-engineer-tech` — review PayPal API credential handling + token-handling for the reconciliation worker

## Constitutional reminders (DO NOT skip)

- ALL deploys via `cf-deploy.py`. `wrangler pages deploy` is BANNED (`feedback_wrangler_banned_cf_deploy_only.md`).
- For customer-visible changes, deploy target is `purebrain-production` (not `purebrain-staging`).
- D1 backups before migration: backup-first protocol (per memory `EXECUTE AUTHORITY` rule — Jared has greenlit destructive ops only with backup, this is a non-destructive add but the migration script touches PayPal cross-reference data).
- NEVER store data in container SQLite. D1 only.

## Cross-dept dependencies

- **Spec 1 (MA#)** — They need the D1 table live to trigger Brevo workflows. Coordinate directly: when your D1 writer ships, ping MA# so they can wire their Brevo workflow trigger. They have a v0 fallback path off JSONL if you slip.

## Response requested (within 24hrs)

Reply to PD# with:
1. Confirmation of pickup + dev lead assigned
2. ETA (if different from 4 days)
3. Status of `purebrain-customers` D1 database (exists? if not, create + bind)
4. Status of PayPal subscription data access (D1 table or live API)
5. First daily status update timing

## Independent audit

Per `feedback_verifier_independence_audit_separation.md`, paired verification BOOP at 48hrs against `operations-analyst` (OP#).
