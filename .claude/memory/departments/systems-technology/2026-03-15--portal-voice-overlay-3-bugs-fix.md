# Portal Voice Overlay — 3 Bug Fix (2026-03-15)

## Context
Portal at app.purebrain.ai. Voice settings overlay has Browser/ElevenLabs engine tabs.

## Root Cause (all 3 bugs shared a single root)
`openHmiVoiceOverlay()` never synced the UI to the saved engine state when the overlay opened.

The HTML hardcodes `class="hmi-engine-btn active"` on the Browser button. So every time
the overlay opened, Browser always appeared selected — regardless of what was actually saved
in localStorage.

`_elSwitchEngine()` (which sets button highlights AND populates the voice dropdown) was only
called on user click events and on initial page load — never on overlay open.

## The 3 Bugs Explained

### Bug 1: Visual mismatch (shows Browser when EL is saved)
- Overlay opens with hardcoded Browser=active in HTML
- `_elSwitchEngine` never called on open → UI stuck at Browser

### Bug 2: EL tab doesn't highlight when clicked
- Only re-appeared when using the tab click after the overlay was open
- Real symptom: overlay opened fresh with Browser always visually selected first,
  so the EL tab appeared "not highlighted" even when already the saved engine

### Bug 3: EL voices don't appear in voice list
- `_elPopulateVoiceSelectEl()` is only called from inside `_elSwitchEngine(true)`
- Since `_elSwitchEngine` was never called on overlay open, dropdown stayed populated
  with browser voices from the last `populateVoiceSelector()` call

## Fix Applied

Added to `openHmiVoiceOverlay()` in `/home/jared/purebrain_portal/portal-pb-styled.html`,
immediately after `startHmiCanvas()`:

```js
// Sync engine/voice UI to actual saved state when overlay opens.
setTimeout(function() {
  var savedEngine = localStorage.getItem('hmi_engine');
  if (typeof window._elSwitchEngineGlobal === 'function') {
    window._elSwitchEngineGlobal(savedEngine === 'elevenlabs');
  }
}, 50);
```

Key: uses `window._elSwitchEngineGlobal` (already exposed to window scope) to bridge
the IIFE closure gap. The 50ms delay lets the overlay DOM settle before the toggle runs.

## Line Reference
- Fix inserted at approximately line 11397 in portal-pb-styled.html
- Backup: `portal-pb-styled.html.bak-voice-engine-fix-20260315`

## Deploy Note
Portal server hot-reloads the HTML file — no restart needed to pick up HTML changes.
