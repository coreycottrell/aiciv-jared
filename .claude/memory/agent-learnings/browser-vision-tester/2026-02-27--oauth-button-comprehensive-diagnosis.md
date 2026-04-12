# Memory: OAuth Button Comprehensive Diagnosis — Three Root Causes Confirmed

**Date**: 2026-02-27
**Type**: teaching + synthesis
**Topic**: Complete diagnosis of OAuth button failure on pay-test-2 and pay-test-sandbox-2

---

## Summary

This is the third and most complete OAuth button diagnosis of the day. Synthesizes all prior findings.

## Root Cause 1: CSP Blocks Direct IP Fetch (Browser-side)

WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443' on BOTH pages.
WordPress CSP connect-src does NOT whitelist 89.167.19.20:8443.
Browser blocks the fetch before it leaves. CSP error in console.
Fix: Change WITNESS_WEBHOOK_HOST to 'https://api.purebrain.ai' (IS in CSP whitelist).

## Root Cause 2: Witness Server DOWN (Backend)

104.248.239.98:8099 = completely unreachable (HTTP 000, connection refused/timeout).
Health check also times out. Server is not running.
Log server (89.167.19.20:8443) is UP but proxies birth/start to dead Witness.
api.purebrain.ai proxies birth/start to same dead Witness. Both return HTTP 000.
Fix: SSH to 104.248.239.98 and restart Witness service / Docker containers.

## Root Cause 3: Earlier — Container Pool Exhaustion

Earlier today (morning): Witness was UP but returned 503 pool_exhausted.
All aiciv containers (aiciv-06 through aiciv-10) were stuck/in-use.
Later: Server went fully down (000 instead of 503).
Fix: After restart, verify pool has available containers.

## The Two Pages Are Almost Identical

Page 689 (pay-test-2) vs Page 688 (pay-test-sandbox-2):
- ONLY difference: Sandbox banner HTML (22 lines, cosmetic, no functional impact)
- SAME WITNESS_WEBHOOK_HOST value on both
- SAME runBirthInit() function (MD5 confirmed)
- Different PayPal client IDs (correct: sandbox vs production)

## OAuth Architecture

There is NO static OAuth button. The button is created dynamically by PTC script ONLY after
/api/birth/start returns {"status":"url_ready","oauth_url":"https://claude.ai/oauth/..."}.
No Witness response = no button. This is not Google OAuth. It is Claude.ai OAuth.

## CSP Analysis (purebrain.ai connect-src)

Allowed: api.purebrain.ai, api.puremarketing.ai, pure-brain-dashboard-api.purebrain.workers.dev,
         www.paypal.com, *.paypal.com, www.sandbox.paypal.com, api.brevo.com, purebrain.ai,
         sageandweaver-network.netlify.app, *.wonderpush.com, cdn.jsdelivr.net
BLOCKED: 89.167.19.20:8443 (not listed)

## Fix Priority

1. URGENT: Restart Witness server at 104.248.239.98:8099
2. CODE: Change WITNESS_WEBHOOK_HOST on both pages to 'https://api.purebrain.ai'
3. VERIFY: Check container pool has available aiciv slots after restart

**Tags**: purebrain, pay-test-2, sandbox-2, oauth, birth-pipeline, witness-down, csp, pool-exhausted, root-cause, diagnosis
