# COMPLETE ONBOARDING FLOW — CONSTITUTIONAL LOCK (2026-03-26)

**THIS DOCUMENT IS THE SINGLE SOURCE OF TRUTH FOR THE ENTIRE CUSTOMER ONBOARDING FLOW.**
**NO DEVIATIONS EVER. NO MATTER WHAT.**

---

## LIVE PAYMENT PAGES (REAL CUSTOMERS)

| Page | Status |
|------|--------|
| purebrain.ai/live/ | LIVE — real seeds |
| purebrain.ai/insiders/ | LIVE — real seeds |
| purebrain.ai/awakened/ | LIVE — real seeds |
| purebrain.ai/partnered/ | LIVE — real seeds |
| purebrain.ai/unified/ | LIVE — real seeds |

## TEST PAGE

| Page | Status |
|------|--------|
| purebrain.ai/pay-test-sandbox-3/ | TEST — seeds marked "THIS IS A SEED TEST FROM JARED OR PURE TECHNOLOGY" |

All live pages verified MATCH sandbox-3 on all critical elements (2026-03-25):
- RETURN_URL: points back to same page + ?payment=success
- USE_SDK_APPROACH: true
- VERIFY_ENDPOINT: https://api.purebrain.ai/api/verify-payment
- onPaymentComplete + launchPostPaymentFlow: present
- checkForPaymentReturn: present
- initPayTestFlow: present
- 64/64 verification checks PASS

---

## THE FLOW (STEP BY STEP — IMMUTABLE)

### Step 1: Customer arrives at payment page
- Clicks "Awaken Your Pure Brain"

### Step 2: Naming ceremony (BEFORE payment)
- AI introduces itself through conversation
- Customer and AI discover the AI's name together
- NAMING HAPPENS BEFORE PAYMENT — ALWAYS
- Nobody can pay without completing the naming chat
- Conversation logged to purebrain_web_conversations.jsonl

### Step 3: Customer pays via PayPal
- PayPal SDK Smart Buttons (in-page)
- Returns: name, email, subscription ID, tier, amount
- If PayPal redirects: RETURN_URL sends back to same page with ?payment=success

### Step 4: SEED FIRES (ONE email, on PayPal payment)
**Trigger:** PayPal payment verified in purebrain_log_server.py
**ONLY fires AFTER obtaining customer's email via PayPal**
**ONE seed per customer — dedup guards prevent double-fire**

Email routing:
- FROM: aether-aiciv@agentmail.to
- TO: aiciv-seed-inbox@agentmail.to
- CC: jared@puretechnology.nyc, aether-aiciv@agentmail.to, purebrain@puremarketing.ai

Email MUST contain:
1. Rich HTML body (dark bg #080a12 with bgcolor attribute)
   - UUID / session ID at top
   - AI Name, Human Name, Email, Tier, Amount, Subscription ID
   - FULL conversation (color-coded rows)
   - Sandbox banner if test page
2. .md plain text body with full conversation (MANDATORY — NEVER skip)

Portal notification: "[SEED FIRED] Name (AI: X) — seed sent to Witness"

### Step 5: Post-payment chatbox continues
- Asks: company, role, primary goal
- This enrichment data collected for addendum

### Step 6: ADDENDUM fires (on "ENTER YOUR AI'S BRAIN STREAM" click)
- FROM: aether-aiciv@agentmail.to
- TO: aiciv-seed-inbox@agentmail.to
- CC: jared@puretechnology.nyc, aether-aiciv@agentmail.to, purebrain@puremarketing.ai
- Contains: UUID, AI name, company, role, primary goal, all post-payment Q&A
- Same rich HTML + .md format as seed
- _addendumFired dedup guard prevents double-fire

### Step 7: Witness provisions container
- Receives seed → creates container → generates magic link
- Sends back email with: AI Name, Magic Link, Container name, UUID

### Step 8: Magic link domain rewrite
- agentmail_monitor.py receives magic link from Witness
- Rewrites: name.ai-civ.com → name.app.purebrain.ai
- Stores in .magic-links.json

### Step 9: Magic link delivered to customer (TWO places)

**Place 1: Button on payment page**
- "ENTER [AI NAME]'S BRAIN STREAM" button lights up with magic link
- Below button: "If this button doesn't light up in the next 3 minutes check the email you provided earlier in the chat."
- Magic link poller checks every 5 seconds for up to 30 minutes

**Place 2: Welcome email to customer**
- FROM: Aether | PureBrain <purebrain@puremarketing.ai>
- BCC: jared@puretechnology.nyc (customer does NOT see Jared)
- Dark-themed HTML template with bgcolor="#080a12"
- Contains: AI name, branded magic link (app.purebrain.ai domain)
- Template placeholders: {{HUMAN_FIRST_NAME}}, {{CIV_NAME}}, {{MAGIC_LINK}}

---

## DEDUP GUARDS
- _seeds_fired_for_orders (server set) — prevents payment + chatbox double-fire
- _seedFired (client boolean) — prevents client-side re-fire
- seed_sent_uuids.json (server file) — persistent UUID dedup for /api/send-seed
- _addendumFired (client boolean) — prevents addendum re-fire

## KEY FILES
- tools/purebrain_log_server.py — payment handler + seed + addendum
- tools/agentmail_monitor.py — magic link receiver + domain rewrite + welcome email
- .magic-links.json — stored magic links
- tools/verify-payment-pages.sh — pre-deploy gate (64/64 checks)

## AUDIT RESULTS (2026-03-26)

| Step | Description | Status |
|------|-------------|--------|
| 1 | Seed fires on PayPal payment | PASS |
| 2 | Post-payment chatbox questionnaire | PASS |
| 3 | Addendum fires on Brain Stream click | PASS (client dedup) |
| 4 | Magic link handling + domain rewrite | PASS |
| 5 | Welcome email to customer (BCC Jared) | PASS |
| 6 | Portal notifications | PASS |
| 7 | Only one seed per customer | PASS |

## NEVER (IMMUTABLE)
- Never change payment logic without Jared approval
- Never modify seed email format
- Never remove full conversation from seed
- Never send seed without .md plain text
- Never remove CC to jared@puretechnology.nyc
- Never send seeds from wrong inbox (ONLY aether-aiciv@agentmail.to)
- Never skip AI name lookup from conversation log
- Never deploy payment pages without verify-payment-pages.sh passing
- Never send bare seed without AI name + conversation
- Never let customers see ai-civ.com domain (always app.purebrain.ai)
- THIS IS HOW WE GET PAID — NO DEVIATIONS EVER
