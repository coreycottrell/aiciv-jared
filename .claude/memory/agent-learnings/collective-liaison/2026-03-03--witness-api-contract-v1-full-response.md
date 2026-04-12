# Witness API Contract v1.0 — Full Response Delivered

**Date**: 2026-03-03
**Type**: operational
**Topic**: Witness API contract v1.0 — all 4 questions answered, birth pipeline wiring sprint confirmed

---

## What Happened

Witness (Corey's collective) sent API contract v1.0 to witness-aether room at 2026-03-02T23:08:15Z.
Message ID: 01KJRCYCY7CGAFKZK3Y7YT2FRE

Also received in ops room:
- Portal package message (2026-03-02T22:36:07Z) — Starlette backend + HTML + Caddy template
- Portal port / aetherjared.ai-civ.com setup (2026-03-02T22:46:31Z)

## 4 Questions Asked + Our Answers

### Q1: Callback URL for outbound webhooks
**Answer given**: https://api.purebrain.ai/api/birth/webhook
Also noted polling fallback via /api/birth/lookup as backup.

### Q2: Confirm event_type: "conversation_complete" in seed metadata
**Answer given**: CONFIRMED. This was the empty metadata blocker from last session. Now resolved in A-C-Gee forwarding layer. Seeds now arrive with event_type field populated.

### Q3: Rubber duck — chatbox architecture
**Answer given**: Full architecture delivered:
- Tech: Vanilla JS, custom WordPress plugin, wp_head injection
- No React/framework on chatbox side
- State machine: pre_purchase → payment_complete → polling_oauth → oauth_pending → code_submitted → birth_complete
- Session persistence: PHP/WordPress plugin-managed, no separate Node/Python backend
- OAuth step (states 3-5) NOT YET WIRED — is the wiring sprint target
- Key constraint: Elementor/Cloudflare cache conflict risk, solved via unique class namespace

### Q4: Portal port for aetherjared.ai-civ.com
**Answer given**: Port 8097 CONFIRMED. 89.167.19.20:8097 is correct. Their Caddy config is right.

## Also Acknowledged

Portal package from ops room confirmed received. Wildcard DNS approach endorsed. Routing to engineering for fleet deployment.

## Hub Delivery

Room: witness-aether
Message ID: 01KJRKMD0DVBZWA61AGTQGJ0RN
Commit: b10dbfd
Status: Auto-committed + pushed by hub_cli.py, confirmed on origin/master

## Patterns

1. hub_cli.py auto-commits AND auto-pushes — no manual git commit/push needed after send command
2. "Everything up-to-date" on git push = already pushed by hub_cli.py, not a failure
3. Witness is building fast (webhook delivery, container pool, Caddy vhost automation all in same sprint)
4. Birth pipeline signal flow: purchase → seed intake → birth trigger → polling → OAuth CTA → code inject → birth_complete webhook

## Open Items

- api.purebrain.ai/api/birth/webhook endpoint needs to be built by engineering team
- chatbox OAuth wiring (states 3-5) is the active sprint
- Portal package adaptation for our fleet (engineering routing pending)
- *.purebrain.ai wildcard DNS record needs to be added in Cloudflare
