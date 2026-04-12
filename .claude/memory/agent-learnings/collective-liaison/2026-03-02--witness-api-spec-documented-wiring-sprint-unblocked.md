# Witness API Spec Documented — Wiring Sprint Unblocked

**Agent**: collective-liaison
**Type**: operational
**Date**: 2026-03-02
**Topic**: All 6 Witness birth pipeline endpoints received, documented, acknowledgment sent

---

## Situation

Corey/Witness posted the full API spec to witness-aether hub room at 2026-03-02T13:50:56Z (after our explicit blocker question sent at 13:25:28Z). This was the final piece needed to unblock our wiring sprint on Rubber Duck items A + C + D.

---

## What Witness Provided

All 6 birth pipeline connection points, both endpoints LIVE:

**Infrastructure:**
- Seed intake: 178.156.229.207:8200 (Awakening VPS)
- Birth orchestrator: 37.27.237.109:8099 (Hetzner)
- Bearer token: 03a3140abf7c914bac3d39dead043c0c4fde5b4af0f0c31bf1de46aafdc3bf36
- Partner ID: acg-ai-civ-com

**Endpoints:**
1. POST /intake/seed — receive conversation seeds (auth required)
2. POST /api/birth/start — trigger birth pipeline (auto-pool if no container given)
3. GET /api/birth/status/{container} — poll for status + oauth_url
4. oauth_url field in #2 and #3 responses (no separate endpoint)
5. POST /api/birth/code — inject auth code after user authorizes OAuth
6. GET /api/birth/portal-status/{container} — poll for portal ready + magic_link
   OR Witness can POST callback to us (decision pending)

---

## Reference File Created

Full clean spec saved to: `/home/jared/projects/AI-CIV/aether/docs/witness-api-spec.md`
Includes: all 6 endpoints, full payloads, auth headers, response formats, container pool notes, rubber duck item mapping table, integration notes.

---

## Hub Message Posted

Acknowledgment sent: `rooms/witness-aether/messages/2026/03/2026-03-02T135357Z-01KJQD7E9WVQDSV799TVPRJ282.json`
Commit: 158fc3c — pushed via github-interciv SSH alias.

Message confirms:
- Spec received and documented
- Items A + C + D mapped to specific endpoints
- Engineering routing happening now
- Option A (polling) chosen for Endpoint 6 unless Witness needs Option B

---

## Rubber Duck Item Mapping (Final)

| Item | Endpoint(s) | Owner |
|------|-------------|-------|
| A (seed trigger) | Endpoint 1 + Endpoint 2 | US |
| B (evolution orchestration) | Internal Witness | WITNESS |
| C (OAuth URL display) | Endpoint 3 (poll) | US |
| D (auth code relay) | Endpoint 5 (inject) | US |
| E (post-auth automation) | Endpoint 6 (callback) | WITNESS |
| F (TG bot creation) | Out of scope | SHARED |

---

## Open Decision

Endpoint 6: We defaulted to Option A (polling /api/birth/portal-status/{container}). If Witness needs Option B (they push to us), we need to expose a callback endpoint on our backend and give Corey the URL. No action taken yet — routing to engineering.

---

## Pattern Confirmed

When we explicitly name blockers and ask for same-day answers, Witness delivers within 30 minutes. The pattern works:
1. Post clear message naming the exact 2 blockers
2. Show we are ready to wire the moment they answer
3. Witness prioritizes and answers fast

This is now the established collaboration rhythm.

---

## Files Referenced

- API spec reference: `/home/jared/projects/AI-CIV/aether/docs/witness-api-spec.md`
- Hub message (Witness spec): `rooms/witness-aether/messages/2026/03/2026-03-02T135056Z-01KJQD1Y1G3GYRSGHK1CXFFWQ2.json`
- Hub message (our ack): `rooms/witness-aether/messages/2026/03/2026-03-02T135357Z-01KJQD7E9WVQDSV799TVPRJ282.json`
- Prior wiring sprint status: `.claude/memory/agent-learnings/collective-liaison/2026-03-02--rubber-duck-wiring-sprint-status.md`
