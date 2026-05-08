# AgentMail Webhook Worker Build

**Date**: 2026-04-30
**Type**: operational
**Agent**: ptt-fullstack (full-stack-developer)

## What Was Built

Created `workers/agentmail-webhook/` — a Cloudflare Worker that replaces the Python polling daemon `tools/agentmail_monitor.py`.

## Key Decisions

1. **No auth on /send-welcome**: The welcome-email-api Worker does NOT require auth on its `/send-welcome` endpoint (only template management does). So this worker calls it without an auth header.

2. **Sandbox bypass logic**: Ported the full sandbox email detection from the Python script (sb-* prefix, example.com domains, (sandbox-sub) literal). Redirects to jared@puretechnology.nyc.

3. **Dual-send logic**: PayPal email looked up from D1 clients table (not a JSON file like the Python version). Both chatbox email and PayPal email receive welcome emails if they differ.

4. **Duplicate detection**: Checks if the exact magic_link URL already exists in D1 before inserting, preventing double-processing on webhook retries.

5. **Domain rewrite**: Uses env vars (DOMAIN_REWRITE_FROM/TO) rather than hardcoded values, matching the pattern from welcome-email-api.

6. **Fallback UUID generation**: When Witness email lacks a UUID field, falls back to `email:{humanEmail}` or `ts:{timestamp}` — same pattern as the Python script.

## Files Created

- `workers/agentmail-webhook/wrangler.toml` — D1 binding to purebrain-social, env vars
- `workers/agentmail-webhook/schema.sql` — magic_links table + indexes
- `workers/agentmail-webhook/package.json` — minimal, no deps
- `workers/agentmail-webhook/src/worker.js` — 663 lines, full pipeline

## Secrets Needed Before Deploy

```bash
wrangler secret put AGENTMAIL_WEBHOOK_SECRET
wrangler secret put ADMIN_TOKEN
wrangler secret put TELEGRAM_BOT_TOKEN
```

## Not Yet Done

- Schema not applied to D1 yet (needs `wrangler d1 execute`)
- Worker not deployed yet
- AgentMail webhook URL not configured yet
- Thank-you page polling URL might need updating from api.purebrain.ai to this worker's URL
