# blog-publish-hook — Deployment Runbook

Spec: `.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md`
Owner of this file: ptt-fullstack (BUILD). Hand-off target: devops-engineer (B10 SHIP).

**DO NOT DEPLOY TO PRODUCTION UNTIL B8 SECURITY + B9 QA GATES PASS.**

---

## Pre-flight checks (run before ANY deploy)

1. Verify D1 schema for `purebrain-social` matches spec:
   ```bash
   wrangler d1 execute purebrain-social --remote \
     --command "PRAGMA table_info(content_items)" | grep -E "metadata|title"
   ```
   - If `metadata` column missing → run migration 0002 BEFORE deploying social-api patch.
   - If `metadata` column present → skip migration 0002; the column is already there.

2. Confirm @purebrain.ai social_accounts row exists, capture its id:
   ```bash
   wrangler d1 execute purebrain-social --remote \
     --command "SELECT id, user_id, platform, account_handle FROM social_accounts WHERE platform='bluesky' AND account_handle LIKE '%purebrain.ai%'"
   ```
   Record the `id` — that becomes the `BLOG_HOOK_HOUSE_ACCOUNT_ID` secret.

3. Verify ROUTER_API_KEY exists on social-api:
   ```bash
   cd workers/social-api && wrangler secret list
   ```
   If absent, set it: `wrangler secret put ROUTER_API_KEY` (use a strong random value; share with blog-publish-hook).

---

## Deploy order (CRITICAL — do not reorder)

Workers are deployed in dependency order: D1 schema → social-api patch → blog-publish-hook.

### Step 1 — D1 migrations (purebrain-social)

```bash
cd workers/blog-publish-hook
wrangler d1 execute purebrain-social --remote --file migrations/0001_published_blog_posts.sql
# If pre-flight #1 above showed metadata column MISSING, also run:
wrangler d1 execute purebrain-social --remote --file migrations/0002_content_items_metadata.sql
```

Verify:
```bash
wrangler d1 execute purebrain-social --remote --command "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('published_blog_posts','worker_metadata')"
```

### Step 2 — Deploy social-api patch (system-role bypass)

```bash
cd workers/social-api
wrangler deploy
# Verify deploy succeeded:
curl -sS https://social-api.purebrain.ai/health
# Quick regression check — non-system caller still gets 401/404 as before:
curl -sS https://social-api.purebrain.ai/api/content -X POST -H "content-type: application/json" -d '{}' -w "\nHTTP %{http_code}\n"
# Expected: HTTP 401, error: unauthorized
```

### Step 3 — Deploy blog-publish-hook Worker

```bash
cd workers/blog-publish-hook

# Set required secrets (one-time):
wrangler secret put SOCIAL_API_SYSTEM_TOKEN     # value = ROUTER_API_KEY from social-api
wrangler secret put BLOG_HOOK_HOUSE_ACCOUNT_ID  # value = social_accounts.id from pre-flight #2

# Optional — for failure alerts via Telegram (the worker does NOT call this; OP# uses it):
# wrangler secret put TG_BOT_TOKEN
# wrangler secret put TG_CHAT_ID

# Deploy:
wrangler deploy
```

Verify deploy:
```bash
curl -sS https://blog-publish-hook.in0v8.workers.dev/health
# Expected: {"ok":true,"name":"blog-publish-hook","time":"..."}

curl -sS https://blog-publish-hook.in0v8.workers.dev/status
# Expected: {"counts":[]} or {"counts":[{"status":"detected","c":N},...]}
```

Confirm cron schedule in CF dashboard (Workers → blog-publish-hook → Triggers tab).

### Step 4 — Manual smoke-test of first tick

```bash
# Trigger a manual tick (auth header same as cron):
curl -sS https://blog-publish-hook.in0v8.workers.dev/run \
  -X POST \
  -H "authorization: Bearer $SOCIAL_API_SYSTEM_TOKEN_VALUE" \
  | python3 -m json.tool
```

Expected on first run:
- `result.skipped` = N (all current blog posts → skipped, since they pre-date deploy)
- `result.detected` = 0
- `result.queued` = 0
- `result.failed` = 0

### Step 5 — Verify in D1

```bash
wrangler d1 execute purebrain-social --remote \
  --command "SELECT slug, status, published_at FROM published_blog_posts ORDER BY published_at DESC LIMIT 20"
```
Expected: every blog post listed with `status='skipped'`. Worker_metadata row created.

```bash
wrangler d1 execute purebrain-social --remote \
  --command "SELECT key, value FROM worker_metadata WHERE key='first_deploy_timestamp'"
```
Expected: a single row with current ISO timestamp.

### Step 6 — Tail logs for first natural cron tick

```bash
wrangler tail blog-publish-hook
```

Wait up to 10 min for cron tick. Expect:
```
[blog-hook] cron tick — 0 detected, 0 queued, 0 failed, 0 skipped in NNms
```
(Zero of everything because all known posts are already in D1 as `skipped`.)

### Step 7 — End-to-end test (post-MA# next blog publish)

When MA# publishes the next blog post, watch:
1. `wrangler tail blog-publish-hook` — should log `queued: <slug> -> content_item <id>` within 15 min
2. `social.purebrain.ai` kanban — new draft row should appear with `content_type='blog-thread'`, `metadata.source='blog-publish-hook'`
3. D1 — `SELECT * FROM published_blog_posts WHERE slug='<new-slug>'` → status=`queued`, FK populated.

---

## Rollback

If anything goes wrong:

1. Disable cron — edit `wrangler.toml`, set `crons = []`, `wrangler deploy`.
2. Revert social-api patch — `git checkout workers/social-api/src/worker.js && cd workers/social-api && wrangler deploy`. (No data loss; the patch is purely additive.)
3. D1 cleanup is OPTIONAL (table can stay; it's harmless without the worker writing). To fully revert:
   ```bash
   wrangler d1 execute purebrain-social --remote --command "DROP TABLE published_blog_posts; DROP TABLE worker_metadata"
   ```

---

## Known constraints (passed to QA / SECURITY)

- **No social-api staging twin** — the system-bypass code path can only be exercised against production. QA must coordinate with devops to do a controlled production smoke test (a single manual `/run` call after deploy) rather than full staging environment isolation.
- **`metadata` column on content_items** — was missing from canonical schema (`shared/social-api-schema.sql`) but accepted by UI POST body (`worker.js:1752`). Migration 0002 makes the contract explicit. Verify the column doesn't already exist in production before applying (PRAGMA table_info check above).
- **Token rotation** — `SOCIAL_API_SYSTEM_TOKEN` shares value with social-api `ROUTER_API_KEY`. Rotating one requires updating the other in the same window. Document this in Operations.

---

## Post-ship verification (OP# pair-verify, B11)

1. First new @purebrain.ai blog post published → kanban draft row appears within 15 min.
2. No false positives (existing 11 posts remain `skipped`, never re-queued).
3. No double-queueing under cron retries.
4. social.purebrain.ai existing kanban flows unaffected (regression).
