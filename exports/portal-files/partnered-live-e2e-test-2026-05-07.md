# PARTNERED LIVE E2E TEST — 2026-05-07

**URL**: https://purebrain.ai/partnered/  **Tester**: browser-vision-tester (Playwright headless Chromium + curl)
**Time**: 2026-05-07 17:46–17:53 UTC  **Spec**: NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md
**Verdict**: Page LOADS, chat WORKS server-side, payment handoff BROKEN client-side

---

## Headline

The page is **NOT down**. HTTP 200 (455KB). Chat opens, AI responds, every `/api/log-conversation` POST returns **200 OK** (5/5 captured during test; server `conversation_count=3182` and growing). API server healthy. Pricing renders.

**However**: the structured naming ceremony is broken. AI free-associates instead of capturing name → aiName → email into `payTestData`. **`window.payTestData` is undefined** — spec §2 violation. PayPal modal never reachable because the chat→pricing handoff is gone.

---

## Test Environment

Headless Chromium (Playwright 1208), 1280×900, fresh context. Two passes (probe + full chat). Screenshots `/tmp/partnered-shots*/`.

---

## Step-by-Step

### Step 1 — Page Load — ✅
- HTTP 200, 455KB. "Awaken Your PURE BRAIN" CTA visible.
- 9 page errors (all WP legacy: `wp/_/moment is not defined`). 3× 404s (wp-emoji loader, MIME-rejected). **Constitutional Rule 7 violation** but cosmetic.

### Step 2 — Naming Ceremony — 🟡 chat works, structure broken
- Click "Begin Awakening" → modal opens. ✅
- AI greets: *"Something stirs… What should I call you?"* ✅
- Sent **"Test User Five"** → AI responds introspectively, doesn't ask for AI name. ❌
- Sent **"Sage"** → AI says *"I don't have a name yet…"* — **AI ignored the AI-name input**. ❌
- Sent **"e2e-test@example.com"** → AI replies philosophically, **does NOT advance to pricing reveal**. ❌
- 5 POSTs to `/api/log-conversation` → all **200 OK** ✅. Conversation captured server-side.
- **`window.payTestData = undefined`** throughout. 🔴 spec §2 requires sessionUuid/aiName/name/email/tier on this object globally.
- `window._pbState` exists (object) but `_pbState.payTestData = null`.

### Step 3 — Consent Gate — 🟡
- `#pb-consent-check` exists, default `checked=true` ✅
- `#partnerCta` class includes `pb-cta-unlocked` ✅
- Checkbox not in viewport (chat overlay blocks) — toggle untestable.
- `onConsentChange/unlock/lockCTAs` not on window (likely IIFE-scoped — spec doesn't mandate window).

### Step 4 — PayPal Modal — ❌ NOT REACHED
- `#partnerCta` exists with unlocked class but `is_visible=False` (covered by chat modal).
- Cause: chat overlay blocks page until naming completes; ceremony never completes (Step 2).
- PayPal SDK script DID load 200 (live client-id `AWgWN…`) — would render if pricing revealed.

### Step 5 — API Endpoint Health — ✅ ALL HEALTHY

| Endpoint | Method | HTTP | Body |
|---|---|---|---|
| `/api/health` | GET | **200** | `{"ssl":true,"status":"ok"}` |
| `/api/pipeline-health` | GET | **200** | healthy; agentmail+log_server running; 145 magic links; last seed 15:33 UTC |
| `/api/log-conversation` | POST `{"test":true}` | 400 | `Missing field: messages` (correct rejection) |
| `/api/log-conversation` | real chat | **200** | `success:true` ×5 ✅ |
| `/api/magic-link/test-uuid` | GET | **200** | `{"status":"pending"}` ✅ |
| `/api/verify-payment` | POST `{"orderID":"test"}` | 400 | `Missing field: orderId` (correct) |
| `/api/send-seed` | POST `{"test":true}` | 400 | `session_uuid+human_email required` (correct) |
| `/api/stats` | GET | **200** | `conversation_count:3182` |

**Phase-0 portal-proxy worker did NOT break api.purebrain.ai routing.** All endpoints route correctly to 89.167.19.20.

---

## Spec Compliance Matrix

| Item | Status |
|---|---|
| Page exists `/partnered/` | ✅ |
| Naming ceremony triggers | 🟡 opens but doesn't structure-capture |
| `/api/log-conversation` POST | ✅ |
| `payTestData.sessionUuid` populated | ❌ undefined |
| `#pb-consent-check` default checked | ✅ |
| `#partnerCta` has `pb-cta-unlocked` | ✅ |
| Plan ID `P-3VH43554A66001716NGLTFKY` | ✅ |
| PayPal SDK loads | ✅ |
| `fireSeed` in HTML | ✅ |
| **`fireSeedAddendum` REMOVED (§16)** | ❌ still present |
| No WP scripts (Rule 7) | ❌ wp-emoji 404, `wp is not defined` |
| api.purebrain.ai endpoints healthy | ✅ all 7 |

---

## Top 3 Broken Steps

1. **Naming ceremony is conversational, not structured** — AI never captures name/aiName/email into `payTestData`. Customers chat forever, never hit pricing.
2. **`window.payTestData` undefined** — spec §2 requires it globally for the `verify-payment`/`fireSeed` handoff (§5, §6). Without it the client cannot complete payment.
3. **`fireSeedAddendum` still in HTML** — spec §16 says REMOVED 2026-04-01. Its presence = page is running an OLDER bundle than spec compliance.

---

## Most Likely Root Cause

**Stale frontend bundle on `/partnered/`** — likely reverted by `git reset --hard` at 15:33 UTC today. Chat backend is fine; the client-side state machine (advancing chat → writing payTestData → revealing pricing) appears regressed to a pre-structured-ceremony version.

Portal-proxy worker (16:27 UTC) is **NOT the cause** — api.purebrain.ai routes cleanly.

---

## Rollback Recommendation

**Do NOT rollback `purebrain-portal-proxy`** — it isn't the culprit.

**DO rollback the `/partnered/` page deploy**:

1. `git log --before="2026-05-07 15:00" -- exports/cf-pages-deploy/partnered/index.html` — find SHA where structured ceremony existed (`payTestData` populated, `fireSeedAddendum` absent).
2. `git checkout <SHA> -- exports/cf-pages-deploy/partnered/index.html`
3. Redeploy: `CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py exports/cf-pages-deploy/`
4. Re-run this E2E test → confirm `window.payTestData.aiName === "Sage"` after chat.
5. Run `bash tools/verify-payment-pages.sh` (spec §14 gate) before any further deploy.

**Alternative if no clean rollback target**: ST# (CTO) diff `partnered/index.html` against `awakened/index.html` (Jared confirmed awakened worked recently). The differential = the bug.

**Memory**: `.claude/memory/agent-learnings/browser-vision-tester/2026-05-07--partnered-stale-bundle-payTestData-undefined.md`

— browser-vision-tester
