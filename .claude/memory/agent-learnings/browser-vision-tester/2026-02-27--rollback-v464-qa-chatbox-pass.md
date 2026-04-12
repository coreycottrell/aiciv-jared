# Memory: Pay-Test-2 Chatbox QA Pass - Post-Rollback to v4.6.4

**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: Chatbox flow fully verified after plugin rollback; all removed scripts confirmed absent

---

## Summary

Full QA pass on pay-test-2 chatbox after plugin rollback to v4.6.4. All 4 removed scripts confirmed gone from both source and DOM. AI conversation flow working with 10 messages delivered.

---

## Key Findings

### 1. Chatbox Works Correctly Post-Rollback
- Begin Awakening button visible and clickable
- AI delivers full opening sequence (10 messages)
- "Hello" message submitted and received by AI
- Zero console errors
- Standard chatbox flow (`startConversation`) is the only flow

### 2. Removed Scripts All Absent
Confirmed NOT present in source OR DOM:
- `pb-bypass-override` - gone
- `pb-sandbox-override` - gone
- `pb-paypal-routing-fix` - gone
- `pb-session-timer-fix` - gone

### 3. Input Disabled/Enabled Playwright Gotcha (TEACHING MOMENT)
The chatbox JS uses `userInput.disabled = true/false` via `showTyping()`/`hideTyping()` functions.
- `is_enabled()` returns False while AI is generating (expected - input disabled during typing)
- But the input IS functionally usable - `fill()` works, submission works, responses come
- `wait_for_function("!el.disabled")` fires correctly but then `is_enabled()` still shows False
  because the AI immediately starts typing the NEXT message (disabled again)
- **Do not use `is_enabled()` as a functional check for this page's chatbox**
- **Instead use**: count of AI messages > 0, OR successful message submission

### 4. WAF-Safe Strategy (Confirmed Working Again)
- WP REST API with Basic auth (Aether + app password)
- Page ID 689, context=edit to get raw content
- Strip `<!-- wp:html -->` markers
- Serve locally via Python HTTP server on random port
- Playwright against localhost - no WAF, no password form submission

---

## Test Configuration

- Page ID: 689 (pay-test-2 production)
- Test method: WP REST API -> local serve -> Playwright
- Browser: Chromium headless, 1440x900
- Script: `tools/rollback_qa_chatbox_v2.py`
- Screenshot: `docs/rollback-qa/chatbox-flow.png`
- Report: `docs/rollback-qa/QA-REPORT.md`

---

## Selectors (Still Valid 2026-02-27)
- Begin button: `.chat-initial__btn`
- Chat input: `#userInput`
- Submit button: `#submitBtn`
- AI messages: `.message--ai`
- Chat section: `.chat-section`

**Tags**: purebrain, pay-test-2, rollback, v464, chatbox, playwright, waf-safe, local-serve, pass, removed-scripts
