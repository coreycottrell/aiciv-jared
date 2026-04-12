# Pay-Test Chatbox 7-Change Deployment — 2026-02-27

## Pages Affected
- **pay-test-2**: WordPress page ID 689
- **pay-test-sandbox-2**: WordPress page ID 688
- Both pages were identical; same fix applied to both.

## Changes Applied

### CHANGE 1+2: DISCOVER Button Loop Fix (Pre-Payment)
**Problem**: When `state.pricingRevealed = true` (Discover button visible), user typing in the text box caused `processResponse()` to call Claude, which responded with `[SHOW_PRICING]` again — creating an infinite loop. The button would be blocked from re-showing (due to `state.pricingRevealed` guard), but no progress was made.

**Fix**: Modified `handleSubmit()` to check `state.pricingRevealed` BEFORE calling `processResponse`. If true, calls `window.showPersonalizedCapabilities()` directly and returns.

```javascript
// In handleSubmit():
if (state.pricingRevealed) {
    userInput.value = '';
    userInput.blur();
    window.showPersonalizedCapabilities();
    return;
}
```

### CHANGE 2 (Post-Payment): promptButtons Textarea Fix
**Problem**: During `promptButtons()` phases (button-only input), if user typed Enter in the textarea, nothing happened.

**Fix**: Extended `promptButtons()` to optionally accept a `dom` parameter. When provided, attaches a keydown listener on the textarea that resolves with the primary button's value on Enter key.

### CHANGE 3: Telegram Text — "Their Brain Stream" → "Its Brain Stream"
In `runTelegramSetup()`, changed:
- `Their Brain Stream` → `Its Brain Stream`
- Also adjusted the sentence slightly for flow

### CHANGE 4: Telegram Connection Success Message
Old: `"Your Telegram bridge is live. ${aiName} will reach you there when your AI is ready."`
New: `"As a back up to your Brain Stream Portal, you will be able to reach ${aiName} on Telegram when ready."`

### CHANGE 5: "The next step" — ALREADY DONE
Was already `"The next step in ${safeAiName}'s set up"` in live code. No change needed.

### CHANGE 6: "One moment" removed / "Yay!" added — ALREADY DONE
Both were already implemented in v4.3.3. Only appeared in changelog comments.

### CHANGE 7: OAuth Button Bottom-Right Placement
Added `flex-end` alignment to the `actions` div when the OAuth button is rendered:
```javascript
actions.style.justifyContent = 'flex-end';
actions.style.flexDirection = 'column';
actions.style.alignItems = 'flex-end';
```
Resets after the "I have my key" button stage.

## Deployment Details
- Deployed: 2026-02-27
- Page 689 modified at: 2026-02-27T11:47:59
- Page 688 modified at: 2026-02-27T11:48:06
- File saved: `exports/pay-test-chatflow-v4-2026-02-27.html`

## Security Review
- No new user data written to innerHTML
- All user-visible text uses existing sanitized variables (`sanitizeText()`)
- `promptButtons` listener uses proper `removeEventListener` pattern
- DISCOVER bypass does not expose user input to any DOM write
- OAuth URL validation unchanged (already strict HTTPS + domain check)

## Patterns Learned
- Pre-payment chat: `handleSubmit` is the user input gateway — intercept there for flow control
- Post-payment chat: `promptButtons` does NOT listen to textarea — must patch if needed
- Pages 689 and 688 are kept in sync as identical content
- WP REST API updates work with `-u Aether:PUREBRAIN_WP_APP_PASSWORD` + `--data-binary @file` for large payloads (403 on Python urllib.request, curl works fine)
