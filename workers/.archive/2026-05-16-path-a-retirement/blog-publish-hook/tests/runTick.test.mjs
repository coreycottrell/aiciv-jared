#!/usr/bin/env node
/**
 * Integration test for runTick with a fake D1 + fake fetch.
 *
 * Validates:
 *   - A5 backfill rule (post older than first_deploy_timestamp -> skipped)
 *   - New post within window -> POST to social-api -> insert as queued
 *   - social-api 4xx response -> insert as failed
 *   - Re-running same tick is idempotent (no double-insert via UPSERT semantics)
 *   - Retry path: a previously-failed slug retries up to MAX_RETRIES
 *
 * Run: node workers/blog-publish-hook/tests/runTick.test.mjs
 */

import { runTick } from "../src/worker.js";

// ---- Fake D1 ---------------------------------------------------------------
class FakeD1 {
  constructor() {
    this.metadata = new Map();
    this.posts = new Map(); // slug -> row
  }
  prepare(sql) {
    return new FakeStmt(sql, this);
  }
}

class FakeStmt {
  constructor(sql, db) { this.sql = sql.replace(/\s+/g, " ").trim(); this.db = db; this.args = []; }
  bind(...args) { this.args = args; return this; }
  async first() {
    const sql = this.sql;
    if (sql.startsWith("SELECT value FROM worker_metadata")) {
      const v = this.db.metadata.get("first_deploy_timestamp");
      return v ? { value: v } : null;
    }
    return null;
  }
  async all() {
    if (this.sql.startsWith("SELECT slug, status, retry_count FROM published_blog_posts")) {
      const results = Array.from(this.db.posts.values()).map(r => ({
        slug: r.slug, status: r.status, retry_count: r.retry_count || 0
      }));
      return { results };
    }
    if (this.sql.startsWith("SELECT status, COUNT(*) as c FROM published_blog_posts")) {
      const m = new Map();
      for (const r of this.db.posts.values()) m.set(r.status, (m.get(r.status) || 0) + 1);
      return { results: Array.from(m, ([status, c]) => ({ status, c })) };
    }
    return { results: [] };
  }
  async run() {
    if (this.sql.startsWith("INSERT OR IGNORE INTO worker_metadata")) {
      if (!this.db.metadata.has("first_deploy_timestamp")) {
        this.db.metadata.set("first_deploy_timestamp", this.args[0]);
      }
      return;
    }
    if (this.sql.startsWith("INSERT INTO published_blog_posts")) {
      const [slug, url, title, published_at, detected_at, status, content_item_id, queued_at, last_error] = this.args;
      // ON CONFLICT DO NOTHING semantics
      if (this.db.posts.has(slug)) return;
      this.db.posts.set(slug, {
        slug, url, title, published_at, detected_at, status,
        thread_queued_content_item_id: content_item_id, thread_queued_at: queued_at,
        last_error, retry_count: 0
      });
      return;
    }
    if (this.sql.startsWith("UPDATE published_blog_posts SET status = 'queued'")) {
      const [content_item_id, queued_at, slug] = this.args;
      const row = this.db.posts.get(slug);
      if (row) Object.assign(row, { status: "queued", thread_queued_content_item_id: content_item_id, thread_queued_at: queued_at, last_error: null });
      return;
    }
    if (this.sql.startsWith("UPDATE published_blog_posts SET status = 'failed'")) {
      const [last_error, retry_count, slug] = this.args;
      const row = this.db.posts.get(slug);
      if (row) Object.assign(row, { status: "failed", last_error, retry_count });
      return;
    }
  }
}

// ---- Fake fetch (blog index + social-api) ---------------------------------
function makeFakeFetch({ blogHtml, socialApiBehavior }) {
  return async function (url, init) {
    if (url.includes("/blog/") && (!init || init.method === undefined || init.method === "GET")) {
      return new Response(blogHtml, { status: 200, headers: { "content-type": "text/html" } });
    }
    if (url.endsWith("/api/content") && init && init.method === "POST") {
      const result = socialApiBehavior(JSON.parse(init.body));
      return new Response(JSON.stringify(result.body), {
        status: result.status,
        headers: { "content-type": "application/json" }
      });
    }
    throw new Error(`unexpected fetch: ${url}`);
  };
}

// ---- Tests -----------------------------------------------------------------
let pass = 0, fail = 0;
function assertEq(a, b, label) {
  if (JSON.stringify(a) === JSON.stringify(b)) { pass++; console.log(`  PASS  ${label}`); }
  else { fail++; console.log(`  FAIL  ${label}\n    expected ${JSON.stringify(b)}\n    actual   ${JSON.stringify(a)}`); }
}

const FIXTURE = `
  <a class="wp-block-latest-posts__post-title" href="/blog/old-post/">Old Post</a><time datetime="2026-01-01T00:00:00+00:00" class="wp-block-latest-posts__post-date">Jan 1</time>
  <a class="wp-block-latest-posts__post-title" href="/blog/new-post/">New Post</a><time datetime="2099-12-31T00:00:00+00:00" class="wp-block-latest-posts__post-date">Dec 31, 2099</time>
`;

const baseEnv = (db) => ({
  DB: db,
  BLOG_INDEX_URL: "https://purebrain.ai/blog/",
  SOCIAL_API_BASE: "https://social-api.purebrain.ai",
  HOUSE_PLATFORM: "bluesky",
  MAX_RETRIES: "3",
  SOCIAL_API_SYSTEM_TOKEN: "fake-token",
  BLOG_HOOK_HOUSE_ACCOUNT_ID: "house-acct-id",
});

console.log("runTick.test.mjs");

// --- TEST 1: A5 backfill — old post is skipped, new post is queued
{
  const db = new FakeD1();
  globalThis.fetch = makeFakeFetch({
    blogHtml: FIXTURE,
    socialApiBehavior: () => ({ status: 201, body: { item: { id: "ci-new-1" } } }),
  });
  const result = await runTick(baseEnv(db));
  assertEq(result.skipped, 1, "old post (pre-deploy) marked skipped");
  assertEq(result.queued, 1, "new post (post-deploy) queued via social-api");
  assertEq(result.failed, 0, "no failures");
  assertEq(db.posts.get("old-post").status, "skipped", "old-post status=skipped in D1");
  assertEq(db.posts.get("new-post").status, "queued", "new-post status=queued in D1");
  assertEq(db.posts.get("new-post").thread_queued_content_item_id, "ci-new-1", "FK populated with content_item id");
}

// --- TEST 2: Idempotency — running the same tick again does nothing new
{
  const db = new FakeD1();
  globalThis.fetch = makeFakeFetch({
    blogHtml: FIXTURE,
    socialApiBehavior: () => ({ status: 201, body: { item: { id: "ci-new-2" } } }),
  });
  await runTick(baseEnv(db));
  const second = await runTick(baseEnv(db));
  assertEq(second.skipped + second.queued + second.detected + second.failed, 0, "second tick takes no new action");
}

// --- TEST 3: social-api 4xx — post inserted as failed, error captured
{
  const db = new FakeD1();
  globalThis.fetch = makeFakeFetch({
    blogHtml: FIXTURE,
    socialApiBehavior: () => ({ status: 400, body: { error: "social_account_id required" } }),
  });
  const result = await runTick(baseEnv(db));
  assertEq(result.failed, 1, "new post failed insert path");
  assertEq(db.posts.get("new-post").status, "failed", "new-post status=failed in D1");
  if (!db.posts.get("new-post").last_error.includes("400")) {
    fail++; console.log("  FAIL  last_error captures HTTP 400");
  } else { pass++; console.log("  PASS  last_error captures HTTP 400"); }
}

// --- TEST 4: Retry path — failed post retries on next tick, succeeds, becomes queued
{
  const db = new FakeD1();
  let calls = 0;
  globalThis.fetch = makeFakeFetch({
    blogHtml: FIXTURE,
    socialApiBehavior: () => {
      calls++;
      if (calls === 1) return { status: 502, body: { error: "bad gateway" } };
      return { status: 201, body: { item: { id: "ci-retry-1" } } };
    },
  });
  await runTick(baseEnv(db));                           // first tick → failed
  assertEq(db.posts.get("new-post").status, "failed", "tick 1 → failed");
  const second = await runTick(baseEnv(db));            // second tick → retry → queued
  assertEq(db.posts.get("new-post").status, "queued", "tick 2 retry → queued");
  assertEq(second.queued, 1, "tick 2 reports 1 queued (the retry)");
}

// --- TEST 5: Retry budget exhaustion — after MAX_RETRIES, stops retrying
{
  const db = new FakeD1();
  globalThis.fetch = makeFakeFetch({
    blogHtml: FIXTURE,
    socialApiBehavior: () => ({ status: 502, body: { error: "always fails" } }),
  });
  const env = baseEnv(db);
  // 4 ticks (initial + 3 retries) — after that, retry_count == MAX_RETRIES, no more retries
  for (let i = 0; i < 5; i++) await runTick(env);
  const row = db.posts.get("new-post");
  assertEq(row.status, "failed", "still failed after exhaustion");
  if (row.retry_count <= 3) { pass++; console.log("  PASS  retry_count <= MAX_RETRIES (3)"); }
  else { fail++; console.log(`  FAIL  retry_count exceeded MAX_RETRIES: got ${row.retry_count}`); }
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
