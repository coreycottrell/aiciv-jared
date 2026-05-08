# Bluesky Publish-Hook Spec — Structural Fix for Distribution Leg

**Date**: 2026-05-02
**Owner**: dept-systems-technology (CTO office)
**Source routing**: `inbox/dept-routing/ST-2026-05-02-bsky-distribution-fix.md`
**Parent diagnosis**: `.claude/memory/departments/dept-marketing-advertising/2026-05-02--bsky-dormancy-investigation.md`
**Status**: SPEC — pending BUILD by ptt-fullstack
**Pair verifier**: operations-analyst (OP#)

---

## Mission

Make it **structurally impossible** for a blog post to publish on `purebrain.ai/blog/<slug>/` without a Bluesky thread row being queued in the `social.purebrain.ai` kanban (constitutional source of truth).

This is the structural complement to MA#'s SOP discipline restoration. Even if a future agent skips `/post-blog`, the publish-hook fires regardless.

---

## Pre-Build Checklist (CONSTITUTIONAL)

| Q | Answer | Implication |
|---|--------|-------------|
| Q1: Software, AI automation, or both? | **SOFTWARE** | The hook itself is deterministic. AI generates the thread *content* downstream, but the queueing must run with no AI active. |
| Q2: Must run without AI active? | **YES** | Blog posts publish 24/7 from CF Pages deploys; we cannot rely on a sub-agent being awake. |
| Q3: Internal or customer-facing? | **CUSTOMER-FACING** (Bsky distribution affects @purebrain.ai brand reach) | Software, deployed properly, monitored. |
| Q4: One-time or recurring? | **RECURRING** (every blog post forever) | Persisted system, not a script. |
| Q5: Real-time or periodic? | **NEAR-REAL-TIME** (within 5 min of deploy) | Cron-polling worker is acceptable; webhook would be ideal but CF Pages doesn't emit deploy webhooks reliably for content changes. |
| Q6: Persistence/tracking? | **YES** — must dedupe published posts, persist last-seen state | D1 database (`purebrain-social` already exists, OR new `purebrain-blog-state` table) |
| Q7: Human configurable? | **YES** (eventually) — manual override, retry, skip | Admin endpoint OR direct kanban card edit |

**Decision**: Software (CF Worker on cron schedule) writing to existing D1-backed social-api Worker.

---

## Architecture

```
[purebrain.ai/blog/index.html]  (CF Pages — purebrain-production project)
        |
        |  rendered/static — has all post slugs + dates
        v
[Cron Worker: blog-publish-hook]                     <-- NEW (this build)
        |
        |  every 10 min:
        |  1. Fetch /blog/index.html
        |  2. Parse post list (slug, title, date, summary)
        |  3. Compare against D1 `published_blog_posts` table
        |  4. For each NEW post:
        |     a. Generate thread draft (template OR AI-assist via prompt to be filed in social-api)
        |     b. POST to social-api: /api/content (status=draft, platform=bluesky, type=blog-thread)
        |     c. Mark post as queued in D1
        v
[social-api Worker]                                  <-- EXISTS
        |
        |  D1 binding: purebrain-social
        |  Endpoint: POST /api/content
        |  Status flow: draft → final → scheduled → live
        v
[social.purebrain.ai kanban UI]
        |
        |  Human reviews → Final → ContentRouter polls /api/content/ready
        v
[ContentRouter (existing) → Bluesky post via stored creds]
```

**Why polling vs webhook**: CF Pages doesn't emit reliable post-deploy events for static content changes. A 10-minute cron worker hitting the public blog index is simple, idempotent, and survives any deploy method (cf-deploy.py, manual upload, future automation). No coupling to deploy mechanics.

---

## Components to Build

### 1. New CF Worker: `blog-publish-hook`

**Location**: `workers/blog-publish-hook/`

**Files**:
- `wrangler.toml` — bindings: D1 `purebrain-social`, secret `SOCIAL_API_SYSTEM_TOKEN`, cron `*/10 * * * *`
- `src/worker.js` — fetch/parse/dedupe/queue logic
- `migrations/0001_published_blog_posts.sql` — D1 schema

**D1 schema** (additive — extend `purebrain-social` DB):
```sql
CREATE TABLE IF NOT EXISTS published_blog_posts (
  slug TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  published_at TEXT NOT NULL,        -- ISO 8601 from blog index
  detected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  thread_queued_content_id INTEGER,  -- FK to content table id (nullable)
  thread_queued_at TEXT,
  status TEXT NOT NULL DEFAULT 'detected'  -- detected | queued | failed | skipped
);
CREATE INDEX IF NOT EXISTS idx_pbp_status ON published_blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_pbp_detected_at ON published_blog_posts(detected_at);
```

**Cron handler logic**:
1. `GET https://purebrain.ai/blog/` (or use `daily-recap.json` if it has the canonical post list)
2. Parse post slugs + dates from HTML (regex on `<a href="/blog/{slug}/">`)
3. `SELECT slug FROM published_blog_posts` — diff
4. For each slug NOT in D1:
   - Fetch the post page, extract `<title>`, `<meta name="description">`, first H2 paragraph for hook seed
   - Build thread-draft payload (see "Thread Draft Template" below)
   - `POST https://social-api.purebrain.ai/api/content` with `Authorization: Bearer ${SOCIAL_API_SYSTEM_TOKEN}`
   - On 200: insert row with `status='queued'`, store `content_id`
   - On error: insert row with `status='failed'`, log error, retry next cron tick (max 3 attempts)
5. Emit operational metric (count of new posts detected, queued, failed) — log line that operations-analyst can grep

### 2. Thread Draft Template (placed in worker, not AI-generated at hook time)

To keep the hook **AI-independent** (Q2 answer), the worker queues a *draft skeleton*. A human or downstream AI agent fills in the rich content before flipping to `Final`.

```
Post 1 (Hook):
🧵 [Blog Title]

[First sentence of meta description, or first 100 chars of first paragraph]

Post 2-5 (Tease — placeholders):
[DRAFT — fill from blog body]
[DRAFT]
[DRAFT]
[DRAFT]

Post 6 (Link):
Full read: {blog_url}

🤖
```

**Stored in social-api as** `status=draft`, `platform=bluesky`, `type=blog-thread`, with metadata `{ source: 'blog-publish-hook', slug, blog_url }`.

This keeps the hook deterministic. AI-assisted draft enrichment (the part that *could* fail or hallucinate) is a separate, human-gated step in the kanban UI.

### 3. social-api Endpoint Contract (verify existing or add)

Worker needs to confirm `POST /api/content` accepts:
```json
{
  "platform": "bluesky",
  "type": "blog-thread",
  "status": "draft",
  "title": "Blog post title",
  "body_json": { "posts": ["post1", "post2", ...] },
  "metadata": { "source": "blog-publish-hook", "slug": "...", "blog_url": "..." }
}
```

If schema doesn't accept this shape, ptt-fullstack adds a thin adapter. **Do not break existing /api/content callers.**

### 4. System Auth Token

- Generate `SOCIAL_API_SYSTEM_TOKEN` (secure random, store in Worker secret + social-api allowlist)
- social-api validates: token present + recognized → grants `system` role (already exists per worker.js header comment: "leader/system role only" on `/api/content/ready`)
- **NEVER** put this token in any container. Wrangler secret only.

### 5. Observability

- Worker logs: `[blog-hook] cron tick — N detected, M queued, K failed`
- Optional: write summary to `social-api` `events` table (if exists) for kanban audit trail
- Failure alert: if 3 consecutive cron ticks return `failed > 0`, send Telegram alert via existing `tg_send.sh` pipeline (NOT from the worker itself — from a separate periodic check or via D1 query in operations-analyst's pair-verify BOOP)

---

## Constitutional Compliance Checks

| Rule | Compliance |
|------|------------|
| NEVER deploy to customer containers | ✅ All in CF Workers + D1 |
| NEVER wrangler deploy (use cf-deploy.py) | ⚠️ cf-deploy.py is for CF Pages. CF Workers deploy via `wrangler deploy` is allowed (`wrangler pages deploy` is the banned one). Confirm with cto agent before ship. |
| NO direct bsky-manager posting | ✅ Hook writes to social-api kanban only. Posting happens downstream via existing ContentRouter. |
| NO container-local data | ✅ D1 only. |
| Source of truth: social.purebrain.ai PureSurf API | ✅ Hook writes there first, never elsewhere. |
| Multi-tenant ready | ✅ social-api already multi-tenant. Hook writes under a designated system user (configurable). |
| Pre-build checklist applied | ✅ See table above. |
| BUILD → SECURITY → QA → SHIP | Required (this spec is BUILD phase scope). |

---

## Engineering Flow

| Phase | Owner | Deliverable |
|-------|-------|-------------|
| **BUILD** | ptt-fullstack | Worker code, D1 migration, wrangler.toml, local test harness, integration test stub |
| **SECURITY** | security-engineer-tech | Review: token storage, social-api auth surface unchanged, no new public endpoints, no PII in logs, idempotency under cron retry, regex parser hardened against malformed HTML |
| **QA** | qa-engineer | Test plan: unit (parser, dedupe), integration (cron tick on staging), end-to-end (deploy real test post → see kanban row appear), regression (existing /api/content callers still work) |
| **SHIP** | devops-engineer | `wrangler deploy` to production, set secret, verify cron schedule, smoke-test first cron tick, monitor 24h |
| **VERIFY** | OP# (independent) | Re-probe per parent memo's checklist + first new @purebrain.ai post within 48h |

---

## Tracks B4 + B5 (Pre-requisites — handle in parallel)

These are independent of B6 (this hook) but routed to the same engineering team:

### B4 — Verify `bluesky-blog-thread` skill end-to-end
- ptt-fullstack runs the skill against a known recent post (e.g., `your-customers-will-tell-you-everything` from 2026-04-14)
- Confirm thread posts via the skill's existing path
- If pass: drop the `🚨 UNTESTED` flag on the skill manifest
- If fail: log specific failure, route fix back through this dept

### B5 — Refresh Bsky session
- ptt-fullstack: regenerate `.bsky_session.txt` for `purebrain.ai` handle (was missing in repo as of 2026-05-02 check)
- Use credentials from `.env` (BSKY_USERNAME, BSKY_PASSWORD)
- Verify auth via test API call (`getAuthorFeed` against own handle)
- Commit session file location (.gitignored if not already) — DO NOT commit the session token contents

These two can run in parallel with B6 BUILD phase, must complete before SHIP phase of B6 (since B6 ultimately depends on the downstream Bsky posting working).

---

## Implementation Tracker

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| B4: Verify bluesky-blog-thread skill | NOT STARTED | ptt-fullstack | 24-48h |
| B5: Refresh Bsky session | NOT STARTED | ptt-fullstack | 4h |
| B6.1: D1 migration | NOT STARTED | ptt-fullstack | |
| B6.2: Worker source code | NOT STARTED | ptt-fullstack | |
| B6.3: Local test harness | NOT STARTED | ptt-fullstack | |
| B6.4: Security review | NOT STARTED | security-engineer-tech | After BUILD |
| B6.5: QA test plan + execution | NOT STARTED | qa-engineer | After SECURITY |
| B6.6: Production deploy | NOT STARTED | devops-engineer | After QA |
| B6.7: Smoke test + 24h monitor | NOT STARTED | devops-engineer | Post-ship |
| B6.8: Pair verify | NOT STARTED | OP# | After SHIP, independent |
| Routing memo archive | NOT STARTED | this dept | After ship |

---

## Acceptance Criteria

- [ ] CF Worker `blog-publish-hook` deployed, cron firing every 10 min
- [ ] D1 table `published_blog_posts` populated with all known posts (initial backfill — see note below)
- [ ] First new blog post lands → kanban row appears within 15 minutes (cron + slack)
- [ ] No false positives (existing posts pre-dating hook do not get queued)
- [ ] No double-queueing under cron retry / partial failure
- [ ] social-api existing endpoints unchanged (regression)
- [ ] OP# pair-verify passes parent memo's 4-point checklist
- [ ] First new @purebrain.ai Bsky post visible within 48h (this depends on MA# Track A backfill flowing through approved kanban rows + the publish-hook surfacing fresh ones)

**Initial backfill note**: First cron tick should treat all currently-listed posts as `status='detected'` but NOT `status='queued'` (i.e., seed the dedupe table without flooding the kanban with 9 backfill drafts — MA# is handling backfill manually per their Track A2). Easiest implementation: an init flag on the worker that on first run inserts current posts as `status='skipped'` then flips to normal mode.

---

## Risks + Mitigations

| Risk | Mitigation |
|------|------------|
| Blog index HTML format changes, regex breaks | Keep parser tolerant; add structured JSON endpoint at `purebrain.ai/blog/index.json` as v2 (separate ticket) |
| social-api token leak | Worker secret only; rotate quarterly; never log |
| Cron worker fails silently | Log line per tick; OP# pair-verify checks for log presence in kanban event stream |
| Race with manual `/post-blog` runs | Worker dedupes by slug; manual run wins (also writes via social-api) |
| Cost (10-min cron = 144 invocations/day) | Trivial. CF Workers free tier covers 100k/day. |

---

## Memory Written

Path: `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md` (this file)
Type: teaching + operational
Topic: Spec for structural distribution-leg fix — publish-hook architecture, pre-build checklist application, BUILD→SECURITY→QA→SHIP plan

---

## CTO Sign-Off — 2026-05-02

**Decision**: **APPROVED-WITH-AMENDMENTS**

**Verdict on the 5 questions:**

### 1. Cron-poll vs CF Pages deploy webhook → **CRON IS CORRECT. Hold the line.**

CF Pages does emit `pages.deployment.success` via Workflow webhooks, but:
- Those webhooks are deploy-scoped, not content-scoped. A deploy that touches `_redirects` fires the same event as one that ships a new blog post. We'd still need to diff `/blog/index.html` against D1, which is exactly the cron-poll logic.
- Webhook reliability has historically been weak for static content changes. We saw this on the 2026-04-15 incident (deploy bound to wrong project — webhook would not have caught the *semantic* miss).
- Cost of polling is trivial (144 invocations/day vs the 100k/day free tier; <0.15%).
- Cron survives ANY deploy method (cf-deploy.py, future automation, manual upload, GitHub Actions). Webhook couples us to one deploy mechanism.
- Latency delta: webhook ~30s vs cron ~5min average. For a kanban-queued draft that a human reviews before posting, 5min is invisible.

**Cron wins on simplicity, idempotency, and decoupling. Approved as specced.**

Future amendment (do NOT include in v1): if we ever need <60s latency (e.g., fully-automated breaking-news posting), revisit with a webhook + cron hybrid where webhook is fast-path and cron is reconciliation.

### 2. D1 schema additivity → **APPROVED. Same DB is correct.**

Use the existing `purebrain-social` DB. Reasoning:
- The new `published_blog_posts` table has a foreign-key relationship to `content_items.id` (via `thread_queued_content_id`). Splitting databases would break referential integrity OR force a brittle cross-DB ID lookup.
- One D1 binding per worker is cleaner. Splitting now would force every future blog/social-coupling feature to maintain two bindings.
- Operational simplicity: one DB to back up, one to migrate, one to monitor.
- The "blog state" concept is **intrinsically a social-distribution concern** — it's only meaningful to track because it gates social posts. It belongs with the social DB.

**Amendment**: rename FK column `thread_queued_content_id` → `thread_queued_content_item_id` to match the existing table name (`content_items`). And declare it as `TEXT` not `INTEGER` — `content_items.id` is a UUID/string per `newId()` in worker.js line 3949, not an int.

### 3. System-token auth model → **REUSE EXISTING SURFACE. Do not add a new one.**

social-api **already has** a system-role auth surface at worker.js:3717 — `ROUTER_API_KEY` env secret yields a synthetic session with `role: "system"` and `user_id: "system"`. Build on this, do not duplicate.

**Two options, in order of preference:**

**Option A (preferred)**: Reuse `ROUTER_API_KEY`. The blog-hook is functionally another internal system caller — same trust tier as ContentRouter. Single secret to rotate.

**Option B (acceptable)**: Add a parallel `BLOG_HOOK_API_KEY` secret in social-api with the same synthetic-session pattern. Rationale = principle of least privilege / separable rotation. Cost = a second `if (env.BLOG_HOOK_API_KEY && token === env.BLOG_HOOK_API_KEY)` branch in `getSession()`.

Either way, the `SOCIAL_API_SYSTEM_TOKEN` name in the spec is fine on the worker side; it just maps to one of the above secrets in social-api.

**Amendment (CRITICAL — bug in current spec)**: `handleCreateContent` (worker.js:3937) requires `social_account_id` and validates `WHERE id = ? AND user_id = ?` against `sess.user_id`. The synthetic system session has `user_id: "system"`, which will NOT match any real `social_accounts` row. Two fixes needed:

1. **social-api side**: Add a system-bypass branch in `handleCreateContent` — when `sess.role === 'system'`, accept a `social_account_id` belonging to a configured "house" user (e.g., the @purebrain.ai bsky account owner) without the `sess.user_id` match. Or accept a `target_user_id` field that only `system` role can set.
2. **Spec payload**: The current spec payload uses `body_json: { posts: [...] }` and a top-level `body` is missing. The existing endpoint requires `body` (string) and stores `content_type`. Adapter the payload to `{ social_account_id, platform: 'bluesky', body: '<joined thread text>', content_type: 'blog-thread', status: 'draft', metadata: '<JSON string>' }`. Note `metadata` is stored as a JSON STRING in the kanban UI today (worker.js:1752 — `JSON.stringify(...)`).

This adapter work is BUILD-phase scope. ptt-fullstack should NOT modify the existing endpoint contract; it should add a thin compatibility shim and the system-bypass path.

### 4. Wrangler-banned check → **CONFIRMED: ban does NOT extend to Workers.**

Constitutional rule (`feedback_wrangler_banned_cf_deploy_only.md`) bans `wrangler pages deploy` specifically because it deletes pages not in the local folder (lost 30hr of investor-page work). 

`wrangler deploy` (Workers) is **allowed and standard**. It's already the production deploy path for `admin-api`, `welcome-email-api`, `agentmail-webhook`, `blog-publisher`, `trio-comms`, and others. Workers deploys do not touch CF Pages projects and do not have the destructive-delete behavior.

ST# is correct. Ship the worker via `wrangler deploy` from `workers/blog-publish-hook/`. **Do not** invoke `cf-deploy.py` for this — that tool is CF Pages only.

Update the compliance table row to: ✅ `wrangler deploy` (Workers) is approved; the ban is scoped to `wrangler pages deploy`.

### 5. Backfill init flag → **APPROVED. Smart call.**

Marking historical posts as `status='skipped'` on first tick is the right move:
- MA# is handling backfill manually (Track A2), so we'd be double-posting if we queued them.
- `skipped` is semantically honest (we saw them, we chose not to queue), unlike `queued` (lie) or `detected` (ambiguous — would the next tick try to queue them?).
- Implementation suggestion: don't use a one-time "init flag" mechanic — instead, a deterministic rule: **on insert, if the post's `published_at` is older than the worker's first-deploy timestamp (stored as a single-row `worker_metadata` row), insert as `skipped`; if newer, insert as `detected` and proceed to queue.** This is idempotent — if the worker is redeployed or the table is dropped and rebuilt, the same rule produces the same result. No "first run" branch to forget.

**Amendment**: replace "init flag on first run" with the timestamp-comparison rule above. Simpler and more durable.

---

### Required Amendments Before BUILD

ptt-fullstack must reflect these in the BUILD deliverable:

1. **D1 schema fix**: rename `thread_queued_content_id` → `thread_queued_content_item_id`, change type from `INTEGER` to `TEXT` (UUID).
2. **social-api adapter**: add system-role bypass in `handleCreateContent` (accepts a configured house-account `social_account_id`, OR introduces an explicit `target_user_id` field gated to `role==='system'`). Path: `workers/social-api/src/worker.js` around line 3937.
3. **Payload adapter**: spec's `body_json: { posts: [...] }` → real payload `{ social_account_id, platform: 'bluesky', body: <joined string>, content_type: 'blog-thread', status: 'draft', metadata: JSON.stringify({source, slug, blog_url}) }`.
4. **Auth secret reuse**: use existing `ROUTER_API_KEY` (preferred) OR add parallel `BLOG_HOOK_API_KEY` in social-api `getSession()` — do NOT invent a new auth model.
5. **Backfill mechanic**: timestamp-comparison rule (worker-deployed-at vs post-published-at), NOT a one-time init flag.
6. **Compliance table fix**: change row "NEVER wrangler deploy" verdict from ⚠️ to ✅ — Workers deploy is approved; ban is `wrangler pages deploy` only.

### Non-Blocking Suggestions (BUILD or post-ship)

- Add a `purebrain.ai/blog/index.json` structured endpoint as a v2 fallback for the regex parser (filed as separate PD# ticket, not blocking).
- The 3-consecutive-failed-tick Telegram alert: implement via `operations-analyst` BOOP querying D1, NOT inside the worker. Worker stays deterministic + log-only. Spec already says this — re-emphasizing.
- Long-term: when MA# fully owns this, consider a kanban-side "regenerate draft" button that calls back into the worker via signed admin endpoint, replacing manual backfill with on-demand re-queue.

### Architectural Verdict

The structural insight is correct: **make distribution non-bypassable by mechanizing the gating**. This is exactly the right pattern for a chronic-flag domain (Bsky has been intermittent for months — relying on agent discipline alone has demonstrably failed). The spec moves the failure mode from "agent forgot" to "worker logged a failure that OP# will catch" — a much better failure mode.

The design respects the Pure Technology principle of OWN the skill, not rent it: this is our own Worker on our own D1, talking to our own social-api. No SaaS dependency for the gating mechanism.

**Gate B6 cleared with amendments. ptt-fullstack: proceed to BUILD with the 6 amendments above. Loop back via SECURITY review (security-engineer-tech) before QA.**

— cto, 2026-05-02

---

## Spec v2 — 2026-05-02 23:25 UTC

**Status change**: SPEC v1 (pending sign-off) → **SPEC v2 — READY FOR B7 BUILD**

**Triggers for v2**:
- CTO sign-off (B6) returned APPROVED-WITH-AMENDMENTS — 6 required changes
- ptt-fullstack B5 returned PASS — session refreshed, posting credentials confirmed healthy
- ptt-fullstack B4 returned FAIL — `bluesky-blog-thread` skill is a phantom (SKILL.md exists, `blog_to_thread.py` does not). Re-scoped from prereq to sibling work.

**Net effect**: B6 prerequisites cleared. B7 BUILD chain (the publish-hook Worker) is unblocked and amendment-locked. B4 moves to a parallel sibling track that does NOT gate B7.

---

### v2.1 — B5 PASS (session refreshed)

**Status**: ✅ COMPLETE — ptt-fullstack regenerated session token via `Client.export_session_string()`, persisted to both canonical paths with perms 600, verified with `getAuthorFeed` against `purebrain.ai`. Identity confirmed: DID `did:plc:zy537fjp73tuq52ercz4ydo2`.

**Spec correction**: The original B5 brief said the session file was *missing*. Actual state was that BOTH session files existed but the token had been **revoked** (likely after long idle period or upstream Bluesky security event). This is a more precise root cause — relevant for v2 hardening.

**Files**:
- `/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt` (833B, 600)
- `/home/jared/projects/AI-CIV/aether/.claude/bsky_session.txt` (833B, 600)

**Implication for downstream**: MA# Track A2 backfill (9 missed threads) can now proceed. Posting infra is healthy.

**Hardening follow-up (folded into B7 sub-task — see v2.5)**: daily auto-relog BOOP that calls `getAuthorFeed`; on `ExpiredToken`, re-login from `.env` credentials and rewrite session file. Makes this self-healing instead of waiting for the next 20-day silent dormancy.

---

### v2.2 — B4 RE-SCOPED (skill is unimplemented, NOT untested)

**Status**: ❌ FAIL as a verification ticket. **MOVED out of prereqs.** Re-scoped to sibling work track (see "Sibling Work — Skill Rewrite" section below).

**Root cause**: `.claude/skills/bluesky-blog-thread/SKILL.md` describes ~250 lines of code for `blog_to_thread.py` — but the file does not exist anywhere in the repo. The `🚨 UNTESTED` flag was misleading: it's not "code exists but untested," it's "no code." Phantom skill.

**Constitutional contradiction surfaced**: SKILL.md describes direct atproto posting (`client.send_post()`). Our constitutional rule is that all social posting routes through social.purebrain.ai kanban as source-of-truth. The skill as written cannot be implemented faithfully without violating the kanban-SoT rule.

**Critical**: B4 was originally listed as a B7 BUILD gate. **It is not.** The B7 publish-hook Worker writes its own template directly to social-api `/api/content` — it never invokes `blog_to_thread.py`. Therefore B7 BUILD proceeds in parallel with the skill rewrite.

---

### v2.3 — Locked BUILD Amendments for B7 (ptt-fullstack)

These six amendments from the CTO sign-off are now LOCKED into the B7 BUILD instructions. ptt-fullstack must apply all six before SECURITY review.

| # | Amendment | Original spec said | v2 locked instruction |
|---|-----------|---------------------|------------------------|
| **A1** | D1 schema FK column | `thread_queued_content_id INTEGER` | **`thread_queued_content_item_id TEXT`** — matches existing `content_items.id` (UUID/string from `newId()` in `workers/social-api/src/worker.js:3949`) |
| **A2** | social-api endpoint adapter | Synthetic system session at `worker.js:3717` would be passed straight to `handleCreateContent` | **Add a system-role bypass branch in `handleCreateContent` (worker.js:3937)** that, when `sess.role === 'system'`, accepts a configured house-account `social_account_id` (or an explicit `target_user_id` field gated to system role) without the `WHERE id = ? AND user_id = ?` match. Without this, every hook call 404s. |
| **A3** | Payload contract | `body_json: { posts: [...] }` | **`{ social_account_id, platform: 'bluesky', body: '<joined thread text>', content_type: 'blog-thread', status: 'draft', metadata: JSON.stringify({source, slug, blog_url}) }`** — `body` is a string, `metadata` is a JSON-stringified string (per worker.js:1752 storage pattern) |
| **A4** | Auth surface | New `SOCIAL_API_SYSTEM_TOKEN` invented | **Reuse existing `ROUTER_API_KEY`** (preferred — same trust tier as ContentRouter) OR add parallel `BLOG_HOOK_API_KEY` constant in same `getSession()` branch at `worker.js:3717`. Do NOT invent a new auth model. The Worker-side env name (e.g., `SOCIAL_API_SYSTEM_TOKEN`) maps to one of these on the social-api side. |
| **A5** | Backfill mechanic | "Init flag on first run" marks historical posts as `skipped` | **Deterministic timestamp-comparison rule**: store `worker_first_deploy_timestamp` as a single-row `worker_metadata` table; on insert, if `published_at < worker_first_deploy_timestamp` → `status='skipped'`, else → `status='detected'` and proceed to queue. Pure-function rule, idempotent under DB rebuild or worker redeploy. |
| **A6** | Compliance table | "NEVER wrangler deploy" was marked ⚠️ | **`wrangler deploy` for Workers is ✅ APPROVED.** The constitutional ban (`feedback_wrangler_banned_cf_deploy_only.md`) is scoped to `wrangler pages deploy` only — that command deletes Pages not in the local folder. `wrangler deploy` for Workers is the production standard for `admin-api`, `welcome-email-api`, `agentmail-webhook`, `blog-publisher`, `trio-comms`. Ship via `wrangler deploy` from `workers/blog-publish-hook/`. Do NOT use `cf-deploy.py` for this Worker. |

**D1 binding**: stays in `purebrain-social` (NOT a separate DB) — preserves FK integrity to `content_items.id` per A1. CTO-confirmed.

---

### v2.4 — Locked BUILD Deliverables (B7)

ptt-fullstack BUILD scope (engineering flow stays BUILD → SECURITY → QA → SHIP):

1. **D1 migration** at `workers/blog-publish-hook/migrations/0001_published_blog_posts.sql`:
```sql
CREATE TABLE IF NOT EXISTS published_blog_posts (
  slug TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  published_at TEXT NOT NULL,
  detected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  thread_queued_content_item_id TEXT,        -- A1: TEXT, matches content_items.id (UUID)
  thread_queued_at TEXT,
  status TEXT NOT NULL DEFAULT 'detected'    -- detected | queued | failed | skipped
);
CREATE INDEX IF NOT EXISTS idx_pbp_status ON published_blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_pbp_detected_at ON published_blog_posts(detected_at);

CREATE TABLE IF NOT EXISTS worker_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
-- A5: seed first_deploy_timestamp on first cron tick if not present
```

2. **social-api adapter** in `workers/social-api/src/worker.js` around line 3937 (`handleCreateContent`):
   - Add system-role bypass per A2
   - Either reuse `ROUTER_API_KEY` or add parallel `BLOG_HOOK_API_KEY` per A4
   - Configure house-account `social_account_id` (the @purebrain.ai bsky account owner) as a Worker secret on social-api side, e.g. `BLOG_HOOK_HOUSE_SOCIAL_ACCOUNT_ID`

3. **Worker source** at `workers/blog-publish-hook/src/worker.js`:
   - Cron handler (`*/10 * * * *`)
   - Fetch `https://purebrain.ai/blog/`, parse post slugs+dates from HTML
   - Diff against `published_blog_posts` table
   - For each new slug: fetch post page, build draft thread skeleton (deterministic template — no AI at hook time), POST to `https://social-api.purebrain.ai/api/content` with `Authorization: Bearer ${SOCIAL_API_SYSTEM_TOKEN}`, payload per A3
   - On success: insert `status='queued'` with `thread_queued_content_item_id` from response
   - On failure: insert `status='failed'`, retry next tick (max 3 attempts)
   - Apply A5 timestamp rule before queueing
   - Log line per tick: `[blog-hook] cron tick — N detected, M queued, K failed`

4. **wrangler.toml** at `workers/blog-publish-hook/wrangler.toml`:
   - D1 binding to `purebrain-social`
   - Cron trigger `*/10 * * * *`
   - Secrets: `SOCIAL_API_SYSTEM_TOKEN` (maps to `ROUTER_API_KEY` value or new `BLOG_HOOK_API_KEY` per A4)

5. **Local test harness** + integration test stub for parser (regex against fixture HTML), dedupe logic, and skipped/detected branching per A5.

**Deploy command** (per A6): `wrangler deploy` from `workers/blog-publish-hook/`.

---

### v2.5 — B7 Sub-task: Self-Healing Session BOOP (folded in)

**Origin**: ptt-fullstack B5 recommendation. The 20-day dormancy was caused by a revoked token; without auto-relog, this WILL recur.

**Scope**: Daily BOOP (or fold into existing `logs/bsky-presence-boop/`) that:
1. Calls `getAuthorFeed(actor='purebrain.ai', limit=1)` against own session
2. On `ExpiredToken`: auto-re-login from `.env` `BSKY_USERNAME` + `BSKY_PASSWORD`, rewrite session files at canonical paths (perms 600), Telegram-alert success/failure
3. On success: log `[bsky-session-health] OK` and exit

**Owner**: ptt-fullstack — BUILD as B7 sub-task (same dispatch, no extra fan-out).
**Acceptance**: simulate token revocation in staging by writing a garbage session string, confirm BOOP detects, re-logs, and verifies. Integration with existing presence BOOP optional but preferred.

**Effort**: ~2-4 hours; trivially small relative to B7 main Worker.

---

### v2.6 — Sibling Work — Skill Rewrite (parallel to B7, NOT a B7 dependency)

**Title**: Rewrite `bluesky-blog-thread` skill for kanban routing
**Owner**: capability-curator + ptt-fullstack (skill author + implementor)
**Status**: NEW — to be dispatched separately after B7 fires
**Blocks**: NOTHING. Independent of B7.

**Spec**:

The current `.claude/skills/bluesky-blog-thread/SKILL.md` describes a direct-atproto posting path that violates the constitutional kanban-SoT rule. Rewrite as the human-driven sibling of B7's publish-hook Worker:

1. **New flow**: skill fetches blog post → generates thread draft (Claude API or template) → POSTs to `social-api` `/api/content` with `status='draft'` → returns kanban URL for human review
2. **Same auth surface as B7**: uses `ROUTER_API_KEY` (or `BLOG_HOOK_API_KEY` per A4) — shares secret rotation with the Worker
3. **Same payload shape as B7** per A3: `body` string + `content_type='blog-thread'` + JSON-stringified `metadata`
4. **Same house-account `social_account_id`** as B7 — coordinated via shared social-api adapter
5. **Implementation file**: `.claude/skills/bluesky-blog-thread/blog_to_thread.py` (currently absent)
6. **SKILL.md rewrite**: drop the `🚨 UNTESTED` flag, replace direct-atproto narrative with kanban-routing narrative, document the dependency on B7's social-api adapter

**Why this is the right shape**: The skill becomes a thin wrapper around the same social-api endpoint B7 uses. Skill (human-driven) and B7 Worker (mechanical) are siblings, not competitors. A blog post can be threaded either by a human running the skill OR automatically by the cron Worker. Both paths land in the kanban as drafts. Both go through the same approval flow. No constitutional contradiction.

**Constraint**: This work CANNOT begin until B7's social-api adapter (A2 + A4) is deployed, because the skill depends on the same system-role bypass. So sibling work is **gated on B7 SHIP**, not on B7 BUILD. (Could BUILD in parallel against staging social-api, but cannot SHIP without B7 SHIP.)

---

### v2.7 — Updated Implementation Tracker

| Item | Status (v1) | Status (v2) | Owner | Notes |
|------|-------------|-------------|-------|-------|
| B4: Verify bluesky-blog-thread skill | NOT STARTED | **DEPRECATED — re-scoped, see v2.6** | — | Skill is phantom; verification ticket dissolved into rewrite ticket |
| B5: Refresh Bsky session | NOT STARTED | **✅ PASS** | ptt-fullstack | Session regenerated; recommend self-healing BOOP per v2.5 |
| B6.1: D1 migration | NOT STARTED | READY (with A1, A5 fixes) | ptt-fullstack | |
| B6.2: Worker source code | NOT STARTED | READY (with A2, A3, A4, A6) | ptt-fullstack | |
| B6.3: Local test harness | NOT STARTED | READY | ptt-fullstack | |
| B6.4: social-api adapter | (was inline) | **NEW EXPLICIT TASK** | ptt-fullstack | A2 + A4 — must land in social-api before Worker can call |
| B6.5: Self-healing session BOOP | (not in v1) | **NEW SUB-TASK** | ptt-fullstack | v2.5 |
| B6.6: Security review | NOT STARTED | After BUILD | security-engineer-tech | |
| B6.7: QA test plan + execution | NOT STARTED | After SECURITY | qa-engineer + ptt-qa | |
| B6.8: Production deploy | NOT STARTED | After QA, `wrangler deploy` | devops-engineer | |
| B6.9: Smoke test + 24h monitor | NOT STARTED | Post-ship | devops-engineer | |
| B6.10: Pair verify | NOT STARTED | After SHIP, independent | OP# | |
| Sibling: Skill rewrite | (not in v1) | **NEW PARALLEL TICKET** | capability-curator + ptt-fullstack | v2.6 — gated on B7 SHIP for prod, can BUILD against staging |
| Routing memo archive | NOT STARTED | After B7 ship + OP# verify | this dept | |

---

### v2.8 — What's UNCHANGED from v1

- Cron-poll architecture (10 min interval)
- BUILD → SECURITY → QA → SHIP flow
- Pre-build checklist answers (already passed; not re-running per Aether's directive)
- Constitutional compliance: NO direct bsky-manager, NO container deploys, social.purebrain.ai is SoT
- Initial backfill philosophy: existing 9 posts seeded as `skipped` (MA# handles backfill manually via Track A2)
- Risks + Mitigations table from v1
- Acceptance Criteria: first new blog post → kanban row within 15 min, no false positives, no double-queue, regression-free, OP# pair-verify passes, first new @purebrain.ai post within 48h post-ship

---

### v2.9 — Verification Statement

Spec v2 reflects:
- ✅ All 6 CTO amendments locked into BUILD instructions (A1-A6)
- ✅ B5 PASS recorded; session healthy; downstream MA# backfill unblocked
- ✅ B4 re-scoped from prereq to sibling work (skill rewrite); does NOT gate B7
- ✅ Self-healing session BOOP added as B7 sub-task
- ✅ D1 stays in `purebrain-social` (FK integrity per CTO)
- ✅ Wrangler deploy (Workers) confirmed as ship command (NOT cf-deploy.py)

**Spec status**: **READY FOR B7 BUILD.** ptt-fullstack is the next dispatch. CTO sign-off complete; no further architectural review needed before BUILD.

— dept-systems-technology, 2026-05-02 23:25 UTC
