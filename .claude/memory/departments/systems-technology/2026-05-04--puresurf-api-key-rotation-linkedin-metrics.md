# PureSurf API Key Rotation — LinkedIn Metrics Collector Fix

**Date**: 2026-05-04
**Type**: operational + teaching
**Dept**: systems-technology (ST#)
**Trigger**: Weekly BOOP `linkedin-metrics-weekly` 401'd POST /sessions on jared-linkedin-fresh

## Root Cause

`tools/linkedin_metrics_collector.py` line 64 had a HARDCODED PureSurf API key
(`O_EnHpl-...w_bg`). That key was rotated/revoked. Current valid key lives in
`.env` as `BAAS_API_KEY` (`YCCs6vtG...6nuU`).

## Verification

```python
# hardcoded → POST /sessions → 401 {"detail":"Invalid API key"}
# env BAAS_API_KEY → POST /sessions → 200 {"session_id":"jared-linkedin-fresh","cookies_loaded":true,...}
```

Both keys reach `/health` (no auth required there) but only env key authenticates
real session creation. Easy to be fooled by health-check-only validation.

## Fix Applied

Replaced hardcoded key with env read (with dotenv fallback) in
`tools/linkedin_metrics_collector.py`. Pattern:

```python
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except Exception:
    pass
PURESURF_API_KEY = os.environ.get('BAAS_API_KEY') or os.environ.get('PURESURF_API_KEY')
if not PURESURF_API_KEY:
    raise RuntimeError('BAAS_API_KEY missing from environment')
```

Backup: `tools/linkedin_metrics_collector.py.bak.20260504`

## Other Files With Same Hardcoded Key (NOT yet patched — flag for follow-up)

```
scripts/execute-traveling-comments-apr6-v2.py:19
scripts/traveling-comments-apr6-targeted.py:20
scripts/execute-traveling-comments-apr6.py:19
tools/linkedin_newsletter_publisher.py:40
tools/linkedin_post_with_image.py:48
tools/browser-manager/test_baas_server.py:45
```

`linkedin_post_with_image.py` and `linkedin_newsletter_publisher.py` are
production-critical. They will 401 next time they run. **Must patch same
pattern in next BOOP cycle.**

## Verification Rerun

After fix, weekly collector got past auth cleanly:
- Session created: jared-linkedin-fresh ✓
- Cookies loaded: true ✓
- Then: NEW blocker — LinkedIn cookies expired (li_at session dead)
- This is the SECOND, separate chronic issue documented in
  `2026-04-05--linkedin-li-at-expired-diagnosis.md` and listed in
  `project_chronic_unresolved_issues.md`

So: API auth FIXED. Metrics collection still blocked, but on a different
known issue (LinkedIn login refresh required for jared-linkedin-fresh
profile via PureSurf UI).

## Teaching for Future Agents

1. **Hardcoded creds in tools/ are landmines.** Audit and migrate to .env.
   Repo grep `grep -rn "API_KEY\s*=\s*['\"]" tools/ scripts/` regularly.
2. **`/health` doesn't validate auth on most BAAS-style services.** Always
   probe with the actual privileged endpoint the tool uses (POST /sessions).
3. **Backup before edit, syntax-check after.** Standard discipline saved
   this from being a one-shot.
4. **Two-failure pattern**: when one BOOP fails, fixing the surface symptom
   often reveals a deeper issue. Don't claim "complete" until end-to-end runs.

## Files

- `tools/linkedin_metrics_collector.py` — patched (line 64 region)
- `tools/linkedin_metrics_collector.py.bak.20260504` — backup
- 6 other files still hardcoded — Day-3 default candidate

## Status

- [x] PureSurf API auth: fixed
- [ ] LinkedIn cookies refresh: BLOCKED on Jared (manual login via surf.purebrain.ai UI for jared-linkedin-fresh)
- [ ] 6 other hardcoded-key files: queued for next ST# BOOP
