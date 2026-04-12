# CTO Memory: Portal Message Truncation — Root Cause & Fix Architecture

**Date**: 2026-03-11
**Type**: teaching
**Topic**: Portal WebSocket polling + JSONL streaming race condition — message truncation bug

---

## The Bug

Messages in portal appear cut off mid-sentence (e.g. "I had a background agent wor") but show fully on hard refresh.

---

## Root Cause — Three Compounding Failure Modes

### Primary Cause: "Lock-In on First Significant Growth" Race

The server poll loop in `ws_chat` (portal_server.py line 734):

```python
if prev_len < 0 or (msg_len > prev_len + 20):
    seen_texts[msg_id] = msg_len
    _mirror_to_portal_log(msg)  # <-- PERSISTS TO DISK HERE
    await websocket.send_text(json.dumps(msg))
```

The problem sequence:

1. Claude is mid-response. JSONL log has partial text: "I had a background agent wor" (28 chars).
2. Poll fires (every 0.8s). `msg_len=28`, `prev_len=-1`. Condition true. Sets `seen_texts[id] = 28`.
3. Message is MIRRORED to `portal-chat.jsonl` with the PARTIAL text.
4. Message is sent over WebSocket to the client.
5. Client renders it, registers `msg.id` in `knownMsgIds`.
6. Claude finishes writing. JSONL now has full text (500 chars).
7. Next poll: `msg_len=500`, `prev_len=28`. `500 > 28 + 20 = true`. Sends update.
8. **Client receives update — but `knownMsgIds.has(msg.id)` is true**, so the `startStreamingMessage()` path is skipped.
9. Instead it hits the **in-place update branch** (line 6436), which DOES work for in-place.
10. BUT: the `_mirror_to_portal_log` at step 3 already wrote the PARTIAL TEXT to portal-chat.jsonl.
11. On hard refresh: `loadChatHistory()` reads portal-chat.jsonl... gets the partial text OR the final (depending on which JSONL wins deduplication).

### Secondary Cause: JSONL File Cache Race

The file cache in `_parse_jsonl_messages_from_file` (line 352-354):

```python
if cached and cached[0] == mtime and cached[2] == fsize:
    return cached[1]
```

When Claude is actively writing to the JSONL, multiple writes can happen within the same 0.8s poll window. The cache key is `(mtime, fsize)`. If the OS batches writes and mtime doesn't update between polls, the cache returns a stale (partial) snapshot. The poll then sends the stale version.

### Tertiary Cause: mirror_to_portal_log Writes Too Early

`_mirror_to_portal_log` is called at the SAME time as `send_text`, before the message is confirmed complete. This means portal-chat.jsonl gets the intermediate (truncated) version locked in. On reconnect or refresh, this partial version is loaded from portal-chat.jsonl, not the final JSONL.

The deduplication in `_parse_all_messages` keeps the LAST occurrence by index — but portal-chat.jsonl messages sort by timestamp, and if the partial was written first with an earlier timestamp it may appear before the final JSONL version, meaning the final JSONL wins dedup. This is why refresh SOMETIMES shows the full message — dedup rescues it. But not always.

---

## The Fix Architecture

### Fix 1: Do Not Mirror to Portal Log Until Message is Stable

Only call `_mirror_to_portal_log` when the message appears COMPLETE (not still growing). Simple heuristic: require two consecutive polls to show the same length before persisting.

```python
# In ws_chat: add a "stable count" tracker
stable_counts: dict[str, int] = {}  # id -> consecutive polls at same length

# In the poll loop:
if prev_len == msg_len:
    stable_counts[msg_id] = stable_counts.get(msg_id, 0) + 1
else:
    stable_counts[msg_id] = 0

# Only mirror once message has been stable for 2 polls (~1.6s)
if stable_counts.get(msg_id, 0) >= 2 and msg_id not in _portal_log_ids:
    _mirror_to_portal_log(msg)
```

### Fix 2: Raise the Growth Threshold or Add a Minimum Message Age

The threshold `msg_len > prev_len + 20` fires on the VERY FIRST poll for any new message, even if it's mid-stream. Consider: do not send the message at all until it has been seen at least twice, OR raise the threshold significantly (e.g., `+ 200`) for initial send.

Better: add a `first_seen` timestamp per message ID and require a minimum age of 2s before first delivery:

```python
first_seen: dict[str, float] = {}  # id -> time.time() when first encountered

# In poll loop:
if msg_id not in first_seen:
    first_seen[msg_id] = time.time()
    continue  # Always skip on first sight, wait for next poll

msg_age = time.time() - first_seen[msg_id]
if prev_len < 0 or (msg_len > prev_len + 20 and msg_age > 1.5):
    ...send...
```

This adds 0.8-1.6s latency to message delivery (negligible for real-world use).

### Fix 3: In-Place Update Path Must Also Update Portal Log

When the client receives an in-place update (msg.id in knownMsgIds), the server must also update the portal-chat.jsonl entry. Current code only writes it once. Add an "overwrite existing entry" path to `_mirror_to_portal_log`:

```python
def _mirror_to_portal_log(msg, overwrite=False):
    mid = msg.get("id")
    if not mid:
        return
    if mid in _portal_log_ids and not overwrite:
        return
    # If overwrite: rewrite the full file replacing this entry
    # (or use a temp file + atomic rename for production safety)
```

### Fix 4: Deduplication in _parse_all_messages Should Prefer Session JSONL Over Portal Log

Currently dedup keeps the last occurrence by sort order. Session JSONL messages should always win over portal-chat.jsonl for the same ID, because the session JSONL has the authoritative final text. Change the merge priority:

```python
# Tag messages by source before sort
for m in session_msgs:
    m['_src'] = 'session'
for m in portal_msgs:
    m['_src'] = 'portal'

# In dedup: when same ID appears, session always wins
seen_idx = {}
for i, m in enumerate(all_messages):
    existing = seen_idx.get(m['id'])
    if existing is None:
        seen_idx[m['id']] = i
    elif m['_src'] == 'session':
        seen_idx[m['id']] = i  # session always overwrites portal
```

---

## Files to Modify

- `/home/jared/purebrain_portal/portal_server.py` — all server-side fixes
- `/home/jared/purebrain_portal/portal-pb-styled.html` — no client changes needed (in-place update path works correctly)

---

## Testing Protocol

After applying fixes, verify:

1. Send a long message (500+ chars). Confirm portal shows it fully without refresh within 2-3s.
2. Send 5 messages rapidly. Confirm all 5 appear fully, none truncated.
3. Disconnect/reconnect WebSocket mid-response. Confirm full message shows on reconnect.
4. Hard refresh during active response. Confirm no truncation in history load.
5. Send message, wait for it to appear fully, then hard refresh. Confirm persisted version is full text.
