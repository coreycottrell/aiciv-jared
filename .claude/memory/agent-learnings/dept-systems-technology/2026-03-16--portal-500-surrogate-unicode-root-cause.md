# Portal 500 Error: UnicodeEncodeError Surrogate Characters
**Date**: 2026-03-16
**Incident time**: ~13:01:53
**Type**: gotcha / incident postmortem

## Root Cause

`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83c' in position 76183: surrogates not allowed`

A surrogate character (half of a split emoji pair, `\ud83c`) was present in the chat history data being serialized by `portal_server.py`. The `JSONResponse` call at line 870 of `api_chat_history()` raised `UnicodeEncodeError` because Python's JSON encoder does not allow lone surrogates in UTF-8 output.

## What Failed

- `POST /api/chat/send` - 1 x 500 (likely triggered the bad entry to be written)
- `GET /api/chat/history?last=200` - 24 x 500 (every subsequent chat history load failed)

All 500s were ASGI-level exceptions, not caught by any try/except in the handler.

## What Served app.purebrain.ai

The cloudflared tunnel (`/etc/cloudflared/config.yml`) routes `portal.purebrain.ai` and `*.purebrain.ai` both to `http://localhost:8099` with 120s connect timeout. The portal is a FastAPI/Uvicorn app at `/home/jared/purebrain_portal/portal_server.py`, run as `aether-portal.service`.

The service itself never crashed - the process stayed up the whole time. Only the chat history and chat send endpoints returned 500. Other endpoints (/api/status, /api/context, /health) continued returning 200 throughout.

## How It Resolved

The fix (`_sanitize()` function) was already added to portal_server.py (lines 886-896) after this incident. The sanitizer runs `str.encode('utf-8', errors='replace').decode('utf-8')` recursively on all message data before passing to `JSONResponse`. This strips surrogates before serialization.

After the fix was deployed and the portal restarted, all `/api/chat/history` requests returned 200.

## Current State (verified at investigation time)

- Portal: active, uptime ~7049s, healthy
- `aether-portal.service`: active
- 0 new 500s in current log tail
- `_sanitize()` protection confirmed present in portal_server.py

## Key Files

- `/home/jared/purebrain_portal/portal_server.py` - portal app, lines 886-896 have the fix
- `/home/jared/projects/AI-CIV/aether/logs/portal_server.log` - access/error log
- `/etc/cloudflared/config.yml` - tunnel routing (portal -> localhost:8099)

## Prevention Pattern

Anytime chat messages are serialized from JSONL logs, surrogate chars can sneak in from external sources (web chat users pasting broken emoji, Claude outputting partial emoji sequences, etc.). The `_sanitize()` recursive replace pattern is the correct defense. Apply the same pattern to any endpoint that serializes messages from user-facing logs.
