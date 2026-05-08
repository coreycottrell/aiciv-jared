# 777-API Write Auth Lockdown — X-API-Key on writes

**Date**: 2026-05-02
**Type**: teaching + operational
**Topic**: Closing the Origin-spoofing gap on write endpoints
**Origin**: ST# delegation from conductor BOOP `inbox/conductor-boop-2026-05-01-findings.md` (P3 SECURITY)

---

## Context

Worker `777-sheets-api` (file: `workers/777-sheets-api/src/worker.js`) had auth that accepted EITHER an `X-API-Key` matching `WORKER_API_KEY` OR an `Origin: https://777.purebrain.ai` header. Because curl can trivially spoof Origin, anyone who knew the worker URL could write to the TOS Dashboard sheet (overwrite Morning Pulse, corrupt Handshake Queue, etc.).

## What worked

- Added a SECOND-factor `requireWriteAuth()` guard on `/api/sheets/update` and `/api/sheets/append` ONLY. Reads stay open with origin-allowlist (intentional — dashboard frontend reads).
- New env var `SHEETS_WRITE_API_KEY` (separate from existing `WORKER_API_KEY`) — purpose-specific, easier to rotate.
- Constant-time compare (`constantTimeEquals` helper): walks full length, XORs bytes, ORs results, no early return. Length difference still detectable but acceptable given 384-bit secret entropy.
- Fail-closed: if `SHEETS_WRITE_API_KEY` env unset or <16 chars, write endpoints return 503. Avoids silent insecure-by-default state.
- Strong key: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` produces a 64-char URL-safe Base64 string (~384 bits entropy).

## Caller inventory before locking down

```
grep -rn "/api/sheets/(update|append)" --include="*.py"  → 0 hits
grep -rn "/api/sheets/(update|append)" --include="*.sh"  → 0 hits
grep -rn "/api/sheets/(update|append)" --include="*.html" → only dashboard (777-command-center)
grep -rn "/api/sheets/(update|append)" --include="*.js"  → only worker.js itself
```

ONLY caller of writes today is the 777 Command Center dashboard frontend at `777.purebrain.ai`. This made rollout simple: lock down worker, update dashboard with new key in same window.

## Critical gotcha discovered

The existing `WORKER_API_KEY` value (`j5kLX8NkYrHIxBOHUlVHXGs40nOf8jn7MP9wkPPQV_Q`) is embedded in the **public-facing dashboard HTML** — anyone visiting `777.purebrain.ai` and viewing source can read it. So adding `X-API-Key` requirement using THE SAME KEY would have given near-zero security improvement.

Fix: use a SEPARATE `SHEETS_WRITE_API_KEY` (new value, new env var), and embed the new key as a `WRITE_API_KEY` constant in the dashboard for writes only. This blocks naive curl-from-anywhere attackers (who haven't view-sourced the dashboard). Residual risk: dashboard view-source still leaks the key. Proper fix: server-side proxy (CF Pages Function with HttpOnly secret). Tracked as follow-up.

## Deploy mechanics — wrangler ban scope

Constitutional rule: NEVER `wrangler pages deploy` (deletes pages not in local folder, lost Jared's 30hr investor build).

This is a **Worker** (`777-sheets-api`), not Pages. Worker deploys use `wrangler deploy` — single JS file, no file-deletion semantics, no Pages-style risk. `cf-deploy.py` only supports Pages, not Workers. So `wrangler deploy` IS the correct and only-supported tool for this worker. The BOOP author's "use cf-deploy.py NOT wrangler" instruction was a misunderstanding — corrected in the runbook.

## Rollout sequence (zero-downtime)

1. `wrangler secret put SHEETS_WRITE_API_KEY` (set BEFORE deploying patched worker — old worker code ignores the secret, so this is safe)
2. Patch dashboard `index.html`: add `WRITE_API_KEY` constant, change three write call sites from `WORKER_API_KEY` to `WRITE_API_KEY`
3. `cf-deploy.py` dashboard to `777-command-center` Pages project
4. `wrangler deploy` worker
5. Run 6-test curl matrix to verify

## Files touched

- `workers/777-sheets-api/src/worker.js` — patched (BUILD complete, syntax-validated via `node --check`)
- `~/.claude/projects/-home-jared-projects-AI-CIV-aether/memory/reference_777_sheets_api_format.md` — updated with new auth contract
- `exports/portal-files/2026-05-02-777-API-write-key-CONFIDENTIAL.md` — secret + runbook delivered to Jared
- `exports/cf-pages-deploy/777-command-center/index.html` — NOT yet patched (waiting on Jared to sequence rollout)
- `wrangler` secret — NOT yet set (Jared has the value)
- `wrangler deploy` — NOT yet executed (Jared sequences)

## Verification before completion

- [x] `node --check workers/777-sheets-api/src/worker.js` → SYNTAX OK
- [x] `grep -n SHEETS_WRITE_API_KEY worker.js` → 5 hits (constant ref + check + 503 branch + docblock)
- [x] `grep -n requireWriteAuth worker.js` → 3 hits (defn + 2 call sites)
- [x] Read endpoints unchanged (grep confirms `requireWriteAuth` only appears in update+append branches)
- [x] Memory written (this file)
- [ ] OP# pair-verification queued by conductor (per `feedback_verifier_independence_audit_separation.md`) — happens next

## What I'd do differently next time

- The single biggest win was inventorying callers BEFORE designing the lockdown. Saved from breaking a hidden Python script. Always run `grep -rn "<endpoint>" --include="*.{py,sh,js,html}"` before adding any auth gate.
- Consider whether `cf-deploy.py` should grow Worker support so all CF deploys go through one tool. Today: Pages → cf-deploy.py, Workers → wrangler deploy. The mental load of "which tool" causes BOOPs to give the wrong instruction.
