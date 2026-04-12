# AI Training Hacks Button - Full Audit

**Date**: 2026-03-13
**Agent**: browser-vision-tester
**Type**: technique + gotcha

## Context

Tested the "AI Training Hacks" button (lightning bolt icon) in the portal left sidebar at http://localhost:8097. This button triggers a background scan of Brainiac training content and sends it to Aether as a chat message.

## Test Approach

**Critical gotcha**: The portal uses WebSocket connections that Playwright's `domcontentloaded` waits for indefinitely. This causes:
1. Playwright to hang at 30s timeout
2. Portal to crash from memory exhaustion (hit 1.5GB MemoryMax)

**Solution**: Block WebSocket routes via `page.route('**/ws/**', route.abort())`, then navigate. This allows domcontentloaded to fire while preventing portal overload.

**Auth**: Must use `?token=TOKEN` in URL. Without it, `#loginOverlay` intercepts all pointer events. The overlay hides automatically when urlToken is detected (no API call needed).

**Click method**: Use `page.evaluate('() => document.getElementById("training-hacks-btn").click()')` instead of `btn.click()` - avoids Playwright's visibility/intercept checks.

## Test Results

### PASS: Button visible in sidebar
- Located at `#training-hacks-btn` with class `nav-item training-hacks`
- Label shows "AI Training Hacks" with lightning bolt icon

### PASS: Scanning state activates on click
- `.scanning` class added immediately to button
- `.th-label` text changes to "Scanning..."
- `window._trainingHacksScanning = true`
- Spinner appears in button

### PASS: Chat input populated with training prompt
- `chat-input` value set to `[BACKGROUND TASK] AI Training Ingestion\n\nPlease scan the Brainiac Mastermind Training page...`
- Confirmed in DOM evaluation at 100ms post-click

### PASS: Auto-send fires after 100ms
- `send-btn.click()` called via setTimeout(100)
- (WebSocket blocked so no actual send, but the mechanism is correct)

### BUG: Toast "Training scan initiated..." does NOT appear
- `window.showToast` is undefined (type: `undefined`)
- `showToast` is defined inside the IIFE as a local function only
- The `fireTrainingHacks()` function (in separate `<script>` block) checks `if (typeof window.showToast === 'function')` - this check fails
- **Fix needed**: Expose `showToast` to window scope inside the IIFE: `window.showToast = showToast;`

## Screenshots

- Before: `/tmp/portal_b4.png` - Portal in normal state, "AI Training Hacks" visible in sidebar
- After: `/tmp/portal_after.png` - Button shows "Scanning..." with spinner, chat panel switching

## Playwright Pattern for Portal Testing

```python
from playwright.sync_api import sync_playwright
import time

TOKEN = 'YOUR_TOKEN'
PORTAL_URL = f'http://localhost:8097/?token={TOKEN}'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})

    # Block WebSockets to prevent portal overload
    page.route('**/ws/**', lambda route: route.abort())

    try:
        page.goto(PORTAL_URL, wait_until='domcontentloaded', timeout=30000)
    except Exception:
        pass  # SSE might cause timeout, that's ok

    time.sleep(4)  # Let JS init run

    # Use JS click to bypass Playwright's pointer-event checks
    page.evaluate('() => document.getElementById("some-btn").click()')
```

## Key Findings

1. Portal is a 572KB single-page app (12K lines HTML)
2. Playwright load hangs due to WebSocket connections - ALWAYS block with `page.route`
3. Auth via `?token=` URL param - no cookie/localStorage needed
4. Toast system has a scope bug (window.showToast not exposed) - minor UX issue
5. All other training hacks mechanics work correctly
