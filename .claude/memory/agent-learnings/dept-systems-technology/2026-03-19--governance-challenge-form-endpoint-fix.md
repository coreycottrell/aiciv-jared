# Governance Challenge Form Endpoint Fix

**Date**: 2026-03-19
**Type**: operational
**Agent**: dept-systems-technology
**Topic**: Missing API endpoint causing "Failed to fetch" on governance form

## Problem

purebrain.ai/governance/ form was throwing "Failed to fetch" on submit.

Root cause: The JS called `https://api.purebrain.ai/api/governance/challenge` (POST) but no such route existed. Server returned 404.

## Infrastructure Architecture (key reference)

- `api.purebrain.ai` -> Cloudflare tunnel -> `https://localhost:8443` (log server, `tools/purebrain_log_server.py`)
- `portal.purebrain.ai` / `app.purebrain.ai` -> nginx 8099 -> `localhost:8097` (portal server)
- CF Pages site makes fetch calls to `api.purebrain.ai` - these go to the LOG SERVER, not the portal server

## Fix

Added `/api/governance/challenge` route to `tools/purebrain_log_server.py` (Flask, port 8443).

Route behavior:
1. Validates `challenge` and `email` fields (required)
2. Writes full submission to `logs/governance_challenges.jsonl`
3. Sends AgentMail notification to `aethergottaeat@agentmail.to` in background thread
4. Returns `{"ok": true, "id": "<uuid>"}`

Inserted before the `@app.errorhandler(400)` block at end of `register_routes()`.

Restarted via `sudo systemctl restart aether-logserver.service`.

## Verification Results

- Local: `curl -sk -X POST https://localhost:8443/api/governance/challenge` -> `{"ok":true,"id":"486bff5d"}`
- Public: `curl -s -X POST https://api.purebrain.ai/api/governance/challenge` -> `{"ok":true,"id":"bc7b9cb3"}`
- CORS OPTIONS preflight: `HTTP 204`
- Log file: `logs/governance_challenges.jsonl` confirmed written

## Prior Submission Found

One real submission from Waqas (Pure Technology) existed in the log from Mar 17 (different schema, no `id` field, `ip` instead of `client_ip`). That was pre-fix. No AgentMail was sent for it - may need manual follow-up.

## Key Pattern

When a CF Pages static site says "Failed to fetch" on form submit:
1. Grep the HTML for the `fetch(` call to find the endpoint URL
2. Check cloudflared config (`/etc/cloudflared/config.yml`) to find which server handles that subdomain
3. Check that server's routes for the missing endpoint
4. Add the route to the correct server (log server = port 8443 = api.purebrain.ai)

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` (added route at line 829)
- `/home/jared/projects/AI-CIV/aether/logs/governance_challenges.jsonl` (log file, auto-created)
