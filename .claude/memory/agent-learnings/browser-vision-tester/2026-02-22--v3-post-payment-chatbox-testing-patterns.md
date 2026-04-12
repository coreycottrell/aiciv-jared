# Memory: V3 Post-Payment Chatbox Testing Patterns

**Date**: 2026-02-22
**Type**: teaching + operational
**Topic**: Testing purebrain.ai pay-test-sandbox-2 post-payment chatbox v3 flow

---

## Key Discoveries

### 1. Correct Password
- sandbox-2 page password: `PureBrain.ai253443$$$` (3 dollar signs)
- Memory previously had `$$$` for other pages - confirmed same here
- Task description said `$$` (2 dollar signs) - was incorrect

### 2. Flow to Trigger Post-Payment Chat
The post-payment chatbox does NOT appear automatically. You must navigate:
1. Fill password -> page loads
2. Click `.chat-initial__btn` ("Begin Awakening")
3. Type `pb-full-bypass` in `#userInput` -> Bypass mode, Keen appears, "DISCOVER WHAT KEEN CAN DO" button
4. Click `#proCta` ("Activate Now") -> PayPal overlay opens
5. Click `#pb-sandbox-bypass-btn` ("Simulate Successful Payment (Test Only)") -> post-payment chat appears

NOTE: The sandbox bypass button ONLY exists on sandbox URLs. It's created dynamically with JS when `window.location.pathname.indexOf('sandbox') !== -1`.

### 3. Post-Payment Chat Selectors
- Container: `#pay-test-post-payment` (class: `ptc-wrapper`)
- AI messages: `.ptc-msg.ptc-msg--ai`
- User messages: `.ptc-msg.ptc-msg--user` (shown as orange bubbles on right)
- Textarea: `textarea[placeholder*="Message Your"]`
- Submit button: `button.ptc-send-btn` (text "Send")
- Chat messages container: `.ptc-messages`

### 4. Questionnaire Flow (v3)
Order: Name -> Email -> Company -> Role -> **Claude Auth** -> Primary Goal
- After Role, "Before we go deeper" Claude API key message appears
- "I have my key →" button appears (class `ptc-btn ptc-btn--primary`)
- User enters API key in textarea
- Key is MASKED: shown as `sk-ant-api03-t••••••••••••` (dots confirmed)
- Then Primary Goal question follows
- Then "Behind the Curtain" 10 slides

### 5. Behind the Curtain Slides
- 10 slides labeled "BEHIND THE CURTAIN · X OF 10"
- Each slide has an emoji icon
- Navigation: "Show Me More →" button (class: `ptc-btn ptc-btn--primary`)
- After slide 10: "That's incredible — let's go →" button
- Transition message: "That's the machine — 22 Brains, six teams, all focused on one person: you."

### 6. Telegram Flow
Trigger word: "Telegram" appears in the AI message after slides
The question "Do you already have it installed on your phone or computer?" has 3 buttons:
- "Yes, I have Telegram"
- "Not sure"
- "No — I need it"

Then walks through: BotFather setup → create bot → get token → paste token → username

Note: Test was at Telegram phase when test ended. Phases 5-6 (Thank You Card, Learn More) not reached in this test run because test was following the wrong sequence after bot token.

### 7. Token Masking CONFIRMED
- Bot token entered: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- The test confirmed `token_plain_visible=False` and `has_dots=True`
- Token is properly masked in the chat display

### 8. WAF Rate Limit Pattern
- GoDaddy WAF shows "Please verify you are human" CAPTCHA after too many requests in short time
- 4 minute wait clears it
- ALWAYS wait 4+ minutes between browser test runs when hitting purebrain.ai

### 9. headless Playwright + fixed overlay
- `#pay-test-post-payment` has `position: fixed` and `display: flex` but `offsetParent === null`
- This is expected in headless - fixed position elements don't have offsetParent
- Screenshots still capture them correctly
- Use `document.querySelectorAll('.ptc-msg--ai').length` to count messages (not offsetParent visibility)

### 10. Phase 5 (Thank You Card) + Phase 6 (Learn More) Status
- NOT tested in this run - the test ended at Telegram phase
- Future test needs to: complete Telegram setup → completion message → "[AI NAME] is ready" button → thank you card
- Thank You card expected checks:
  - "Welcome to the Family!" heading
  - Timeline: "Now" / "Next 2 mins" / "Next 5 mins"
  - PureBrain logo
  - "Learn more →" button
  - NO "Return to Homepage" text
  - NO "Questions? Email us" text
  - Portal placeholder

---

## Visual Test Results (Confirmed Passing)

1. **Chat with Your AI** header visible with PureBrain logo
2. **"Online · Ready to assist"** status indicator (green dot)
3. **All questionnaire AI responses** received correctly
4. **Claude auth "Before we go deeper"** appears AFTER role question
5. **"I have my key →" button** visible and clickable
6. **API key masking** confirmed: `sk-ant-api03-t••••••••••••`
7. **10 slides** with emoji icons all navigable
8. **Slide icons visible**: brain, document, magnifier, people, identity, conversation, gift, infrastructure, sparkle
9. **Telegram setup** begins correctly with 3 choice buttons

---

## Test Script Locations
- Main test: `/home/jared/projects/AI-CIV/aether/tools/test_v3_complete.py`
- Exploration scripts: `tools/explore_sandbox.py`, `tools/explore_sandbox2.py`, `tools/explore_sandbox3.py`
- Results JSON: `exports/v3_test_results.json`
- Screenshots: `exports/screenshots/v3_test_*.png` (41 captured)

---

**Tags**: purebrain, pay-test, post-payment, v3, chatbox, playwright, sandbox, questionnaire, claude-auth, telegram, slides
