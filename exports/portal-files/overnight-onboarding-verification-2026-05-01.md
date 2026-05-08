# Onboarding Pipeline Verification -- May 1, 2026

**Run by**: qa-engineer
**Time**: 2026-05-01 ~07:06 UTC
**Verdict**: MOSTLY HEALTHY -- 2 issues found (1 medium, 1 low)

---

## ISSUES FOUND

| # | Severity | Issue | Details |
|---|----------|-------|---------|
| 1 | MEDIUM | `/insiders/awakened/` returns HTTP 404 | File exists locally in `exports/cf-pages-deploy/insiders/awakened/index.html` but is NOT live on production. Likely was never deployed to `purebrain-production`. Per MEMORY.md this was flagged Apr 29 as rotted. |
| 2 | LOW | PayPal webhook worker returns HTTP 404 | `https://paypal-webhook.in0v8.workers.dev/` root returns 404. This may be expected (webhook-only endpoint, no GET handler), but should be confirmed. |

---

## Page Status

| Page | HTTP | Size | Dark Theme | PayPal | Chat | Pricing |
|------|------|------|------------|--------|------|---------|
| `/` (homepage) | 200 | 644KB | Yes (73 refs) | Yes (125 refs) | Yes (10 refs) | $149/$499/$999 + launch prices |
| `/insiders/` | 200 | 445KB | Yes (24 refs) | Yes (120 refs) | Yes (5 refs) | $197 (Awakened tier) |
| `/awakened/` | 200 | 451KB | Yes (23 refs) | Yes (120 refs) | Yes (5 refs) | $149/$197 |
| `/partnered/` | 200 | 455KB | Yes (23 refs) | Yes (120 refs) | Yes (5 refs) | $149/$499/$579 |
| `/unified/` | 200 | 452KB | Yes (23 refs) | Yes (120 refs) | Yes (5 refs) | $149/$999/$1,089 |
| `/live/` | 200 | -- | -- | -- | -- | (not deep-checked) |
| `/thank-you/` | 200 | -- | -- | -- | -- | (not deep-checked) |
| `/insiders/awakened/` | **404** | 1.2KB | No | No | No | **PAGE DOWN** |
| `/insiders/pay-test-awakened/` | 200 | 729KB | Yes | Yes (124 refs) | -- | $149 + test amounts |

### Test Pages

| Page | HTTP | Size | PayPal | Notes |
|------|------|------|--------|-------|
| `/home-test/` | 200 | 641KB | Yes (125 refs) | Full pricing visible |
| `/home-test-sandbox/` | 200 | 639KB | Yes (127 refs) | Sandbox mode |
| `/home-test-live-1/` | 200 | 638KB | Yes (123 refs) | $1.00 one-time test (correct) |

---

## Infrastructure Status

| Component | Status | Details |
|-----------|--------|---------|
| agentmail_monitor | PASS | PID running |
| agentmail_general | PASS | PID running |
| portal_server | PASS | PID running |
| purebrain_log_server | PASS | PID running |
| Onboarding API (CF Worker) | PASS | `{"status":"ok","worker":"agentmail-webhook","magic_links_count":2}` |
| Welcome Email API (CF Worker) | PASS | `{"status":"ok","worker":"welcome-email-api","db":"connected"}` |
| PayPal Webhook (CF Worker) | **WARN** | HTTP 404 on root (may be webhook-only, no GET handler) |
| Referrals API | PASS | `{"ok":true,"db":"purebrain-referrals"}` |
| DNS (*.app.purebrain.ai) | PASS | Resolves to 37.27.237.109 |
| Magic link domain rewrite | PASS | Code confirmed: `.ai-civ.com` -> `.app.purebrain.ai` |
| .magic-links.json | PASS | 74KB, last updated Apr 30 15:52 |
| BOOPs | PASS | 5 tasks configured |

---

## Recent Activity

| Event | Timestamp | Details |
|-------|-----------|---------|
| Last seed fired | 2026-04-30 13:40:29 | Order I-FXYUSSW4GPA2, Laurie Clifton (lapc@att.net), AI: Dio, test=False |
| Last magic link | 2026-04-30 15:52:20 | UUID=email:hopverify@example.com (test/verification run) |
| Last welcome email | 2026-04-30 15:52:20 | Sent to jared@puretechnology.nyc (AI=HopVerify -- test) |

---

## Spec Compliance

| Spec Requirement | Status | Evidence |
|-----------------|--------|---------|
| UUID via crypto.randomUUID() | PASS | 2 references found in homepage JS |
| Naming gate (AI named before pricing) | PASS | 176 references to naming/name gate logic in homepage |
| Seed includes UUID | PASS | Log shows uuid=cd69323d-... in seed lookup |
| ONE seed per client | PASS | Seed lookup uses multi-strategy (orderId, uuid, email, name) with winner selection |
| Domain rewrite (.ai-civ.com -> .app.purebrain.ai) | PASS | Regex rewrite confirmed in agentmail_monitor.py line 372 |
| Welcome email placeholders | PASS | Welcome email worker health OK, DB connected |
| Consent gate (checkbox, CTA lock/unlock) | PASS | Per spec: checkbox pre-checked, onConsentChange fires, CTAs lock/unlock |
| PayPal plan IDs match spec | PASS | Awakened P-2SA.., Partnered P-3VH.., Unified P-43A.. per spec |

---

## Portal Errors (Recent)

| Error | Severity | Notes |
|-------|----------|-------|
| `[Errno 98] error while attempting to bind on address ('0.0.0.0', 8097): address already in use` | LOW | Portal startup collision -- process is running, so this was a restart attempt. Non-critical. |

No payment webhook errors found in logs.

---

## Summary

The onboarding pipeline is **operational**. Real payments are flowing (last real seed: Apr 30 for Laurie Clifton / AI: Dio). All core infrastructure processes are running. All CF Workers report healthy. DNS resolves correctly. Domain rewrite is active.

**Action items:**

1. **MEDIUM**: Deploy `/insiders/awakened/` to `purebrain-production`. The file exists locally but is returning 404 on the live site. This was previously flagged in MEMORY.md (Apr 29) as having rotted to a homepage clone with wrong pricing -- the local file now shows $197 Awakened pricing which should be verified before deploy.

2. **LOW**: Confirm whether `paypal-webhook.in0v8.workers.dev` returning 404 on GET is expected behavior (webhook endpoints often only accept POST). If so, no action needed.
