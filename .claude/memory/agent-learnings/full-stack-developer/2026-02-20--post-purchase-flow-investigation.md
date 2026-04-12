# Post-Purchase Flow Investigation - purebrain.ai pay-test pages

**Date**: 2026-02-20
**Type**: operational
**Topic**: Complete mapping of post-payment data flow for welcome email automation

---

## What Was Investigated

Full end-to-end mapping of what data is available and where at each stage of the purebrain.ai pay-test purchase flow.

---

## Key Findings

### Data Available at flow:complete

The `payTestData` JS object collects all user data during the post-payment chat flow:

```javascript
{
  tier: "Awakened|Bonded|Partnered|Unified",
  aiName: "chosen by user in pre-purchase chat",  // e.g. "Keen", "Clarity"
  orderId: "PAYPAL-ORDER-ID",
  name: "User Full Name",          // collected in questionnaire
  email: "user@email.com",         // collected in questionnaire (validated)
  company: "Company name",         // optional
  role: "CEO / title",             // optional
  primaryGoal: "user's stated goal", // optional
  telegramBotToken: "bot token",   // if Telegram setup done
  claudeMaxStatus: "pending|existing|connected",
  timestamps: { flowComplete: ISO-timestamp, ... }
}
```

### Where aiName Comes From

- Set in pre-purchase chat via AI response parsing (`state.aiName`)
- AI generates name via Claude API, detects it via regex in response
- Passed to post-payment flow via `window._pbPrePurchaseSession.aiName`
- Stored in `payTestData.aiName` for the duration of the flow

### Server Logging

Two endpoints receive data on `flow:complete` event:
1. `POST https://api.purebrain.ai/api/log-pay-test` → writes to `logs/purebrain_pay_test.jsonl`
2. `POST https://api.purebrain.ai/api/log-conversation` → writes to `logs/purebrain_web_conversations.jsonl`

Server also sends Telegram notification on each log-pay-test call.

**Critical gap**: Server does NOT currently trigger Brevo or send welcome emails. That step is completely missing.

### Thank-You Page

- URL: `https://purebrain.ai/thank-you/`
- Content: Static HTML - "Welcome to the Family!", "Payment Confirmed"
- Has a CTA saying "Check your email for your receipt and onboarding details"
- Does NOT display personalized data (no name, no tier, no aiName)
- Does NOT receive URL parameters carrying user data
- Redirect happens via button click at flow:complete: `window.location.href = '/thank-you/'`

### Redirect Flow

1. Payment captured → `window.onPaymentComplete(tier, orderId, payerInfo)` fires
2. Post-payment chat flow launches (fullscreen overlay)
3. Questionnaire: name, email, company, role, primaryGoal collected
4. Behind-the-curtain phase + Telegram setup + Claude Max setup
5. `flow:complete` event fires → `logPayTestData()` sends to server
6. Welcome button appears: "[aiName] is ready — see your next steps →"
7. User clicks → `window.location.href = '/thank-you/'`
8. Thank-you page is static, no URL params, no personalization

### Brevo Current State

**Only integration that exists**: Enterprise tier leads → List 4 (Enterprise Leads). Non-enterprise paid users are NOT added to Brevo at all.

**Templates existing**:
- IDs 1-7: "Neural Feed" welcome sequence (7 emails over 21 days) → List 3 (blog subscribers)
- ID 8: Brevo default "Automation Template - Welcome mail" (placeholder, not PureBrain branded)
- IDs 9, 10: Duplicate copies of Neural Feed Email 7 (likely test artifacts)

**No post-purchase welcome templates exist yet.** Templates 1-7 are for pre-purchase blog newsletter nurture sequence.

### Payment Logs - Actual Real Data

From `purebrain_payments.jsonl`: PayPal captures have `payerEmail: ""` and `payerName: ""` - these fields are empty even for real subscriptions (I-JW7705PBAV32 etc). PayPal subscription API does NOT return payer PII in the verify-payment response.

From `purebrain_pay_test.jsonl`: The post-payment chat flow DOES capture real data:
- `name`, `email`, `company`, `role`, `primaryGoal` all present
- Real test with Philip Bliss: email=philip@puretechnology.ai, company, role, primaryGoal all collected
- `flowCompleted: false` on all entries (no `flow:complete` event has fired successfully yet)

---

## Critical Gaps Identified

1. **flowCompleted is always false** - The `flow:complete` event doesn't seem to be firing / reaching the server with flowCompleted=true. Need to investigate why.

2. **No Brevo integration for paid users** - Server receives complete data but does nothing with it for email triggering.

3. **Thank-you page is static** - Cannot display personalized content without URL params or session.

4. **No post-purchase email templates** - Need to create dedicated templates (not the nurture sequence).

---

## Recommended Architecture for Welcome Emails

### Option 1: Server-side trigger at log-pay-test (BEST)
When `event == 'flow:complete'` is received at `/api/log-pay-test`:
1. Add contact to Brevo with FIRSTNAME, LASTNAME, COMPANY, ROLE, AI_NAME, TIER attributes
2. Add to appropriate list (e.g. List 5: "Customers")
3. Brevo automation triggers on list add → sends welcome email

**Pros**: Reliable server-side, one place to add logic
**Cons**: Need new Brevo list + automation + email template

### Option 2: Client-side Brevo call in pay-test JS (SIMPLER)
At flow:complete in the JS, add a `fetch` to `https://api.brevo.com/v3/contacts` with full payTestData.
Already done for Enterprise leads - same pattern for non-Enterprise.

**Pros**: No server changes needed, consistent with Enterprise approach
**Cons**: Client-side API key exposure (already an issue with Enterprise code)

### Option 3: Use /thank-you/ page with URL params
Redirect to `/thank-you/?email=X&name=Y&ai=Z&tier=T` and have the thank-you page trigger Brevo.

**Cons**: Exposes user data in URL, complex

### Recommendation: Option 1 (server-side) for security, but Option 2 is fastest to ship

---

## Brevo Contact Attributes to Set

For paid users, these custom attributes should be set:
- `FIRSTNAME` / `LASTNAME`: from payTestData.name
- `AI_NAME`: payTestData.aiName (personalize emails with AI's chosen name)
- `TIER`: payTestData.tier
- `COMPANY`: payTestData.company
- `ROLE`: payTestData.role
- `PRIMARY_GOAL`: payTestData.primaryGoal

---

## File Paths Referenced

- Pay-test page: WordPress page ID 439 (pay-test) and 468 (pay-test-sandbox)
- Server: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` (line 545: log_pay_test route)
- Pay logs: `logs/purebrain_pay_test.jsonl`, `logs/purebrain_payments.jsonl`
- Template IDs file: `to-jared/brevo-template-ids.json`
- Thank-you page: WordPress page ID 309
