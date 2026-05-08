# 5-Page Definitive Verification — 2026-05-07

**Verifier**: browser-vision-tester
**Method**: Source-of-truth HTML inspection + external JS resolution + live API connectivity
**Spec**: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §§2-7, §16
**Constraint**: No real payments. All evidence is HTTP/source-level — no live PayPal completion.

---

## Test Environment

- WSL2 Linux 6.8.0; tool: `curl -sL`
- Pages downloaded fresh to `/tmp/verify-5pages/`
- External JS dependencies (`/js/payment-glue.js`, `payment-shared.js`, `payment-background.js`) also resolved
- API endpoints probed for connectivity

**Honest limitation**: I cannot execute JS in a real browser session in this leaf-agent context (MCP browser server not active). Evidence is source-level — what each page WILL do when loaded, derived from served HTML + external JS. For runtime state inspection (`window.payTestData` value at step N, modal visibility, network tab traces), a Playwright runner is needed. For the 7 spec checks, source inspection is decisive: every check resolves to a presence/absence in served files.

---

## Critical Methodology Note (Mid-Investigation Correction)

First-pass grep found `window.onPaymentComplete = function` defined **zero times** in `awakened/partnered/unified/insiders`. I almost dispatched the fix sprint. Then I noticed the 4 single-tier pages include `<script src="/js/payment-glue.js">` while homepage and sandbox do NOT. Resolving that external file (HTTP 200, 173 lines) revealed `onPaymentComplete` defined identically with the 300ms `/thank-you/` redirect. **The 4 single-tier pages are spec-compliant via shared external glue, not broken.** Recording this as a learning — future verification must always resolve external scripts before declaring a page broken.

---

## Per-Page Evidence

### 1. Homepage — `https://purebrain.ai/`

| Check | Evidence | Result |
|---|---|---|
| HTTP 200 | curl returns 200 | PASS |
| Chat UI | `id="chatMessages"` line 8462, `class="chat-container"` line 8445 | PASS |
| log-conversation wiring | 6 references | PASS |
| `payTestData` | 172 references (declarations + state mutations) | PASS |
| Consent gate | `<input id="pb-consent-check" checked />` line 8627; CSS classes `pb-cta-locked`/`pb-cta-unlocked` lines 7279-7310 | PASS |
| PayPal SDK | 1 SDK script + 14 `pb-paypal-overlay` refs | PASS |
| `window.onPaymentComplete` | INLINE definition lines 16081-16160 | PASS |
| `fireSeedAddendum` removed (spec §16) | **4 references remain** (lines 15302, 15692, 15817, 15910) — click handler on legacy `#ty-portal-btn` only | SPEC §16 DRIFT |
| `/thank-you/` redirect | `window.location.href = '/thank-you/?aiName=...&name=...&email=...'` line 16158, 300ms setTimeout | PASS |
| Seed before redirect (Rule 4) | `fetch('/api/send-seed')` line 16139, then 300ms delay line 16157 | PASS |

**Verdict**: Compliant. Only deviation is `fireSeedAddendum` cosmetic drift.

---

### 2. `/awakened/`

| Check | Evidence | Result |
|---|---|---|
| HTTP 200 | 200 | PASS |
| Chat UI | `id="chatMessages"` line 1540 | PASS |
| log-conversation | 3 refs | PASS |
| payTestData | 166 refs | PASS |
| Consent gate | `<input id="pb-consent-check" checked />` line 1705 | PASS |
| PayPal SDK | 1 SDK + 14 overlay refs | PASS |
| `onPaymentComplete` | **DEFINED in `/js/payment-glue.js`** loaded via `<script src="/js/payment-glue.js">` | PASS (via external) |
| `fireSeedAddendum` removed | 4 refs | SPEC §16 DRIFT |
| `/thank-you/` redirect | payment-glue.js line 101: `/thank-you/?aiName=...&name=...&email=...&tier=...` 300ms | PASS |
| Seed before redirect | payment-glue.js line 82 `fetch('/api/send-seed')` BEFORE line 100 setTimeout | PASS |
| Inline hash-scroll fallback (line 5330) | Fires at 800ms; /thank-you/ redirect at 300ms triggers full nav first → fallback never reached | PASS |

**Verdict**: Compliant via shared payment-glue.js.

---

### 3. `/partnered/` and 4. `/unified/` and 5. `/insiders/`

All three follow the awakened pattern identically:
- HTTP 200; chat UI present; consent gate present; PayPal SDK + 14 overlay refs
- 165-166 `payTestData` refs, 3 `log-conversation` refs each
- Include `<script src="/js/payment-glue.js">` → `onPaymentComplete` defined externally
- `fireSeedAddendum` 4 refs (uniform drift)
- `/thank-you/` redirect via payment-glue, 300ms

**Verdict**: All three compliant via shared payment-glue.js. Same `fireSeedAddendum` drift.

---

### 6. `/home-test-sandbox/` (CONTROL — known-good baseline)

| Check | Evidence | Result |
|---|---|---|
| HTTP 200 | 200 | PASS |
| Chat UI | `chatMessages` line 8401 | PASS |
| log-conversation | 6 refs | PASS |
| payTestData | 169 refs | PASS |
| Consent gate | 13 refs (CSS + DOM + JS) | PASS |
| PayPal SDK | 1 SDK + 14 overlay | PASS |
| `onPaymentComplete` | **INLINE** line 16013 (no payment-glue dependency) | PASS |
| `fireSeedAddendum` | 4 refs | SAME DRIFT |
| `/thank-you/` redirect | Inline ~line 16095, 300ms | PASS |

**Verdict**: Compliant. Same drift as prod — confirming uniform deploy artifact, not per-page bug.

---

## Side-by-Side Comparison

| Check | Homepage | Awakened | Partnered | Unified | Insiders | Sandbox |
|---|---|---|---|---|---|---|
| HTTP 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Chat UI loads | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `payTestData` populates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Consent gate | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| PayPal SDK + modal wiring | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `onPaymentComplete` defined | ✅ inline | ✅ glue | ✅ glue | ✅ glue | ✅ glue | ✅ inline |
| `fireSeedAddendum` ABSENT (§16) | ❌ 4 | ❌ 4 | ❌ 4 | ❌ 4 | ❌ 4 | ❌ 4 |
| Redirect to `/thank-you/` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Seed before redirect (300ms) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Supporting Infrastructure (live)

- `api.purebrain.ai/api/log-conversation` → POST 400 on empty body (alive, validates)
- `api.purebrain.ai/api/send-seed` → OPTIONS 204 (CORS configured)
- `api.purebrain.ai/api/magic-link/{uuid}` → GET 200
- `purebrain.ai/thank-you/` → 200, has `setInterval(..., 5000)` polling, dual-endpoint fallback (onboarding-api primary, api.purebrain.ai fallback), URL param parsing, magic link button reveal

---

## Final Verdict Per Page

| Page | Verdict | Reasoning |
|---|---|---|
| Homepage | 🟢 GREEN | All 7 checks pass. One cosmetic drift. |
| `/awakened/` | 🟢 GREEN | Compliant via `/js/payment-glue.js`. Same drift. |
| `/partnered/` | 🟢 GREEN | Compliant via `/js/payment-glue.js`. Same drift. |
| `/unified/` | 🟢 GREEN | Compliant via `/js/payment-glue.js`. Same drift. |
| `/insiders/` | 🟢 GREEN | Compliant via `/js/payment-glue.js`. Same drift. |
| `/home-test-sandbox/` (control) | 🟢 GREEN | Reference-implementation match. |

**Universal drift**: `fireSeedAddendum` should have been removed per §16 but persists on all 6 pages — used only as click handler on legacy in-chat portal button. Does NOT fire during normal payment → thank-you flow. Customer impact: zero.

---

## TOP RECOMMENDATION

**🟢 NO FIX SPRINT NEEDED. Declare false alarm on the 5 LIVE pages.**

The original concern — that live pages fall back to legacy in-chat flow with no `/thank-you/` redirect — is **not borne out by the evidence**. The 4 single-tier pages load `/js/payment-glue.js`, which defines `window.onPaymentComplete` identically to the homepage's inline implementation, including the 300ms-delayed `/thank-you/` redirect with full URL parameter encoding. Homepage and sandbox define inline; the 4 single-tier pages define via shared external file. Both architectures are spec-equivalent.

**Why I almost got this wrong**: First-pass grep showed 0 `onPaymentComplete = function` definitions on the 4 single-tier pages. Without resolving external scripts, that looks like a critical bug. Resolving `/js/payment-glue.js` showed the function is defined there. **Future verification agents MUST resolve `<script src=...>` references before declaring a page broken.**

### Single Cosmetic Drift (Optional Cleanup)

`fireSeedAddendum` is referenced 4× per page across all 6 pages. Per §16 it should have been removed. Since it only fires on click of a legacy in-chat portal button (not part of the live payment flow), customer impact is zero. Recommend a low-priority cleanup PR: remove the function + 3 click-handler attachments. Static refactor, zero behavior change. **Not a fix sprint trigger.**

### Behavioral Certainty Caveat

This verification is source-level. For runtime certainty (does PayPal modal actually open? does `payTestData` actually populate at step N? does redirect actually fire?), dispatch a Playwright runner. The `webapp-testing` skill is granted but MCP browser server is not active in this leaf-agent context. Source-level evidence is already strong enough to lift the fix-sprint dispatch flag.

---

## Memory Written

Path: `.claude/memory/agent-learnings/browser-vision-tester/2026-05-07--external-script-resolution-before-declaring-broken.md`
Type: gotcha
Topic: Always resolve `<script src=...>` references before declaring a page broken — pages can split critical callbacks into shared external glue files. Grep on served HTML alone produces false-broken signals.

---

**END OF VERIFICATION**
