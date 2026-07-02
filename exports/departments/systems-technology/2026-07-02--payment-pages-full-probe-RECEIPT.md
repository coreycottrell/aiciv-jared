# RECEIPT — Full Money-Path Payment-Page Probe (STAGED, not activated)

**Date:** 2026-07-02
**Agent:** devops-engineer
**Branch:** feat/migrate-seed-fold-gate1-2026-06-30 (built on top of HEAD 4e29894)
**Status:** STAGED + COMMITTED to branch. NOT pushed. NOT deployed. No daemon activated.

---

## What this is

An additive overnight probe that expands payment-page coverage to ALL 9 money-path
pages and asserts far more than "HTTP 200". Catches the empty-seed / broken-logging
regression class the NIGHT it happens (this class rotted ~5 weeks unnoticed).

Does NOT replace or weaken existing checks:
- `tools/verify-payment-pages.sh` (live pricing / banned plan-ID gate) — untouched
- `tools/verify-payment-pages-pbsessionuuid.sh` (static pbSessionUuid gate) — untouched
- BOOP `nightly-payment-pages-qa` — untouched (still `enabled:false` from the 06-24 cutover pause)

---

## Files staged (absolute paths)

1. `/home/jared/projects/AI-CIV/aether/tools/verify-payment-pages-full.py`
   — the probe (new file, executable).
2. `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/payment-pages-full-probe-BOOP-snippet.json`
   — the PROPOSED scheduler entry (a snippet to merge; NOT applied to
   `.claude/scheduled-tasks-state.json`).
3. `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/2026-07-02--payment-pages-full-probe-RECEIPT.md`
   — this receipt.

`.claude/scheduled-tasks-state.json` was deliberately NOT modified.

---

## The 3 assertions (per page)

| # | Assertion | How it's checked | FAIL label |
|---|-----------|------------------|------------|
| A | Page loads | HTTP 200 via GET (CF Pages 404 on HEAD) | `page-not-loading` |
| B | Checkout is LIVE | PayPal SDK button (`paypal.com/sdk/js` + `paypal.Buttons`) and/or Stripe embedded checkout (`js.stripe.com` / `EmbeddedCheckout` / `create-checkout-session`) detected in served HTML. JS-rendered Next.js pages (/awakening, /sme-awakening) are curl-blind → asserted via headless DOM (PayPal iframe / Stripe frame) in `--render` mode. Also FAILs if `sk_live` leaks into client HTML. | `checkout-not-live` (or `sk_live-leaked`) |
| C | Conversation-logging + identity-linkage | POST a synthetic naming-conversation to `https://api.purebrain.ai/api/log-conversation`, then (C-1) confirm it PERSISTS to the seed-read store `logs/purebrain_web_conversations.jsonl`, and (C-2) confirm it is STRONG-KEY findable by its sessionUuid (replica of the strict `_lookup_naming_conversation` S2 branch). | `conversation-not-persisted` / `not-strong-key-findable` |

Assertion (C) runs ONCE per run (the logging endpoint + store + lookup are shared
infra across all pages; testing once proves the class). The linkage key traced from
`tools/purebrain_log_server.py`: `log_conversation()` L1212 writes the record
(L1258-1281), the strong key `sessionUuid` is carried in `metadata.sessionUuid` (and
mirrored to top-level `session_id`), and `_lookup_naming_conversation` L4477 (strict
guard L4549) binds it. The synthetic record is written in the SAME shape a real
frontend record uses so the S2 lookup binds it.

---

## Synthetic-capture SAFETY (no real seed / payment / customer)

The synthetic sessionUuid is prefixed `BOOP-SYNTH-<uuid4>` and is structurally
UNBINDABLE to any real order — every strong/weak key in the seed lookup is
unreachable for it:

| Seed key | Why the synthetic record can never match a real order |
|----------|-------------------------------------------------------|
| S0 account_id | not sent → unreachable |
| S1 orderId | not sent → unreachable |
| S2 sessionUuid | `BOOP-SYNTH-<uuid4>` → only matches ITSELF |
| S3 payer-email-in-content | no email in message content → unreachable |
| S4 recency | page_url is a NON-payment synthetic marker AND only 4 msgs (S4 needs a payment-page URL AND >5 msgs) → unreachable on two counts |

Additional guards:
- The probe NEVER calls `/api/verify-payment`, `/api/send-seed`,
  `/api/finish-wakeup`, or `/api/create-checkout-session`. It only exercises the
  conversation-LOG write + a read-only lookup replica.
- `--dry-run` writes the synthetic record to a TEMP COPY of the store, never to the
  production file, and runs the lookup against that copy (CI-safe).
- Playwright cleanup (`pkill chromium/playwright`) runs after every `--render` page.

---

## Verification performed this session (evidence)

- `--dry-run --no-alert --only-conversation`: PASS — synthetic persisted to a temp
  copy and was strong-key findable (ai_name='SynthProbeAI', 4 msgs). EXIT 0.
- `--dry-run --no-alert` (full 9-page live loop + dry-run section C): all pages
  asserted correctly. EXIT 0. Live calibration results:
  - Pages 2-6 (insiders, old-pricing, tiers, partnered-how, unified-how): PayPal + Stripe both WIRED in served HTML → checkout LIVE.
  - Page 7 (ce/check-out ?ref): PayPal WIRED (Stripe not required here) → checkout LIVE.
  - Pages 1 (/awakening/) & 8 (/sme-awakening ?aid): Next.js React, curl-blind → INFO in fast mode; assert via `--render`.
  - Page 9 (/migrate-awakening): 404 today → PENDING/skip-until-live (config `pending:true`).
- The dry-run copied the REAL production store (3290 records) and ran the exact
  persistence + strong-key lookup against it → proves (C-1)/(C-2) logic against
  real data shape.
- NOT exercised this session (intentional): the live POST round-trip to
  `api.purebrain.ai/api/log-conversation`, because the seed-read store is
  git-tracked and STAGE-only discipline forbids polluting the tracked file. The
  live POST leg is exactly what the activated nightly BOOP performs.

---

## EXACT Jared-GO activation steps (nothing below was done)

1. **Merge the scheduler entry**: copy the `nightly-payment-pages-full-probe`
   object from
   `exports/departments/systems-technology/payment-pages-full-probe-BOOP-snippet.json`
   into the `tasks` map of `.claude/scheduled-tasks-state.json`.
2. **Enable it**: set that entry's `"enabled": true` (leave the others as-is).
3. **Restart the BOOP executor daemon** so it picks up the new schedule
   (committed != live for daemons). The executor reads
   `.claude/scheduled-tasks-state.json` and dispatches on `agent=` /`command=`.
4. **(Optional) confirm portal alerting**: `PORTAL_ALERT=1` is the default; ensure
   the portal server (localhost:8097) is up so `tools/portal_deliver.sh` delivers
   failure reports.
5. **First-run smoke**: `python3 tools/verify-payment-pages-full.py --render`
   manually once and confirm EXIT 0 (this WILL write one inert `BOOP-SYNTH-` line
   to `logs/purebrain_web_conversations.jsonl` — expected, harmless, unbindable).

To activate the future page (9): flip `pending: true` → `false` in the PAGES config
in `tools/verify-payment-pages-full.py` once `/migrate-awakening` is live (one line).
