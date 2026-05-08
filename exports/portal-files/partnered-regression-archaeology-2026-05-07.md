# `/partnered/` Capture Pipeline — Regression Archaeology

**Date**: 2026-05-07
**Trigger**: Sheila Keeper paid $499 Partnered (PayPal `I-RBXHJ68JCJPL`) → received Jay Hutton's portal credentials. Jared said "this worked when Jay Whitehurst paid a few days ago."
**Verdict**: **No code regression.** Two design bugs co-shipped 4/12 finally collided today. Plus a `git reset --hard` cascade at 15:33 UTC that wiped 25 days of state files.

---

## 1. Working Baseline — Jay Whitehurst, 2026-05-02 13:44 UTC

Witness emitted `MAGIC LINK — Spark for Jay Whitehurst`, container `spark-jay.app.purebrain.ai`, sent to `jay@couplify.com`. Critical: **"Spark" appears nowhere in `purebrain_web_conversations.jsonl`** — not in current file (3164 lines) nor in stash@{0} (4299 lines through 2026-04-29 17:21). Zero "Spark" entries ever. So our local dispatcher S1-S5 also missed on May 2; the seed reached Witness with `(No conversation found)` and **Witness picked "Spark" as a default name**. May 2 was luck, not a working pipeline.

## 2. Suspect Files — Audit

| File | Last meaningful change | Verdict |
|---|---|---|
| `tools/purebrain_log_server.py` | `fbe3fc1` 4/12 (initial — S1-S5 verbatim) | Not regressed |
| `exports/cf-pages-deploy/partnered/index.html` | `557f307` 5/7 16:29 (post-incident `pb_ref`) | Not regressed |
| `logs/purebrain_web_conversations.jsonl` | Tracked, 3158 lines at `fbe3fc1` | Reset-wiped today |
| `logs/seed_events.jsonl`, `payer_emails_by_uuid.json` | Tracked, capped Apr 11/12 | Reset-wiped today |

No commit altered `log-conversation`, S1-S5, or `session_uuid` between 5/2 and 5/7.

## 3. Destructive Reset — 5/7 15:32-15:33 UTC

`git reflog` during a `referral-v1` branch maneuver:

```
HEAD@{15:32:08} reset: moving to origin/main   ← jsonl 4299→3158
HEAD@{15:33:18} reset: moving to HEAD
HEAD@{15:33:35} reset: moving to 11443b58
```

`stat logs/purebrain_web_conversations.jsonl` Birth = **2026-05-07 15:33:18 UTC**, all four state files reverted to Apr 11-12 snapshots. Did NOT cause Sheila's misroute (her seed fired 11:54, before reset) but destroys evidence and breaks future S1-S4 lookups until repopulated.

## 4. Silent-Failure Mode — Architectural

- **`/partnered/index.html` never had `logConversationToBackend('message_exchange', …)`** — that callback exists only in `exports/cf-pages-deploy/index.html` (lines 10821-11046). `/partnered/` POSTs `/api/log-conversation` once, from `logPayTestData()` at line 5807, **after payment**. Pre-purchase chat lives in `window._pbPrePurchaseSession.conversationHistory` in browser memory only.
- Across all git history, `/partnered/` has logged exactly **1 message_exchange** vs 518 from other pages.
- S5-payerName (`purebrain_log_server.py:1029-1062`, since `fbe3fc1`) papered over this silence by guessing from old chats. Unique payer first name → S5 lands right (5/2 = lucky). Two payers share a first name → S5 collides. Sheila got Torque's container.

## 5. Recovery — Forward-Fix, Do Not Revert

Revert wins nothing: working-tree data was never committed (irrecoverable beyond stash@{0}), and `557f307` is unrelated.

1. **Stop the leak**: invalidate token `7T_DXpgs…M4MhKg`, provision fresh container for Sheila (CTO + Witness gate).
2. **Disable S5-payerName** at `purebrain_log_server.py:1060-1062`. Replace with hard guard: `session_uuid` empty AND `payer_email` absent from chats AND S4-recent empty → BLOCK seed + Telegram-alert. Per `feedback_seed_flow_never_deviate.md`, name-must-populate is constitutional.
3. **Port `logConversationToBackend(eventType, data)` from homepage into `/partnered/`** so per-message capture lands in JSONL during chat, not after payment.
4. **Untrack state files**: add `logs/*.jsonl` + `logs/payer_emails_by_uuid.json` to `.gitignore`. Runtime state, never code.

## 6. Constitutional Monitoring Gap

- **S5-firing canary** — any `Winner: S5-payerName` log line Telegram-reds Jared.
- **Capture-rate watchdog** — `/api/verify-payment` 200 with no `/api/log-conversation` for that `session_uuid` in prior 30 min → BLOCK seed.
- **Pre-reset git-clean check** — `git status logs/` before `git reset --hard` would have surfaced 1141 lines about to die.

---

## Culprit + Recommendation

**Culprit commit**: `fbe3fc1` (2026-04-12). Co-shipped two design bugs: S5-payerName fuzzy fallback + `/partnered/` page lacking per-message capture. Their interaction stayed masked for 25 days until two payers shared a first name. Sheila — payer-of-record "Jay Whitehurst" — was the first collision.

**Aggravator**: today's `git reset --hard origin/main` at 15:32:08 UTC wiped 1141 working-tree lines of state JSONLs.

**Recommendation**: forward-fix per Section 5. Do NOT revert `557f307`. S5 disablement + `/partnered/` per-message capture are the two CTO-gated patches.

---

## Memory Search

`.claude/memory/` for `seed`, `partnered`, `payerName`. Found `feedback_seed_flow_never_deviate.md`, `feedback_magic_link_pipeline_constitutional.md`, `2026-05-07--seed-cross-contamination-s5-payername-bug.md`. Applied: name-must-populate (S5 substring violates); UUID lock (page emits UUID but capture never lands → S2 always misses on /partnered/).

## Memory Written

Path: `.claude/memory/agent-learnings/code-archaeologist/2026-05-07--partnered-capture-not-regressed-but-state-files-wiped.md`
Type: gotcha
Topic: `/partnered/` per-message capture never wired; S5-payerName hid the silence; `git reset --hard` wiped tracked state JSONLs.
