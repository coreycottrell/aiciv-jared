# Magic Link Pipeline — Auto-Fire Architecture

**Date**: 2026-03-13
**Type**: Build record
**Status**: Deployed

## What Was Built

### Problem
When Witness completes a CIV birth, the customer needs a magic link to enter their Brain Stream.
Previously: manual process, Brevo webhook-dependent.
New: fully automated, dual-channel (webhook + AgentMail email), real-time button activation.

### 4 Components

**1. AgentMail Monitor** (`tools/agentmail_monitor.py`)
- Watches for emails with "MAGIC LINK" in subject from any Witness sender
- Parses: AI Name, Human Name, Email, UUID, Container, Magic Link URL
- Rewrites domain: `.ai-civ.com` → `.app.purebrain.ai` (regex: `(https?://)([^./]+)\.ai-civ\.com`)
- Stores in `.magic-links.json` keyed by session UUID (persistent, thread-safe, atomic writes)
- Sends welcome email via Google SMTP (template at `/tmp/magic-link-email-template.html`)
- Notifies Jared on Telegram

**2. Log Server Endpoint** (`tools/purebrain_log_server.py`)
- `GET /api/magic-link/{uuid}` — returns `{status: "pending"}` or `{status: "ready", magic_link, ai_name, ...}`
- Reads from `.magic-links.json`
- UUID format validation (security — rejects non-UUID inputs with 400)
- Injected before `/api/stats` route inside `register_routes()`

**3. Chatbox JS** (all 6 payment pages in `exports/cf-pages-deploy/`)
- New function: `runMagicLinkPoller(dom, aiName)` — polls every 5 seconds
- Called alongside `runPortalButtonWatcher` (they race; first to fire wins)
- Uses `payTestData.sessionUuid` as the lookup key
- Activates button with `ptc-portal-btn ptc-portal-btn--pulsing` class
- Button text: `Enter {AI_NAME}'s Brain Stream` (AI name from API response)
- Allowed domains updated to include `ai-civ.com` for URL validation

**4. Deployment**
- Services: `aether-logserver` + `agentmail-monitor` restarted via systemctl
- CF Pages: deployed to `purebrain-staging` project

## Key File Locations

- Magic links store: `/home/jared/projects/AI-CIV/aether/.magic-links.json`
- Email template: `/tmp/magic-link-email-template.html`
- AgentMail monitor: `tools/agentmail_monitor.py`
- Log server: `tools/purebrain_log_server.py` (endpoint at line ~2142)

## Testing

```bash
# Test endpoint returns ready for Lucas Neuteufel
curl -sk "https://api.purebrain.ai/api/magic-link/4d1a1ede-f188-4458-b816-d7781c1d649e"
# Expected: {"status":"ready","magic_link":"https://testailucas.app.purebrain.ai/",...}

# Test pending UUID
curl -sk "https://api.purebrain.ai/api/magic-link/00000000-0000-4000-8000-000000000001"
# Expected: {"status":"pending"}

# Test invalid UUID security rejection
curl -sk "https://api.purebrain.ai/api/magic-link/not-a-uuid"
# Expected: {"error":"Invalid UUID format"}
```

## Patterns Learned

- The log server uses nested function defs inside `register_routes()` — inject new routes inside that function scope
- Services are `aether-logserver` and `agentmail-monitor` (not `purebrain-log-server`)
- CF Pages deploy token var: `CF_PAGES_TOKEN` (not `CLOUDFLARE_API_TOKEN`)
- `payTestData.sessionUuid` is the chatbox's session identifier — always a UUID v4 format
- The button placeholder element: `id="ptc-portal-placeholder"` → replaced with `<a class="ptc-portal-btn ptc-portal-btn--pulsing">`
- Two parallel polling strategies run concurrently and race: container-based (30s) + UUID-based (5s)
