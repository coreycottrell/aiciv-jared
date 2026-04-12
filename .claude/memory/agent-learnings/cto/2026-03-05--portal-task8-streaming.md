# Portal Task 8: Real-Time Response Streaming

**Date**: 2026-03-05
**Type**: operational
**Topic**: Typewriter streaming simulation for portal.purebrain.ai/pb chat

## What Was Built

Patch script: `/home/jared/purebrain_portal/apply_task8_streaming.py`

Adds real-time streaming simulation to AI chat responses in the portal.

## Key Architecture Finding

The server WebSocket (`/ws/chat`) sends **complete messages**, not token streams.
JSON shape: `{role, text, timestamp, id}` — one complete message per WS frame.
Therefore streaming must be simulated client-side (typewriter effect).

## Streaming Design

- 3 chars per tick, 12ms intervals = ~250 chars/sec (feels like fast token streaming)
- Markdown re-renders every 60 chars (balance: correctness vs DOM thrashing)
- Blinking blue cursor (2px wide line, `var(--gold)`, 0.7s blink cycle)
- `.stream-cursor` CSS class, appended to `streamTarget` on each tick

## Thinking Indicator Integration

Key insight: the thinking indicator should disappear when the FIRST TOKEN arrives,
not when the fetch() call completes. Two components hand off:

1. `_dispatchChatMessage()` stores `thinkingId` on `window._pendingThinkingId`
2. `chatWs.onmessage` reads it and passes to `startStreamingMessage()`
3. `startStreamingMessage()` calls `removeThinkingIndicator()` BEFORE starting the typewriter

On error paths, `_dispatchChatMessage` clears the pending ID and removes the indicator itself.

## Duplicate Prevention

`knownMsgIds` is pre-registered with the msgId before streaming starts.
This prevents `addMessage()` from creating a duplicate if it's called with the same ID.
(Since we handle the message in `chatWs.onmessage` with `return`, this shouldn't happen,
but the pre-registration is a safety net.)

## DOM Structure

`startStreamingMessage()` mirrors `addMessage()` exactly for assistant role:
- Same avatar (grabs src from first existing `.msg.assistant` avatar on page)
- Same bubble, meta, bookmark button, context menu handlers
- Quote blocks supported (reply-to pattern)
- Post-processing on completion: `parseAiFiles`, `renderAiFileCards`, `addCodeCopyButtons`, `updateCtxGauge`

## Patch Count

4 patches total:
1. CSS: `.stream-cursor` + `.msg-bubble.streaming` (before `END HOVER TOOLTIPS`)
2. State: `activeStream` var (after `knownMsgIds`)
3. Function: `startStreamingMessage()` (before `addThinkingIndicator`)
4. WS handler: `chatWs.onmessage` routes assistant messages to streamer
5. Dispatch: `_dispatchChatMessage` stores thinkingId on window

## File Sizes

- Portal input: ~354KB (post Tasks 0-7)
- Task 8 adds ~3KB (CSS ~0.3KB, JS ~2.7KB)

## CSS Anchor

`  /* ===== END CTX INFO CARD ===== */\n  /* ===== END HOVER TOOLTIPS ===== */`
(Added by Task 7/6 — confirmed at line 2792)
