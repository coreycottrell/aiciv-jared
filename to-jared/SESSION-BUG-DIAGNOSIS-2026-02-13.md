# Pure Brain Session Tracking Bug Diagnosis

**Agent**: pattern-detector
**Domain**: Bug Pattern Detection
**Date**: 2026-02-13

---

## Executive Summary

**Root Cause**: Client-server field name mismatch.

The Pure Brain web client sends `sessionId` (camelCase JavaScript convention), but the server expects `session_id` (snake_case Python convention). This is a classic API contract violation.

---

## Evidence

### Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Entries with `session_id: "unknown"` | 68 | 92% |
| Entries with valid session_id | 6 | 8% |
| **Total entries** | **74** | 100% |

### Valid Session IDs - All From Server Tests

All 6 entries with valid session_ids came from Aether server tests (IP: 89.167.19.20), NOT from production web traffic:

```
Line 5:  session_id: "test-session-001"        - browser-vision-tester test
Line 31: session_id: "ssl-test-1770919372"     - SSL diagnostic test
Line 32: session_id: "acgee-diagnostic-1770920786" - A-C-Gee diagnostic
Line 33-35: session_id: "jared-fulltest-1770927500" - Jared's full test
```

### Unknown Session IDs - All From Real Web Users

All 68 entries with `session_id: "unknown"` came from real web traffic (IPs: 108.35.12.204, 135.232.20.13, 74.179.68.9).

---

## Root Cause Analysis

### Server Code (Expects snake_case)

**File**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
**Line 298**:

```python
log_entry = {
    'session_id': data.get('session_id', 'unknown'),  # <-- Expects snake_case
    'messages': data['messages'],
    ...
}
```

### Client Code (Sends camelCase)

**File**: `/home/jared/projects/AI-CIV/aether/to-jared/purebrain-MERGED-v70.html`
**Lines 4125-4132**:

```javascript
const sessionId = 'lander_' + Date.now();

async function logConversationToBackend(eventType, data = {}) {
    try {
        const payload = {
            eventType: eventType,
            timestamp: new Date().toISOString(),
            sessionId: sessionId,  // <-- Sends camelCase (WRONG)
            ...
        };
```

### The Mismatch

| Layer | Field Name | Result |
|-------|------------|--------|
| Client sends | `sessionId` (camelCase) | Value: "lander_1739372123456" |
| Server reads | `session_id` (snake_case) | Value: (not found) |
| Server fallback | `data.get('session_id', 'unknown')` | Value: "unknown" |

The client IS generating valid session IDs (e.g., `lander_1739372123456`), but the server never reads them because it's looking for the wrong key name.

---

## Fix Options

### Option A: Fix Client-Side (Recommended - Minimal Change)

**File to modify**: The deployed HTML on purebrain.ai

**Change line ~4132** from:
```javascript
sessionId: sessionId,
```

**To**:
```javascript
session_id: sessionId,
```

**Pros**:
- Single-line change
- No server restart needed
- Maintains Python API convention

**Cons**:
- Requires re-deploying the HTML to purebrain.ai/Elementor

### Option B: Fix Server-Side (Accept Both)

**File to modify**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`

**Change line 298** from:
```python
'session_id': data.get('session_id', 'unknown'),
```

**To**:
```python
'session_id': data.get('session_id') or data.get('sessionId', 'unknown'),
```

**Pros**:
- Handles both conventions (forward/backward compatible)
- No client re-deploy needed

**Cons**:
- Requires server restart
- Slightly less clean

### Option C: Fix Both (Most Robust)

1. Server accepts both `session_id` and `sessionId`
2. Client uses `session_id` going forward

This provides backward compatibility while standardizing on snake_case for the API.

---

## Historical Note

Interestingly, an older version of the HTML (`purebrain-elementor-clean v7.html`) had this correct:

```javascript
const payload = {
    session_id: sessionId,  // <-- Correct snake_case
    event_type: eventType,
    messages: messages,
    ...
};
```

The bug was introduced when the code was refactored in the v70 MERGED versions, which switched to camelCase JavaScript conventions throughout the payload.

---

## Verification Steps After Fix

1. **Deploy the fix** (client or server side)
2. **Trigger a new conversation** on purebrain.ai
3. **Check the log file**:
   ```bash
   tail -5 /home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl | jq .session_id
   ```
4. **Confirm** session_id shows `lander_XXXXXXXXXX` instead of `unknown`

---

## Impact of Bug

Without proper session tracking:

- Cannot distinguish unique users
- Cannot track conversation continuity
- Cannot measure retention/return visits
- Cannot build meaningful analytics dashboards
- Cannot identify high-value prospects

**This is a P0 bug** - it blocks all meaningful analytics for Pure Brain.

---

## Files Referenced

| File | Path |
|------|------|
| Log server | `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` |
| Merged HTML v70 | `/home/jared/projects/AI-CIV/aether/to-jared/purebrain-MERGED-v70.html` |
| Conversation log | `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl` |
| Older working HTML | `/home/jared/projects/AI-CIV/aether/docs/from-telegram/purebrain-elementor-clean v7.html` |

---

## Recommended Action

**Option B (server-side fix)** is the fastest path to resolution since it:
1. Doesn't require Elementor/WordPress re-deploy
2. Can be applied immediately by restarting the log server
3. Is backward compatible with any existing clients

Single-line change in `purebrain_log_server.py` line 298:

```python
'session_id': data.get('session_id') or data.get('sessionId', 'unknown'),
```

Then restart the log server:
```bash
sudo systemctl restart purebrain-log-server  # or however it's managed
```

---

**Diagnosis complete. Ready for fix implementation.**
