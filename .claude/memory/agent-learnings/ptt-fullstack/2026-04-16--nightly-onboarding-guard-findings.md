# Nightly Onboarding Guard Findings - 2026-04-16
Type: operational
Topic: Payment pipeline verification, page pricing audit, Bryce Lohr onboarding

## Key Findings

### Pipeline Health
- Full E2E pipeline (payment -> seed -> magic link -> welcome email) completed in ~6 minutes for Bryce Lohr
- All 8 pages return HTTP 200
- UUID generation via crypto.randomUUID confirmed on all pages
- PayPal buttons render on all pages
- Chat widget loads on all pages

### /insiders/ Pricing Discrepancy
- /insiders/ shows Awakened at $74.50/mo (plan P-8AU4270420374002JNGY3VYQ)
- All other pages show $149/mo (plan P-2SA65600MT088594TNGLTFKY)
- Different PayPal plan IDs suggest this is intentional insider pricing
- Flagged for Jared confirmation -- do NOT change pricing without approval

### SSL Issue Pattern (recurring)
- cornerstone-bryce.app.purebrain.ai SSL fails: "tlsv1 alert internal error"
- Caddy on 37.27.237.109 cannot issue certs for new *.app.purebrain.ai subdomains
- This is the same pattern as previous portal subdomains -- Caddy needs wildcard cert or on-demand TLS config fix
- Blocks customer portal access until fixed

### Seed Pipeline Robustness
- The chatbox send-seed POST returned 400 but the payment-triggered seed pipeline correctly found conversation via sessionUuid (25 messages) and fired successfully
- AI name "Cornerstone" correctly extracted from conversation
- Fallback strategy (S1-orderId -> S2-sessionUuid -> S3-email -> S4-recent -> S5-name) works well

## Files
- Report: `/home/jared/exports/portal-files/overnight-onboarding-guard-2026-04-16.md`
