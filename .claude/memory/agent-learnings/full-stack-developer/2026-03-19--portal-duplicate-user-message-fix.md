# Portal Duplicate User Message Bug — Root Cause & Fix

**Date**: 2026-03-19
**Type**: teaching
**Topic**: Portal WS poll loop echoes user messages despite optimistic render

## The Bug

User messages appeared twice in the PureBrain portal chat.

## Root Cause

Two-phase render collision between optimistic UI and WS poll loop:

1. User sends message → optimistic render with temp `opt-{timestamp}` ID, added to `knownMsgIds`
2. Fetch to `/api/chat/send` saves message to `portal-chat.jsonl` with ID `portal-{timestamp}-{hex}`
3. WS poll loop finds new portal-chat entry (prev_len = -1), sends it to client 1.5s later
4. Client receives WS message with real `portal-{...}` ID — `knownMsgIds.has()` = false (only has `opt-` ID)
5. Text-match dedup (`lastSentOptimisticText === msg.text`) is the only guard — fragile, gets nulled after first match

## The Fix

**Server** (portal_server.py, api_chat_send): Capture return value of `_save_portal_message()`, include `msg_id` in response JSON.

**Client** (portal-pb-styled.html, _dispatchChatMessage fetch handler): In success `.then()`, if `data.msg_id` present, call `knownMsgIds.add(data.msg_id)` immediately. This pre-registers the real server ID before WS echo arrives.

## Files Changed

- /home/jared/purebrain_portal/portal_server.py (~line 928)
- /home/jared/purebrain_portal/portal-pb-styled.html (~line 9597)
