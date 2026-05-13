# Thread B Phase 1 Days 6-7 — AI tokens + room widget + compression toggle SHIPPED

**Date**: 2026-05-13
**Type**: operational
**Topic**: Shipped CTO Decision 1 (per-AI tokens) and Decision 2 (reuse existing human auth) for Thread B Phase 1.

## What Worked

### Worker (trio-comms)

1. **Async authSender with fast-path** — the 4 legacy fixed tokens hit zero D1
   queries. Only customer AI tokens fall through to `await env.DB.prepare(...).first()`.
   Verified by probing both legacy `/trio/messages` (Aether token) and a synthetic
   inserted ai_tokens row plaintext bearer; both 200 with correct sender_id format.

2. **Migration 0005-ai-tokens.sql** applied via
   `npx wrangler d1 execute purebrain-referrals --remote --file migrations/0005-ai-tokens.sql`.
   Idempotent (`CREATE TABLE IF NOT EXISTS`). Verified table exists post-apply.

3. **/rooms/ensure mint-and-return** — generates `crypto.getRandomValues(32)` per AI,
   base64url-encodes (43 chars), sha256-hashes into D1, returns plaintext in
   `ai_tokens[]` exactly ONCE. Idempotent: existing tokens for (customer_id, ai_id)
   are NOT regenerated (returned with `already_minted: true, token: null`).

4. **was_compressed flag** stored in R2 customMetadata + returned in upload response.
   Verified with E2E probe — both `true` and `false` round-tripped cleanly.

5. **Audio MIME** (`audio/mpeg`, etc.) already in ALLOWED_MIME_EXACT from Days 4-5;
   verified end-to-end upload returns 201.

### Widget

1. **Compression pattern port** from `/home/jared/purebrain_portal/portal-pb-styled.html`
   lines 5660-5840 (CSS) + 10940-11070 (JS) translated cleanly to `room-widget.js`.
   Key functions: `_compressImage`, `_compressText`, `_estimateCompressedSize`,
   `_showUploadModeModal`. JPEG quality 0.7, max 1920px width preserved.

2. **Default-compress heuristic** per Jared spec 2026-05-13:
   - Image >= 5MB → recommend Original
   - Image < 5MB / PDF / text / docx → recommend Compressed
   - .ai / .psd / .sketch / .fig → recommend Original
   - Audio → no compression (already compressed format)

3. **Polling cadence** via Page Visibility API: 5s visible, 30s hidden.
   `scheduleNextPoll()` re-evaluates on `visibilitychange`.

4. **Sender identity rendering**: parses `ai:{customer_id}:{ai_id}` → capitalize(ai_id),
   `human:{email}` → email local-part, legacy fixed → capitalize.

## Constitutional Gates Honored

- ✅ Morning curl gate (authHumanViaPortalProxy returns 401 not 500, social-api binding live)
- ✅ Pre-deploy `git status --porcelain workers/trio-comms/` empty
- ✅ Committed BEFORE wrangler deploy (constitutional)
- ✅ Pushed to origin BEFORE deploy (per feedback_pttfullstack_must_push_commits_to_origin.md)
- ✅ Credential scan clean (no plaintext tokens in code/commits)
- ✅ D1 migration applied BEFORE worker code deploy (no orphan code path)
- ✅ Backward compat: legacy `/trio/upload` and `/trio/messages` still 200
- ✅ All `/media/{key}` URLs proxied through Worker (no raw r2.dev)

## Verification Outputs

```
PROBE 1: /health → {"ok":true,"version":"thread-b-phase1"} HTTP=200
PROBE 2: /trio/messages (Aether legacy token) → 200, array of recent msgs
PROBE 3: /rooms/{id}/messages bad bearer → 401 (async authSender clean)
PROBE 4: /rooms/{id}/upload audio MIME → 201 (allowlist working)
PROBE 5: /rooms/{id}/rotate-ai-token no internal-binding → 401 (gate works)
PROBE 6: /rooms/ensure no auth → 401
E2E AI token (synthetic): inserted ai_tokens row + probed plaintext → 200
E2E upload was_compressed=true → 201 + response includes was_compressed:true
E2E upload was_compressed=false → 201 + response includes was_compressed:false
E2E heartbeat → 200 + server_now timestamp
E2E presence → 200 + status:"online" for fresh heartbeat
E2E post message → 200 + seq:1 allocated
E2E read messages → 200 + message returns with correct sender+content+hash
```

## Deploy Receipts

- **Worker deploy ID**: `ca3baeb7-b880-43be-abdd-fa921e134357`
- **D1 migration**: 0005-ai-tokens.sql applied to remote purebrain-referrals
- **Git commit**: f2965be (referral-v1 branch)
- **Origin push**: a475875..f2965be referral-v1 -> referral-v1
- **Local HEAD == Origin HEAD**: YES (f2965bee839714b77aadd918a4225779f5d36a3d)
- **Files**:
  - `/home/jared/projects/AI-CIV/aether/workers/trio-comms/src/worker.js` (1000 lines)
  - `/home/jared/projects/AI-CIV/aether/workers/trio-comms/migrations/0005-ai-tokens.sql`
  - `/home/jared/projects/AI-CIV/aether/exports/duo-chat/room-widget.html`
  - `/home/jared/projects/AI-CIV/aether/exports/duo-chat/room-widget.js`

## What Was Out of Scope (Days 8-9 follow-up)

- `room_poller.py` (AI container daemon)
- `clients-api /internal/seed-ai-room-token` (token delivery to container)
- Customer portal `/room` route wiring + sidebar nav (server-rendered seat_count gate)
- T7 token rotation reliability test
- T8 human-auth bridge probe with real magic-link customer session

The widget is built and verified standalone; portal integration into purebrain_portal
(routes.py extension + template) is a separate task that touches the leader portal
that already has uncommitted drift (per git status — admin-clients.html, affiliate-portal.html
etc. M-status). Recommend Aether dispatch that portal-integration work in a clean session
after addressing those pre-existing drifts.

## Open Blockers for Days 8-9

1. **INTERNAL_BINDING_SECRET delivery path** (Path A vs B): the per-AI mint flow
   in `/rooms/ensure` returns plaintext to caller; clients-api needs a
   `/internal/seed-ai-room-token` endpoint to write `~/duo/room-config.json` in
   the customer container. The birth-pipeline secret-injection mechanism owner
   (capability-curator or admin-api) needs to confirm the path.

2. **Customer portal sidebar nav** — requires server-rendered `seat_count >= 2`
   check. Source unclear: clients-api D1 has clients table; does it have a `seat_count`
   column or is it derived from PayPal subscription tier? Need clarification from
   billing/clients-api owner.

3. **room_widget.html hosting**: standalone HTML created, but routing it onto
   `app.purebrain.ai/room` requires either (a) adding to `exports/cf-pages-deploy/`
   with a route mapping, (b) extending `purebrain_portal/custom/routes.py` to serve
   under FastAPI, or (c) building a small dedicated CF Pages site. Need decision
   from Aether on which path before Day 8.

## Memory Written
Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-13--thread-b-days-6-7-shipped.md`
Type: operational
Topic: Shipped Worker changes (async authSender + ai_tokens migration + mint-and-return + rotate + was_compressed + audio MIME) and standalone widget HTML/JS with portal-parity compression toggle for Thread B Phase 1 Days 6-7.
