# CTO: Container -> CF Migration Plan

**Date**: 2026-04-20
**Type**: teaching + synthesis
**Topic**: Comprehensive migration plan for 8 tunnel-dependent subdomains to CF Workers/Pages/D1

## Key Architectural Findings

### What CAN migrate (5 of 8)
1. **cc.purebrain.ai** -> Already on CF Pages as 777.purebrain.ai (DNS swap only)
2. **comms.purebrain.ai** -> Likely dead/unused, sunset candidate
3. **paypal.purebrain.ai** -> Perfect CF Worker candidate (webhook = HTTP POST)
4. **video.purebrain.ai** -> Split: UI to CF Pages, transcode stays VPS
5. **cal.purebrain.ai** -> Already dead (530 errors), just remove

### What MUST stay on VPS (3 of 8)
1. **app.purebrain.ai** -> WebSocket to tmux, Claude Code session control, filesystem JSONL reads. This IS the AI brain interface. No CF alternative exists.
2. **api.purebrain.ai** -> Seed email pipeline (CONSTITUTIONAL), JSONL file writes, Gmail OAuth tokens. Extract read-only routes incrementally.
3. **surf.purebrain.ai** -> Headless Chromium browser automation (200-500MB/session). Browsers need real machines.

### Hard technical boundaries (CF Workers CANNOT):
- Run persistent processes (WebSocket to tmux)
- Access local filesystem (JSONL logs, SQLite DBs)
- Run headless browsers (128MB limit, no Chromium)
- Hold 30-minute stateful sessions (execution time limits)

## Patterns for Future

### Flag-gated cutover (from referral D1 migration)
- Deploy Worker with `USE_D1_X=false` flag
- Run both old and new in parallel
- Flip flag after data reconciliation
- Auto-fallback to old on Worker error

### Split migration pattern (from video plan)
- Read operations -> CF Worker (edge performance)
- Write/compute operations -> VPS (filesystem, FFmpeg)
- Frontend -> CF Pages (static, CDN)
- This avoids the "all or nothing" trap

## Blockers Found
- R2 credentials still missing (video migration)
- Referral D1 vs SQLite data reconciliation ($48.38 vs $61.51)
- Need to audit comms gateway usage before sunsetting

## Files
- Plan: `/home/jared/exports/portal-files/CONTAINER-MIGRATION-PLAN.md`
- cloudflared config: `/home/jared/purebrain_portal/aether-infrastructure/cloudflare/cloudflared-config.yml`
- Live config: `/etc/cloudflared/config.yml` (assumed -- based on systemd service)
