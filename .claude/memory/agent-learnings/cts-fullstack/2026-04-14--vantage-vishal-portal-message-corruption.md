# Vantage Portal Message Corruption — Vishal Doddanna

**Date**: 2026-04-14
**Type**: operational
**Topic**: Portal feed showing duplicates, wrong order, messages at bottom

## Environment
- Container: `vantage-vishal` on 37.27.237.109 port **2245** (aiciv user)
- Claude Code: **2.1.80** (NOT 2.1.77 regression — this is a different bug class)
- Portal server: `/home/aiciv/purebrain_portal/portal_server.py` (PID 1631734, started Apr 14 15:46)
- Storage: file-based `portal-chat.jsonl` (1,415 lines, 974KB) + JSONL session logs in `~/.claude/projects/-home-aiciv/`

## Evidence (from /api/chat/history)
- 1,415 rows in portal-chat.jsonl
- **149 duplicate IDs** written twice (same `id`, once with `_src=None ts=0`, once with `_src=portal ts=0`)
- **42 rows use millisecond timestamps** (13-digit) while 1,115 use second timestamps (10-digit). Same file, same role (assistant), same server.
- Example: one user prompt "Check email, texts, and voicemails for Vishal..." appears **16 times** with distinct IDs and timestamps.

## Root Causes

### Bug 1: Timestamp unit inconsistency (explains "messages at bottom")
`portal_server.py` has ~20 call sites using `int(time.time())` (seconds) but several write paths use `int(time.time() * 1000)` (milliseconds) — including line 1487 `timestamp_ms = int(time.time() * 1000)` and line 2081. When `_trim_portal_chat_log` sorts by `float(timestamp)`, ms rows become ~1000x larger and sink to the bottom/top of the rendered feed. The UI shows them as "future" messages.

### Bug 2: Duplicate mirror writes (explains "same messages keep showing up")
`_mirror_to_portal_log` guards against re-writes using an in-memory set `_portal_log_ids`. Messages with `timestamp=0` (older session entries) get mirrored from TWO codepaths — once without `_src` and once as `_src=portal`. The in-memory guard doesn't catch this because the two paths build different `msg` dicts for the same `id`. Result: 149 duplicate-id rows.

### Bug 3: Frontend de-dup is ID-only
WebSocket streaming (`ws_chat`) dedupes by `msg["id"]` only. But when the same text has different IDs (16x email check prompt), the frontend has no content-hash fallback and renders every instance.

## Why the 16x email-check duplication
User hit "send" once, portal `/api/chat/send` logged it, tmux injected it, Claude session logged it as user turn with its OWN uuid (different from portal's portal-{ms} id). Both get rendered. Then the session keeps picking up the same scheduled task trigger and logging it again each wake-up. No idempotency key on scheduled-task injections.

## Impact on Vishal
Feed is unusable — duplicates dominate, wrong timestamps push messages to bottom, assistant responses in session-JSONL get mirrored to portal-chat with `ts=0` so they appear at the top-oldest position, responses to his messages may be rendered before his message itself.

## NOT the cause
- Claude Code 2.1.77 rate-limit regression (this container is on 2.1.80)
- OAuth/credentials (the weft investigation memo confirmed tokens are isolated)
- Clock skew at OS level (host clock fine — it's a code-level unit bug)
- Storage corruption (JSONL parses cleanly; malformed entries are 0)

## Fix Plan (NOT YET APPLIED — needs ST# delegation)

1. **Hotfix**: Normalize all timestamps to seconds in `_save_portal_message`, `_mirror_to_portal_log`, and the `/api/chat/send` write path. Any `ts > 10**12` → `ts // 1000`.
2. **Backfill**: One-shot script to rewrite existing `portal-chat.jsonl` normalizing ms→s and collapsing duplicate IDs (keep the one with `_src=portal` if present).
3. **De-dup logic**: Add content hash `(role, first 200 chars of text, rounded minute)` as secondary dedup in both `_mirror_to_portal_log` AND frontend render.
4. **Scheduled-task idempotency**: When the BOOP/scheduled-task system injects the same "Check email..." prompt, include a `task_run_id` so repeated identical injections within N minutes are collapsed.
5. **Immediate relief for Vishal NOW**: Rewrite his portal-chat.jsonl with normalized timestamps + deduped IDs. Restart portal. He can use it within 5 minutes.
6. **Fleet audit**: This bug likely affects every customer on this portal version. Check all 13 containers on 37.27.237.109 for mixed ts units.

## Files to fix
- `/home/aiciv/purebrain_portal/portal_server.py` lines 1487, 2081 (ms→s)
- `/home/aiciv/purebrain_portal/portal_server.py` `_mirror_to_portal_log` (add content-hash dedup)
- Any `cfd_template/purebrain_portal/portal_server.py` in the provisioning template so new customers don't inherit it
