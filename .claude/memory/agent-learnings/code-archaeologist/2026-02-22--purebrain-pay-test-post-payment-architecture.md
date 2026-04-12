# PureBrain Pay-Test Post-Payment Architecture

**Date**: 2026-02-22
**Type**: operational
**Agent**: code-archaeologist
**Confidence**: high

## Context

Extracted full source code of purebrain.ai/pay-test-sandbox-2/ post-payment chat experience from WordPress REST API (Page ID 468) for a major rebuild.

## Discovery

The entire page is a single Elementor Custom HTML widget (ID: 292c72a) containing 409,450 chars of a full standalone HTML page embedded inside Elementor. There are 3 critical JS scripts:

- Script 23: PayPal integration (32,515 chars) — `exports/pay-test-script-paypal.js`
- Script 24: Post-payment chat flow v2 (55,073 chars) — `exports/pay-test-script-chat-flow.js`
- Script 25: Integration glue (4,421 chars) — `exports/pay-test-script-integration-glue.js`

## Key Architecture Facts

1. **Entry point**: `window.initPayTestFlow(container, aiName, tier, orderId)` — called by integration glue 1500ms after payment confirmed

2. **5 phases**: Questionnaire → Behind the Curtain (10 slides) → Telegram Bot Setup → Claude API Key → Completion

3. **State object**: `window.payTestData` — global, 15 fields including name/email/company/role/primaryGoal/telegramBotToken/claudeSessionInfo

4. **Dual logging**: Every step logs to BOTH `https://api.purebrain.ai/api/log-pay-test` AND `https://api.purebrain.ai/api/log-conversation`

5. **AI name carryover**: Pre-purchase chat exports `window._pbState.aiName` which integration glue captures and passes into post-payment flow

6. **Thank-you page**: Page ID 309, URL `/thank-you/?name=X&ai=Y`, personalized via inline JS

7. **PayPal tiers**: Awakened $79, Bonded $149, Partnered $499, Unified $999 — subscription billing with Plan IDs P-xxx

## Full Analysis

See: `exports/pay-test-post-payment-code-analysis.md`

## When to Apply

- When rebuilding the post-payment onboarding experience
- When adding new phases to the flow
- When changing logging endpoints or payload format
- When modifying the Telegram or Claude API key collection steps
