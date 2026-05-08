# Seed Cross-Contamination via S5-payerName Fallback

**Date**: 2026-05-07
**Type**: gotcha
**Severity**: HIGH (token leak — Customer A receives Customer B's portal magic link)
**File**: `tools/purebrain_log_server.py` lines 1029-1062

## What Happened

Sheila (real customer email `sheila@couplify.com`, paid 2026-05-07 11:54 UTC, $499 Partnered tier, order `I-RBXHJ68JCJPL`) was emailed Jay Hutton's magic link: `https://torque-jay.app.purebrain.ai/?token=7T_DXpgsffaQz-YCmnwD7QI4AJmexuLU1qFFxU9MhKg`.

Container subdomain `torque-jay` belongs to Jay Hutton (named in March 2026). Sheila now has credentials to his portal.

## Root Cause

The `/api/verify-payment` -> seed dispatch code in `purebrain_log_server.py` runs 5 lookup strategies to find the chat session that should be paired with the payment:

- **S1** orderId match
- **S2** session_uuid match
- **S3** payer email substring in chat content
- **S4** recent payment-page chat <30min
- **S5** payer first name appearing in assistant messages (>=3 chars, >=3 msgs)

Sheila never ran the naming ceremony chat (likely buyer Jay Whitehurst onboarded her externally). S1-S4 all returned 0. S5 fell back on **first name** of the **PayPal payer** (Jay Whitehurst), found 26 messages where assistants said "jay" to Jay Hutton, and bound Sheila's payment to Jay Hutton's "Torque" container.

The AI-name-must-populate rule from `feedback_seed_flow_never_deviate.md` was satisfied numerically (AI name = Torque) but semantically violated — Torque belongs to a different human.

## The Fix Class (CTO gate required)

1. **Disable S5 entirely**, OR gate it behind email-domain match (require payer email to ALSO appear in conv content, not just first name).
2. **Hard guard**: if `payer_email` has zero chat history AND `session_uuid` is empty, BLOCK the seed and Telegram-alert. Do not fuzzy-fall-back to a first-name match.
3. First-name matching is structurally unsafe — common names ("Jay", "John", "Mark", "Sara") guarantee future cross-contamination.

## Investigation Path That Worked

1. `grep -i "sheila\|keeper" logs/*.log` -> `agentmail_monitor.log` and `purebrain_log_server.log`
2. The log line containing `[payment-seed] Lookup results` is the smoking gun — it logs all 5 strategy hit counts AND the winner.
3. `grep -ic "hutton" logs/purebrain_web_conversations.jsonl` confirmed Jay Hutton has 13 chat records; `grep -ic "couplify" ...` confirmed Sheila has 0.

## Files Referenced

- `tools/purebrain_log_server.py:1029-1062` (S5 logic)
- `logs/purebrain_log_server.log` (live trace)
- `logs/agentmail_monitor.log` (magic link rewrite + welcome email)
- `logs/purebrain_web_conversations.jsonl` (chat history corpus)

## Pattern

**Whenever a payment is verified, the seed pipeline MUST verify the chat-session link via a strong identifier (UUID or email), never a fuzzy demographic (first name).** Treat S5 as a last-resort that should alert-not-fire.
