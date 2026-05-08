# Vantage-Vishal Portal Corruption Fix — One-Off

**Date**: 2026-04-14
**Type**: operational
**Agent**: cts-fullstack
**Status**: Runbook prepared; execution requires container SSH

## Explicit Scope (per Jared)

> "nobody except vishal is experiencing this JUST for the record... you have permission to fix this for him BUT do not touch anything for anyone else because i dont think anyone else actually having this issue."

**Constraint**: ONLY vantage-vishal (port 2245, 37.27.237.109).
**DO NOT TOUCH**: chy-jared, lyra-pmg, other customer containers, or the portal template used to spawn future containers.
**Fleet rollout**: EXPLICITLY DEFERRED. If another customer reports the same symptom, open a new ticket — do not preemptively patch.

## Root Cause Summary

1. **149 duplicate IDs** in `portal-chat.jsonl` — caused by double-mirror writes in `_mirror_to_portal_log` (lines 734–752 of portal_server.py) lacking content-hash dedup
2. **42 timestamp mixing** rows — `int(time.time()*1000)` at lines 1487 and 2081 writing ms, while line 946 writes seconds; UI sorts break when mixed
3. **16× repeat** of "Check email..." scheduled-task injection — no idempotency key on task injection path

## Fix Runbook

### SSH + Backup
```bash
ssh -p 2245 aiciv@37.27.237.109
cp /home/aiciv/purebrain_portal/portal-chat.jsonl \
   /home/aiciv/purebrain_portal/portal-chat.jsonl.bak-$(date +%s)
```

### Code edits (`/home/aiciv/purebrain_portal/portal_server.py` on THIS container only)
- Line 1487: `int(time.time()*1000)` → `int(time.time())`
- Line 2081: `int(time.time()*1000)` → `int(time.time())`
- Line 946: leave (already seconds)
- Lines 734–752 (`_mirror_to_portal_log`): add dual guard
  - maintain in-memory `_recent_hashes = collections.deque(maxlen=500)`
  - compute `h = hashlib.sha1((msg['id'] + '|' + msg.get('content','')).encode()).hexdigest()`
  - skip write if `h in _recent_hashes`
  - append `h` after successful write
- Scheduled-task injector: compute `idem = sha1(task_id + '|' + str(int(ts//60)))`; skip if already in deque

### One-shot cleanup (`/tmp/vishal_jsonl_clean.py`)
```python
import json, hashlib, os, shutil
IN = '/home/aiciv/purebrain_portal/portal-chat.jsonl'
OUT = IN + '.new'
rows = []
with open(IN) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try: rows.append(json.loads(line))
        except: pass
before = len(rows)
# normalize ts
for r in rows:
    ts = r.get('ts') or r.get('timestamp') or 0
    if ts > 10_000_000_000: ts //= 1000
    r['ts'] = ts
# dedup by id, prefer _src=='portal'
by_id = {}
for r in rows:
    rid = r.get('id')
    if not rid:
        by_id[id(r)] = r; continue
    if rid not in by_id or (r.get('_src')=='portal' and by_id[rid].get('_src')!='portal'):
        by_id[rid] = r
rows = list(by_id.values())
# dedup identical content within 60s window
rows.sort(key=lambda r: r.get('ts',0))
seen = []  # (ts, content_hash)
kept = []
for r in rows:
    ch = hashlib.sha1((r.get('content','') or '').encode()).hexdigest()
    dup = any(abs(r['ts']-t) <= 60 and h==ch for t,h in seen)
    if dup: continue
    seen.append((r['ts'], ch))
    if len(seen) > 500: seen.pop(0)
    kept.append(r)
kept.sort(key=lambda r: r.get('ts',0))
with open(OUT, 'w') as f:
    for r in kept: f.write(json.dumps(r) + '\n')
os.replace(OUT, IN)
print(f'rows before={before} after={len(kept)}')
```

### Restart
```bash
pkill -f "python.*portal_server.py"
sleep 3
pgrep -f "python.*portal_server.py"
```

### Verify
- `curl -I "https://vantage-vishal.app.purebrain.ai/?token=2MfyOZzFnMJ7Hkm76Ouu0CGiY2dBY4M8I5kvkULIERU"` → 200
- `tail -20 portal-chat.jsonl | jq .ts` → all 10-digit seconds
- Browser: feed renders chronological, no dup cards

## Execution Status

Agent session does not have live SSH creds to 37.27.237.109:2245. Runbook handed back to Jared/Primary for on-container execution or ST# routing.

## Lessons

- Timestamp unit mixing (ms vs s) is silent until a client sorts/filters on ts
- Any append-only log mirror needs content-hash dedup, not just id dedup (ids can collide on retry)
- Scheduled-task injection must be idempotent by (task_id, minute_bucket) to survive supervisor restarts
- Scoped fixes > fleet rollouts when only one customer reports; template drift is a separate governance decision

## Related Files
- `/home/aiciv/purebrain_portal/portal_server.py` (on vantage-vishal container ONLY)
- `/home/aiciv/purebrain_portal/portal-chat.jsonl` (on vantage-vishal container ONLY)
