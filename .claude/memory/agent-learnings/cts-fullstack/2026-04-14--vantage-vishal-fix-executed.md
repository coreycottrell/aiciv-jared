# Vantage-Vishal Portal Fix — EXECUTED

**Date**: 2026-04-14
**Type**: operational
**Agent**: cts-fullstack
**Status**: Live fix completed on container

## What Happened

Executed jsonl cleanup + portal restart on `vantage-vishal` (37.27.237.109:2245).
Skipped the proposed global `sed` against `portal_server.py` after discovering 3 of the 4
`int(time.time() * 1000)` sites are legitimate (upload filename uniqueness at 1645, OAuth
expiry comparison at 2081, message-ID suffix at 947). Only line 1487 is arguably a
chat-timestamp use, and even it feeds a filename, not the chat sort key.

The 42 ms-timestamp rows in the jsonl came from an **older code path** (likely a prior
mirror that's since been removed) — no active code bug in current portal_server.py to patch.
The 150 dup-ID rows were historical artifacts. Fix was **data-only** (jsonl cleanup) plus
process restart to flush in-memory caches.

## Numbers

| Metric | Before | After |
|--------|--------|-------|
| portal-chat.jsonl rows | 1430 | 1172 (removed 258) |
| Duplicate IDs | 150 | 0 |
| Millisecond-ts rows | 42 | 0 |
| Content dups within 60s | 108 | 0 |
| portal_server.py PID | 1631734 (4h 31m old) | 1682439 (fresh) |
| External HTTP | n/a | 200 OK, 94ms |

## Key Gotchas Discovered

1. **`pkill -f "python.*portal_server.py"` in SSH one-liner KILLS YOUR OWN SHELL** —
   because the bash command line itself contains the pattern. Use exact PID: `kill $PID`.

2. **Portal ignores SIGTERM** — waited 11+ seconds, no exit. Had to SIGKILL.

3. **`restart.sh` on the container has a stale path** — hardcodes `/home/jared/...`
   instead of `/home/aiciv/...`. Would fail silently on respawn. Jared should fix or delete.

4. **No supervisor/systemd** — portal PPID is 1 (init = entrypoint.sh), must be manually
   restarted with `setsid nohup python3 portal_server.py >> portal.log 2>&1 < /dev/null & disown`.

5. **`ssh -o BatchMode=yes`** is essential so auth failures don't hang the tool.

6. **Backup before any destructive op** — saved `portal-chat.jsonl.bak-1776197779` and
   `portal_server.py.bak-1776197779` on the container. Rollback = `mv .bak- original`.

7. **Read the code before running sed** — prior runbook said "sed the 3 sites", actual
   grep found 4 sites and 3 of them were NOT bugs. Would have broken uploads and OAuth.

## Files Touched on Container

- `/home/aiciv/purebrain_portal/portal-chat.jsonl` — cleaned (1172 rows)
- `/home/aiciv/purebrain_portal/portal-chat.jsonl.bak-1776197779` — backup
- `/home/aiciv/purebrain_portal/portal_server.py.bak-1776197779` — backup (code unchanged)
- `/tmp/vishal_jsonl_clean.py` — cleanup script (can reuse)

## NOT Done (deferred)

- Dedup hardening inside `_mirror_to_portal_log` (prior diagnosis may be stale — would
  need fresh read of current lines 734–752 before editing)
- Scheduled-task injector idempotency — same reason
- Rollout to other containers — EXPLICITLY SCOPED OUT per Jared

## Related

- Prior runbook: `.claude/memory/agent-learnings/cts-fullstack/2026-04-14--vantage-vishal-portal-fix.md`
- Container: vantage-vishal, 37.27.237.109:2245
