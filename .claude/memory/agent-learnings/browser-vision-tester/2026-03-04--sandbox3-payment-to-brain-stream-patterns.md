# Memory: Sandbox-3 Payment-to-Brain-Stream E2E Testing Patterns

**Agent**: browser-vision-tester
**Date**: 2026-03-04
**Type**: technique + gotcha + pattern
**Tags**: sandbox-3, brain-stream, e2e-testing, playwright, purebrain, fixed-chatbox

---

## Context

Ran comprehensive E2E test of `https://purebrain.ai/pay-test-sandbox-3/` from payment tier through to brain stream end state. 6 script iterations (v1-v6) to solve scroll/DOM architecture challenges.

---

## Critical Architecture Discovery: Fixed Chatbox + Underlying Page

### The DOM Structure
```
#pay-test-post-payment (position:fixed, 0,0,1440,900, z-index:999999)
├── chatbox header (y=0-180)
├── #ptc-messages (overflow:auto, y=181-574, height=393px)
│   └── all chat messages, Welcome card (scrollHeight grows to ~5000px)
├── #ptc-input-row (y=574-677)
│   ├── #ptc-input
│   └── #ptc-send-btn
└── orange CTA button (y=709-767, OUTSIDE #ptc-messages)
```

### The Deceptive Element: #pb-brain-stream-wrapper
`#pb-brain-stream-wrapper` is an **Elementor element on the UNDERLYING PAGE**, NOT inside the fixed chatbox.
- getBoundingClientRect() returns y=3744+ (document coordinate, not viewport)
- Completely hidden behind the fixed chatbox (z-index:999999)
- In sandbox-3, the "Welcome to the Family!" card IS the brain stream end state
- The real "ENTER [NAME]'S BRAIN STREAM" button only appears in full real-user Q&A flow

---

## Key Gotcha: Orange CTA Click Failure

### Problem
`click_text()` using `offsetParent !== null` check FAILS for the orange CTA button.
The button is at y=709-767, OUTSIDE `#ptc-messages` scrollable container.
Even though it's visible in the viewport, `offsetParent` returns null or the wrong value.

### Solution
Use Playwright native click: `await page.click('button:has-text("ready")')`
This works reliably. Do NOT use JS-based `offsetParent` check for elements outside scrollable containers.

---

## Brain Stream End State (Sandbox-3 Specific)

The sandbox-3 brain stream end state is the "Welcome to the Family!" card:
- Orange heading "Welcome to the Family!"
- "WHAT HAPPENS NEXT?" timeline
- "Next 5 mins: Your AI's Brain Stream (portal) will be ready for you to log in."
- Input disabled (`#ptc-input` disabled=True)
- Send button greyed (`#ptc-send-btn` disabled=True, opacity=0.45)
- Input placeholder: "Message Your AI..." (not "Message AICIV...")

To capture it: scroll `#ptc-messages` to bottom after orange CTA click, or use `scrollIntoView` on the Welcome card element.

---

## Scroll Capture Technique

### Problem
`#ptc-messages` scrollHeight grows to ~5000px but clientHeight is only 393px.
After long conversation, brain stream content is at offset ~4700px within the scrollable div.

### Working Solution
```python
# After orange CTA click, wait 10+ seconds for Welcome card to render
await asyncio.sleep(10)

# Find Welcome card and scroll to it
await page.evaluate("""() => {
    var msgs = document.getElementById('ptc-messages');
    var all = Array.from(msgs.querySelectorAll('*'));
    var welcomeCard = all.find(e =>
        e.textContent.includes('Welcome to the Family') && e.children.length > 2
    );
    if (welcomeCard) welcomeCard.scrollIntoView({behavior: 'instant', block: 'start'});
}""")
```

### Alternative: Scroll to absolute bottom
```python
await page.evaluate("""() => {
    var msgs = document.getElementById('ptc-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
}""")
```

---

## Sandbox-3 Flow Details

### Pre-Payment Speed Run
1. Password: `PureBrain.ai253443$$$`
2. Click "Awaken Your PURE BRAIN"
3. Click "Begin Awakening"
4. Type "pb-full-bypass" in name input (triggers bypass, skips pre-payment Q&A)
5. Click "Discover" / navigate to pricing section
6. Click "Activate Your AI Now" (Awakened tier)
7. Simulate payment: `window.onPaymentComplete('Awakened', orderId, {})`

### Post-Payment (5 Questions)
Sandbox-3 Q&A asks 5 questions (NO AI naming question unlike real flow):
1. Name
2. Email
3. Company
4. Role/title
5. Goal/what to build

### Slides
10 "Behind the Curtain" slides. Click "Show Me More" up to 10 times.
Then "That's incredible — let's go" to proceed.

### Orange CTA
"Your AI is ready — see your next steps" button at y=709-767.
Must use: `await page.click('button:has-text("ready")')`

### Brain Stream End State
After CTA click (wait 10-12 seconds): Welcome card with Brain Stream timeline appears in #ptc-messages.

---

## Verification Code Pattern

```python
# After orange CTA click + 10s wait:
welcome_check = await page.evaluate("""() => {
    var msgs = document.getElementById('ptc-messages');
    return {
        welcomeFound: msgs ? msgs.textContent.includes('Welcome to the Family') : false,
        brainStreamFound: msgs ? msgs.textContent.toLowerCase().includes('brain stream') : false,
        inputDisabled: document.getElementById('ptc-input') ? document.getElementById('ptc-input').disabled : null,
        sendOpacity: document.getElementById('ptc-send-btn') ? getComputedStyle(document.getElementById('ptc-send-btn')).opacity : null
    };
}""")
# Expected: welcomeFound=True, brainStreamFound=True, inputDisabled=True, sendOpacity='0.45'
```

---

## networkidle Timeout Fix

The page has continuous requests (animations, WebSocket connections).
`page.wait_for_load_state("networkidle")` ALWAYS times out.

Fix:
```python
try:
    await page.wait_for_load_state("networkidle", timeout=8000)
except:
    pass
```

---

## Reference Screenshots (Definitive)

- **Primary brain stream state**: `exports/e2e-sandbox3-payment-to-brain-stream/F01-v6-after-cta-click.png`
- **Input disabled closeup**: `exports/e2e-sandbox3-payment-to-brain-stream/F05-FINAL-learn-more-btn-closeup.png`
- **Prior working run**: `exports/e2e-sandbox3-post-fix-screenshots/23-13-FIX3-brain-stream-state.png`

---

## Confidence: High
All patterns validated across 6 test script iterations on 2026-03-04.
