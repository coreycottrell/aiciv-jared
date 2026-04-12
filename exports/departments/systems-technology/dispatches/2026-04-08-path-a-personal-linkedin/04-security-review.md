# Wave 2: SECURITY REVIEW

**Agent**: security-engineer-tech
**Wave**: 2 of 4 (BUILD -> **SECURITY** -> QA -> SHIP)
**Priority**: P1 CRITICAL - SHIP TODAY
**From**: dept-systems-technology
**Date**: 2026-04-08
**Blocks**: Wave 3 (QA) and Wave 4 (SHIP)

## Objective

Audit the Wave 1 deliverables BEFORE anything deploys. Your sign-off is required to proceed.

## Inputs to Review

1. Modified `exports/departments/systems-technology/apex-migration/pureapex-worker/src/linkedin.js`
2. New `tools/social_publisher.py`
3. New `social-publisher.service` systemd unit
4. Install runbook `INSTALL.md`

## Mandatory Checks

### A. Token Handling

- [ ] LinkedIn access tokens never written to `console.log`, `print()`, logs, or response bodies
- [ ] Refresh token logic handles failure gracefully (no infinite loops)
- [ ] Token refresh is atomic (no race where two requests both refresh)
- [ ] D1 updates use parameterized queries (no string interpolation)
- [ ] `INTERNAL_AUTH_TOKEN` never leaked in error messages or 500 responses

### B. Internal Auth

- [ ] Comparison is constant-time (not `===` on strings)
- [ ] 401 response reveals nothing about why it failed
- [ ] No bypass path (OPTIONS, preflight, query param, etc.)
- [ ] Secret is actually read from `env.INTERNAL_AUTH_TOKEN`, not hardcoded or from request body

### C. SSRF Protection on `image_url`

- [ ] `https://` only
- [ ] Hostname allowlist enforced (no regex holes like `purebrain.ai.evil.com`)
- [ ] Rejects IP literals, `localhost`, private ranges
- [ ] Rejects redirects to unsafe hosts (follow redirects manually and re-check, OR disable redirects)
- [ ] Image size cap (reject >10 MB to prevent DoS)
- [ ] Content-type check (must be `image/*`)

### D. Rate Limits

- [ ] 5 posts/hour ceiling on worker side
- [ ] 5 posts/hour ceiling on publisher side (defense in depth)
- [ ] Counter cannot be bypassed via clock skew or key collision

### E. Publisher Service

- [ ] `.env` is not world-readable (check: `stat .env`)
- [ ] Kill switch file check happens EVERY cycle before any action
- [ ] Signal handlers work cleanly
- [ ] No shell injection in log messages (user-controlled `post.content` must not be interpolated into shell)
- [ ] Telegram alert does not leak secrets (test with a simulated token leak)
- [ ] Idempotency check uses authoritative source (fresh poll, not cached)

### F. Systemd Unit

- [ ] `NoNewPrivileges=true`
- [ ] `ProtectSystem=strict`
- [ ] `ReadWritePaths` limited to logs + state file
- [ ] `ProtectHome` enabled
- [ ] Runs as non-root user
- [ ] Environment file is not world-readable

### G. Secret Rotation Plan

Document a rotation plan:
- How to rotate `INTERNAL_AUTH_TOKEN` (update Worker secret + `.env` + restart publisher)
- How to rotate LinkedIn OAuth tokens (re-run OAuth flow)
- Who has access to what

## Output

Produce a file at `exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/SECURITY-REVIEW.md` with:

```
VERDICT: APPROVED | APPROVED WITH CONDITIONS | BLOCKED

Findings:
- [SEV] finding 1 (with file:line reference)
- ...

Conditions (if any): ...
```

**Do NOT approve unless every A-G checkbox is satisfied.**

## Verification Required

- Show the SECURITY-REVIEW.md contents
- Memory written to `.claude/memory/agent-learnings/security-engineer-tech/2026-04-08--linkedin-publisher-audit.md`
