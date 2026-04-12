# Witness Birth Pipeline — v4 Chatbox Integration Spec

**Issued by**: CTO
**Date**: 2026-02-24
**For**: full-stack-developer (already building), api-architect (review), security-engineer-tech (review), qa-engineer (test)

---

## Objective

Wire the Witness Birth Pipeline into PureBrain post-payment chatbox v3 to produce v4.
Output file: `exports/pay-test-script-chat-flow-v4.js`

---

## What Exists in v3 (Do Not Break)

- `runPortalButtonWatcher(dom, aiName)` — exists, polls WRONG endpoint, needs endpoint fix only
- `runThankYouMessage(dom, aiName, firstName)` — exists, triggers watcher + learnMore concurrently
- `runLearnMoreLoop(dom, aiName, firstName)` — exists, untouched
- `payTestData` object — add `containerName` field only
- `initPayTestFlow` — untouched
- All Phase 1–4 code — untouched

---

## Changes Required

### Change 1: Add containerName to payTestData

```js
const payTestData = {
  // ... existing fields ...
  containerName: null,   // NEW: "{civname}-{humanname}" from payment metadata
};
```

In `initPayTestFlow`, before the flow starts:

```js
// Resolve container name from payment metadata (injected by integration glue)
payTestData.containerName = window._pbContainerName || `purebrain-${orderId || 'guest'}`;
```

---

### Change 2: New function runBirthInit(dom)

Insert call BEFORE `runPortalButtonWatcher` inside `runThankYouMessage`, after the "Learn more" button is clicked.

```js
// ---------------------------------------------------------------------------
// PHASE 5b — Witness Birth Init + OAuth Flow (NEW in v4)
// Calls /start → shows OAuth URL → collects code → calls /code
// Runs BEFORE runPortalButtonWatcher and runLearnMoreLoop
// ---------------------------------------------------------------------------

async function runBirthInit(dom) {
  const { msgList, actions } = dom;
  const container = payTestData.containerName;
  const WITNESS_BASE = 'https://api.purebrain.ai/api/birth';  // Proxied — never call 104.x directly from browser
  const TIMEOUT_MS = 180_000;

  // Step 1: Call /start
  await aiSay(msgList,
    `Hold on one moment \u2014 I\u2019m initializing your AI environment now.\u2026`,
    600
  );

  let oauthUrl;
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);

    const resp = await fetch(`${WITNESS_BASE}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ container }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);

    if (!resp.ok) throw new Error(`/start returned ${resp.status}`);
    const data = await resp.json();
    if (!data.oauth_url) throw new Error('No oauth_url in response');
    oauthUrl = data.oauth_url;

  } catch (err) {
    // Graceful fallback — don't kill the flow
    await aiSay(msgList,
      `Your environment is taking a moment to spin up \u2014 no action needed from you. ` +
      `We\u2019ll email you with access details within 5 minutes.`,
      800
    );
    await logPayTestData({ ...payTestData, event: 'birth:start:error', error: err.message });
    return;  // Skip OAuth step, portal-status polling will still run
  }

  // Step 2: Show OAuth URL + instructions
  await aiSay(msgList,
    `Your AI environment is ready to be authorized. Here\u2019s what to do:<br><br>` +
    `<strong>1.</strong> Click the button below to open the authorization page.<br>` +
    `<strong>2.</strong> Sign in and approve access.<br>` +
    `<strong>3.</strong> Copy the <strong>8-character code</strong> shown and paste it back here.`,
    900
  );

  // Show "Authorize Your AiCIV" button — opens oauth_url in new tab
  // Validate oauth_url before using it
  let safeOauthUrl;
  try {
    const parsed = new URL(oauthUrl);
    if (!['https:', 'http:'].includes(parsed.protocol)) throw new Error('Bad protocol');
    safeOauthUrl = oauthUrl;
  } catch {
    safeOauthUrl = 'https://claude.ai/authorize';
  }

  await new Promise((resolve) => {
    actions.innerHTML = '';
    const authBtn = document.createElement('a');
    authBtn.href = safeOauthUrl;
    authBtn.target = '_blank';
    authBtn.rel = 'noopener noreferrer';
    authBtn.className = 'ptc-btn ptc-btn--primary';
    authBtn.textContent = 'Authorize Your AiCIV \u2192';
    authBtn.style.display = 'inline-block';
    authBtn.style.textDecoration = 'none';

    const doneBtn = document.createElement('button');
    doneBtn.className = 'ptc-btn ptc-btn--secondary';
    doneBtn.textContent = 'I\u2019ve got the code \u2192';
    doneBtn.style.marginTop = '8px';
    doneBtn.addEventListener('click', () => {
      actions.innerHTML = '';
      resolve();
    });

    actions.appendChild(authBtn);
    actions.appendChild(document.createElement('br'));
    actions.appendChild(doneBtn);
  });

  // Step 3: Collect auth code
  await aiSay(msgList, `Paste the 8-character code from the authorization page here:`, 400);

  let authCode;
  let attempts = 0;
  while (attempts < 2) {
    authCode = await new Promise((resolve) => {
      actions.innerHTML = '';
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 8;
      input.placeholder = 'e.g. A1B2C3D4';
      input.className = 'ptc-input';
      input.autocomplete = 'off';
      input.autocorrect = 'off';
      input.autocapitalize = 'none';
      input.spellcheck = false;

      const submitBtn = document.createElement('button');
      submitBtn.className = 'ptc-btn ptc-btn--primary';
      submitBtn.textContent = 'Submit Code';
      submitBtn.addEventListener('click', () => {
        // Sanitize: strip whitespace, allow only alphanumeric, max 8 chars
        const raw = (input.value || '').trim().replace(/[^A-Za-z0-9]/g, '').slice(0, 8);
        if (raw.length < 4) {
          input.style.borderColor = 'var(--bright-orange)';
          input.focus();
          return;
        }
        actions.innerHTML = '';
        resolve(raw);
      });

      actions.appendChild(input);
      actions.appendChild(submitBtn);
      input.focus();
    });

    // Step 4: Relay code to Witness
    try {
      const resp = await fetch(`${WITNESS_BASE}/code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ container, code: authCode }),
      });
      if (!resp.ok) throw new Error(`/code returned ${resp.status}`);
      await logPayTestData({ ...payTestData, event: 'birth:code:success' });
      break;  // Success — exit retry loop
    } catch (err) {
      attempts++;
      await logPayTestData({ ...payTestData, event: 'birth:code:error', attempt: attempts, error: err.message });
      if (attempts >= 2) {
        await aiSay(msgList,
          `We had trouble verifying that code. No worries \u2014 your access will be emailed to you within 5 minutes.`,
          700
        );
        return;
      }
      await aiSay(msgList, `That code didn\u2019t work \u2014 let\u2019s try once more. Paste it again:`, 500);
    }
  }

  await aiSay(msgList,
    `Authorization confirmed. Your AI environment is now being fully initialized \u2014 ` +
    `this takes about 5 minutes. I\u2019ll show you a button the moment it\u2019s ready.`,
    800
  );
  await logPayTestData({ ...payTestData, event: 'birth:init:complete' });
}
```

---

### Change 3: Fix runPortalButtonWatcher endpoint

Replace the `checkPortalReady` inner function body only. Everything else stays identical.

**Old:**
```js
const resp = await fetch('https://api.purebrain.ai/api/portal-status', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  mode: 'cors',
  body: JSON.stringify({
    email: payTestData.email,
    aiName: payTestData.aiName,
    orderId: payTestData.orderId,
  }),
});
```

**New:**
```js
const container = payTestData.containerName;
// WITNESS ENDPOINT FIX (v4): was POST to api.purebrain.ai — now GET to Witness via proxy
const resp = await fetch(`https://api.purebrain.ai/api/birth/portal-status/${encodeURIComponent(container)}`, {
  method: 'GET',
  headers: { 'Accept': 'application/json' },
  mode: 'cors',
});
```

---

### Change 4: Wire runBirthInit into runThankYouMessage

In `runThankYouMessage`, after `if (choice === 'learn') {`:

**Old:**
```js
if (choice === 'learn') {
  runPortalButtonWatcher(dom, aiName);
  await runLearnMoreLoop(dom, aiName, firstName);
}
```

**New:**
```js
if (choice === 'learn') {
  // Step 1: Birth init (OAuth) — blocking, must complete before watcher
  await runBirthInit(dom);
  // Step 2: Portal watcher + LearnMore run concurrently
  runPortalButtonWatcher(dom, aiName);
  await runLearnMoreLoop(dom, aiName, firstName);
}
```

---

## Proxy Requirement (CRITICAL — Security Must Confirm)

The browser cannot call `http://104.248.239.48:8099` directly from `https://purebrain.ai` due to
mixed-content blocking. All Witness calls in the JS must go through:

```
https://api.purebrain.ai/api/birth/* → http://104.248.239.48:8099/api/birth/*
```

This proxy must be configured on api.purebrain.ai (Cloudflare Worker or Nginx reverse proxy)
BEFORE v4 is deployed. The full-stack-developer must either:
(a) Confirm an existing proxy is configured, OR
(b) Deploy a Cloudflare Worker rule for this route

---

## Deployment Sequence

1. full-stack-developer produces `exports/pay-test-script-chat-flow-v4.js`
2. Confirm/deploy the api.purebrain.ai/api/birth/* proxy
3. security-engineer-tech reviews v4 code (XSS on input, containerName injection, CORS)
4. Deploy to page 688 (sandbox-2) only
5. qa-engineer tests page 688
6. On QA pass: deploy to page 689 (pay-test-2)
7. Mark done

---

## v4 Version Header

Update top comment:
```
/* === Post-Payment Chat Flow v4 (Witness Birth Pipeline: runBirthInit, OAuth, portal-status fix) === */
```

---

## Container Name Note

The spec says container name comes from `window._pbContainerName` (injected by integration glue / payment
metadata). If that is not yet wired in the payment glue, use this fallback for now:
`purebrain-${orderId || Date.now()}`. Witness nursemaid provisioning (what triggers it before /start)
is still an open question — for this integration, assume the container is provisioned by the time
the customer reaches the thank-you screen (~2–3 min post-payment).
