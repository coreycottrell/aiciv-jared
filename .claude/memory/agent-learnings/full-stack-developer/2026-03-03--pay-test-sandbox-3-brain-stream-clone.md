# pay-test-sandbox-3: Clone + OAuth/Telegram Removal + Brain Stream Button

**Date**: 2026-03-03
**Agent**: dept-systems-technology → full-stack-developer
**Page**: 1232 (NEW — pay-test-sandbox-3)
**Source**: 689 (pay-test-2, UNTOUCHED)
**Status**: DEPLOYED AND VERIFIED

## Task

Create a new page cloned from pay-test-2 (page 689) with:
1. OAuth/Claude authentication flow removed
2. Telegram integration removed
3. "Connect to Brain Stream" button added at end of flow

## Architecture Discovery (CRITICAL)

**The chat flow JS lives in `_elementor_data`, NOT `post_content`.**

- `_elementor_data[0].elements[0].settings.html` = 458,624 char HTML widget
- This is where ALL the JS (initPayTestFlow, runBirthInit, runTelegramSetup, etc.) lives
- `post_content` is also populated but Elementor renders from `_elementor_data`
- Always modify `_elementor_data` for chat flow changes on this page

## What Was Removed

### 1. `runBirthInit` (OAuth Flow) — 11,499 chars
- Function: `async function runBirthInit(dom, aiName, firstName)`
- Removed: /api/birth/start call, oauth_url validation, OAuth button DOM creation, /api/birth/code POST
- Still referenced 11x in COMMENTS (changelog text) — harmless

### 2. Phase 3 Telegram Setup — 9,931 chars
- Comment block: `// PHASE 3 — Telegram Setup v3`
- Helper function: `function isValidBotToken(token)`
- Main function: `async function runTelegramSetup(dom, aiName, firstName)`

### 3. Phase 4 Dead Code (runClaudeMaxSetup) — 2,196 chars
- `async function runClaudeMaxSetup()` — already dead code, referenced OAuth flow

### 4. Inline Call Removals
- `await runBirthInit(dom, aiName, firstName)` + its comment block (Step 5b) from questionnaire
- `await runTelegramSetup(dom, aiName, firstName)` + comment from main flow

## What Was Added: Brain Stream Connect Button

### JS: `window.showBrainStreamButton(url, aiName)`
- Hidden by default (display:none wrapper)
- Call `window.showBrainStreamButton(magicLinkUrl, 'PureBrain')` to reveal
- Witness/AiCIV calls this after portal is ready
- Sets href dynamically, updates AI name, smooth fade-in animation
- Scrolls button into view on reveal

### HTML Structure
```html
<div id="pb-brain-stream-wrapper" style="display:none;">
  <span id="pb-brain-stream-eyebrow">Your AI is ready</span>
  <a id="pb-brain-stream-btn" href="#brain-stream-link" data-brain-stream-url="#brain-stream-link">
    Click to Connect to <span id="pb-bs-ai-name">Your AI</span>'s Brain Stream
  </a>
  <span id="pb-brain-stream-subtext">Your personalized AI portal is ready...</span>
</div>
```

### CSS Features
- Gold-to-orange gradient (`#f59e0b → #f87c0a → #f1420b`)
- Pulsing glow animation (`pb-bs-pulse`)
- Hover: scale(1.05) + translateY(-3px) + stronger glow
- Smooth fade-in transition on reveal

## Page Details

| Property | Value |
|----------|-------|
| Page ID | 1232 |
| Slug | pay-test-sandbox-3 |
| URL | https://purebrain.ai/pay-test-sandbox-3/ |
| Password | PureBrain.ai253443$$$ |
| Template | elementor_canvas |
| Status | publish |
| Source | Cloned from page 689 (pay-test-2) |

## Verification (Live Page)

All checks ran against `https://purebrain.ai/pay-test-sandbox-3/`:

| Check | Result |
|-------|--------|
| `async function runBirthInit(` | 0 — REMOVED |
| `async function runTelegramSetup(` | 0 — REMOVED |
| `function isValidBotToken(` | 0 — REMOVED |
| `oauthUrl = startData` | 0 — REMOVED |
| `await runBirthInit(` | 0 — REMOVED |
| `await runTelegramSetup(` | 0 — REMOVED |
| PayPal integration | 68 occurrences — KEPT |
| `initPayTestFlow` | 11 occurrences — KEPT |
| `runPortalButtonWatcher` | 9 occurrences — KEPT |
| `runCompletion` | 3 occurrences — KEPT |
| `runBehindTheCurtain` | 2 occurrences — KEPT |
| `pb-brain-stream-btn` | 4 occurrences — ADDED |
| `showBrainStreamButton` | 6 occurrences — ADDED |

Page 689 (pay-test-2) confirmed UNTOUCHED.

## How to Use the Brain Stream Button

From Witness/AiCIV, once the portal is ready:
```javascript
// Call this on the page to reveal and link the button
window.showBrainStreamButton('https://purebrain.ai/portal/?magic=TOKEN', 'PureBrain');
```

The button will:
1. Update its text to "Click to Connect to PureBrain's Brain Stream"
2. Set href to the magic link URL
3. Fade in with animation
4. Scroll itself into view

## Script Files (session-only, not persisted)
- `/tmp/build_sandbox3_v2.py` — initial clone (used post_content, needed fixing)
- `/tmp/modify_elementor_sandbox3.py` — FINAL CORRECT script that modified _elementor_data
