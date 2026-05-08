# S5 Disable — SHIP Receipt

**Date:** 2026-05-07
**Specialist:** wtt-fullstack
**Authorization:** Jared (CEO) — "fix the bug for sheila"
**Status:** SHIPPED-AND-VERIFIED

## Cherry-pick result

Two commits on `main` (via `/tmp/aether-main-wt` worktree to avoid touching dirty `referral-v1`):

| referral-v1 | main | Purpose |
|---|---|---|
| `47b0214a` | `48d6b8a` | Disable S5 + hard-block (original BUILD) |
| `629ad4b` | `775c840` | NameError hot-fix found during prod verify |

No conflicts. Pre-commit hooks ran (not bypassed).

## SEC review

PASS with one note. Attack surface reduced (warning -> explicit return). Telegram alert goes to Jared's chat_id only (private). subprocess uses list form (no shell injection). No new credentials. Feature flag defaults false. Path uses `__file__`-derived dirs, no traversal.

NOTE: `logs/*.jsonl` is not gitignored; existing tracked `.jsonl` files set the precedent. Recommend adding `logs/blocked_seeds.jsonl` to .gitignore in a follow-up. Not a blocker.

## QA results

Local synthetic (`/tmp/qa_s5_disable.py`) against cherry-picked main: 4/4 PASS — Sheila-flag-OFF blocks, S3 winner normal, empty blocks, Sheila-flag-ON re-enables S5 with `[FLAG-OVERRIDE]`. JSONL had 2 entries for the 2 expected blocks.

## SHIP path

Production = `aether-logserver.service` systemd unit on this host. WorkingDirectory + ExecStart point at the same source file in this working tree. Deploy = `sudo systemctl restart aether-logserver.service`. Restarted twice (initial 18:17:09, hot-fix 18:28:42). Port 8443 stayed up. PID 1863094 -> 3054029 -> 3059337.

Not a customer container. Not a CF Pages deploy. No SSH or scp.

## Production verification

Sent 4 synthetics to `https://127.0.0.1:8443/api/verify-payment`. First three confirmed S5 disable (`S5-name=0 | Winner != S5`) but did not exercise the new hard-block code: an S4 candidate was within the 30-min window, then a second test exposed the NameError. Final synthetic after hot-fix:

- **Order:** `QA-TEST-S5-FIXED-2026-05-07`
- **Lookup:** `S1=0 S2=0 S3=0 S4=0 S5=0 | Winner: none`
- **Hard-block log:** `CRITICAL [payment-seed] BLOCKED-NO-MATCH: order=QA-TEST-S5-FIXED-2026-05-07 ... amount=499.00 tier=Partnered. S1-S4 empty; S5 fuzzy fallback disabled.`
- **JSONL written:** `logs/blocked_seeds.jsonl` 392 bytes, 1 entry, full payload + `requires_action: manual review`

Comparison vs pre-fix (06:36 UTC same day): old code logged `S5-name=25 | Winner: S5-payerName (25 msgs)` for Henrik Sylvest -> seed sent with wrong AI name. New code: S5 cannot win regardless of match count.

## Telegram alert confirmation

Real production hard-block alert delivered to Jared (chat_id 548906264) as `message_id 49857`:

> 🚨 SEED BLOCKED: order=QA-TEST-S5-FIXED-2026-05-07 payer=qa-fixed@aether-test-noexist.invalid amount=$499.00 tier=Partnered. S1-S4 all empty; S5 disabled. Manual review required. See logs/blocked_seeds.jsonl

Plus three other messages (heads-ups + final SHIPPED-AND-VERIFIED summary).

## NameError postmortem

Original BUILD (47b0214a) referenced `{amount}` and `{tier}` in the hard-block f-strings. Those names do not exist in the `_fire_payment_seed` closure — actual variables are `_seed_amount` and `_seed_tier` (assigned at lines 875-876 from `data.get('tier'/'amount')`). Local QA missed it because the test harness redefined `amount`/`tier` as locals. Production exposed it: NameError raised, outer `except` swallowed as `"Conversation lookup failed: name 'amount' is not defined"`, control fell through to the existing `_validate_ai_name_for_seed` guard (Matt Keough fix). Effect: hard-block didn't fire, but seed was still blocked by the older guard. Not a regression. Hot-fix swapped names in three places.

Lesson for memory: when adding a closure-scoped log/alert, copy variable names from the immediate enclosing scope, not from the request handler. Local tests that use top-level globals can mask NameErrors that only surface in the closure.

## Status

**SHIPPED-AND-VERIFIED.**

- S5 disabled in prod (verified by `S5-name=0` always)
- Hard-block path: log + JSONL + Telegram all firing
- `ALLOW_S5_FUZZY_FALLBACK=true` available for emergency re-enable (not set)
- Sheila-class collision permanently impossible

Commits on main: `48d6b8a`, `775c840`.
