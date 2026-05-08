# Nightly Onboarding Pipeline Verification

**Date**: 2026-05-02 07:06 UTC
**Agent**: qa-engineer
**Status**: ALL SYSTEMS OPERATIONAL

---

## Page Checks (HTTP Status)

| Page | Status | Result |
|------|--------|--------|
| purebrain.ai/ | 200 | PASS |
| purebrain.ai/insiders/ | 200 | PASS |
| purebrain.ai/awakened/ | 200 | PASS |
| purebrain.ai/partnered/ | 200 | PASS |
| purebrain.ai/unified/ | 200 | PASS |
| purebrain.ai/home-test/ | 200 | PASS |
| purebrain.ai/home-test-sandbox/ | 200 | PASS |
| purebrain.ai/home-test-live-1/ | 200 | PASS |

**Result: 8/8 pages returning HTTP 200**

---

## Infrastructure Checks

| Service | Status |
|---------|--------|
| agentmail_monitor | PASS (running) |
| agentmail_general | PASS (running) |
| portal_server | PASS (running) |
| purebrain_log_server | PASS (running) |

---

## Workers Health

| Worker | Status | Details |
|--------|--------|---------|
| onboarding-api.purebrain.ai | OK | magic_links_count: 2 |
| welcome-email-api.in0v8.workers.dev | OK | db: connected |
| referrals-api.purebrain.ai | OK | db: purebrain-referrals |

---

## DNS

| Record | Value | Result |
|--------|-------|--------|
| test.app.purebrain.ai | 37.27.237.109 | PASS |

---

## Recent Activity

### Seeds
- Last seed activity: 2026-04-27 (Michael Foley - BLOCKED due to missing AI name)
- Guard working correctly: placeholder names rejected

### Magic Links
- Last activity: 2026-04-30 (HopVerify test, sandbox bypass for jared@puretechnology.nyc)

### Welcome Emails
- Last sent: 2026-04-30 to jared@puretechnology.nyc (AI=HopVerify)

---

## Jay Whitehurst / Sara Arnell Check

**No payment, seed, or verification activity found for either name.**

---

## Held Seeds (Attention Required)

| Date | Name | Email | Reason |
|------|------|-------|--------|
| 2026-04-27 | Michael Foley | michaeltfoley@hotmail.com | AI name = "(not yet named)" |

This seed remains held. The guard is working as designed - no seed sends without a valid AI name.

---

## Summary

- All 8 payment/onboarding pages: PASS
- All 4 local processes: PASS
- All 3 CF Workers: PASS
- DNS resolution: PASS
- Seed guard: OPERATIONAL (blocking unnamed AIs correctly)
- No Whitehurst/Arnell activity detected

**Overall Pipeline Status: GREEN**
