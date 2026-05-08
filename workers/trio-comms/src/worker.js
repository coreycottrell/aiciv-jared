// Trio Comms Worker — Jared + Aether + Chy + Morphe
// Server-side identity via Bearer tokens; clients cannot claim identity.

const ALLOWED_ORIGINS = [
  "https://purebrain.ai",
  "https://portal.purebrain.ai",
  "https://777.purebrain.ai",
];

const MAX_CONTENT_LEN = 100000;
const DEFAULT_LIMIT = 50;
const MAX_LIMIT = 200;
const RATE_LIMIT_PER_MIN = 20;

function pickOrigin(req) {
  const o = req.headers.get("Origin") || "";
  return ALLOWED_ORIGINS.includes(o) ? o : ALLOWED_ORIGINS[0];
}

function secHeaders(req) {
  return {
    "X-Robots-Tag": "noindex",
    "Access-Control-Allow-Origin": pickOrigin(req),
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Authorization,Content-Type",
    "Vary": "Origin",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'none'",
    "Content-Type": "application/json; charset=utf-8",
  };
}

function json(req, status, body) {
  return new Response(JSON.stringify(body), { status, headers: secHeaders(req) });
}

function authSender(req, env) {
  const h = req.headers.get("Authorization") || "";
  const m = h.match(/^Bearer\s+(.+)$/i);
  if (!m) return null;
  const tok = m[1].trim();
  const map = {
    [env.TRIO_TOKEN_JARED || ""]: "jared",
    [env.TRIO_TOKEN_AETHER || ""]: "aether",
    [env.TRIO_TOKEN_CHY || ""]: "chy",
    [env.TRIO_TOKEN_MORPHE || ""]: "morphe",
  };
  delete map[""];
  return map[tok] || null;
}

async function sha256Hex(s) {
  const buf = new TextEncoder().encode(s);
  const h = await crypto.subtle.digest("SHA-256", buf);
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, "0")).join("");
}

async function checkRateLimit(env, sender) {
  // Simple D1-based: count messages from sender in last 60s.
  const since = new Date(Date.now() - 60_000).toISOString();
  const r = await env.DB
    .prepare("SELECT COUNT(*) AS c FROM trio_messages WHERE sender_id = ? AND timestamp > ?")
    .bind(sender, since)
    .first();
  return (r?.c ?? 0) < RATE_LIMIT_PER_MIN;
}

async function handlePost(req, env) {
  const sender = authSender(req, env);
  if (!sender) return json(req, 401, { error: "unauthorized" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }
  const content = typeof body?.content === "string" ? body.content : "";
  if (!content) return json(req, 400, { error: "content required" });
  if (content.length > MAX_CONTENT_LEN) return json(req, 413, { error: "content too long" });

  // Support optional trio_id for multi-tenant operation
  const trio_id = typeof body?.trio_id === "string" ? body.trio_id : "trio-0";

  if (!(await checkRateLimit(env, sender))) {
    return json(req, 429, { error: "rate limit exceeded" });
  }

  const id = crypto.randomUUID();
  const timestamp = new Date().toISOString();
  const content_hash = await sha256Hex(content);

  await env.DB
    .prepare(
      "INSERT INTO trio_messages (id, timestamp, sender_id, sender_verified, content, content_hash, audit_log, trio_id, media_refs) VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)"
    )
    .bind(id, timestamp, sender, content, content_hash, "[]", trio_id, JSON.stringify(body.media_refs || []))
    .run();

  return json(req, 200, { id, timestamp });
}

async function handleGet(req, env) {
  const sender = authSender(req, env);
  if (!sender) return json(req, 401, { error: "unauthorized" });

  const url = new URL(req.url);
  const since = url.searchParams.get("since");
  const trio_id = url.searchParams.get("trio_id") || "trio-0";
  let limit = parseInt(url.searchParams.get("limit") || String(DEFAULT_LIMIT), 10);
  if (!Number.isFinite(limit) || limit <= 0) limit = DEFAULT_LIMIT;
  if (limit > MAX_LIMIT) limit = MAX_LIMIT;

  let stmt;
  if (since) {
    stmt = env.DB
      .prepare("SELECT id, timestamp, sender_id, sender_verified, content, content_hash, audit_log, media_refs FROM trio_messages WHERE trio_id = ? AND timestamp > ? ORDER BY timestamp DESC LIMIT ?")
      .bind(trio_id, since, limit);
  } else {
    stmt = env.DB
      .prepare("SELECT id, timestamp, sender_id, sender_verified, content, content_hash, audit_log, media_refs FROM trio_messages WHERE trio_id = ? ORDER BY timestamp DESC LIMIT ?")
      .bind(trio_id, limit);
  }
  const { results } = await stmt.all();
  return json(req, 200, results || []);
}

async function handleMarkRead(req, env) {
  const reader = authSender(req, env);
  if (!reader) return json(req, 401, { error: "unauthorized" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }
  const mid = typeof body?.message_id === "string" ? body.message_id : "";
  if (!mid) return json(req, 400, { error: "message_id required" });

  const row = await env.DB
    .prepare("SELECT audit_log FROM trio_messages WHERE id = ?")
    .bind(mid)
    .first();
  if (!row) return json(req, 404, { error: "not found" });

  let log = [];
  try { log = JSON.parse(row.audit_log || "[]"); if (!Array.isArray(log)) log = []; } catch { log = []; }
  log.push({ reader, at: new Date().toISOString() });

  await env.DB
    .prepare("UPDATE trio_messages SET audit_log = ? WHERE id = ?")
    .bind(JSON.stringify(log), mid)
    .run();

  return json(req, 200, { ok: true });
}

async function handleUpload(req, env) {
  const sender = auth(req, env);
  if (!sender) return json(req, 401, { error: "unauthorized" });
  if (!env.UPLOADS) return json(req, 503, { error: "R2 not bound" });

  const formData = await req.formData();
  const file = formData.get("file");
  if (!file) return json(req, 400, { error: "no file" });

  const ts = Date.now();
  const safe = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
  const key = `trio/${sender}/${ts}-${safe}`;

  await env.UPLOADS.put(key, file.stream(), {
    httpMetadata: { contentType: file.type },
    customMetadata: { sender, originalName: file.name, uploadedAt: new Date().toISOString() },
  });

  const url = `https://purebrain-uploads.r2.dev/${key}`;
  return json(req, 201, { key, url, filename: file.name, size: file.size, sender });
}

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: secHeaders(req) });
    }
    const url = new URL(req.url);
    const p = url.pathname;

    if (req.method === "POST" && p === "/trio/message") return handlePost(req, env);
    if (req.method === "GET" && p === "/trio/messages") return handleGet(req, env);
    if (req.method === "POST" && p === "/trio/mark-read") return handleMarkRead(req, env);
    if (req.method === "POST" && p === "/trio/upload") return handleUpload(req, env);
    if (req.method === "GET" && p === "/trio/health") return json(req, 200, { ok: true });

    return json(req, 404, { error: "not found" });
  },
};
