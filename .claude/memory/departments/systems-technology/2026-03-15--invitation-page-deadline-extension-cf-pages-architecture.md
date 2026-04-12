# Invitation Page Deadline Extension + CF Pages Architecture Discovery

**Date**: 2026-03-15
**Type**: deployment + architecture
**Status**: Complete

## What Was Done

Extended /invitation/ page deadline from March 18 → March 21, 2026 (Wednesday → Friday).

**6 string replacements:**
1. `2026-03-19T04:59:59Z` → `2026-03-22T04:59:59Z` (countdown target)
2. Comment updated
3. `Closes Wednesday` → `Closes Friday`
4. `March 18th, EOD Eastern` → `March 21st, EOD Eastern`
5. `CLAIMED = 12` → `CLAIMED = 15` (fallback)
6. `pb-claimed-count">12` → `pb-claimed-count">15`

**File**: `exports/cf-pages-deploy/invitation/index.html`

## CRITICAL ARCHITECTURE DISCOVERY

**purebrain.ai is served from Cloudflare Pages, NOT WordPress GoDaddy.**

- DNS: `purebrain.ai → CNAME → purebrain-staging.pages.dev`
- WP REST API, wp-admin, wp-login — ALL return 200 HTML (homepage) but it's the CF Pages site
- WP is NOT accessible externally at all
- All page changes MUST go via `exports/cf-pages-deploy/` + wrangler deploy

**Deploy command:**
```bash
cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy
CLOUDFLARE_API_TOKEN=$CF_PAGES_TOKEN CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID \
npx wrangler pages deploy . --project-name=purebrain-staging --commit-dirty=true
```

CF Pages project: `purebrain-staging`
Zone: `49400cad1527af716705f6cb8c22bb65`

## Signup Flow Architecture

All pay-test pages (/pay-test-2/, /insiders/, /pay-test-awakened/, /pay-test-partnered/, /pay-test-unified/) share:
- SAME Google Form: `1FAIpQLSei-RHBkOYsm79-4ueVqVSYAhNMrAwjTcoI1wpBpPPAtf2ujg`
- SAME server-side flow: api.purebrain.ai/api/log-pay-test
- Spots counter: api.purebrain.ai/api/spots-status (16/25 as of 2026-03-15)
- Brevo: transactional emails only (birth welcome) - NOT list signup from waitlist form

/invitation/ itself has NO signup form - it's a showcase/CTA page linking to pay-test pages.

## Spots Count Discrepancy
- API: 16 claimed (spots_state.json has 16 orders)
- Jared says 15 - the extra is `jared-test` (Bonded, manual-entry 2026-02-26)
- Page JS fetches live from API → will display 16
