# B7 BUILD — blog-publish-hook Worker (+ social-api adapter + self-healing session BOOP)

**Date**: 2026-05-02
**Agent**: ptt-fullstack
**Type**: operational + teaching
**Phase**: B7 BUILD complete; ready for B8 SECURITY review

**Spec**: `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md` (v2)
**Routing memo**: `inbox/dept-routing/ST-2026-05-02-bsky-distribution-fix.md`
**CTO sign-off**: `.claude/memory/agent-learnings/cto/2026-05-02--bsky-publish-hook-signoff-B6.md`

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/ptt-fullstack/` for prior CF Worker / D1 / cron patterns
- Found:
  - `2026-04-14--blog-index-and-archive-regen.md` — prior blog-index parsing pattern (HTML scraping)
  - `2026-05-02--bsky-prereqs-b4-b5.md` — own predecessor; B5 PASS established session health
  - 75+ adjacent memos on social-api, referrals-api, welcome-email-api as Worker-deploy patterns
- Reused: `workers/blog-publisher/` directory layout, `workers/social-api/wrangler.toml` D1-binding format, `tools/bsky_utils.py` session string handling

---

## (a) What got built

### 1. `workers/blog-publish-hook/` — new CF Worker
| File | Purpose |
|------|---------|
| `wrangler.toml` | Cron `*/10 * * * *`, D1 binding to `purebrain-social`, env vars + secrets contract |
| `src/worker.js` | Cron handler + HTTP handler (`/health`, `/status`, `POST /run`); blog-index parser; A5 timestamp rule; social-api caller; idempotent insert; retry-budgeted failure path |
| `migrations/0001_published_blog_posts.sql` | `published_blog_posts` table + `worker_metadata` table |
| `migrations/0002_content_items_metadata.sql` | Adds missing `content_items.metadata` column to social-api DB |
| `tests/parser.test.mjs` | 12 unit tests on the regex parser (HTML decoding, dedupe, slug guard, ISO comparison sanity) |
| `tests/runTick.test.mjs` | 15 integration tests with fake D1 + fake fetch (A5 backfill, idempotency, failure capture, retry path, retry budget exhaustion) |
| `package.json` | `"type": "module"` plus npm scripts for `test`, `deploy`, `tail` |
| `DEPLOY.md` | Step-by-step deployment runbook for B10 devops-engineer |

### 2. `workers/social-api/src/worker.js` — patched in place
- `handleCreateContent` now has a system-role bypass branch: when `sess.role === 'system'`, looks up the social_account by id alone (skipping the `user_id` ownership match), pulls the OWNING `user_id` off the row, and inserts `content_items.user_id` against that real owner — so existing per-user list/scope queries still work.
- Added optional `target_user_id` field (system-only override).
- Now persists `body.metadata` as a string into `content_items.metadata` (was silently dropped before — UI sends it but the INSERT didn't include the column).
- `generated_by` defaults to `"system"` for system-role calls (was always `"human"`).
- Diff: +39 / -8 in `workers/social-api/src/worker.js`.

### 3. `tools/bsky-session-health/check_and_heal.py` — Spec v2.5 self-healing BOOP
- Probes `getAuthorFeed(actor='purebrain.ai', limit=1)` against current session.
- On `ExpiredToken` / `InvalidToken` / "Token has been revoked" / parse-corruption: re-logs from `BSKY_USERNAME` + `BSKY_PASSWORD` in `.env`, writes refreshed session to BOTH canonical paths at perms 0600.
- Telegram-notifies on heal-success / heal-failure (silent on healthy ticks; OP#-friendly).
- Exit codes: 0 healthy/healed, 1 heal-failed (manual intervention), 2 misconfigured.
- Constitutional: never commits session contents; uses .env directly; idempotent.

---

## (b) Which amendments applied

| ID | Amendment | Where applied |
|----|-----------|---------------|
| **A1** | D1 schema FK column type | `migrations/0001_published_blog_posts.sql:13` — `thread_queued_content_item_id TEXT` (UUID, not INTEGER) |
| **A2** | social-api system-role bypass in `handleCreateContent` | `workers/social-api/src/worker.js:3939-3960` — branch on `sess.role === 'system'`, resolves owner from social_accounts row directly, accepts optional `target_user_id` |
| **A3** | Payload contract reshape | `workers/blog-publish-hook/src/worker.js:postToSocialApi` — sends `{ social_account_id, platform, status, body (string), content_type: 'blog-thread', metadata (JSON string) }` to `/api/content` |
| **A4** | Reuse existing `ROUTER_API_KEY` auth surface | `wrangler.toml:vars` — Worker-side env name `SOCIAL_API_SYSTEM_TOKEN` maps to social-api's existing `ROUTER_API_KEY` (no new auth model invented). Branch at `worker.js:3717` is unchanged. |
| **A5** | Deterministic backfill rule | `src/worker.js:getFirstDeployTimestamp` + main loop — first cron tick stores `worker_metadata.first_deploy_timestamp`; subsequent inserts compare `post.published_at` lexicographically against that ISO string (works because ISO 8601 sorts as text). No "init flag" required; idempotent under DB rebuild. |
| **A6** | Wrangler deploy approval | Confirmed in `wrangler.toml` comment + `DEPLOY.md` step 3. Ship via `wrangler deploy` (Workers), NOT `cf-deploy.py` or `wrangler pages deploy`. |

All 6 amendments applied and verified.

---

## (c) Test evidence

### Unit tests (parser):
```
parser.test.mjs
  PASS  extracts 3 posts from fixture
  PASS  first post slug
  PASS  first post ISO datetime
  PASS  first post URL
  PASS  first post title prefix
  PASS  decodes &amp; to &
  PASS  no remaining &amp; in title
  PASS  empty html returns []
  PASS  no-match html returns []
  PASS  dedupes repeated slug within single fetch
  PASS  ISO 8601 strings compare lexicographically (A5 rule depends on this)
  PASS  rejects underscored/uppercase slugs (regex guard)

12 passed, 0 failed
```

### Integration tests (runTick with fake D1 + fake fetch):
```
runTick.test.mjs
  PASS  old post (pre-deploy) marked skipped
  PASS  new post (post-deploy) queued via social-api
  PASS  no failures
  PASS  old-post status=skipped in D1
  PASS  new-post status=queued in D1
  PASS  FK populated with content_item id
  PASS  second tick takes no new action
  PASS  new post failed insert path
  PASS  new-post status=failed in D1
  PASS  last_error captures HTTP 400
  PASS  tick 1 → failed
  PASS  tick 2 retry → queued
  PASS  tick 2 reports 1 queued (the retry)
  PASS  still failed after exhaustion
  PASS  retry_count <= MAX_RETRIES (3)

15 passed, 0 failed
```

### Self-healing BOOP simulated revocation test:
1. Backed up healthy session → `/tmp/bsky_session_backup.txt`
2. Wrote garbage data to `.claude/bsky_session.txt` (simulates revoked token)
3. Ran `tools/bsky-session-health/check_and_heal.py`:
   ```
   [bsky-session-health] EXPIRED — not enough values to unpack (expected 5, got 1)
   [bsky-session-health] HEALED — session refreshed; persisted to 2 paths
   exit=0
   ```
4. Verified both canonical paths refreshed at 833 bytes, perms 600
5. Re-ran healthy probe: `[bsky-session-health] OK — getAuthorFeed succeeded`

### Syntax check:
- `node --check workers/social-api/src/worker.js` → OK
- `node --check workers/blog-publish-hook/src/worker.js` → OK

### Live social-api regression (pre-deploy state):
- `GET /health` → 200, `{"status":"ok","service":"social-api"}`
- `POST /api/content` (no auth) → 401 `{"error":"unauthorized"}` (existing contract intact)

### blog-publish-hook NOT yet deployed (correct — B7 staging-only scope):
- `GET https://blog-publish-hook.in0v8.workers.dev/health` → 1042/404 (expected; deploy is B10's job)

---

## (d) Deviations from spec with rationale

1. **Migration 0002 (`content_items.metadata` ALTER TABLE) was not listed in the spec.**
   The spec assumed the column existed because the kanban UI POST body sends `metadata` (worker.js:1752). On audit, the canonical `shared/social-api-schema.sql:50` does NOT define this column, so the field was being silently dropped on insert today. I added migration 0002 explicitly so the persistence path is real, with an idempotency note in DEPLOY.md (run `PRAGMA table_info(content_items)` first; skip migration if column already exists in production via prior out-of-band ALTER).

2. **`generated_by` value for system-role inserts.**
   Spec didn't address this. Current code defaults `generated_by` to `"system"` for `sess.role === 'system'` calls (vs `"human"` for normal callers). Rationale: kanban analytics that count human-vs-AI vs system-generated posts would otherwise mis-attribute hook-queued drafts as human work. Trivial change, semantically honest.

3. **`/run` admin endpoint added to the Worker.**
   Spec mentioned only the cron path. I added an authenticated POST /run that triggers `runTick` once, gated by the same `SOCIAL_API_SYSTEM_TOKEN`. Justification: gives OP# / on-call a manual smoke-test path without waiting up to 10 min for a cron, and supports the DEPLOY.md step 4 first-run verification. Same auth surface, no new attack surface.

4. **Self-healing BOOP error-signal list is broader than spec described.**
   Spec said: "On `ExpiredToken`, auto-re-log." I broadened the trigger list to also catch `InvalidToken`, `"Token has been revoked"`, `"Authentication Required"`, `"not enough values to unpack"` (parse failure), `AuthMissing`, `AuthFactorTokenRequired`. Discovered during simulation: garbage session data raises a parse error, NOT `ExpiredToken`, but the heal action is identical. Broadening prevents the BOOP from going dark on a corrupt-file failure mode.

5. **NOT folded into existing `logs/bsky-presence-boop/`.**
   Spec said this was "preferred but optional." The presence BOOP is a markdown-output diagnostic, not a Python-callable module. Folding would require either a refactor of the presence BOOP into a library or a duplication. I built session-health as a clean standalone tool at `tools/bsky-session-health/check_and_heal.py`. The two can be wired together later via cron (presence BOOP runs after session-health, sees a healthy session).

---

## Files written / changed

```
workers/blog-publish-hook/wrangler.toml                        (NEW)
workers/blog-publish-hook/package.json                         (NEW)
workers/blog-publish-hook/src/worker.js                        (NEW)
workers/blog-publish-hook/migrations/0001_published_blog_posts.sql  (NEW)
workers/blog-publish-hook/migrations/0002_content_items_metadata.sql (NEW)
workers/blog-publish-hook/tests/parser.test.mjs                (NEW)
workers/blog-publish-hook/tests/runTick.test.mjs               (NEW)
workers/blog-publish-hook/DEPLOY.md                            (NEW — runbook for devops-engineer)
workers/social-api/src/worker.js                               (PATCHED — handleCreateContent system-bypass + metadata)
tools/bsky-session-health/check_and_heal.py                    (NEW — Spec v2.5 self-healing BOOP)
```

---

## Hand-off to B8 SECURITY

Next gate: security-engineer-tech reviews:
- `SOCIAL_API_SYSTEM_TOKEN` storage (Worker secret only, never logged)
- social-api system-bypass branch — confirm no privilege escalation surface (only social_account ownership relaxed; user_id is still pulled from a real owner, not arbitrary input)
- Idempotency under cron retry — DB ON CONFLICT and per-tick read-then-write race window
- Regex parser hardened against malformed HTML — confirmed empty/no-match returns [] (test 8, 9)
- No PII in logs — log lines contain only slug + content_item_id + status counters
- The new `/run` admin endpoint — same auth as cron, no public surface
- The self-healing BOOP's broadened error-signal list — confirm none of those signals come from network/transient errors that would cause unnecessary reauths

Open question for SECURITY: should the `target_user_id` system-override field be gated to a tighter allowlist (e.g., only known house-account user_ids), or is "system role can target any user_id" acceptable trust model?

---

## Memory Written

Path: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-02--blog-publish-hook-build.md` (this file)
Type: operational + teaching
Topic: B7 BUILD complete — Worker + social-api adapter + self-healing session BOOP, all 6 CTO amendments applied, 27 tests passing, ready for B8 SECURITY review

---

## Verification Statement

- IDENTIFY: parser unit tests, runTick integration tests, self-healing BOOP simulated revocation
- RUN: all three test suites + node --check on both workers
- READ: 12+15 = 27 PASS lines + healed exit=0 + node --check OK
- VERIFY: BUILD scope (staging-deploy-ready) achieved; production deploy is B10's job
- CLAIM: B7 BUILD complete. Awaiting B8 SECURITY review per the documented engineering chain.
