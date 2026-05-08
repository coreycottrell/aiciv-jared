# Hancock Law Full QA Audit

**Date**: 2026-05-07
**Type**: operational
**Topic**: Full QA audit of legal.purebrain.ai Hancock Law platform

## Key Findings

- **56 API endpoints** discovered and tested via live API
- **2 CRITICAL**: Stored XSS (no server-side sanitization) + All AI endpoints broken (return "Generation failed")
- **5 HIGH**: No token expiry, no rate limit on AI endpoints, no session management, no password change, negative pagination accepted
- **4 MEDIUM**: Empty search returns all clauses, inconsistent error params, empty comm body, empty HR compliance response
- **5 LOW**: Aggressive login lockout (1hr), batch review always 0 risk, 10K query CF error, API key permissions not enforced, audit log empty

## What Worked Well
- Firm data isolation is solid (tested with 2nd firm account)
- CORS locked to legal.purebrain.ai (not wildcard)
- Login rate limiting fires at ~8 attempts (HTTP 429)
- SQL injection payloads returned safe results
- Frontend esc() function handles HTML entities on render
- 301K clause search + CourtListener caselaw proxy both functional

## Dead Ends
- Worker source code not found at /home/jared/projects/AI-CIV/aether/workers/hancock-law-api/ or /home/aiciv/repos/hancock-law/
- Could not test token expiry definitively (rate limit locked out re-login)
- DOCX export endpoint not tested (requires file download verification)

## Patterns
- AI failure is consistent across ALL generation endpoints -- suggests single root cause (missing/expired AI API key)
- Token is UUID+hex (68 chars), not JWT -- custom auth system
- API returns HTML page (not 401 JSON) for unauthenticated requests to data endpoints
- The frontend esc() function is the only XSS defense -- no server-side sanitization

## Files
- Report: /home/jared/exports/portal-files/HANCOCK-LAW-QA-AUDIT-2026-05-07.md
