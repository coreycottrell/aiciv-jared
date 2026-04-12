# Witness Seed Spec Integration — sandbox-3 Birth Pipeline

**Date**: 2026-03-05
**Agent**: dept-systems-technology
**Type**: integration / fix

---

## Summary

Audited and patched the sandbox-3 birth pipeline to comply with Witness's two-file seed spec.

---

## Witness Requirements Recap

- **File 1**: `purebrain_*.json` — pre-purchase naming ceremony
  - AI must have chosen a name in conversation
  - Must have `session_id` or `capture_id`
  - Optional (fast): `metadata.civ_name`, `metadata.human_name`, `metadata.email`
- **File 2**: `pb-post-*.json` — post-payment Q&A profile
  - `messages[1]=name`, `[3]=email`, `[5]=company`, `[7]=role`, `[9]=goal`
- Files must be within 60 min of each other

---

## Findings

### File 2 (pb-post-*.json) — ALREADY WORKING
- Format confirmed matching Witness spec exactly
- `session_id` starts with `pb-post-` (e.g. `pb-post-34V39751PV812792D`)
- Messages at indices [1,3,5,7,9] correctly contain name/email/company/role/goal
- Both `/api/log-pay-test` and `/api/log-conversation` called on completion
- Status: **NO CHANGES NEEDED**

### File 1 (purebrain_*.json) — MOSTLY WORKING, OPTIONAL FIX APPLIED
- `session_id` EXISTS — format `purebrain_TIMESTAMP_RANDOMSTRING` — satisfies Witness requirement
- `ai_name` already present in `metadata.ai_name` — Witness can extract AI name
- `capture_id` NOT present — but `session_id` is sufficient per Witness spec
- **MISSING**: `metadata.civ_name` — optional fast field for Witness
- **MISSING**: `metadata.human_name`, `metadata.email` — NOT AVAILABLE at naming time (these come from post-payment flow)

### Webhook Endpoint (`/api/birth/webhook`) — WORKING
- Lives in `tools/purebrain_log_server.py` at the `/api/birth/webhook` route
- Accessible at `https://api.purebrain.ai/api/birth/webhook`
- Accepts `X-Witness-Secret: witness-secret-2026`
- Returns `{"ok": true}` on valid `birth_complete` events
- Handles: email de-dup, birth completions log, Brevo email, Telegram notification, subdomain routing

---

## Fix Applied

**File**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
**Change**: After optional fields are merged into log_entry, for sessions with `session_id` starting with `purebrain_`:
- Reads `metadata.ai_name` (already set by JS client)
- If present and `metadata.civ_name` not already set, adds `metadata.civ_name = ai_name`
- This mirrors the field Witness needs for instant extraction without regex+AI

**Deployed**: Yes — `aether-logserver.service` restarted at 2026-03-05T11:50:28 UTC
**Verified**: Test log entry confirms `metadata.civ_name` is now present

---

## Architecture Notes

- The naming ceremony chatbox JS lives in **Elementor page data** for page ID 1232, NOT in the plugin
- The plugin (`purebrain-security-plugin.php`) only handles proxying to `api.purebrain.ai`
- The log server (`purebrain_log_server.py`) handles the actual storage and forwarding
- The log server runs as `aether-logserver.service` (systemd, port 8443, behind Cloudflare tunnel at `api.purebrain.ai`)

---

## What Witness's capture_watcher Actually Sees

After the fix, a complete naming ceremony entry has:
```json
{
  "session_id": "purebrain_1772662547515_pqaskj6j8",
  "messages": [...],
  "metadata": {
    "event_type": "conversation_complete",
    "ai_name": "Aria",
    "civ_name": "Aria",  // NEW — added by log server
    "message_count": 15,
    "timestamp": "...",
    "page_url": "https://purebrain.ai/pay-test-sandbox-3/..."
  }
}
```

The `pb-post-*` session with matching email comes within 60 min (during the same user journey).

---

## Remaining Gap

`metadata.human_name` and `metadata.email` cannot be set at naming ceremony time — they are collected in the post-payment Q&A (the `pb-post-*` session). This is fine per Witness spec — these are optional fields and Witness matches the two files by `capture_watcher` polling within 60 min.

If Witness needs cross-file linking by email, the current flow doesn't provide that at the naming step. One future option: after the post-payment flow completes and we have the email, patch the original `purebrain_*` entry with human_name+email. But Witness confirmed current format works — not needed now.
