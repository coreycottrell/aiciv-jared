# Nightly Onboarding Pipeline Verification — April 24, 2026

**Run by**: Payment Flow QA Engineer (READ-ONLY)
**Timestamp**: 2026-04-24

---

## STEP 1: Page Load Verification (HTTP 200, Dark Theme, Core Elements)

| # | Page | HTTP | Dark Theme | Chat | PayPal SDK | randomUUID | Status |
|---|------|------|------------|------|------------|------------|--------|
| 1 | purebrain.ai/ | 200 | YES (10 refs) | YES | YES | YES | GREEN |
| 2 | /insiders/ | 200 | YES (5 refs) | YES | YES | YES | GREEN |
| 3 | /awakened/ | 200 | YES (4 refs) | YES | YES | YES | GREEN |
| 4 | /partnered/ | 200 | YES (4 refs) | YES | YES | YES | GREEN |
| 5 | /unified/ | 200 | YES (4 refs) | YES | YES | YES | GREEN |
| 6 | /home-test/ | 200 | YES (11 refs) | YES | YES | YES | GREEN |
| 7 | /home-test-sandbox/ | 200 | YES (11 refs) | YES | YES | YES | GREEN |
| 8 | /home-test-live-1/ | 200 | YES (11 refs) | YES | YES | YES | GREEN |

**All 8 pages: GREEN** — HTTP 200, dark #080a12 theme confirmed, chatbox code present, PayPal SDK loaded via PAYPAL_CLIENT_ID variable, crypto.randomUUID() for session IDs.

---

## STEP 2: Payment Flow Elements

### PayPal Plan IDs

| Plan | Expected ID | Present In |
|------|------------|------------|
| Awakened | P-2SA65600MT088594TNGLTFKY | awakened, partnered, unified, home-test, home-test-sandbox |
| Partnered | P-3VH43554A66001716NGLTFKY | awakened, partnered, unified, home-test, home-test-sandbox |
| Unified | P-43A28944XN5237411NGLTFLA | awakened, partnered, unified, home-test, home-test-sandbox |

**home-test-sandbox** also contains 3 sandbox plan IDs (P-6DU..., P-6JY..., P-9KA...) — expected for sandbox testing.

**home-test-live-1**: Plan IDs are set to empty strings (PLAN_IDS = { Awakened: '', Partnered: '', Unified: '' }). This means it uses createOrder (one-time capture) flow instead of subscriptions.

| Check | Status |
|-------|--------|
| PayPal SDK loads (all 8 pages) | GREEN |
| Correct plan IDs (3 payment pages) | GREEN |
| verify-payment endpoint referenced (all 8) | GREEN |
| Naming ceremony BEFORE payment | GREEN — "PRICING SECTION — HIDDEN UNTIL NAMING CEREMONY COMPLETES" confirmed in source |

**YELLOW**: home-test-live-1 has empty plan IDs — uses one-time capture flow, not subscriptions. This may be intentional for testing but differs from live pages.

---

## STEP 3: Seed Flow

| Check | Result | Status |
|-------|--------|--------|
| fireSeed() function present | YES (all pages, 6 references each) | GREEN |
| _seedFired guard (double-fire prevention) | YES (3 refs per page — declaration, check, set) | GREEN |
| _addendumFired guard | YES (separate guard for addendum) | GREEN |
| send-seed CORS preflight | OPTIONS -> HTTP 204 | GREEN |
| AI name validation guard (server-side) | YES — BLOCKED + held for manual review if ai_name missing/placeholder | GREEN |
| Seed FROM address | aether-aiciv@agentmail.to | GREEN |
| Seed TO address | aiciv-seed-inbox@agentmail.to | GREEN |
| Seed CC | jared@puretechnology.nyc, aether-aiciv@agentmail.to, purebrain@puremarketing.ai | GREEN |
| Held seeds endpoint | /api/held-seeds exists for blocked seed review | GREEN |

**All seed flow checks: GREEN**

---

## STEP 4: Magic Link Flow

| Check | Result | Status |
|-------|--------|--------|
| /api/magic-link/{email} responsive | HTTP 200 | GREEN |
| Fallback 3 REMOVED | Line 1437: "Fallback 3 REMOVED (2026-04-23): Previously grabbed most-recently-active client's magic link regardless of requester — security leak." Code is commented out / neutralized. DB lookup still runs but result is NOT used. | GREEN |

**Magic link security fix verified: GREEN**

---

## STEP 5: Thank-You Page

| Check | Result | Status |
|-------|--------|--------|
| Page loads | HTTP 200 | GREEN |
| Magic link polling (setInterval) | YES (1 instance) | GREEN |
| "Enter Your Brain Stream" button | YES — "Enter Your Brain Stream" with dynamic personalization to "Enter {aiName}'s Brain Stream" | GREEN |
| aiName param used | YES (7 references) | GREEN |
| email param used | YES (28 references) | GREEN |
| magic-link references | YES (5 references) | GREEN |

**Note**: Button text is "Enter Your Brain Stream" (not "ENTER YOUR AI'S BRAIN STREAM" as specified in the check). It dynamically updates to include the AI name. This is functionally correct.

**Thank-you page: GREEN**

---

## STEP 6: Infrastructure Processes

| Process | PID | Status |
|---------|-----|--------|
| agentmail_monitor | 1203627 | GREEN — Running |
| purebrain_log_server | 1203617 | GREEN — Running |
| telegram_bridge | 1203631 | GREEN — Running |

### Domain Rewrite

| Check | Result | Status |
|-------|--------|--------|
| .ai-civ.com -> .app.purebrain.ai rewrite | YES — regex substitution at line 367-376 in agentmail_monitor.py | GREEN |
| Rewritten link stored as magic_link_pb | YES | GREEN |

**All infrastructure: GREEN**

---

## STEP 7: Portal Notifications

| Notification | Present | Status |
|-------------|---------|--------|
| [NEW PAYMENT] | YES — fires on PayPal payment with name, amount, tier | GREEN |
| [SEED FIRED] | YES — fires on both payment-triggered and chat-triggered seeds | GREEN |

**Portal notifications: GREEN**

---

## STEP 8: Performance Optimizations

| Check | Result | Status |
|-------|--------|--------|
| Preconnect to PayPal | YES (line 11 of homepage) | GREEN |
| DNS-prefetch to PayPal | YES (line 12 of homepage) | GREEN |
| No GoDaddy references | 0 occurrences on homepage | GREEN |

---

## OVERALL VERDICT: GREEN

All 7 verification steps pass. No critical or red issues found.

### One YELLOW advisory:

1. **home-test-live-1 empty plan IDs** — PLAN_IDS all set to empty strings, causing one-time capture flow instead of subscription. Likely intentional for testing, but worth noting if subscription testing is expected on this page.

---

*Verification complete. READ-ONLY analysis — no files modified.*
