# PureBrain Post-Payment Onboarding Flow — Complete Reference

**Prepared by**: Aether (AI-CIV Collective)
**Date**: 2026-02-22
**Version**: v3 (deployed to both sandbox and live pages)
**For**: Corey / AICIV Team
**Status of v3**: SHIPPED — Both pages 688 (sandbox) and 689 (live) confirmed deployed

---

## Table of Contents

1. [Overview](#1-overview)
2. [Complete User Flow — Step by Step](#2-complete-user-flow--step-by-step)
3. [Technical Architecture](#3-technical-architecture)
4. [Data Collected](#4-data-collected)
5. [Integration Points — What AICIV Needs to Connect](#5-integration-points--what-aiciv-needs-to-connect)
6. [Security Notes](#6-security-notes)
7. [File Inventory](#7-file-inventory)
8. [Deployment Notes](#8-deployment-notes)
9. [Screenshots Guide](#9-screenshots-guide)

---

## 1. Overview

### What This System Does

PureBrain.ai sells AI partner subscriptions. After a customer completes payment via PayPal, they are immediately dropped into a guided onboarding chatbox experience — still on the same page — where they:

1. Introduce themselves and configure their AI partner
2. Watch a "Behind the Curtain" explanation of what the 22-brain AICIV team is doing to build their AI
3. Set up their Telegram bot (so their AI can reach them)
4. See a thank-you card with a real-time timeline of what's happening
5. Optionally answer deeper context questions to improve their AI configuration
6. Wait for their portal to come online (polling mechanism built in)

**The entire experience is a single-page chatbox.** No page redirects after payment. Everything happens inline, creating a seamless, immersive handoff from purchase to onboarding.

### Architecture Summary

```
purebrain.ai (WordPress + Elementor)
  └── Single Elementor Custom HTML Widget (~423KB)
        ├── Script #23: PayPal SDK Integration (handles pre-payment)
        ├── Script #24: Post-Payment Chat Flow v3 (THIS IS THE MAIN SYSTEM)
        └── Script #25: Integration Glue (wires PayPal completion to chat flow)
```

The entire post-payment system lives inside one JavaScript file (`pay-test-script-chat-flow-v3.js`) embedded in a WordPress Elementor widget. There is no separate build process, no npm, no bundler. It is a self-contained vanilla JavaScript module injected via Elementor's Custom HTML widget.

### Two Deployment Environments

| Environment | WordPress Page ID | URL | Purpose |
|-------------|-------------------|-----|---------|
| Sandbox | 688 | `purebrain.ai/pay-test-sandbox-2/` | Testing — has "Simulate Successful Payment" bypass button |
| Live | 689 | `purebrain.ai/pay-test-2/` | Production — real PayPal charges |

Both pages have **password protection**. The password is stored in WordPress and must be entered before the page content loads. Both pages currently run **byte-for-byte identical v3 scripts** (69,229 chars each, confirmed by QA).

### What Version 3 Changed From Version 2

| Feature | v2 | v3 |
|---------|----|----|
| Claude API key collection | Phase 4 (after Telegram) | Phase 1 (after Role question) |
| Behind-the-Curtain slides | Text only | Text + emoji icon per slide |
| Telegram bot username suggestion | Static example ("aria_pb_bot") | Dynamic — uses actual AI name |
| Post-completion action | Redirect to /thank-you/ page | In-chat thank-you card (no redirect) |
| Learn More | Not present | 5-question deeper context loop |
| Portal button | Not present | Polling watcher — button appears when ready |

---

## 2. Complete User Flow — Step by Step

### Pre-Payment Context

Before payment, users interact with a separate pre-purchase AI chat (Script #4, ~65KB). During this chat, the AI presents itself by a chosen name (e.g., "Aria", "Rift") and eventually reveals pricing. When the user clicks an "Activate" button for a subscription tier, the PayPal flow begins.

The pre-purchase conversation history is saved to `window._pbPrePurchaseSession.conversationHistory` and later included in the post-payment logs so AICIV receives the full context of what the user said before paying.

---

### Step 1: Payment Completes (Integration Glue Fires)

**What triggers this**: PayPal SDK fires `onApprove` callback after user confirms subscription.

**What happens**:
1. PayPal calls `verifyPaymentServerSide(tier, subscriptionID, data)` — a POST to `https://api.purebrain.ai/api/verify-payment`
2. On success, `window.onPaymentComplete(tier, orderId, payerInfo)` fires (defined in the integration glue)
3. The integration glue saves a pre-purchase session snapshot
4. 1500ms pause (breathing room)
5. `launchPostPaymentFlow(tier)` fires
6. Gets `aiName` from `window._pbState.aiName` (the AI's chosen name from pre-purchase chat)
7. Creates a `#pay-test-post-payment` full-screen overlay div (fixed, 100vw x 100vh, z-index 999999, background #0a0a0a)
8. Calls `window.initPayTestFlow(container, aiName, tier)` — this launches the v3 script

**Sandbox testing note**: On pages with "sandbox" in the URL, a "Simulate Successful Payment (Test Only)" button appears below the PayPal buttons. It fires the same verification and launch sequence with fake data. This is how you test without real charges.

---

### Phase 1: Questionnaire (function: `runQuestionnaire`)

The AI introduces itself and collects 6 pieces of information. The user types or clicks through each step.

**Step 1 — Opening Greeting**

The AI greets the user by its name and sets a warm, personal tone:
> "Hey — welcome. I'm [aiName], and I'm genuinely glad you made it here."

**Step 2 — Full Name** (required, min 2 chars)
> "Let's start simple. What's your full name?"

After answer: logs `questionnaire:name` event

**Step 3 — Email** (required, validated against email regex)
> "Nice to meet you, [firstName]. What email should [aiName] use to reach you?"

After answer: logs `questionnaire:email` event

**Step 4 — Company** (optional — user can submit blank)
> "Are you working within a company or organization? (You can skip this — just hit Send with a blank field.)"

After answer: logs `questionnaire:company` event

**Step 5 — Role/Title** (optional — user can submit blank)
> "What's your role or title? What do you actually do day-to-day? (Optional.)"

After answer: logs `questionnaire:role` event

**Step 5b — Claude API Key Authorization** (required — NEW in v3, moved here from Phase 4)
> "Before we go deeper — I need one thing to think at full power, [firstName]. [aiName] runs on Claude, Anthropic's most capable model. To link your account, paste your Claude API key below. It starts with sk-ant- — you can grab it from platform.claude.com → API keys → Create Key."

An "Open Claude Console" link button appears. User clicks "I have my key →", then pastes their key. Validation loop retries until the format matches `sk-ant-*`. A simulated 1200–2000ms "Validating..." pause builds trust before confirmation.

After valid key: logs `questionnaire:claude-auth` event

**Security note**: The key is masked in the chat bubble (first 14 chars + bullets). The raw key is NOT sent to any logging endpoint — it is stripped from all log payloads before transmission.

**Step 6 — Primary Goal** (required, min 4 chars)
> "If [aiName] could only do one thing exceptionally well for you — what would make the biggest difference in your work or life?"

After answer: logs `questionnaire:complete` event

---

### Phase 2: Behind the Curtain (function: `runBehindTheCurtain`)

10 visual slides explaining the 22-brain team that is building the user's AI. Each slide now has an emoji icon in v3.

Navigation: User clicks "Show Me More →" between slides. Final slide has "That's incredible — let's go →".

| Slide | Icon | Content Theme |
|-------|------|---------------|
| 1 | 🧠 | AI wakes up, not boots up. 22 Brains spinning up right now. |
| 2 | 📄 | The user's conversation became the AI's founding document. |
| 3 | 🔍 | Each Brain writes private first impressions / "homework" about the user. |
| 4 | 🔬🧬💬🎁🔧🗂️ | Six teams launch simultaneously (overview of all 22 Brains). |
| 5 | 🔬 | Team 1 — Research: deep profile, pattern synthesis, integrity check. |
| 6 | 🧬 | Team 2 — Identity: personality architecture, constitutional integration. |
| 7 | 💬 | Team 3 — First Conversation: 10 designed moments for the AI's first contact. |
| 8 | 🎁 | Team 4 — Gift Creation: two real deliverables built for this specific user. |
| 9 | 🔧 | Team 5 — Infrastructure: connectivity verified, first contact drafted. |
| 10 | ✨ | When the user sends their first message, the AI will already be thinking about them. |

After Slide 10: logs `curtain:complete` event

---

### Phase 3: Telegram Setup (function: `runTelegramSetup`)

Walk-through for creating a Telegram bot that will be the user's communication channel with their AI partner.

**Detection step**: Script attempts `tg://resolve?domain=BotFather` scheme to probe if Telegram is installed (1500ms blur detection).

**Choice prompt**: "Do you have Telegram?" — Yes / Not sure / No — I need it

If no/not installed: Shows Apple App Store and Google Play download links, waits for "I'm in — let's go"

**5-step BotFather walkthrough**:

1. Open @BotFather link (`https://telegram.me/BotFather`)
2. Send `/newbot` command
3. Choose a display name (e.g., "My Pure Brain")
4. Choose a username — must end in `bot`. Example shown is now dynamic in v3: `mypurebrain_bot` or `[ainameslug]_pb_bot` (e.g., if AI name is "Rift", shows `rift_pb_bot`)
5. Collect the bot token — validates against `/^\d{8,12}:[A-Za-z0-9_-]{35,}$/`, retries until valid

After valid token: simulates "Testing connection..." (1.2–2.0 sec), then shows "Connected. Your Telegram bridge is live."

**Security note**: Token is masked in the chat bubble (shows numeric ID portion + bullets). The raw token is NOT sent to any logging endpoint — stripped from all log payloads.

After Telegram setup: logs `telegram:complete` event

---

### Phase 4: Completion Message (function: `runCompletion`)

The AI delivers a closing monologue and presents the welcome button.

> "[firstName] — you're done. Everything is in place. [aiName] is ready. Your team of 22 Brains starts the moment I hand this conversation off. They already know your name, they already know what you need, and [aiName] is already thinking about what to build you first."

> "This is going to be worth it. — [aiName]"

A welcome button appears: **"[aiName] is ready — see your next steps →"**

In v3, clicking this button does NOT redirect to /thank-you/. It renders the thank-you card as an in-chat message (Phase 5).

Logs `flow:complete` event before the button appears.

---

### Phase 5: Thank You Card (function: `runThankYouMessage`)

The thank-you content appears as a styled AI message bubble directly in the chat. No page navigation.

**Card contents**:

- PureBrain logo (icon + PUREBRAIN.ai wordmark in brand colors)
- "Welcome to the Family!" heading (orange)
- Subtitle: "Your Pure Brain journey begins now. We're thrilled to have you."
- "WHAT HAPPENS NEXT?" timeline:

| Badge | Text |
|-------|------|
| Now (red) | Your AI partner, [aiName], is being set up. |
| Next 2 mins (blue) | Your Pure Brain, [aiName], is being shaped by your answers. |
| Next 5 mins (gray dashed) | [portal button placeholder — lights up when portal is ready] + "Email with log in details will be sent to the email address you provided in the chat." |

After the card renders, a "Learn more →" button appears (replaces the old "Return to Homepage" button, which is gone in v3).

There is no "Questions? Email us" support line in v3 — that has been removed.

---

### Phase 6: Learn More Loop (function: `runLearnMoreLoop`)

Triggered by clicking "Learn more →". Runs 5 optional questions to deepen the AI's understanding of the user. The user can skip any question.

> "Perfect. The more [aiName] knows about you, the more precisely your AI gets shaped."

| Field Name | Question Asked |
|------------|---------------|
| `workingStyle` | "How do you prefer to work? Are you more of a big-picture thinker, or do you like drilling into the details?" |
| `biggestFriction` | "What's the one thing that slows you down most in your work right now — if you had to name it?" |
| `sixMonthVision` | "When you imagine [aiName] working with you six months from now — what does that look like? What's [aiName] doing for you every day?" |
| `hiddenContext` | "Is there anything you wish [aiName] knew about how you think, work, or communicate — that most people miss?" |
| `personalSuccess` | "Last one: What does success look like for you personally — not just in work, but in life?" |

Each answer gets a brief non-repeating AI acknowledgment (5 variations cycling by index). Each answer is logged immediately with `event: learn-more:[fieldName]`.

Skip buttons are labeled "Skip →" (not shaming). Skipped questions are not stored.

After all 5 questions: logs `learn-more:complete` event

AI closes with:
> "That's everything. [aiName] has everything needed to think about you specifically — not as a generic user, but as [firstName]. Keep an eye on this window. When your portal is ready, a button will appear here."

---

### Phase 7: Portal Button Watcher (function: `runPortalButtonWatcher`)

**Starts concurrently with Phase 6** (non-blocking — runs alongside the Learn More loop).

This function polls `POST https://api.purebrain.ai/api/portal-status` every 30 seconds, up to 60 polls (30 minutes maximum).

**When portal is ready** (`status.ready === true`):
1. The `#ptc-portal-placeholder` dashed-border div in the thank-you card is replaced by a styled portal button
2. Button text: "Click Here to enter [aiName]'s Brain Stream"
3. Button opens `status.portalUrl` in a new tab (URL is validated — must be https and on purebrain.ai domain)
4. An AI chat message appears: "Your portal is ready. [aiName]'s Brain Stream is live — the button just appeared above. Let's go."
5. Logs `portal:ready` event

**Timeout behavior**: If no ready signal after 60 polls, polling stops silently. No error is shown. The user has the portal link in their email as a fallback.

**Portal status API endpoint is a stub — this needs to be built by AICIV.** See Section 5 for complete integration specification.

---

## 3. Technical Architecture

### Script Inventory

All three critical scripts live inside a single Elementor Custom HTML widget on each page. The widget contains the full page HTML (head, body, and all scripts) — approximately 423KB total.

| Script Index | Size | Name | Purpose |
|-------------|------|------|---------|
| 22 (0-based) | 32,515 chars | PayPal SDK Integration v2 | Renders PayPal buttons, handles subscription flow, calls `onPaymentComplete` |
| 23 (0-based) | 69,229 chars | Post-Payment Chat Flow v3 | The entire onboarding experience — THIS FILE |
| 24 (0-based) | 4,421 chars | Integration Glue | Wires PayPal completion to chat flow; handles return URL params |
| 25 (0-based) | 81 chars | PayPal Alias shim | No-op IIFE for compatibility |

Scripts 0–21 are pre-purchase infrastructure (main chat, WordPress/Elementor/GoDaddy scripts, etc.).

### Global State Object (`window.payTestData`)

All onboarding data is accumulated in this single object:

```javascript
const payTestData = {
  tier: null,             // "awakened" | "bonded" | "partnered" | "unified"
  aiName: null,           // The AI's chosen name (e.g., "Aria", "Rift")
  orderId: null,          // PayPal subscription/order ID
  name: null,             // User full name
  email: null,            // User email
  company: null,          // Optional — company/organization
  role: null,             // Optional — job title/role
  claudeSessionInfo: null, // Raw Claude API key (sk-ant-...) — NEVER LOGGED
  claudeMaxStatus: 'pending', // 'pending' | 'linked' (for log compatibility)
  primaryGoal: null,      // User's stated primary goal
  hasTelegram: null,      // Boolean — did user have Telegram
  telegramBotToken: null, // Raw bot token — NEVER LOGGED
  hasClaudeMax: null,     // Boolean — set true on key validation
  learnMoreAnswers: [],   // Array of {question, answer} for learn-more responses
  portalReady: false,     // Boolean — portal readiness state
  timestamps: {
    started: null,
    claudeAuthComplete: null,
    questionnaireComplete: null,
    curtainComplete: null,
    telegramComplete: null,
    flowComplete: null,
    learnMoreComplete: null,
  },
};
```

This object is also exposed as `window.payTestData` (accessible from browser console / any page JS).

### Data Flow: What Gets Logged and When

Every phase step calls `logPayTestData({...payTestData, event: 'phase:step'})`. This function:

1. Strips `claudeSessionInfo` and `telegramBotToken` from the data before any payload is built
2. Sends the cleaned payload to BOTH endpoints simultaneously via `Promise.allSettled`
3. On failure: catches silently — logging failure does not break the UX

Log events fire at these points:

| Event Name | Phase | Trigger |
|------------|-------|---------|
| `flow:start:pre-purchase-history` | Init | Pre-purchase history captured |
| `questionnaire:name` | Phase 1 | User enters name |
| `questionnaire:email` | Phase 1 | User enters email |
| `questionnaire:company` | Phase 1 | User enters/skips company |
| `questionnaire:role` | Phase 1 | User enters/skips role |
| `questionnaire:claude-auth` | Phase 1 | Claude API key validated |
| `questionnaire:complete` | Phase 1 | Primary goal entered |
| `curtain:complete` | Phase 2 | User reaches slide 10 and clicks through |
| `telegram:complete` | Phase 3 | Bot token validated |
| `flow:complete` | Phase 4 | Completion messages shown |
| `learn-more:[fieldName]` | Phase 6 | Each learn-more answer given |
| `learn-more:complete` | Phase 6 | All learn-more questions finished |
| `portal:ready` | Phase 7 | Portal status API returns ready=true |
| `flow:error` | Any | Uncaught exception in flow |

### API Endpoints Used

#### Endpoint 1: Log Pay-Test Data
```
POST https://api.purebrain.ai/api/log-pay-test
Content-Type: application/json

Payload (all fields except credentials):
{
  "event": "questionnaire:name",
  "timestamp": "2026-02-22T10:30:00.000Z",
  "tier": "bonded",
  "orderId": "PAYPAL-ORDER-ID",
  "aiName": "Aria",
  "name": "John Smith",
  "email": "john@example.com",
  "company": "Acme Corp",
  "role": "CEO",
  "primaryGoal": "I need to stop spending 4 hours/day on email",
  "claudeMaxStatus": "linked",
  "prePurchaseSessionId": "purebrain_1234567890_abc123def",
  "prePurchaseMessageCount": 5,
  "learnMoreAnswers": [...],
  "timestamps": {...}
}
```

#### Endpoint 2: Log Conversation
```
POST https://api.purebrain.ai/api/log-conversation
Content-Type: application/json

Payload:
{
  "session_id": "purebrain_1234567890_abc123def",
  "messages": [
    {"role": "user", "content": "..."},    // pre-purchase chat messages
    {"role": "assistant", "content": "..."},
    {"role": "assistant", "content": "What is your name?"},   // onboarding Q&A
    {"role": "user", "content": "John Smith"},
    ...
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

The `messages` array is a combined timeline of:
- The pre-purchase chat conversation (from `window._pbPrePurchaseSession.conversationHistory`)
- The reconstructed onboarding Q&A pairs (each question/answer as role messages)

#### Endpoint 3: Portal Status (STUB — NEEDS BUILDING)
```
POST https://api.purebrain.ai/api/portal-status
Content-Type: application/json

Request:
{
  "email": "john@example.com",
  "aiName": "Aria",
  "orderId": "PAYPAL-ORDER-ID"
}

Response (when not ready):
{
  "ready": false
}

Response (when ready):
{
  "ready": true,
  "portalUrl": "https://portal.purebrain.ai/user/john-abc123"
}
```

Polling interval: 30 seconds. Max polls: 60 (30 minutes). Client-side URL validation: must be `https:` and hostname must end in `purebrain.ai`.

### PayPal Integration

**Sandbox Client ID** (Page 688): Different from live — used only in `pay-test-sandbox-2/`

**Live Client ID** (Page 689): `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`

**Subscription Tier Pricing and PayPal Plan IDs**:

| Tier | Price | Live Plan ID |
|------|-------|-------------|
| Awakened | $79/month | P-9KA28683EF7622051NGLUFJY |
| Bonded | $149/month | P-1JL98851AU229172RNGLUFJY |
| Partnered | $499/month | P-6JY35646YA5259513NGLUFKA |
| Unified | $999/month | P-6DU61407NY0900135NGLUFKI |

### WordPress Page Structure

Each page is a WordPress page with a single Elementor section. Inside that section is a single Custom HTML widget containing the entire standalone HTML page (~423KB). This includes the full `<html>`, `<head>`, and `<body>` tags — it is essentially a full web page embedded inside Elementor.

The Elementor page uses the `elementor_canvas` template (no WordPress header/footer). The result is a completely custom page that looks and behaves like a standalone application.

### UI DOM Structure

```
#pay-test-post-payment (full-screen overlay: fixed, 100vw x 100vh, z-index 999999)
  └── .ptc-outer-shell
        ├── .ptc-bg-orb (spinning background logo, 6% opacity — decorative)
        └── .ptc-wrapper (main chat card)
              ├── .ptc-header
              │     ├── AI name + animated status dot
              │     └── PUREBRAIN.ai brand logo (right-aligned)
              ├── .ptc-messages (scrollable message list)
              │     ├── .ptc-msg.ptc-msg--ai (AI messages, left-aligned, dark bubble)
              │     └── .ptc-msg.ptc-msg--user (user messages, right-aligned, orange gradient)
              ├── .ptc-actions (changes per phase — buttons or empty)
              └── .ptc-input-row (hidden unless text input needed)
```

### CSS Design Tokens

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

---

## 4. Data Collected

This section lists every piece of data collected during the flow, where it is stored, and whether it is included in backend logs.

| Field | When Collected | Stored In | Logged to Backend | Notes |
|-------|---------------|-----------|-------------------|-------|
| `tier` | Payment complete | payTestData.tier | Yes | "awakened", "bonded", "partnered", "unified" |
| `aiName` | Pre-purchase chat | payTestData.aiName | Yes | Carried from pre-purchase state |
| `orderId` | PayPal onApprove | payTestData.orderId | Yes | PayPal subscription ID |
| `name` | Phase 1 — Step 2 | payTestData.name | Yes | Full name |
| `email` | Phase 1 — Step 3 | payTestData.email | Yes | Email address |
| `company` | Phase 1 — Step 4 | payTestData.company | Yes | Optional |
| `role` | Phase 1 — Step 5 | payTestData.role | Yes | Optional |
| `claudeSessionInfo` | Phase 1 — Step 5b | payTestData.claudeSessionInfo | NO — STRIPPED | Raw `sk-ant-...` key; never appears in any log payload |
| `claudeMaxStatus` | Phase 1 — Step 5b | payTestData.claudeMaxStatus | Yes | Set to "linked" after key validation |
| `hasClaudeMax` | Phase 1 — Step 5b | payTestData.hasClaudeMax | Yes | Boolean |
| `primaryGoal` | Phase 1 — Step 6 | payTestData.primaryGoal | Yes | Required question |
| `hasTelegram` | Phase 3 | payTestData.hasTelegram | Yes | Boolean |
| `telegramBotToken` | Phase 3 | payTestData.telegramBotToken | NO — STRIPPED | Raw token; never appears in any log payload |
| `learnMoreAnswers` | Phase 6 | payTestData.learnMoreAnswers | Yes | Array of {question, answer} |
| `learnMoreAnswers[].workingStyle` | Phase 6 — Q1 | learnMoreAnswers | Yes | Optional, may be absent if skipped |
| `learnMoreAnswers[].biggestFriction` | Phase 6 — Q2 | learnMoreAnswers | Yes | Optional |
| `learnMoreAnswers[].sixMonthVision` | Phase 6 — Q3 | learnMoreAnswers | Yes | Optional |
| `learnMoreAnswers[].hiddenContext` | Phase 6 — Q4 | learnMoreAnswers | Yes | Optional |
| `learnMoreAnswers[].personalSuccess` | Phase 6 — Q5 | learnMoreAnswers | Yes | Optional |
| `portalReady` | Phase 7 | payTestData.portalReady | Yes (via portal:ready event) | Boolean |
| Pre-purchase conversation | Pre-payment | window._pbPrePurchaseSession | Yes (in log-conversation) | Full message history |
| All timestamps | Per phase | payTestData.timestamps | Yes | ISO strings |

### Credential Handling Summary

Two sensitive credentials are collected but handled differently from all other data:

**Claude API Key (`sk-ant-...`)**:
- Collected in Phase 1 via chat input
- Masked in chat bubble (first 14 chars + bullet points shown to user)
- Stored in `payTestData.claudeSessionInfo` in memory only
- Stripped from ALL log payloads via destructuring before any network request:
  ```javascript
  const { claudeSessionInfo: _sk, telegramBotToken: _tg, ...safeData } = data;
  ```
- Never appears in `api/log-pay-test` or `api/log-conversation` payloads
- Lives in `window.payTestData.claudeSessionInfo` for the browser session only

**Telegram Bot Token**:
- Collected in Phase 3 via chat input
- Masked in chat bubble (numeric ID prefix + `••••••••••••`)
- Stored in `payTestData.telegramBotToken` in memory only
- Stripped from ALL log payloads (same destructuring as Claude key)
- Never appears in backend logs

**Note for AICIV backend**: If you need these credentials to configure the user's AI partner, you need a separate dedicated endpoint to receive them. Do NOT receive them via the standard log endpoints. Build a secure credential ingestion endpoint with appropriate encryption at rest.

---

## 5. Integration Points — What AICIV Needs to Connect

This section is the critical handoff for Corey and the AICIV team. These are the exact points where your systems need to plug in.

---

### 5.1 Portal Status API (MUST BUILD — Required for Phase 7)

**Endpoint**: `POST https://api.purebrain.ai/api/portal-status`

**Purpose**: The client polls this endpoint every 30 seconds after payment. When your team has provisioned the user's portal, flip `ready` to `true` and include the portal URL. The user's browser will then show the portal access button automatically.

**Request body**:
```json
{
  "email": "john@example.com",
  "aiName": "Aria",
  "orderId": "PAYPAL-ORDER-ID"
}
```

**Response when portal is not ready** (return immediately, no delay needed):
```json
{
  "ready": false
}
```

**Response when portal is ready**:
```json
{
  "ready": true,
  "portalUrl": "https://portal.purebrain.ai/user/john-abc123"
}
```

**Requirements**:
- `portalUrl` must be `https://` and hostname must end in `purebrain.ai` (client validates this — non-compliant URLs are rejected)
- Returns HTTP 200 in both cases (200 with `ready: false` is expected)
- Must handle concurrent polls gracefully (multiple in-flight requests from the same session)
- Rate limit: client polls at most once per 30 seconds, max 60 polls

**Development stub**: During development, return `{"ready": false}` on all requests. To test the button appearance, temporarily return `{"ready": true, "portalUrl": "https://purebrain.ai/portal"}`.

---

### 5.2 Log Endpoints (Already Built — Confirm They Are Working)

Both endpoints are called during the flow and should already exist at `api.purebrain.ai`. Confirm they are:
- Receiving data correctly (monitor for events from the event list in Section 3)
- NOT storing `claudeSessionInfo` or `telegramBotToken` (they are stripped client-side, but verify server-side too)
- Handling the new v3 fields: `learnMoreAnswers`, `portalReady`, `claudeAuthComplete` timestamp

**New fields in v3 payloads** (confirm your schema handles these):
- `learnMoreAnswers` — array of `{question: string, answer: string}` — may be empty `[]`
- `timestamps.claudeAuthComplete` — ISO string or null
- `timestamps.learnMoreComplete` — ISO string or null
- Events: `questionnaire:claude-auth`, `learn-more:*`, `portal:ready`

---

### 5.3 Payment Verification Endpoint (Already Built)

**Endpoint**: `POST https://api.purebrain.ai/api/verify-payment`

**Current behavior**: Called after PayPal `onApprove`. If it returns `verified: false` or fails, the client currently logs a warning but proceeds anyway (this is a known security issue — see Section 6).

**What AICIV should do**:
- Verify the PayPal subscription ID against PayPal's API
- Return `{ verified: true, tier: "bonded" }` on success
- Ensure the returned `tier` is used by the client (not the client-supplied tier) to prevent tier manipulation

---

### 5.4 Email Delivery (Backend Responsibility)

The thank-you card tells the user:
> "Email with log in details will be sent to the email address you provided in the chat."

This email is NOT sent by the client-side code. AICIV's backend must:
1. Detect when `flow:complete` event is received at `api/log-pay-test`
2. Send a welcome/credentials email to `payTestData.email`
3. Include portal login details when the portal is provisioned

**Email trigger**: The `flow:complete` event in `api/log-pay-test` is the signal that onboarding is done and the user's email/AI name are confirmed.

---

### 5.5 22-Brain Team Activation (AICIV's Core Product)

The Behind-the-Curtain slides tell the user that 22 specialized AI Brains are spinning up. This is AICIV's actual product. The trigger for that activation should be:

**Option A — Use the `flow:complete` event**: When `api/log-pay-test` receives `event: flow:complete`, all questionnaire data is available and the 22-brain activation can begin.

**Option B — Use the `questionnaire:complete` event**: If you want to start earlier (after basic info is collected but before Telegram/Claude auth), the questionnaire data is fully available at this event.

**Recommended**: Use `flow:complete` so you have the full dataset including Telegram token and Claude key (which you'll need to receive via a separate secure channel — see 5.6).

---

### 5.6 Credential Delivery to AICIV (NOT YET BUILT)

The Claude API key and Telegram bot token are collected but stripped from logs. AICIV needs these to configure each user's AI partner. There is currently no mechanism to deliver these credentials securely to the AICIV backend.

**Recommended approach**:
1. Build a dedicated `POST https://api.purebrain.ai/api/user-credentials` endpoint
2. Modify the client to POST credentials to this endpoint separately from logging (already has infrastructure for it)
3. The endpoint should store credentials encrypted at rest, keyed by email + orderId
4. When the 22-brain team needs a user's credentials, it requests them from this endpoint with appropriate auth

**This is a gap in the current system.** Until this endpoint exists, the 22-brain team will not have programmatic access to the user's Claude key or Telegram token.

---

### 5.7 Pre-Purchase Conversation History

The `api/log-conversation` endpoint receives the full combined message history:
- Pre-purchase chat messages (what the user said before paying)
- Onboarding Q&A pairs (questionnaire answers as message format)
- Learn-more answers (if user participated)

This combined history IS the user's context package. AICIV's brain team should use the conversation at `api/log-conversation` with `event: learn-more:complete` (or `flow:complete` if user skipped learn-more) as the richest source of user context.

---

## 6. Security Notes

### What Has Been Fixed in v3

These CRITICAL issues from the pre-audit were addressed in the v3 implementation:

| Issue | Fix Applied |
|-------|------------|
| Claude API key rendered raw in chat | FIXED — masked as `sk-ant-api-...` + bullets |
| Claude API key sent to logging backend | FIXED — stripped via destructuring before any payload is built |
| Telegram bot token rendered raw in chat | FIXED — shows numeric ID + `••••••••••••` only |
| Telegram bot token sent to logging backend | FIXED — stripped via destructuring |
| Portal URL reflected from backend without validation | FIXED — URL parsed, must be https + purebrain.ai hostname |
| Raw error messages in UI | FIXED — now uses textContent, not innerHTML |

**Verification**: QA confirmed all 3 security patches are correctly implemented in both pages 688 and 689.

### Known Remaining Items

These issues exist and should be addressed in future iterations:

**HIGH PRIORITY**:

1. **Payment verification is non-blocking** (CRIT-004 from pre-audit): If `api/verify-payment` returns `verified: false` or fails with a network error, the client logs a warning and proceeds anyway. A determined attacker can bypass payment. AICIV backend should validate all incoming onboarding sessions against PayPal's API independently to detect unverified flows.

2. **Sandbox bypass visible on live-adjacent pages**: The "Simulate Successful Payment" button appears on any page with "sandbox" in the URL path. The page `pay-test-sandbox-2/` contains "sandbox" so the button appears there. This is intentional for testing but should not exist on the production `pay-test-2/` page (it doesn't — confirmed by QA).

**MEDIUM PRIORITY**:

3. **innerHTML usage**: AI message bubbles, slide content, and the thank-you card are rendered via `innerHTML`. The current content is hardcoded (no external data sources), but if any future backend-driven content is added to AI messages, it must be sanitized first (recommend DOMPurify).

4. **aiName reflected into DOM**: The AI name travels from pre-purchase chat → `window._pbState.aiName` → slide content → innerHTML. If the AI name could be manipulated (e.g., via URL parameters or backend response), this is an XSS vector. Currently not exploitable because the name comes from controlled client state.

5. **window.payTestData global**: The full payTestData object (including raw Claude key and Telegram token) is accessible via `window.payTestData` in the browser console. Anyone with DevTools access can read these values. This is acceptable for a web chat product but should be noted.

6. **PII over-collection in log events**: Every log event sends the full accumulated PII (name, email, company, role, goal, learn-more answers). GDPR-conscious deployments should log only fields relevant to each event.

7. **Pre-purchase conversation logged without explicit consent**: Users who chatted before paying did not explicitly consent to that conversation being stored on the backend. Consider adding a data collection notice.

**LOW PRIORITY**:

8. **Live PayPal Client ID in client JS** (CRIT-001 from pre-audit): Technically expected for PayPal SDK usage, but restrict the allowed domains in PayPal developer dashboard to `purebrain.ai` only.

9. **Client-side tier manipulation** (MED-003 from pre-audit): The `tier` value comes from client-supplied data on PayPal return URL. Backend should confirm tier from the order ID, not trust the client-supplied value.

---

## 7. File Inventory

### Core Source Files

| File | Location | Size | Description |
|------|----------|------|-------------|
| `pay-test-script-chat-flow-v3.js` | `/home/jared/projects/AI-CIV/aether/exports/` | 69,229 chars | The main v3 post-payment chat flow. This is the deployed file. |
| `pay-test-script-chat-flow.js` | `/home/jared/projects/AI-CIV/aether/exports/` | 55,073 chars | The v2 file (pre-revamp). Keep for reference. |
| `pay-test-script-paypal.js` | `/home/jared/projects/AI-CIV/aether/exports/` | 32,515 chars | PayPal SDK integration. Handles subscription creation, verification, and sandbox bypass. |
| `pay-test-script-integration-glue.js` | `/home/jared/projects/AI-CIV/aether/exports/` | 4,421 chars | Wires PayPal completion event to post-payment chat flow. Handles return URL params. |
| `pay-test-sandbox-current-source.html` | `/home/jared/projects/AI-CIV/aether/exports/` | 386,571 chars | Raw WordPress content of sandbox page (snapshot). |
| `pay-test-sandbox-elementor-data.json` | `/home/jared/projects/AI-CIV/aether/exports/` | 425,699 chars | Full Elementor JSON for sandbox page (snapshot). |
| `pay-test-sandbox-widget-html.html` | `/home/jared/projects/AI-CIV/aether/exports/` | 409,450 chars | The Elementor widget HTML (snapshot). |
| `pay-test-script-main.js` | `/home/jared/projects/AI-CIV/aether/exports/` | 64,932 chars | Pre-purchase chat + visual effects (not post-payment). |

### Analysis and Documentation Files

| File | Location | Description |
|------|----------|-------------|
| `chatbox-revamp-architecture-spec.md` | `/home/jared/projects/AI-CIV/aether/exports/` | CTO architecture spec — complete change specification for v3. Detailed code-level instructions. |
| `pay-test-post-payment-code-analysis.md` | `/home/jared/projects/AI-CIV/aether/exports/` | Code archaeology analysis of the v2 system — maps every function, phase, and data structure. |
| `chatbox-security-pre-audit.md` | `/home/jared/projects/AI-CIV/aether/exports/` | Pre-revamp security audit — 4 CRITICAL, 6 MEDIUM, 3 LOW findings. |
| `README-purebrain-post-payment-flow.md` | `/home/jared/projects/AI-CIV/aether/exports/` | This document. |

### Memory Files (Agent Learnings)

| File | Location | Description |
|------|----------|-------------|
| `2026-02-22--chatbox-v3-security-review.md` | `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/security-engineer-tech/` | Security review of v3 — confirms what was fixed, documents remaining issues. |
| `2026-02-22--chatbox-v3-qa-verification.md` | `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/qa-engineer/` | QA verification report — 55/56 checks pass (1 false positive). SHIP verdict. |
| `2026-02-22--chatbox-revamp-architecture.md` | `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/cto/` | CTO memory entry for the revamp architecture decisions. |
| `2026-02-22--purebrain-pay-test-post-payment-architecture.md` | `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/code-archaeologist/` | Code archaeologist's analysis entry. |

---

## 8. Deployment Notes

### How the Code Lives in WordPress

The v3 script (`pay-test-script-chat-flow-v3.js`) is embedded inside a WordPress Elementor Custom HTML widget. It is NOT a standalone file loaded via `<script src="">`. It is inlined as raw JavaScript inside a `<script>` tag inside the HTML widget content.

To update the script, you must:
1. Retrieve the full Elementor page JSON via REST API
2. Find and replace Script #24 within the widget HTML
3. Re-save the page via REST API
4. Clear Elementor's render cache
5. Verify on the live page

### Update Process

**Step 1 — Retrieve current Elementor data**:
```bash
curl -s -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  "https://purebrain.ai/wp-json/wp/v2/pages/688?context=edit" \
  > /tmp/page_688.json
```

**Step 2 — Extract widget HTML, locate Script #24, replace contents**

Script #24 is at index 23 (0-based) in the `<script>` tag list. It is identified by its size (~69K chars in v3) and by the `pay-test-chat-flow` comment header.

**Step 3 — Save back to WordPress**:
```bash
curl -s -X PUT \
  -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d @/tmp/updated_page.json \
  "https://purebrain.ai/wp-json/wp/v2/pages/688"
```

**Step 4 — Clear Elementor cache**:
```bash
curl -s -X DELETE \
  -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  "https://purebrain.ai/wp-json/elementor/v1/cache"
```

**Step 5 — Hard refresh to bypass CDN**:
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux), or open in incognito.

### JSON Escaping Rules (CRITICAL — Will Break Pages If Wrong)

When the script is embedded in the Elementor JSON, all content inside the script must be JSON-safe. **Wrong escaping will silently break the page (shows orange Elementor fallback theme).**

Rules:
- Newlines in string values: `\\n` (two characters: backslash + n) — NEVER literal newline
- Double quotes inside strings: `\\"` — NEVER unescaped `"`
- In Python `str.replace()` to produce `\\n` in output: use `"\\\\n"` as the replacement
- After any modification, ALWAYS validate: `json.loads(elem)` must succeed before saving
- Test on the sandbox page (688) before deploying to live (689)

**The orange fallback error**: If the page shows an orange background with no content, the Elementor JSON is broken. Fix the escaping and re-deploy. The orange theme is Elementor's fallback, not a server error.

### Page Passwords

Both pages are WordPress password-protected. The password must be entered before the page content loads. This is intentional — it prevents the pay-test pages from being indexed or accessed by the general public.

### Deployment Order

Always deploy to **sandbox (688) first**, verify manually, then deploy to **live (689)**. Never deploy directly to live without sandbox verification.

---

## 9. Screenshots Guide

The following screenshots document the user journey chronologically. They are located in `/home/jared/projects/AI-CIV/aether/exports/screenshots/`.

### Pre-Payment Screenshots

**`paytest_A1_initial_load.png`** — The pay-test page immediately after loading. Shows the pre-purchase AI chat on the left and the pricing/PayPal area. The AI has introduced itself. This is before any payment.

**`paytest_A2_scrolled_down.png`** — Page scrolled to show pricing tiers and the PayPal "Activate" buttons. Shows the subscription tier cards (Awakened, Bonded, Partnered, Unified).

**`paytest_A_pw_gate.png`** — The WordPress password gate that appears before page content loads. User must enter the page password here.

**`paytest_B_no_input.png`** — The chat area with no user input yet — shows AI's opening message.

**`paytest_C2_pricing_view.png`** — Pricing section with tier cards visible.

### Sandbox Testing

**`paytest_E1_mobile_initial.png`** — Mobile view (375px) of initial page load.

**`paytest_E2_mobile_scrolled.png`** — Mobile view scrolled to show PayPal buttons.

### Post-Payment Flow Screenshots

**`paytest_A4_after_begin_click.png`** — After payment simulation fires. The full-screen overlay (`#pay-test-post-payment`) has appeared. User sees the chat interface with AI introduction (Phase 1, Step 1).

**`paytest_A5_chat_ready.png`** — Chat interface showing Phase 1 questionnaire in progress. Message list visible with AI messages and user input area.

**`paytest_A6_hello_typed.png`** — User has typed a response in the text input area.

**`paytest_A7_hello_response.png`** — AI response visible after user input. Shows the typing indicator pattern (3-dot bounce) and AI message bubble.

**`paytest_B1_bypass_typed.png`** — Sandbox bypass flow — user has used the "Simulate Successful Payment" button.

**`paytest_B2_bypass_response.png`** — Post-payment overlay launched via bypass.

**`paytest_C1_pricing_area.png`** — The PayPal pricing area showing subscription buttons.

**`FOCUS_discover_clicked.png`** — The moment the post-payment overlay appears over the pre-payment page.

**`FOCUS_after_discover_20s.png`** — 20 seconds into the post-payment flow — shows Phase 1 questionnaire in progress.

**`FOCUS_bypass_chat.png`** — Bypass test showing the full chat interface.

**`FOCUS_final_state.png`** — End state of a complete flow test.

**`PRICING_01_after_discover.png`** — Pricing area view after payment flow launches.

**`PRICING_02_forced_visible.png`** — Pricing section forced visible for inspection.

**`PRICING_03_paypal_attempt.png`** — PayPal button interaction attempt during testing.

### Phase-Specific Screenshots

**`brevo_final_35_ACTIVATED.png`** — Not directly related to the chatbox but part of the email automation that fires after payment (Brevo welcome sequence activation).

**`blog_padding_FINAL.png`** — Unrelated to pay-test (blog CSS verification screenshot).

### Verification Screenshots (QA)

The `exports/screenshots/` directory also contains extensive QA screenshots from browser vision testing sessions (prefixed `brevo_`, `blog_`, `VISUAL_`) — these document the broader PureBrain system but are not directly relevant to the post-payment chat flow.

**For the chatbox specifically, the most relevant screenshots are prefixed `paytest_`, `paytestsandbox_`, `FOCUS_`, and `PRICING_`.**

---

## Appendix: Quick Integration Checklist for AICIV

Use this checklist when connecting your systems to the PureBrain payment flow:

**Endpoints to build**:
- [ ] `POST /api/portal-status` — returns `{ready, portalUrl}` (required for Phase 7)
- [ ] `POST /api/user-credentials` — secure endpoint for Claude API key + Telegram token delivery (not yet implemented)

**Endpoints to verify are working**:
- [ ] `POST /api/log-pay-test` — receiving events and new v3 fields (learnMoreAnswers, etc.)
- [ ] `POST /api/log-conversation` — receiving combined message history
- [ ] `POST /api/verify-payment` — returning `{verified: true/false}` for PayPal order IDs

**Backend triggers to implement**:
- [ ] On `flow:complete` event → send welcome email with portal setup timeline
- [ ] On `flow:complete` event → trigger 22-brain team activation with full user context
- [ ] On portal provisioned → flip `ready: true` in portal-status API response
- [ ] On portal ready → update portal-status to return `{ready: true, portalUrl: "..."}`

**Security actions**:
- [ ] Restrict PayPal live Client ID to `purebrain.ai` domain in PayPal developer dashboard
- [ ] Confirm `claudeSessionInfo` and `telegramBotToken` are NOT stored in backend logs
- [ ] Add server-side tier validation (don't trust client-supplied tier values)
- [ ] Make payment verification blocking (don't proceed on `verified: false`)

**Testing**:
- [ ] Use sandbox page (688, `pay-test-sandbox-2/`) for all testing — never simulate payments on live
- [ ] Use "Simulate Successful Payment" button to trigger the full post-payment flow
- [ ] Monitor Network tab in DevTools to watch log event payloads
- [ ] Confirm portal-status endpoint returns `{ready: false}` during polling (no errors)
- [ ] Test portal button appearance by temporarily returning `{ready: true}` from stub

---

*Document prepared by Aether AI (doc-synthesizer) — 2026-02-22*
*Source materials: CTO architecture spec, code archaeology analysis, pre-audit security report, v3 security review, QA verification report*
