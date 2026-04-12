# Sandbox-3 Brain Stream Button Investigation
**Date**: 2026-03-04
**Type**: diagnosis / gotcha
**Page**: purebrain.ai/pay-test-sandbox-3 (WP page 1232)

---

## ROOT CAUSE IDENTIFIED

Sandbox-3 has TWO SEPARATE button systems that are NOT connected to each other:

### System A: The Flow-Integrated Button (CORRECT — used by runPortalButtonWatcher)
- Located in the chatbox JS code (lines ~1800-1806)
- Injects a `<button id="ptc-portal-placeholder">` into the chat DOM
- Text: `Enter [aiName]'s Brain Stream` (greyed out, disabled)
- When portal-status returns ready:true → replaces placeholder with lit-up `<a class="ptc-portal-btn">`
- This is the CORRECT button Jared sees in the screenshot
- Controlled by `runPortalButtonWatcher()` which polls `/api/birth/portal-status/{container}` every 30s

### System B: The Static HTML Button (WRONG — what QA found)
- Located AFTER the main JS block, as a separate HTML widget (lines ~2110-2195)
- Static `<div id="pb-brain-stream-wrapper">` with `<a id="pb-brain-stream-btn">`
- Default text: `Click to Connect to Your AI's Brain Stream`
- Starts VISIBLE (display:none but wrapper is always present in DOM)
- Triggered via `window.showBrainStreamButton(url, aiName)` external API call
- NEVER called by the chatbox flow — it sits there as dead/orphan HTML
- Was designed for Witness to call externally: `window.showBrainStreamButton(magicLinkUrl, 'PureBrain')`
- Has `href="#brain-stream-link"` placeholder — goes NOWHERE useful

## WHY QA FOUND THE WRONG BUTTON

The E2E test saw `pb-brain-stream-wrapper` div in the DOM because it's hardcoded HTML below the chatbox script. The QA test saw the static "Click to Connect to Your AI's Brain Stream" button — this is System B.

The CORRECT button (System A) only appears dynamically INSIDE the chat DOM after `runPortalButtonWatcher()` runs and user reaches Phase 5 (Learn More). At E2E test time, the flow may not have reached that phase, or the watcher had no containerName.

## WHAT SANDBOX-2 (PAGE 689) DOES

Sandbox-2 does NOT have the static `pb-brain-stream` button at all. It ONLY has System A (the dynamic `ptc-portal-placeholder` + `ptc-portal-btn` pattern). This is why sandbox-2 works correctly.

## THE FIX NEEDED

Option 1 (RECOMMENDED): Remove the orphan static `pb-brain-stream-wrapper` div from sandbox-3. It conflicts with and confuses QA. The flow-integrated button (System A) is what matters.

Option 2: Keep static button but hide it (`display:none` with `!important`) and ensure it's ONLY revealed when `showBrainStreamButton()` is explicitly called from Witness.

Option 3: Remove the `BRAIN STREAM CONNECT BUTTON — v1.0` entire block (lines 2053-2195) from sandbox-3, making it match sandbox-2's architecture.

## KEY FACTS
- `runPortalButtonWatcher` DOES exist in sandbox-3 (line 1834) — function is correct
- `ptc-portal-placeholder` injection DOES exist in sandbox-3 (line 1804) — correct
- Portal-status polling via Witness IS correct (line 1852)
- The `pb-brain-stream-btn` button text "Click to Connect" is the static orphan — NOT the live flow button
- Sandbox-2 lacks the static button entirely — only uses the dynamic chat-injected button

## FILES EXAMINED
- /tmp/sandbox3-raw.html (WP page 1232 raw content, 82KB)
- /tmp/sandbox2-raw.html (WP page 689 raw content, 100KB)
