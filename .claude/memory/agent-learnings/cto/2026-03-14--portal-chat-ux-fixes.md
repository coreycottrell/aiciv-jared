# CTO Memory: Portal Chat UX Fixes Analysis
**Date**: 2026-03-14
**Type**: operational
**Topic**: Portal chat UX — linkify, persistence, voice TTS gating

## What Was Asked
Three urgent portal fixes while Jared was actively testing:
1. Clickable URLs in chat messages
2. Chat persistence across portal restarts
3. Voice TTS should not interrupt background agent responses

## What I Found (Code Archaeology)

### Fix 1 — Clickable Links
`renderMarkdown()` in `portal-pb-styled.html` ALREADY HAD auto-linking (step 7b, line 5435-5439).
Root cause of "plain text URLs" complaint: the existing auto-link regex was CORRECT but links had NO STYLE applied — they blended in with surrounding text (no color, no underline visible on dark theme).
Fix: add `style="color:#2a93c1;text-decoration:underline;"` to both step 7 (markdown links) and step 7b (bare URL auto-link).
Also improved step 7b from negative-lookbehind approach to split-on-anchor approach — more robust, avoids edge cases with browsers that have inconsistent lookbehind support.

### Fix 2 — Chat Persistence
ALREADY FULLY IMPLEMENTED. `loadChatHistory()` is called on every WS connect/reconnect (line 7260). The server endpoint `/api/chat/history` exists in `portal_server.py` (line 824). Messages are loaded from `portal-chat.jsonl`. No code change needed.

### Fix 3 — Voice TTS Gating
ALREADY FULLY IMPLEMENTED. `window._voiceSendTimestamp` is set when user sends via voice (lines 11398, 11699). Streaming completion checks this timestamp and only speaks if `_elapsed < 90000` (90 seconds), then resets to 0. No code change needed.

## What Was Deployed
Patch script at `/home/jared/purebrain_portal/apply_portal_patch.py`
Run script at `/home/jared/purebrain_portal/run_portal_patch.sh`

## Key Pattern for Future CTO Work
When portal CSS complaints arise about links/text not being styled: check `renderMarkdown()` step 7 and 7b. The function exists and works — styling issues are separate from linkification.

## Architecture Note
The portal HTML file is 12,417 lines. Without a Bash executor, CTO agents should prepare Python patch scripts for targeted changes rather than attempting full file read/write cycles.
