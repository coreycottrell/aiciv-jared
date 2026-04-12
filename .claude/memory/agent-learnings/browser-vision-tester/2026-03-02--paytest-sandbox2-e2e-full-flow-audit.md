# Memory: Pay-Test Sandbox-2 E2E Full Flow Audit

**Date**: 2026-03-02
**Agent**: browser-vision-tester
**Type**: pattern + gotcha + synthesis
**Tags**: browser-vision, visual-testing, purebrain, paytest, sandbox, seed-firing, playwright, paypal

---

## Context

Full E2E test of `https://purebrain.ai/pay-test-sandbox-2/` for Monday go-live validation.
v4.9 post-payment script with Claude Max check + 3-stage seed firing architecture.
Goal: verify chatbox fires seeds to Witness/AI-CIV at correct trigger points.

---

## Key Findings

### 1. Page Architecture (Critical to Know)

Page 688 (pay-test-sandbox-2) has TWO content locations in WordPress:
- `content.raw` (WP REST API) = ONLY the post-payment v4.9 script (98k chars). Not the full page.
- `meta._elementor_data` widget ID `292c72a` = full 456k char self-contained HTML with pre-payment chatbox + pricing + PayPal SDK + sandbox bypass button

If testing from WP REST API content alone, page will render as `<!-- wp:html --><!-- /wp:html -->` only. Must use live URL.

### 2. Playwright Patterns That Work on This Page

```python
# Password unlock
await pw_inp.fill(PAGE_PASSWORD)
sub = await page.query_selector('input[type="submit"]')
if sub: await sub.click()
else: await pw_inp.press("Enter")
await asyncio.sleep(10)  # Wait for full page render after unlock

# Begin Awakening (JS click - not Playwright click)
await page.evaluate("document.querySelector('.chat-initial__btn').click()")
await asyncio.sleep(3)

# Bypass code - MUST use dispatchEvent, not just .value
await page.evaluate("""
    var inp = document.getElementById('userInput');
    if (inp) {
        inp.value = 'pb-full-bypass';
        inp.dispatchEvent(new Event('input', {bubbles: true}));
    }
    var sub = document.getElementById('submitBtn');
    if (sub) sub.click();
""")
await asyncio.sleep(6)

# proCta click - element is OFF viewport, cannot scroll to it
# Use JS click directly, NOT Playwright .click() or scroll_into_view_if_needed()
await page.evaluate("document.getElementById('proCta').click()")
await asyncio.sleep(5)

# Sandbox bypass button
await page.evaluate("document.getElementById('pb-sandbox-bypass-btn').click()")
await asyncio.sleep(15)  # Seeds fire async - need full wait

# NO full_page=True screenshots on this page (Three.js/WebGL causes timeout)
await page.screenshot(path=path, timeout=10000)  # 10s timeout for regular shots
```

### 3. Seed Fire Architecture (v4.9)

3-stage seed firing sequence:
- Stage 1: `fireSeed('payment_complete', 1)` - fires in `handlePaymentSuccess()`
- Stage 2: `fireSeed('oauth_authenticated', 2)` - fires after OAuth complete
- Stage 3: `fireSeed('portal_ready', 3)` - fires when portal launches

Endpoints:
- Primary: `https://api.purebrain.ai/api/intake/seed`
- Fallback: `http://104.248.239.98:8200/intake/seed`

**Gotcha**: HTTP fallback endpoint is mixed-content blocked when page is HTTPS.
Playwright headless may not capture seed fires even if they ARE firing.
Always verify via Witness server logs, not just Playwright network layer.

### 4. orderId Field Name Mismatch (Bug Found)

Client sends: `{ orderId: "SANDBOX-TEST-..." }` (camelCase)
Server expects: `{ order_id: "..." }` (snake_case)
Result: `{ error: "Missing required field: order_id" }`

Flow continues regardless (sandbox bypass does not block on verify failure).
In production this could be a real issue. Needs fix before go-live.

### 5. JS Scope Fix Pattern ([PB-FIX])

On every page load: `[PB-FIX] openPayPalCheckout not found, retrying...` fires 4x
Then: `[PB-FIX] PayPal routing restored: openWaitlistModal -> openPayPalCheckout`

This is the scope fix from 2026-03-01. It's working but introduces 3-4s delay.
4 PayPal tiers use `openPayPalModal()`. Only Enterprise uses `openWaitlistModal()` (intentional).

### 6. Post-Payment Chatbox Selectors (v4.9)

```python
# Container
".ptc-wrapper, #pay-test-post-payment"

# AI messages
".ptc-msg--ai, .ptc-msg.ptc-msg--ai"

# Initial messages confirmed
# msg[0]: "Hey - welcome. I'm Your AI..."
# msg[1]: "Let's start simple. What's your full name?"

# Textarea input - CANNOT use .value alone
# Must use page.type() for v4.9 (React-style onChange handlers)
# page.evaluate(".value = x") does NOT trigger onChange
```

### 7. WAF Rate Limiting

GoDaddy WAF blocks after 3+ rapid page loads in a session.
Symptoms: Page loads but JS functions (`openPayPalModal`, etc.) are `undefined`.
Recovery: 15-20 min wait between test runs.

### 8. Screenshots

Path: `/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-live-sandbox2-20260302/`
Key files:
- `005-p2b-after-bypass.png` - Pre-payment chatbox post-bypass (4 msgs + Activate Now)
- `009-p4a-ptc-initial.png` - Post-payment chatbox (2 initial messages confirmed)

---

## Go-Live Checklist Derived from This Test

- [ ] Fix `orderId` -> `order_id` field mismatch in verify-payment
- [ ] Confirm seeds reach Witness via server logs (check ~14:00-14:05 UTC 2026-03-02)
- [ ] Manual Q&A flow test to confirm portal button appears after all questions
- [ ] Optional: Fix `[PB-FIX]` retry timing (4x on every load)

---

## Patterns to Apply Next Time

1. Always use JS click (`page.evaluate`) for off-viewport elements, never Playwright `.click()`
2. Never `full_page=True` on pages with Three.js/WebGL
3. Use `page.type()` not `.value =` for textarea input in React-style chatboxes
4. Seed verification = check Witness server logs, not just Playwright network interceptor
5. WAF rate limit = wait 15+ min between full test runs on live purebrain.ai
6. `_elementor_data` contains the real page HTML; `content.raw` is just the injected script

---

## Report Location

Full report: `/home/jared/projects/AI-CIV/aether/exports/e2e-live-sandbox2-report-20260302.md`
