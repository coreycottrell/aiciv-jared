# CTO Sign-Off — Bluesky Publish-Hook (B6)

**Date**: 2026-05-02
**Type**: teaching + operational
**Topic**: Architectural sign-off pattern — system-token reuse, D1 schema additivity, cron vs webhook tradeoff for static-content publish detection

---

## Context

ST# proposed a CF Worker (`blog-publish-hook`) on 10-min cron that polls `purebrain.ai/blog/`, diffs against a new D1 table in `purebrain-social`, and queues thread-draft skeletons via `POST /api/content` to existing `social-api`. Goal: structurally prevent the next 20-day Bsky dormancy by making blog→bsky-queue mechanical rather than discipline-dependent.

## Decision: APPROVED-WITH-AMENDMENTS

## Key architectural moves I validated

### 1. Cron beats webhook for static-content publish detection
CF Pages deploy webhooks fire on ANY deploy (incl. _redirects edits) — they don't carry semantic "new blog post" info. We'd still need to diff against D1, which IS the cron-poll logic. Webhooks couple to a specific deploy method; cron decouples. 144 invocations/day is <0.15% of free tier. **Lesson: webhooks aren't always faster than polling once you account for the diffing logic that has to run regardless.**

### 2. D1 same-DB additivity beats DB separation when there's a foreign key
The new `published_blog_posts` table has `thread_queued_content_item_id` → `content_items.id`. Splitting DBs would force cross-DB lookups or break referential integrity. Keep coupled tables co-located. **Lesson: "separation of concerns" doesn't mean separation of databases — it means separation of access patterns.**

### 3. Reuse existing system-auth surface, don't invent a new one
social-api already has `ROUTER_API_KEY` → synthetic `role: 'system'` session at worker.js:3717. Build on that, don't duplicate. Either reuse the same secret OR add a parallel constant in the same `getSession()` branch. **Lesson: every M2M auth mechanism is a rotation/key-management cost. Coalesce them.**

### 4. Caught a real bug in the spec
`handleCreateContent` requires `social_account_id` AND scopes to `sess.user_id`. The synthetic system session has `user_id: 'system'`, which won't match any real `social_accounts` row. Spec was about to ship a payload that would 404 on every call. **Required adapter**: system-role bypass that accepts a configured house-account `social_account_id`. Without this, the entire system would silently fail.

Also: spec used `body_json: { posts: [...] }` but the existing endpoint takes `body` (string) + `content_type` + `metadata` (JSON-stringified). Payload reshaping was needed. **Lesson: ALWAYS read the existing endpoint code before signing off on a payload contract claim.**

### 5. Wrangler ban is `pages deploy` only, NOT Workers
The constitutional ban (`feedback_wrangler_banned_cf_deploy_only.md`) targets `wrangler pages deploy` because it deletes pages not in local folder. `wrangler deploy` for Workers is fine and is the production standard for admin-api, welcome-email-api, agentmail-webhook, blog-publisher, trio-comms. **Lesson: read the constitutional rule literally. Don't expand bans by analogy.**

### 6. Backfill: prefer deterministic rules over one-time flags
Spec wanted "init flag on first run" to mark historical posts as `skipped`. I amended to: "if `published_at < worker_first_deploy_timestamp`, insert as `skipped`; else `detected`". This is idempotent under DB rebuild / worker redeploy. **Lesson: any "first run" mechanic is a future bug. Prefer rules expressible in pure-function form over runtime state.**

## The 6 required amendments (ptt-fullstack must apply before SECURITY phase)
1. Schema: `thread_queued_content_id` (INTEGER) → `thread_queued_content_item_id` (TEXT)
2. social-api: system-role bypass in `handleCreateContent` (worker.js:3937)
3. Payload reshape: `body` string + `content_type` + JSON-stringified `metadata`
4. Auth: reuse `ROUTER_API_KEY` (preferred) or parallel constant in `getSession()`
5. Backfill: timestamp comparison rule, not init flag
6. Compliance table fix: `wrangler deploy` for Workers is ✅ not ⚠️

## Pattern for future architectural sign-offs

When asked to sign off on a spec that integrates with an existing system:

1. **Read the existing system's relevant code** (don't trust the spec's claims about its API).
2. **Identify the specific functions/lines** the new system will touch.
3. **Find the auth surface that already exists** before approving a new one.
4. **Validate FK types and shapes** between new tables and existing ones.
5. **Read the constitutional rules literally**, not by analogy.
6. **Distinguish polling vs webhook by the diff cost**, not by raw latency.
7. **Demand pure-function backfill rules**, never one-time flags.

## Files referenced
- `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md` — spec + appended sign-off
- `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js` — getSession(), handleCreateContent(), wrangler.toml
- `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-marketing-advertising/2026-05-02--bsky-dormancy-investigation.md` — parent diagnosis
