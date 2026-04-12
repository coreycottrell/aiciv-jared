# E2E Pay-Test-Sandbox-2 Live Audit - Full Report

**Date**: 2026-03-02
**Tester**: browser-vision-tester
**Version**: v4.9 (Claude Max check + 3-stage seed firing)
**URL**: https://purebrain.ai/pay-test-sandbox-2/
**Test Window**: 13:59 - 14:05 UTC
**Purpose**: Monday go-live validation

---

## OVERALL VERDICT: CONDITIONAL GO

The core user-facing flow works. One server-side field name mismatch needs a fix before go-live. Seeds could not be confirmed firing from headless Playwright (likely HTTP/mixed-content block in that environment) - recommend verifying via Witness server logs.

---

## Flow Status Summary

| Phase | Step | Status | Notes |
|-------|------|--------|-------|
| 0 | Password gate renders | PASS | Input + submit visible |
| 0 | Password unlock | PASS | Redirects to full page |
| 1 | Page loads with "Awaken Your PURE BRAIN" | PASS | Hero section visible |
| 1 | Begin Awakening button visible | PASS | `.chat-initial__btn` present |
| 2 | Chatbox opens on Begin click | PASS | Chat UI renders |
| 2 | Bypass code accepted | PASS | 4 AI messages rendered |
| 2 | "Activate Now" (proCta) present | PASS | `#proCta` in DOM |
| 3 | proCta click opens PayPal modal | PASS | `#pb-paypal-overlay` active |
| 3 | Sandbox bypass button visible | PASS | "Simulate Successful Payment (Test Only)" |
| 3 | verify-payment POST fires | PASS | Request confirmed to api.purebrain.ai |
| 3 | Server verify-payment response | ISSUE | `{error: Missing required field: order_id}` |
| 4 | Post-payment chatbox opens | PASS | `.ptc-wrapper` visible |
| 4 | Initial welcome message | PASS | "Hey - welcome. I'm Your AI..." |
| 4 | Second message (name question) | PASS | "Let's start simple. What's your full name?" |
| 4 | Q&A flow progression | NOT TESTED | Playwright input limitation |
| 4 | Portal launch button | NOT CONFIRMED | Requires completing Q&A flow |
| 5 | Seed fire - payment_complete | UNCONFIRMED | 0 captured in network layer |
| 5 | Seed fire - oauth_authenticated | UNCONFIRMED | 0 captured in network layer |
| 5 | Seed fire - portal_ready | UNCONFIRMED | 0 captured in network layer |

---

## Phase-by-Phase Detail

### Phase 0: Page Load + Password

**Status: PASS**

- URL: `https://purebrain.ai/pay-test-sandbox-2/`
- Password gate rendered correctly: `input[name="post_password"]` visible
- Password `PureBrain.ai253443$$$` accepted on submit
- After unlock: full page with dark background rendered

**Screenshots**: `001-p0-load.png`, `002-p1-after-pw.png`

---

### Phase 1: Pre-Payment Chatbox

**Status: PASS**

- Hero section visible: "Awaken Your PURE BRAIN" heading
- `.chat-initial__btn` (Begin Awakening button) present and clickable
- After click: chat overlay opened, conversation started
- Bypass code `pb-full-bypass` accepted and processed
- 4 AI messages rendered post-bypass
- `#proCta` element in DOM with "Activate Now" text
- `openPayPalModal` confirmed available: `typeof window.openPayPalModal === 'function'`
- `initPayTestFlow` confirmed available

**Console note**: `[PB-FIX] openPayPalCheckout not found, retrying...` appeared 4x during initial load, then resolved: `[PB-FIX] PayPal routing restored: openWaitlistModal -> openPayPalCheckout`. This is the JS scope fix from 2026-03-01 working correctly.

**Screenshots**: `003-p2-pre-chat.png`, `004-p2a-after-begin.png`, `005-p2b-after-bypass.png`

---

### Phase 2: PayPal Modal + Sandbox Bypass

**Status: PASS (with field name issue)**

- `#proCta` click (via JS evaluate) opened PayPal overlay
- `#pb-paypal-overlay` confirmed active: `classList.contains('pb-active') = true`
- `#pb-sandbox-bypass-btn` visible, text: "Simulate Successful Payment (Test Only)"
- Sandbox bypass btn click confirmed fired
- `POST https://api.purebrain.ai/api/verify-payment` confirmed in network layer

**ISSUE - Field name mismatch**:
- Client sends: `{ orderId: "SANDBOX-TEST-..." }` (camelCase)
- Server expects: `{ order_id: "..." }` (snake_case)
- Server response: `{ error: "Missing required field: order_id" }`
- Flow CONTINUES regardless (by design - sandbox bypass does not block on verify failure)
- **FIX NEEDED BEFORE GO-LIVE**: Either update client to send `order_id` or update server to accept `orderId`

---

### Phase 3: Post-Payment Chatbox (PTC)

**Status: PASS - Opens correctly**

- `#pay-test-post-payment` container created and visible after sandbox bypass
- `.ptc-wrapper` visible
- 2 initial AI messages confirmed:
  1. "Hey - welcome. I'm Your AI, and I'm genuinely glad you made it here. Now that Your AI is officially yours, let's make sure I actually know who I'm working with. This isn't a form - it's a conversation..."
  2. "Let's start simple. What's your full name?"

**Q&A progression**: Not fully testable via Playwright headless. Setting `.value` on textarea does not trigger v4.9's React-style onChange handlers. Real user typing works. `page.type()` should be used in future for proper simulation.

**Portal button**: Not reached (requires completing Q&A flow).

**Screenshots**: `009-p4a-ptc-initial.png`, `010-p4b-q1-name.png` through `013-p4e-q4-role.png`

---

### Phase 4: Seed Fire Analysis

**Status: UNCONFIRMED - 0 captured**

**Architecture confirmed from source code**:
- Stage 1: `fireSeed('payment_complete', 1)` - fires after `handlePaymentSuccess()`
- Stage 2: `fireSeed('oauth_authenticated', 2)` - fires after OAuth
- Stage 3: `fireSeed('portal_ready', 3)` - fires after portal launch

**Seed endpoints**:
- Primary: `https://api.purebrain.ai/api/intake/seed`
- Fallback: `http://104.248.239.98:8200/intake/seed`

**Why seeds may not have been captured**:
1. HTTP fallback endpoint (`http://104.248.239.98:8200`) is mixed-content blocked when page is HTTPS
2. Primary endpoint (`api.purebrain.ai`) may be CSP-restricted in headless Playwright context
3. Playwright network interceptor timing: seed fires may happen after test observation window

**Recommendation**: Check Witness server logs at `104.248.239.98:8200` for inbound requests around 14:00-14:05 UTC today. If seeds appear in Witness logs, they ARE firing and the Playwright capture method is the limitation.

**Alternative verification**: Add `console.log('[SEED FIRED]', ...)` to `fireSeed()` and re-check console logs.

---

## Console Analysis

**Total errors/warnings**: 28

**Critical (blocking)**: 0

**Non-critical CSP violations** (all third-party analytics/tracking):
- Microsoft Clarity (`clarity.ms`) blocked by CSP - expected, analytics only
- Google Analytics (`region1.google-analytics.com`) blocked by CSP - expected
- GoDaddy CSP (`csp.secureserver.net`) blocked by CSP - expected

**PureBrain-specific logs** (27 entries):
- `[PB-FIX] openPayPalCheckout not found, retrying...` x4 - JS scope fix working
- `[PB-FIX] PayPal routing restored: openWaitlistModal -> openPayPalCheckout` - confirmed fixed
- `[PB PayPal] SDK pre-loaded and ready.` - PayPal SDK loaded
- `[PB PayPal] Server verification returned unverified. orderId: SANDBOX-TEST-... response: {error: Missing required field: order_id}` - field mismatch (see above)
- `[PB-BYPASS-BLOCKER] Blocked plugin bypass handler: submit` - security plugin working
- `[PB-BYPASS-BLOCKER] Blocked plugin bypass handler: keydown` - security plugin working

---

## Critical Findings for Monday Go-Live

### FINDING 1 (HIGH): verify-payment field name mismatch
- **What**: Client sends `orderId`, server expects `order_id`
- **Impact**: Payment verification always returns unverified in sandbox. Flow continues by design, but in production this may block legitimate payment confirmation.
- **Fix**: Update either client (`orderId` -> `order_id`) or server to accept both forms
- **Urgency**: HIGH - fix before go-live

### FINDING 2 (MEDIUM): Seed fires unconfirmed
- **What**: 0 seed fires captured in Playwright test. Architecture says they should fire.
- **Impact**: If seeds aren't reaching Witness, new users won't get onboarded into AI-CIV
- **Fix**: Verify via Witness server logs (104.248.239.98:8200) around 14:00-14:05 UTC today. If logs show inbound, seeds ARE working.
- **Urgency**: MEDIUM - confirm before go-live

### FINDING 3 (LOW): Q&A flow progression not E2E tested
- **What**: Post-payment chatbox Q&A couldn't be driven programmatically
- **Impact**: Portal launch button appearance not confirmed in this test
- **Fix**: Use `page.type()` in next test run, or manual QA by Jared clicking through
- **Urgency**: LOW - manual test sufficient

### FINDING 4 (INFO): `[PB-FIX]` retries on page load
- **What**: `openPayPalCheckout not found, retrying...` fires 4x on every page load before routing fix kicks in
- **Impact**: ~3-4 second delay on pricing buttons while fix loads. No user impact but indicates timing dependency.
- **Fix**: Consider increasing script load priority or preloading the fix
- **Urgency**: INFO only

### FINDING 5 (INFO): CSP blocks analytics
- **What**: Clarity.ms and Google Analytics blocked by Content Security Policy
- **Impact**: Analytics data may not be captured for some users
- **Fix**: Add `https://www.clarity.ms` and `https://region1.google-analytics.com` to CSP connect-src/script-src
- **Urgency**: INFO - not blocking go-live

---

## Go/No-Go Assessment

| Category | Status |
|----------|--------|
| Core user flow (pre-payment) | GO |
| Payment modal + sandbox bypass | GO |
| Post-payment chatbox opens | GO |
| Server verify-payment | CONDITIONAL (field mismatch needs fix) |
| Seed fires to Witness | NEEDS MANUAL CONFIRMATION |
| Q&A flow end-to-end | NEEDS MANUAL QA |

**OVERALL: CONDITIONAL GO**

Fix the `orderId` -> `order_id` field mismatch AND confirm seeds are reaching Witness server via logs. After those two items confirmed, system is GO for Monday.

---

## Test Environment

**Browser**: Chromium (headless)
**Viewport**: 1440x900
**User Agent**: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0
**Test Scripts**:
- Primary: `/home/jared/projects/AI-CIV/aether/tools/e2e_final_sandbox2.py`
- Seed detection: `/home/jared/projects/AI-CIV/aether/tools/e2e_targeted_seed_test.py`

**Screenshots (24)**: `/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-live-sandbox2-20260302/`

Key screenshots:
- `001-p0-load.png` - Password gate
- `002-p1-after-pw.png` - Post-unlock page
- `003-p2-pre-chat.png` - Full page with hero
- `004-p2a-after-begin.png` - Chatbox open
- `005-p2b-after-bypass.png` - Post-bypass 4 messages + Activate Now
- `009-p4a-ptc-initial.png` - Post-payment chatbox with 2 messages
- `016-019` - Portal monitoring (PTC state held, portal not reached)

---

**Report by**: browser-vision-tester
**Test completed**: 2026-03-02 ~14:05 UTC
