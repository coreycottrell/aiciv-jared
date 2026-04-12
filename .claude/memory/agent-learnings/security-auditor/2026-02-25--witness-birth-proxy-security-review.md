# Memory: Witness Birth Proxy — Security Review Findings

**Date**: 2026-02-25
**Agent**: security-auditor (via doc-synthesizer memory-write BOOP)
**Type**: security-review
**Topic**: 10 findings from proxy endpoint security review (3 routes in purebrain_log_server.py)

---

## Context

Three proxy endpoints built in `tools/purebrain_log_server.py` to route purebrain.ai chatbox birth API calls to Witness (104.248.239.98:8099) via our HTTPS VPS (89.167.19.20:8443). This avoids mixed-content and CORS issues.

## Findings Summary (10 total)

| Severity | Count | Status |
|----------|-------|--------|
| HIGH     | 1     | FIXED  |
| MEDIUM   | 4     | FIXED  |
| LOW      | 3     | FIXED  |
| INFO     | 2     | NOTED  |

### P0 Fixes Applied
1. **CORS restricted** — was `*`, now locked to `purebrain.ai` origins only
2. **Real IP extraction** — `X-Forwarded-For` / `X-Real-IP` headers used for rate limiting
3. **Rate limits on all 3 endpoints** — prevents abuse of proxy as open relay
4. **Body size cap** — prevents large payload abuse
5. **Raw passthrough removed** — responses sanitized

### Key Pattern: Proxy Security Checklist
When building proxy endpoints that forward to external services:
- [ ] CORS: Lock to known origins (never `*` in production)
- [ ] Rate limiting: Per-IP limits on all routes
- [ ] Body size: Cap request bodies
- [ ] IP extraction: Use forwarded headers behind reverse proxy
- [ ] Response sanitization: Don't blindly forward upstream responses
- [ ] Timeout: Set upstream request timeouts to prevent hanging
- [ ] Logging: Log proxy requests for audit trail

## Status
All P0/P1 fixes applied. Awaiting Jared approval for deployment (log server restart + chatbox v4.4 to WP pages 688/689).
