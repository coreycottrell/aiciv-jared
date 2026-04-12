# Portal Voice Settings — 5 Bug Fix Session
**Date**: 2026-03-15
**File**: /home/jared/purebrain_portal/portal-pb-styled.html
**Type**: bug-fix
**Backup**: portal-pb-styled.html.bak-5-voice-bugs-20260315

---

## Root Causes Found

### Bugs 1-3: Visual mismatch, EL tab not highlighting, EL voices not appearing

**Root cause**: `speechSynthesis.onvoiceschanged` event fires asynchronously AFTER the
EL engine restore (300ms DOMContentLoaded delay). When it fires, `populateVoiceSelector()`
unconditionally overwrites `hmiVoiceSelect` with browser voices and selects "Daniel (English
United Kingdom)" as default — regardless of whether EL is the active engine.

This also clobbered the engine button state indirectly by showing browser voices even when
`_elEnabled = true`.

**Fix**: Added guard at top of `populateVoiceSelector()`:
```js
if (_elEnabled) return;
```

The existing 50ms overlay-open sync (`_elSwitchEngineGlobal`) is correct and sufficient
once `populateVoiceSelector` stops clobbering EL state.

### Bugs 4-5: Background task messages read aloud / triggering voice injection

**Root cause**: The `_shouldSpeak` fallback in `startStreamingMessage` completion:
```js
if (!_shouldSpeak && window._hmiVoiceOverlayOpen && window._hmiConversationMode) {
    _shouldSpeak = true;
}
```
This fired TTS for ALL assistant messages while the overlay was open — including background
task results arriving via WebSocket. Background tasks (BOOP, scheduled tasks) never set
`_voiceSendTimestamp`, so they bypassed the timestamp gate and hit this fallback.

**Fix (two parts)**:
1. `_dispatchChatMessage` now sets `window._voiceSendTimestamp = Date.now()` when the
   overlay is open. This means typed user sends ALSO gate via timestamp (previously only
   voice sends did this).
2. The broad fallback was removed. TTS is now gated exclusively on `_voiceSendTimestamp`.
   Background tasks don't set this timestamp, so they stay silent.

---

## Deployment
- No server restart needed — `FileResponse` reads file from disk per request
- Jared needs hard refresh (Ctrl+F5) to bypass browser cache

---

## Key File Paths
- Portal HTML: `/home/jared/purebrain_portal/portal-pb-styled.html`
- Portal server: `/home/jared/purebrain_portal/portal_server.py`
- Backup: `/home/jared/purebrain_portal/portal-pb-styled.html.bak-5-voice-bugs-20260315`

---

## Pattern: voiceschanged async clobber
Browser's `speechSynthesis.onvoiceschanged` is the most common async ordering trap in
Web Speech API code. Always guard it with engine-state checks before modifying shared UI.

## Pattern: background task TTS gating
Use explicit send timestamps (not open-overlay booleans) to gate TTS. Background task
responses arrive via the same WebSocket channel as user-directed responses — the only
reliable distinguishing signal is whether the user intentionally sent something.
