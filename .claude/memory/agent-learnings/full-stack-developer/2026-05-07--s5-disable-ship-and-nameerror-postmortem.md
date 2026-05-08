# 2026-05-07 — S5 disable shipped to production + NameError caught only via live verification

**Type:** teaching
**Domain:** SHIP gates, closure-scope variables, production verification
**Authorization:** Jared "fix the bug for sheila"

## What worked

1. **Worktree-based cherry-pick** when working tree was dirty:
   ```bash
   git worktree add /tmp/aether-main-wt main
   cd /tmp/aether-main-wt && git cherry-pick <hash>
   ```
   Avoided ALL stash/reset/clean operations on the dirty `referral-v1` working tree.
   Constitutional safety preserved (no `--hard`, no destructive ops).

2. **Pre-deploy snapshot pattern**:
   - `pgrep -af` to capture current PID
   - `tail -20` of log to capture recent state
   - `ss -tlnp | grep <port>` to confirm port binding
   - Compare `stat -c '%Y' file` to process start time to verify code reload

3. **systemd `aether-logserver.service` deploy path**:
   - WorkingDirectory + ExecStart point at the same source file in the working tree
   - Deploy = edit file (or git checkout) + `sudo systemctl restart aether-logserver.service`
   - Service auto-restarts on crash (`Restart=always`, `StartLimitIntervalSec=0`)
   - PID changes prove restart; verify with `ps -p <new_pid>`

4. **Layered safety nets caught the bug-in-the-fix**:
   - The S5 disable broke the new hard-block path (NameError)
   - But the existing `_validate_ai_name_for_seed` (Matt Keough fix, 2026-04-08) still blocked the seed
   - Constitutional guards stack — even buggy fixes don't necessarily ship customer-facing breakage

## What didn't work

1. **Local QA missed a closure-scope NameError.** The original BUILD f-string referenced `{amount}` and `{tier}` — but those names don't exist in the `_fire_payment_seed` closure. Actual names are `_seed_amount` and `_seed_tier` (set at lines 875-876 of `tools/purebrain_log_server.py` from `data.get('tier'/'amount')`). My local test harness redefined `amount`/`tier` as test-script-level locals, masking the bug.

2. **Test-timing artifacts almost hid the bug.** First two production synthetics had S4 candidates within the 30-min recency window, so the priority chain stopped at S4 (winner != none, so the new else branch never executed). I had to wait 4+ minutes for the S4 candidate to age out before the bug surfaced.

3. **Outer try/except masked the NameError as a generic warning** (`Conversation lookup failed: name 'amount' is not defined`) instead of crashing loudly. Took multiple log greps to find it because I was looking for `BLOCKED-NO-MATCH` not `Conversation lookup failed`.

## Key learnings (TRANSFERABLE)

1. **Closure-scope variables ≠ outer-scope variables.** When adding f-strings or new code paths inside a closure (`def _fire_payment_seed`), copy variable names from the immediate enclosing scope (lines 875-876 here), NOT from the request handler scope (line 590-602 here).

2. **Test harnesses must use the SAME variable names as production.** If your test redefines `amount = '499'`, you mask NameErrors that would surface in the closure.

3. **Outer try/except blocks in long-running threads silently swallow bugs.** The pattern:
   ```python
   try:
       # 200 lines including new code
   except Exception as _err:
       logger.warning(f'... {_err}')
   ```
   means ANY exception in the new code becomes a warning, not a crash. **Always grep for "WARNING" lines after deploy**, not just for the new code's intended log lines.

4. **Production verification requires waiting for environmental conditions to clear.** S4 has a 30-min recency window — to test "all strategies miss", I had to wait until no payment-page conversation existed in the last 30 min. Plan for this when designing production verification.

5. **Telegram alerts as deploy-confirmation signal.** Sending a heads-up to Jared BEFORE the synthetic + a confirmation AFTER means he can see the test happen on his phone. The `🚨 SEED BLOCKED` alert text doubles as both a normal-operation notice AND the verification of the deploy.

## File paths referenced

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` — production dispatcher
- `/etc/systemd/system/aether-logserver.service` — systemd unit
- `/home/jared/projects/AI-CIV/aether/logs/blocked_seeds.jsonl` — new manual-review queue
- `/home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log` — log stream (single file, append-only)
- `/home/jared/projects/AI-CIV/aether/tools/tg_send.sh` — Telegram alert wrapper
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/s5-disable-ship-receipt-2026-05-07.md` — SHIP receipt

## Commits

- `48d6b8a` (main) — S5 disable + hard-block path (original BUILD)
- `775c840` (main) — NameError hot-fix (`amount` -> `_seed_amount`, `tier` -> `_seed_tier`)
- `47b0214a` (referral-v1) — original BUILD before cherry-pick
- `629ad4b` (referral-v1) — hot-fix before cherry-pick

## Future-self checklist for similar SHIP gates

- [ ] Diff the cherry-pick before restart — look for any variable referenced in the new code, confirm it's defined in the same scope
- [ ] After deploy, grep logs for ALL of: new INFO lines, new CRITICAL lines, AND `WARNING.*Exception` patterns
- [ ] If outer try/except wraps the new code, intentionally trigger it locally to confirm exception path also works
- [ ] If the verification depends on environmental timing (recency windows etc.), document the wait period in the receipt
