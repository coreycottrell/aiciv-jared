# RECEIPT — Checkout Seed-Fire Repair + Full Per-Page E2E (BUILD) — 2026-07-03

**Status: 🟢 DEPLOYED (server seed-fix + /tiers) — post-deploy E2E PASS. 🟡 Stripe $1 code-approved, deploy gated on CF source confirmation.**
**Owner:** dept-systems-technology (ST#)
**Pipeline:** BUILD → SECURITY → QA → SANDBOX E2E → PER-PAGE MATRIX → **DEPLOY (Jared GO)** → POST-DEPLOY LIVE E2E PASS
**Written:** 2026-07-03 · **Deployed:** 2026-07-03 (Jared explicit GO via trusted conductor relay)

---

## ★ LIVE DEPLOY RESULT (executed on Jared's GO)

| Surface | Action | Result | Evidence |
|---------|--------|--------|----------|
| **Server seed-fix** | scoped commit `974c2a0` + `systemctl restart aether-logserver.service` | ✅ **DEPLOYED, VERIFIED** | new pid 668681, `/api/health` 200, pipeline healthy, no startup traceback. Rollback anchor `3f6f0db`. |
| **/tiers reroute** | merge → purebrain-site `main` `e5bceb48` + push | ✅ **DEPLOYED, LIVE** | `purebrain.ai/tiers/` serves all 3 `awakening?tier=…` reroutes |
| **Stripe $1 one-time** | Option A endpoint built + security-passed | 🟡 **HELD — deploy-source gate** | code PASS-with-nits; needs CF deploy-source confirmation (see below) |

**Post-deploy LIVE E2E (wtt-qa, against prod pid 668681): DEPLOY VERIFIED — PASS, no rollback.**
- OUR one-time seed path fires POPULATED on live: `log-conversation` persisted binding → `send-seed` (conversation+ai_name omitted) **hydrated ai_name + non-empty conversation by EXACT key** → HTTP 200 + SES message_id; `seed_events.jsonl` 37→38 with populated content.
- Subscription path NOT broken: the only 2 deletions in the deploy are the `verified:True`→`_p2b_verified` observability swap; verify-payment fire path is additive-only. Real prod sessions flowing normally post-restart.
- Service healthy: `active`, pid 668681, `/api/health` 200, `/api/pipeline-health` healthy, no new tracebacks.
- **Distinction held:** (a) OUR seed fires = PASS (the deploy gate). (b) Witness births = separately tracked — and **appear to have RESUMED** post-restart (last magic-link mint 18:54, `magic_links_last_hour: 2`), vs the prior ~42h stall. Not the gate, but good news.

**Stripe $1 remaining gate (before `wrangler pages deploy`):** security PASS-with-nits on the code, but the reviewed change lives only in commit `5391374` and there are ~6 divergent `exports/` copies of the clone source; the true CF deploy source is dashboard state. **Operator MUST confirm (a) the deployed dir content == commit `5391374`, and (b) that dir is the real CF source for project `purebrain-awakening-clone` (which serves ALL live Stripe pages) — else the review doesn't cover what ships.** Non-blocking NITs: add route-scoped body-size cap + rate limiting. Webhook-owner flags: `sessionUuid` is client-controlled/unvalidated → downstream consumers must key exact-match fail-closed; `metadata[tier]` verbatim could carry a high tier on a $1 charge → referral commission must key off actual amount (phantom-commission tie-in). **Deploy = `npx wrangler pages deploy <confirmed-dir> --project-name=purebrain-awakening-clone` after (a)+(b).**

---

**(Historical build record below — superseded by the deploy result above where they differ.)**

---

## 0. THE SINGLE BIGGEST BLOCKER (read this first)

**Our checkout code works end-to-end. The WITNESS BIRTH TAIL is stalled — and it is Witness-side, not our code.**

- Full sandbox E2E proves OUR chain fires a **correct, populated seed** (ai_name + non-empty conversation + correct email + single-UUID) on both sandbox pages. PASS.
- But **no magic link has been minted for ANYONE in ~42 hours** (last = Verun, 2026-07-02 00:40; `magic_links_last_hour: 0`). The real in-flight birth **Vega** (`purebrain_1783027001486_lxdljmduf`) is `pending` ~63 min after its seed was sent.
- Our ingestion monitor (`agentmail_monitor.py`) is provably **alive and healthy** (state file saving every ~10s, normal poll sleep). So Vega `pending` means **Witness has emailed back no magic-link reply** — there is nothing for us to ingest.

**Conclusion:** paying customers currently complete pay → seed, then the AI does not auto-birth because **Witness is not minting/returning magic links.** This needs a Witness-side investigation (separate from this checkout work). Our fix removes every silent failure on OUR side and makes the seed correct and populated; it cannot make Witness mint links.
**Secondary latent (our-side):** when Witness last DID reply (07-02), our monitor logged `Failed to parse any fields from magic link email body`. Harden that parser before Witness resumes, or ingestion could re-block.

---

## 1. WHAT'S CONFIRMED, BUILT, AND GATE-PASSED

| Item | State | Gate |
|------|-------|------|
| **Server patch** (P1c dead-letter+portal, P1d exact-key persisted binding, P2b one-time verify, money-event guard) | Staged on disk + committed patch | ✅ Security PASS-with-nits (no leak), ✅ Sandbox E2E 4/4 |
| **/tiers genuine-gap fix** (reroute ceremony-less checkout → `/awakening`) | Staged branch + patch | Trivial client reroute (see §6 note) |
| **Defensive silent-400 → dead-letter + PORTAL alert** | In the server patch (P1c) | ✅ pure-upside, kept |
| **Full 12-page PASS/FAIL matrix** | Delivered (§4) | Read-only verified |

**Net safety property proven across all pages: no page can SEND an empty seed anymore.** The fail-closed guards (ai_name guard, empty-conversation guard, P1c missing-key dead-letter) mean the worst case is a HELD/blocked seed + PORTAL alert (customer awaits manual dispatch), never a silent empty-seed send. That is the core exposure closed.

---

## 2. FULL SANDBOX E2E — per-stage (wtt-qa, local instance port 8901, prod :8443 untouched, zero leak)

| Stage | Owner | Result |
|-------|-------|--------|
| Sandbox payment → verify-payment | OUR | ✅ PASS (`verified:true`) |
| verify-payment → seed fired | OUR | ✅ PASS (`[payment-seed] Seed fired … AI: Ember`, hydrated 4 msgs) |
| Seed WITH ai_name + NON-EMPTY conversation | OUR | ✅ PASS (send-seed: ai_name Solace, 4/4 non-empty; verify-payment: ai_name Ember, 4/4 non-empty) |
| Single-UUID threading + correct email | OUR | ✅ PASS |
| Fail-closed guards (empty conv / unknown uuid) | OUR | ✅ PASS (empty→422+dead-letter; unknown-uuid→blocked, no stranger data) |
| **Witness receives seed** | WITNESS | ⛔ STALLED (Vega no reply ~63 min) |
| **`/api/magic-link/{uuid}` returns link** | WITNESS | ⛔ STALLED (`pending`; `magic_links_last_hour: 0`) |
| Convert to `app.purebrain.ai` portal link | OUR (blocked upstream) | ⏸ BLOCKED (conversion code proven-good on past births; no link to convert) |
| Welcome email sent | WITNESS/OUR | ⏸ BLOCKED (needs a minted link) |

**Verdict: (a) OUR checkout code = PASS. (b) Witness birth tail = STALLED, Witness-side.**

---

## 3. THE CONFIRMED DEPLOY-READY SERVER PATCH (staged, not deployed)

**File:** `tools/purebrain_log_server.py` (edited on disk `M`, uncommitted; durable patch `to-jared/PATCH-checkout-seed-fix-server-2026-07-03.patch`, py_compile exit 0)

| Item | Change | Why |
|------|--------|-----|
| **P1c** | Missing `session_uuid`/`human_email` → dead-letter (`blocked_seeds.jsonl`) + PORTAL alert (mirror empty-conv guard) | Closes the zero-trace drop that made Ashley invisible |
| **P1d** | Persist `session_uuid → conversation` binding at ceremony time; hydrate by EXACT key only | One-time/weak-key buyers seed WITH content, no recency fallback (the actual Ashley regression fix) |
| **P2a** | Stripe caller missing `ai_name` after hydrate → dead-letter + PORTAL alert | Defensive observability |
| **P2b** | Non-`I-` one-time orders confirm real captured amount via PayPal Orders-API; unconfirmed/≤0 → verified:false | Kills the latent `$0.00`/verified:true blind spot |
| **Guard** | Money-event reconcile (PayPal capture + Stripe session) → grace window → dead-letter + PORTAL alert | Catches paid-but-no-seed on BOTH rails, anchored on the money event |

**07-03 fail-closed hardening UNTOUCHED. No recency/fuzzy reintroduced — every new hydrate is exact-key-or-fail-closed** (security-verified in the actual comparison logic; 11 `strict=True` sites + S4/S5 byte-unchanged).

---

## 4. DEFINITIVE 12-PAGE MATRIX (payment-flow-qa, read-only) — current-live → post-fix

⬛ = load-bearing stage. "Post-fix" = staged server patch + /tiers reroute deployed.

| # | Page | Verdict current → post-fix | Load-bearing note |
|---|------|----------------------------|-------------------|
| 1 | **/awakening** (live checkout) | PASS → PASS (PayPal sub) | ⬛ seed fires **server-side** in verify-payment; client-400 is redundant, now dead-lettered. **Stripe rail = see §5 gap** |
| 2 | /awakened $297 | PASS → PASS | ⬛ routes → /awakening (inherits #1) |
| 3 | /partnered $597 | PASS → PASS | ⬛ routes → /awakening |
| 4 | /unified $1097 | PASS → PASS | ⬛ routes → /awakening |
| 5 | /insiders | PASS → PASS | ⬛ ceremony + sessionUuid stamped |
| 6 | **/tiers** | **FAIL → PASS** | ⬛ no ceremony → held seed; **fixed by staged reroute** |
| 7 | /old-pricing | PASS → PASS | ⚠ still serves legacy NGLTFKY/NGLTFLA plan IDs (not NICOI7Q) — confirm |
| 8 | /home-test | PASS → PASS | PayPal-only test surface |
| 9 | /home-test-sandbox | PASS (sandbox) | E2E-proven; N/A real $ |
| 10 | /home-test-live-1 $1 | **PARTIAL → PASS** | PayPal $1 works; **Stripe $1 BLOCKED** (§5) |
| 11 | /pay-test-sandbox-3 | PASS (sandbox) | E2E-proven; N/A real $ |
| 12 | /pay-test-sandbox-5 | RETIRED | meta-refresh → / (no money surface) |

**Pages where a real paying client could still fail post-fix (our-side), and the stage:**
1. **/awakening STRIPE rail** — stage = client-side single-UUID threading. All staged patches are server-side; the Next.js funnel still doesn't mint one `sessionUuid` threaded through log-conversation + create-checkout-session. Post-fix, Stripe /awakening converts empty-seed → **BLOCKED** (safe, no empty send) but the customer gets **no auto-AI** until manual dispatch. PayPal rail is fine (server email-resolution). **This is the one page to fix next on our side.**
2. **/tiers** reaches PASS only once the reroute actually deploys.
3. **/old-pricing** legacy plan IDs — confirm merchant/plan-ID intent.

**Could not verify from this host (stated, not guessed):** live Stripe rail behavior (no Stripe secret on host; the live `stripe-seed-d1 worker.prod.js` still mints a fresh uuid + `"PURE BRAIN"` default → the frontend/webhook Stripe path is NOT source-fixed, only caught by the Python guard), Witness async tail timing, and live `api.purebrain.ai` deploy parity vs this host's copy.

---

## 5. BLOCKED — Stripe $1 one-time on /home-test-live-1 (Jared-gated, code-ready)

The price-id blocker is **dissolved** (a `mode:'payment'` session needs no pre-created one-time price — inline `price_data` works). But a real second blocker remains: **the Stripe SECRET binding lives ONLY on the `purebrain-awakening-clone` Pages project, not on purebrain-site** (verified: purebrain-site has zero Stripe server code / no `STRIPE_SECRET` binding; every Stripe page here posts cross-origin to `purebrain-awakening-clone.pages.dev/api/create-checkout-session`).

**➡️ NEED FROM JARED (pick one):**
- **(A)** Add a `mode:'payment'` one-time branch to `create-checkout-session` **on purebrain-awakening-clone** (has the secret; out of purebrain-site scope), or
- **(B)** Add a `STRIPE_SECRET` binding to the **purebrain-site** Pages project so we add the endpoint here.

Drop-in the moment you choose (amount server-held, never client-supplied; sessionUuid as idempotency key):
```js
line_items:[{price_data:{currency:'usd',unit_amount:100,product_data:{name:'PureBrain Awakening (one-time $1)'}},quantity:1}],
mode:'payment', client_reference_id:sessionUuid, metadata:{sessionUuid, tier}
```
The existing **PayPal $1 one-time on this page works on its own** (its seed now fires via the server P1d/P1c fix).

---

## 6. WHAT WAS BUILT THIS PASS (staged, HELD)

- **/tiers reroute — DONE.** Branch `stage/checkout-seed-confirmed-20260703` (commit `9de805a4`, pushed to origin as a feature branch, NOT main). Only `tiers/index.html` (3 CTAs → `/awakening?tier=awakened|partnered|unified`, referral/UTM forwarded). Patch: `to-jared/PATCH-checkout-seed-confirmed-2026-07-03.patch`. *Note: this is a trivial client-side href reroute to an already-verified surface — no new charge logic/attack surface; not independently security-reviewed (recommend a glance only if desired).* Minor flag: the Next.js marketing pages link to plain `/awakening` (no tier param), so `?tier=X` may not pre-select the tier — harmless; the goal (real ceremony → non-empty seed) holds regardless.
- **Server patch** — built prior, gate-passed (§3).
- **Stripe $1** — code-ready, blocked on the binding question (§5). Disabled placeholder staged on `stage/home-test-live-1-stripe-onetime-20260703`.
- **/awakening JS (subscription) — shelved, NOT needed** (subscriptions verified E2E-complete). Unmerged branch `stage/checkout-seed-fix-20260703` kept for reference only.

---

## 7. SECURITY + QA SUMMARY

- **Security (independent, server patch): PASS-with-nits.** Cross-customer leak stays closed; exact-key-or-fail-closed verified; 11 strict sites + S4/S5 untouched; reconcile only reads/alerts. Nits (non-blocking follow-ups): MEDIUM unbounded `threading.Timer` reconcile (DoS/availability — bound it or use an out-of-band sweep of `paid_events.jsonl`); LOW tmux portal-inject prompt-injection pattern (add `-l`, strip newlines); LOW sandbox also suppresses dead-letter write; LOW positive client `amount` still trusted (pre-existing).
- **QA sandbox E2E: 4/4 PASS + full-chain per-stage (§2).** Two behavioral findings (pre-existing, not defects): `is_sandbox=true` does NOT suppress the real AgentMail seed send (future testers MUST fake AgentMail); sandbox also suppresses the dead-letter write (prod correct).

---

## 8. EXACT DEPLOY STEPS (run only on Jared's GO — two independent surfaces)

**A) Server patch (the seed-fire fix)** — activation = one systemd restart:
```bash
cd /home/jared/projects/AI-CIV/aether
git rev-parse --abbrev-ref HEAD          # feat/migrate-seed-fold-gate1-2026-06-30
git status --short tools/purebrain_log_server.py   # " M" (edits present); if wiped: git apply to-jared/PATCH-checkout-seed-fix-server-2026-07-03.patch
python3 -m py_compile tools/purebrain_log_server.py && echo "compile OK"
git add tools/purebrain_log_server.py    # scoped, source-of-truth
git commit -m "fix(seed): exact-key persisted binding + dead-letter/portal on send-seed 400 (one-time seed-fire repair)"
sudo systemctl restart aether-logserver.service    # THE gated lever (last restart caused the regression)
systemctl is-active aether-logserver.service       # active
curl -s -o /dev/null -w "%{http_code}\n" https://api.purebrain.ai/health   # 200
# Verify on ONE real job (idle /health is not proof): next real ceremony writes session_uuid_bindings.jsonl,
# next real one-time capture produces seed_sent WITH non-empty conversation.
```
Rollback: `git checkout tools/purebrain_log_server.py && sudo systemctl restart aether-logserver.service`.

**B) /tiers reroute** — canonical purebrain-site deploy (merge feature branch → main → push):
```bash
cd /home/jared/projects/purebrain-site
git checkout main && git pull
git merge --no-ff stage/checkout-seed-confirmed-20260703   # brings ONLY tiers/index.html
git push origin main    # canonical deploy to puretechnyc/purebrain-site
# verify: curl -s https://purebrain.ai/tiers | grep -o "awakening?tier=[a-z]*" | head
```

---

## 9. AWAITING JARED

1. **GO / NO-GO: server-patch deploy** (§8A) — the one-time $1 seed-fire fix + observability. Security + sandbox QA passed.
2. **GO / NO-GO: /tiers reroute deploy** (§8B) — closes the only genuine per-page gap.
3. **Stripe secret binding: (A) clone endpoint or (B) purebrain-site binding?** (§5) — unblocks the $1 Stripe button.
4. **Witness birth investigation** (§0) — the real blocker to customers getting their AI: no magic link minted in ~42h; Witness-side. Recommend routing to whoever owns Witness birth/container-spawn.
5. FYI follow-ups (non-blocking): /awakening Stripe-rail frontend single-UUID threading (§4·1), magic-link email parser hardening (§0), Timer-DoS nit (§7), /old-pricing legacy plan IDs (§4·7).

---

## 10. PERSISTENCE (nothing left only in a scratch clone)

- Server code: on disk `M` + committed patch `PATCH-checkout-seed-fix-server-2026-07-03.patch`.
- /tiers fix: branch `stage/checkout-seed-confirmed-20260703` pushed to origin + `PATCH-checkout-seed-confirmed-2026-07-03.patch`.
- Shelved /awakening JS: branch `stage/checkout-seed-fix-20260703` (unmerged) + client patch.
- Stripe scaffold: branch `stage/home-test-live-1-stripe-onetime-20260703` + patch.
- Sole-committer discipline held; scoped adds only; IDOR + pre-existing dirty state untouched; no main pushed; nothing deployed/restarted.
