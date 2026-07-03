# RECEIPT — Checkout Seed-Fire Repair (BUILD) — 2026-07-03

**Status: 🟡 HELD AT DEPLOY — awaiting Jared's explicit final GO**
**Owner:** dept-systems-technology (ST#)
**Pipeline run:** BUILD → SECURITY → QA → SANDBOX-PROVE → **HELD** (no deploy, no restart, no real-money tx, no client-record touched)
**Authority:** Jared GO to **BUILD** ("ok yeah lets go") + mid-task scope CORRECTION (false-positive casualties). Deploy remains gated.
**Written:** 2026-07-03

---

## 1. BOTTOM LINE

The confirmed, gate-passed, deploy-ready fix is a **single server-side patch** to `tools/purebrain_log_server.py`. It repairs the one genuinely-confirmed failure — the **one-time $1 seed-fire regression** (Ashley/Vega) — and adds the observability that let it sit silent. It is built, independently security-reviewed (PASS-with-nits, no leak), and sandbox-E2E proven (4/4 PASS). **It is staged on disk + as a patch; it has NOT been deployed. Deploy = one systemd restart, held for your GO.**

Two other scope items resolved without shipping code:
- The `/awakening` subscription-JS changes are **NOT needed** — read-only verification proved the subscription flow completes E2E (the "Jason/Brad casualties" were reconciliation false positives). That work is quarantined on an unmerged branch, shelved.
- The **Stripe $1 one-time** button is **BLOCKED (buildability gate)** — needs a confirmed one-time payment-mode price-id + endpoint that do not exist in code/config. One Jared-gated question below. No charge path was fabricated.

---

## 2. SCOPE CORRECTION (mid-task, from you)

The E2E audit flagged Jason id132 / Brad id131 as paid-but-no-AI casualties. **False positive** — the audit read only canonical `clients.ai_name`/`clients.magic_link`, which are backfill-lagged. Read-only re-verification across ALL stores (payment-flow-qa):
- **Jason id132** — real chain COMPLETE: `.magic-links.json` uuid `1326a1db…` → ai_name **Verun**, `verun-jason.app.purebrain.ai/react?token=…` status **ready**; `seed_events.jsonl` rows 35-36. Only defect = seed body was empty-conversation (the 07-01 hydrate gap — which THIS patch defends against). Every pipeline STEP fired.
- **Brad** = three separate identities, correctly not merged. Your Brad = **id117 Peter/Unified**, chain COMPLETE (`seed_events` row 28, `.magic-links.json` uuid `909b0a5b…` status ready). id131 (gmail) = correct **fail-closed block** in `blocked_seeds.jsonl` (PayPal manual case, guard working as designed), a different person from Peter.
- **Sample subscribers id115/120/121/127/128 = 5/5** complete in both stores.
- **VERDICT: GENUINE-BREAKAGE = NO** on subscriptions. No client-record was touched; this is a code fix, not a data fix. (Two pre-existing, separately-tracked items surfaced: the send-seed empty-conversation hydrate gap, and canonical-column backfill lag — a reconciliation/data-sync task, not a live-page fix.)

---

## 3. THE CONFIRMED DEPLOY-READY PACKAGE — server patch (STAGED, not deployed)

**File:** `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` (edited on disk, uncommitted `M`)
**Durable patch:** `to-jared/PATCH-checkout-seed-fix-server-2026-07-03.patch` (34 KB, 618-line diff)
**Compiles:** `python3 -m py_compile` → **exit 0** (verified by build author AND by independent security reviewer)

| Item | Change | Why |
|------|--------|-----|
| **P1c** (send-seed silent-400) | Missing `session_uuid`/`human_email` → **dead-letter (`blocked_seeds.jsonl`) + PORTAL alert** (mirrors the existing L3321 empty-conv guard), then still returns 400. Real-signal only (pure-noise probes stay quiet). | Closes the zero-trace drop that made Ashley invisible. PORTAL, not Telegram. |
| **P1d** (the actual regression fix) | Persist a durable **`session_uuid → conversation` binding** at naming-ceremony time (`/api/log-conversation` → `logs/session_uuid_bindings.jsonl`); hydrate at seed time by **EXACT sessionUuid key only**. | One-time/weak-key buyers hydrate WITHOUT the (correctly removed) recency fallback. This is what broke Ashley's seed. |
| **P2a** (Stripe empty-seed) | Stripe caller (`X-Seed-Secret`) still lacking `ai_name` after exact-key hydrate → dead-letter + PORTAL alert. | Defensive observability for the tier-only path (the Jason empty-body class). Alerts only; doesn't alter the working path. |
| **P2b** (verify_payment blind spot) | Non-`I-` one-time orders now confirm the **real captured amount via PayPal Orders-API** (server creds); unconfirmed/≤0 → `verified=False` + dead-letter. | Kills the latent `$0.00`/`verified:true` bug before any one-time flow relies on it. |
| **Cross-cutting guard** | Money-event-anchored paid-vs-seed reconcile on PayPal `PAYMENT.CAPTURE.COMPLETED` + Stripe `checkout.session.completed` (`logs/paid_events.jsonl` + 900s reconcile → dead-letter + PORTAL alert). | Catches any paid-but-no-seed on BOTH rails, anchored on the money event (not a downstream D1 row, which was absent in the Ashley failure). |

**The 07-03 fail-closed hardening is UNTOUCHED.** No recency/proximity/fuzzy identity fallback is reintroduced. Every new hydrate is exact-key-or-fail-closed. The 11 `strict=True` sites and the S4/S5 gating are byte-unchanged (verified by security review). This ADDS the missing pieces so legitimate seeds fire again — it does not undo the leak fix.

---

## 4. HELD / SHELVED — `/awakening` subscription JS + `/tiers` (NOT in the deploy package)

Built in the first pass on the false-casualty premise, then verification proved they are **not needed**. Left on an **unmerged, non-deployed** feature branch as a record; do NOT merge:
- Branch `stage/checkout-seed-fix-20260703` (commit `d6a0a1b2`, pushed to origin as a feature branch, NOT main). Contents: `awakening-post-payment.js` (human_email fallback + uuid threading), `awakening-chatbox.js`, `tiers/index.html` reroute.
- Patch: `to-jared/PATCH-checkout-seed-fix-client-2026-07-03.patch`.
- Status: HELD-pending-nothing (verification says not needed). Keep for reference; deploy only if future evidence shows genuine `/awakening` breakage.

---

## 5. BLOCKED — Stripe $1 one-time on `/home-test-live-1/` (Jared-gated question)

Buildability gate (spec-is-law → STOP, no fabrication). A Stripe one-time charge needs a **payment-mode** `create-checkout-session` endpoint + a confirmed **one-time price-id**. Neither exists:
- `functions/api/create-checkout-session.js` does not exist on `origin/main` (only the separate awakening-clone project has a Stripe endpoint, and it is **subscription-mode**).
- The only $1 Stripe price on record (`price_1TnmxKGdQ6Jplni4LEVwWtc2`) is `recurring=month` — a subscription, not one-time. Per prior memory, one-time Stripe 400s without the right env price-id (config fact, not code). Not guessed.

**Staged (safe, no charge path):** branch `stage/home-test-live-1-stripe-onetime-20260703` (commit `fb37db96`, pushed feature branch) — a **disabled** "coming soon" placeholder + documented drop-in server contract. Patch: `to-jared/PATCH-home-test-live-1-stripe-onetime-2026-07-03.patch`. The existing **PayPal $1 one-time on this page is a genuine one-time capture and works on its own** (its seed now fires via the server P1d/P1c fix).

**➡️ NEED FROM JARED:** *Which Stripe one-time payment-mode (`mode:'payment'`, non-recurring) price-id, and which create-checkout-session endpoint, should the `$1` one-time Stripe button wire to?* On answer, ptt wires it staged (still HELD).

---

## 6. SECURITY REVIEW — independent (security-engineer-tech)

**VERDICT: PASS-WITH-NITS. The cross-customer leak stays closed. Safe to lift the HELD deploy.**
- No fuzzy reintroduction: `_lookup_session_binding` matches `session_uuid` exactly; blank/absent key → `('',[])`; blank bindings are never written → blank cannot collide. Exact-key-or-fail-closed verified in the actual comparison logic.
- 11 `strict=True` sites + S4/S5 recency/payerName block byte-unchanged (still behind `if not strict:` + `ALLOW_S5_FUZZY_FALLBACK`).
- Dead-letter/portal alerts are built from the triggering request's own vars only — no cross-customer bleed into the shared surface.
- Binding write is keyed by the request's own sessionUuid; read is exact-key (strictly better than the removed recency scan, which leaked without knowing the UUID).
- Reconcile Timer only reads seed stores + appends jsonl + alerts — never sends a seed, never mutates a customer record. P2b amount comes from PayPal, not the client (not spoofable in the handled case).

**Non-blocking nits (file as follow-up):**
- **MEDIUM — unbounded `threading.Timer` DoS** (`purebrain_log_server.py:1127`): one 900s daemon thread per verify-payment/send-seed with no cap. Fix: bound with a semaphore, or drop per-event timers and rely on an out-of-band sweep of the durable `paid_events.jsonl`. Availability risk, not a leak.
- LOW — tmux portal-inject widens a pre-existing prompt-injection pattern (customer fields into `tmux send-keys` without `-l`); add `-l` + strip newlines.
- LOW — `is_sandbox` suppresses the dead-letter write too (observability only).
- LOW — positive client `amount` still trusted in verify-payment (pre-existing; P2b only hardens ≤0).

---

## 7. QA — sandbox E2E, PASS 4/4 (wtt-qa)

Local test instance on **port 8899** (production :8443 pid 521414 never restarted/bound, verified untouched before + after; all jsonl redirected to scratch; AgentMail/portal/Telegram neutralized; test server killed, logs clean).

| Test | Proves | Result |
|------|--------|--------|
| **A — P1d** | `/api/send-seed` with conversation + ai_name OMITTED → server hydrated **ai_name=Kaira + full conversation** from the persisted binding by exact key; `seed_sent` written, `ok:true`. This IS the regression fix: one-time/weak-key seeds WITH content, no recency fallback. | ✅ PASS |
| **B — P1c** | Non-sandbox request missing session_uuid+human_email → durable **dead-letter** (`reason=missing_session_uuid_or_human_email`) + portal alert (captured), NOT a silent 400. The Ashley invisibility is closed. | ✅ PASS |
| **C — exact-key fail-closed** | send-seed with an unknown sessionUuid while two OTHER customers' bindings sat in the store → **422 held, NO seed, NO stranger data hydrated.** Leak did not reopen. | ✅ PASS |
| **D — magic-link** | Minted async Witness-side (not in this server's send path, not sandbox-exercisable). Proximate proof = the Test-A `seed_sent` success. | ✅ PASS (honest scope) |

**Two behavioral findings (characterizations, not defects in this patch — flagged for you):**
1. **`is_sandbox=true` does NOT suppress the real AgentMail seed send** in this codebase — it only prepends a banner then sends to `aiciv-seed-inbox@agentmail.to` with the real key. Pre-existing. Any future re-test MUST fake AgentMail or a real test seed fires. Worth a hardening ticket.
2. In **sandbox** mode the dead-letter write is also suppressed (only observable in production) — production behavior is correct.

---

## 8. EXACT DEPLOY STEPS (run only on Jared's GO)

The deploy target is the server patch only (Section 3). Production runs from this same working tree via systemd, so the on-disk edits activate on restart.

```bash
# 0. Safety: confirm branch/HEAD and that the on-disk file carries the reviewed edits
cd /home/jared/projects/AI-CIV/aether
git rev-parse --abbrev-ref HEAD          # expect: feat/migrate-seed-fold-gate1-2026-06-30
git status --short tools/purebrain_log_server.py   # expect: " M" (edits present)
python3 -m py_compile tools/purebrain_log_server.py && echo "compile OK"   # must print compile OK

# 1. (recommended, source-of-truth) commit the reviewed server edit — scoped add ONLY
git add tools/purebrain_log_server.py
git commit -m "fix(seed): persist session_uuid->conversation binding + dead-letter/portal on send-seed 400 (one-time \$1 seed-fire repair)"

# 2. DEPLOY = restart the systemd unit (this is the activation lever; the LAST restart caused the regression, so this is the gated step)
sudo systemctl restart aether-logserver.service

# 3. Verify live health
systemctl is-active aether-logserver.service              # expect: active
curl -s -o /dev/null -w "%{http_code}\n" https://api.purebrain.ai/health   # expect: 200
# 4. Prove it survives one REAL job E2E before declaring recovered (idle /health is not proof):
#    watch logs/session_uuid_bindings.jsonl grow on the next real naming ceremony,
#    and confirm the next real one-time capture produces a seed_sent WITH non-empty conversation.
```

**If the working tree was wiped before deploy:** the edit is reconstructable — `git apply to-jared/PATCH-checkout-seed-fix-server-2026-07-03.patch` against a clean HEAD, then steps 1-4.

**Rollback:** `git checkout tools/purebrain_log_server.py && sudo systemctl restart aether-logserver.service` (reverts to pre-patch code).

---

## 9. PERSISTENCE (staged work will NOT evaporate)

- Server code: on disk `M` + durable `to-jared/PATCH-checkout-seed-fix-server-2026-07-03.patch` (committed with this receipt).
- Client (held): branch `stage/checkout-seed-fix-20260703` pushed to origin + `PATCH-checkout-seed-fix-client-2026-07-03.patch`.
- Client (blocked scaffold): branch `stage/home-test-live-1-stripe-onetime-20260703` pushed to origin + `PATCH-home-test-live-1-stripe-onetime-2026-07-03.patch`.
- Nothing left only in a scratch clone. IDOR files + pre-existing dirty state untouched (scoped adds only). Sole-committer discipline held; forensic read-only agent not disturbed.

---

## 10. WHAT'S AWAITING YOU

1. **GO / NO-GO on the server-patch deploy** (Section 8) — the one-time $1 seed-fire fix + observability. Passed security + sandbox QA.
2. **The Stripe one-time price-id/endpoint answer** (Section 5) — to unblock the $1 Stripe button.
3. FYI only: the MEDIUM Timer-DoS follow-up + the two AgentMail/sandbox hardening tickets (Sections 6-7). Not deploy blockers.
