# Security Posture BOOP — 2026-05-02

**Window**: Last 48h commits + uncommitted changes
**Reviewer**: security-engineer-tech (BOOP)
**Prior baseline**: `2026-05-01--security-posture-boop-onboarding-pipeline.md`

## Commits in scope (since baseline)

| Hash | Title | Risk |
|------|-------|------|
| `4f729a3` | seo: add FAQPage JSON-LD to 3 blog posts (AIO) | 🟢 cosmetic, no exec context |
| (no other new commits in 24h) | | |

## Uncommitted changes (live working tree)

| File | Change | Risk |
|------|--------|------|
| `exports/cf-pages-deploy/insiders/awakened/index.html` | 8093 → 28 lines, replaced w/ meta-refresh redirect → `/awakened/` | 🟢 spec compliance fix (per OP# 2026-05-02 verification) |
| `exports/cf-pages-deploy/insiders/pay-test-awakened/index.html` | -126 / +82 lines, removed forbidden `launchPostPaymentFlow` + added `fireSeed()` after email capture | 🟢 spec compliance fix (Rule 4 + Rule 5 of ONBOARDING-SPEC) |
| `tools/verify-payment-pages.sh` | Removed `insiders/awakened` from PAGES list | 🟢 consistent with redirect (no longer a payment page) |
| `.claude/ONBOARDING-SPEC-DEFINITIVE.md`, `.claude/NIGHTLY-ONBOARDING-GUARD.md` | Spec edits | needs ST# review for spec accuracy, no direct security impact |

OP# pair-verified the `/insiders/` regression repair: HTTP 200, redirect target `/awakened/` serves `$149.00` + plan `P-2SA65600MT088594TNGLTFKY`, forbidden markers count = 0, `fireSeed` count = 5. Constitutional compliance restored.

## 🔴 STILL OUTSTANDING — UNFIXED FROM 2026-05-01 BOOP

The two CRITICAL findings from yesterday remain live in production code. **No remediation commits in 24h.**

### C1 (UNFIXED). agentmail-webhook accepts unsigned webhooks
- **Code**: `workers/agentmail-webhook/src/worker.js:294-313` (verified today)
- Line 304 still uses `.includes(env.AGENTMAIL_WEBHOOK_SECRET)` — substring match, exploitable.
- Line 311 still logs mismatch but proceeds: `'proceeding anyway (learning mode)'`.
- **Live URL**: `https://onboarding-api.purebrain.ai/webhook` — exploit path unchanged from yesterday.
- **Impact**: Customer phishing via forged Witness magic-link emails; arbitrary D1 writes to `magic_links` + `clients`; arbitrary Telegram notification injection to Jared.

### C2 (UNFIXED). paypal-webhook has no real signature verification
- **Code**: `workers/paypal-webhook/src/worker.js:164-183` (verified today)
- Line 178 comment unchanged: `Log but don't reject — full signature verification is the proper way`.
- **Impact**: Forged `BILLING.SUBSCRIPTION.ACTIVATED` → grants Awakened/Unified tier without payment; corrupts revenue analytics; cancel/suspend any client by subscription ID.
- **Constitutional concern**: Spec says PayPal-Auto-Split is constitutional — this means the integrity of PayPal events is constitutional too. Forged events corrupt the split logic.

### M1, M2, M3, M4 (UNFIXED)
- M1: 777-sheets-api Origin/localhost auth bypass — still exploitable via `Origin: https://localhost.attacker.com`.
- M2: magic-link polling unauthenticated email harvest — still active.
- M3: env mutation race-prone pattern at `worker.js:616-619` — confirmed unchanged.
- M4: PureSurf BaaS key still hardcoded client-side; rotation event waiting.

## NEW findings (this window)

### N1. /insiders/ index price drift held (acknowledged, not yet fixed)
- Live `/insiders/` serves `$74.50` + non-canonical plan `P-8AU4270420374002JNGY3VYQ` instead of spec-required `$149.00` + `P-2SA65600MT088594TNGLTFKY`.
- This is a **financial integrity** issue: customers paying through `/insiders/` are charged half the spec price and routed to a non-canonical PayPal plan that bypasses PayPal-Auto-Split routing.
- Held by ST# pending Jared approval per investor-frozen rule (per OP# memo).
- 🟡 Risk classification: known + held + tracked = acceptable, but timer is ticking.

### N2. /pay-test-sandbox-5/ broken
- No PRICES, no PLAN_IDS, no `/thank-you/` redirect, no `fireSeed`.
- Listed in spec section 1 as a sandbox page but appears non-functional / placeholder.
- 🟢 Not customer-facing payment, but a spec drift — flag for ST# cleanup.

## CVE check (deps)

Worker package.json files checked:
- `welcome-email-api`, `agentmail-webhook`, `admin-api`, `blog-publisher`, `ara-index` — all CF Workers, runtime is Cloudflare's V8 isolate (no node deps shipped). No npm audit surface.
- No new third-party deps introduced this window.
- **Recommendation**: deferred — CF Workers attack surface is the hand-written code, not deps.

## Engineering flow audit

Today's commits + uncommitted changes:
- `4f729a3` (FAQ JSON-LD): 🟢 BUILD-only, no exec context, no SECURITY/QA gate needed.
- `/insiders/*` repair: appears to have followed BUILD → QA flow (browser-vision-tester ran nightly E2E + OP# pair-verified). SECURITY pass not explicitly logged but content is meta-refresh + spec-compliant payment glue — not a security-impacting change.

## ROUTING (escalation)

**ST# (dept-systems-technology)** — P0 escalation, second BOOP cycle in a row:
1. C1 fix — agentmail-webhook MUST reject on secret mismatch + use `crypto.subtle.timingSafeEqual` on equal-length bytes. Drop `.includes()` matching.
2. C2 fix — paypal-webhook MUST call `/v1/notifications/verify-webhook-signature` OR verify cert locally. Reject on failure with 401.
3. M1 fix — 777-sheets-api MUST require X-API-Key for `/api/*` and tighten localhost regex.
4. M2 fix — magic-link polling MUST require server-generated UUID OR signed token; drop email-fallback lookup.

**LC# (dept-legal-compliance)** — informational:
- N1 financial integrity issue (`/insiders/` $74.50 vs $149) is held pending Jared. If a paying customer disputes, we have a paper trail showing dept-level awareness + held-for-investor-rule.

## Disposition

- ✅ `/insiders/*` regression repair: clean, OP#-verified, spec-compliant
- 🔴 Webhook auth bypasses (C1 + C2): still live, 24h since flagged, second BOOP — escalate to ST# with cross-BOOP-convergence skill (two independent BOOPs flagging same root cause)
- 🟡 N1 price drift: held appropriately per constitutional investor-frozen rule
- Next BOOP: verify C1 + C2 PRs landed within 48h or escalate to Jared directly
