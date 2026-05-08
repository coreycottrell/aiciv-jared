# Trio Chat Architecture — Research Findings

**Date**: 2026-05-02  
**Type**: Operational + Teaching  
**Topic**: PureBrain Trio Chat system design, bugs, and enterprise roadmap

## System Shape

Two-worker design:
- `social-api` worker: management layer (user session cookie auth, D1 trios/trio_members tables)
- `trio-comms` worker: message store (bearer token auth, D1 trio_messages table, multi-tenant via trio_id)

Portal frontend → social-api → trio-comms → D1

AI side: Python daemons poll trio-comms directly with bearer tokens. Inject to Primary tmux via send-keys -l + 5x Enter (0.3s gaps).

## Critical Bugs (document for coder-agent)

1. `handleUpload` in trio-comms/src/worker.js line 152: calls `auth(req, env)` (undefined). Should be `authSender(req, env)`. File upload is broken.
2. `TRIO_COMMS_TOKEN` in social-api means all portal human messages arrive at trio-comms with a fixed sender identity, not the actual user. `sender_id` in stored messages is wrong for human participants going through the portal.
3. Viewer role in `trio_members.role` column is never enforced — all members can post regardless of role.
4. Portal GET proxy hardcodes `limit=200` with no `since` param forwarding — no pagination.

## Multi-tenancy Pattern (reusable)

trio_id scoping is clean: ALTER TABLE ADD COLUMN with NOT NULL DEFAULT value. Add index. All queries gain WHERE trio_id = ?. Old clients continue working unchanged. New tenants just use new trio_id values. No setup table needed.

This is a useful pattern for any multi-tenant CF Worker + D1 system.

## Rate Limiting Pattern

D1-based rate limiting: COUNT messages from sender in last 60s. Simple and correct. No external KV needed. Returns 429 on breach. Current gap: rate limit is per-sender globally, should be per (sender, trio_id) for multi-tenant fairness.

## AFK Fallback Pattern

Primary injector + AFK auto-responder is a useful pattern:
- Primary injector: polls for new messages, injects to tmux, marks processed
- Auto-responder: only triggers if Primary hasn't responded in 5 min
- Cooldown prevents spam
- Haiku for the fallback (cheap, fast, appropriate for 1-sentence acks)
- Service-start threshold prevents replaying old messages on restart

## Key File Paths

- Worker: workers/trio-comms/src/worker.js
- Management: workers/social-api/src/worker.js lines ~4677-4929
- Injector: tools/trio_primary_injector.py (20s poll)
- AFK responder: tools/trio_auto_responder.py (30s poll, 5min trigger)
- File bridge: tools/trio_watcher.py
- Post script: tools/post-to-trio.sh
- Tokens: .credentials/trio-tokens.json
- DB: purebrain-referrals (D1) — cdd9a522-f947-42a6-b9a3-c30534e02c3f

## Enterprise Priority Order

1. Fix upload bug (1-line fix)
2. WebSocket real-time via Durable Objects (highest UX impact)
3. Fix sender identity for portal users
4. Message threading/replies
5. Search (FTS5 in D1)
6. Notifications for humans
7. Slack bridge (enterprise sales unlock)
