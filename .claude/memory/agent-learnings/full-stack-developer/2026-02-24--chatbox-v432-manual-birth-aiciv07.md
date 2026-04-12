# Chatbox v4.3.2 - Manual Birth Trigger + Explicit Container

**Date**: 2026-02-24
**Type**: operational
**Topic**: Pay-test chatbox v4.3.2 — manual runBirthInit + hardcoded aiciv-07

## What Was Done

Two changes to `exports/pay-test-script-chat-flow-v4.js` for sandbox page 688:

### Change 1: Manual birth trigger
- Old: `runBirthInit()` auto-fired at end of `runQuestionnaire()` after Q4
- New: Shows AI message + "Start AI Birth →" button (class `ptc-link-btn`)
- `runBirthInit()` only fires after button click
- Button disabled immediately on click to prevent double-fire
- Shows "Initiating birth…" feedback message while button is disabled
- Reason: Witness has single-threaded Flask webhook; auto-fire every 2.5 min was blocking their server

### Change 2: Hardcoded container
- Old: Resolved from `window._pbContainerName` or firstName-derived slug
- New: `window._pbContainerName = 'aiciv-07'` + `const containerName = 'aiciv-07'` hardcoded in `runBirthInit()`
- POST /api/birth/start always sends {"container": "aiciv-07"}
- Reason: Auto-allocation was picking aiciv-08 with stale processes

## File Updated
`/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js` v4.3.2

## Deployment Pattern for Elementor Pages
- Page 688 uses Elementor HTML widget (widget ID 292c72a at path [0].elements[0])
- Must update `_elementor_data` meta field — NOT `post_content`
- `content.raw` will be empty (0 bytes) for Elementor pages — normal
- Cloudflare CDN caches purebrain.ai pages for 31 days
- Testers bypass: Ctrl+Shift+R in Chrome, or add ?v=NNN query param

## Verification Results
- Elementor data in DB: ALL PASS (v4.3.2, aiciv-07, Start AI Birth, birthBtn.disabled)
- Live page: Cloudflare cache HIT until testers force-refresh
