# Memory: Voice Overlay Mobile - AETHER Name / Status Text Overlap

**Date**: 2026-03-13
**Agent**: browser-vision-tester
**Type**: gotcha + pattern
**Tags**: portal, mobile, voice-overlay, hmi, overlap, CSS, app.purebrain.ai, TL-readout

---

## Summary

Tested voice overlay at app.purebrain.ai on iPhone 14 (390x844). Found confirmed overlap
between the TL corner status readout and the AETHER name / logo during active states.

**Status in STANDBY**: Overlay looks correct, no overlap. Status readout is hidden (display:none).
**Status in LISTENING / PROCESSING / TRANSMIT**: OVERLAP CONFIRMED. Status text renders directly over the AETHER name and logo circle.

---

## The Bug

### TL Readout (.hmi-voice-overlay__readout--tl) overlaps AETHER name (#hmiAiName)

**Coordinates at conflict:**

- `#hmiAiName` ("AETHER"): top=95, bottom=121, left=114, right=276, height=26px, font 18px
- `.hmi-voice-overlay__readout--tl` (LISTENING...): top=100, bottom=131, left=165, right=273, height=31px
- Overlap region: Y 100-121 (21px vertical overlap), X 165-273 (108px horizontal overlap)
- `nameOverlapsTL: true` confirmed by getBoundingClientRect comparison

### Logo (#hmiLogoContainer) also overlaps identity text

The logo (48x48px, centered at 171-219 x 106-154) sits directly over the AETHER name (95-121) and tagline (123-135).
The name is BEHIND the logo. This appears intentional (name is styled behind the circular brain animation container).

### What it looks like visually

In LISTENING state: "AETHER" text, logo circle, and "LISTENING..." text all render in the same zone (Y 95-154).
Result is: illegible overlap — user sees orange/blue letters clashing in top-center of the circle.

---

## Layout Architecture (good to know for future testing)

Voice overlay full layout at 390x844 (from top to bottom):

```
Y=0-56:    TTS Toggle (left) + Close X (right) — top bar
Y=40-220:  .hmi-voice-overlay__container (180x180 circle, centered)
  Y=95-135:  .hmi-voice-overlay__identity (AETHER + tagline)
    Y=95-121:  #hmiAiName ("AETHER") — 18px, 26px tall
    Y=123-135: .hmi-voice-overlay__tagline — 10px, 12px tall
  Y=106-154:  #hmiLogoContainer (brain logo, 48x48, z-indexes over name)
  Y=100-131:  .hmi-voice-overlay__readout--tl (when visible: LISTENING... etc)
  Y=190-210:  #hmiAudioLevel (audio bars)
Y=230-399:  .hmi-voice-overlay__controls
  Y=230-272:  #hmiMicBtn (mic button, 42x42)
  Y=282-295:  #hmiMicStatus (status text: "Mic access denied" / "LISTENING...")
  Y=305-327:  .hmi-voice-overlay__state-controls (4 buttons: Standby/Listening/Processing/Transmit)
  Y=343-399:  .hmi-voice-overlay__voice-picker
    Y=345-364:  #hmiEngineToggle (Browser | ElevenLabs)
    Y=343-367:  #hmiElGearBtn (gear icon)
    [AI VOICE dropdown also here]
Y=399+:     445px empty space below all controls
```

### What is NOT broken

- AETHER name does NOT overlap with `#hmiMicStatus` text (Y=282, 161px gap below name)
- Status buttons (STANDBY/LISTENING/PROCESSING/TRANSMIT) do NOT overlap with each other or mic button
- ENGINE and AI VOICE controls are fully visible, not cut off
- Voice picker bottom (Y=399) is well within viewport (844px), 445px space below
- The overlay itself fits without scrolling (scrollHeight = clientHeight = 844)
- No horizontal overflow

---

## Root Cause Hypothesis

The `.hmi-voice-overlay__readout--tl` element is positioned absolutely (or uses negative margins)
to place it at the TL corner of the circle. When the circle center is at Y=40-220, the TL corner
readout renders at approximately Y=40+60=100 (top 1/3 of circle). This lands directly on the
AETHER name which is also positioned at Y=95.

The AETHER identity block is positioned at the top of the circle container, and the TL readout
overlaps exactly that zone.

### Fix suggestion

Option A: Move AETHER name ABOVE the circle (not inside it), e.g. Y=10-40, before circle starts at Y=40.
Option B: Move status readout text BELOW the circle, not overlapping the name zone.
Option C: Hide the identity block (#hmiAiName + tagline) when readout is active.
Option D: Make TL readout render ABOVE the circle container (top: -30px from container top).

---

## Auth Pattern for Future Testing

Token passes via URL param: `?token=UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ`
Token file: `/home/jared/purebrain_portal/.portal-token`
Login overlay is hidden on page load when token is valid (loginOverlay display:none).
Voice overlay opens via `#hmiTtsToggle` button (top-left of voice button at bottom of chat).

When voice button not clickable in Playwright, use JS:
```javascript
document.getElementById('hmiVoiceOverlay').classList.add('visible');
document.getElementById('hmiVoiceOverlay').style.display = 'flex';
```

---

## Screenshots

Dir: `/tmp/voice-overlay-mobile-test/`
- `01-portal-loaded.png` — Portal chat view, no overlay
- `02-voice-overlay-open.png` — Voice overlay open (actual click, default STANDBY)
- `03-standby-js-open.png` — JS-opened overlay, STARTING VOICE state
- `04-listening-forced.png` — LISTENING state: OVERLAP CLEARLY VISIBLE
- `05-processing-forced.png` — PROCESSING state: same overlap pattern
- `06-transmit-forced.png` — TRANSMIT state: same overlap pattern
