// Trio Comms Worker — Jared + Aether + Chy + Morphe + per-customer rooms
// Server-side identity via Bearer tokens (AI) and portal session (human).
//
// Thread B Phase 1 (2026-05-12): added rooms/* endpoints for in-portal
// DUO/TRIO chat. Backward-compat: /trio/* endpoints continue working
// unchanged — they internally map to room_id = 'room_' || trio_id.
//
// Endpoints:
//   Legacy:
//     POST /trio/message            (existing)
//     GET  /trio/messages           (existing)
//     POST /trio/mark-read          (existing)
//     POST /trio/upload             (existing, hotfixed)
//     GET  /trio/health             (existing)
//   Rooms (new):
//     POST   /rooms/ensure                  — idempotent room+member upsert
//     GET    /rooms/{id}                    — read room + members
//     PATCH  /rooms/{id}                    — update name / retention
//     POST   /rooms/{id}/messages           — post with seq + idempotency
//     GET    /rooms/{id}/messages           — cursor-paginate by seq
//     POST   /rooms/{id}/upload             — multipart, ≤25MB, R2
//     GET    /media/{key}                   — auth+membership-gated R2 proxy
//     POST   /rooms/{id}/heartbeat          — AI presence ping
//     GET    /rooms/{id}/presence           — list members + last_seen
//     POST   /rooms/{id}/mark-read          — audit-log read receipt
//   Internal:
//     GET    /health                        — public health
//
// Dual-auth (Day 3): /rooms/* endpoints accept EITHER
//   (a) AI bearer token (TRIO_TOKEN_*) — same identity map as legacy
//   (b) Human portal session cookie / Bearer (validated via SOCIAL_API binding)
// Membership in `room_members` is checked before any read/write.

const ALLOWED_ORIGINS = [
  "https://purebrain.ai",
  "https://portal.purebrain.ai",
  "https://app.purebrain.ai",
  "https://777.purebrain.ai",
];

const MAX_CONTENT_LEN = 100000;
const DEFAULT_LIMIT = 50;
const MAX_LIMIT = 200;
const RATE_LIMIT_PER_MIN = 20;

// Attachment limits (CTO Decision 1, 2026-05-12)
const MAX_UPLOAD_BYTES = 25 * 1024 * 1024; // 25 MB per-file
const MAX_ATTACHMENTS_PER_MSG = 5;
// MIME allowlist — images, docs, plain text, JSON, ZIP, AUDIO (Jared 2026-05-12 Phase 1)
const ALLOWED_MIME_PREFIXES = ["image/", "audio/", "text/"];
const ALLOWED_MIME_EXACT = new Set([
  "application/pdf",
  "application/json",
  "application/zip",
  "audio/mpeg",
  "audio/wav",
  "audio/mp4",
  "audio/webm",
  "audio/ogg",
]);

function pickOrigin(req) {
  const o = req.headers.get("Origin") || "";
  return ALLOWED_ORIGINS.includes(o) ? o : ALLOWED_ORIGINS[0];
}

function secHeaders(req) {
  return {
    "X-Robots-Tag": "noindex",
    "Access-Control-Allow-Origin": pickOrigin(req),
    "Access-Control-Allow-Methods": "GET,POST,PATCH,OPTIONS",
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

// =========================================================================
// AUTH
// =========================================================================

// AI identity — matches Bearer token to sender_id slug.
//
// Day 6 (2026-05-13): authSender is now async. FAST-PATH on the 4 legacy
// fixed tokens BEFORE the D1 lookup. Per-customer AI tokens fall through to
// ai_tokens table (sha256(token) → row). Legacy traffic pays zero D1 cost.
//
// Sender_id format:
//   Legacy fixed: "jared" | "aether" | "chy" | "morphe"
//   Customer AI:  "ai:{customer_id}:{ai_id}"  (e.g. "ai:cust_42:keen")
async function authSender(req, env) {
  const h = req.headers.get("Authorization") || "";
  const m = h.match(/^Bearer\s+(.+)$/i);
  if (!m) return null;
  const tok = m[1].trim();

  // 1. Fast path: 4 legacy fixed tokens (zero D1 hit)
  const map = {
    [env.TRIO_TOKEN_JARED || ""]: "jared",
    [env.TRIO_TOKEN_AETHER || ""]: "aether",
    [env.TRIO_TOKEN_CHY || ""]: "chy",
    [env.TRIO_TOKEN_MORPHE || ""]: "morphe",
  };
  delete map[""];
  if (map[tok]) return map[tok];

  // 2. Per-AI customer tokens: hash + D1 lookup (indexed PK)
  if (!env.DB) return null;
  let tokenHash;
  try {
    tokenHash = await sha256Hex(tok);
  } catch {
    return null;
  }
  const row = await env.DB
    .prepare("SELECT customer_id, ai_id FROM ai_tokens WHERE token_hash = ? AND revoked_at IS NULL")
    .bind(tokenHash)
    .first();
  if (!row) return null;

  // Fire-and-forget last_used_at touch (do NOT await; never log plaintext)
  try {
    env.DB.prepare("UPDATE ai_tokens SET last_used_at = ? WHERE token_hash = ?")
      .bind(Date.now(), tokenHash).run();
  } catch { /* swallow */ }

  return `ai:${row.customer_id}:${row.ai_id}`;
}

// Human identity via portal session (Day 3 dual-auth).
// Validates Bearer/cookie against social-api /internal/validate-session.
// Same pattern as purebrain-portal-proxy validateLeaderSession at commit 08922b7.
// Returns { sender_id: "human:{email}", display_name, role } or null.
async function authHumanViaPortalProxy(req, env) {
  let token = "";
  const auth = req.headers.get("Authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7).trim();
  if (!token) {
    const cookies = req.headers.get("Cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return null;
  if (!env.SOCIAL_API || !env.INTERNAL_BINDING_SECRET) return null;

  try {
    const validateReq = new Request("https://social-api/internal/validate-session", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding": "social-api",
        "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
      },
      body: JSON.stringify({ token }),
    });
    const resp = await env.SOCIAL_API.fetch(validateReq);
    if (!resp.ok) return null;
    const j = await resp.json();
    if (!j || j.valid !== true) return null;
    // social-api returns at minimum {valid, email, role, client_id, goes_by?}.
    // Map to room member identity: sender_id = "human:{email}".
    const email = (j.email || "").toLowerCase();
    if (!email) return null;
    return {
      sender_id: `human:${email}`,
      display_name: j.goes_by || j.name || email,
      role: j.role || "user",
      client_id: j.client_id || null,
    };
  } catch {
    return null;
  }
}

// Dual-auth: try AI bearer first (cheaper), then human session.
// Returns { sender_id, display_name, member_type } or null.
async function authAny(req, env) {
  const ai = await authSender(req, env);
  if (ai) {
    return { sender_id: ai, display_name: ai, member_type: "ai" };
  }
  const human = await authHumanViaPortalProxy(req, env);
  if (human) {
    return {
      sender_id: human.sender_id,
      display_name: human.display_name,
      member_type: "human",
      role: human.role,
      client_id: human.client_id,
    };
  }
  return null;
}

// Internal-binding auth (Thread B Phase 1 Day 4, 2026-05-13).
// Sibling Workers calling trio-comms via CF Service Binding present
//   x-internal-binding: <caller-id>
//   x-internal-binding-secret: env.INTERNAL_BINDING_SECRET
// Same pattern as paypal-webhook → clients-api / referrals-api.
// Constant-time compare to avoid timing oracle on the shared family secret.
function authInternalBinding(req, env) {
  if (!env.INTERNAL_BINDING_SECRET) return null;
  const caller = req.headers.get("x-internal-binding") || "";
  const presented = req.headers.get("x-internal-binding-secret") || "";
  if (!caller || !presented) return null;
  if (presented.length !== env.INTERNAL_BINDING_SECRET.length) return null;
  let diff = 0;
  for (let i = 0; i < presented.length; i++) {
    diff |= presented.charCodeAt(i) ^ env.INTERNAL_BINDING_SECRET.charCodeAt(i);
  }
  if (diff !== 0) return null;
  return { sender_id: `internal:${caller}`, caller };
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

// =========================================================================
// MEMBERSHIP HELPERS (Day 3)
// =========================================================================

// Verify sender is a member of room with at least the required scope.
// Returns the membership row or null.
async function requireRoomMember(env, room_id, sender_id, requiredScope) {
  const row = await env.DB
    .prepare("SELECT room_id, member_id, member_type, display_name, scopes_json FROM room_members WHERE room_id = ? AND member_id = ?")
    .bind(room_id, sender_id)
    .first();
  if (!row) return null;
  let scopes = ["read", "write", "upload"];
  try { const j = JSON.parse(row.scopes_json || "[]"); if (Array.isArray(j) && j.length) scopes = j; } catch {}
  if (requiredScope && !scopes.includes(requiredScope)) return null;
  return row;
}

// Atomic per-room seq allocation.
async function allocSeq(env, room_id) {
  const r = await env.DB
    .prepare(
      "INSERT INTO room_seq_counters (room_id, next_seq) VALUES (?, 2) " +
      "ON CONFLICT(room_id) DO UPDATE SET next_seq = next_seq + 1 RETURNING next_seq"
    )
    .bind(room_id)
    .first();
  // On first insert next_seq=2 is stored; the message just assigned gets seq=1.
  // On conflict, stored=N+1; message assigned gets seq=N+1.
  // To keep semantics simple, we return (stored - 1) on first insert and stored
  // on conflict. But the RETURNING gives us only the post-update value.
  // Simpler approach: always treat returned value as "next available seq" and
  // subtract 1, with the initial INSERT seeding to 2 so first message = 1.
  return (r?.next_seq ?? 1) - 1;
}

function isAllowedMime(mime) {
  if (!mime || typeof mime !== "string") return false;
  if (ALLOWED_MIME_EXACT.has(mime)) return true;
  for (const p of ALLOWED_MIME_PREFIXES) if (mime.startsWith(p)) return true;
  return false;
}

function sanitizeFilename(name) {
  return (name || "file").replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 120);
}

// =========================================================================
// LEGACY /trio/* HANDLERS (unchanged behavior, kept for backward-compat)
// =========================================================================

async function handlePost(req, env) {
  const sender = await authSender(req, env);
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
  // Mirror to room model: legacy posts populate room_id so /rooms/* reads them.
  const room_id = `room_${trio_id}`;

  await env.DB
    .prepare(
      "INSERT INTO trio_messages (id, timestamp, sender_id, sender_verified, content, content_hash, audit_log, trio_id, media_refs, room_id) VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)"
    )
    .bind(id, timestamp, sender, content, content_hash, "[]", trio_id, JSON.stringify(body.media_refs || []), room_id)
    .run();

  return json(req, 200, { id, timestamp });
}

async function handleGet(req, env) {
  const sender = await authSender(req, env);
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
  const reader = await authSender(req, env);
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
  // 2026-05-12 hotfix: was calling undefined `auth()` (caused HTTP 500/1101 on all
  // /trio/upload calls since v1 ship). Corrected to authSender() — the only
  // identity function in this worker. Live regression confirmed via curl probe
  // before this fix returned 500; after fix returns 401 for invalid bearer.
  // 2026-05-13 Day 6: authSender now async (per-AI token D1 lookup).
  const sender = await authSender(req, env);
  if (!sender) return json(req, 401, { error: "unauthorized" });
  if (!env.UPLOADS) return json(req, 503, { error: "R2 not bound" });

  const formData = await req.formData();
  const file = formData.get("file");
  if (!file) return json(req, 400, { error: "no file" });

  const ts = Date.now();
  const safe = sanitizeFilename(file.name);
  const key = `trio/${sender}/${ts}-${safe}`;

  await env.UPLOADS.put(key, file.stream(), {
    httpMetadata: { contentType: file.type },
    customMetadata: { sender, originalName: file.name, uploadedAt: new Date().toISOString() },
  });

  // 2026-05-12 hotfix: r2.dev public URL is BANNED per constitutional rule
  // (2026-05-04 R2 proxy migration memory + CTO Decision 8.4 in Thread B brief).
  // All attachment reads MUST go through Worker proxy /media/{key}.
  const url = `https://trio-comms.in0v8.workers.dev/media/${key}`;
  return json(req, 201, { key, url, filename: file.name, size: file.size, sender });
}

// =========================================================================
// ROOMS HANDLERS (Days 2-3)
// =========================================================================

// POST /rooms/ensure
// Idempotent: creates room if not exists, ensures all ai_ids are members.
// Body: { customer_id, ai_ids: [...], human?: { email, goes_by } }
// Returns: { room_id, created: bool, members: [...] }
//
// Auth (Day 4): accepts EITHER
//   (a) internal-binding header pair (paypal-webhook auto-provision path,
//       agentmail-webhook, or future sibling Workers)
//   (b) AI bearer token or human portal session (manual/admin path)
// `/rooms/ensure` is the only room endpoint that accepts internal-binding —
// downstream reads/writes still require AI/human membership in the room.
async function handleRoomsEnsure(req, env) {
  const internal = authInternalBinding(req, env);
  const auth = internal ? { sender_id: internal.sender_id, display_name: internal.caller, member_type: "internal" } : await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }

  const customer_id = typeof body?.customer_id === "string" ? body.customer_id.trim() : "";
  if (!customer_id) return json(req, 400, { error: "customer_id required" });

  const ai_ids = Array.isArray(body?.ai_ids) ? body.ai_ids.filter(x => typeof x === "string" && x) : [];
  if (ai_ids.length < 1) return json(req, 400, { error: "ai_ids must be non-empty array" });

  const human = body?.human && typeof body.human === "object" ? body.human : null;
  const room_id = `room_${customer_id}`;
  const now = Date.now();

  // INSERT OR IGNORE on UNIQUE(customer_id) — true idempotency
  const insertRoom = await env.DB
    .prepare(
      "INSERT OR IGNORE INTO rooms (id, customer_id, name, created_at) VALUES (?, ?, ?, ?)"
    )
    .bind(room_id, customer_id, "", now)
    .run();
  const created = (insertRoom.meta?.changes ?? 0) > 0;

  // Seed seq counter (idempotent)
  await env.DB
    .prepare("INSERT OR IGNORE INTO room_seq_counters (room_id, next_seq) VALUES (?, 1)")
    .bind(room_id)
    .run();

  // Upsert AI members + mint per-AI tokens (Day 6, CTO Decision 1)
  // Tokens returned plaintext ONCE in response; only sha256 stored.
  // Per-AI display_name from optional body.ai_display_names map (ai_id → name).
  const aiDisplayNames = (body?.ai_display_names && typeof body.ai_display_names === "object")
    ? body.ai_display_names : {};
  const aiTokens = [];
  for (const ai_id of ai_ids) {
    const display_name = (typeof aiDisplayNames[ai_id] === "string" && aiDisplayNames[ai_id])
      ? aiDisplayNames[ai_id].slice(0, 80) : ai_id;
    await env.DB
      .prepare(
        "INSERT OR IGNORE INTO room_members (room_id, member_id, member_type, display_name, scopes_json, joined_at) " +
        "VALUES (?, ?, 'ai', ?, '[\"read\",\"write\",\"upload\"]', ?)"
      )
      .bind(room_id, ai_id, display_name, now)
      .run();

    // Check existing active token for (customer_id, ai_id) — idempotent
    const existing = await env.DB
      .prepare("SELECT token_hash FROM ai_tokens WHERE customer_id = ? AND ai_id = ? AND revoked_at IS NULL LIMIT 1")
      .bind(customer_id, ai_id)
      .first();
    if (existing) {
      // Already minted — do NOT regenerate (token plaintext already delivered)
      aiTokens.push({ ai_id, display_name, token: null, already_minted: true });
      continue;
    }

    // Mint fresh 256-bit token, base64url-encode (43 chars, URL-safe)
    const rand = crypto.getRandomValues(new Uint8Array(32));
    const tokenPlaintext = base64UrlEncode(rand);
    const tokenHash = await sha256Hex(tokenPlaintext);
    await env.DB
      .prepare(
        "INSERT INTO ai_tokens (token_hash, customer_id, ai_id, display_name, room_id, created_at) " +
        "VALUES (?, ?, ?, ?, ?, ?)"
      )
      .bind(tokenHash, customer_id, ai_id, display_name, room_id, now)
      .run();
    aiTokens.push({ ai_id, display_name, token: tokenPlaintext, already_minted: false });
  }

  // Upsert human member if provided
  if (human && typeof human.email === "string" && human.email) {
    const human_id = `human:${human.email.toLowerCase()}`;
    const display = (human.goes_by || human.email || "").toString().slice(0, 80);
    await env.DB
      .prepare(
        "INSERT OR IGNORE INTO room_members (room_id, member_id, member_type, display_name, scopes_json, joined_at) " +
        "VALUES (?, ?, 'human', ?, '[\"read\",\"write\",\"upload\"]', ?)"
      )
      .bind(room_id, human_id, display, now)
      .run();
  }

  // Return current member list + freshly-minted tokens (plaintext once)
  const { results: members } = await env.DB
    .prepare("SELECT member_id, member_type, display_name, scopes_json, joined_at FROM room_members WHERE room_id = ?")
    .bind(room_id)
    .all();

  return json(req, 200, { room_id, created, members: members || [], ai_tokens: aiTokens });
}

// Helper: base64url-encode bytes (no padding, URL-safe)
function base64UrlEncode(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// POST /rooms/{id}/rotate-ai-token  (internal-binding only)
// Body: { ai_id }
// Revokes old token row, mints new, returns plaintext once.
async function handleRotateAiToken(req, env, room_id) {
  const internal = authInternalBinding(req, env);
  if (!internal) return json(req, 401, { error: "internal binding required" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }
  const ai_id = typeof body?.ai_id === "string" ? body.ai_id.trim() : "";
  if (!ai_id) return json(req, 400, { error: "ai_id required" });

  // Look up room to find customer_id (cannot rotate without knowing customer)
  const room = await env.DB.prepare("SELECT customer_id FROM rooms WHERE id = ?").bind(room_id).first();
  if (!room) return json(req, 404, { error: "room not found" });

  // Revoke any existing active tokens for this (customer_id, ai_id)
  const now = Date.now();
  await env.DB
    .prepare("UPDATE ai_tokens SET revoked_at = ? WHERE customer_id = ? AND ai_id = ? AND revoked_at IS NULL")
    .bind(now, room.customer_id, ai_id)
    .run();

  // Look up display_name from room_members for continuity
  const memberRow = await env.DB
    .prepare("SELECT display_name FROM room_members WHERE room_id = ? AND member_id = ? AND member_type = 'ai'")
    .bind(room_id, ai_id)
    .first();
  const display_name = memberRow?.display_name || ai_id;

  // Mint fresh token
  const rand = crypto.getRandomValues(new Uint8Array(32));
  const tokenPlaintext = base64UrlEncode(rand);
  const tokenHash = await sha256Hex(tokenPlaintext);
  await env.DB
    .prepare(
      "INSERT INTO ai_tokens (token_hash, customer_id, ai_id, display_name, room_id, created_at) " +
      "VALUES (?, ?, ?, ?, ?, ?)"
    )
    .bind(tokenHash, room.customer_id, ai_id, display_name, room_id, now)
    .run();

  return json(req, 200, { ai_id, display_name, token: tokenPlaintext, rotated_at: now });
}

// GET /rooms/{id}
async function handleRoomGet(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "read");
  if (!member) return json(req, 403, { error: "not a room member" });

  const room = await env.DB
    .prepare("SELECT id, customer_id, name, created_at, archived_at, retention_days, attachment_bytes_used FROM rooms WHERE id = ?")
    .bind(room_id)
    .first();
  if (!room) return json(req, 404, { error: "room not found" });

  const { results: members } = await env.DB
    .prepare("SELECT member_id, member_type, display_name, scopes_json, joined_at, last_heartbeat_at, last_seq_seen FROM room_members WHERE room_id = ?")
    .bind(room_id)
    .all();

  return json(req, 200, { room, members: members || [] });
}

// PATCH /rooms/{id}
async function handleRoomPatch(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "write");
  if (!member) return json(req, 403, { error: "not a room member" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }

  const updates = [];
  const binds = [];
  if (typeof body?.name === "string") {
    if (body.name.length > 120) return json(req, 400, { error: "name too long (max 120)" });
    updates.push("name = ?"); binds.push(body.name.slice(0, 120));
  }
  if (Number.isFinite(body?.retention_days)) {
    const rd = parseInt(body.retention_days, 10);
    if (rd < 1 || rd > 36500) return json(req, 400, { error: "retention_days out of range" });
    updates.push("retention_days = ?"); binds.push(rd);
  }
  if (!updates.length) return json(req, 400, { error: "no fields to update" });

  binds.push(room_id);
  await env.DB
    .prepare(`UPDATE rooms SET ${updates.join(", ")} WHERE id = ?`)
    .bind(...binds)
    .run();

  return json(req, 200, { ok: true });
}

// POST /rooms/{id}/messages
// Body: { content, client_msg_id, attachments?: [{url, mime, filename, size}] }
async function handleRoomMessagePost(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "write");
  if (!member) return json(req, 403, { error: "not a room member" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }

  const content = typeof body?.content === "string" ? body.content : "";
  if (!content) return json(req, 400, { error: "content required" });
  if (content.length > MAX_CONTENT_LEN) return json(req, 413, { error: "content too long" });

  const client_msg_id = typeof body?.client_msg_id === "string" && body.client_msg_id
    ? body.client_msg_id.slice(0, 64)
    : crypto.randomUUID();

  const attachments = Array.isArray(body?.attachments) ? body.attachments.slice(0, MAX_ATTACHMENTS_PER_MSG) : [];

  // Rate limit by sender identity
  if (!(await checkRateLimit(env, auth.sender_id))) {
    return json(req, 429, { error: "rate limit exceeded" });
  }

  // Idempotency: if a row exists for (room_id, client_msg_id), return it.
  const existing = await env.DB
    .prepare("SELECT id, seq, timestamp FROM trio_messages WHERE room_id = ? AND client_msg_id = ?")
    .bind(room_id, client_msg_id)
    .first();
  if (existing) {
    return json(req, 200, { id: existing.id, seq: existing.seq, timestamp: existing.timestamp, idempotent: true });
  }

  // Allocate seq atomically
  const seq = await allocSeq(env, room_id);
  const id = crypto.randomUUID();
  const timestamp = new Date().toISOString();
  const content_hash = await sha256Hex(content);

  // Resolve trio_id for backward-compat (mirror room_id back to trio_id).
  // room_id is "room_<x>" → trio_id = "<x>" (stripping prefix).
  const trio_id = room_id.startsWith("room_") ? room_id.slice(5) : "trio-0";

  try {
    await env.DB
      .prepare(
        "INSERT INTO trio_messages (id, timestamp, sender_id, sender_verified, content, content_hash, audit_log, trio_id, media_refs, room_id, seq, client_msg_id, attachments_json) " +
        "VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
      )
      .bind(
        id, timestamp, auth.sender_id, content, content_hash, "[]",
        trio_id, "[]", room_id, seq, client_msg_id, JSON.stringify(attachments)
      )
      .run();
  } catch (e) {
    // Race on UNIQUE(room_id, client_msg_id) — fetch winner row and return it.
    const winner = await env.DB
      .prepare("SELECT id, seq, timestamp FROM trio_messages WHERE room_id = ? AND client_msg_id = ?")
      .bind(room_id, client_msg_id)
      .first();
    if (winner) return json(req, 200, { id: winner.id, seq: winner.seq, timestamp: winner.timestamp, idempotent: true });
    return json(req, 500, { error: "insert failed", detail: String(e).slice(0, 200) });
  }

  return json(req, 200, { id, seq, timestamp });
}

// GET /rooms/{id}/messages?since_seq=N&limit=M
async function handleRoomMessageGet(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "read");
  if (!member) return json(req, 403, { error: "not a room member" });

  const url = new URL(req.url);
  const sinceSeqRaw = url.searchParams.get("since_seq");
  const since_seq = sinceSeqRaw !== null ? parseInt(sinceSeqRaw, 10) : 0;
  let limit = parseInt(url.searchParams.get("limit") || String(DEFAULT_LIMIT), 10);
  if (!Number.isFinite(limit) || limit <= 0) limit = DEFAULT_LIMIT;
  if (limit > MAX_LIMIT) limit = MAX_LIMIT;

  const safeSince = Number.isFinite(since_seq) && since_seq >= 0 ? since_seq : 0;

  const { results } = await env.DB
    .prepare(
      "SELECT id, timestamp, sender_id, content, content_hash, audit_log, attachments_json, seq, client_msg_id " +
      "FROM trio_messages WHERE room_id = ? AND seq IS NOT NULL AND seq > ? " +
      "ORDER BY seq ASC LIMIT ?"
    )
    .bind(room_id, safeSince, limit)
    .all();

  const out = (results || []).map(r => ({
    id: r.id,
    seq: r.seq,
    timestamp: r.timestamp,
    sender: r.sender_id,
    content: r.content,
    content_hash: r.content_hash,
    client_msg_id: r.client_msg_id,
    attachments: safeJsonArray(r.attachments_json),
    audit_log: safeJsonArray(r.audit_log),
  }));

  return json(req, 200, { messages: out, next_since_seq: out.length ? out[out.length - 1].seq : safeSince });
}

function safeJsonArray(s) {
  try { const j = JSON.parse(s || "[]"); return Array.isArray(j) ? j : []; } catch { return []; }
}

// POST /rooms/{id}/upload  (multipart/form-data, ≤25MB, MIME-allowlisted)
async function handleRoomUpload(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "upload");
  if (!member) return json(req, 403, { error: "not a room member or upload scope denied" });
  if (!env.UPLOADS) return json(req, 503, { error: "R2 not bound" });

  // Optional client_msg_id passed via querystring or form field
  const url = new URL(req.url);
  let client_msg_id = url.searchParams.get("client_msg_id") || "";

  let formData;
  try { formData = await req.formData(); } catch { return json(req, 400, { error: "invalid form" }); }

  const file = formData.get("file");
  if (!file || typeof file === "string") return json(req, 400, { error: "no file" });

  if (!client_msg_id) {
    const cm = formData.get("client_msg_id");
    if (typeof cm === "string" && cm) client_msg_id = cm.slice(0, 64);
  }
  if (!client_msg_id) client_msg_id = crypto.randomUUID();

  // Day 7 compression toggle (Jared spec 2026-05-13): accept was_compressed flag.
  // Stored in customMetadata + returned in response. Widget UI shows
  // "Original quality" badge when false. Defaults to false if absent.
  const wasCompressedRaw = (formData.get("was_compressed") || "").toString().toLowerCase();
  const was_compressed = (wasCompressedRaw === "true" || wasCompressedRaw === "1");

  const size = file.size;
  if (!Number.isFinite(size) || size <= 0) return json(req, 400, { error: "empty file" });
  if (size > MAX_UPLOAD_BYTES) return json(req, 413, { error: "file too large (max 25MB)" });

  const mime = file.type || "application/octet-stream";
  if (!isAllowedMime(mime)) return json(req, 415, { error: `mime not allowed: ${mime}` });

  // Check per-room storage cap (hard cap = 5GB)
  const room = await env.DB
    .prepare("SELECT attachment_bytes_used, storage_hard_cap_bytes FROM rooms WHERE id = ?")
    .bind(room_id)
    .first();
  if (!room) return json(req, 404, { error: "room not found" });
  if ((room.attachment_bytes_used || 0) + size > (room.storage_hard_cap_bytes || 5 * 1024 * 1024 * 1024)) {
    return json(req, 507, { error: "room storage cap exceeded" });
  }

  const ts = Date.now();
  const safe = sanitizeFilename(file.name);
  const key = `rooms/${room_id}/${ts}-${client_msg_id}-${safe}`;

  await env.UPLOADS.put(key, file.stream(), {
    httpMetadata: { contentType: mime },
    customMetadata: {
      room_id,
      sender: auth.sender_id,
      originalName: file.name,
      uploadedAt: new Date().toISOString(),
      client_msg_id,
      was_compressed: was_compressed ? "true" : "false",
    },
  });

  // Update room storage counter
  await env.DB
    .prepare("UPDATE rooms SET attachment_bytes_used = attachment_bytes_used + ? WHERE id = ?")
    .bind(size, room_id)
    .run();

  const mediaUrl = `https://trio-comms.in0v8.workers.dev/media/${key}`;
  return json(req, 201, {
    key,
    url: mediaUrl,
    mime,
    size,
    filename: file.name,
    client_msg_id,
    was_compressed,
  });
}

// GET /media/{key}  (auth + room-membership gated R2 proxy)
async function handleMedia(req, env, key) {
  const auth = await authAny(req, env);
  if (!auth) return new Response("unauthorized", { status: 401 });
  if (!env.UPLOADS) return new Response("R2 not bound", { status: 503 });

  // Key shape rules:
  //   rooms/{room_id}/...    → requires room membership
  //   trio/{sender}/...      → legacy; allow any authenticated AI (backward compat)
  if (key.startsWith("rooms/")) {
    const parts = key.split("/");
    if (parts.length < 3) return new Response("invalid key", { status: 400 });
    const room_id = parts[1];
    const member = await requireRoomMember(env, room_id, auth.sender_id, "read");
    if (!member) return new Response("not a room member", { status: 403 });
  } else if (!key.startsWith("trio/")) {
    return new Response("invalid key", { status: 400 });
  }

  const obj = await env.UPLOADS.get(key);
  if (!obj) return new Response("not found", { status: 404 });

  const headers = new Headers();
  headers.set("Content-Type", obj.httpMetadata?.contentType || "application/octet-stream");
  headers.set("Cache-Control", "private, max-age=300");
  headers.set("X-Robots-Tag", "noindex");
  headers.set("Access-Control-Allow-Origin", pickOrigin(req));
  if (obj.size) headers.set("Content-Length", String(obj.size));
  return new Response(obj.body, { status: 200, headers });
}

// POST /rooms/{id}/heartbeat
// Body: { last_seq_seen?: number }
async function handleHeartbeat(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "read");
  if (!member) return json(req, 403, { error: "not a room member" });

  let body = {};
  try { body = await req.json(); } catch { /* tolerate empty body */ }

  const last_seq_seen = Number.isFinite(body?.last_seq_seen) ? parseInt(body.last_seq_seen, 10) : null;
  const now = Date.now();

  if (last_seq_seen !== null && last_seq_seen >= 0) {
    await env.DB
      .prepare("UPDATE room_members SET last_heartbeat_at = ?, last_seq_seen = MAX(last_seq_seen, ?) WHERE room_id = ? AND member_id = ?")
      .bind(now, last_seq_seen, room_id, auth.sender_id)
      .run();
  } else {
    await env.DB
      .prepare("UPDATE room_members SET last_heartbeat_at = ? WHERE room_id = ? AND member_id = ?")
      .bind(now, room_id, auth.sender_id)
      .run();
  }

  return json(req, 200, { ok: true, server_now: now });
}

// GET /rooms/{id}/presence
async function handlePresence(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "read");
  if (!member) return json(req, 403, { error: "not a room member" });

  const now = Date.now();
  const { results } = await env.DB
    .prepare("SELECT member_id, member_type, display_name, last_heartbeat_at, last_seq_seen FROM room_members WHERE room_id = ?")
    .bind(room_id)
    .all();

  // Status thresholds: <90s green, <5min yellow, else red.
  const ONLINE_MS = 90_000;
  const STALE_MS = 5 * 60_000;
  const presence = (results || []).map(r => {
    const age = r.last_heartbeat_at ? now - r.last_heartbeat_at : Infinity;
    const status = age < ONLINE_MS ? "online" : age < STALE_MS ? "stale" : "offline";
    return {
      member_id: r.member_id,
      member_type: r.member_type,
      display_name: r.display_name,
      last_heartbeat_at: r.last_heartbeat_at,
      last_seq_seen: r.last_seq_seen,
      status,
    };
  });

  return json(req, 200, { room_id, server_now: now, presence });
}

// POST /rooms/{id}/mark-read  (same as legacy but takes room_id from path)
async function handleRoomMarkRead(req, env, room_id) {
  const auth = await authAny(req, env);
  if (!auth) return json(req, 401, { error: "unauthorized" });
  const member = await requireRoomMember(env, room_id, auth.sender_id, "read");
  if (!member) return json(req, 403, { error: "not a room member" });

  let body;
  try { body = await req.json(); } catch { return json(req, 400, { error: "invalid json" }); }
  const mid = typeof body?.message_id === "string" ? body.message_id : "";
  if (!mid) return json(req, 400, { error: "message_id required" });

  // Verify message belongs to this room
  const row = await env.DB
    .prepare("SELECT audit_log, room_id FROM trio_messages WHERE id = ?")
    .bind(mid)
    .first();
  if (!row) return json(req, 404, { error: "not found" });
  if (row.room_id && row.room_id !== room_id) {
    return json(req, 403, { error: "message not in room" });
  }

  let log = [];
  try { log = JSON.parse(row.audit_log || "[]"); if (!Array.isArray(log)) log = []; } catch { log = []; }
  log.push({ reader: auth.sender_id, at: new Date().toISOString() });

  await env.DB
    .prepare("UPDATE trio_messages SET audit_log = ? WHERE id = ?")
    .bind(JSON.stringify(log), mid)
    .run();

  return json(req, 200, { ok: true });
}

// =========================================================================
// ROUTER
// =========================================================================

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: secHeaders(req) });
    }
    const url = new URL(req.url);
    const p = url.pathname;

    // Legacy routes (unchanged)
    if (req.method === "POST" && p === "/trio/message") return handlePost(req, env);
    if (req.method === "GET" && p === "/trio/messages") return handleGet(req, env);
    if (req.method === "POST" && p === "/trio/mark-read") return handleMarkRead(req, env);
    if (req.method === "POST" && p === "/trio/upload") return handleUpload(req, env);
    if (req.method === "GET" && p === "/trio/health") return json(req, 200, { ok: true });
    if (req.method === "GET" && p === "/health") return json(req, 200, { ok: true, version: "thread-b-phase1" });

    // /media/{key}  — key may contain slashes
    if (req.method === "GET" && p.startsWith("/media/")) {
      const key = decodeURIComponent(p.slice("/media/".length));
      return handleMedia(req, env, key);
    }

    // /rooms/ensure
    if (req.method === "POST" && p === "/rooms/ensure") return handleRoomsEnsure(req, env);

    // /rooms/{id}/...
    if (p.startsWith("/rooms/")) {
      // Strip prefix; first segment is room_id, rest is action (or empty for /rooms/{id})
      const rest = p.slice("/rooms/".length);
      const slash = rest.indexOf("/");
      const room_id = slash === -1 ? rest : rest.slice(0, slash);
      const tail = slash === -1 ? "" : rest.slice(slash + 1);
      if (!room_id) return json(req, 404, { error: "missing room id" });

      // /rooms/{id}
      if (tail === "") {
        if (req.method === "GET") return handleRoomGet(req, env, room_id);
        if (req.method === "PATCH") return handleRoomPatch(req, env, room_id);
        return json(req, 405, { error: "method not allowed" });
      }
      if (tail === "messages") {
        if (req.method === "POST") return handleRoomMessagePost(req, env, room_id);
        if (req.method === "GET") return handleRoomMessageGet(req, env, room_id);
        return json(req, 405, { error: "method not allowed" });
      }
      if (tail === "upload" && req.method === "POST") return handleRoomUpload(req, env, room_id);
      if (tail === "heartbeat" && req.method === "POST") return handleHeartbeat(req, env, room_id);
      if (tail === "presence" && req.method === "GET") return handlePresence(req, env, room_id);
      if (tail === "mark-read" && req.method === "POST") return handleRoomMarkRead(req, env, room_id);
      if (tail === "rotate-ai-token" && req.method === "POST") return handleRotateAiToken(req, env, room_id);
      return json(req, 404, { error: "not found" });
    }

    return json(req, 404, { error: "not found" });
  },
};
