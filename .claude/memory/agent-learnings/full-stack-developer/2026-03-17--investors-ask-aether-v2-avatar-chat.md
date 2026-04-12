# investors-ask-aether: 3D Avatar + Real API Chat Integration

**Date**: 2026-03-17
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Created `/exports/cf-pages-deploy/investors-ask-aether/index.html` — a clone of the investor page with:

1. **3D Neural Network Avatar** (Three.js, ES module) embedded above the Ask Aether chat section
2. **Real API chat engine** that POSTs to `/api/investor-chat` (backend TBD)
3. **Avatar mode state machine**: idle → listening (typing) → thinking (waiting) → speaking (responding) → idle
4. **Toned-down visual settings** for idle/listening states

## Key Technical Patterns

### importmap placement
- Must go in `<head>` BEFORE any `<script type="module">` that uses it
- The page already had Three.js r128 UMD loaded globally — ES module import is isolated, no conflict

### Avatar visual tuning (idle/listening calmer)
```js
const MODE_CFG = {
  idle:      { bloom:0.25, fireRate:0.3  },  // was 0.45, 0.8
  listening: { bloom:0.40, fireRate:1.8  },  // was 0.62
  // ...
};
const BASE_EMIT = 0.22; // node base emissive, was 0.35
```

### Avatar-chat wiring
- Avatar `aaSetMode()` exposed as `window.aaSetMode`
- Chat engine calls it safely: `if (typeof window.aaSetMode === 'function') window.aaSetMode(mode)`
- Typing debounce → listening mode (2.5s reset to idle)
- On send: immediately → thinking mode
- On response received: → speaking mode (with typeText animation)
- After typing completes: → idle after 2s delay

### Session storage key
- Changed from `aetherChat` to `aetherChatV2` to avoid conflict with original page

### API contract expected
```
POST /api/investor-chat
{ message: string, history: [{role, text}] }
→ { response: string }
```

## Files
- New page: `/exports/cf-pages-deploy/investors-ask-aether/index.html` (3254 lines)
- Original unchanged: `/exports/cf-pages-deploy/investors/index.html`
- Avatar POC source: `/portal_uploads/from-portal/portal_20260317_103207_aether-avatar-poc.html`
