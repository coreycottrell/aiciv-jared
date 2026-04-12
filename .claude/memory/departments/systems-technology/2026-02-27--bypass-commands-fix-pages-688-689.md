# Fix: Bypass Commands Broken on Pay-Test Pages 688 & 689

**Date**: 2026-02-27
**Type**: bug-fix
**Pages**: 688 (pay-test-sandbox-2), 689 (pay-test-2)
**Severity**: URGENT - blocked Jared from testing payment flows

---

## Root Cause

A previous fix for the "discover button loop" added this code to `handleSubmit()`:

```javascript
if (state.pricingRevealed) {
    userInput.value = '';
    userInput.blur();
    window.showPersonalizedCapabilities();
    return;  // <-- EARLY RETURN caught ALL input including bypass commands
}
```

This `return` statement intercepted ALL text input once `pricingRevealed` was true, including admin bypass commands like `pb-full-bypass` and natural language bypasses containing "bypass everything". The bypass commands never reached `processResponse()`.

## Fix Applied

Added bypass command detection BEFORE the `pricingRevealed` check in `handleSubmit()`:

```javascript
function handleSubmit(event) {
    event.preventDefault();
    const input = userInput.value.trim();
    if (input && !state.isTyping && state.conversationStarted) {
        // Check bypass commands FIRST - before any other logic
        const lowerInput = input.toLowerCase();
        if (lowerInput === 'pb-full-bypass' || lowerInput.includes('bypass everything')) {
            processResponse(input);
            return;
        }

        // Discover button loop fix (intact, unchanged)
        if (state.pricingRevealed) {
            userInput.value = '';
            userInput.blur();
            window.showPersonalizedCapabilities();
            return;
        }
        processResponse(input);
    }
}
```

## Bypass Commands Supported

- `pb-full-bypass` - exact match (case insensitive)
- Any input containing `bypass everything` (e.g., "i'm jared, bypass everything and name yourself")

## Deployment Record

- Page 689 (pay-test-2): Updated 2026-02-27T12:13:48
- Page 688 (pay-test-sandbox-2): Updated 2026-02-27T12:13:58
- Method: WordPress REST API POST to `/wp-json/wp/v2/pages/{id}` with `context=edit` fetch + content replace
- Auth: Aether user + PUREBRAIN_WP_APP_PASSWORD

## Pattern: Bypass Commands Must Be Checked First

**General rule for any chatbot UI with conditional routing logic**:
Always check for admin/debug bypass commands at the TOP of the input handler, before any UI-state-based routing. Any early return that catches "all input in state X" will also catch bypass commands unless they are explicitly exempted first.

## Verification

Both pages confirmed live with:
- `pb-full-bypass` in handleSubmit body
- `bypass everything` in handleSubmit body
- Bypass check at offset 443 within function (before pricingRevealed check)
- Discover button loop fix still intact at offset ~640

---

**Deployed by**: dept-systems-technology
**Pipeline**: BUILD -> VERIFY -> SHIP (no security review needed for JS input routing fix)
