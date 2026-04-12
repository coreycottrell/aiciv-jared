# Witness Birth Pipeline Integration — Architecture Decision

**Date**: 2026-03-03
**Type**: architecture
**Topic**: Seed sender + webhook receiver design for PureBrain → AiCIV pipeline

## Key Decisions

1. Webhook receiver goes in purebrain_log_server.py at /api/birth/webhook (not WordPress)
2. Webhook URL to give Witness: https://api.purebrain.ai/api/birth/webhook (already confirmed)
3. HMAC verification via X-Witness-Signature header (sha256=<hex>)
4. Seed sender partially built (v4.8 3-stage), needs payload update to formal spec
5. Magic link delivery: Brevo email + Telegram to Jared + optional chatbox display

## Current Infrastructure State

- Seed proxy: /api/intake/seed → http://178.156.229.207:8200/intake/seed (EXISTS, line 788 log server)
- Birth proxy: /api/birth/start|code|status|portal-status → http://37.27.237.109:8099 (EXISTS)
- Webhook receiver: DOES NOT EXIST — primary build target
- Brevo API key: in .env as BREVO_API_KEY
- Witness fleet host: 37.27.237.109:8099
- Witness seed VPS: 178.156.229.207:8200

## P0 Tasks (webhook live)

1. Generate WITNESS_WEBHOOK_SECRET + add to .env
2. Share secret with Witness via hub
3. Add /api/birth/webhook route
4. Implement HMAC verify_witness_signature()
5. Implement Brevo birth email send
6. Create Brevo birth template
7. Implement Telegram notify
8. Implement idempotency check
9. Security review
10. Deploy + QA

## Reference

Full architecture doc: exports/departments/systems-technology/2026-03-03--witness-birth-pipeline-architecture.md
