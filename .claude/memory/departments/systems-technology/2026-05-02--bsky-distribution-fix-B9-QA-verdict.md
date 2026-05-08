# B9 QA Verdict — bsky-distribution-fix BUILD chain

**Date**: 2026-05-02
**Agent**: dept-systems-technology (synthesizing qa-engineer + ptt-qa scope)
**Type**: operational
**Topic**: B9 QA gate verification for blog-publish-hook Worker + social-api patch + bsky-session-health tool

---

## Verdict

**CONDITIONAL-PASS.** All 8 dispatched QA items verified with evidence. 0 CRITICAL, 0 HIGH new findings. 1 MEDIUM (M5) + 1 LOW (L1) discovered, both rolled into 14-day post-SHIP hardening (already routed). **READY FOR B10 SHIP** with explicit Jared-gate via conductor BOOP — no auto-fire of `wrangler deploy`.

## What was QA'd

1. **NEW Worker** `workers/blog-publish-hook/` — wrangler.toml, src/worker.js (370 lines), 2 SQL migrations, 27 tests (12 parser + 15 runTick), DEPLOY.md
2. **PATCHED Worker** `workers/social-api/src/worker.js` — `handleCreateContent` system-role bypass + metadata persistence (lines 3928–3995)
3. **NEW tool** `tools/bsky-session-health/check_and_heal.py` — Spec v2.5 self-healing session BOOP (190 lines)

## Evidence highlights (for future BOOPs)

### Item 1 — system-role override gate (security-critical)

In `social-api/src/worker.js` `handleCreateContent`:
- L3954: `let ownerUserId = sess.user_id;` (default = caller)
- L3955–3960: `if (sess.role === "system")` → reads `body.target_user_id` (override path)
- L3961–3966: `else` branch — verifies social_account_id ownership, **never references target_user_id**

The override path is structurally unreachable for non-system callers. Confirmed by line-level inspection. Test gap: no specific test asserts non-system + target_user_id is silently dropped — added to 14-day hardening sub-memo.

### Item 3 — healer empirical proof

Built a temp PROJECT_ROOT under `/tmp/healer_test_*`, injected garbage session, called `mod.write_session_string(...)`:
- Both canonical paths created: `<root>/.claude/bsky_session.txt` AND `<root>/.claude/from-jared/bsky/bsky_automation/bsky_session.txt`
- `mode=0o600` on BOTH paths (verified via `p.stat().st_mode & 0o777`)
- `check_session()` on garbage returns `status=expired, detail="not enough values to unpack..."` → `heal_signals` tuple matches → would invoke `heal()` flow

Live `heal()` not exercised (would consume real BSKY creds). Probe-before-persist pattern is correct: `c.login(user, pw)` → `export_session_string()` → `c2.login(session_string=...)` → `get_author_feed(...)` probe → `write_session_string(...)`.

### Item 5 — 27/27 GREEN

```
parser.test.mjs:  12 passed, 0 failed (exit 0)
runTick.test.mjs: 15 passed, 0 failed (exit 0)
```

GOTCHA: `package.json` "test" script only runs parser tests. To run the full 27, must invoke `node tests/runTick.test.mjs` explicitly. LOW finding L1.

### Item 8 — constitutional check

Most recent commit `4f729a3` is unrelated. No `wrangler deploy` or `wrangler pages deploy` has been executed. Build artifacts uncommitted. Production untouched. Constitutional ban on `wrangler pages deploy` honored — DEPLOY.md uses Worker `wrangler deploy` only (per CTO sign-off A6).

## New findings (rolled into hardening)

### M5 — `/status` exposes only counts, not `last_error`

Diagnosing a rotation failure currently requires direct D1 query (`SELECT slug, last_error FROM published_blog_posts WHERE status='failed'`). Recommend extending `/status` (or adding `/status/details`) during 14-day hardening sprint.

### L1 — `npm test` only runs parser tests

`package.json`: `"test": "node tests/parser.test.mjs"`. Should be `"test": "node tests/parser.test.mjs && node tests/runTick.test.mjs"`. Single-line fix.

## Sub-memo opened during B9

`inbox/dept-routing/ST-2026-05-02-target-user-id-allowlist-hardening.md` — OPEN, 14-day SLA, owners: ptt-fullstack/security-engineer-tech/ptt-qa.

This satisfies the dispatch instruction "Confirm dept-routing memo for 14-day target_user_id allowlist hardening is OPEN before B9 closes." Handshake Queue Row 72 cross-check deferred to OP# / Aether (sister-container scope, not accessible from aether filesystem).

## Pre-ship rider for B10

- DEPLOY.md is the runbook. Steps 1→7 in order.
- **DO NOT auto-fire wrangler deploy.** Conductor BOOP / Aether gates production.
- Pre-flight PRAGMA check on `metadata` column is mandatory (mitigates non-idempotent migration 0002).
- First production tick should show all-skipped (A5 backfill rule).

## Lessons (for future BUILD-chain QA dispatches)

1. **Test-runner gaps are structural risk**: `npm test` not running all suites is the kind of thing that causes "27 tests green!" claims to mean "12 tests green and we forgot the other 15." Always invoke each test file directly during QA, don't trust the npm alias.
2. **System-role overrides need explicit non-system regression tests**: It's mathematically obvious from line-level reading that `target_user_id` is unreachable for non-system callers, but a test asserting that explicitly is cheap defense-in-depth.
3. **Probe-before-persist for self-healing tools**: The healer logs in with creds, exports the session, then **logs in again with the exported session and probes** before writing to disk. If the probe fails, the canonical paths aren't corrupted by a half-good session. Adopt this pattern across self-healing infra.
4. **Cross-container memory cannot be verified from aether**: Handshake Queue Row 72 lives in `/home/aiciv/shared/`. Any QA item that depends on Triangle OS state must be deferred to Aether or operations-analyst. Document this as a known scope-limit, don't fake-attest it.
5. **A test gap is a finding, not a blocker**: "No automated test for path X" with line-level proof that path X is correct is LOW severity. Don't escalate test gaps to FAIL when the code is provably right.

## Next chain step

**B10 SHIP — devops-engineer**: prepare deploy plan from DEPLOY.md, gate via conductor BOOP.
**B11 OP# — operations-analyst**: post-ship pair-verify + Row 72 confirmation + 14-day hardening track.
