# Portal Message Truncation — Root Cause & Fix 5

**Date**: 2026-03-11
**Agent**: cto
**Status**: Fix written, server reconstruction complete, awaiting restart

---

## Root Cause Summary

Portal messages were arriving truncated. Example: "ST# Both tasks complete. Task 1 (redirect): /how-it-works n" — cut off mid-sentence.

**Three bugs found in `ws_chat` poll loop (`portal_server.py`):**

### Bug 1 (Primary — "missing final bytes"): Growth threshold never re-fires
The send condition: `if prev_len < 0 or (msg_len > prev_len + 20 and msg_age > 0.8)`

When server first sends a message (prev_len = -1), it records `seen_texts[id] = current_len`.
If the message continues growing but the final burst is <=20 chars from the last sent version,
the condition never fires again. Client gets a partial version and never receives the complete text.

### Bug 2 (Compound): Stability branch persisted but didn't re-send
The old `elif stable_counts >= 2` branch wrote to portal log (correct) but never called
`await websocket.send_text(...)`. Even when correctly detecting message stability, the complete
text was NOT delivered to the client.

### Bug 3 (Client-side, not actually a problem): knownMsgIds dedup
Initially suspected the client would reject re-sends for known message IDs. Investigation of
`portal-pb-styled.html` lines 6436-6483 revealed the client ALREADY has an in-place update path:
when it receives a message with an already-known ID and role=assistant, it finds the existing
DOM bubble and updates `innerHTML` via `renderMarkdown`. No client changes needed.

---

## The Fix (Fix 5)

Added `stable_sent: set = set()` to `ws_chat`:

```python
stable_sent: set = set()  # IDs where final stable version was delivered

# During initial registration:
stable_sent.add(msg["id"])  # mark pre-existing messages already complete

# New elif branch in poll loop:
elif is_stable and msg_id not in stable_sent:
    # Message stopped growing. Re-send complete version.
    stable_sent.add(msg_id)
    if msg_id not in _portal_log_ids:
        _mirror_to_portal_log(msg)
    else:
        _overwrite_portal_log_entry(msg_id, msg)  # overwrite partial
    if prev_len >= 0 and msg_len != prev_len:
        seen_texts[msg_id] = msg_len
        await websocket.send_text(json.dumps(msg))
```

**Logic**: When `stable_counts[id] >= 2` (two consecutive polls same length = message complete)
and `id not in stable_sent`, the server re-sends the now-complete text. The client's existing
in-place update path handles updating the DOM bubble in-place. `stable_sent` prevents endless
re-sends on subsequent polls.

---

## Supporting Fixes (Pre-existing: Fixes 1-4)

- **Fix 1**: `stable_counts` tracks consecutive same-length polls
- **Fix 2**: `first_seen` dict skips first poll cycle for brand-new messages (prevents half-written delivery)
- **Fix 3**: `_src` tagging — session JSONL wins over portal-chat.jsonl in dedup (authoritative source)
- **Fix 4**: `_overwrite_portal_log_entry` atomic temp-file rewrite of portal log (prevents partial persistence)

---

## File Architecture

- `/home/jared/purebrain_portal/portal_server.py` — Starlette async server, port 8097
- `/home/jared/purebrain_portal/portal-pb-styled.html` — Client (no changes needed)
- `/home/jared/purebrain_portal/portal-chat.jsonl` — Persistence layer for portal messages
- `~/.claude/projects/*/` — Claude Code session JSONL files (authoritative message source)

## Restart Command
```bash
bash /home/jared/purebrain_portal/_validate_and_restart.sh
```

Or manually:
```bash
pkill -f portal_server.py; sleep 1
cd /home/jared/purebrain_portal
nohup python3 portal_server.py > /tmp/portal_server.log 2>&1 &
```

## Key Lesson

The growth threshold `msg_len > prev_len + 20` is a noise filter (prevents sending every
single character mid-stream). But it has a fatal edge case: if the message's final growth
burst is <=20 chars, the final version is never delivered. Fix 5 catches this by tracking
stability separately from the growth threshold and guaranteeing a final delivery on stability.
