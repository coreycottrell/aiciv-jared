# PureBrain Frontend 3D Portal — Integration Audit

**Date**: 2026-02-26
**Type**: operational
**Topic**: Full audit of purebrain-frontend-3d.html v2 from Shahbaz (Witness)

---

## Key Finding: Files Are Identical

The new file from Jared (`docs/from-telegram/purebrain-frontend-3d.html`) and the
existing export (`exports/purebrain-frontend-3d.html`) are byte-for-byte identical
(both 14,495 lines, diff returns exit code 0).

This means: no update was actually delivered. The file Shahbaz sent IS the current version.

---

## Architecture: This Is an AICIV Gateway Frontend, NOT a PureBrain Birth Pipeline Client

This is a critical distinction. The frontend does NOT call our birth pipeline endpoints directly.

**What the frontend IS**:
- A full-featured AI chat portal UI (Claude-like interface)
- Connects to an "AICIV Gateway" — a separate backend server (not purebrain_log_server.py)
- Gateway URL is configurable via Settings or `/aiciv-config.json` file
- Branding overlaid with PureBrain colors, logo, login UI

**What it calls (AicivClient)**:
- `POST /api/auth/login` — login with aiciv_name + secret
- `GET /api/auth/verify` — verify stored token
- `DELETE /api/auth/logout` — logout
- `GET /api/health` — gateway health check
- `POST /api/start` — start chat session
- `POST /api/message/{sessionId}` — send message
- `GET /api/response/{sessionId}` — poll for response
- `DELETE /api/session/{sessionId}` — end session
- `GET /api/agents` — list agents
- `GET /api/memories` — list memories
- `GET /api/conversations` — conversation history
- `GET /api/skills` — skills list
- `GET /api/boop/status` — boop status
- `GET /api/teams` — teams info
- `GET /api/events` — live events stream

**NONE of these endpoints exist in our purebrain_log_server.py.**

---

## What purebrain_log_server.py Actually Exposes

Our server at api.purebrain.ai exposes:
- `/api/health` — health check (compatible)
- `/api/log-conversation` — POST conversation logs
- `/api/verify-payment` — POST payment verification
- `/api/paypal-webhook` — POST webhooks
- `/api/log-pay-test` — POST test logs
- `/api/stats` — GET stats
- `/api/proxy/birth/start` or `/api/birth/start` — proxy to Witness
- `/api/proxy/birth/code` or `/api/birth/code` — proxy to Witness
- `/api/proxy/birth/portal-status/<container>` — proxy to Witness

---

## Hardcoded External URLs

1. `https://pure-brain-dashboard-api.purebrain.workers.dev` — stored as `API_CONFIG.baseUrl`
   - Marked DEPRECATED in code comments
   - Not actively called by main chat flow
   - Legacy Cloudflare Workers endpoint

2. `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-1.png` — logo image
   - Fine as-is

---

## Missing External Dependency: aiciv-terminal-patch.js

The HTML ends with: `<script src="aiciv-terminal-patch.js"></script>`
This file does NOT exist anywhere in the aether repo.
Terminal mode UI is declared "handled by aiciv-terminal-patch.js".
If this file is missing when served, terminal features will be broken (silent JS error).

---

## Security Assessment

**XSS**: Low risk. escapeHtml() is properly implemented and used for user-supplied data.
User data inserted into DOM uses textContent (not innerHTML) in most places.
Attachment filenames use escapeHtml() in innerHTML contexts. Acceptable.

**Auth**: Bearer token stored in localStorage. Acceptable for this use case.
No hardcoded API keys or secrets found.

**Selah legacy data**: Code migrates old `selah_*` localStorage keys to `aiciv_*` — clean migration.

**CORS/CSRF**: Frontend makes fetch() requests to configurable gatewayUrl.
If gatewayUrl is empty string (default), all calls go to same origin — safe.

---

## Configuration Flow

1. On load: tries to fetch `/aiciv-config.json` from same origin
2. If found: sets `gatewayUrl = serverConfig.backendUrl`
3. If not found: uses `localStorage.getItem('aiciv_gateway_url') || ''` (same origin)
4. User can override in Settings panel

So to point this at a real backend: serve an `aiciv-config.json` alongside the HTML:
```json
{ "backendUrl": "https://api.purebrain.ai" }
```
But that backend must implement the AICIV Gateway API (not our current log server).

---

## Summary for Shahbaz

This frontend requires a full AICIV Gateway server implementing ~10 REST endpoints.
Our api.purebrain.ai (purebrain_log_server.py) is NOT that server.
The birth pipeline proxy endpoints we added are separate — they are called by the
post-payment chatbox (chatbox v3), NOT by this portal frontend.

This portal is the customer-facing AI chat UI. It needs Witness's AICIV backend
(the system that runs agents, manages sessions, etc.) pointed at via aiciv-config.json.
