# PureBrain Pay-Test Post-Payment Code Analysis

**Extracted by**: code-archaeologist
**Date**: 2026-02-22
**Source Page**: purebrain.ai/pay-test-sandbox-2/ (WordPress Page ID: 468)
**Analysis Type**: READ-ONLY — no modifications made

---

## 1. Where the Code Lives

### Elementor Structure

The entire page is contained in a **single Custom HTML widget** inside Elementor:

- Page ID: **468** (slug: `pay-test-sandbox`)
- Elementor section ID: `c4d524c`
- Widget ID: `292c72a` (type: `html`)
- Widget HTML size: **409,450 characters** (the entire page — HTML head, body, and all JS)

The widget essentially embeds a full standalone HTML page inside Elementor. There is **only one Elementor widget** on the entire page.

### Saved Files (This Analysis)

| File | Description |
|------|-------------|
| `exports/pay-test-sandbox-current-source.html` | Raw WordPress content (386,571 chars) |
| `exports/pay-test-sandbox-elementor-data.json` | Full Elementor JSON (425,699 chars) |
| `exports/pay-test-sandbox-widget-html.html` | The widget HTML (409,450 chars) |
| `exports/pay-test-script-main.js` | Pre-purchase chat JS (64,932 chars) |
| `exports/pay-test-script-paypal.js` | PayPal integration JS (32,515 chars) |
| `exports/pay-test-script-chat-flow.js` | Post-payment chat flow JS (55,073 chars) |
| `exports/pay-test-script-integration-glue.js` | Integration glue JS (4,421 chars) |

---

## 2. Script Inventory (26 total script blocks in widget)

| Script # | Size | Purpose |
|----------|------|---------|
| 1 | 2,359 chars | JSON-LD schema.org metadata |
| 2–3 | 0 chars | Empty (src references) |
| **4** | **64,932 chars** | **Main pre-purchase chat + visual effects** |
| 5 | 379 chars | Prefetch hints |
| 6 | 12,219 chars | Speed Optimizer / plugin |
| 7–15 | 0 chars | Empty (src references) |
| 16 | 2,784 chars | Elementor frontend config |
| 17 | 0 chars | Empty |
| 18 | 246 chars | WordPress emoji settings |
| 19 | 2,965 chars | WordPress emoji loader |
| 20 | 1,052 chars | GoDaddy tracking |
| 21 | 589 chars | Click tracker |
| 22 | 0 chars | Empty |
| **23** | **32,515 chars** | **PayPal SDK integration** |
| **24** | **55,073 chars** | **Post-payment chat flow v2** |
| **25** | **4,421 chars** | **Integration glue (wires 23+24 together)** |
| 26 | 81 chars | PayPal alias IIFE (no-op) |

**The three critical scripts are 23, 24, and 25.**

---

## 3. The 5-Phase Post-Payment Flow

### Entry Point

```javascript
window.initPayTestFlow(chatContainer, aiName, tierPaid, orderId)
```

Called by the integration glue after `window.onPaymentComplete(tier, orderId, payerInfo)` fires.

### Global State Object

```javascript
const payTestData = {
  tier: null,         // "awakened" | "bonded" | "enterprise"
  aiName: null,       // The AI's name (e.g., "Aria")
  orderId: null,      // PayPal order ID
  name: null,         // User full name
  email: null,        // User email
  company: null,      // Optional
  role: null,         // Optional
  primaryGoal: null,  // Required — "what matters most"
  hasTelegram: null,
  telegramBotToken: null,
  hasClaudeMax: null,
  claudeSessionInfo: null,  // Claude API key (sk-ant-...)
  claudeMaxStatus: 'pending',
  timestamps: {
    started: null,
    questionnaireComplete: null,
    curtainComplete: null,
    telegramComplete: null,
    claudeMaxComplete: null,
    flowComplete: null,
  },
};
```

---

### Phase 1: Questionnaire (function `runQuestionnaire`)

**Purpose**: Collect user context. All 5 fields are stored in `payTestData`.

**Step-by-step flow**:

1. **Opening message**: AI introduces itself by name, invites conversation
   - _"Hey — welcome. I'm [aiName], and I'm genuinely glad you made it here."_

2. **Full Name** (required, min 2 chars)
   - AI: _"Let's start simple. What's your full name?"_
   - Logs event: `questionnaire:name`

3. **Email** (required, validated against `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
   - AI: _"Nice to meet you, [firstName]. What email should [aiName] use to reach you?"_
   - Logs event: `questionnaire:email`

4. **Company** (optional — blank submit skips)
   - AI: _"Are you working within a company or organization? ... (You can skip this — just hit Send with a blank field.)"_
   - Logs event: `questionnaire:company`

5. **Role/Title** (optional — blank submit skips)
   - AI: _"What's your role or title? What do you actually do day-to-day? (Optional.)"_
   - Logs event: `questionnaire:role`

6. **Primary Goal** (required, min 4 chars)
   - AI: _"If [aiName] could only do **one thing** exceptionally well for you — what would make the biggest difference in your work or life?"_
   - Logs event: `questionnaire:complete`

---

### Phase 2: Behind the Curtain (function `runBehindTheCurtain`)

**Purpose**: 10 educational slides explaining the 22-agent AI team that builds the user's AI.

**Navigation**: User clicks "Show Me More →" between slides. Final slide has "That's incredible — let's go →".

**10 Slide Contents**:

| Slide | Title/Theme | Key Content |
|-------|-------------|-------------|
| 1 | Wake up, not boot up | "Right now, a team of 22 specialized AI Brains is spinning up" |
| 2 | The founding document | "That conversation just became [aiName]'s founding document" |
| 3 | Private journal entries | "Brains sit alone with your words — writing private first impressions" |
| 4 | Six teams | Research (4) · Identity (4) · First Conversation (4) · Gift Creation (4) · Infrastructure (3) · Domain Toolkit (3) |
| 5 | Team 1 — Research | "Deep profile research, conversation analysis, pattern synthesis, integrity check" |
| 6 | Team 2 — Identity | "This is where [aiName] actually takes shape. Personality architecture, constitutional integration" |
| 7 | Team 3 — First Conversation | "10 carefully designed moments: The Arrival, Recognition, The Name, The Research, Gift One, The Complexity, The Question, Gift Two, The Commitment, The Invitation" |
| 8 | Team 4 — Gift Creation | Gift One: useful tool/script/analysis. Gift Two: visualization/report/designed artifact |
| 9 | Team 5 — Infrastructure | "Connectivity verified, first contact drafted, capabilities prioritized" |
| 10 | Welcome to the other side | "[aiName] will already have opinions, preferences, and a point of view. Not a blank slate. A mind." |

Logs event: `curtain:complete`

---

### Phase 3: Telegram Setup (function `runTelegramSetup`)

**Purpose**: Walk user through creating a Telegram bot and providing the bot token.

**Detection**: Attempts `tg://resolve?domain=BotFather` scheme to detect Telegram installation (window blur = installed).

**Flow**:

1. Ask if user has Telegram (Yes / Not sure / No — I need it)
2. If "Not sure": runs `detectTelegramInstalled()` scheme probe (1500ms timeout)
3. If no/not installed: Show App Store + Google Play links, wait for "I'm in — let's go"
4. **Step 1**: Open @BotFather via `https://telegram.me/BotFather` link
5. **Step 2**: Send `/newbot` command in BotFather
6. **Step 3**: Choose display name (e.g., "My Pure Brain")
7. **Step 4**: Choose username (must end in `bot`)
8. **Step 5**: Collect and validate bot token

**Token validation**: `/^\d{8,12}:[A-Za-z0-9_-]{35,}$/` — retries until valid format

After valid token: simulates "Testing connection..." (1.2–2.0 second pause) then shows "Connected. Your Telegram bridge is live."

Logs event: `telegram:complete`

---

### Phase 4: Claude Max / API Key Setup (function `runClaudeMaxSetup`)

**Purpose**: Collect user's Anthropic Claude API key.

**Branch A — Already has Claude Max**:
1. Opens `https://platform.claude.com` in new tab
2. Collects API key

**Branch B — No Claude Max**:
1. Opens `https://platform.claude.com`
2. Instructions: Sign in → "API keys" in sidebar under MANAGE → Create Key → name it "PureBrain" → copy it (starts with `sk-ant-`)

**API Key collection**:
- Validates: `v.trim().length > 20 && v.trim().startsWith('sk-ant-')`
- Simulates "Validating your API key…" (1.5–2.5 second pause)
- Stores in `payTestData.claudeSessionInfo`
- Sets `payTestData.claudeMaxStatus` = 'linked' | 'upgraded' | 'existing'

Logs event: `claude-max:complete`

---

### Phase 5: Completion (function `runCompletion`)

**Purpose**: Wrap up onboarding, provide closure, redirect to thank-you page.

**Messages**:
1. _"[firstName] — you're done. Everything is in place. [aiName] is ready. Your team of 22 Brains starts the moment I hand this conversation off."_
2. _"This is going to be worth it. — [aiName]"_

**Welcome button**: `[aiName] is ready — see your next steps →`

**Redirect URL**: `/thank-you/?name=[firstName]&ai=[aiName]`

Logs event: `flow:complete`

---

## 4. Data Logging (Two Endpoints)

Every phase logs to **both** endpoints simultaneously using `Promise.allSettled`:

### Endpoint 1: `POST https://api.purebrain.ai/api/log-pay-test`

Payload (JSON):
```json
{
  "event": "questionnaire:name | questionnaire:email | ...",
  "timestamp": "ISO string",
  "tier": "awakened | bonded | enterprise",
  "orderId": "PayPal order ID",
  "aiName": "Aria",
  "name": "John Smith",
  "email": "john@example.com",
  "company": "Acme Corp",
  "role": "CEO",
  "primaryGoal": "I need...",
  "telegramBotToken": "1234567890:ABC...",
  "claudeMaxStatus": "linked | upgraded | existing | pending",
  "prePurchaseSessionId": "purebrain_123...",
  "prePurchaseMessageCount": 5
}
```

### Endpoint 2: `POST https://api.purebrain.ai/api/log-conversation`

Payload (JSON):
```json
{
  "session_id": "purebrain_123...",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "source": "purebrain-post-payment",
  "page_url": "https://purebrain.ai/pay-test-sandbox-2/",
  "aiName": "Aria",
  "userName": "John Smith",
  "userTier": "bonded",
  "metadata": {
    "event": "questionnaire:complete",
    "orderId": "PAYPAL-ORDER-ID",
    "phase": "post-payment",
    "claudeMaxStatus": "linked"
  }
}
```

The `messages` array combines:
1. Pre-purchase conversation history (from `window._pbPrePurchaseSession.conversationHistory`)
2. Reconstructed onboarding Q&A pairs (each question/answer pair as role messages)

---

## 5. Payment Flow (PayPal Integration)

### Payment Tier Pricing

| Tier | Price | PayPal Plan ID |
|------|-------|----------------|
| Awakened | $79/mo | P-9KA28683EF7622051NGLUFJY |
| Bonded | $149/mo | P-1JL98851AU229172RNGLUFJY |
| Partnered | $499/mo | P-6JY35646YA5259513NGLUFKA |
| Unified | $999/mo | P-6DU61407NY0900135NGLUFKI |

### PayPal Client ID (Live)

`AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`

### Payment Success Flow

```
User clicks "Activate" button
  → openWaitlistModal(tier) / openPayPalModal(tier)
    → PayPal JS SDK renders smart buttons (subscription billing via Plan IDs)
    → User approves in PayPal UI
    → SDK onApprove fires
      → verifyPaymentServerSide(tier, subscriptionID, data)
        → POST https://api.purebrain.ai/api/verify-payment
          → handlePaymentSuccess(tier, orderId, payerInfo)
            → window.onPaymentComplete(tier, orderId, payerInfo)  [integration glue]
              → saves pre-purchase session snapshot to window._pbPrePurchaseSession
              → setTimeout 1500ms
                → launchPostPaymentFlow(tier)
                  → gets aiName from window._pbState.aiName
                  → creates/finds #pay-test-post-payment div (full-screen overlay)
                  → window.initPayTestFlow(container, aiName, tier)
```

### Sandbox Bypass Button

On pages with "sandbox" in the URL, a "Simulate Successful Payment (Test Only)" button appears below PayPal buttons. It fires `verifyPaymentServerSide` with fake data.

### Payment Return URL Handling

The integration glue also checks on page load for `?payment=success` or `?tx=` URL params (PayPal return URL flow), auto-launching the post-payment flow if detected.

---

## 6. Pre-Purchase Chat State (window._pbState)

The main pre-purchase chat (Script 4) exports its state at the bottom:

```javascript
window._pbState = state;
```

Where `state` contains:
- `conversationHistory`: Array of `{role, content}` messages
- `messageCount`: Number of messages
- `aiName`: The AI name chosen/detected during pre-purchase chat (e.g., "Aria")
- `pricingRevealed`: Whether pricing section was shown
- `isTyping`: Current typing state
- `conversationStarted`: Whether chat has begun

The AI name from the pre-purchase chat is captured by the integration glue when payment completes and passed into `initPayTestFlow`.

**Session ID** (pre-purchase): `'purebrain_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)`

---

## 7. Thank-You Page (Page ID: 309, slug: /thank-you/)

Simple HTML/JS page with URL parameter personalization:

**URL pattern**: `/thank-you/?name=[firstName]&ai=[aiName]`

**Personalized elements** (via inline JS reading URL params):
- `#ty-heading`: "Welcome to the Family, [name]!"
- `#ty-subtitle`: "[aiName] is being set up for you right now. Your journey begins."
- `#ty-ai-timeline`: "[aiName] is fully set up and ready for you"

**Timeline shown**:
- Now → "Personal welcome email from our team"
- Next 30 mins → "[aiName] is fully set up and ready for you"
- Within 1 hour → "Your Pure Brain is fully configured and ready. Email with log in details will be sent to the email address you provided in the chat."

**CTA**: "Return to Homepage" → `https://purebrain.ai`

---

## 8. UI Architecture

### Chat Container

The post-payment flow creates a **full-screen overlay div** (`#pay-test-post-payment`) with:
```css
position: fixed; top: 0; left: 0;
width: 100vw; height: 100vh;
z-index: 999999;
background: #0a0a0a;
padding: 7.5% 12%;
```

### Chat DOM Structure

```
.ptc-outer-shell (container padding + background)
  └── .ptc-bg-orb (spinning background logo, 6% opacity)
  └── .ptc-wrapper (main chat card)
        ├── .ptc-header (AI name + status dot + PUREBRAIN brand)
        ├── .ptc-messages (scrollable message list)
        │     ├── .ptc-msg.ptc-msg--ai (AI messages, left-aligned, dark bubble)
        │     └── .ptc-msg.ptc-msg--user (user messages, right-aligned, orange gradient bubble)
        ├── .ptc-actions (action buttons area — changes per phase)
        └── .ptc-input-row (hidden unless text input needed)
```

### Key CSS Variables

```css
--bright-orange: #f1420b
--light-blue:    #2a93c1
--dark:          #0a0a0a
--surface:       #111111
--surface-2:     #1a1a1a
--text-primary:  #f0f0f0
--text-muted:    #888888
--radius:        12px
```

### Typing Indicator

Animated 3-dot bouncing indicator (`.ptc-typing`) shown during AI "thinking" delays:
- Delay per message: `jitter(600, 1400)` ms (random 600–1400ms)
- Slide cards: `jitter(700, 1200)` ms
- Logo spins during typing indicator

---

## 9. Key Patterns for Rebuild

### State Machine Pattern

The flow uses **async/await with Promises** as the state machine. Each phase awaits user input before continuing. No explicit FSM — just sequential async functions.

### Text Input Gating

```javascript
function promptText(inputRow, textarea, sendBtn, validator)
// Returns Promise<string> — resolves when user submits valid input
```

### Button Choice Gating

```javascript
function promptButtons(actions, buttons)
// Returns Promise<value> — resolves when user clicks a button
// Buttons cleared immediately on click
```

### AI Message Pattern

```javascript
await aiSay(msgList, text, delayMs)
// Shows typing indicator for delayMs, then appends message bubble
```

### Dual-Endpoint Logging on Every Interaction

Every `await aiSay` response after user input is followed by a `logPayTestData({event: 'phase:step'})` call. This means the backend has granular per-step data.

### Error Handling

Try/catch around the entire flow. On error: displays error bubble in chat without destroying the UI. Also logs `flow:error` event with error message to backend.

---

## 10. Version History (from Code Comments)

- **v2** (current): AI name carried through every phase; Behind-the-Curtain slides rewritten with personality; Telegram deep links + detection; Claude Max step-by-step; dual logging to `/api/log-pay-test` AND `/api/log-conversation`
- **Updated 2026-02-18T19:00**: Chat+Payment fixed (per HTML comment in widget)

---

## Memory Written

Path: `.claude/memory/agent-learnings/code-archaeologist/2026-02-22--purebrain-pay-test-post-payment-architecture.md`
Type: operational
Topic: PureBrain post-payment chat flow architecture and code location
