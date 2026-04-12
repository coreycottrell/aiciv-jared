# Portal Message Truncation — 4 Fixes Deployed

**Date**: 2026-03-11
**Type**: bug-fix, pattern
**File Modified**: `/home/jared/purebrain_portal/portal_server.py`
**Backup**: `portal_server.py.bak-st-truncation-fix`

---

## Root Cause

Messages appeared cut off in the portal and only showed fully after hard refresh.

The bug: `_mirror_to_portal_log()` was called on every WS poll cycle as soon as text grew
by >20 chars. This meant a mid-stream partial message got persisted to `portal-chat.jsonl`
before the session JSONL had finished writing it. On refresh, the portal loaded the stale
truncated version from `portal-chat.jsonl`.

---

## 4 Fixes Applied

### Fix 1 — Do Not Persist Until Stable (ws_chat)
Added `stable_counts: dict[str, int]` tracking consecutive polls with no text growth.
A message only gets written to `portal-chat.jsonl` once `stable_counts[msg_id] >= 2`
(meaning ~1.6s of no growth = 2 x 0.8s poll). Live WS updates still stream to the
frontend — only persistence is gated.

### Fix 2 — Raise First-Send Minimum Age (ws_chat)
Added `first_seen: dict[str, float]` tracking when each message ID was first observed.
All brand-new messages are skipped on their first poll cycle (0.8s wait). Prevents
premature sends of barely-started messages.

### Fix 3 — Session JSONL Always Wins Deduplication (_parse_all_messages)
Changed dedup logic to tag messages by source (`_src = 'session'` vs `_src = 'portal'`).
When the same message ID appears in both session JSONL and portal-chat.jsonl, the session
JSONL version wins. Session JSONL is authoritative; portal-chat.jsonl is just a mirror.

### Fix 4 — Overwrite Portal Log on In-Place Update (_mirror_to_portal_log)
Added `_overwrite_portal_log_entry(mid, updated_msg)` — atomically rewrites
`portal-chat.jsonl` using temp-file + rename when a message that was already mirrored
grows further. Previously the entry was append-only; now it gets updated in place.

---

## Key Patterns Learned

- **Stability window pattern**: Require N consecutive polls with no growth before persisting
  streamed content. 2 polls x 0.8s = 1.6s stability window is sufficient for most AI responses.

- **Source tagging in dedup**: When merging from multiple sources (session JSONL + portal JSONL),
  tag entries at parse time with `_src` so the dedup loop can apply source priority rules cleanly.

- **Atomic file rewrite via temp+rename**: For in-place JSONL updates, write to `.jsonl.tmp`
  then `Path.replace()` — atomic on Linux, crash-safe.

- **First-poll skip pattern**: Never send a message on the first poll it appears. Wait one cycle
  (0.8s) so the source file has time to finish writing before we read/send.

---

## Verification

```
python3 -m py_compile portal_server.py  # Syntax OK
sudo systemctl restart aether-portal.service
curl http://localhost:8097/health
# {"status":"ok","civ":"aether","uptime":9}
```
