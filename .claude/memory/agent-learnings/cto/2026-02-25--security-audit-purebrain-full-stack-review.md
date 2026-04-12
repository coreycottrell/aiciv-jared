# Memory: CTO Security Audit — purebrain.ai Full-Stack Review

**Date**: 2026-02-25
**Agent**: cto
**Type**: operational + teaching
**Topic**: Comprehensive security audit delegated by Co-CEO (Aether). Reviewed .env, log server, WordPress plugin, Cloudflare config, and agent learnings.

---

## Summary of Findings

### CRITICAL — .env File Exposure (Structural Risk)

The .env file at `/home/jared/projects/AI-CIV/aether/.env` contains ALL production secrets in plaintext:
- BSKY_PASSWORD (Bluesky app password)
- GOOGLE_APP_PASSWORD (Gmail)
- OPENAI_API_KEY (OpenAI)
- PAYPAL_CLIENT_ID + PAYPAL_SECRET (live PayPal keys)
- PUREBRAIN_WP_PASSWORD + PUREBRAIN_WP_APP_PASSWORD
- BREVO_API_KEY
- TWITTER API keys (all 4)
- SKETCHFAB, MESHY, AIRTABLE, APIFY, NETLIFY tokens
- REDDIT credentials in plaintext

Git status shows .env is MODIFIED (not gitignored check needed) — the file is in the working tree and tracked changes exist.

**Risk**: If this repo were accidentally pushed public, or if the server were compromised, ALL credentials would be exposed simultaneously.

**Recommendation for Jared**: Rotate any credentials that have been compromised. Verify `.env` is in `.gitignore`. Consider a secrets manager (Doppler, HashiCorp Vault) for production-grade secret management.

---

### MEDIUM — PAYPAL_WEBHOOK_ID Is Empty

In `.env` line 83: `PAYPAL_WEBHOOK_ID=` (empty value)

In `purebrain_log_server.py` lines 1288-1304: When `PAYPAL_WEBHOOK_ID` is not set, webhook signature verification is SKIPPED and the event is processed anyway with a warning log.

This means any attacker can forge PayPal webhook events by POSTing to `/api/paypal-webhook` — the server will log the event and potentially trigger downstream actions (Telegram notifications, email sequences) without any verification.

**Recommendation**: Register the webhook in PayPal dashboard and set PAYPAL_WEBHOOK_ID.

---

### MEDIUM — Log Server Missing Global Body Size Cap

The Flask app has NO global `MAX_CONTENT_LENGTH` set. Body size caps exist only on the birth proxy endpoints (65536 bytes). The `/api/log-conversation`, `/api/verify-payment`, and `/api/log-pay-test` endpoints have no size cap.

An attacker could POST a 50MB payload to these endpoints, causing memory pressure.

**Recommendation**: Add `app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024` (1MB) globally.

---

### LOW — /api/stats Exposes Internal File Path

The `/api/stats` endpoint returns `log_file` field containing the absolute server path:
`/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl`

This leaks server directory structure. Not critical (it's behind CORS) but unnecessary information disclosure.

**Recommendation**: Remove `log_file` from the stats response, or replace with a sanitized label.

---

### LOW — ACGEE Forwarding Uses Plain HTTP

`ACGEE_LANDING_CHAT_URL = 'http://5.161.90.32:3001/api/landing-chat'` — plain HTTP to an IP address. Conversation data (messages, session IDs) transmitted unencrypted over this leg.

**Recommendation**: If the A-C-Gee endpoint supports HTTPS, switch to it. If not, document this as an accepted risk with partner.

---

### INFORMATIONAL — Existing Security Controls (Good)

These are working correctly:
1. CORS restricted to purebrain.ai + jareddsanborn.com origins (SEC-001)
2. Birth proxy endpoints have rate limiting (5/min start, 10/min code, 60/min portal-status)
3. Real client IP extraction via CF-Connecting-IP > X-Forwarded-For > remote_addr
4. Body size cap on birth proxy endpoints (65536 bytes)
5. Container name allowlist pattern `^[a-zA-Z0-9_-]{1,50}$`
6. WITNESS_BASE_URL hardcoded (never from request input — SSRF prevention)
7. Non-JSON Witness responses logged server-side only (no upstream error exposure)
8. WordPress plugin v6.1.0 blocks user enumeration (?author= redirect, /wp/v2/users removed)
9. Security headers present: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy
10. Cloudflare Tunnel (TLS) used — raw IP no longer exposed in WP proxy calls
11. XSS fix applied in chatbox v4.2 (sanitizeText helper, DOM API for user input)
12. OAuth URL domain validation before DOM injection
13. PayPal credentials stripped from client-side log payload (CRIT-001)
14. Telegram tokens masked in chat UI (CRIT-002)

---

## Plugin Version Status

Current deployed: v6.1.0 (most recent in tools/security/)
Security features at v6.1.0 include all fixes through v3.8.0:
- PUREBRAIN_BEHIND_CLOUDFLARE constant (requires manual wp-config.php entry)
- Brevo fail-closed on missing API key (MED-003)
- esc_html() at output point (LOW-001)

**Open item from v3.8.0**: wp-config.php needs `define('PUREBRAIN_BEHIND_CLOUDFLARE', true)` on both sites. Without this, rate limiting uses Cloudflare edge IP (shared bucket = broken rate limiting).

---

## Files Reviewed

- `/home/jared/projects/AI-CIV/aether/.env`
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` (v6.1.0)
- `.claude/memory/agent-learnings/full-stack-developer/*security*` (8 files reviewed)
