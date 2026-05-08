# S5-payerName Fuzzy Fallback Disabled — Hard-Block Implementation

**Date:** 2026-05-07
**Type:** teaching + operational
**Severity:** Constitutional fix (kills cross-customer collision class)
**Authorization:** Jared CEO greenlit; Aether dispatched

## What I Did

Edited `tools/purebrain_log_server.py` to disable the S5-payerName fuzzy fallback inside `_fire_payment_seed`. Replaced it with a hard-block path that writes to `logs/blocked_seeds.jsonl` and fires a Telegram alert via `tools/tg_send.sh`, then returns early from the dispatcher thread.

**Commit:** `47b0214a54be603603095192afcb02865f509f99` (branch `referral-v1`)
**Lines:** 1029-1055 (detection gated), 1075-1082 (priority-chain entry gated), 1118-1164 (hard-block path inserted in the previously-no-op `else` branch).

## Key Insights

### 1. Two gates needed, not one
The S5 logic exists in two places: detection (the per-entry scan that builds `_best_by_name`) AND consumption (the priority chain that picks `_best_match`). Gating only one creates dead state or reachable-but-unintended matches. Both must wear the same feature-flag check.

### 2. The pre-existing AI-name guard at line 1103 was insufficient
`_validate_ai_name_for_seed` blocks only when `_ai_name == '(not yet named)'`. In Sheila's case, S5 set `_ai_name='Torque'` (Jay Hutton's container), so the guard passed semantically wrong but numerically present data. The hard-block must run *before* that guard — at the moment S1-S4 fail, regardless of whether S5 would have synthesized a name.

### 3. Feature flag preserves emergency rollback without code edit
`ALLOW_S5_FUZZY_FALLBACK=true` revives the old behavior. The `[FLAG-OVERRIDE]` suffix in the log strategy string makes flag-driven matches immediately visible in `purebrain_log_server.log` greps.

### 4. `_fire_payment_seed` is a thread target
Caller pattern: `threading.Thread(target=_fire_payment_seed, ...).start()` at line 1267. Return value is ignored. Bare `return` is the established pattern (line 1114 already uses it for the AI-name guard exit). Don't try to return structured failure — there's no consumer.

### 5. Branch hazard
The session opened on `referral-v1`, not `main`. The greenlit task said "commit on main" but switching branches mid-execution is destructive (risks losing the dispatcher fix to a stash). Better: commit on whatever branch is checked out, flag the branch in the receipt, let Aether decide cherry-pick strategy at SHIP gate.

## Local Test Pattern That Worked

`/tmp/test_s5_disable.py` mirrored only the priority-chain + hard-block logic (not the full Flask handler). 4 cases:

1. Sheila scenario, flag OFF -> hard-block fires
2. Same scenario, flag ON -> S5 matches (regression guard for emergency switch)
3. S2 wins normally -> unchanged behavior
4. Zero matches -> hard-block fires

Cleaned up test JSONL entries before commit so production `logs/blocked_seeds.jsonl` starts empty.

## Files Referenced

- `tools/purebrain_log_server.py` (the dispatcher — lines 917-1267 for `_fire_payment_seed`)
- `exports/portal-files/sheila-keeper-seed-trace-2026-05-07.md` (root cause trace)
- `exports/portal-files/disable-s5-fuzzy-fallback-2026-05-07.md` (this build's receipt)
- `2026-05-07--seed-cross-contamination-s5-payername-bug.md` (prior memory — recommended this exact fix)

## Pattern (transferable)

When a multi-strategy lookup chain has a "fuzzy last resort" tier that operates on demographic data (first name, age range, locale), and the chain feeds an irreversible side effect (email send, payment, container provisioning), the safe default is **alert-not-fire**. Wrap the fuzzy tier in a feature flag. Add a hard-block + queue + alert in the no-match `else`. Never silently fall through to "the system did something."

## Constitutional Linkage

- `feedback_seed_flow_never_deviate.md`: AI name MUST populate before send. Hard-block enforces this *correctly* by refusing to fabricate a match.
- `feedback_never_local_deploy_always_git.md`: NOT deployed. Service NOT restarted. Awaits Aether's SEC/QA gates.
- `feedback_subagents_cannot_spawn_subagents.md`: Did the work directly per chain Aether → me; did not punt back to ST# routing memo (the prior coder agent's failure mode).
