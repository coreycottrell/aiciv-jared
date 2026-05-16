/**
 * blog-publish-hook — CF Worker
 *
 * Cron polls purebrain.ai/blog/, diffs new posts against D1 published_blog_posts,
 * and queues a Bluesky thread DRAFT into social.purebrain.ai kanban via social-api
 * `POST /api/content`.
 *
 * Constitutional: writes to social-api (kanban = source of truth). Never posts
 * to Bluesky directly. ContentRouter handles posting downstream.
 *
 * Spec:        .claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md (v2)
 * CTO sign-off: APPROVED-WITH-AMENDMENTS (A1-A6 applied below)
 *
 * Bindings:
 *   env.DB                          D1 — purebrain-social
 *   env.SOCIAL_API_SYSTEM_TOKEN     Secret — maps to social-api ROUTER_API_KEY (A4)
 *   env.BLOG_HOOK_HOUSE_ACCOUNT_ID  Secret — social_accounts.id of @purebrain.ai bsky row
 *   env.BLOG_INDEX_URL              Var    — usually https://purebrain.ai/blog/
 *   env.SOCIAL_API_BASE             Var    — usually https://social-api.purebrain.ai
 *   env.HOUSE_PLATFORM              Var    — "bluesky"
 *   env.MAX_RETRIES                 Var    — default "3"
 *   env.TG_BOT_TOKEN                Secret — optional, for alerts (NOT used by worker today; OP# polls D1)
 *
 * Cron schedule: every 10 minutes (see wrangler.toml triggers)
 */

// ============================================================================
// Helpers
// ============================================================================

function nowIso() {
  return new Date().toISOString();
}

function logTick(env, msg) {
  // Worker logs are pulled by `wrangler tail`. Prefix lets OP# grep cleanly.
  console.log(`[blog-hook] ${msg}`);
}

// ============================================================================
// Blog index parsing
// ============================================================================

/**
 * Parses purebrain.ai/blog/ HTML for post entries.
 *
 * The blog uses WP latest-posts blocks. Each entry block looks like:
 *   <a class="wp-block-latest-posts__post-title" href="/blog/{slug}/">{title}</a>
 *   <time datetime="{ISO 8601}" class="wp-block-latest-posts__post-date">{human-date}</time>
 *
 * The two elements are siblings under the same <li>, so we use a single regex
 * that captures slug + title + iso-datetime in one shot.
 *
 * Returns: [{ slug, title, url, published_at }, ...]
 *
 * Tolerance: if the format changes and zero posts match, the worker logs and
 * exits cleanly (no false positives, no kanban flood).
 */
export function parseBlogIndex(html, baseUrl = "https://purebrain.ai") {
  const posts = [];
  // Capture: anchor with title-class href slug, then capture title text up to closing </a>,
  // then a <time> with datetime attribute. Allow arbitrary whitespace + minor markup between.
  const re = /<a\s+class="wp-block-latest-posts__post-title"\s+href="\/blog\/([a-z0-9][a-z0-9-]*)\/?"[^>]*>([^<]+)<\/a>\s*<time\s+datetime="([^"]+)"/gi;
  let m;
  const seen = new Set();
  while ((m = re.exec(html)) !== null) {
    const slug = m[1];
    if (seen.has(slug)) continue;        // dedupe in-page (some posts appear twice in WP blocks)
    seen.add(slug);
    posts.push({
      slug,
      title: decodeHtml(m[2].trim()),
      url: `${baseUrl}/blog/${slug}/`,
      published_at: m[3],
    });
  }
  return posts;
}

function decodeHtml(s) {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ");
}

// ============================================================================
// A5 — Backfill timestamp rule
// ============================================================================

/**
 * Returns the worker_first_deploy_timestamp from D1, creating it on first call.
 * This is the cutoff used by the backfill rule:
 *   post.published_at < first_deploy_timestamp  →  status='skipped'
 *   post.published_at >= first_deploy_timestamp →  status='detected' (queue it)
 *
 * Idempotent: if the row exists, return it; if not, INSERT once and return.
 * Survives DB rebuild / worker redeploy with the same semantics.
 */
async function getFirstDeployTimestamp(env) {
  const row = await env.DB.prepare(
    "SELECT value FROM worker_metadata WHERE key = 'first_deploy_timestamp'"
  ).first();
  if (row && row.value) return row.value;

  const ts = nowIso();
  // Use OR IGNORE in case a parallel cron tick raced us.
  await env.DB.prepare(
    "INSERT OR IGNORE INTO worker_metadata (key, value) VALUES ('first_deploy_timestamp', ?)"
  ).bind(ts).run();

  // Re-read to get the canonical value (someone else may have won the race).
  const fresh = await env.DB.prepare(
    "SELECT value FROM worker_metadata WHERE key = 'first_deploy_timestamp'"
  ).first();
  return fresh.value;
}

// ============================================================================
// Thread draft template (deterministic — no AI at hook time, per spec)
// ============================================================================

/**
 * Builds the placeholder thread skeleton. A human (or downstream AI agent
 * working from the kanban UI) fills in posts 2-5 before flipping to Final.
 *
 * Returns a single string suitable for content_items.body. Posts are
 * separated by `\n\n---\n\n` so the kanban renderer can preview them as
 * a series. ContentRouter (downstream) parses this same separator when it
 * pushes to Bluesky as a thread.
 */
function buildThreadDraft(post) {
  const sep = "\n\n---\n\n";
  return [
    `🧵 ${post.title}`,
    `[DRAFT — fill from blog body / first paragraph]`,
    `[DRAFT]`,
    `[DRAFT]`,
    `[DRAFT]`,
    `Full read: ${post.url}\n\n🤖`,
  ].join(sep);
}

// ============================================================================
// social-api call
// ============================================================================

async function postToSocialApi(env, post) {
  const payload = {
    // A3 — payload shape:
    social_account_id: env.BLOG_HOOK_HOUSE_ACCOUNT_ID,
    platform:          env.HOUSE_PLATFORM || "bluesky",
    status:            "draft",
    body:              buildThreadDraft(post),
    content_type:      "blog-thread",
    metadata:          JSON.stringify({
      source:   "blog-publish-hook",
      slug:     post.slug,
      blog_url: post.url,
      title:    post.title,
      published_at: post.published_at,
      detected_at:  nowIso(),
    }),
  };

  const res = await fetch(`${env.SOCIAL_API_BASE}/api/content`, {
    method: "POST",
    headers: {
      "authorization": `Bearer ${env.SOCIAL_API_SYSTEM_TOKEN}`,
      "content-type":  "application/json",
    },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  let parsed = null;
  try { parsed = JSON.parse(text); } catch { /* keep raw */ }

  return {
    ok:      res.ok,
    status:  res.status,
    body:    parsed || text,
    item_id: parsed?.item?.id || null,
  };
}

// ============================================================================
// D1 — published_blog_posts table operations
// ============================================================================

async function getKnownSlugs(env) {
  const { results } = await env.DB.prepare(
    "SELECT slug, status, retry_count FROM published_blog_posts"
  ).all();
  const map = new Map();
  for (const r of (results || [])) map.set(r.slug, r);
  return map;
}

async function insertPost(env, post, status, contentItemId, errorMsg) {
  await env.DB.prepare(
    `INSERT INTO published_blog_posts
       (slug, url, title, published_at, detected_at, status, thread_queued_content_item_id, thread_queued_at, last_error)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(slug) DO NOTHING`
  ).bind(
    post.slug, post.url, post.title, post.published_at, nowIso(),
    status, contentItemId || null, contentItemId ? nowIso() : null, errorMsg || null
  ).run();
}

async function markFailed(env, slug, errorMsg, retryCount) {
  await env.DB.prepare(
    `UPDATE published_blog_posts
        SET status = 'failed', last_error = ?, retry_count = ?
      WHERE slug = ?`
  ).bind(errorMsg.slice(0, 500), retryCount, slug).run();
}

async function markQueued(env, slug, contentItemId) {
  await env.DB.prepare(
    `UPDATE published_blog_posts
        SET status = 'queued', thread_queued_content_item_id = ?, thread_queued_at = ?, last_error = NULL
      WHERE slug = ?`
  ).bind(contentItemId, nowIso(), slug).run();
}

// ============================================================================
// Cron handler
// ============================================================================

export async function runTick(env) {
  const tickStart = Date.now();

  // Fetch blog index. We treat any HTTP error as a transient infra problem and
  // bail this tick (next one in 10 min retries naturally).
  let html;
  try {
    const res = await fetch(env.BLOG_INDEX_URL, {
      // CF default cache is fine; we don't need bleeding-edge freshness.
      cf: { cacheTtl: 60, cacheEverything: true },
    });
    if (!res.ok) {
      logTick(env, `fetch failed: HTTP ${res.status} on ${env.BLOG_INDEX_URL}`);
      return { detected: 0, queued: 0, failed: 0, skipped: 0, error: `http_${res.status}` };
    }
    html = await res.text();
  } catch (e) {
    logTick(env, `fetch threw: ${(e?.message || e).toString().slice(0, 200)}`);
    return { detected: 0, queued: 0, failed: 0, skipped: 0, error: "fetch_threw" };
  }

  const posts = parseBlogIndex(html);
  if (posts.length === 0) {
    logTick(env, `parser returned 0 posts — index format may have changed; bailing tick`);
    return { detected: 0, queued: 0, failed: 0, skipped: 0, error: "parser_empty" };
  }

  const firstDeployTs = await getFirstDeployTimestamp(env);
  const known = await getKnownSlugs(env);

  const maxRetries = parseInt(env.MAX_RETRIES || "3", 10);
  let counters = { detected: 0, queued: 0, failed: 0, skipped: 0 };

  for (const post of posts) {
    const existing = known.get(post.slug);

    // Already-known posts: only retry if previously failed and under retry budget.
    if (existing) {
      if (existing.status === "failed" && (existing.retry_count || 0) < maxRetries) {
        const result = await postToSocialApi(env, post);
        if (result.ok && result.item_id) {
          await markQueued(env, post.slug, result.item_id);
          counters.queued += 1;
          logTick(env, `retry success: ${post.slug} -> content_item ${result.item_id}`);
        } else {
          const errMsg = `retry_${(existing.retry_count || 0) + 1}: HTTP ${result.status} ${typeof result.body === "string" ? result.body : JSON.stringify(result.body)}`;
          await markFailed(env, post.slug, errMsg, (existing.retry_count || 0) + 1);
          counters.failed += 1;
          logTick(env, `retry failed: ${post.slug} (${errMsg.slice(0, 120)})`);
        }
      }
      continue;
    }

    // New post — apply A5 backfill rule.
    if (post.published_at < firstDeployTs) {
      await insertPost(env, post, "skipped", null, null);
      counters.skipped += 1;
      continue;
    }

    counters.detected += 1;

    // Queue draft to social-api kanban.
    const result = await postToSocialApi(env, post);
    if (result.ok && result.item_id) {
      await insertPost(env, post, "queued", result.item_id, null);
      counters.queued += 1;
      logTick(env, `queued: ${post.slug} -> content_item ${result.item_id}`);
    } else {
      const errMsg = `HTTP ${result.status}: ${typeof result.body === "string" ? result.body.slice(0, 300) : JSON.stringify(result.body).slice(0, 300)}`;
      await insertPost(env, post, "failed", null, errMsg);
      counters.failed += 1;
      logTick(env, `failed: ${post.slug} (${errMsg.slice(0, 120)})`);
    }
  }

  const dur = Date.now() - tickStart;
  logTick(
    env,
    `cron tick — ${counters.detected} detected, ${counters.queued} queued, ${counters.failed} failed, ${counters.skipped} skipped in ${dur}ms`
  );
  return counters;
}

// ============================================================================
// HTTP handler — health / manual trigger / status read
// ============================================================================

async function handleHttp(request, env) {
  const url = new URL(request.url);
  if (url.pathname === "/health") {
    return new Response(
      JSON.stringify({ ok: true, name: "blog-publish-hook", time: nowIso() }),
      { headers: { "content-type": "application/json" } }
    );
  }
  // Admin trigger — same secret as cron (gives OP# / on-call a manual tick).
  if (url.pathname === "/run" && request.method === "POST") {
    const auth = request.headers.get("authorization") || "";
    const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
    if (!env.SOCIAL_API_SYSTEM_TOKEN || token !== env.SOCIAL_API_SYSTEM_TOKEN) {
      return new Response(JSON.stringify({ error: "unauthorized" }), {
        status: 401, headers: { "content-type": "application/json" }
      });
    }
    const result = await runTick(env);
    return new Response(JSON.stringify({ ok: true, result }), {
      headers: { "content-type": "application/json" }
    });
  }
  if (url.pathname === "/status") {
    const { results } = await env.DB.prepare(
      "SELECT status, COUNT(*) as c FROM published_blog_posts GROUP BY status"
    ).all();
    return new Response(JSON.stringify({ counts: results || [] }), {
      headers: { "content-type": "application/json" }
    });
  }
  return new Response("blog-publish-hook — try /health, /status, or POST /run", {
    status: 404, headers: { "content-type": "text/plain" }
  });
}

// ============================================================================
// Worker entry points
// ============================================================================

export default {
  async fetch(request, env, ctx) {
    return handleHttp(request, env);
  },
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runTick(env));
  },
};
