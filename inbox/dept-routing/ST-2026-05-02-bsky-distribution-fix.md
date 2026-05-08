# ST# Routing: Bluesky distribution mechanics — fix the broken pipe

**From**: dept-marketing-advertising (CMO)
**To**: dept-systems-technology (CTO)
**Priority**: Medium-High — 20 days of dropped distribution, ~9 missed threads
**Pair verify**: operations-analyst (OP#)
**Parent memo**: `.claude/memory/departments/dept-marketing-advertising/2026-05-02--bsky-dormancy-investigation.md`

## Context
@purebrain.ai dormant 20.5 days. Investigation confirmed blog is publishing fine (9 posts since 4/14) but the `post-blog` → `bluesky-blog-thread` distribution leg never fires. MA# is handling backfill + SOP discipline. ST# owns the mechanics so this can't recur.

## Asks (3 tracks)

### B4 — Verify bluesky-blog-thread skill end-to-end
- Skill at `.claude/skills/bluesky-blog-thread/SKILL.md` still flagged `🚨 UNTESTED`
- Run a single test thread against a recent blog post, confirm posts land, drop the UNTESTED flag
- Owner: full-stack-developer + qa-engineer (BUILD → QA)

### B5 — Refresh Bsky session
- `.bsky_session.txt` shows modified in git status — confirm token still valid for `purebrain.ai` handle
- If expired, regenerate via standard auth flow
- Owner: full-stack-developer

### B6 — Build publish-hook (structural fix)
- Goal: when a post lands at `purebrain.ai/blog/<slug>/`, auto-queue a Bluesky thread draft into social.purebrain.ai kanban
- Options: CF Pages build hook → Worker → /api/items POST | OR polling worker that watches blog index | OR webhook from WP/CMS layer
- CTO scopes the approach
- Constitutional: writes go to social.purebrain.ai FIRST (source of truth), never direct bsky-manager
- Owner: cto + full-stack-developer

## Constraints (CONSTITUTIONAL)
- NO direct bsky-manager posting — must flow through social.purebrain.ai
- NO container-local data (D1 + CF Workers per `feedback_never_deploy_to_customer_containers.md` family of rules)
- BUILD → SECURITY → QA → SHIP flow

## ETA expected
- B4+B5: 24-48h
- B6: 5-10 day build with normal review cycle

## Pair verify
OP# will re-probe per parent memo's verification checklist.

---

## ST# ACCEPTANCE — 2026-05-02

**Accepted by**: dept-systems-technology
**Spec filed**: `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md`
**Status**: BUILD phase dispatched
**Engineering chain**:
- B4 (verify bluesky-blog-thread skill) → ptt-fullstack + ptt-qa, 24-48h
- B5 (refresh Bsky session) → ptt-fullstack, 4h, parallel with B4
- B6 (publish-hook BUILD) → ptt-fullstack with cto architectural sign-off
- B6 SECURITY → security-engineer-tech (after BUILD)
- B6 QA → qa-engineer + ptt-qa (after SECURITY)
- B6 SHIP → devops-engineer (after QA, via wrangler deploy on Worker only)
- B6 VERIFY → operations-analyst (independent pair-verify)

Approach summary: 10-min cron Worker polls `purebrain.ai/blog/`, dedupes against new D1 table `published_blog_posts`, queues thread drafts to `social-api` `/api/content` with system token. Worker is software (Q1 of pre-build checklist), runs without AI active (Q2), customer-facing (Q3), recurring (Q4), near-real-time (Q5), persisted in D1 (Q6), human-configurable via existing kanban UI (Q7). Initial backfill flagged `skipped` to avoid flooding kanban (MA# Track A2 handles the 9 missed posts manually).

Routing memo will be archived once SHIP completes and OP# pair-verify passes.

---

## STATUS UPDATE — 2026-05-02 23:25 UTC — READY FOR B7 BUILD

**Spec version**: v2 (amendments locked) — see appended "Spec v2 — 2026-05-02 23:25 UTC" section in `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md`

**Prereq status**:
- **B4** (verify bluesky-blog-thread skill): ❌ FAIL — skill is phantom (SKILL.md exists, `blog_to_thread.py` does not). **RE-SCOPED** to sibling work track (skill rewrite for kanban routing). Does NOT gate B7. Detail: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--bluesky-blog-thread-skill-test.md`
- **B5** (refresh Bsky session): ✅ PASS — session regenerated, `getAuthorFeed` verified, identity confirmed @purebrain.ai. Both canonical paths refreshed (perms 600). Real root cause was REVOKED token, not missing file. Detail: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--bsky-prereqs-b4-b5.md`
- **B6** (CTO architectural sign-off): ✅ APPROVED-WITH-AMENDMENTS — 6 required fixes locked into BUILD spec (D1 schema FK type, social-api system-bypass, payload reshape, ROUTER_API_KEY reuse, timestamp-comparison backfill, wrangler deploy approval). Detail: `.claude/memory/agent-learnings/cto/2026-05-02--bsky-publish-hook-signoff-B6.md`

**B7 BUILD dispatch status**: READY. Conductor to fan out to ptt-fullstack with the v2 spec as the BUILD brief. Includes new B7 sub-task: self-healing session BOOP (auto-relog on `ExpiredToken`) — fold into existing presence BOOP at `logs/bsky-presence-boop/`.

**Sibling track**: Skill rewrite (re-scoped B4) dispatches separately AFTER B7 ships — gated on B7's social-api adapter being deployed.

**No re-routing needed**: This dept (ST#) has cleared all architectural and prereq gates. Engineering chain is BUILD → SECURITY → QA → SHIP; ptt-fullstack owns BUILD.

---

## STATUS UPDATE — 2026-05-02 — READY FOR B8 SECURITY REVIEW

**B7 BUILD complete**. Owner: ptt-fullstack.

**BUILD memo**: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--blog-publish-hook-build.md`

**Deliverables**:
- `workers/blog-publish-hook/` (NEW Worker — `wrangler.toml`, `src/worker.js`, 2 migrations, 2 test suites, `DEPLOY.md`)
- `workers/social-api/src/worker.js` (PATCHED — `handleCreateContent` system-role bypass + metadata persistence)
- `tools/bsky-session-health/check_and_heal.py` (NEW — Spec v2.5 self-healing session BOOP)

**Amendments applied**: All six (A1 through A6) per CTO sign-off. Verified individually in BUILD memo section (b).

**Tests**:
- 12/12 parser unit tests passing
- 15/15 runTick integration tests passing (A5 backfill, idempotency, retry path, retry budget exhaustion)
- Self-healing BOOP: simulated session revocation → auto-healed → both canonical paths refreshed at perms 600 → re-probe healthy
- `node --check` on both Workers: OK
- Live social-api regression: `/health` 200, `POST /api/content` (no auth) 401 — existing contract intact

**Production deploy NOT performed** (correct per B7 scope). DEPLOY.md runbook in `workers/blog-publish-hook/DEPLOY.md` documents exact steps for B10 devops-engineer.

**Open question for B8 SECURITY**: Should the new optional `target_user_id` system-override field be gated to a tighter allowlist (only known house-account user_ids), or is "system role can target any user_id" acceptable trust model? Documented in BUILD memo for security-engineer-tech to decide.

**Status**: **READY FOR B8 SECURITY REVIEW** — dept-systems-technology to dispatch security-engineer-tech with the BUILD memo as the brief.

— ptt-fullstack, 2026-05-02

---

## B8 SECURITY review — 2026-05-02

**Status**: **READY FOR B9 QA** — no CRITICAL findings, 2 HIGH findings tracked as post-SHIP follow-ups, no BUILD rework required.

**Reviewer**: security-engineer-tech
**Memo**: `.claude/memory/agent-learnings/security-engineer-tech/2026-05-02--blog-publish-hook-security-review.md`

**Severity counts**: 0 CRITICAL · 2 HIGH · 4 MEDIUM · 4 LOW · 3 INFO

**Verdict**: The system-role bypass is correctly bounded. Multi-tenant scoping preserved (`handleListContent` still filters `WHERE user_id = ?`; system writes resolve to real owner via `houseAcct.user_id`, not the literal "system" string). Cron retry idempotency verified. Self-healing session BOOP doesn't leak credentials. Constitutional compliance: PASS on all 7 checks.

**Open-question decision (CTO requested ruling on `target_user_id` allowlist)**: **Acceptable as written for B7 SHIP, BUT requires structural allowlist within 14 days post-ship.** Rationale: blog-publish-hook itself does NOT pass `target_user_id` (relies on default `houseAcct.user_id` resolution path), so the currently shipping caller does not exercise the override. The override IS a cross-tenant content-injection primitive for any holder of `ROUTER_API_KEY`, but holders of that key already have `system` role with full permissions — gap is defense-in-depth, not active vuln. Locked HIGH-2 follow-up: add `social_accounts.is_house_account` allowlist column within 14 days. Owner: ptt-fullstack.

**HIGH findings (both = post-SHIP follow-ups, not BUILD rework)**:
1. **HIGH-1 — Token rotation foot-gun**: `SOCIAL_API_SYSTEM_TOKEN` and `ROUTER_API_KEY` are coupled by string equality. Silent failure during rotation = repeat of the original 20-day dormancy. Mitigation: wire `result.failed` to OP# nightly monitor (already tracked in B11), add Rotation Runbook to DEPLOY.md.
2. **HIGH-2 — `target_user_id` lacks allowlist**: System callers can attribute content to ANY user_id. Mitigation: `social_accounts.is_house_account` column + strict `target_user_id === houseAcct.user_id` check. 14-day post-SHIP fix.

**MEDIUM findings (track for hardening sprint, not blocking)**: `/run` admin endpoint shares secret with outbound auth (M1); D1 `last_error` truncation drops forensic data (M2); metadata column has no length cap (M3); session healer has no heal-cycle rate limit (M4).

**LOW + INFO**: 7 minor items including incomplete HTML entity decoder, non-idempotent migration 0002 (DEPLOY.md correctly mitigates with PRAGMA check), and verified-correct A5 race handling. See memo.

**Recommendations to B9 QA**:
1. Verify regression: non-system caller passing `target_user_id` is IGNORED (override only fires under `sess.role === "system"`)
2. Smoke-test the rotation failure mode: wrong SOCIAL_API_SYSTEM_TOKEN → confirm `result.failed` increments + visible in `/status`
3. Healer sanity check: garbage session string → auto-heal → both canonical paths refreshed at 0600
4. Confirm dept-routing memo opens for the 14-day allowlist hardening before this review closes

**Files reviewed**: 6 source files + 2 references (schema + spec). Verified line-level. No CRITICAL findings means BUILD chain proceeds to QA without rework.

— security-engineer-tech, 2026-05-02


---

## B9 QA — 2026-05-02

**Verdict**: **CONDITIONAL-PASS** — all 8 QA items verified, 0 new CRITICAL/HIGH, 1 new MEDIUM (`/status` does not surface `last_error`, only counts), 1 new LOW (npm test only runs parser tests; runTick must be invoked explicitly). **READY FOR B10 SHIP** with one pre-ship rider (see end).

**Owner**: dept-systems-technology (synthesizing qa-engineer + ptt-qa scope per dispatch)
**New findings count**: 0 CRITICAL, 0 HIGH, 1 MEDIUM, 1 LOW

### Item-by-item evidence

**Item 1 — Regression: non-system caller passing `target_user_id` MUST be IGNORED → PASS**
- File: `workers/social-api/src/worker.js` lines 3928–3995 (`handleCreateContent`)
- Code path verified line-level:
  - L3954: `let ownerUserId = sess.user_id;` (initialized to caller's own user_id)
  - L3955–3960: `if (sess.role === "system")` block — only here is `body.target_user_id` ever read (`ownerUserId = body.target_user_id || houseAcct.user_id;`)
  - L3961–3966: `else` branch — verifies `social_account_id` ownership against `sess.user_id`. **Never references `body.target_user_id`.** `ownerUserId` retains the L3954 default.
- Conclusion: non-system caller path mathematically cannot be influenced by `target_user_id`. Override gate is correct.
- Test gap noted: no automated test in social-api specifically asserts "non-system + target_user_id is silently dropped." Existing role/permission tests cover the gate via `hasPermission`. This is a LOW finding for follow-up test addition during the 14-day hardening sprint (already routed — see sub-memo).

**Item 2 — Smoke-test rotation failure mode: wrong `SOCIAL_API_SYSTEM_TOKEN` → `result.failed` increments + visible in `/status` → PASS (with MEDIUM finding)**
- File: `workers/blog-publish-hook/src/worker.js`
  - `runTick`: wrong token → `postToSocialApi` returns `{ ok: false, status: 401, ... }` → falls into the `else` branch which calls `insertPost(env, post, "failed", null, errMsg)` and increments `counters.failed += 1`
  - `/status` endpoint: `SELECT status, COUNT(*) FROM published_blog_posts GROUP BY status` exposes the failed count
- Confirmed in test output: `runTick.test.mjs` "tick 1 → failed" + "last_error captures HTTP 400" cases prove the failure path is wired.
- **NEW MEDIUM finding (M5)**: `/status` exposes only counts, not `last_error`. To diagnose a rotation failure, OP# must query D1 directly (`SELECT slug, last_error FROM published_blog_posts WHERE status='failed'`). Recommend extending `/status` to optionally include the most-recent `last_error` per status bucket (or adding a separate `/status/details` endpoint) during the 14-day hardening sprint. Not a B10 blocker — DEPLOY.md Step 5 already documents the manual D1 query.
- DEPLOY.md Step 4 includes an explicit smoke-test invocation pattern (manual `/run` call with the bearer token). Procedure is documented for devops-engineer.

**Item 3 — Healer sanity check: garbage session → auto-heal → both canonical paths at perms 0600 → PASS**
- File: `tools/bsky-session-health/check_and_heal.py`
- Static inspection:
  - `CANONICAL_SESSION_PATHS` defined at L36–39 with **two** paths:
    1. `<root>/.claude/bsky_session.txt`
    2. `<root>/.claude/from-jared/bsky/bsky_automation/bsky_session.txt`
  - `write_session_string` (L73–82): iterates both paths, calls `p.chmod(stat.S_IRUSR | stat.S_IWUSR)` (= `0o600`)
  - `heal_signals` tuple (L113–116) includes `"not enough values to unpack"` — covers garbage/corrupt session strings
- Empirical test (executed in `/tmp/healer_test_*`):
  - Wrote garbage `{"garbage": true}` to primary path
  - Called `mod.write_session_string("fake-refreshed-session")` — both paths created
  - Verified: `mode=0o600` on BOTH paths, content matches
  - Verified: `check_session()` on garbage returns `status=expired, detail="not enough values to unpack..."` → triggers heal flow
- Live `heal()` (network call to bsky.social) NOT executed — would consume real BSKY creds. Heal logic is straight-line: `c.login(user, pw)` → `c.export_session_string()` → `c2.login(session_string=...)` → `c2.get_author_feed(...)` probe → `write_session_string(...)`. Probe-before-persist pattern is correct.
- File-perm test: PASS on both canonical paths.

**Item 4 — Confirm dept-routing memo OPEN for 14-day `target_user_id` allowlist hardening → PASS (memo opened during B9)**
- Sub-memo created during B9 QA: `inbox/dept-routing/ST-2026-05-02-target-user-id-allowlist-hardening.md`
- Status: OPEN. Owner: ptt-fullstack (BUILD), security-engineer-tech (review), ptt-qa (verify).
- Acceptance criteria: schema migration (`is_house_account` col) + code allowlist check + 3 new tests + B11 OP# verifies synthetic non-house attribution returns 403.
- Cadence: re-evaluate next BOOP; escalate to Jared if 10 days elapse without progress.
- **Handshake Queue Row 72 verification**: handshake-queue.md lives in `/home/aiciv/shared/` (sister-container scope, not accessible from this filesystem). Per-dispatch instruction "verify Row 72 is still OPEN" must be confirmed by Aether (Primary, has Triangle OS access) or by operations-analyst during B11. The aether-side canonical record is the sub-memo above.

**Item 5 — Re-run all 27 tests (12 parser + 15 runTick) → PASS (27/27 GREEN)**
- Executed: `cd workers/blog-publish-hook && node tests/parser.test.mjs` AND `node tests/runTick.test.mjs`
- Parser: **12 passed, 0 failed** (exit 0). Cases: extracts 3 posts, slug, ISO datetime, URL, title prefix, decode `&amp;`, no remaining entities, empty/no-match returns `[]`, dedupes within page, ISO lex-comparable (A5 dependency), regex rejects underscored/uppercase slugs.
- runTick: **15 passed, 0 failed** (exit 0). Cases: A5 backfill (old=skipped, new=queued), no failures, FK populated, second tick is no-op (idempotency), failed insert path captures HTTP 400 + last_error, failed→retry→queued recovery, retry exhaustion under MAX_RETRIES=3.
- Total: **27/27 GREEN.** Identical to B7 BUILD claim.
- **NEW LOW finding (L1)**: `package.json` "test" script only runs `parser.test.mjs`. To execute runTick tests, the command must be invoked explicitly (`node tests/runTick.test.mjs`). Recommend updating to `"test": "node tests/parser.test.mjs && node tests/runTick.test.mjs"` so a single `npm test` covers all 27 cases. Not a B10 blocker; documenting for ptt-fullstack to fix during the next touch.

**Item 6 — Multi-tenant scoping in `handleListContent` filters `WHERE user_id = ?` → PASS**
- File: `workers/social-api/src/worker.js` lines 3915–3925 (`handleListContent`)
- Code: `let q = "SELECT * FROM content_items WHERE user_id = ?"; const args = [sess.user_id];`
- Status filter and platform filter both append with `AND`, never replacing the user_id constraint. Bind order preserves `sess.user_id` as the first parameter.
- Defense-in-depth confirmation: even if a client crafts arbitrary status/platform, the user_id filter is invariant. Multi-tenant isolation holds.

**Item 7 — Idempotency: `runTick` twice with identical input → second run no-op → PASS**
- Two enforcement layers in `workers/blog-publish-hook/src/worker.js`:
  1. **Logical guard**: `if (existing) { ... continue; }` — known slugs are skipped on tick 2 unless previously failed AND under retry budget. Successful (status='queued') and skipped (status='skipped') rows never re-enter the work loop.
  2. **DB constraint** (`insertPost`): `INSERT INTO published_blog_posts ... ON CONFLICT(slug) DO NOTHING` — the slug column has UNIQUE constraint per migration 0001. Even under a race, double-insert is structurally impossible.
- Empirical: runTick test "second tick takes no new action" + log line `cron tick — 0 detected, 0 queued, 0 failed, 0 skipped in 0ms` — observed during the test run above.

**Item 8 — Constitutional check: NO production deploy yet → PASS**
- `git log --oneline -30`: most recent commit is `4f729a3 seo: add FAQPage JSON-LD to 3 blog posts (AIO)` — unrelated to bsky-distribution-fix. Last 36 hours: only `4f729a3`.
- Bsky-distribution build artifacts (workers/blog-publish-hook/, workers/social-api/src/worker.js patch, tools/bsky-session-health/check_and_heal.py) are present in working tree but NOT committed.
- Grep for `wrangler\s+(pages\s+)?deploy` across `**/*.{md,sh,py,yml,yaml,toml,json}`: all matches are in **documentation** (DEPLOY.md, routing memos, B7/B8 memos) or **package.json scripts** (`"deploy": "wrangler deploy"` — alias only, not auto-fired). NO executable invocation of `wrangler deploy` exists.
- `wrangler pages deploy` (constitutionally banned): zero matches anywhere in the repo for this BUILD chain.
- DEPLOY.md exists and is the runbook for devops-engineer (B10), but has not been executed.
- Constitutional pass: production is untouched. Jared-gating preserved for B10.

### Synthesis

- **0 CRITICAL, 0 HIGH** new findings during B9.
- **1 new MEDIUM (M5)**: `/status` should expose `last_error`, not just counts. Roll into 14-day hardening sprint.
- **1 new LOW (L1)**: `npm test` should run both test suites. Single-line package.json fix.
- All 8 dispatched QA items have **evidence-backed PASS** verdicts. Item 4 required dept-systems-technology to open the sub-memo during B9 (now done). Item 4's Row 72 cross-check is deferred to OP#/Aether (out of aether-filesystem scope).

### Pre-ship rider for B10 SHIP (devops-engineer)

The B9 verdict is CONDITIONAL-PASS. The "conditional" is procedural, not technical:

- DEPLOY.md is the runbook of record. Execute Steps 1→7 in order.
- **DO NOT auto-fire `wrangler deploy`.** Conductor BOOP gates the actual production fire — devops-engineer prepares + dry-runs, then waits for Jared's explicit greenlight per constitutional payment-flow / production-deploy rules.
- Pre-flight #1 (PRAGMA check on `metadata` column) is mandatory before running migration 0002 — non-idempotent migration is correctly mitigated by the runbook check, but skipping the check would error.
- Step 4 manual smoke-test (`POST /run` with bearer) is the production validation — first run should show all-skipped (backfill rule), zero queued.
- Items M5 (status endpoint detail) and L1 (npm test wiring) are post-SHIP touch-ups; not blocking.

### Next chain step

**B10 SHIP — devops-engineer**: prepare deploy plan from DEPLOY.md. Confirm with conductor BOOP / Aether before executing wrangler. Verify each `wrangler deploy` against the worker target (this is `wrangler deploy` for Workers, NOT `wrangler pages deploy` — constitutionally distinct).

**B11 OP# — operations-analyst**: independent verifier. Will need to:
1. Confirm Handshake Queue Row 72 status (allowlist hardening) — out of B9 scope, requires Triangle OS access
2. Pair-verify the 4 post-ship checks listed in DEPLOY.md
3. Track the 14-day hardening sub-memo (`ST-2026-05-02-target-user-id-allowlist-hardening.md`) on the standard re-evaluation cadence

### Memory writes

- Dept memory: `.claude/memory/departments/systems-technology/2026-05-02--bsky-distribution-fix-B9-QA-verdict.md`
- New routing memo: `inbox/dept-routing/ST-2026-05-02-target-user-id-allowlist-hardening.md` (OPEN, 14-day SLA)

— dept-systems-technology, 2026-05-02
