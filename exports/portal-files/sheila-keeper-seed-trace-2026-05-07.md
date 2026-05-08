# Sheila / Keeper Seed Trace — 2026-05-07

**Status**: Confirmed cross-contamination. Sheila received Jay Hutton's seed.
**Bug class**: (b) Cross-contamination via `S5-payerName` fallback in `purebrain_log_server.py`.

## 1. Sheila Payment — YES, paid

- **Time**: 2026-05-07 11:54:35 UTC
- **Order**: `I-RBXHJ68JCJPL` (PayPal subscription)
- **Tier / Amount**: Partnered / $499
- **Customer email**: `Sheila@couplify.com`
- **PayPal payer name**: `Jay Whitehurst` (subscription holder paying for Sheila)
- **Evidence**: `logs/purebrain_log_server.log` 11:54:35 — `PayPal LIVE subscription API fetch OK: sub=I-RBXHJ68JCJPL, email=Sheila@couplify.com, name=Jay Whitehurst, amount=499.0`

## 2. Sheila Seed Record — DOES NOT EXIST

- Searches for `sheila` / `couplify.com` in `logs/purebrain_web_conversations.jsonl`: **0 matches**.
- Sheila never ran the naming ceremony. No `civ_name`, no `session_uuid`, no chat record.
- Per `feedback_seed_flow_never_deviate.md`: AI name MUST populate before send. There was no ceremony for Sheila to populate one — pipeline should have BLOCKED.

## 3. Jay Hutton Seed Record — Exists

- 13 conversations contain "Hutton" (e.g. `pb-post-1773879588078`, 2026-03-19).
- 26 conversations have assistant messages referencing "jay".
- Bound AI name: **Torque**. Container: `torque-jay`.

## 4. Email Actually Sent to Sheila

- **Subject**: `MAGIC LINK — Torque for Jay Whitehurst` (PayPal payer name became `human_name`)
- **Sent**: 2026-05-07 11:58:00 UTC to `sheila@couplify.com` (fired twice — duplicate)
- **Magic link**: `https://torque-jay.app.purebrain.ai/?token=7T_DXpgsffaQz-YCmnwD7QI4AJmexuLU1qFFxU9MhKg`
- **Evidence**: `logs/agentmail_monitor.log` 11:58:00–11:58:04

## 5. Bug Class Diagnosis — (b) Cross-contamination

Root cause: `tools/purebrain_log_server.py` lines 1029-1062 (Strategy 5).

```
[payment-seed] Lookup results for order I-RBXHJ68JCJPL,
  uuid=, email=Sheila@couplify.com, name=Jay Whitehurst:
  S1-orderId=0, S2-uuid=0, S3-email=0, S4-recent=0,
  S5-name=26 | Winner: S5-payerName (26 msgs)
[payment-seed] Found conversation via S5-payerName: AI name: Torque
```

Failure chain:
1. `session_uuid` empty (Sheila never chatted) -> S2 misses.
2. `Sheila@couplify.com` never in any chat -> S3 misses.
3. No recent payment-page chat -> S4 misses.
4. S5 falls back to **first-name substring match in assistant messages**. Payer first name `jay` matched 26 messages where assistants addressed Jay Hutton. System bound Sheila's payment to Jay Hutton's container.

Why dangerous: S5 mis-routes for any common first name (Jay, John, Mark, Sara). This is a token leak — Sheila has credentials to Jay Hutton's portal.

## 6. Recovery Recommendation (read-only — not executed)

1. **Invalidate token** `7T_DXpgsffaQz-YCmnwD7QI4AJmexuLU1qFFxU9MhKg` so Sheila cannot enter Jay's container. Coordinate with Witness CIV.
2. **Provision fresh container** for Sheila: new `session_uuid`, new subdomain, AI name TBD (Sheila runs ceremony or Jared picks).
3. **Send corrected magic link** to `sheila@couplify.com` via `/api/send-seed`.
4. **Notify Jay Hutton**: subdomain leaked; consider rotation.

**Code fix (CTO gate required)**:
- Disable S5, OR gate it behind email-domain match (require payer email to also appear, not just first name).
- Hard guard: if `payer_email` has no chat history AND `session_uuid` is empty, BLOCK seed and Telegram-alert Jared.

---

## Memory Search
- Searched `.claude/memory/` for `seed`, `magic.link`, `birth.pipeline`.
- Found: `feedback_seed_flow_never_deviate.md`, `feedback_magic_link_pipeline_constitutional.md`, `2026-03-07--witness-seed-spec-v2-naming-session-uuid.md`, `project_birth_pipeline_live.md`.
- Applied: AI-name-must-populate rule (violated by S5 fallback); UUID pipeline lock (violated by `session_uuid=''` path).

## Memory Written
Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--seed-cross-contamination-s5-payername-bug.md`
Type: gotcha
Topic: S5-payerName lookup leaks portal credentials when buyer first name matches a prior customer.
