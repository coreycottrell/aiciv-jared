# Wave 3 QA: LinkedIn post-with-image Worker

**Date**: 2026-04-08
**Type**: operational
**Endpoint**: https://apex.purebrain.ai/api/linkedin/post-with-image

## Test Results

| Test | Description | Expected | Actual | Verdict |
|------|-------------|----------|--------|---------|
| 1a | Missing X-Internal-Auth header | 401 | 401 `{"success":false,"error":"unauthorized"}` | PASS |
| 1b | Wrong X-Internal-Auth value | 401 | 401 `{"success":false,"error":"unauthorized"}` | PASS |
| 2  | Off-allowlist image_url (evil.com) | 400 SSRF | 400 `{"error":"image_url rejected by SSRF guard","stage":"register"}` | PASS |
| 3  | Wrong content-type (sitemap.xml on allowed domain) | 400 invalid content-type | 401 `{"error":"LinkedIn not connected","stage":"register"}` | BLOCKED — register check runs before content-type fetch |
| 4  | LIVE FIRE 88% post | 200 with post_urn | 401 `{"error":"LinkedIn not connected","stage":"register"}` | FAIL — NO-GO |

## Root Cause (Test 4 Failure)

The worker cannot complete `linkedin/rest/images?action=initializeUpload` because it has no valid LinkedIn OAuth access token. The error surfaces at `stage:"register"` which is the LinkedIn asset registration step.

Possible causes:
1. LinkedIn OAuth token never stored in worker KV/D1/secret binding
2. Token expired and no refresh flow wired up
3. Wrong LinkedIn account connected (URN mismatch)
4. Missing `w_member_social` scope on the stored token

## Verdict: NO-GO for Wave 4

Auth gate + SSRF guard both PASS. Worker plumbing is healthy.
Blocker: LinkedIn OAuth connection not configured on the worker.

## Next Steps for ST#
1. Check worker secrets for `LINKEDIN_ACCESS_TOKEN` or KV namespace for OAuth store
2. Verify OAuth connection flow exists and has been run for Jared's LinkedIn account
3. Confirm scopes include `w_member_social` (required for UGC posts) and `r_liteprofile`
4. Re-run Test 4 after connection established

## Hard Rule Compliance
- No banner PNG read into context
- No retry on non-200
- Mozilla UA used on all curls
- Stopped at first live-fire failure
