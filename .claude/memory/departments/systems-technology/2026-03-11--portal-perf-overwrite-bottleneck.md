# Memory: Portal Server Performance Bottleneck Pattern

**Date**: 2026-03-11
**Type**: gotcha + pattern
**Topic**: portal_server.py chat history slowness — _overwrite_portal_log_entry O(n) per message

## Root Cause Pattern

When a server endpoint:
1. Returns N items
2. Calls a "sync to disk" function on each item
3. That sync function does a full file read+rewrite for "already seen" items

Result: O(N * file_size) I/O per request. With N=100 and 3.2MB file: 5+ seconds per request.

## Specific Instance

`/api/chat/history` in portal_server.py calls `_mirror_to_portal_log()` for each of 100 returned messages.
For already-mirrored messages, calls `_overwrite_portal_log_entry()` which reads+rewrites portal-chat.jsonl (3.2MB, 7554 lines).
Measured: 53.5ms per call * 100 calls = 5.3 seconds.

## Fix Pattern

For "mirror on read" patterns where the goal is eventual consistency:
- Skip overwrites for already-tracked IDs (check set membership, don't rewrite file)
- OR batch all updates and do a single rewrite at end
- The atomic temp+rename pattern is correct for crash safety but must not be called N times per request

## Secondary Finding

JSONL session files: 825 files / 2.7GB in .claude/projects/. Portal scans top 10 by mtime = ~490ms per cold request.
Cache (mtime+size keyed) works correctly but busts when active Claude sessions write to JSONL files.
Reducing max_files from 10 to 3 would cut this to ~150ms.

## System State Note

VPS RAM: 3.7GB total, swap is essentially full (2047/2048MB used) from 9 concurrent Claude processes.
Not causing the portal slowness directly (vmstat swap I/O is low) but is a risk factor worth monitoring.

## Verification Command

```bash
PORTAL_TOKEN=$(cat /home/jared/purebrain_portal/.portal-token)
time curl -s -H "Authorization: Bearer $PORTAL_TOKEN" "http://127.0.0.1:8097/api/chat/history?last=100"
```
Baseline before fix: ~9-10 seconds
Target after fix: <1.5 seconds
