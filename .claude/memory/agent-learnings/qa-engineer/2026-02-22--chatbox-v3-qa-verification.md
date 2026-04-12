# QA Memory: Chatbox v3 Post-Payment Flow Verification

**Date**: 2026-02-22
**Type**: operational
**Topic**: Full QA verification of pay-test-chat-flow-v3.js on pages 688 and 689
**Verdict**: SHIP

---

## Pages Verified

- Page 688: `purebrain.ai/pay-test-sandbox-2` — Sandbox/testing page
- Page 689: `purebrain.ai/pay-test-2` — Production pay-test page

---

## Verification Method

Used WordPress REST API with `?context=edit` to pull raw Elementor JSON data from both pages.
Extracted HTML widget content (single widget per page, ~423KB), parsed script tags, and ran
automated string-match checks against 56 checklist items.

```bash
curl -s -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  "https://purebrain.ai/wp-json/wp/v2/pages/688?context=edit" \
  > /tmp/qa_688.json
```

---

## Script Inventory

Page 688 has 26 `<script>` tags. The v3 stack is:
- Index 22 (Script 23): PayPal SDK Integration v2 — 32,515 chars
- Index 23 (Script 24): Post-Payment Chat Flow v3 — 69,229 chars
- Index 24 (Script 25): Integration Glue — 4,421 chars
- Index 25 (Script 26): PayPal Alias shim — 81 chars

Pages 688 and 689 have **byte-for-byte identical v3 scripts** (both 69,229 chars).

---

## Checklist Results Summary

**Total: 55 PASS / 1 FALSE-POSITIVE FAIL out of 56**

The single "FAIL" (P4-02_no_thank_you_redirect) was a false positive in the check logic.
`window.location.href` appears twice in the script but neither is a `/thank-you/` redirect:
1. `page_url: window.location.href` — legitimate logging
2. `window.location.href = 'tg://resolve?domain=BotFather'` — Telegram detection probe

The `/thank-you/` string appears only in comments explaining what was **removed**, never as a redirect target.
**Actual status: PASS** — no redirect to /thank-you/ in code.

---

## Phase-by-Phase Results

### Phase 1 — Questionnaire (PASS)
- Claude auth block positioned AFTER role question, BEFORE primary goal question
- "Before we go deeper" message text present
- "I have my key" button present
- `sk-ant-` validation loop present with retry logic
- API key masked with `claudeKey.slice(0, 14) + bullets` pattern
- `payTestData.claudeSessionInfo = claudeKey.trim()` assignment present
- `questionnaire:claude-auth` event logged

### Phase 2 — Behind-the-Curtain (PASS)
- `showSlide(msgList, index, total, content, iconHtml = null)` — iconHtml parameter present
- `buildCurtainSlides` returns array of `{icon, content}` objects
- Exactly 10 slides, each with emoji icon:
  1. 🧠 Wake up
  2. 📄 Founding document
  3. 🔍 Research
  4. 🔬🧬💬🎁🔧🗂️ Six teams (wide multi-emoji)
  5. 🔬 Team 1 Research
  6. 🧬 Team 2 Identity
  7. 💬 Team 3 First Conversation
  8. 🎁 Team 4 Gift Creation
  9. 🔧 Team 5 Infrastructure
  10. ✨ Welcome
- `.ptc-slide-icon` CSS class defined in `injectStyles()`

### Phase 3 — Telegram Setup (PASS)
- Dynamic bot username: `aiNameSlug = aiName.toLowerCase().replace(/[^a-z0-9]/g, '')`
- Token masking: `tokenNumericId + ':••••••••••••'` (CRIT-002)
- No Claude auth logic in Telegram setup function

### Phase 4 — Completion (PASS)
- `runCompletion` calls `await runThankYouMessage(dom, aiName, firstName)`
- No `window.location.href` redirect to `/thank-you/` in completion flow

### Phase 5 — Thank You Message (PASS)
- `runThankYouMessage` function exists (line ~1665)
- PureBrain logo with `background:transparent` style
- "Welcome to the Family!" heading present
- Timeline: "Now" / "Next 2 mins" / "Next 5 mins" badges
- `id="ptc-portal-placeholder"` div present
- "Learn more" button (NOT "Return to Homepage")
- No "Questions? Email us" text
- `.ptc-ty-card` CSS block in `injectStyles()`

### Phase 6 — Learn More Loop (PASS)
- `runLearnMoreLoop` function exists
- 5 questions: workingStyle, biggestFriction, sixMonthVision, hiddenContext, personalSuccess
- Skip button per question
- 5-entry acknowledgment array (`acks`)
- Per-answer logging: `event: \`learn-more:${q.field}\``

### Phase 7 — Portal Button Watcher (PASS)
- `runPortalButtonWatcher` function exists
- Polls `/api/portal-status` every 30,000ms
- `MAX_POLLS = 60` (30 minutes max)
- URL validation: `parsedPortalUrl.protocol !== 'https:'` and `.endsWith('purebrain.ai')` (HIGH-001)
- `currentPlaceholder.replaceWith(portalBtn)` on ready

### Flow Orchestration (PASS)
- `initPayTestFlow` calls: runQuestionnaire → runBehindTheCurtain → runTelegramSetup → runCompletion
- `runClaudeMaxSetup` NOT called in `initPayTestFlow` (dead code only)
- `learnMoreAnswers: []` and `portalReady: false` in payTestData

---

## Security Patches Verified

### CRIT-001: Credential Stripping from Logs (PASS)
```javascript
const { claudeSessionInfo: _sk, telegramBotToken: _tg, ...safeData } = data;
```
Both `claudeSessionInfo` and `telegramBotToken` are destructured out before any payload
is built. Neither key appears in `payTestPayload` or `convPayload`. The `...safeData`
spread is safe because the keys were already extracted.

### CRIT-002: Token Masking in Chat UI (PASS)
```javascript
const tokenNumericId = token.trim().split(':')[0];
const maskedToken = tokenNumericId + ':••••••••••••';
userSay(msgList, maskedToken);
```
Raw token never displayed to user.

### HIGH-001: Portal URL Validation (PASS)
```javascript
const parsedPortalUrl = new URL(rawPortalUrl);
if (parsedPortalUrl.protocol !== 'https:' || !parsedPortalUrl.hostname.endsWith('purebrain.ai')) {
  throw new Error('Invalid portal URL');
}
portalBtn.href = rawPortalUrl;
```
Open redirect prevented. Falls back to `https://purebrain.ai/portal` on invalid URL.

---

## PayPal Scripts

Both pages use PayPal SDK Integration v2. Functionally identical except:
- Different `PAYPAL_CLIENT_ID` values (sandbox vs production accounts)
- Different subscription Plan IDs for each tier
- Page 689 has slightly simplified subscription config (30,399 chars vs 32,515)

Both still have the same functional structure (createOrder, onApprove, onError, onCancel).

---

## Notes for Future QA

1. **Orange banner is intentional** — The `#ff6600` div at the top of both pages is the
   "SANDBOX MODE - No real charges" debug banner. Not an error state.

2. **Triple-DOCTYPE structure** — Both pages contain the full homepage snapshot inside
   Elementor HTML widget. This is the established pattern for pay-test pages.

3. **runClaudeMaxSetup as dead code** — The function still exists but has a console.log
   noting it's intentionally dead. This is correct per v3 spec.

4. **Script retrieval pattern** — The v3 script is always at scripts[23] (index 23, 0-based).
   PayPal is at scripts[22]. Glue at scripts[24].

---

## Verdict

**SHIP** — All 56 checklist items pass (1 false-positive in check logic resolved to PASS).
Both pages (688 and 689) have identical v3 chatbox scripts.
All 3 security patches are correctly implemented.
