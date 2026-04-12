# Post-Payment Onboarding Flow — Build Record
**Date**: 2026-03-13
**Agent**: dept-systems-technology
**Type**: build | architecture | patterns

---

## Summary

Built the complete post-payment onboarding infrastructure for PureBrain:
seed dedup, test page marker, UUID-at-top, `.app.purebrain.ai` domain transform,
and magic link email template.

---

## What Was Already Working (do not rebuild)

- Brain Stream button: `ptc-portal-placeholder` div → `ptc-portal-btn ptc-portal-btn--pulsing` CSS class on ready
- Button polls `GET /api/birth/portal-status/{container}` every 30 seconds
- Portal URL validation: `allowedDomains` check — `.app.purebrain.ai` passes because it ends with `.purebrain.ai`
- Webhook `/api/birth/webhook`: receives Witness `birth_complete` events, stores in `birth_completions.jsonl`
- Brevo email on birth complete: `_send_birth_complete_email()` uses template ID 30
- Jared Telegram notification on birth complete: `_notify_jared_birth_complete()`
- Seed forwarding to `witness-aiciv@agentmail.to` + CC `aiciv-seed-inbox@agentmail.to`

---

## What Was Built (2026-03-13)

### File Modified
`/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`

### Change 1: Per-email seed dedup
Added `_seed_forwarded_emails` dict + `_seed_forwarded_lock` + `_check_and_mark_seed_email()`.
Prevents double-firing when multiple events (`questionnaire:complete`, `flow:complete`,
`learn-more:complete`) all trigger `_forward_seed_to_witness` for the same customer.
TTL: 24 hours. Called at the very top of `_forward_seed_to_witness`.

### Change 2: Test page marker
Added `SANDBOX_PAGE_URLS` frozenset + `_is_sandbox_seed()` function.
Sandbox pages: `pay-test-sandbox-3`, `pay-test-sandbox`, `pay-test-sandbox-2`, `pay-test-sandbox-5`, `pay-test-5`.
When detected, email subject gets `[PureBrain Seed TEST]` prefix, body gets yellow banner:
"THIS IS A SEED TEST FROM JARED OR PURE TECHNOLOGY"

### Change 3: UUID at top of seed email
Session UUID now appears as the FIRST element in the seed email HTML body,
inside a styled monospace block with blue border. Previously it was buried in the table.

### Change 4: `.app.purebrain.ai` domain transform
Changed birth complete webhook URL rewrite from `{name}.purebrain.ai` to
`{ainame}{humanfirst}.app.purebrain.ai`. This keeps PureBrain branding, hides AICIV.
Pattern: `{ainame}{firstname}.app.purebrain.ai/?token=...`

### Template Created
`/tmp/magic-link-email-template.html` — sent to Jared for review.
Placeholders: `{{HUMAN_FIRST_NAME}}`, `{{CIV_NAME}}`, `{{MAGIC_LINK}}`
Dark theme, blue (#2a93c1) / orange (#f1420b) branding, pulsing CTA button, mobile-responsive.
Status: PENDING JARED'S APPROVAL — do not auto-send.

---

## Architecture Notes

### Flow sequence (full pipeline)
1. Customer pays on payment page
2. Chatbox collects: AI name, full name, email, company, role, primaryGoal
3. On `questionnaire:complete` → `_forward_seed_to_witness()` fires (deduped by email)
4. Seed email → `aiciv-seed-inbox@agentmail.to` (Witness reads this)
5. Witness births the CIV, POSTs to `/api/birth/webhook` with magic link
6. Webhook stores entry in `birth_completions.jsonl`
7. Chatbox polls `/api/birth/portal-status/{container}` every 30s
8. When ready: button lights up with `ptc-portal-btn--pulsing` class
9. Customer clicks button → enters `{ainame}{firstname}.app.purebrain.ai`
10. Brevo sends welcome email via template ID 30

### Seed email target
`aiciv-seed-inbox@agentmail.to` — Witness processes seeds from this inbox.
Also CC'd: `witness-aiciv@agentmail.to`, `jared@puretechnology.nyc`

### Seed fire trigger
Only fires on: `questionnaire:complete`, `flow:complete`, `learn-more:complete`
(all three events carry email — email is Q2 in questionnaire, fires before Q3/Q4)
Dedup ensures only ONE seed email per customer email address per 24h.

### Log server service
`aether-logserver.service` (systemd) — enabled, auto-restart on crash.
Restart command: `sudo systemctl restart aether-logserver.service`
Health check: `curl -sk https://localhost:8443/api/health`

---

## Pending / Needs Jared Input

1. Email template approval — `/tmp/magic-link-email-template.html` sent to Telegram
2. DNS: `*.app.purebrain.ai` CNAME → Cloudflare proxy → Hetzner or local routing
   (This subdomain may not be configured yet — check with Jared before going live)
3. Brevo template ID 30 — verify template exists and uses `magic_link` param correctly
4. `.app.purebrain.ai` SSL cert — wildcard cert needed or Cloudflare handles TLS
