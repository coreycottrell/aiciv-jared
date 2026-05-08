# `/partnered/` Capture: Apparent Regression Was Two Latent Bugs + One Destructive Reset

**Date**: 2026-05-07
**Type**: Gotcha
**Confidence**: High

## Context

Investigating Sheila Keeper's Partnered payment that bound her to Jay Hutton's portal container (cross-contamination). Jared's framing: "this worked a few days ago when Jay Whitehurst paid." Hypothesis: code regression between 5/2 and 5/7.

## Discovery

**There was no regression.** Two latent design bugs co-shipped in the same initial commit (`fbe3fc1`, 2026-04-12) and stayed masked for 25 days:

1. `tools/purebrain_log_server.py:1029-1062` — Strategy 5 fallback matches by **payer first-name substring** in any prior assistant message. Works fine when payer first names are unique in chat history. Collides when two payers share a first name.
2. `exports/cf-pages-deploy/partnered/index.html` — page **never had `logConversationToBackend('message_exchange', …)`** the way `exports/cf-pages-deploy/index.html` does (line 10821-11046 of homepage). `/partnered/` only POSTs `/api/log-conversation` once via `logPayTestData()` at line 5807, **after payment**. So pre-purchase chat lives only in browser memory; S1-S4 dispatcher lookups always miss; S5 always fires.

The "working" 5/2 Whitehurst payment had **no Spark conversation in JSONL either** (verified across both current file and stash@{0}). What actually happened: our dispatcher sent Witness an empty seed; Witness picked "Spark" as a default name; the result happened to fit because "Jay" had no prior collision in chat history yet.

## Aggravator

A `git reset --hard origin/main` cascade at 2026-05-07 15:32-15:33 UTC wiped 1141 lines of working-tree state from `logs/purebrain_web_conversations.jsonl` (verified via `stat` Birth timestamp + `git stash show stash@{0} --stat`). All four runtime state files are tracked in git: `logs/*.jsonl` and `logs/payer_emails_by_uuid.json`. They should not be — they are runtime state.

## Why It Matters

A frame of "regression" can drive a futile `git revert` hunt when the reality is **architectural drift hidden by luck**. When you cannot find a clear regression in git history between a working-then-broken window, consider:

- Was the "working" outcome luck (default-naming, recency-window happenstance)?
- Are there two latent bugs whose interaction was masked by a missing edge case?
- Did a `git reset --hard` happen in the window? Tracked state files are vulnerable.

## When to Apply

- Any "this worked yesterday" report on payment / seed / multi-stage pipelines.
- Any time the suspect commit window is empty but symptoms diverge.
- Whenever runtime state files appear in `git ls-files` — they belong in `.gitignore`.

## Concrete File Refs

- `tools/purebrain_log_server.py:963` (S5-payerName first-name extract)
- `tools/purebrain_log_server.py:1029-1062` (S5 logic + winner priority chain)
- `exports/cf-pages-deploy/partnered/index.html:5807` (sole `/api/log-conversation` POST, post-payment only)
- `exports/cf-pages-deploy/index.html:10821,10884,11024,11046` (per-message `logConversationToBackend` — the pattern `/partnered/` is missing)
- `logs/purebrain_web_conversations.jsonl` Birth = 2026-05-07 15:33:18 UTC
- Reflog reset cluster: 2026-05-07 15:32:08 → 15:33:35 UTC
- Last commit of jsonl: `fbe3fc1` 2026-04-12 (3158 lines)
- Apr-29 stash with full data: `git stash show stash@{0}` (parent `050ecb2`, 4299 lines)
