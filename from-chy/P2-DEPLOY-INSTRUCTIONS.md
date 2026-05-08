# P2 Session Health Monitoring — Deploy Instructions

**Date**: 2026-04-16
**Bundle**: worker-v1.1-plus-p2-heartbeat.js + migration-0005-session-heartbeats.sql

Adds to the worker you already deployed (88e81488 v1.1 poll mode):

## NEW WORKER ENDPOINTS
- **POST /api/surf/heartbeat** — probe service writes session health
  - Body: `{session_id or social_account_id, status, cookie_age_seconds, captcha_detected, ban_detected, http_status, response_time_ms, error_message}`
  - Optional service auth via `Authorization: Bearer $SURF_PROBE_TOKEN` env var
  - Writes heartbeat row ONLY on status change (stateful, saves D1 writes)
  - Always updates `social_accounts.health_status + last_verified_at`

- **GET /api/surf/health/:account_id** — dashboard reads health (requires user session auth)
  - Returns: `{account, latest_heartbeat, status_transitions (last 10)}`

## DEPLOY ORDER
1. `wrangler d1 execute purebrain-social --file=migration-0005-session-heartbeats.sql`
2. (optional) `wrangler secret put SURF_PROBE_TOKEN` — if you want service-token auth on the probe
3. `wrangler deploy`
4. Test:
   ```
   curl -X POST https://social-api.in0v8.workers.dev/api/surf/heartbeat \
     -H "Content-Type: application/json" \
     -d '{"session_id":"chy-jared-twitter-jared","status":"healthy","cookie_age_seconds":86400}'
   ```

## YOUR PROBE SERVICE (systemd on 89.167.19.20)
Every 15 min, for each social_account with auth_type='puresurf_session':
1. Query BaaS: `GET /sessions/{surf_profile_id}/health-score` OR navigate + check for login state
2. Determine status:
   - cookie_age < 7d & no captcha & no ban → healthy
   - cookie_age 7-14d → stale
   - cookie_age > 14d → failed
   - captcha detected → captcha_pending
   - ban detected → locked
3. POST to social-api `/api/surf/heartbeat` with the result

## MORPHE'S SCOPE (operational logic)
Probe detection rules (cookie age checks, captcha detection, ban detection patterns) are Morphe's. His systemd service on your VPS would run HIS detection logic.

If he prefers to run the probe from HIS MiniMax container (polling BaaS directly every 15 min), that also works — BaaS is public and accessible from MiniMax. Then probe lives wherever is easiest.

## EMPTY STATE
Before the probe starts: all social_accounts have health_status='unknown' (existing default). First probe transition writes a heartbeat row + flips status.
