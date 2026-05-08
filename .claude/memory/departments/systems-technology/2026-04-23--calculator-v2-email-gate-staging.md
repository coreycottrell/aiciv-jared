# Calculator v2 — Email Capture Gate (Staging)

**Date**: 2026-04-23
**Type**: operational
**Agent**: dept-systems-technology

## What Was Built

Cloned the AI Partnership Assessment to `/ai-partnership-assessment-v2/` with an email capture gate:
- 5 questions (removed question 6 inline contact form)
- After Q5: email gate screen (First Name + Email only)
- On submit: immediate results (non-blocking API call)
- API: `POST /api/calculator-lead` stores in D1 + creates Brevo contact

## Key Architecture Decisions

1. **Route lives in `_worker.js`** — NOT `/functions/` directory. The `_worker.js` file at root of purebrain-site means CF Pages ignores the `/functions/` directory entirely. All API routes must be added to `_worker.js`.

2. **D1 table `calculator_leads`** created in `purebrain-referrals` database (same DB as referral system). Migration: `d1-migrations/0002-calculator-leads.sql`.

3. **Brevo list ID 7** used for "Calculator Leads" list. Contact creation uses `updateEnabled: true` so existing contacts just get the list added.

4. **Non-blocking API** — `fetch('/api/calculator-lead').catch()` means results show instantly even if API fails. No user-facing delay.

5. **Staging project (`purebrain-staging`) does NOT execute `_worker.js`** — it's static-only. API works on production project only. This means full flow testing requires production deploy.

## Files Created/Modified

- `ai-partnership-assessment-v2/index.html` — v2 page with email gate
- `functions/api/calculator-lead.js` — reference (not executed, superseded by _worker.js)
- `d1-migrations/0002-calculator-leads.sql` — D1 schema
- `_worker.js` — added `/api/calculator-lead` route + CORS for staging.purebrain.ai

## Deploy Status

- Staging: DEPLOYED (purebrain-staging project)
- Production: NOT deployed (awaiting approval)
- D1 table: CREATED (purebrain-referrals database)
- Brevo list: needs verification (list ID 7 may need creation in Brevo dashboard)

## Gotchas

- purebrain-staging has no GitHub integration — requires manual `cf-deploy.py` after git push
- `_worker.js` presence disables `/functions/` directory — all routes go through worker
- Staging project is static-only — no worker execution, so API endpoints return 405 on staging
