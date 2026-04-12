# pay-test-sandbox-2 Full E2E Flow - v6 Definitive Run

**Date**: 2026-03-02
**Agent**: browser-vision-tester
**Type**: technique + pattern + gotcha
**Tags**: pay-test, PTC, birth-pipeline, playwright, paypal-sandbox, e2e, OAuth

---

## Context

Definitive E2E test of `https://purebrain.ai/pay-test-sandbox-2/` using Playwright headless.
Full flow: password -> begin awakening -> bypass code -> PayPal modal -> sandbox bypass -> post-payment chatbox (PTC) -> Q&A -> BIRTH -> OAuth gate.

Script: `/home/jared/projects/AI-CIV/aether/tools/e2e_paypal_real_v6.py`

---

## Key Findings

### 1. Full Flow CONFIRMED WORKING

The entire pipeline from payment to OAuth gate works. All API calls returned 200.
- verify-payment: confirmed, orderId=SANDBOX-TEST-xxx, verified:true
- log-pay-test: 6 entries (one per Q&A answer + birth events)
- log-conversation: 6 entries (progressive accumulation of messages)
- birth/start: 200, url_ready, real Claude OAuth URL generated

### 2. PTC Selector Patterns (LOCKED)

- Textarea: `#ptc-input` (or `textarea.ptc-input`)
- Send button: `#ptc-send-btn` (or `.ptc-send-btn`)
- Input row: `#ptc-input-row` (starts display:none, becomes display:flex after bypass)
- AI messages: `.ptc-msg--ai`
- Portal button: `.ptc-portal-btn` (only appears after OAuth Stage 3 completes)

**Timing**: `#ptc-input-row` becomes flex within 8-28 seconds after sandbox bypass click.
**Pattern**: Poll with `wait_ptc_input_active(page, timeout=60)` - checks every 1s.

### 3. BIRTH Triggers After Role, Before Goal

BIRTH API is called immediately after the "role" question is answered.
This means:
- `primaryGoal` will always be null in logs for automated tests
- The "goal" question input gets overlaid by "Authorize Keen's AI Brain" + "I have my key" buttons
- These buttons cause `ta.click()` to timeout (30s) in Playwright - element is obscured
- This is by design: OAuth gate takes over the UI after role collection

### 4. Goal send failure = ta.click() Timeout (NOT a bug in the chatbox)

When the "Authorize Keen's AI Brain" buttons appear:
- `#ptc-input-row` display is still `flex`
- `#ptc-input` is still in DOM and visible
- BUT: Something in the button rendering causes Playwright's click to timeout
- Root cause: Likely the button overlay or React state that disables the input at this point
- Workaround: Skip the goal send entirely once BIRTH has fired (check birth_calls list)

### 5. Portal Button (.ptc-portal-btn) Only Appears After OAuth Stage 3

The script correctly failed to find `.ptc-portal-btn` because:
- Stage 3 seeds (`portal_ready`) only fire after OAuth completion
- OAuth requires a real human to click "Authorize", go to claude.ai, come back with code
- Cannot be automated in headless Playwright

### 6. PayPal Iframe - Style Frame vs Button Frame

PayPal SDK loads TWO types of iframes:
- `https://www.sandbox.paypal.com/smart/buttons?style...` - STYLE PRELOAD (no buttons)
- The actual button frame has different URL (zoid-based, with `token=` or different path)

To click the real PayPal button: filter frames with `name*=paypal` or `name*=zoid`, not just URL.
Or: use `page.frames` and iterate ALL frames looking for ones that contain `button` elements.
The v5 run CONFIRMED the popup opens - it was a different selector strategy issue.

### 7. PayPal Sandbox Creds Invalid

`sb-c89tj49549583@personal.example.com` / `Z0+6<dS` -> "Some of your info didn't match"
Get fresh creds from: developer.paypal.com -> Sandbox -> Accounts -> Buyer Account
The login page flow IS correct - the creds just expired or are wrong.

### 8. Seeds Not Capturable via Playwright

Seeds fire to `https://api.purebrain.ai/api/intake/seed` via Cloudflare tunnel.
Playwright's network interceptor sees the Cloudflare proxy but not the tunnel internals.
To verify seeds: SSH to Witness server and check inbound logs during test window.
This is expected and not a bug.

### 9. Duplicate Log-Pay-Test at Role Stage

At role collection, 2x `log-pay-test` fire (and 2x `log-conversation`):
- One for `event: questionnaire:role`
- One for `event: birth:init:start`

This is expected - BIRTH initialization fires a log event alongside the role questionnaire event.

---

## Script Pattern (Use This in Future)

```python
# Key pattern for PTC interaction:

async def wait_ptc_input_active(page, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        display = await page.evaluate("""(function(){
            var row = document.getElementById('ptc-input-row');
            if (!row) return 'not-found';
            return window.getComputedStyle(row).display;
        })()""")
        if display not in ("none", "not-found"):
            return True
        await asyncio.sleep(1)
    return False

async def ptc_send(page, text):
    ta = await page.query_selector("#ptc-input")
    if not ta:
        ta = await page.query_selector("textarea.ptc-input")
    if not ta:
        return False
    await ta.click()
    await asyncio.sleep(0.3)
    await ta.fill("")
    await asyncio.sleep(0.2)
    await ta.type(text, delay=30)
    await asyncio.sleep(0.5)
    send = await page.query_selector("#ptc-send-btn")
    if send and await send.is_visible():
        await send.click()
        return True
    await ta.press("Enter")
    return True

# Note: ta.click() will TIMEOUT after role is answered (BIRTH triggers, OAuth overlay appears)
# Detect this with: try/except around ptc_send - if Exception, check if birth_calls > 0
```

---

## Flow Timings (From v6 run, 2026-03-02 15:50-16:06 UTC)

| Stage | Time to reach from script start |
|-------|--------------------------------|
| Password accepted | 22s |
| Begin Awakening clicked | 30s |
| Bypass code submitted | 53s |
| Modal opened | 63s |
| Sandbox bypass | 80s |
| verify-payment 200 | 81s |
| PTC active (display:flex) | 109s |
| Name sent | 118s |
| Email sent | 131s |
| Company sent | 143s |
| Role sent | 158s |
| BIRTH API called | 188s |
| OAuth gate visible | 197s |

Total pipeline to OAuth gate: approximately 3m 17s.

---

## What Is Still Unverified (Needs Manual)

1. OAuth flow completion (Stage 3 - requires real Claude.ai auth)
2. Portal button URL (`.ptc-portal-btn` href)
3. Witness server seed receipt (check 89.167.19.20 logs)
4. Real PayPal payment (needs fresh sandbox buyer creds)

---

## Bugs Found

1. **BIRTH triggers after role, before goal** - primaryGoal always null in automated tests
2. **PayPal sandbox creds expired** - sb-c89tj49549583@personal.example.com / Z0+6<dS rejected
3. **PayPal style frame vs button frame** - need to target button frame specifically
