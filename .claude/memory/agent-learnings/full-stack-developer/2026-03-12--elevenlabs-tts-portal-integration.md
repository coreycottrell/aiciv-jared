# ElevenLabs TTS Integration — PureBrain Portal

**Date**: 2026-03-12
**Type**: teaching
**Topic**: Integrating ElevenLabs streaming TTS alongside existing browser speechSynthesis in a large HTML portal

---

## What Was Built

Added ElevenLabs as a premium TTS engine option inside the HMI Voice Overlay of the PureBrain portal. Browser TTS remains as fallback.

**File modified**: `/home/jared/purebrain_portal/portal-pb-styled.html`

---

## Architecture

### State Variables (added to HMI IIFE scope)
- `_elEnabled` — boolean, whether EL engine is active
- `_elApiKey` — loaded from `localStorage('elevenlabs_api_key')`
- `_elVoiceId` — loaded from `localStorage('elevenlabs_voice_id')`, defaults to Adam
- `_elAudioCtx` — AudioContext for decoding/playing mp3 buffers
- `_elCurrentSource` — active AudioBufferSourceNode (for stop support)

### Key Functions
- `_elSpeak(text, onEnd)` — POSTs to ElevenLabs `/v1/text-to-speech/{id}/stream`, gets ArrayBuffer, decodes via AudioContext, plays. Falls back to `_browserSpeak` on any error.
- `_browserSpeak(text, onEnd)` — extracted original speechSynthesis logic (was inline in `_hmiSpeakResponse`)
- `_elStopCurrent()` — stops active AudioBufferSourceNode
- `_elSwitchEngine(useEl)` — toggles UI state + repopulates voice selector dropdown

### Modified Functions
- `_hmiSpeakResponse` — now checks `_elEnabled && _elApiKey`, routes to `_elSpeak` or `_browserSpeak` accordingly

---

## UI Changes

### Voice Picker (HMI overlay, was ~line 9696)
Added above the voice `<select>`:
- Engine toggle row: "Browser" | "ElevenLabs ✦" buttons + ⚙ gear button
- Voice select repopulates based on engine — browser voices OR 5 EL presets

### Settings Modal (`#elSettingsModal`)
- Password input for API key (saved to localStorage)
- Dropdown of 5 EL voices (Adam, Antoni, Josh, Arnold, Sam)
- Save / Test Voice / Cancel buttons
- Test Voice fetches real audio and plays it to verify key works
- Status dot (green/red) reflects key validity

### CSS (added before "HMI Mobile responsive")
- `.hmi-el-gear-btn` — gear button
- `.hmi-engine-toggle` / `.hmi-engine-btn` — pill toggle UI
- `#elSettingsModal` + `.el-modal-*` — dark modal matching portal theme

---

## ElevenLabs API Pattern

```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream
Headers:
  xi-api-key: {key}
  Content-Type: application/json
  Accept: audio/mpeg
Body:
  { text, model_id: "eleven_monolingual_v1", voice_settings: { stability: 0.5, similarity_boost: 0.75 } }
Response: ArrayBuffer (mp3) — decode with AudioContext.decodeAudioData
```

---

## Fallback Chain

1. ElevenLabs enabled + key present → EL API
2. EL API error (bad key, 429, network) → browser speechSynthesis
3. EL disabled → browser speechSynthesis directly

---

## Key Gotchas

- `AudioContext` must be created after a user gesture in Chrome (not at parse time) — lazy init works fine since user must click a button to invoke TTS
- EL `Accept: audio/mpeg` header is required or the stream returns wrong format
- `AudioBufferSourceNode` can only be played once — create a new one each time
- The voice selector `<option value>` is used differently for each engine: index (int) for browser voices, voice_id string for EL
- Repopulating the voice selector must handle both modes cleanly

---

## Voice Presets (EL)
| ID | Name | Character |
|----|------|-----------|
| pNInz6obpgDQGcFmaJgB | Adam | Deep, authoritative (default) |
| ErXwobaYiN019PkySvjV | Antoni | Warm, professional |
| TxGEqnHWrfWFTfGW9XjX | Josh | Deep, narrative |
| VR6AewLTigWG4xSOukaG | Arnold | Powerful, commanding |
| yoZ06aMxZJJ28mfd3POQ | Sam | Confident, dynamic |
