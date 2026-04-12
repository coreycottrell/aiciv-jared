# Witness OAuth Integration Architecture — Response Drafted

**Date**: 2026-02-27
**Type**: operational
**Agent**: collective-liaison
**Topic**: Drafted comprehensive integration response for Witness OAuth webhook wiring

---

## What Happened

Witness sent OAuth integration coordination message via /tmp/witness-aether-comms/ file drop.
They have a production-ready OAuth webhook (port 8099, ~37s end-to-end) and needed:
1. Where in PureBrain flow OAuth starts
2. New tab vs iframe for OAuth URL
3. How we detect OAuth completion
4. API contract expectations
5. Error/edge case handling
6. Testing approach

Drafted comprehensive response based on pay-test-script-chat-flow-v4.js analysis.

## Key Architecture Facts (for future reference)

### PureBrain OAuth Touch Points (v4.7)

**Trigger**: End of Q4 (role/title), beginning of runBirthInit()
**Auto-fire**: Yes — v4.5 per Corey/Witness spec, no user button
**Sequence**:
  1. POST /api/birth/start (name, email, aiName, tier)
  2. Response: {oauth_url, container}
  3. Show "Authorize [aiName]'s AI Brain →" in actions area (new tab, _blank)
  4. User completes OAuth in new tab, gets code
  5. "I have my key →" button → text input
  6. POST /api/birth/code (container, auth_code)
  7. Confirm: "Yay! [aiName]'s brain is connected."
  8. Continue with Q5 (primary goal)
  9. At flow:complete → POST /birth/seed (full profile, PROPOSED)
  10. Portal polling: GET /api/birth/portal-status/{container} every 30s

### Security Constraints

- OAuth URL validated: must be HTTPS + claude.ai or anthropic.com domain
- Container name comes ONLY from server response (v4.6+ — no client-side generation)
- WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai' (Cloudflare proxy, never direct IP)
- auth_code input sanitized before POST

### Timeouts

- /birth/start: 45s (should extend to 60s before E2E — Witness reports ~37s)
- /birth/code: 120s
- Portal polling: 30s interval, 10min max

### Retry Logic

- /start: 3 attempts, then "Skip setup" option shown to user
- /code: User re-enters code (no hard limit)
- Portal: 10min total, then fallback "check email" message

## Open Issues (blocking E2E as of 2026-02-27)

1. Container pool exhausted (aiciv-06 through aiciv-10 stuck) — Witness must free
2. v1.2.0 API contract confirmation (field names unchanged from v1.1.0?)
3. Michael Hancock / Metis / aiciv-07 provisioning status
4. /birth/seed endpoint — needs Witness spec before we can wire it

## Response File

Draft saved to: /home/jared/projects/AI-CIV/aether/to-witness/2026-02-27--oauth-integration-architecture-response.md
Status: DRAFT — awaiting Jared review before sending

## Pattern: File Drop Communication Channel

Witness uses /tmp/witness-aether-comms/ for async file drops.
This works alongside hub witness-aether room (persistent record).
Both channels active simultaneously — file drop for rich docs, hub for searchable log.

## Key Script Reference

- Chat flow: /home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js
- runBirthInit(): lines ~1913-2190
- runPortalButtonWatcher(): lines ~2200-2293
- WITNESS_WEBHOOK_HOST: line 1900
- runQuestionnaire() auto-fires runBirthInit at line 1216
