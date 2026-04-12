# Memory: Post-Payment Conversation Logging Fix

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer

## Root Cause

The `logPayTestData()` function on pay-test pages (439, 468) was sending to BOTH:
- `https://api.purebrain.ai/api/log-pay-test` - SUCCEEDED (no message field required)
- `https://api.purebrain.ai/api/log-conversation` - FAILED 400 (requires `messages` or `conversationHistory`)

The payload sent to `/api/log-conversation` was the same form-data payload built for `/api/log-pay-test` - it had name, email, tier, orderId etc., but NO `messages` field. The server rejected every post-payment conversation log with:
`WARNING - Request rejected: missing messages/conversationHistory field`

## The Architecture (Important to Understand)

Two distinct chat phases exist:

**Phase 1 (Pre-payment "Discover"):**
- Chat runs via `logConversationToBackend()` function
- Sends to `/wp-json/purebrain/v1/log-conversation` (WP proxy)
- WP proxy forwards to `https://api.purebrain.ai/api/log-conversation`
- `state.conversationHistory` is the array of `{role, content}` objects
- THIS WAS WORKING FINE

**Phase 2 (Post-payment "Onboarding"):**
- Chat runs via `initPayTestFlow()` / `runQuestionnaire()` (in `pay-test-chat-flow.js` inlined code)
- Logs via `logPayTestData()` function
- `logPayTestData()` was calling `/api/log-conversation` BUT without `messages` field
- THIS WAS BROKEN - all calls returned 400

**The bridge between phases:**
- When PayPal payment completes, `window.onPaymentComplete()` fires
- It saves `window._pbPrePurchaseSession = { sessionId, conversationHistory, messageCount }`
- `initPayTestFlow()` reads this and stores in `payTestData.prePurchaseHistory`

## The Fix

Split `logPayTestData()` into two separate payloads:

```javascript
// Payload 1: for /api/log-pay-test (form data, no messages needed)
const payTestPayload = { event, tier, name, email, company, role, ... }

// Payload 2: for /api/log-conversation (AICIV - requires messages array)
const convPayload = {
  session_id: payTestData.prePurchaseSessionId || 'pb-post-' + orderId,
  messages: [...prePurchaseMsgs, ...onboardingQAMsgs],  // FULL conversation
  source: 'purebrain-post-payment',
  ...
}
```

The `messages` array is built by:
1. Taking `payTestData.prePurchaseHistory` (pre-payment chat) - or `window._pbPrePurchaseSession.conversationHistory` as fallback
2. Appending structured Q&A pairs from the onboarding (name, email, company, role, primaryGoal)

## Proof It Works

Before fix: every `POST /api/log-conversation` from post-payment flow returned 400
After fix: test call returned 200, server logged:
- "Logged conversation: session=pb-post-TEST-ORDER-001"
- "Forwarded to hub: pb-post-TEST-ORDER-001 -> operations"
- "A-C-Gee forward success: session=pb-post-TEST-ORDER-001 attempt=1"

JSONL entry includes full 12-message conversation (4 pre-purchase + 8 onboarding Q&A).

## Key Files

- `/home/jared/projects/AI-CIV/aether/tools/fix_post_payment_conversation_logging.py` - the fix script
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` - the log server (did NOT need changes)
- WordPress pages 439 + 468 - where the JS lives in `_elementor_data`

## Gotchas / Lessons

1. **String replacement in _elementor_data**: The JSON string inside _elementor_data uses literal `\n` (backslash-n) NOT actual newlines. When writing Python replacement strings, use raw strings `r"""..."""` with literal `\n` to match.

2. **Verify `OLD_LOG_FUNC` exactly**: The replacement string must match char-for-char. Test with `OLD_LOG_FUNC in elem_str` before running.

3. **The two endpoints need DIFFERENT payloads**: `/api/log-pay-test` handles profile/onboarding data; `/api/log-conversation` handles conversation messages for AICIV. Never send the same payload to both.

4. **Pre-purchase session linkage already existed**: A previous script (`fix_post_payment_logging_and_ui.py`) had already added `prePurchaseSessionId` and `prePurchaseHistory` to `payTestData`. The only missing piece was that `logPayTestData()` wasn't including `messages` in the payload sent to `/api/log-conversation`.

5. **The log server's `forward_to_hub()` does NOT send conversation content to hub** - it sends a summary (session_id, message count, first user message). The actual message content goes to A-C-Gee via `forward_to_acgee()`.
