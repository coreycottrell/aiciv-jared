# HMI Voice Overlay — PureBrain Portal Integration

**Date**: 2026-03-12
**Type**: operational
**Topic**: Porting voice HMI canvas overlay from v8 dashboard source to portal-pb-styled.html

---

## What Was Built

Full-screen voice HMI (Human-Machine Interface) overlay for the PureBrain portal. Activated by clicking the existing `id="mic-btn"` microphone button in the chat input bar.

## Key Adaptations Made (source → portal)

1. **AI Name**: `AppState.ui.*` → `window._hmiVoiceOverlayOpen = true/false`. Name reads from `civName` (module-level var set in `boot()` from `/health` endpoint). DOM element `id="hmiAiName"` updated on open.

2. **Chat input ID**: `document.getElementById('messageInput')` → `document.getElementById('chat-input')`. This is the textarea in the portal's chat input bar.

3. **Send message**: `sendMessage()` → `document.getElementById('send-btn').click()`. The portal wires its send via the button's own event listener.

4. **AppState → window flag**: `AppState.ui.hmiVoiceOverlayOpen` → `window._hmiVoiceOverlayOpen`. Canvas animation checks this flag to know when to stop.

5. **Logo URL**: Source used `LOGO_URL` variable. Portal ALSO has `LOGO_URL` defined as a base64 PNG data URI at line ~6158. Same variable name, no change needed - just reference it.

6. **Mobile helpers**: Source called `isMobileViewport()` and `closeMobileSidebar()`. Portal has `closeMobileMenu()` instead. Used that. No `isMobileViewport()` — inlined `window.innerWidth < 768` check directly.

7. **autoResizeTextarea**: Source called this after updating input value. Portal textarea is fixed `rows=3` with no resize function. Omitted - not needed.

8. **Animation name conflicts**: Source used `logoSpin` and `micPulse` keyframe names. Portal already defines `logoSpin` for the thinking indicator (line 389). Renamed HMI versions to `hmiLogoSpin` and `hmiMicPulse` to avoid conflicts.

9. **IIFE scoping**: Wrapped the entire HMI JS block in an IIFE `(function() { ... })()` to avoid polluting global scope. Exported only what's needed: `window.closeHmiVoiceOverlay`, `window._hmiSpeakResponse`, `window._lastSendWasVoice`, `window._hmiVoiceOverlayOpen`.

## TTS Integration

- `window._lastSendWasVoice` flag set to `true` when overlay closes with a transcript
- `window._hmiSpeakResponse(text)` function exposed globally
- Hook inserted at streaming completion point in `startStreamingMessage()` — right after `bubble.classList.remove('streaming')` and `streamTarget.innerHTML = renderMarkdown(...)`
- TTS toggle button (`id="hmiTtsToggle"`) in overlay top-left corner, off by default
- Markdown stripped before speech synthesis for cleaner audio

## File Structure

- **CSS inserted**: After `.chat-mic-btn:hover` styles (~line 1626), before `/* WELCOME HERO */` comment
- **HTML inserted**: After the original tooltip IIFE `</script>` (line 9616), as separate `<!-- HMI Voice Overlay -->` block
- **JS inserted**: In new `<script>` tag after HTML block, before `</body>`
- **TTS hook**: In existing `startStreamingMessage()` function, after `bubble.classList.remove('streaming')`

## Portal File

`/home/jared/purebrain_portal/portal-pb-styled.html`
- Before: 9,562 lines
- After: 10,111 lines (+549 lines)

## Source Reference

`/home/jared/portal_uploads/from-portal/portal_20260312_224447_pure-brain-v8-aether-dashboard.html`
- HMI CSS: lines 1522-1555, 1746-1752
- HMI HTML: lines 4517-4555
- HMI JS: lines 12378-12738
