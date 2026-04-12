# ONBOARDING SPECIFICATION -- DEFINITIVE

**Status**: CONSTITUTIONAL -- Single Source of Truth
**Last Updated**: 2026-04-01
**Overwrites**: All previous onboarding docs, specs, and fragments
**Author**: dept-systems-technology
**Rule**: This document is non-negotiable. Any agent modifying the onboarding pipeline MUST read this first.

---

## Table of Contents

1. [Landing Pages Inventory](#1-landing-pages-inventory)
2. [Pre-Payment Naming Ceremony](#2-pre-payment-naming-ceremony)
3. [Consent Gate](#3-consent-gate)
4. [Payment Tiers and Pricing](#4-payment-tiers-and-pricing)
5. [PayPal Integration](#5-paypal-integration)
6. [Post-Payment: Seed + Redirect](#6-post-payment-seed--redirect)
7. [Thank-You Page](#7-thank-you-page)
8. [Seed to Witness](#8-seed-to-witness)
9. [Magic Link Flow](#9-magic-link-flow)
10. [Welcome Emails (Auto via agentmail_monitor)](#10-welcome-emails-auto-via-agentmail_monitor)
11. [Portal Access](#11-portal-access)
12. [Constitutional Rules](#12-constitutional-rules)
13. [Server Infrastructure](#13-server-infrastructure)
14. [Verification Script](#14-verification-script)
15. [End-to-End Flow Diagram](#15-end-to-end-flow-diagram)
16. [What Was Removed](#16-what-was-removed)

---

## 1. Landing Pages Inventory

All pages live under `exports/cf-pages-deploy/` and deploy to Cloudflare Pages (`purebrain-staging`).

### LIVE Payment Pages (Real PayPal, Real Subscriptions)

These pages accept real money. Modifications require explicit Jared approval.

| Path | Tier | Pricing Shown | PayPal Mode | Seed |
|------|------|---------------|-------------|------|
| `/` (homepage) | All 3 tiers | $149 / $499 / $999 | LIVE subscription | Yes |
| `/live/` | All 3 tiers | $149 / $499 / $999 | LIVE subscription | Yes |
| `/awakened/` | Awakened | $149 | LIVE subscription | Yes |
| `/partnered/` | Partnered | $499 | LIVE subscription | Yes |
| `/unified/` | Unified | $999 | LIVE subscription | Yes |
| `/insiders/` | Awakened | $149 | LIVE subscription | Yes |
| `/insiders/awakened/` | Awakened | $74.50 (insider price) | LIVE subscription | Yes |

### Sandbox / Test Pages

These pages use sandbox PayPal credentials. Used for E2E testing.

| Path | Purpose | PayPal Mode | Seed |
|------|---------|-------------|------|
| `/home-test-sandbox/` | Primary sandbox testing | Sandbox subscription | Yes |
| `/pay-test-sandbox-3/` | Sandbox testing | Sandbox subscription | Yes |
| `/pay-test-sandbox-5/` | Latest sandbox testing | Sandbox subscription | Yes |

### Test Pages (LIVE PayPal, low amounts)

| Path | Purpose | PayPal Mode | Seed |
|------|---------|-------------|------|
| `/home-test/` | Original test page | LIVE | Yes |
| `/home-test-live-1/` | $1 one-time test | LIVE one-time | Yes |

### Supporting Pages

| Path | Purpose |
|------|---------|
| `/thank-you/` | Post-payment redirect destination with status + magic link polling |

### Pages Checked by verify-payment-pages.sh

```
homepage, live, home-test, home-test-sandbox, awakened, partnered, unified,
pay-test-sandbox-3, pay-test-sandbox-5, insiders, insiders/awakened, thank-you
```

---

## 2. Pre-Payment Naming Ceremony

### Location

Inline on each payment page, BEFORE the pricing section is revealed.

### Flow

1. Visitor arrives at the page
2. Chat interface appears with Claude-powered AI conversation
3. AI guides the visitor through naming their AI partner
4. Visitor provides:
   - Their full name
   - A name for their AI partner (the "naming ceremony")
   - Their email address
   - (Optional) Company, role, primary goal
5. Conversation is stored in `window._pbState.conversationHistory`
6. All conversation data is logged to `POST /api/log-conversation`

### Key Constraint: Naming BEFORE Payment

The customer names their AI BEFORE they ever see pricing or pay. The naming ceremony builds emotional investment. Every seed MUST include the full naming conversation. If a seed arrives without conversation data, the lookup pipeline is broken -- fix the bug immediately.

### Data Object (payTestData)

```javascript
payTestData = {
    sessionUuid: '...',      // Generated on page load
    aiName: '...',           // From naming ceremony
    name: '...',             // Customer full name
    email: '...',            // Email from chatbox
    tier: '...',             // Awakened|Partnered|Unified
    tierPaid: '...',         // Tier that was paid for
    orderId: '...',          // PayPal order/subscription ID
    company: '...',          // Optional
    role: '...',             // Optional
    primaryGoal: '...',      // Optional
    prePurchaseSessionId: '...',
    prePurchaseHistory: [],  // Full pre-purchase conversation
};
```

---

## 3. Consent Gate

### Implementation Location

Inline `<script>` block at the bottom of each payment page, wrapped in an IIFE.

### Behavior

1. **Checkbox HTML**: `<input type="checkbox" id="pb-consent-check" class="pb-consent-checkbox" checked />`
2. **Default state**: Checkbox starts CHECKED
3. **On page load**: `DOMContentLoaded` fires `onConsentChange(true)` because checkbox is pre-checked
4. **onConsentChange(true)**:
   - Generates a consent UUID (v4 format)
   - Stores `{uuid, timestamp}` in `sessionStorage` under key `pb_consent_v1`
   - Logs consent to conversation history
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
- **Locked (consent revoked)**: Greyed-out buttons, `aria-disabled="true"`, pointer events blocked

### CSS Classes

```css
.pb-consent-wrapper { /* container */ }
.pb-consent-checkbox { /* the checkbox input */ }
.pb-consent-label { /* label text with links to Terms/Privacy */ }
.pb-cta-locked { /* greyed out, non-interactive */ }
.pb-cta-unlocked { /* bright orange, interactive */ }
```

---

## 4. Payment Tiers and Pricing

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

### JS PRICES Object

```javascript
var PRICES = {
    Awakened:  '149.00',
    Bonded:    '299.00',   // Legacy tier -- not currently sold
    Partnered: '499.00',
    Unified:   '999.00',
};
```

---

## 5. PayPal Integration

### Credentials

- **Live Client ID**: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
- **Business Email**: `support@puremarketing.ai`
- **Sandbox credentials**: In `.env` as `PAYPAL_SANDBOX_CLIENT_ID` and `PAYPAL_SANDBOX_SECRET`

### SDK Integration

PayPal JS SDK Smart Buttons -- in-page popup/modal.

### Payment Flow

1. User clicks tier CTA button (e.g., `#proCta`)
2. PayPal overlay modal opens (`#pb-paypal-overlay`)
3. SDK renders Smart Buttons in `#pb-paypal-buttons-container`
4. For subscription tiers: `createSubscription` with `PLAN_IDS[tier]`
5. For one-time payment: `createOrder` with `PRICES[tier]`
6. `onApprove` callback fires after successful payment
7. Server-side verification: POST to `https://api.purebrain.ai/api/verify-payment`
8. On success: `onPaymentComplete` fires (seed + redirect -- see Section 6)

---

## 6. Post-Payment: Seed + Redirect

### What Happens After Payment (onPaymentComplete)

This is the critical post-payment sequence. There is NO post-payment chatbox. The flow is:

1. **Payment verified** -- `onApprove` receives success from `/api/verify-payment`
2. **Seed fires** -- `fireSeed()` sends seed to Witness via `POST /api/send-seed`
   - Includes: AI name, human name, email, tier, order ID, full conversation
   - Guard: `_seedFired` boolean prevents double-fire
3. **300ms delay** -- allows seed request to complete
4. **Redirect to /thank-you/** -- browser navigates to:
   ```
   /thank-you/?aiName={encodeURIComponent(aiName)}&name={encodeURIComponent(name)}&email={encodeURIComponent(email)}&tier={tier}
   ```

### Key Points

- Seed fires BEFORE redirect (not after)
- The redirect carries all personalization data as URL parameters
- There is NO post-payment chatbox overlay
- There is NO post-payment questionnaire
- There is NO magic link button on the payment page
- The customer sees the /thank-you/ page immediately after payment

---

## 7. Thank-You Page

### Location

`exports/cf-pages-deploy/thank-you/index.html`

### URL Parameters (received from redirect)

```
/thank-you/?aiName=Aria&name=John%20Smith&email=john@example.com&tier=Awakened
```

### What the Customer Sees

A personalized status page with a checklist that updates in real-time:

1. **"Payment confirmed"** -- shows green check immediately
2. **"[AI Name] is being configured"** -- animating spinner, goes green when magic link arrives
3. **"Welcome email on its way"** -- animating spinner, goes green when magic link arrives
4. **"Check your inbox at [email]"** -- shows their email address
5. **Hint text**: "Or, when the button appears below, you can just click it."

### Magic Link Polling

The thank-you page polls the magic link API every 5 seconds:

```javascript
GET https://api.purebrain.ai/api/magic-link/{sessionUuid}?email={email}
```

**Responses**:
- `{"status": "pending"}` -- keep polling, show spinners
- `{"status": "ready", "magic_link": "https://..."}` -- update checklist, show button

### When Magic Link Arrives

1. All checklist items go green
2. Portal hint text disappears
3. **"Enter [AI Name]'s Brain Stream"** button appears
4. Button links directly to the magic link URL

### Typical Wait Time

2-5 minutes for Witness to process the seed, create the container, and send the magic link.

---

## 8. Seed to Witness

### Two Seed Triggers (Deduplicated)

#### Trigger 1: PayPal Payment Verification (Server-side, Primary)

- **When**: Immediately after `POST /api/verify-payment` succeeds
- **Where**: Background thread in `purebrain_log_server.py` (`_fire_payment_seed()`)
- **From**: `aether-aiciv@agentmail.to`
- **To**: `aiciv-seed-inbox@agentmail.to`
- **CC**: `jared@puretechnology.nyc`, `aether-aiciv@agentmail.to`, `purebrain@puremarketing.ai`
- **Dedup**: Order ID tracked in `_seeds_fired_for_orders` set (in-memory)
- **Content**: Looks up conversation from `purebrain_web_conversations.jsonl` using 5-strategy fallback:
  1. **S1 - orderId**: Match by `metadata.orderId`
  2. **S2 - sessionUuid**: Match by `session_uuid` or `metadata.sessionUuid`
  3. **S3 - payerEmail**: Search all message content for PayPal payer email
  4. **S4 - recentConv**: Most recent conversation on payment page within 30 min with >5 messages
  5. **S5 - payerName**: Search AI responses for payer first name (>= 3 chars)

#### Trigger 2: Client-side Seed (Browser, Secondary)

- **When**: `fireSeed()` called in browser inside `onPaymentComplete` flow
- **Where**: Client-side JS POSTs to `POST /api/send-seed`
- **Dedup**: UUID tracked in `logs/seed_sent_uuids.json` AND order-level check
- **Client-side guard**: `_seedFired` boolean prevents double-call

### Seed Email Format (Rich HTML -- LOCKED)

```
Subject: [emoji] SEED: [AI Name] / [Human Name] -- [Tier] ($[Amount]/month)
   (or TEST SEED for sandbox)

Body (HTML):
- Session UUID (monospace, highlighted)
- Structured table: Tier, AI Name, Human Name, Email, Order ID, Payment, Trigger, Timestamp
- Full Conversation section: color-coded rows (ASSISTANT=blue, USER=green, SYSTEM=gray)
```

### Sandbox Detection

Seed is marked as TEST when ANY of:
- `isSandbox: true` in payload
- Order ID starts with `SANDBOX-TEST`, `E2E-`, or `test-`
- PayPal email starts with `sb-` or ends with `@personal.example.com` / `@business.example.com`
- Page URL contains `pay-test-sandbox` or `/pay-test`

Test seeds get a red banner: "THIS IS A SANDBOX TEST -- NOT A REAL CUSTOMER"

---

## 9. Magic Link Flow

### Pipeline

```
Payment verified
  |
  v
Seed fired to Witness (aiciv-seed-inbox@agentmail.to)
  |
  v
Witness allocates container + builds customer portal (2-5 minutes)
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
Auto welcome email(s) sent (see Section 10)
  |
  v
Thank-you page polls GET /api/magic-link/{uuid}?email={email}
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
7. **Thank-you page polls**: `GET /api/magic-link/{this-uuid}`

If UUIDs mismatch at any point, the pipeline breaks.

### Magic Link Endpoint Fallbacks

`GET /api/magic-link/{uuid}?email={email}` checks in order:

1. Direct UUID key lookup in `.magic-links.json`
2. `email:{email}` key lookup
3. Scan all entries for matching `human_email`
4. Cross-reference `clients.db` for recent activity (last 30 minutes)

### Domain Rewrite

All `.ai-civ.com` domains are rewritten to `.app.purebrain.ai`:
```
https://aria-lucas.ai-civ.com/portal?token=xxx
  becomes
https://aria-lucas.app.purebrain.ai/portal?token=xxx
```

---

## 10. Welcome Emails (Auto via agentmail_monitor)

### How It Works

Welcome emails are sent AUTOMATICALLY by `agentmail_monitor.py` when it detects a magic link email from Witness. There is no manual trigger.

### Dual-Send Logic

The PayPal payer email (Email A) may differ from the chatbox email (Email B). Both addresses need the welcome email.

1. **Email B** (chatbox email): Comes from the Witness magic link email `human_email` field
2. **Email A** (PayPal email): Looked up from `logs/payer_emails_by_uuid.json`
3. **Dedup**: Both emails normalized to lowercase and added to a set
4. **Filter sandbox**: `sb-*` prefix and `example.com` domain filtered out
5. **Sandbox bypass**: `sb-*@example.com` emails redirect to `jared@puretechnology.nyc`
6. **Send**: Welcome email sent to each unique address in the set

### Welcome Email Properties

- **From**: `Aether | PureBrain <purebrain@puremarketing.ai>`
- **BCC**: `jared@puretechnology.nyc` (NOT CC -- CONSTITUTIONAL)
- **Reply-To**: `support@puremarketing.ai`
- **Subject**: `Your AI [AI Name] is Ready -- Enter Your Brain Stream`
- **SMTP**: Google SMTP (`smtp.gmail.com:587`)
- **Credentials**: `SMTP_USER` (purebrain@puremarketing.ai) + `GOOGLE_APP_PASSWORD` from `.env`

### Email Design Requirements

- Dark background: `#080a12`
- Inline `bgcolor` attributes on all elements (email clients strip `<style>` tags)
- NO Cloudflare scripts
- NO WordPress artifacts
- BCC jared@puretechnology.nyc (NEVER CC)

### Template Variables

```
{{HUMAN_FIRST_NAME}} -- First name from Witness data
{{CIV_NAME}}         -- AI name chosen by customer
{{MAGIC_LINK}}       -- Rewritten .app.purebrain.ai link
```

---

## 11. Portal Access

### After Welcome Email

1. Customer receives welcome email with magic link
2. Click magic link -> directed to their personal portal at `[container].app.purebrain.ai`
3. Portal is a unique container/instance allocated by Witness

### From Thank-You Page

1. Thank-you page detects magic link is ready (polling succeeds)
2. "Enter [AI Name]'s Brain Stream" button appears
3. Customer clicks button -> directed to portal via magic link

Either path (email or thank-you page button) leads to the same portal.

---

## 12. Constitutional Rules

These rules are NON-NEGOTIABLE. Violation is a deployment blocker.

### Rule 1: Seed Flow MUST NEVER DEVIATE

The seed email format, recipients, and trigger logic are LOCKED. This is how Pure Technology gets paid and how customers receive their AI. Any change requires explicit Jared approval.

### Rule 2: Naming BEFORE Payment -- ALWAYS

Customers name their AI BEFORE they pay. The naming ceremony builds emotional investment. Every seed MUST include the full naming conversation. If a seed arrives without conversation data, the lookup pipeline is broken -- fix immediately.

### Rule 3: ONE UUID Through Entire Pipeline

The session UUID generated at page load MUST be the same UUID used in seed, magic link storage, magic link polling, and welcome email lookup. UUID mismatch = pipeline failure.

### Rule 4: Seed BEFORE Redirect

In the `onPaymentComplete` flow, `fireSeed()` MUST fire BEFORE the browser redirects to `/thank-you/`. A 300ms delay ensures the seed request initiates before navigation.

### Rule 5: No Post-Payment Chatbox

There is NO post-payment chatbox overlay. The old chatbox had a black screen bug and has been replaced with the /thank-you/ redirect flow. Any code referencing `launchPostPaymentFlow`, `_postPaymentLaunched`, or `postPaymentOverlay` must be removed.

### Rule 6: Canvas + Video Pause on Pricing Reveal

When the pricing section becomes visible, background canvas animations and video must pause. This prevents GPU/CPU contention during the critical payment moment.

### Rule 7: NO WordPress Scripts/CSS on Payment Pages

Zero tolerance for active WordPress runtime scripts. Legacy static references (up to 5) are tolerated but should be cleaned over time.

### Rule 8: Never Modify Live Payment Pages Overnight

No autonomous/nightly agent may modify live payment pages. Sandbox pages only.

### Rule 9: Sandbox Email Auto-Filtering

Emails matching `sb-*`, `@personal.example.com`, or `@business.example.com` are automatically detected as sandbox. Sandbox emails bypass to `jared@puretechnology.nyc`.

### Rule 10: Thank-You Page Must Exist

The `/thank-you/index.html` page MUST exist in the deploy directory. It MUST parse URL parameters and poll for magic links. Without it, customers see nothing after payment.

---

## 13. Server Infrastructure

### purebrain_log_server.py

- **Location**: `tools/purebrain_log_server.py`
- **Runtime**: Flask with SSL
- **Server IP**: `89.167.19.20`
- **Domain**: `api.purebrain.ai`

**Key Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/log-conversation` | POST | Log chatbox conversations to JSONL |
| `/api/verify-payment` | POST | Verify PayPal payment, fire seed, store payer email |
| `/api/send-seed` | POST | Fire seed email (client-side trigger, deduplicated) |
| `/api/magic-link/{uuid}` | GET | Poll for magic link availability |
| `/api/pipeline-health` | GET | Health check for entire pipeline |
| `/api/health` | GET | Basic health check |
| `/api/stats` | GET | Conversation statistics |

### agentmail_monitor.py

- **Location**: `tools/agentmail_monitor.py`
- **Runtime**: Persistent daemon, polls every 30 seconds
- **Inbox**: `aether-aiciv@agentmail.to`

**Key Responsibilities**:
1. Monitor inbox for new messages
2. Detect MAGIC LINK emails from Witness
3. Parse magic link fields (AI name, human name, email, UUID, container, link)
4. Rewrite `.ai-civ.com` to `.app.purebrain.ai`
5. Store in `.magic-links.json` keyed by UUID AND email
6. Look up PayPal payer email from `logs/payer_emails_by_uuid.json`
7. Send welcome email(s) to both addresses if different
8. Handle sandbox email bypass (sb-* -> jared@puretechnology.nyc)

### Key Data Files

| File | Purpose |
|------|---------|
| `logs/purebrain_web_conversations.jsonl` | All chatbox conversations |
| `logs/purebrain_payments.jsonl` | All payment verifications |
| `logs/seed_sent_uuids.json` | UUIDs of seeds already sent (dedup) |
| `logs/payer_emails_by_uuid.json` | PayPal email -> UUID mapping for dual-send |
| `logs/spots_state.json` | Invitation spots counter |
| `.magic-links.json` | Magic links received from Witness |

### AgentMail Inboxes

| Inbox | Purpose |
|-------|---------|
| `aether-aiciv@agentmail.to` | Onboarding monitor, seed sending |
| `aiciv-seed-inbox@agentmail.to` | Witness receives seeds here |
| `witness-aiciv@agentmail.to` | Witness sends magic links from here |

---

## 14. Verification Script

**File**: `tools/verify-payment-pages.sh`

**Usage**:
```bash
bash tools/verify-payment-pages.sh [optional-deploy-dir]
# Default: exports/cf-pages-deploy
```

**Per-Page Checks (10 checks)**:
1. No GoDaddy/WordPress tracking
2. PayPal preconnect present
3. Canvas pause on pricing reveal
4. Video pause on pricing reveal
5. Seed capture references
6. Thank-you redirect present
7. Email parameter in redirect URL
8. No post-payment chatbox code (must be ABSENT)
9. No excessive WP scripts (max 5)
10. No excessive WP CSS (max 5)

**Thank-You Page Checks (3 checks)**:
1. Magic link polling present
2. URL parameter parsing present
3. Personalized status display present

**Exit Codes**:
- `0` -- All pages clean, safe to deploy
- `1` -- One or more pages have failures, DO NOT DEPLOY

**Run this before EVERY deploy. No exceptions.**

---

## 15. End-to-End Flow Diagram

```
CUSTOMER                     BROWSER                      API SERVER                   AGENTMAIL/WITNESS
   |                            |                              |                              |
   | visits purebrain.ai        |                              |                              |
   |--------------------------->|                              |                              |
   |                            | Page loads with chat UI      |                              |
   |                            | Consent checkbox pre-checked |                              |
   |                            | CTAs locked until naming     |                              |
   |                            |                              |                              |
   | === PRE-PAYMENT NAMING CEREMONY ===                       |                              |
   |                            |                              |                              |
   | Names AI "Aria"            |                              |                              |
   |--------------------------->| payTestData.aiName = "Aria"  |                              |
   |                            |----------------------------->| POST /api/log-conversation   |
   | Provides name, email       |                              |   (conversation logged)      |
   |--------------------------->| payTestData filled            |                              |
   |                            |                              |                              |
   | === PRICING REVEALED ===   |                              |                              |
   |                            | Canvas + video PAUSE         |                              |
   |                            | CTAs unlocked (orange)       |                              |
   |                            |                              |                              |
   | === PAYMENT ===            |                              |                              |
   |                            |                              |                              |
   | Clicks tier CTA            |                              |                              |
   |--------------------------->| PayPal overlay opens         |                              |
   |                            | SDK Smart Buttons render     |                              |
   |                            |                              |                              |
   | Completes PayPal payment   |                              |                              |
   |--------------------------->| onApprove fires              |                              |
   |                            |----------------------------->| POST /api/verify-payment      |
   |                            |                              |   - Logs payment              |
   |                            |                              |   - Stores payer email by UUID|
   |                            |                              |   - Fires seed (bg thread)--->| SEED to aiciv-seed-inbox
   |                            |                              |                              |
   | === POST-PAYMENT ===       |                              |                              |
   |                            | onPaymentComplete fires      |                              |
   |                            | fireSeed() (client-side)---->| POST /api/send-seed (dedup)  |
   |                            | 300ms delay                  |                              |
   |                            | REDIRECT to /thank-you/      |                              |
   |                            |   ?aiName=Aria&name=...      |                              |
   |                            |   &email=...&tier=Awakened   |                              |
   |                            |                              |                              |
   | === THANK-YOU PAGE ===     |                              |                              |
   |                            |                              |                              |
   | Sees status checklist      |                              |                              |
   |  [x] Payment confirmed     |                              |                              |
   |  [ ] AI being configured   |                              |                              |
   |  [ ] Welcome email coming  |                              |                              |
   |  "Check inbox at [email]"  |                              |                              |
   |                            |                              |                              |
   |                            | Polls every 5s:              |                              |
   |                            | GET /api/magic-link/{uuid}-->| Returns pending or ready     |
   |                            |                              |                              |
   |                            |              Witness processes seed (2-5 min)...             |
   |                            |              Allocates container...                          |
   |                            |              Sends MAGIC LINK email to aether-aiciv          |
   |                            |                              |                              |
   |                            |                              |  agentmail_monitor detects    |
   |                            |                              |  MAGIC LINK email             |
   |                            |                              |  - Parses fields              |
   |                            |                              |  - Rewrites .ai-civ.com      |
   |                            |                              |    to .app.purebrain.ai      |
   |                            |                              |  - Stores in .magic-links    |
   |                            |                              |  - Sends welcome email(s)    |
   |                            |                              |  - BCC jared@puretechnology  |
   |                            |                              |                              |
   |                            | Poll returns "ready"!        |                              |
   |                            |<-----------------------------|                              |
   |                            |                              |                              |
   | Checklist goes all green   |                              |                              |
   |  [x] Payment confirmed     |                              |                              |
   |  [x] AI configured         |                              |                              |
   |  [x] Welcome email sent    |                              |                              |
   |                            |                              |                              |
   | "Enter Aria's Brain Stream"|                              |                              |
   |     [BUTTON APPEARS]       |                              |                              |
   |                            |                              |                              |
   | Clicks button (or email)   |                              |                              |
   |--------------------------->| Opens portal via magic link   |                              |
   |                            | [container].app.purebrain.ai |                              |
```

---

## 16. What Was Removed (2026-04-01)

The following were part of the old flow and have been REMOVED:

### Post-Payment Chatbox (REMOVED)
- `launchPostPaymentFlow()` function
- `_postPaymentLaunched` guard variable
- `postPaymentOverlay` DOM element
- `handlePaymentSuccess()` triggering chatbox
- Black screen prevention guard (no longer needed)
- The chatbox had a persistent black screen bug where `launchPostPaymentFlow` fired twice

### Post-Payment Questionnaire (REMOVED)
- Step-by-step questionnaire after payment (name, email, company, role, goal)
- `fireSeedAddendum()` function and `/api/seed-addendum` endpoint usage
- These questions are now collected PRE-payment in the naming ceremony

### Magic Link Button on Payment Page (REMOVED)
- Portal button that appeared after chatbox polling
- The thank-you page now handles magic link polling and portal access

### Archive
All removed code is archived at `/oldchatbox/` (password: PUREBRAIN2026) for reference.

---

**END OF DOCUMENT**
