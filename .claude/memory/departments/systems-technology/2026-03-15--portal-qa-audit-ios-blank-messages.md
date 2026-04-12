# Portal QA Audit — iOS Blank Messages Root Cause
**Date**: 2026-03-15
**Type**: diagnosis + full-qa
**Agent**: dept-systems-technology

## iOS Blank Messages Root Cause (HIGH — not yet fixed)

The visibilitychange handler at line 10881 of `portal-pb-styled.html` only sets `isVisible`:
```javascript
document.addEventListener('visibilitychange', () => { isVisible = document.visibilityState === 'visible'; });
```
The comment block at line 7419 `// ===== VISIBILITY CHANGE — minimal, safe =====` has NO code — previous fix attempts were rolled back.

**The race condition**:
1. iOS kills WebSocket silently (no onclose fires immediately)
2. `chatLoaded = true` — so `switchPanel('chat')` only calls `smartScroll`, NOT `loadChatHistory`
3. Heartbeat timer (10s check, 30s threshold) eventually detects dead WS and triggers reconnect
4. Exponential backoff (2s→30s) delays the reconnect
5. During this window: blank messages

**Safe fix approach** (pending Jared approval):
```javascript
document.addEventListener('visibilitychange', function() {
  isVisible = document.visibilityState === 'visible';
  if (isVisible && token) {
    if (!chatWs || chatWs.readyState === WebSocket.CLOSED || chatWs.readyState === WebSocket.CLOSING) {
      if (chatWsReconnectTimeout) { clearTimeout(chatWsReconnectTimeout); chatWsReconnectTimeout = null; }
      _wsReconnectDelay = 2000;
      connectChatWS();
    }
  }
});
```
Replace the line at 10881 with the above.

## Other Bugs Found

| Severity | Description | Line | Fix |
|----------|-------------|------|-----|
| MEDIUM | `knownMsgIds` Set never cleared — grows forever, loadChatHistory doesn't reset it | 6991-6992 | Add `knownMsgIds.clear()` before `chatLoaded = true` |
| LOW | `updateCtxGauge` interval reference not stored (anonymous setInterval) | 5679 | Store as `ctxGaugeInterval` |
| LOW | `pollCompactStatus` 2s interval reference not stored | 5706 | Store reference |
| LOW | Safe area insets missing from main portal layout (only on login overlay) | 124-125 | Add env(safe-area-inset-top) to sidebar/chrome |
| LOW | Terminal DOM thrash: full textContent replace on each WS message | 6009 | Incremental append |

## Full QA Status
All panels PASS except iOS blank messages (HIGH). Voice TTS fix confirmed working. Auth/OAuth flow confirmed working. Bookmarks, search, scroll behavior all confirmed working.

## Report Location
`/home/jared/projects/AI-CIV/aether/exports/overnight-blog/portal-qa-report-2026-03-15.md`
