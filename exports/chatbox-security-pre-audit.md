# security-engineer-tech: PureBrain Post-Payment Chatbox Security Pre-Audit

**Agent**: security-engineer-tech
**Domain**: Security Engineering
**Date**: 2026-02-22

---

## Executive Summary

**Pre-Revamp Security Audit — PureBrain Post-Payment Chat Flow**

Files reviewed:
- `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow.js` (56K)
- `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-paypal.js` (32K)
- `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-integration-glue.js` (4.4K)
- `/home/jared/projects/AI-CIV/aether/exports/pay-test-post-payment-code-analysis.md` (17K)

**Risk Summary**

| Severity | Count |
|----------|-------|
| CRITICAL | 4 |
| MEDIUM | 6 |
| LOW | 3 |

**The CRITICAL findings must be fixed before this flow handles real customers.** The most severe issues are: a live PayPal Client ID hardcoded in client-side JavaScript, the Claude API key (`sk-ant-*`) being collected and stored in plaintext in the browser, the Telegram bot token transmitted to a logging endpoint in plaintext, and the payment verification bypass that allows the post-payment flow to proceed even when server verification explicitly returns `verified: false`.

---

## CRITICAL Findings

---

### CRIT-001: Live PayPal Client ID Hardcoded in Client-Side JavaScript

**File**: `pay-test-script-paypal.js`, line 46

**Evidence**:
```javascript
var PAYPAL_CLIENT_ID = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_';
```

**Impact**: This is the live production PayPal Client ID for the `support@puremarketing.ai` merchant account. It is embedded in a public-facing JavaScript file served inside a WordPress Elementor widget (409K characters of raw HTML). Anyone who views page source can extract it.

**What an attacker can do with it**:
- Load the PayPal SDK with this Client ID from any domain
- Render PayPal buttons that charge the real `support@puremarketing.ai` account
- Craft phishing pages that appear to be official Pure Brain checkout flows
- The Client ID also reveals the merchant account identity, which can be used for targeted fraud against the business account via PayPal's dispute system

**Note on severity**: PayPal Client IDs are technically "semi-public" in that they are needed by the PayPal SDK to render. However, embedding a live production ID in client-side code with no origin restriction (CORS policy on the PayPal SDK load is controlled by PayPal, not you) means any third party can impersonate the merchant's checkout experience.

**Fix for revamp**:
- Set allowed domains in the PayPal developer dashboard under the app's settings — restrict to `purebrain.ai` only
- Consider serving the Client ID from a server-side endpoint that validates the request origin before returning it, rather than hardcoding it in static JS
- Rotate to a new Client ID after the old one has been restricted

---

### CRIT-002: Claude API Key Collected Client-Side and Logged to Backend in Plaintext

**File**: `pay-test-script-chat-flow.js`, lines 1451–1458, 1464

**Evidence**:
```javascript
const sessionInfo = await promptText(
  inputRow, textarea, sendBtn,
  (v) => v.trim().length > 20 && v.trim().startsWith('sk-ant-'),
);
userSay(msgList, sessionInfo);       // <-- renders the key IN THE CHAT UI
payTestData.claudeSessionInfo = sessionInfo;
```

Then in `logPayTestData` (line 59–75), the entire `payTestData` object — which contains `claudeSessionInfo` — is sent to:

```javascript
fetch('https://api.purebrain.ai/api/log-pay-test', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payTestPayload),
})
```

**Impact**:

1. **The key is displayed back in the chat bubble** via `userSay(msgList, sessionInfo)`. Any screen recording, screenshot, shoulder-surf, or shared screen session captures the live API key in full view.

2. **The key is logged to `api.purebrain.ai/api/log-pay-test`** — a backend you control. If that backend stores logs to a database or file system and that system is ever compromised, all collected keys are exposed simultaneously.

3. **Anthropic `sk-ant-*` keys have no scope restrictions** — a key can call any Claude API endpoint, including expensive model calls, and there is no rate-limiting by default. A stolen key costs real money.

4. The key also lives in `window.payTestData` — a global variable — for the entire session duration. Any injected JS or browser extension can read it via `window.payTestData.claudeSessionInfo`.

**Fix for revamp**:
- Do NOT render the key back in the chat UI. Mask it: show only the first 10 characters plus asterisks
- Do NOT include the key in the log payload sent to the backend. Strip it before logging
- If you must store it server-side, encrypt it at rest with a key stored separately from the data
- Validate the key server-side (make a minimal API call like `GET /v1/models` with the key) rather than in the browser
- Consider whether collecting this key in a web chat flow is architecturally necessary — a safer alternative is to have users enter it directly in the Claude.ai or platform.claude.com interface and provide an OAuth-style integration

---

### CRIT-003: Telegram Bot Token Logged to Backend in Plaintext

**File**: `pay-test-script-chat-flow.js`, lines 1328, 59–75

**Evidence**:
```javascript
payTestData.telegramBotToken = token.trim();
```

The `payTestData` object (including `telegramBotToken`) is then included in every subsequent `logPayTestData()` call:

```javascript
const payTestPayload = {
  ...
  telegramBotToken: payTestData.telegramBotToken,
  ...
};
fetch('https://api.purebrain.ai/api/log-pay-test', { body: JSON.stringify(payTestPayload) });
```

**Impact**:

A Telegram bot token is equivalent to full control of that bot. With it, an attacker can:
- Send messages to any user who has messaged the bot
- Read all messages sent to the bot
- Set up webhooks to intercept future messages
- Delete the bot or change its name/profile

If the logging backend stores these tokens in a database and that database is ever breached, every customer's Telegram bot is compromised. The attacker gains the ability to send messages to customers impersonating Pure Brain's AI.

Additionally, the token is stored in `window.payTestData` (a global) for the entire session.

**Fix for revamp**:
- Strip `telegramBotToken` from the log payload before it reaches the backend
- If the backend needs the token to set up webhook integrations, send it in a separate dedicated endpoint with appropriate server-side encryption, not as a log field alongside personally-identifiable information
- Mask the token in the UI after entry (show only the numeric ID portion, e.g. `12345678:****`)
- Consider whether storing this token is necessary at all if the user is setting it up themselves for their own bot

---

### CRIT-004: Payment Verification Bypass — Server `verified: false` Does Not Block Flow

**File**: `pay-test-script-paypal.js`, lines 466–489

**Evidence**:
```javascript
fetch(VERIFY_ENDPOINT, { ... })
  .then(function (response) {
    return response.json().then(function (data) {
      if (!response.ok || data.verified === false) {
        // Log the mismatch — payment may still be valid; do not block the user
        console.warn('[PB PayPal] Server verification returned unverified.', ...);
      } else {
        console.log('[PB PayPal] Server verification confirmed.', data);
      }
      // Proceed regardless so UX is never blocked by a backend issue
      handlePaymentSuccess(tier, orderId, payerInfo);  // <-- fires either way
    });
  })
  .catch(function (err) {
    // Network or CORS error — do not block the user
    console.warn('[PB PayPal] Server verification request failed (network/CORS). ...');
    handlePaymentSuccess(tier, orderId, payerInfo);   // <-- fires on network failure too
  });
```

**Impact**: The server-side verification at `https://api.purebrain.ai/api/verify-payment` is completely non-blocking. If it returns `{ verified: false }`, the code logs a warning and proceeds anyway. If there is a network error, the code also proceeds.

Combined with the sandbox bypass button (lines 584–623) that calls `verifyPaymentServerSide` with fake data, this means:

1. Anyone who loads the page with "sandbox" in the URL path can click "Simulate Successful Payment" and get the full post-payment onboarding experience without paying
2. If the verification endpoint is down, payments proceed client-side without any server confirmation
3. A sophisticated attacker could intercept or spoof the `api.purebrain.ai/api/verify-payment` response to return `verified: false` and the flow would continue anyway

**Note**: The sandbox bypass is conditioned on `window.location.pathname.indexOf('sandbox') !== -1` — if the production URL ever contains "sandbox" (e.g., `pay-test-sandbox-2`), the bypass button appears in production. The URL `purebrain.ai/pay-test-sandbox-2/` already contains "sandbox", meaning this bypass is currently visible on that page.

**Fix for revamp**:
- Make verification blocking: if `verified: false` is returned, display an error and do NOT proceed to the onboarding flow
- On network error, show a "verification temporarily unavailable" message and provide a support contact — do not silently proceed
- Move the sandbox bypass to a separate page that is not accessible on the production domain, or gate it behind an admin flag that is never set on production
- The verification endpoint should cryptographically sign its response so the client can confirm the response is genuine (HMAC or similar)

---

## MEDIUM Findings

---

### MED-001: XSS Vector — AI Message Content Rendered as innerHTML Without Sanitization

**File**: `pay-test-script-chat-flow.js`, lines 759, 805

**Evidence**:
```javascript
// In aiSay():
bubble.innerHTML = text.replace(/\n/g, '<br>');

// In showSlide():
body.innerHTML = content.replace(/\n/g, '<br>');
```

**Impact**: The `text` parameter in `aiSay()` comes from hardcoded string literals in the script itself, so in the current codebase this is not immediately exploitable. However, the pattern is dangerous for the revamp because:

1. If any future backend response is used to populate `text` (e.g., AI-generated messages from a backend API), and that content is not sanitized, it becomes a stored XSS vector
2. The slide content `content` follows the same pattern
3. Error messages from `err.message` are also rendered via `innerHTML`:
   ```javascript
   errMsg.innerHTML = `... <small style="opacity: 0.6;">${err.message}</small>`;
   ```
   If an attacker can influence the error message content (e.g., through a crafted backend response), this is a direct XSS injection point

**Fix for revamp**:
- Use `textContent` for plain text, or use a dedicated HTML sanitization library (DOMPurify) for any content that requires HTML formatting
- For the error message specifically: use `textContent` on the `<small>` element rather than template literal interpolation into `innerHTML`
- Establish a rule: any data originating outside the current script file must be sanitized before DOM insertion

---

### MED-002: Sensitive PII Logged After Every Interaction Step — Over-Collection Pattern

**File**: `pay-test-script-chat-flow.js`, lines 57–149

**Evidence**:
The `logPayTestData` function includes the full cumulative `payTestData` object in every call. This means by `questionnaire:name` (first log), only the name is sent. But by `telegram:complete`, every single call sends the full payload including:
- Full name
- Email address
- Company
- Role
- Primary goal
- Telegram bot token (CRIT-003)
- Claude API key (CRIT-002)
- PayPal order ID
- Pre-purchase conversation history

This data is sent 8+ times to the backend (once per phase step).

**Impact**:
- Every network request that contains this payload is a potential exfiltration vector
- If the backend logs raw request bodies (common in development), all of this data lives in log files
- The pre-purchase conversation history (`preMsgs`) is included in logging — this may include personally sensitive content users typed to the AI that they did not expect to be stored
- GDPR/data minimization principle: collect only what is needed, when it is needed

**Fix for revamp**:
- Log only the fields relevant to the current event, not the entire accumulated state
- Separate the sensitive credentials (token, API key) from the PII logging entirely
- Add a privacy notice before the questionnaire informing users what data is collected and stored
- Define a data retention policy for the logged data

---

### MED-003: Client-Side Payment Tier Manipulation

**File**: `pay-test-script-integration-glue.js`, lines 99–116

**Evidence**:
```javascript
var tier = params.get('tier') || window.paymentTier || 'Bonded';
var orderId = params.get('tx') || window.paymentOrderId || 'RETURN-' + Date.now();
```

**Impact**: When a user returns from the PayPal redirect flow, the `tier` is read directly from the URL query parameter `?tier=`. A user who paid for the `Awakened` tier ($79) could manually set `?tier=Unified` in the URL and be onboarded as a `Unified` tier customer ($999) if the backend does not validate the tier against the actual payment amount.

The `window.paymentTier` global is also set client-side and is readable/writable by any JavaScript on the page.

**Fix for revamp**:
- Never trust the tier from client-side sources (URL params, globals)
- The `api.purebrain.ai/api/verify-payment` endpoint should return the verified tier based on the PayPal order ID, and the client should use that server-confirmed tier — not the URL parameter
- The redirect should not carry tier in the URL at all; the server should know the tier from the order ID

---

### MED-004: Thank-You Page URL Parameters Carry PII Without Expiry

**File**: `pay-test-script-chat-flow.js`, lines 1516–1518 (completion redirect)

**Evidence**:
```javascript
window.location.href = '/thank-you/?name=' + encodeURIComponent(firstName) + '&ai=' + encodeURIComponent(aiName);
```

**Impact**:
- The user's first name is now in the browser's address bar, browser history, and any analytics tools (Google Analytics, Clarity, etc.) that capture full URLs
- The URL will appear in server access logs
- If the user shares the thank-you page URL, their name is revealed
- Analytics platforms (GA4, Microsoft Clarity, Hotjar) collect page URLs by default — this is a GDPR concern if European customers use this flow

**Fix for revamp**:
- Use session storage or a short-lived server-side session token to pass personalization data to the thank-you page rather than URL parameters
- If URL parameters must be used, strip them from the URL after reading (via `history.replaceState`) to prevent analytics collection

---

### MED-005: Fallback Payment Flow Has No Server-Side Verification

**File**: `pay-test-script-paypal.js`, lines 765–766

**Evidence**:
```javascript
window.__pbPaymentYes = function () {
  handlePaymentSuccess(currentTier || 'Unknown', 'FALLBACK-' + Date.now(), {});
};
```

**Impact**: The Approach B fallback (form POST to PayPal popup) has a "Did your payment complete? Yes / No" prompt. If the user clicks "Yes, I paid", `handlePaymentSuccess` is called with a generated fake order ID (`FALLBACK-1234567890`) and no verification whatsoever. There is no server-side confirmation that any payment occurred.

This means any user who sees the fallback flow can self-certify their payment by clicking "Yes, I paid" regardless of whether they actually paid.

**Fix for revamp**:
- The fallback flow should use PayPal's IPN (Instant Payment Notification) or webhook to the backend to confirm payment before triggering onboarding
- If the form POST approach is retained, redirect to a landing page with a `?tx=` parameter that the backend validates against PayPal's Transaction Search API before showing the onboarding flow

---

### MED-006: Pre-Purchase Conversation History Sent to Backend Without User Consent

**File**: `pay-test-script-chat-flow.js`, lines 79–83, 115–131

**Evidence**:
```javascript
const preMsgs = (payTestData.prePurchaseHistory && payTestData.prePurchaseHistory.length)
  ? payTestData.prePurchaseHistory
  : ((window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory)
      ? window._pbPrePurchaseSession.conversationHistory
      : []);
// ...
const convPayload = {
  session_id: logSessionId,
  messages: allMessages, // includes pre-purchase chat
  source: 'purebrain-post-payment',
  page_url: window.location.href,
  ...
};
```

**Impact**: Users who chatted with the pre-purchase AI before paying did not explicitly consent to that conversation being stored on Pure Brain's backend servers. The pre-purchase flow is presented as an exploratory chat; the post-payment flow silently uploads the entire conversation history to `api.purebrain.ai/api/log-conversation`.

Under GDPR Article 6, storing and processing conversation content requires a lawful basis (consent, contract, legitimate interest). The pre-purchase chat happens before any contract is formed with the user. This is a potential compliance issue if any EU users use this flow.

**Fix for revamp**:
- Add a clear data collection notice before or during the pre-purchase chat explaining that conversations may be stored
- Obtain explicit consent before sending pre-purchase history to the backend
- Give users the ability to opt out of conversation history logging

---

## LOW Findings

---

### LOW-001: Error Messages Exposed to End Users May Reveal Internal Information

**File**: `pay-test-script-chat-flow.js`, lines 1597–1606

**Evidence**:
```javascript
errMsg.innerHTML = `
  <div class="ptc-bubble" style="background: #2a0a0a; color: var(--bright-orange);">
    Something went wrong on my end. Please refresh and try again.<br>
    <small style="opacity: 0.6;">${err.message}</small>
  </div>`;
```

**Impact**: JavaScript `Error.message` values can contain internal stack information, API response bodies, or internal path/variable names depending on what throws. Rendering this in the UI can expose implementation details to users (and to anyone inspecting the page) that aid in further attack planning.

**Fix for revamp**:
- Log `err.message` and `err.stack` to the backend for diagnostics but do not render raw error messages in the UI
- Show a generic user-facing message only

---

### LOW-002: Telegram Installation Detection Uses window.location.href Navigation

**File**: `pay-test-script-chat-flow.js`, lines 1115–1143

**Evidence**:
```javascript
window.location.href = 'tg://resolve?domain=BotFather';
```

**Impact**: Navigating `window.location.href` to a `tg://` scheme on some browsers (particularly mobile Safari) can trigger an "Open in Telegram?" dialog that interrupts the user's flow even if they selected "I'm not sure." On browsers where the scheme is not handled, this can trigger a navigation event that breaks back-button history. This is a UX concern with security implications — an unexpected navigation mid-flow could confuse users into thinking they are being redirected to a different site.

**Fix for revamp**:
- Use an anchor element with `href="tg://..."` that the user explicitly clicks, rather than auto-navigating `window.location.href`
- Or skip detection entirely and just show the install/already-installed options

---

### LOW-003: PayPal Plan IDs Exposed Client-Side

**File**: `pay-test-script-paypal.js`, lines 56–61

**Evidence**:
```javascript
var PLAN_IDS = {
  Awakened:  'P-9KA28683EF7622051NGLUFJY',
  Bonded:    'P-1JL98851AU229172RNGLUFJY',
  Partnered: 'P-6JY35646YA5259513NGLUFKA',
  Unified:   'P-6DU61407NY0900135NGLUFKI',
};
```

**Impact**: PayPal Subscription Plan IDs are semi-public by design (the PayPal SDK uses them client-side), but exposing them in client-side JS means competitors or researchers can enumerate your billing plans and pricing directly from source code. More significantly, if an attacker creates a subscription with a stolen payment method using your Plan ID, it goes to your merchant account — meaning your PayPal account becomes the vehicle for fraud.

**Fix for revamp**:
- This is lower severity because PayPal's security model expects Plan IDs to be in client code when using the SDK
- However, in the revamp consider having the server return the Plan ID dynamically based on the selected tier, rather than hardcoding all four in the JS bundle — this makes it harder to enumerate all available plans

---

## Architecture Recommendations for the Revamp

These are not individual vulnerabilities but systemic patterns to change during the revamp:

### 1. Never Collect Credentials in a Chat Interface

The current flow asks users to paste their Telegram bot token and Claude API key into a chat input box. This pattern:
- Normalizes credential sharing in chat interfaces (creates phishing risk for users)
- Stores credentials in chat bubbles and DOM elements
- Transmits credentials through general-purpose logging pipelines

**Alternative**: Use a dedicated form step (not a chat input) with a clearly scoped purpose, visual masking (password-style input), and a dedicated secure endpoint for credential storage that is completely separate from the logging pipeline.

### 2. Move Post-Payment Logic Server-Side

Currently the entire post-payment flow is client-side JavaScript that trusts client-supplied data (tier, order ID, payment status). The revamp should:
- Validate payment server-side before showing the onboarding flow
- Have the server issue a short-lived signed token after payment verification
- Use that token to gate the onboarding flow (client presents token, server validates, then returns the tier and order info — client never decides this itself)

### 3. Separate Logging and Credential Handling Pipelines

The `logPayTestData` function currently sends everything — PII, conversation history, credentials, payment data — in a single payload to a single endpoint. In the revamp:
- Create separate endpoints with separate access controls for: (a) PII/onboarding data, (b) payment data, (c) credentials
- Strip credentials from all logging pipelines entirely
- Apply field-level encryption to sensitive fields before storage

### 4. Add a Content Security Policy Header

The page loads external scripts (Google Fonts, PayPal SDK, Telegram links) and injects inline styles and scripts dynamically. A strong Content-Security-Policy header would limit the damage from any XSS by restricting what external origins can be loaded and whether inline script/style is permitted.

Recommended CSP for the revamp:
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://www.paypal.com https://www.paypalobjects.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src https://fonts.gstatic.com;
  img-src 'self' https://purebrain.ai https://www.paypalobjects.com;
  connect-src 'self' https://api.purebrain.ai;
  frame-src https://www.paypal.com;
```

### 5. Add Rate Limiting to Logging Endpoints

The current implementation fires `logPayTestData()` on every user interaction (name entry, email entry, each button click). This means `api.purebrain.ai/api/log-pay-test` and `/api/log-conversation` receive a burst of 8–15 requests per user session. Without rate limiting, these endpoints are vulnerable to:
- Flood attacks that fill database storage
- Cost amplification (if the backend uses a pay-per-request service)
- Enumeration of session IDs

**Fix**: Apply per-IP and per-session rate limits at the API gateway layer (e.g., Cloudflare rate limiting on `api.purebrain.ai`).

---

## Summary — Must-Fix Before Revamp Ships to Real Customers

| ID | Issue | Severity | Fix Complexity |
|----|-------|----------|----------------|
| CRIT-001 | Live PayPal Client ID in client JS | CRITICAL | Low (config change + domain restriction) |
| CRIT-002 | Claude API key collected + logged plaintext | CRITICAL | High (architecture change needed) |
| CRIT-003 | Telegram bot token logged to backend plaintext | CRITICAL | Medium (strip from log payload + mask in UI) |
| CRIT-004 | Payment verification non-blocking + sandbox bypass on prod URL | CRITICAL | Medium (verification must block + move sandbox page) |
| MED-001 | innerHTML without sanitization | MEDIUM | Low (use DOMPurify or textContent) |
| MED-002 | PII over-collection in every log event | MEDIUM | Medium (restructure log payloads) |
| MED-003 | Client-side tier manipulation via URL param | MEDIUM | Medium (server must own tier determination) |
| MED-004 | PII in thank-you URL tracked by analytics | MEDIUM | Low (use sessionStorage + history.replaceState) |
| MED-005 | Fallback payment has zero verification | MEDIUM | High (requires backend IPN/webhook integration) |
| MED-006 | Pre-purchase chat logged without consent | MEDIUM | Low (add privacy notice + consent) |
| LOW-001 | Raw error messages in UI | LOW | Low (sanitize error display) |
| LOW-002 | Auto-navigating tg:// scheme | LOW | Low (use explicit link instead) |
| LOW-003 | All PayPal Plan IDs exposed in JS bundle | LOW | Low (serve dynamically from backend) |

---

*Analysis performed via static code review only. No requests were made to any live endpoints.*
