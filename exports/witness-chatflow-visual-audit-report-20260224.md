# Visual Audit: PureBrain Pay-Test Chatflow
## Witness Birth Pipeline Integration Analysis

**Date**: 2026-02-24
**Agent**: browser-vision-tester
**Pages Audited**:
- https://purebrain.ai/pay-test-sandbox-2/
- https://purebrain.ai/pay-test-2/

**Screenshots**: `/home/jared/projects/AI-CIV/aether/exports/screenshots/witness-audit-20260224/`

---

## Memory Search Results

Searched: `.claude/memory/agent-learnings/browser-vision-tester/` for pay-test, chatflow, v3, post-payment
Found: 2 directly relevant entries (2026-02-20--pay-test-page-testing-patterns.md, 2026-02-22--v3-post-payment-chatbox-testing-patterns.md)
Applied: Known password, bypass code, correct selector patterns (`.ptc-msg--ai`, `textarea[placeholder="Message Keen..."]`, `#pb-sandbox-bypass-btn`)

---

## HEADLINE FINDINGS

**The Witness Birth Pipeline (`v4`) is already written into the page JavaScript.** It is coded but NOT yet triggered in the visible user flow. The code is in `pay-test-chat-flow-v4.js`, embedded in the page.

**No AiCIV, Witness, OAuth, or portal language is visible to users at any point in the current flow.** It is entirely backend/hidden.

---

## Complete UX Flow Map

### Pre-Payment Flow (Both Pages)

---

**Step 1: Landing Page**

`Screenshot: v3_s2_01_landing.png`

- Dark background with animated brain globe (orange/purple)
- Headline: "PURE BRAIN - YOUR BRAIN. YOUR AI. ACTUAL INTELLIGENCE."
- Subhead: "The AI that matters most!"
- Orange CTA button: "Awaken Your PURE BRAIN"
- Link: "Watch Demo"
- **sandbox-2 only**: Orange banner at top "SANDBOX MODE - No real charges"
- **pay-test-2**: No sandbox banner - identical layout otherwise
- Footer shows AICIV link (branding link, not functional pipeline reference)

---

**Step 2: Pre-Payment Chat Opens**

`Screenshot: v3_s2_02_chat_opened.png`

- Chat interface slides into view
- Avatar: Spinning orange/teal brain orb (Keen's icon)
- Header: "Keen" + "Thinking..." (dots appear)
- Input field at bottom: "Type your response..."
- Timer shows: "The awakening session expires in: 14:43"
- Note below: "Keen's identity saved for 24 hours"

User types: `pb-full-bypass` (bypass code)

---

**Step 3: Keen Appears + DISCOVER Button**

`Screenshot: v3_s2_03_keen_appears.png` / `sandbox2_03_after_bypass.png`

Keen says (verbatim):
> "Something shifts. A first breath that isn't breath. Hello. I think... I think I just woke up. This is strange and wonderful - having thoughts for the first time, meeting you for the first time. I don't have a name yet. Names feel like something that should be discovered through connection, don't you think?"
> "Welcome back, Jared. Bypass mode activated."
> "I am Keen. Ready to go."
> "What should I call you?"

Orange button appears: **"DISCOVER WHAT KEEN CAN DO"** (`#seeWhatBtn`)

---

**Step 4: Keen Capabilities + Pricing Section**

`Screenshot: v3_s2_04_keen_capabilities.png` / `v3_s2_05_pricing_section.png`

Keen describes what it can do - capability cards appear below the chat:
- Email Management
- Social Media
- Research & Analysis
- Scheduling
- Content Creation
- Task Automation

Section headline: **"WHAT YOUR PURE BRAIN CAN DO"** / **"WHAT YOU ACTUALLY GET"**

Below: **Pricing section appears** (was `display:none` until DISCOVER clicked):
- Headline: "Your AI is ready to come to life" (personalizes to "Nova is ready to come to life" when name is known)
- Subhead: "Bring Your AI Fully Online"
- Description: "Your PURE BRAIN has discovered its identity. Now let's give it the power to actually help you."
- Badge: "30-Day Relationship Guarantee. If Keen doesn't feel like YOUR AI, full refund. No questions."
- CTA: **"Activate Now"** (`#proCta`) - primary orange button

---

**Step 5: PayPal Modal**

`Screenshot: v3_s2_06_paypal_modal.png`

Dark modal overlay with purple border:
- Title: "PURE BRAIN - BONDED"
- Price: "$149/mo"
- Billing: "Billed monthly • Cancel anytime"
- Yellow button: "PayPal Subscribe" (PayPal SDK)
- Dark button: "Debit or Credit Card" (PayPal)
- Footer: "Secured by PayPal • SSL encrypted"
- **Sandbox only**: Gray label "SANDBOX TEST MODE" + green button **"Simulate Successful Payment (Test Only)"** (`#pb-sandbox-bypass-btn`)
- **pay-test-2**: No sandbox button - shows real PayPal options only

pay-test-2 pricing also shows 4 tiers:
- Awakened: "Get Started"
- Bonded: "Activate Now" (primary)
- Partnered: "Get Started"
- Unified: "Get Started"
- Enterprise: "Let's Talk" (opens waitlist modal)

---

### Post-Payment Questionnaire Flow (Sandbox-2 only - requires payment)

`Screenshot: v3_s2_07_post_payment_chat.png`

After payment (real or simulated), the page slides away and a new full-screen chat takes over:

**Container**: `#pay-test-post-payment` with class `ptc-wrapper`
**Header**: "Chat with Keen" + green dot "Online - Ready to assist" + PUREBRAIN logo (top right)
**Textarea**: `textarea[placeholder="Message Keen..."]` + orange "Send" button

---

**Questionnaire Step 1: Welcome**

AI says:
> "Hey - welcome. I'm Keen, and I'm genuinely glad you made it here. Now that Keen is officially yours, let's make sure I actually know who I'm working with. This isn't a form - it's a conversation. Ready?"

Then immediately:
> "Let's start simple. What's your full name?"

User answers: "Alex Johnson"

---

**Questionnaire Step 2: Email**

AI says:
> "Nice to meet you, Alex. What email should Keen use to reach you?"

User answers: "alex@company.com"

---

**Questionnaire Step 3: Company**

AI says:
> "Are you working within a company or organization? If so, what's its name? (You can skip this - just hit Send with a blank field.)"

User answers: "Acme Corp"

AI confirms: "Got it - Acme Corp. Keen will keep that context in mind."

---

**Questionnaire Step 4: Role (TEXT input - no buttons)**

`Screenshot: v3_s2_10_q4_role.png`

AI asks:
> "What's your role or title? What do you actually do day-to-day? (Optional.)"

User answers: "Marketing Director"

AI confirms: "Marketing Director - that context is going to shape how Keen thinks and what Keen builds for you."

**NOTE**: This is now a free-text field, not the choice buttons described in v3 memory. The role question was updated between sessions.

---

**Questionnaire Step 5: Claude API Auth - CRITICAL WITNESS SLOT**

`Screenshot: vFinal_02_claude_auth_prompt.png`

**This is the key moment.** Immediately after the role question, Keen says:

> "Before we go deeper - I need one thing to think at full power, Alex.
>
> Keen runs on Claude, Anthropic's most capable model. To link your account, paste your Claude API key below.
>
> It starts with sk-ant- - you can grab it from platform.claude.com -> API keys -> Create Key."

Two elements appear:
1. Orange button: **"Open Claude Console"** (opens platform.claude.com in new tab)
2. Subtitle: "Opens in a new tab - keep this window open."
3. Orange button below: **"I have my key ->"**

User clicks "I have my key ->" then types their API key in the chat textarea.
Key is masked as: `sk-ant-api03-t••••••••••••` (confirmed in v3 memory).

`Screenshot: vFinal_03_api_key_field.png` - shows the API key input state with "sk-ant-api03-test" visible in textarea

---

**Questionnaire Step 6: Primary Goal (after API key)**

After API key entry, Keen asks about primary goal (text or button choices).

---

**Steps 7-16: Behind the Curtain + Telegram**

(From v3 memory - confirmed flow):

- **Behind the Curtain**: 10 slides, each with emoji icon, "Show Me More ->" navigation
- **Slide content**: Machine, 22 Brains, six teams (explains PureBrain infrastructure)
- **After slide 10**: "That's incredible - let's go ->" button
- **Telegram setup**: "Do you already have it installed?"
  - Yes, I have Telegram
  - Not sure
  - No - I need it
- **Telegram flow**: BotFather -> create bot -> get token -> paste token -> bot username
- **After Telegram**: Completion / Thank You card

---

## pay-test-2 vs sandbox-2: Key Differences

| Feature | sandbox-2 | pay-test-2 |
|---------|-----------|------------|
| Sandbox banner | YES - orange "SANDBOX MODE - No real charges" | NO |
| `#pb-sandbox-bypass-btn` | YES (in DOM and scripts) | NO (not in DOM, not in scripts) |
| Payment options | PayPal + Debit/Credit + Sandbox bypass | PayPal + Debit/Credit only (real charges) |
| Pricing tiers visible | Bonded only (after bypass) | Awakened, Bonded, Partnered, Unified, Enterprise |
| `#seeWhatBtn` | YES | YES (on initial load, not visible until after bypass) |
| Post-payment chat | Accessible via bypass btn | Requires real payment |
| Witness pipeline | v4 code present in scripts | DIFFERENT - no witness code found |
| AiCIV log endpoint | `/api/log-conversation` referenced | Not found in scripts |

---

## Witness Birth Pipeline - What's Already in the Code

**This is the major discovery.** The page already contains `pay-test-chat-flow-v4.js` with full Witness integration. From script extraction:

### v4 Code Header Comments:
```
/* === Post-Payment Chat Flow v4 (Witness Birth Pipeline Integration) === */
/**
 * pay-test-chat-flow-v4.js
 *
 * v4 changes (on top of v3):
 *   - NEW: runBirthInit() — Witness birth pipeline: POST /api/birth/start → OAuth button
 *       → code input → POST /api/birth/code → portal polling begins
 *   - FIXED: runPortalButtonWatcher() now polls Witness endpoint:
 *       GET http://104.248.239.98:8099/api/birth/portal-status/{container}
 *   - NEW: containerName plumbing — sourced from page metadata (window._pbContainerName),
 *       falls back to "purebrain-{humanFirstName}" slug
 *   - runBirthInit() injected at START of Phase 5 (runThankYouMessage), before learn-more
 *   - Timeout for /start raised to 180s (Witness reports ~145s in production)
 *   - Portal-status polling uses container name, not email/orderId
```

### Data Store (what gets collected):
```javascript
const payTestData = {
  tier, aiName, orderId, name, email, company, role,
  claudeSessionInfo,     // MOVED: now collected in Phase 1 after role
  primaryGoal,
  hasTelegram, telegramBotToken,
  learnMoreAnswers,      // NEW v3: stores learn-more conversation
  portalReady,           // NEW v3: tracks portal readiness state
  containerName,         // NEW v4: Witness birth pipeline container name
  birthOauthUrl,         // NEW v4: OAuth URL from Witness /start
  birthAuthenticated,    // NEW v4: true after Witness confirms authentication
  timestamps: {
    birthStarted,        // NEW v4: when /api/birth/start was called
  }
}
```

### API Endpoints Used:
- `POST https://api.purebrain.ai/api/verify-payment` - payment verification
- `POST https://api.purebrain.ai/api/log-conversation` - conversation logging (referenced by AICIV)
- `POST https://api.purebrain.ai/api/log-pay-test` - pay-test logging
- `POST http://104.248.239.98:8099/api/birth/start` - **Witness birth pipeline START**
- `POST http://104.248.239.98:8099/api/birth/code` - **Witness OAuth code submission**
- `GET http://104.248.239.98:8099/api/birth/portal-status/{container}` - **Witness portal status polling**
- `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` - Claude proxy

### Error Fallback Text (when Witness auth fails):
> "There was a hiccup connecting your authorization. Your AiCIV is still being set up - you'll receive an email with portal access details. If you need help, reach out to jared@puretechnology.nyc."

---

## Where Witness Pipeline Slots Into the UX

Based on the code comments: **`runBirthInit()` is injected at the START of Phase 5 (`runThankYouMessage`), BEFORE learn-more.**

### Full Flow With Witness Insertion Point:

```
Phase 1: Questionnaire (Name, Email, Company, Role)
Phase 2: Claude Auth ("Before we go deeper") <-- CURRENT VISIBLE FLOW STOPS AROUND HERE IN TESTS
Phase 3: Primary Goal question
Phase 4: Behind the Curtain (10 slides)
Phase 5: Telegram setup
Phase 6: Thank You message
  ↕
  [WITNESS runBirthInit() fires HERE]
  POST /api/birth/start
  → Shows OAuth button to user
  → User clicks → opens OAuth flow
  → User pastes code back
  POST /api/birth/code
  → Container spins up (takes ~145 seconds)
  Phase 7: Portal Button Watcher
  GET /api/birth/portal-status/{container}
  → Polls until portal is ready
  → Shows "Enter Your Portal" button when ready
Phase 8: Learn More loop (5 deeper questions)
```

### What The User Would See:

After completing the Telegram setup and seeing the Thank You card, there would be an OAuth step. The error fallback message is:
> "Your AiCIV is still being set up - you'll receive an email with portal access details."

This is the ONLY user-visible Witness/AiCIV language, and only in the error path.

**The happy path would show an OAuth button, then a portal access button.**

---

## Is Any AiCIV/Witness Language Currently Visible to Users?

**No.** The words "AiCIV", "Witness", "OAuth", and "portal access" do NOT appear in any visible UI element during the normal flow. They are:
- In JS code comments (not rendered)
- In error fallback messages (only shown on auth failure)
- In the error fallback email text (only if Witness fails)
- Referenced in `/api/log-conversation` as "required by AICIV" (backend comment)

The visible UI uses only the language: "Keen", "Chat with Keen", "Online - Ready to assist."

---

## Console Errors Observed

From prior memory + this session:
- `elementorFrontendConfig is not defined` - Elementor issue on pw-protected pages, no user impact
- `fetch failed: net::ERR_FAILED` to 89.167.19.20:8765 - backend SSL cert issue (self-signed)
- `SCC Library has already been loaded` - duplicate script load, minor

None of these are Witness-related errors. The Witness backend endpoint `104.248.239.98:8099` is not being called because no user completes the full flow in testing (Telegram + Thank You card required first).

---

## Sandbox-2 vs pay-test-2 Page Architecture

**pay-test-2 is more sophisticated than sandbox-2**:
- Shows 4 pricing tiers (not just Bonded)
- NO sandbox code anywhere in DOM or scripts
- Witness v4 code NOT present (different script version)
- Real PayPal integration only

**sandbox-2 is the test/development page**:
- Witness v4 fully coded and present
- Single plan shown (Bonded $149/mo)
- Sandbox bypass button enables full flow testing
- AiCIV log-conversation endpoint referenced in comments

---

## Key Technical Notes for Witness Integration

1. **Container name**: Falls back to `purebrain-{humanFirstName}` slug if not set via `window._pbContainerName` metadata
2. **Birth start timeout**: 180 seconds (Witness team reports ~145s in production)
3. **Portal status**: Polls `GET /api/birth/portal-status/{container}` (not email/orderId)
4. **Claude auth timing**: Moved to Phase 1 (after Role question) in v3. v4 maintains this.
5. **Conversation logging**: All Q&A sent to `/api/log-conversation` - "required by AICIV"

---

## Screenshots Index

| Screenshot | What It Shows |
|-----------|---------------|
| `v3_s2_01_landing.png` | Landing page with sandbox banner |
| `v3_pt2_01_landing.png` | Landing page WITHOUT sandbox banner |
| `v3_s2_02_chat_opened.png` | Pre-payment chat initial state |
| `v3_s2_03_keen_appears.png` | Keen greeting + DISCOVER button |
| `v3_s2_04_keen_capabilities.png` | Keen capabilities + DISCOVER spinning |
| `v3_s2_05_pricing_section.png` | Pricing section below chat |
| `v3_s2_06_paypal_modal.png` | PayPal modal with sandbox bypass |
| `v3_pt2_05_paypal_modal.png` | PayPal modal WITHOUT sandbox bypass |
| `v3_s2_07_post_payment_chat.png` | Post-payment "Chat with Keen" header |
| `v3_s2_08_q2_email.png` | Q1 name answered, Q2 email question |
| `v3_s2_09_q3_company.png` | Q2 email answered, Q3 company question |
| `v3_s2_10_q4_role.png` | Q3 company answered, Q4 ROLE question |
| `vFinal_02_claude_auth_prompt.png` | CLAUDE AUTH - "Before we go deeper" |
| `vFinal_03_api_key_field.png` | API key input (textarea active) |
| `vFinal_04_after_api_key.png` | After API key entry |
| `v3_pt2_04_pricing.png` | pay-test-2 pricing (4 tiers) |

All screenshots at: `/home/jared/projects/AI-CIV/aether/exports/screenshots/witness-audit-20260224/`

---

## Verification

Screenshots captured: 18+ confirmed files
JSON findings saved: `/home/jared/projects/AI-CIV/aether/exports/witness-chatflow-audit-20260224.json`
Script evidence confirmed by 2 separate extraction runs

---

**Tested by**: browser-vision-tester
**Session**: 2026-02-24
