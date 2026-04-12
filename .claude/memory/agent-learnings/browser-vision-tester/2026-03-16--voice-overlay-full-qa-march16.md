# Memory: Voice Overlay Full QA Audit — 2026-03-16

**Date**: 2026-03-16
**Agent**: browser-vision-tester
**Type**: technique + pattern + gotcha
**Tags**: portal, voice-overlay, hmi, qa, conversational-ai, elevenlabs, speech-recognition, mobile, state-machine

---

## Context

Full QA audit of HMI Voice Overlay at app.purebrain.ai:8097 (localhost:8097).
19 screenshots taken. 4 state transitions tested. Mobile + desktop. ElevenLabs settings panel audited.

---

## Key Findings

### Architecture (Updated from 2026-03-13)

The voice overlay has been significantly redesigned since the previous mobile audit:

**Previous layout (2026-03-13):**
- Circle was 180x180 on mobile
- AETHER name was INSIDE circle container at Y=95 → caused overlap with readouts
- Readouts were `display:none` only partially

**Current layout (2026-03-16):**
- Circle is 500x500 on DESKTOP, 180x180 on mobile (container CSS uses media query or the circle renders smaller)
- AETHER identity block is BELOW the circle container (Y=255 on mobile, 35px gap after circle ends at Y=220)
- All 4 readouts now have `display: none !important` globally — they were only visible in screenshots because JS forced them visible
- This RESOLVES the 2026-03-13 overlap bug

### DOM Structure (Current)
```
#hmiVoiceOverlay
├── .hmi-tts-toggle-wrap (top-left: 🔊 button + label)
├── .hmi-voice-overlay__close (top-right: X)
├── .hmi-voice-overlay__container (the circle)
│   ├── #hmiCanvas (500x500)
│   ├── #hmiLogoContainer (spinning logo)
│   ├── 4x .hmi-voice-overlay__readout (TL/TR/BL/BR — HIDDEN by display:none !important)
│   └── #hmiAudioLevel (8 bars, opacity:0 until active)
├── .hmi-voice-overlay__identity (BELOW circle)
│   ├── #hmiAiName ("AETHER", 42px gradient text)
│   └── .hmi-voice-overlay__tagline
└── .hmi-voice-overlay__controls
    ├── #hmiMicBtn (60x60 circle mic)
    ├── #hmiMicStatus (status text)
    ├── .hmi-voice-overlay__state-controls (4 state buttons)
    └── .hmi-voice-overlay__voice-picker
        ├── #hmiEngineToggle (Browser/ElevenLabs toggle)
        ├── #hmiElGearBtn → opens #elSettingsModal
        ├── #hmiVoiceSelect (AI voice dropdown)
        └── #hmiSendWord + #hmiSendWordSave
```

### State Machine — What Changes per State
Clicking state buttons updates `hmiStatusVal` text:
- Standby → "STANDBY"
- Listening → "RECEIVING"
- Processing → "COMPUTE"
- Transmit → "TRANSMIT"

But: `.hmi-voice-overlay__state-btn.active` class does NOT move between buttons on click. Only "Standby" has `.active` in DOM. This is a CSS/JS bug.

### ElevenLabs Integration
- 6 voices pre-loaded: Aether custom (RX0kjGhuL9AMRVJm2dG5), Adam, Antoni, Josh, Arnold, Sam
- API key must be entered by user and saved to localStorage
- No Aether-managed API key for this flow
- Gear button opens modal correctly
- Cancel/Save/Test Voice buttons work visually

### Canvas Animation
- Confirmed active: center pixel RGBA = (235, 60, 7, 38) = orange comet particle
- 500x500 canvas with orange+blue particle system
- Logo spins at 30s rotation

### JS Global Functions
- `closeHmiVoiceOverlay` — EXISTS on window
- `openHmiVoiceOverlay` — DOES NOT exist on window (scoped in closure)
- `_hmiVoiceOverlayOpen` — EXISTS (boolean, false when closed)
- `SpeechRecognition/webkitSpeechRecognition` — EXISTS (browser API)
- `speechSynthesis` — EXISTS but 0 voices in headless
- `AudioContext` — EXISTS
- `MediaDevices/getUserMedia` — EXISTS

---

## Bugs Found

### Bug 1: No Live Transcription Display [CRITICAL]
- Missing: text area showing what user is currently saying during LISTENING
- No `#hmiTranscript`, no `.transcript` elements anywhere
- Users speak and see nothing until the message posts to chat

### Bug 2: State Button Active Class Doesn't Update [HIGH]
- `.hmi-voice-overlay__state-btn.active` stays on Standby button
- When state transitions to Listening/Processing/Transmit, the corresponding button doesn't get `.active`
- Fix: state machine needs `querySelectorAll('.hmi-voice-overlay__state-btn').forEach(b => b.classList.remove('active'))` + add to current button

### Bug 3: openHmiVoiceOverlay Not Global [HIGH]
- Not on window object — scoped in closure
- Fix: `window.openHmiVoiceOverlay = function() { ... }`

---

## Mobile Layout Data (390x844)
```
Circle container: 180x180 at (105, 40) — Y=40 to Y=220
AETHER name: Y=255-281 (35px gap below circle)
Controls: Y=313-578 (all fit in 844px viewport)
No scroll needed, no horizontal overflow
```

---

## Auth Pattern (Unchanged)
- Token via URL: `?token=UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ`
- Token file: `/home/jared/purebrain_portal/.portal-token`
- Login overlay auto-hides when token valid
- `#mic-btn` in chat input opens voice overlay (not `#hmiTtsToggle` which is inside the overlay)

---

## For Future Testing

### Real Device Test Checklist
1. Chrome on desktop or mobile at https://app.purebrain.ai:8097
2. Click mic icon → confirm overlay opens
3. Click 🎤 HMI mic → grant mic permission → verify LISTENING state UI
4. Speak → verify something happens (should see transcription or mic pulses)
5. Say configured send word → confirm auto-submit
6. Check if TTS speaks Aether's response

### Playwright Gotchas
- Use `domcontentloaded` not `networkidle` for this portal (keeps long-polling connections)
- Force-open overlay with `el.classList.add('visible'); el.style.display = 'flex';`
- EL settings modal (`#elSettingsModal`) can block clicks — close it with JS before other interactions
- Canvas has active content even in headless (animation runs)

---

## Previous Bug Status
- 2026-03-13 overlap bug: RESOLVED — AETHER name moved below circle, readouts hidden by `!important`
