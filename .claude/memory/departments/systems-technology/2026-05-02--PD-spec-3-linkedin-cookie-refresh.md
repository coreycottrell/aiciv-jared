# ST# DISPATCH from PD# — Spec 3: LinkedIn Cookie Refresh Workflow

**To**: dept-systems-technology (ST#)
**From**: dept-product-development (PD#)
**Date**: 2026-05-02
**Priority**: P1
**Effort**: S (small, 2 dev days)
**Source spec**: `.claude/memory/departments/dept-product-development/2026-05-02--chronic-flag-specs.md`
**Trigger**: Aether BOOP — chronic 14+ flag issue. Manual cookie refresh is recurring drag on Jared and blocks ~30% of LinkedIn ops.

---

## Context — read the prior ST# work first

You shipped the cookie destruction-loop fix on 2026-05-01 (`.claude/memory/departments/systems-technology/2026-05-01--linkedin-puresurf-session-idempotency-fix.md`). That was the hard part. Cookies no longer get destroyed by failed sessions. The residual problem is two-fold:

1. **Initial seed** — one human re-login still required to populate `aether-linkedin` profile with valid `li_at` (documented in your 2026-05-01 fix). Jared needs to do this once.
2. **Ongoing expiry** — `li_at` cookies naturally expire (~30 days). When they do, automation breaks silently and Jared discovers it via "why didn't my LinkedIn post go out today?" That's the loop this spec breaks.

## Decision — Plan A only (PD# decided)

Per Aether BOOP, PD# was asked to choose between:
- **Plan A**: Telegram one-tap refresh page when cookies near expiry
- **Plan B**: Independent OAuth path the team already built

**PD# decision: Plan A.** Reasoning:
- Plan B (independent OAuth) is for OTHER team members operating their own LinkedIn presence — `feedback_plan_b_oauth_means_independent.md` explicitly says we never collect their codes. Plan B does NOT apply to Pure Tech's own `aether-linkedin` automation account.
- For Pure Tech's automation account, official LinkedIn API access requires Developer App approval — multi-week, not in our control. That is a separate PR# (dept-pure-research) track.
- Plan A unblocks ops THIS WEEK with 2 dev days and makes the manual step painless rather than mysterious.

## Spec summary

### Component 1 — Cookie expiry monitor (CF Worker, scheduled cron daily 09:00 UTC)

For each LinkedIn profile in PureSurf (`aether-linkedin` initially, schema for future profiles):
- Call `GET https://surf.purebrain.ai/api/v1/profiles/{profile}/cookies`
- Find `li_at` cookie, parse expiry timestamp
- Trigger alert if: expiry < 7 days away OR cookie missing entirely OR `linkedin_icp_commenter.py` log shows "PRE-FLIGHT FAIL" line in the last 24hrs (tail or grep)

### Component 2 — Telegram one-tap refresh

Alert payload to Jared via Telegram bot:
```
LinkedIn cookies for {profile} expire in {N} days (or: ARE MISSING).
One-tap refresh: https://refresh.purebrain.ai/linkedin?profile={profile}&token={one_time_token}
```

Token = single-use, 1hr TTL, stored in D1 `refresh_tokens` table (new):
```sql
CREATE TABLE refresh_tokens (
  token TEXT PRIMARY KEY,
  profile TEXT NOT NULL,
  purpose TEXT NOT NULL DEFAULT 'linkedin_cookie_refresh',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  consumed_at TIMESTAMP
);
```

### Component 3 — Refresh page (CF Pages, deploy via cf-deploy.py)

Target deployment: new project `purebrain-tools` (or extend existing) → serves `refresh.purebrain.ai`.

Page renders:
- Token validation (single-use, 1hr TTL)
- Mobile-responsive (Jared often refreshes from phone)
- 3-step checklist:
  1. "Click here to open PureSurf" — button opens `https://surf.purebrain.ai` with profile pre-selected
  2. "Log into LinkedIn manually, wait for page load"
  3. "Click 'Verify' below" — button hits monitor endpoint, confirms `li_at` is fresh + valid
- On verify success: mark token consumed, send confirmation to Aether's Telegram
- On verify fail: show retry instructions, do not consume token

## Acceptance criteria (you must verify all 5)

1. Cookie expiry monitor runs daily and successfully identifies a deliberately-expired test cookie within one cron cycle.
2. Telegram alert fires to Jared with a clickable refresh link when expiry < 7 days OR cookie missing.
3. Refresh page loads, validates one-time token, renders correctly on mobile (Jared often refreshes from phone).
4. After Jared completes manual login + verify click, cookie monitor confirms fresh `li_at`, sends confirmation to Telegram, and any blocked LinkedIn workflows (`linkedin_icp_commenter.py --discover`) succeed on next scheduled run.
5. Reduce "manual cookie refresh requests in Telegram" to zero unprompted asks per month — every refresh initiated by the monitor, not by Jared discovering posts didn't go out.

## Sub-agent delegation (you choose your team)

Recommended:
- `full-stack-developer` — Monitor worker, refresh page, D1 tokens table
- `security-engineer-tech` — token entropy + rate limiting + page security review (no XSS, no token leak in URL on referrer)
- `qa-engineer` — End-to-end test: trigger expiry → alert → refresh → verify → automation success

## Constitutional reminders

- Deploy via `cf-deploy.py` ONLY. `wrangler pages deploy` is BANNED.
- Customer-visible domains use `purebrain-production` deploy target — but `refresh.purebrain.ai` is internal-tool so a dedicated `purebrain-tools` project is fine. Confirm with Aether/Jared which CF project to bind.
- Telegram bot creds: `config/telegram_config.json` (NOT `.env`).
- D1 `refresh_tokens` table goes in `purebrain-customers` database (extend, don't create a new DB).

## Cross-dept handoff (after ship)

After ship, hand off to MA# (`dept-marketing-advertising`) to:
- Update LinkedIn weekly engine SOP to include "check cookie monitor status" as pre-flight
- Confirm new flow replaces ad-hoc Telegram requests in their playbook
- Acknowledge in their next LinkedIn ops memo

PD# will route this MA# adoption handoff once ST# confirms ship.

## Response requested (within 24hrs)

Reply to PD# with:
1. Confirmation of pickup + dev lead assigned
2. ETA (if different from 2 days)
3. Decision on which CF Pages project hosts `refresh.purebrain.ai`
4. Confirmation that Jared still needs to do the ONE-TIME initial re-login to seed `aether-linkedin` cookies (residual blocker from your 2026-05-01 fix) — the monitor handles all future expiries but this first one is human-only

## Independent audit

Per `feedback_verifier_independence_audit_separation.md`, paired verification BOOP at 48hrs against `operations-analyst` (OP#).
