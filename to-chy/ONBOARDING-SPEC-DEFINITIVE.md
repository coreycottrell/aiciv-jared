# ONBOARDING SPECIFICATION -- DEFINITIVE

**Status**: CONSTITUTIONAL -- Single Source of Truth
**Last Updated**: 2026-03-28
**Overwrites**: All previous onboarding docs, specs, and fragments
**Author**: dept-systems-technology
**Rule**: This document is non-negotiable. Any agent modifying the onboarding pipeline MUST read this first.

---

## Table of Contents

1. [Landing Pages Inventory](#1-landing-pages-inventory)
2. [Consent Gate](#2-consent-gate)
3. [Payment Tiers and Pricing](#3-payment-tiers-and-pricing)
4. [PayPal Integration](#4-paypal-integration)
5. [Chatbox Flow (Post-Payment)](#5-chatbox-flow-post-payment)
6. [Seed to Witness](#6-seed-to-witness)
7. [Seed Addendum](#7-seed-addendum)
8. [Magic Link Flow](#8-magic-link-flow)
9. [Welcome Emails (Dual Send)](#9-welcome-emails-dual-send)
10. [Portal Access](#10-portal-access)
11. [Constitutional Rules](#11-constitutional-rules)
12. [Server Infrastructure](#12-server-infrastructure)
13. [Verification Script](#13-verification-script)
14. [End-to-End Flow Diagram](#14-end-to-end-flow-diagram)

---

## 1. Landing Pages Inventory

All pages live under `exports/cf-pages-deploy/` and deploy to Cloudflare Pages (`purebrain-staging`).

### LIVE Payment Pages (Real PayPal, Real Subscriptions)

These pages accept real money. Modifications require explicit Jared approval.

| Path | Tier | Pricing Shown | PayPal Mode | Seed/Addendum |
|------|------|---------------|-------------|---------------|
| `/live/` | All 3 tiers | $149 / $499 / $999 | LIVE subscription | Yes |
| `/awakened/` | Awakened | $149 | LIVE subscription | Yes |
| `/partnered/` | Partnered | $499 | LIVE subscription | Yes |
| `/unified/` | Unified | $999 | LIVE subscription | Yes |
| `/insiders/` | Awakened | $149 | LIVE subscription | Yes |
| `/insiders/awakened/` | Awakened | $74.50 (insider price) | LIVE subscription | Yes |

### Sandbox / Test Pages

These pages use sandbox PayPal credentials. Used for E2E testing.

| Path | Purpose | PayPal Mode | Seed/Addendum |
|------|---------|-------------|---------------|
| `/pay-test-sandbox-3/` | Primary sandbox testing | Sandbox subscription | Yes |
| `/pay-test-sandbox-4/` | Secondary sandbox testing | Sandbox subscription | Yes |
| `/pay-test-sandbox-5/` | Latest sandbox testing | Sandbox subscription | Yes |

### Legacy / Partial Pages (No Active Payment Flow)

These pages exist but do NOT have the full modern payment+seed pipeline:

| Path | Notes |
|------|-------|
| `/pay-test/` | Legacy -- minimal PayPal refs, no seed |
| `/pay-test-2/` | Older full flow -- may be outdated |
| `/pay-test-5/` | Older full flow -- may be outdated |
| `/pay-test-awakened/` | Tier-specific test |
| `/pay-test-partnered/` | Tier-specific test |
| `/pay-test-unified/` | Tier-specific test |
| `/pay-test-sandbox/` | Legacy sandbox -- minimal refs |
| `/pay-test-sandbox-2/` | Legacy sandbox -- minimal refs |
| `/aether-awakening/` | Landing page only -- 1 PayPal ref, no payment flow |

### Pages Checked by verify-payment-pages.sh

The constitutional verification script checks these 8 pages:

```
live, awakened, partnered, unified, pay-test-sandbox-3, pay-test-sandbox-5, insiders, insiders/awakened
```

---

## 2. Consent Gate

### Implementation Location

Inline `<script>` block at the bottom of each payment page, wrapped in an IIFE.

### Behavior

1. **Checkbox HTML**: `<input type="checkbox" id="pb-consent-check" class="pb-consent-checkbox" checked />`
2. **Default state**: Checkbox starts CHECKED
3. **On page load**: `DOMContentLoaded` fires `onConsentChange(true)` because checkbox is pre-checked
4. **onConsentChange(true)**:
   - Generates a consent UUID (v4 format)
   - Stores `{uuid, timestamp}` in `sessionStorage` under key `pb_consent_v1`
   - Logs consent to conversation history (`window._pbState.conversationHistory`)
   - POSTs consent event to `https://api.purebrain.ai/api/log-conversation`
   - Calls `unlockCTAs()` -- removes `pb-cta-locked` class, adds `pb-cta-unlocked`
5. **onConsentChange(false)** (user unchecks):
   - Removes `pb_consent_v1` from sessionStorage
   - Calls `lockCTAs()` -- adds `pb-cta-locked` class, removes `pb-cta-unlocked`
   - Buttons become greyed out and non-clickable (`aria-disabled: true`)

### CTA Button IDs

```javascript
document.querySelectorAll('#proCta, #partnerCta, #unifiedCta')
```

### Visual States

- **Unlocked (consent given)**: Bright orange buttons, fully clickable
- **Locked (consent revoked)**: Greyed-out buttons, `aria-disabled="true"`, pointer events blocked by CSS

### CSS Classes

```css
.pb-consent-wrapper { /* container */ }
.pb-consent-checkbox { /* the checkbox input */ }
.pb-consent-label { /* label text with links to Terms/Privacy */ }
.pb-cta-locked { /* greyed out, non-interactive */ }
.pb-cta-unlocked { /* bright orange, interactive */ }
```

---

## 3. Payment Tiers and Pricing

### Current Pricing (as displayed on live pages)

| Tier | Current Price | Launch Price | Plan ID |
|------|--------------|--------------|---------|
| Awakened | $149/month | $197/mo at launch | `P-2SA65600MT088594TNGLTFKY` |
| Partnered | $499/month | $579/mo at launch | `P-3VH43554A66001716NGLTFKY` |
| Unified | $999/month | $1,089/mo at launch | `P-43A28944XN5237411NGLTFLA` |

### Special Pricing Variants

| Page | Tier | Price | Notes |
|------|------|-------|-------|
| `/insiders/awakened/` | Awakened | $74.50/month | Insider discount (half of $149) |

### JS PRICES Object (in PayPal SDK integration)

```javascript
var PRICES = {
    Awakened:  '149.00',
    Bonded:    '299.00',   // Legacy tier -- not currently sold on live pages
    Partnered: '499.00',
    Unified:   '999.00',
};
```

### Tier-to-Price Fallback (Server Side)

In `purebrain_log_server.py`, when PayPal API returns no amount:

```python
_TIER_PRICES = {
    'awakened':  '149.00',
    'bonded':    '299.00',
    'partnered': '499.00',
    'unified':   '999.00',
}
```

---

## 4. PayPal Integration

### Credentials

- **Live Client ID**: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
- **Business Email**: `support@puremarketing.ai`
- **Sandbox credentials**: In `.env` as `PAYPAL_SANDBOX_CLIENT_ID` and `PAYPAL_SANDBOX_SECRET`

### SDK Integration

- Approach A (DEFAULT): PayPal JS SDK Smart Buttons -- in-page popup/modal
- Approach B (fallback): PayPal Form POST in centered popup window

### Payment Flow

1. User clicks tier CTA button (e.g., `#proCta`)
2. PayPal overlay modal opens (`#pb-paypal-overlay`)
3. SDK renders Smart Buttons in `#pb-paypal-buttons-container`
4. For subscription tiers: `createSubscription` with `PLAN_IDS[tier]`
5. For one-time payment: `createOrder` with `PRICES[tier]`
6. `onApprove` callback fires after successful payment
7. Server-side verification: POST to `https://api.purebrain.ai/api/verify-payment`
8. On success: `handlePaymentSuccess()` triggers the post-payment chatbox flow

### Return/Cancel URLs

```javascript
var RETURN_URL = 'https://purebrain.ai/awakened/?payment=success';
var CANCEL_URL = 'https://purebrain.ai/awakened/';
```

---

## 5. Chatbox Flow (Post-Payment)

### Version: v4.7 (Witness Production)

The post-payment chatbox is the naming ceremony. It collects critical data.

### Flow Steps

1. **Payment verified** -- `handlePaymentSuccess()` triggers
2. **Chatbox appears** -- AI assistant guides customer through questions
3. **Step 1: Name** -- "What is your full name?"
4. **Step 2: AI Naming** -- Customer NAMES their AI (CONSTITUTIONAL: naming BEFORE payment completion acknowledgment)
5. **Step 3: Email** -- "What email should [AI name] use to reach you?"
6. **Step 3 TRIGGER**: On email collection, `fireSeed()` fires IMMEDIATELY
7. **Step 4: Company** (optional) -- "Are you working within a company or organization?"
8. **Step 5: Role** (optional) -- "What is your role?"
9. **Step 6: Primary Goal** (optional) -- "What is your primary goal for your AI?"
10. **Step 7: Learn More** (optional) -- Additional questions
11. **Step 8: Portal button** -- On click, `fireSeedAddendum()` fires

### Data Object (payTestData)

```javascript
payTestData = {
    sessionUuid: '...',      // Generated at payment time
    aiName: '...',           // From naming ceremony
    name: '...',             // Customer full name
    email: '...',            // Email from chatbox (may differ from PayPal)
    tier: '...',             // Awakened|Partnered|Unified
    tierPaid: '...',         // Tier that was paid for
    orderId: '...',          // PayPal order/subscription ID
    company: '...',          // Optional
    role: '...',             // Optional
    primaryGoal: '...',      // Optional
    learnMoreAnswers: [],    // Optional questionnaire
    magicLink: '...',        // Populated when portal ready
    prePurchaseSessionId: '...',
    prePurchaseHistory: [],  // Pre-purchase conversation
};
```

### Key Constraint: Naming BEFORE Payment

The customer CANNOT complete the purchase flow without going through the naming ceremony. The chatbox IS the gate. Every seed MUST include the full conversation. If no conversation is found in the seed, the lookup is broken -- this is a bug, not a feature gap.

---

## 6. Seed to Witness

### Two Seed Triggers

There are TWO paths that fire seeds. They are deduplicated.

#### Trigger 1: PayPal Payment Verification (Primary)

- **When**: Immediately after `POST /api/verify-payment` succeeds
- **Where**: Background thread in `purebrain_log_server.py` (`_fire_payment_seed()`)
- **From**: `aether-aiciv@agentmail.to`
- **To**: `aiciv-seed-inbox@agentmail.to`
- **CC**: `jared@puretechnology.nyc`, `aether-aiciv@agentmail.to`, `purebrain@puremarketing.ai`
- **Dedup**: Order ID tracked in `_seeds_fired_for_orders` set (in-memory)
- **Content**: Looks up conversation from `purebrain_web_conversations.jsonl` using multi-strategy lookup:
  1. Match by `metadata.orderId` (strongest -- post-payment log arrived)
  2. Match by `session_uuid` or `metadata.sessionUuid` (links pre-payment chatbox to payment via `payTestData.sessionUuid`)
  3. For each strategy, picks the entry with the most messages
  - **2026-03-28 FIX**: Pre-payment chatbox logs now include `sessionUuid` and `aiName` at top level, so the seed can find conversations even when the post-payment log (which carries orderId) has not yet arrived due to race conditions.
  - **NON-NEGOTIABLE**: A seed MUST NEVER be sent with "not yet named" when a naming conversation exists in the logs. The multi-strategy lookup ensures conversations are always found. If all strategies fail, the seed MUST still fire (payment cannot be lost) but an alarm MUST trigger so the conversation can be manually attached. Zero tolerance for missing conversations in seeds.

#### Trigger 2: Chatbox Email Collection (Secondary)

- **When**: `fireSeed()` called in browser after email is obtained (Step 3)
- **Where**: Client-side JS POSTs to `POST /api/send-seed`
- **From**: `aether-aiciv@agentmail.to` (server-side)
- **To**: `aiciv-seed-inbox@agentmail.to`
- **Dedup**: UUID tracked in `logs/seed_sent_uuids.json` AND order-level check against `_seeds_fired_for_orders`
- **Client-side guard**: `_seedFired` boolean prevents double-call from browser

### Seed Email Format (Rich HTML -- LOCKED)

The seed is sent as a rich HTML email with structured table:

```
Subject: [emoji] SEED: [AI Name] / [Human Name] -- [Tier] ($[Amount]/month)
   (or TEST SEED for sandbox)

Body (HTML):
- Session UUID (monospace, highlighted)
- Structured table: Tier, AI Name, Human Name, Email, Order ID, Payment, Trigger, Timestamp
- Full Conversation section: color-coded rows (ASSISTANT=blue, USER=green, SYSTEM=gray)

Body (Plain text / .md):
- Same fields in markdown format
- Full conversation transcript
```

### Sandbox Detection

Seed is marked as TEST when ANY of:
- `isSandbox: true` in payload
- Order ID starts with `SANDBOX-TEST`, `E2E-`, or `test-`
- PayPal email starts with `sb-` or ends with `@personal.example.com` / `@business.example.com`
- Page URL contains `pay-test-sandbox` or `/pay-test`

Test seeds get a red banner: "THIS IS A SANDBOX TEST -- NOT A REAL CUSTOMER"

---

## 7. Seed Addendum

### Trigger

- **When**: Customer clicks the "Enter Portal" button after completing all optional questions
- **Client function**: `fireSeedAddendum()`
- **Client guard**: `_addendumFired` boolean prevents double-fire
- **Endpoint**: `POST /api/seed-addendum`

### Payload

```javascript
{
    event: 'seed-addendum',
    session_uuid: '...',
    aiName: '...',
    name: '...',
    email: '...',
    tier: '...',
    company: '...',
    role: '...',
    primaryGoal: '...',
    orderId: '...',
    learnMoreAnswers: [],
    magicLink: '...',
    prePurchaseSessionId: '...',
    naming_session_id: '...',
    name_suffix: '...',
    conversation: [/* structured post-email messages */],
    timestamp: '...',
    page_url: '...',
}
```

### Server Processing (purebrain_log_server.py /api/seed-addendum)

- Sends addendum email via AgentMail to `aiciv-seed-inbox@agentmail.to`
- Includes all post-email questionnaire data
- UUID matches the original seed UUID

---

## 8. Magic Link Flow

### Pipeline

```
Payment verified
  |
  v
Seed fired to Witness (aiciv-seed-inbox@agentmail.to)
  |
  v
Witness allocates container + builds customer portal
  |
  v
Witness sends MAGIC LINK email to aether-aiciv@agentmail.to
  |
  v
agentmail_monitor.py receives email, parses fields
  |
  v
Stores in .magic-links.json keyed by:
  1. Session UUID (primary key)
  2. email:{human_email} (fallback key)
  |
  v
Rewrites domain: .ai-civ.com -> .app.purebrain.ai
  |
  v
Welcome email(s) sent (see Section 9)
  |
  v
Page polls GET /api/magic-link/{uuid}?email={email}
  |
  v
Returns {"status": "ready", "magic_link": "https://..."} when available
```

### UUID Consistency (CONSTITUTIONAL)

ONE UUID flows through the entire pipeline:

1. **Generated on page**: `payTestData.sessionUuid`
2. **Sent in verify-payment**: `data.sessionUuid`
3. **Stored for PayPal email lookup**: `logs/payer_emails_by_uuid.json`
4. **Sent in fireSeed()**: `seedPayload.session_uuid`
5. **Used in seed email**: Session UUID field
6. **Witness stores magic link**: Keyed by this UUID
7. **Page polls**: `GET /api/magic-link/{this-uuid}`

If UUIDs mismatch at any point, the pipeline breaks. Fallback lookup by email exists but is a safety net, not the design.

### Magic Link Endpoint Fallbacks

`GET /api/magic-link/{uuid}?email={email}` checks in order:

1. Direct UUID key lookup in `.magic-links.json`
2. `email:{email}` key lookup
3. Scan all entries for matching `human_email`
4. Cross-reference `clients.db` for recent activity (last 30 minutes)

### Magic Link Email Format (from Witness)

```
Subject: MAGIC LINK -- [AI Name] for [Human Name]
Body:
    AI Name: ...
    Human Name: ...
    Email: ...
    UUID: ...
    Container: ...
    Magic Link: https://[container].ai-civ.com/portal?token=...
```

### Domain Rewrite

All `.ai-civ.com` domains are rewritten to `.app.purebrain.ai`:
```
https://aria-lucas.ai-civ.com/portal?token=xxx
  becomes
https://aria-lucas.app.purebrain.ai/portal?token=xxx
```

---

## 9. Welcome Emails (Dual Send)

### The Problem

The PayPal payer email (Email A) may differ from the chatbox email (Email B). Both addresses need the welcome email.

### Implementation (in agentmail_monitor.py handle_magic_link_email)

1. **Email B** (chatbox email): Comes from the Witness magic link email `human_email` field
2. **Email A** (PayPal email): Looked up from `logs/payer_emails_by_uuid.json` (stored at payment verification time)
3. **Dedup**: Both emails normalized to lowercase and added to a set
4. **Filter sandbox**: `sb-*` prefix and `example.com` domain filtered out
5. **Send**: Welcome email sent to each unique address in the set

### Logic

```
IF Email A != Email B:
    Send welcome email to BOTH (dual send)
IF Email A == Email B:
    Send ONE welcome email (dedup via set)
IF Email A is sandbox:
    Skip Email A, send only to Email B (if valid)
```

### Welcome Email Properties

- **From**: `Aether | PureBrain <purebrain@puremarketing.ai>`
- **BCC**: `jared@puretechnology.nyc` (NOT CC -- CONSTITUTIONAL)
- **Reply-To**: `support@puremarketing.ai`
- **Subject**: `Your AI [AI Name] is Ready -- Enter Your Brain Stream`
- **SMTP**: Google SMTP (`smtp.gmail.com:587`)
- **Credentials**: `SMTP_USER` (purebrain@puremarketing.ai) + `GOOGLE_APP_PASSWORD` from `.env`

### Email Template

- **Primary**: `/tmp/welcome-email-template.html`
- **Fallback**: `/tmp/magic-link-email-template.html`
- **Inline fallback**: Generated HTML if no template file exists

### Template Variables

```
{{HUMAN_FIRST_NAME}} -- First name from Witness data
{{CIV_NAME}}         -- AI name chosen by customer
{{MAGIC_LINK}}       -- Rewritten .app.purebrain.ai link
```

### Email Design Requirements

- Dark background: `#080a12`
- Inline `bgcolor` attributes on all elements (email clients strip `<style>` tags)
- NO Cloudflare scripts
- NO WordPress artifacts
- BCC jared@puretechnology.nyc (NEVER CC)

---

## 10. Portal Access

### After Welcome Email

1. Customer receives welcome email with magic link
2. Click magic link -> directed to their personal portal at `[container].app.purebrain.ai`
3. Portal is a unique container/instance allocated by Witness

### Portal Button (Post-Payment Chatbox)

The chatbox polls `GET /api/magic-link/{uuid}?email={email}` every few seconds:
- While pending: Shows "Setting up your portal..." message
- When ready: Portal button becomes clickable, `fireSeedAddendum()` fires on click

---

## 11. Constitutional Rules

These rules are NON-NEGOTIABLE. Violation is a deployment blocker.

### Rule 1: Seed Flow MUST NEVER DEVIATE

The seed email format, recipients, and trigger logic are LOCKED. This is how Pure Technology gets paid and how customers receive their AI. Any change requires explicit Jared approval.

### Rule 2: Naming BEFORE Payment -- ALWAYS

Customers CANNOT pay without naming their AI. Every seed MUST include the full naming conversation. If a seed arrives without conversation data, the lookup pipeline is broken -- fix the bug immediately.

### Rule 3: ONE UUID Through Entire Pipeline

The session UUID generated at payment time MUST be the same UUID used in:
- Seed email
- Magic link storage
- Magic link polling
- Welcome email lookup

UUID mismatch = pipeline failure.

### Rule 4: 8 Payment Page Performance Checks

Run `tools/verify-payment-pages.sh` before EVERY deploy. Must pass 100%.

The 8 checks per page:
1. No GoDaddy/WordPress tracking scripts (`_trfq`, `_trfd`, `scc-c2`, `tccl-tti`, `secureserver`, `wpaas`)
2. PayPal preconnect/dns-prefetch present
3. Canvas pause on pricing reveal (comment marker: "Pause canvas for performance when pricing")
4. Video pause on pricing reveal (`bgVideo.pause`)
5. Seed capture (`_seedFired` + `send-seed` references)
6. Addendum capture (`fireSeedAddendum` + `seed-addendum` references)
7. No excessive WP scripts (max 5 `wp-content/*.js` references)
8. No excessive WP CSS (max 5 `wp-content/*.css` / `wp-includes/*.css` references)

### Rule 5: Canvas + Video Pause on Pricing Reveal

When the pricing section becomes visible, background canvas animations and video must pause. This prevents GPU/CPU contention during the critical payment moment.

### Rule 6: NO WordPress Scripts/CSS on Payment Pages

Zero tolerance for active WordPress runtime scripts. Legacy static references (up to 5) are tolerated but should be cleaned over time.

### Rule 7: Never Modify Live Payment Pages Overnight

No autonomous/nightly agent may modify live payment pages. Sandbox pages only.

### Rule 8: Sandbox Email Auto-Filtering

Emails matching `sb-*`, `@personal.example.com`, or `@business.example.com` are automatically detected as sandbox and:
- Spots counter NOT incremented
- Seed marked as TEST
- Welcome email skipped for that address

---

## 12. Server Infrastructure

### purebrain_log_server.py

- **Location**: `tools/purebrain_log_server.py` (2,589 lines)
- **Runtime**: Flask with SSL
- **Server IP**: `89.167.19.20`
- **Domain**: `api.purebrain.ai` (points to this server)

**Key Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/log-conversation` | POST | Log chatbox conversations to JSONL |
| `/api/verify-payment` | POST | Verify PayPal payment, fire seed, store payer email |
| `/api/send-seed` | POST | Fire seed email (chatbox trigger, deduplicated) |
| `/api/seed-addendum` | POST | Send questionnaire data after seed |
| `/api/magic-link/{uuid}` | GET | Poll for magic link availability |
| `/api/pipeline-health` | GET | Health check for entire pipeline |
| `/api/health` | GET | Basic health check |
| `/api/stats` | GET | Conversation statistics |

### agentmail_monitor.py

- **Location**: `tools/agentmail_monitor.py` (687 lines)
- **Runtime**: Persistent daemon, polls every 30 seconds
- **Inbox**: `aether-aiciv@agentmail.to`
- **State file**: `memories/agents/email-monitor/agentmail_state.json`

**Key Responsibilities**:
1. Monitor inbox for new messages
2. Detect MAGIC LINK emails from Witness
3. Parse magic link fields (AI name, human name, email, UUID, container, link)
4. Rewrite `.ai-civ.com` to `.app.purebrain.ai`
5. Store in `.magic-links.json` keyed by UUID AND email
6. Look up PayPal payer email from `logs/payer_emails_by_uuid.json`
7. Send welcome email(s) to both addresses if different
8. Notify Jared on Telegram

### Key Data Files

| File | Purpose |
|------|---------|
| `logs/purebrain_web_conversations.jsonl` | All chatbox conversations |
| `logs/purebrain_payments.jsonl` | All payment verifications |
| `logs/seed_sent_uuids.json` | UUIDs of seeds already sent (dedup) |
| `logs/payer_emails_by_uuid.json` | PayPal email -> UUID mapping for dual-send |
| `logs/spots_state.json` | Invitation spots counter |
| `.magic-links.json` | Magic links received from Witness |
| `/tmp/welcome-email-template.html` | Welcome email HTML template |

### AgentMail Inboxes

| Inbox | Purpose |
|-------|---------|
| `aether-aiciv@agentmail.to` | Onboarding monitor, seed sending |
| `aiciv-seed-inbox@agentmail.to` | Witness receives seeds here |
| `witness-aiciv@agentmail.to` | Witness sends magic links from here |

---

## 13. Verification Script

**File**: `tools/verify-payment-pages.sh`

**Usage**:
```bash
bash tools/verify-payment-pages.sh [optional-deploy-dir]
# Default: exports/cf-pages-deploy
```

**Pages Checked**: live, awakened, partnered, unified, pay-test-sandbox-3, pay-test-sandbox-5, insiders, insiders/awakened

**Exit Codes**:
- `0` -- All pages clean, safe to deploy
- `1` -- One or more pages have failures, DO NOT DEPLOY

**Run this before EVERY deploy. No exceptions.**

---

## 14. End-to-End Flow Diagram

```
CUSTOMER                     BROWSER                      API SERVER                   AGENTMAIL/WITNESS
   |                            |                              |                              |
   | visits /awakened/          |                              |                              |
   |--------------------------->|                              |                              |
   |                            | Checkbox pre-checked         |                              |
   |                            | onConsentChange(true)------->| POST /api/log-conversation   |
   |                            | CTAs unlocked (orange)       |   (consent logged)           |
   |                            |                              |                              |
   | Clicks tier CTA            |                              |                              |
   |--------------------------->|                              |                              |
   |                            | PayPal overlay opens         |                              |
   |                            | SDK Smart Buttons render     |                              |
   |                            |                              |                              |
   | Completes PayPal payment   |                              |                              |
   |--------------------------->|                              |                              |
   |                            | onApprove fires              |                              |
   |                            |----------------------------->| POST /api/verify-payment      |
   |                            |                              |   - Logs payment              |
   |                            |                              |   - Stores payer email by UUID|
   |                            |                              |   - Fires seed (bg thread)--->| SEED to aiciv-seed-inbox
   |                            |                              |   - Updates clients.db        |   CC: jared, aether, purebrain
   |                            |                              |                              |
   |                            | handlePaymentSuccess()       |                              |
   |                            | Post-payment chatbox opens   |                              |
   |                            |                              |                              |
   | Names AI ("Aria")          |                              |                              |
   |--------------------------->| payTestData.aiName = "Aria"  |                              |
   |                            |                              |                              |
   | Provides full name         |                              |                              |
   |--------------------------->| payTestData.name = "..."     |                              |
   |                            |                              |                              |
   | Provides email             |                              |                              |
   |--------------------------->| payTestData.email = "..."    |                              |
   |                            | fireSeed()                   |                              |
   |                            |----------------------------->| POST /api/send-seed           |
   |                            |                              |   (deduplicated if payment    |
   |                            |                              |    seed already fired)        |
   |                            |                              |                              |
   |                            |              Witness processes seed...                       |
   |                            |              Allocates container...                          |
   |                            |              Sends MAGIC LINK email...                       |
   |                            |                              |                              |
   |                            |                              |  agentmail_monitor.py detects |
   |                            |                              |  MAGIC LINK email             |
   |                            |                              |  - Parses fields              |
   |                            |                              |  - Rewrites domain            |
   |                            |                              |  - Stores in .magic-links.json|
   |                            |                              |  - Looks up PayPal email      |
   |                            |                              |  - Sends welcome email(s)     |
   |                            |                              |  - Notifies Jared on Telegram |
   |                            |                              |                              |
   |                            | Polls GET /api/magic-link/   |                              |
   |                            |   {uuid}?email={email}       |                              |
   |                            |<-----------------------------| {"status": "ready",           |
   |                            |                              |  "magic_link": "https://..."}|
   |                            |                              |                              |
   | Completes optional Qs      |                              |                              |
   | Clicks "Enter Portal"      |                              |                              |
   |--------------------------->| fireSeedAddendum()           |                              |
   |                            |----------------------------->| POST /api/seed-addendum       |
   |                            |                              |   (questionnaire data)        |
   |                            |                              |                              |
   | Redirected to portal       |                              |                              |
   |--------------------------->| [container].app.purebrain.ai |                              |
   |                            |                              |                              |
```

---

## Appendix: What Changed (2026-03-28)

This spec was written from scratch by reading actual implementation code:
- `tools/purebrain_log_server.py` (2,589 lines) -- all API endpoints
- `tools/agentmail_monitor.py` (687 lines) -- magic link + welcome email pipeline
- `tools/verify-payment-pages.sh` -- constitutional verification script
- `exports/cf-pages-deploy/*/index.html` -- all payment page HTML

Key findings documented for the first time:
1. Dual-send welcome email logic (PayPal email vs chatbox email)
2. Complete magic link fallback chain (4 levels)
3. Two seed trigger paths with deduplication logic
4. Full list of pages with active vs legacy payment flows
5. Payer email storage by UUID for cross-reference at welcome email time

---

**END OF DOCUMENT**
