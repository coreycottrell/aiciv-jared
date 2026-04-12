# Voice Overlay vs Speaker Button Conflict Fix
**Date**: 2026-03-13
**Type**: bug fix / behavioral state management
**File**: `/home/jared/purebrain_portal/portal-pb-styled.html`

## Problem
Two voice subsystems competed on the portal:
- **Speaker button** (`_hmiTtsEnabled`) — auto-reads AI responses via TTS when active
- **Voice overlay** (`_hmiConversationMode`) — full conversation mode with mic + AI voice

`_hmiSpeakResponse` fires if EITHER flag is true (`if (!_hmiTtsEnabled && !_hmiConversationMode) return`).
When both were active: AI spoke during user input, feedback loops, talking over each other.

## Fix (3 surgical changes)
**Variable added** (near `_hmiTtsEnabled` declaration):
```js
var _ttsSavedBySpeaker = false;
```

**`openHmiVoiceOverlay()`** — save and suppress speaker TTS:
```js
_ttsSavedBySpeaker = _hmiTtsEnabled;
_hmiTtsEnabled = false;
var speakerBtnEl = document.getElementById('speaker-btn');
if (speakerBtnEl) speakerBtnEl.classList.remove('active');
```

**`closeHmiVoiceOverlay()`** — restore speaker TTS state:
```js
_hmiTtsEnabled = _ttsSavedBySpeaker;
var speakerBtnEl = document.getElementById('speaker-btn');
if (speakerBtnEl) {
  speakerBtnEl.classList.toggle('active', _hmiTtsEnabled);
  speakerBtnEl.title = _hmiTtsEnabled ? 'Speaker ON...' : 'Speaker OFF...';
}
```

## Result: Two clean non-competing modes
- **Text mode + speaker ON**: AI reads responses aloud via speaker button. Works normally.
- **Voice overlay mode**: Full conversational turn-taking. Speaker TTS suppressed. AI only speaks in response to user voice. Mic does not fight TTS.
- **Close overlay**: Speaker returns exactly to the state it was before overlay opened.

## Key architecture notes
- `_hmiSpeakResponse` guard `(!_hmiTtsEnabled && !_hmiConversationMode)` was already correct — just needed the upstream state management
- The overlay's internal TTS (`_hmiConversationMode`) is untouched — overlay voice still works fully
- Speaker button visual state (`active` class) syncs correctly on both open and close
- Security: pure boolean state management, no new inputs/outputs, no XSS surface
