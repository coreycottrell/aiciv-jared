# LinkedIn PureSurf Session Idempotency Fix — 2026-05-01

**Status**: SHIPPED (software fix). Residual blocker: human one-time login required.
**Type**: teaching + operational
**Dept**: systems-technology (ST#)
**Trigger**: ST# unblock dispatch from Aether after MA# 2026-05-01 BOOP shipped 0 posts / 0 comments
**Independent verifier (paired BOOP, 24h)**: `operations-analyst` (OP#) — per `feedback_verifier_independence_audit_separation.md`

---

## What Was Diagnosed (Live State 2026-05-01)

Probed `surf.purebrain.ai` directly:
- `GET /sessions` → `{"sessions":[]}` — **NO leaked session right now** (the Apr 15 409 has cleared via TTL)
- `GET /api/v1/profiles/aether-linkedin/cookies` → `200` with **0 cookies total** (li_at, li_mc, JSESSIONID all absent)

**Conclusion**: The active blocker today is purely an empty cookie store on the `aether-linkedin` profile. The 409 leak the BOOP report worried about has self-cleared, BUT the *root cause that destroyed the cookies* was still in our code — and would destroy them again the moment a human re-logs in. So the fix had to land BEFORE asking for a re-login, not after.

The root-cause pattern (per memory `2026-04-06--cookie-overwrite-on-session-close.md`): when a PureSurf session is closed, it saves the browser's current cookies back to `cookies.json`. If the session landed on a login page (because li_at was invalid), it overwrites cookies.json with empty/login-page cookies, destroying the profile's auth state.

This had been happening on every dry-run discovery attempt for weeks. Each "fail-closed" log line in `logs/linkedin_icp_commenter.log` was actually a destructive event — it called `_puresurf_cleanup` which DELETE'd the session and saved login-page cookies over the profile.

## What Shipped

Three surgical fixes to `tools/linkedin_icp_commenter.py`:

### Fix 1: Pre-flight cookie check (`_puresurf_profile_has_li_at`)
Before creating a session, GET `/api/v1/profiles/{profile}/cookies` and confirm `li_at` is present. If not, log a clear error pointing at the human-login URL and return None. **No session is created → nothing can be destroyed.** Breaks the destruction loop.

### Fix 2: Idempotent ensure_session (409 retry path)
If POST /sessions returns 409 "already has an active session", we now:
1. Call new `_puresurf_force_close_for_profile()` which tries `DELETE /sessions/{profile_name}?save_cookies=false`, then falls back to listing sessions and deleting by session_id.
2. Sleep 2s.
3. Retry session create exactly once.

The `save_cookies=false` query param is critical — see Fix 3 reasoning. Force-closing a leaked session must NEVER overwrite cookies, since we don't know what state that session was in.

### Fix 3: Safe cleanup (`_puresurf_cleanup`)
Cleanup now reads `_PURESURF_SESSION_CACHE["logged_in_verified"]`:
- **True** (session reached `/feed/`) → normal `DELETE /sessions/{sid}` (cookies saved — they're good)
- **False** (login page or unverified) → `DELETE /sessions/{sid}?save_cookies=false` (cookies NOT saved — protect the profile)

The `logged_in_verified` flag is already set to `True` in `backend_puresurf_search` after a successful `_puresurf_check_logged_in` call. No new bookkeeping needed.

## Why This Took Weeks To Surface

The original code log line "fail-closed > fake data" felt safe but was actively corrupting the profile every run. The destruction was silent because the profile already had bad cookies — closing with empty cookies "looked like" no change. Memory `2026-04-06--cookie-overwrite-on-session-close.md` had described this exact failure mode but the fix was filed under "Feature Request for BaaS" instead of being implemented client-side. **Lesson: when memory says "feature request to vendor", check if a client-side guard is also viable. It usually is.**

## Verification (Live, 2026-05-01)

Ran `python3 tools/linkedin_icp_commenter.py --discover --persona agency-director --count 2 --dry-run`:

```
2026-05-01 18:44:02 [ERROR] [puresurf] PRE-FLIGHT FAIL: profile=aether-linkedin
  has 0 li_at cookies. Cannot start LinkedIn automation. Human one-time
  login required: open https://surf.purebrain.ai , select profile
  'aether-linkedin', log into linkedin.com manually, then re-run.
  (See memory: 2026-04-06--cookie-overwrite-on-session-close.md for why this happens.)
2026-05-01 18:44:02 [INFO] [DRY-RUN] segment=agency-director: 0 candidates ...
2026-05-01 18:44:02 [INFO] === ICP discovery DONE total_candidates=0 ...
```

Compared to the Apr 15 logs which showed `[puresurf] session_id=...` (session created → fail → DELETE) on every persona, the new code creates no session at all. **The destruction loop is broken.**

Syntax check: `python3 -m py_compile tools/linkedin_icp_commenter.py` → OK.

## Residual Blocker (For Aether/Jared)

**One human action required:**

1. Open `https://surf.purebrain.ai` in a browser
2. Select profile `aether-linkedin`
3. Manually log into linkedin.com (with whatever LinkedIn account this profile is meant to operate as — confirm with Jared which account)
4. Once logged in, close the surf.purebrain.ai tab cleanly (the manual session SHOULD save cookies — surf UI handles this differently from automation API)
5. Re-run: `python3 tools/linkedin_icp_commenter.py --discover --all --count 5 --dry-run` and confirm pre-flight passes (li_at found) and discovery returns >0 candidates

**This is the same one-time human-login step documented in 2026-04-15--linkedin-icp-puresurf-backend.md — and it was always going to be required.** The new software fix means we won't have to do it AGAIN every time a session goes wrong.

## Companion Issues NOT Fixed Here (Out of ST# Scope)

Today's MA# BOOP report listed four blockers. ST# owned 1 + 2 (cookies + session leak). The other two are MA# / PD# territory and need their own routes:

- **Blocker 3 (MA#)**: `configs/linkedin_icps.json` is empty. Even with cookies fixed, commenter has no targets. MA# must seed it OR run `--discover --all --auto-approve` to populate it (now that pre-flight will gate on cookies first).
- **Blocker 3b (MA#)**: PureSurf scheduled queue has 24 posts but none match today's slot timestamps — needs bulk reschedule into May 2026 dates.
- **Blocker 5 (PD#)**: `GET /sessions/{name}` returns 405 — PureSurf API needs a session-status endpoint. Open feature request to PT# for surf.purebrain.ai.

## Files Touched

- `/home/jared/projects/AI-CIV/aether/tools/linkedin_icp_commenter.py` — +60 lines, -3 lines (3 surgical fixes)

## Pattern For Future Agents

Whenever cleaning up a session against a third-party persistence anchor (cookies, OAuth tokens, etc.):

1. **Never blindly save state on close** — verify the state is good first. "Save what you have" is dangerous if "what you have" is corruption.
2. **Pre-flight before resource creation** — if the resource will fail, fail before allocation, not after.
3. **Idempotency on conflict** — 409 should always have an automated recovery path, not just a warning log.

## Pair-Verifier Assignment

OP# (`operations-analyst`) — please run within 24h:
1. Confirm `tools/linkedin_icp_commenter.py` still syntax-clean
2. Run dry-run discovery and confirm pre-flight gate fires correctly (no session created when cookies absent)
3. **After Jared completes one-time login**, confirm a real run produces >0 candidates AND that profile cookies are NOT wiped post-run (re-check `GET /api/v1/profiles/aether-linkedin/cookies` — li_at should still be present).
4. Write back to memory under `agent-learnings/operations-analyst/` with VERIFIED or REGRESSED status.

Per `feedback_verifier_independence_audit_separation.md` — verifier MUST be different agent than implementer.
