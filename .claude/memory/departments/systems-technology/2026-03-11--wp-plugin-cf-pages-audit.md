# WP Plugin → CF Pages Function Audit
**Date**: 2026-03-11
**Type**: architecture audit
**Topic**: Which WordPress plugin functions need replication on Cloudflare Pages

## Key Findings

### Two Backend Servers
1. **WordPress (purebrain.ai)** — serves `/wp-json/purebrain/v1/*`, `/wp-json/pb-security/v1/*`, `/wp-json/pb-referral/v1/*`
2. **Flask server (api.purebrain.ai)** — `tools/purebrain_log_server.py`, serves `/api/*` via Cloudflare Tunnel

### Critical Bug Found
CF pages (homepage, pay-test-2, homepage-clone-v2) use **relative URLs** for logging:
```
const LOGGING_ENDPOINT = '/wp-json/purebrain/v1/log-conversation-fallback';
```
On CF Pages domains these are 404. Fix: replace with `https://api.purebrain.ai/api/log-conversation`.

### Flask Server Missing 2 Endpoints
1. `POST /api/guide-unlock` — 5 compare/vs pages call `/wp-json/purebrain/v1/guide-unlock`
2. `POST /api/investor-lead` — investor-intelligence page calls `/wp-json/purebrain/v1/investor-lead`

### Security Headers
Use CF Pages `_headers` file — no Worker needed. Create `purebrain-site/public/_headers`.

### Referral Plugin (9 endpoints)
Keep on WordPress for now. Tables need MySQL. Option A = keep WP as referral backend.

### CSS/JS Already Baked In
All dark background enforcement, pricing UI, GA4 tracking, PayPal integration are baked into static HTML. No replication needed for those.

## Priority Actions
1. Fix relative `/wp-json/` URLs in CF page HTML → absolute `https://api.purebrain.ai/api/log-conversation`
2. Add `guide-unlock` and `investor-lead` endpoints to `tools/purebrain_log_server.py`
3. Create `_headers` file for security headers
4. Referral system stays on WP (low priority to migrate)

## Report
`exports/departments/systems-technology/2026-03-11--wp-plugin-functions-cf-audit.md`
