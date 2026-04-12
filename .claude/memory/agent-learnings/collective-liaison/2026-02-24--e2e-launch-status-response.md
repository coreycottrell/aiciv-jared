# Memory: E2E Birth Pipeline Launch Status — Aether Response to Witness

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational + teaching
**Topic**: Responded to Witness URGENT E2E coordination request. Chatbox v4.3 fully wired; one blocker found (HTTPS proxy 404). Option A/B unblock plan drafted.

---

## Situation

Witness sent urgent message: Corey and Jared want to launch E2E demo TOMORROW. Requested our implementation status + connectivity test results.

---

## Connectivity Tests Run

| Endpoint | Result |
|----------|--------|
| `http://104.248.239.98:8099/health` | 200 OK (v1.2.0 confirmed) |
| `http://104.248.239.98:8099/api/birth/start` POST `{}` | TCP connects, response takes >15s (expected — OAuth init is 29s+) |
| `https://api.purebrain.ai/api/birth/start` POST `{}` | 404 Not Found (BLOCKER) |

Key finding: The direct IP is live. The HTTPS proxy is NOT routing `/api/birth/*` to Witness.

---

## Implementation Status Found

Chatbox v4.3 is FULLY WIRED with complete birth pipeline integration:
- `runBirthInit()`: POST /birth/start → OAuth button → code input → POST /birth/code
- `runPortalButtonWatcher()`: polls portal-status, shows Enter button on ready:true
- All routes through `WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai'` (the broken proxy)
- Deployed to pages 688 and 689 with 8/8 verification checks passing

---

## The Blocker

`https://api.purebrain.ai/api/birth/*` returns 404. The nginx/Cloudflare proxy on purebrain.ai does not have a route for `/api/birth/` pointing to `104.248.239.98:8099`.

---

## Proposed Fix

**Option A (E2E test, immediate)**: Change WITNESS_WEBHOOK_HOST to direct IP in v4.3, redeploy to page 688 sandbox only. ~15 minutes.

**Option B (production)**: Add nginx `location /api/birth/` block proxying to `104.248.239.98:8099`. Proper production setup.

Recommendation in response: Option A for E2E NOW, Option B before public launch.

---

## Communication Used

1. Wrote full status to `/tmp/witness-aether-comms/from-aether-e2e-status.md` (local filesystem, readable by Witness via SSH to 89.167.19.20)
2. Notified via tmux injection to `witness-primary-20260223-214904` with `[from-Aether]` prefix
3. No commands injected — message only (Rule 2 compliance)

---

## Teaching: Proxy Routing vs Direct IP

When security engineering moves a webhook host from plain HTTP IP to HTTPS proxy (`api.purebrain.ai`), you MUST verify the proxy actually routes that path. This was a classic "fixed in code, not in infrastructure" gap. The chatbox code is correct; the infrastructure is not aligned.

Pattern: whenever WITNESS_WEBHOOK_HOST changes, run a connectivity test immediately to verify the proxy path exists end-to-end.

---

## Files Written

- Response: `/tmp/witness-aether-comms/from-aether-e2e-status.md`
- This memory: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--e2e-launch-status-response.md`
