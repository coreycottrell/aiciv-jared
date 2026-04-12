# Memory: pay-test-sandbox-3 Post-Payment Chatbox Fix

**Date**: 2026-03-03
**Type**: gotcha + fix + pattern
**Topic**: runCompletion function missing from cloned pay-test page causing blank black screen

---

## Root Cause

Page 1232 (pay-test-sandbox-3) was cloned from page 689 (pay-test-2).
During cloning, the `runCompletion` function was accidentally deleted from widget 292c72a.

The function list in page 1232 widget was:
`runQuestionnaire → runBehindTheCurtain → runThankYouMessage → runLearnMoreLoop → runPortalButtonWatcher → initPayTestFlow`

Missing: `runCompletion` (Phase 4 — Completion Message)

The `initPayTestFlow` function calls `await runCompletion(dom, aiName, firstName)` which threw a **ReferenceError: runCompletion is not defined** at runtime.

The error was caught by the `catch (err)` block in `initPayTestFlow`, which appended a brief error bubble to the overlay div. The result was a blank #0a0a0a fixed overlay covering the page — appearing as a "blank black screen."

---

## How It Was Diagnosed

1. Fetched live page 1232 with auth (two-step cookie approach)
2. Verified all scripts were present: PayPal popup, v4.7 chat flow, integration glue, BrainStream
3. Found script load order was correct
4. Listed all `function` and `async function` declarations in the chat flow script
5. `runCompletion` was NOT in the function list
6. Confirmed `await runCompletion(...)` was called in `initPayTestFlow`
7. Compared with page 688 (working) → 688 has `runCompletion`, 1232 does not

---

## The Fix

Extracted `runCompletion` from page 688's widget 292c72a and inserted it into page 1232's widget 292c72a immediately before `initPayTestFlow`.

The function was inserted at position ~426403 in the widget HTML with a phase comment:
```
// ---------------------------------------------------------------------------
// PHASE 4 — Completion Message
// ---------------------------------------------------------------------------
async function runCompletion(dom, aiName, firstName) { ... }
```

Deployed via WordPress REST API to `_elementor_data` meta, cleared Elementor cache.

---

## runCompletion Function (for reference)

```javascript
async function runCompletion(dom, aiName, firstName) {
  const { msgList, actions } = dom;

  await aiSay(
    msgList,
    `${firstName} — you're done. Everything is in place.<br><br>` +
    `${aiName} is ready. Your team of 22 Brains starts the moment I hand this conversation off. ` +
    `They already know your name, they already know what you need, ` +
    `and ${aiName} is already thinking about what to build you first.`,
    1100,
  );

  await aiSay(
    msgList,
    `This is going to be worth it.<br><br>` +
    `— ${aiName}`,
  );

  payTestData.timestamps.flowComplete = new Date().toISOString();
  logPayTestData({ ...payTestData, event: 'flow:complete' });

  // Welcome button — v3: NO redirect; click triggers in-chat thank-you
  const welcomeBtn = document.createElement('button');
  welcomeBtn.className = 'ptc-welcome-btn';
  welcomeBtn.textContent = `${aiName} is ready — see your next steps →`;
  welcomeBtn.addEventListener('click', async () => {
    welcomeBtn.remove();
    actions.innerHTML = '';
    await runThankYouMessage(dom, aiName, firstName);
  });

  actions.innerHTML = '';
  dom.container.appendChild(welcomeBtn);
}
```

---

## Page 1232 Architecture Notes

- Widget 292c72a: 438,986 char self-contained HTML (contains EVERYTHING)
- content.raw: v4.9 chat flow + BrainStream button — NOT rendered (elementor_canvas template bypasses WP loop)
- PayPal client ID: AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_ (sandbox)
- SDK URL: https://www.sandbox.paypal.com/sdk/js (sandbox mode)
- Post-payment flow: v4.7 (same as pages 688/689 but without runBirthInit — intentionally removed)
- BrainStream button: present as static HTML, hidden by CSS display:none, revealed by window.showBrainStreamButton()
- Password: PureBrain.ai253443$$$

---

## Key Gotcha

**When cloning Elementor pages that use custom HTML widgets with large JS payloads**:
- Functions can be silently deleted during clone/edit
- The async error catch blocks in initPayTestFlow swallow errors silently (no console.error shown to user)
- Result: blank black screen (the position:fixed overlay exists but chat UI never built)

**Diagnostic pattern**: List all `function` / `async function` declarations in the script, then check which ones are called vs defined. Any called-but-undefined function will silently crash async flow.

---

## Verification

All 9 checks passed after deployment:
- runCompletion defined ✓
- runCompletion called in initPayTestFlow ✓
- initPayTestFlow present ✓
- runThankYouMessage present ✓
- runBehindTheCurtain present ✓
- runQuestionnaire present ✓
- initPayTestFlow exported ✓
- onPaymentComplete defined ✓
- BrainStream button defined ✓

---

**Tags**: purebrain, pay-test, sandbox, post-payment, chatbox, runCompletion, missing-function, elementor, clone
