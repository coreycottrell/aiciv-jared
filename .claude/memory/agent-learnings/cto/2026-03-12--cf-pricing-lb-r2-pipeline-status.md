# CTO Memory: CF Pricing Analysis + R2/Zoom Pipeline Status

**Date**: 2026-03-12
**Type**: operational
**Topic**: Cloudflare Pro vs LB add-on analysis + Zoom pipeline one-time blocker

---

## Cloudflare Pricing (Current as of 2026-03)

- Pro plan: $20/month — WAF, image optimization, 50 page rules, priority support
- Load Balancing: SEPARATE add-on, starts at $5/mo for 2 origins + 60s health checks
- Load Balancing NOT included in any base plan tier
- Total if both: $25+/month

## Key Decision Framework for LB

Only worth buying CF Load Balancing if:
1. Multiple origin servers exist (need failover target)
2. Need geo-routing to direct traffic by region
3. Health check frequency matters (sub-60s failover)

Single VPS = no reason to buy. Health checks with no failover target = wasted money.

## R2 Video Pipeline: Current Blocker (2026-03-12)

Pipeline fully built: `tools/zoom_brainiac_pipeline.py` (7 steps)
- R2 credentials: confirmed in .env
- Zoom creds: confirmed in .env
- Training page: live, wired for new video URLs

ONE BLOCKER: Zoom OAuth app missing recording scopes.
- Missing: `cloud_recording:read:list_user_recordings` + admin variant
- Fix: Jared adds scopes at marketplace.zoom.us/develop/apps, re-authorizes
- After fix: run `python3 tools/zoom_brainiac_pipeline.py --manual`

## Soft Dependency

`ffmpeg` must be installed on VPS for transcode step. Verify with `ffmpeg -version`.
