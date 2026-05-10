/**
 * admin-api Worker — PureBrain admin dashboard backend
 *
 * Separated from social-api so admin dashboard is independent of
 * social content deployments.
 *
 * D1 binding: env.DB = purebrain-social (shared, read/write for admin tables)
 *
 * Endpoints:
 *   GET    /health
 *   GET    /api/check-name                 — public: check AI name uniqueness
 *   GET    /api/admin/clients              — list all clients with stats
 *   POST   /api/admin/clients/update       — Save modal (leader only, MODAL_ALLOWLIST)
 *   PATCH  /api/admin/clients/by-email/:e  — update client by email (leader only)
 *   PATCH  /api/admin/clients/:id          — update client by ID (leader only)
 *   POST   /api/admin/invite               — create team invite (leader only)
 *   POST   /api/admin/invite/revoke        — revoke invite (leader only, hard delete)
 *   GET    /api/admin/invites              — list all invites
 *   DELETE /api/admin/invites/:id          — delete invite (leader only)
 *   GET    /api/admin/validate-token       — public: validate invite token
 *
 * Meeting endpoints moved to meetings-api Worker (2026-04-23).
 *
 * Auth: Bearer token (D1 sessions table) OR X-Admin-Token header
 */

// ---------- Helpers ----------

function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
    },
  });
}

function err(status, message) {
  return json({ error: message }, { status });
}

function generateToken() {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

// ---------- Mutation Allowlists ----------
// MODAL_ALLOWLIST = fields the admin Save modal may mutate (UI-driven, narrowed).
// Excludes payment-derived columns (payment_status, monthly_amount), referral_code,
// password_hash, total_paid, hidden, uuid, id, created_at — those are owned elsewhere.
const CLIENT_MODAL_ALLOWLIST = [
  "name", "goes_by", "email", "ai_name", "company",
  "tier", "status", "notes",
];
// INTERNAL_ALLOWLIST = broader set used by existing PATCH-by-id route (hide toggle etc).
const CLIENT_INTERNAL_ALLOWLIST = [
  "ai_name", "name", "company", "tier", "status", "payment_status",
  "monthly_amount", "goes_by", "notes", "hidden", "email", "role", "goal",
];

// Shared helper — interpolates ONLY allowlist KEYS into SET clause, never values.
// All values bound parameterized via prepare(...).bind(...).
async function updateClientFields(env, identifier, by, body, allowlist) {
  const updates = [];
  const params = [];
  for (const key of allowlist) {
    if (body[key] !== undefined) {
      updates.push(key + " = ?");
      params.push(body[key]);
    }
  }
  if (updates.length === 0) return err(400, "no valid fields");
  params.push(by === "email" ? String(identifier).toLowerCase() : identifier);
  const where = by === "email" ? "LOWER(email) = ?" : "id = ?";
  await env.DB.prepare(
    "UPDATE clients SET " + updates.join(", ") + " WHERE " + where
  ).bind(...params).run();
  return json({ status: "ok" });
}

// Shared helper — hard delete from team_invites.
// Constrained to admin-source rows (matches existing handleDeleteInvite invariant).
async function revokeInviteById(env, id) {
  await env.DB.prepare(
    "DELETE FROM team_invites WHERE id = ? AND (source = 'admin' OR source IS NULL)"
  ).bind(id).run();
  return json({ status: "ok" });
}

function corsHeaders(origin) {
  const allowed = [
    "https://purebrain.ai",
    "https://portal.purebrain.ai",
    "https://777.purebrain.ai",
    "https://social.purebrain.ai",
  ];
  const allowOrigin = allowed.includes(origin) ? origin : allowed[0];
  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "access-control-allow-headers": "authorization, content-type, x-admin-token",
    "vary": "origin",
  };
}

// ---------- Auth ----------

// Phase 5: validate sessions via clients-api Service Binding bridge.
// 60s in-memory cache absorbs load. Bridge 401 = authoritative invalid.
// Bridge 5xx / network error → falls back to direct D1 read for availability.
const SESSION_CACHE_TTL_MS = 60 * 1000;
const sessionCache = new Map();
function cacheGetSession(token) {
  const e = sessionCache.get(token);
  if (!e) return null;
  if (Date.now() > e.expires_at_ms) { sessionCache.delete(token); return null; }
  return e.sess;
}
function cachePutSession(token, sess) {
  if (sessionCache.size > 5000) sessionCache.clear();
  sessionCache.set(token, { sess, expires_at_ms: Date.now() + SESSION_CACHE_TTL_MS });
}

async function bridgeValidateSession(token, env) {
  if (!env.CLIENTS_API) return undefined;
  if (!env.INTERNAL_BINDING_SECRET) return undefined;
  try {
    const req = new Request("https://clients-api/internal/validate-session", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding": "clients-api",
        "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
      },
      body: JSON.stringify({ token }),
    });
    const resp = await env.CLIENTS_API.fetch(req);
    // Phase 5 policy: any non-success → fallback to local D1 (see social-api
    // matching comment). Tightens to authoritative in Phase 7c.
    if (!resp.ok) return undefined;
    const j = await resp.json();
    if (!j || j.valid !== true) return undefined;
    // admin-api session shape historically uses display_name; clients-api
    // returns `name`. Map to keep call sites unchanged.
    return {
      user_id: j.user_id,
      email: j.email,
      role: j.role,
      display_name: j.name,
      team_id: j.team_id,
      billing_tier: j.billing_tier,
      expires_at: j.expires_at,
    };
  } catch {
    return undefined;
  }
}

async function getSession(request, env) {
  // 1. Check X-Admin-Token header (set by portal proxy) — local check, never bridged
  const adminToken = request.headers.get("x-admin-token") || "";
  if (env.ADMIN_TOKEN && adminToken && adminToken === env.ADMIN_TOKEN) {
    return {
      user_id: "admin",
      email: "admin@system",
      role: "leader",
      display_name: "Admin",
    };
  }

  // 2. Check Bearer token / session cookie
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return null;

  // System API key passthrough — local check
  if (env.ROUTER_API_KEY && token === env.ROUTER_API_KEY) {
    return {
      user_id: "system",
      email: "router@system",
      role: "system",
      display_name: "System",
    };
  }

  // 60s cache
  const cached = cacheGetSession(token);
  if (cached) return cached;

  // Service Binding bridge call (primary path)
  const bridged = await bridgeValidateSession(token, env);
  if (bridged === null) return null;
  if (bridged && bridged.user_id) {
    cachePutSession(token, bridged);
    return bridged;
  }

  // Fallback: direct D1 read (preserves availability if bridge unavailable)
  try {
    const row = await env.DB.prepare(
      "SELECT s.user_id, s.expires_at, u.email, u.role, u.name AS display_name FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?"
    ).bind(token).first();
    if (!row) return null;
    if (new Date(row.expires_at) < new Date()) return null;
    cachePutSession(token, row);
    return row;
  } catch {
    return null;
  }
}

async function requireAuth(request, env) {
  const sess = await getSession(request, env);
  if (!sess) return { error: err(401, "unauthorized"), sess: null };
  return { error: null, sess };
}

// ---------- Route Handlers ----------

// PUBLIC — intentionally no auth (used by signup form to validate AI name uniqueness).
/**
 * GET /api/check-name?ai_name=X&human_name=Y
 * Public endpoint (no auth) — checks AI name uniqueness in clients table.
 * Returns: { ai_name_taken, exact_match, existing_count, suggested_suffix }
 */
async function handleCheckName(env, url) {
  const aiName = (url.searchParams.get("ai_name") || "").trim();
  if (!aiName) return json({ ai_name_taken: false, existing_count: 0 });

  const humanName = (url.searchParams.get("human_name") || "").trim();

  try {
    // Count how many clients already use this AI name (case-insensitive)
    const { results } = await env.DB.prepare(
      "SELECT ai_name, name FROM clients WHERE LOWER(ai_name) = LOWER(?)"
    ).bind(aiName).all();

    const existingCount = results ? results.length : 0;

    if (existingCount === 0) {
      return json({ ai_name_taken: false, existing_count: 0 });
    }

    // Check if exact match (same AI name + same human name)
    let exactMatch = false;
    if (humanName) {
      exactMatch = results.some(
        (r) => r.name && r.name.toLowerCase() === humanName.toLowerCase()
      );
    }

    // Suggest a suffix (find the highest existing number suffix)
    let maxSuffix = 1;
    for (const r of results) {
      const m = (r.ai_name || "").match(/(\d+)$/);
      if (m) {
        const num = parseInt(m[1], 10);
        if (num >= maxSuffix) maxSuffix = num + 1;
      }
    }
    const suggestedSuffix = maxSuffix > 1 ? maxSuffix : existingCount + 1;

    return json({
      ai_name_taken: true,
      exact_match: exactMatch,
      existing_count: existingCount,
      suggested_suffix: suggestedSuffix,
    });
  } catch (e) {
    // If clients table doesn't exist or query fails, assume name is available
    return json({ ai_name_taken: false, existing_count: 0 });
  }
}

async function handleGetClients(request, env, url) {
  const { error: authErr } = await requireAuth(request, env);
  if (authErr) return authErr;

  const showHidden = url.searchParams.get("show_hidden") === "1";
  const { results } = await env.DB.prepare(
    "SELECT * FROM clients ORDER BY last_active_at DESC"
  ).all();
  const visible = showHidden ? results : results.filter((r) => !r.hidden);
  const activeVisible = visible.filter(
    (r) => r.status === "active" && !r.hidden
  );
  const mrr = activeVisible.reduce(
    (s, r) => s + (Number(r.monthly_amount) || 0),
    0
  );
  const stats = {
    total: visible.length,
    active: activeVisible.length,
    onboarding: visible.filter((r) => r.status === "onboarding").length,
    churned: visible.filter(
      (r) => r.status === "churned" || r.status === "cancelled"
    ).length,
    total_revenue: visible.reduce(
      (s, r) => s + (Number(r.total_paid) || 0),
      0
    ),
    mrr,
    hidden_count: results.filter((r) => r.hidden).length,
  };
  return json({ clients: visible || [], stats });
}

async function handleUpdateClientByEmail(request, env, clientEmail) {
  const { error: authErr, sess } = await requireAuth(request, env);
  if (authErr) return authErr;
  if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");

  const body = await request.json();
  console.log(`[admin-action] role=${sess.role} user=${sess.user_id} action=update_client_by_email target=${clientEmail}`);
  return updateClientFields(env, clientEmail, "email", body, CLIENT_INTERNAL_ALLOWLIST);
}

async function handleUpdateClientById(request, env, clientId) {
  const { error: authErr, sess } = await requireAuth(request, env);
  if (authErr) return authErr;
  if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");

  const body = await request.json();
  console.log(`[admin-action] role=${sess.role} user=${sess.user_id} action=update_client_by_id target=${clientId}`);
  return updateClientFields(env, clientId, "id", body, CLIENT_INTERNAL_ALLOWLIST);
}

// POST /api/admin/clients/update — Save modal handler.
// Frontend posts {id, ...modal_fields}. Uses MODAL_ALLOWLIST (narrower than INTERNAL).
async function handleUpdateClient(request, env) {
  const { error: authErr, sess } = await requireAuth(request, env);
  if (authErr) return authErr;
  if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");

  const body = await request.json();
  const id = body.id;
  if (!id) return err(400, "id required");
  console.log(`[admin-action] role=${sess.role} user=${sess.user_id} action=update_client target=${id}`);
  return updateClientFields(env, id, "id", body, CLIENT_MODAL_ALLOWLIST);
}

async function handleCreateInvite(request, env) {
  const { error: authErr, sess } = await requireAuth(request, env);
  if (authErr) return authErr;
  if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");

  const body = await request.json();
  const email = (body.email || "").trim().toLowerCase();
  const name = (body.name || "").trim();
  const role = body.role || "member";
  if (!email) return err(400, "email required");

  const id = crypto.randomUUID();
  const token = generateToken();
  const now = new Date().toISOString();

  // Ensure token column exists (ALTER TABLE is idempotent-safe via try/catch)
  try {
    await env.DB.prepare("ALTER TABLE team_invites ADD COLUMN token TEXT").run();
  } catch { /* column already exists */ }
  try {
    await env.DB.prepare("ALTER TABLE team_invites ADD COLUMN name TEXT").run();
  } catch { /* column already exists */ }

  await env.DB.prepare(
    "INSERT INTO team_invites (id, email, name, role, token, invited_by, invited_at, source) VALUES (?, ?, ?, ?, ?, ?, ?, 'admin')"
  )
    .bind(id, email, name, role, token, sess.user_id, now)
    .run();

  const dashboard_url = `https://portal.purebrain.ai/admin/clients?admin_token=${token}`;
  return json({ status: "ok", id, email, name, role, token, dashboard_url });
}

async function handleGetInvites(request, env) {
  const { error: authErr } = await requireAuth(request, env);
  if (authErr) return authErr;

  try {
    const { results } = await env.DB.prepare(
      "SELECT id, email, name, role, token, invited_by, invited_at AS created_at, status FROM team_invites WHERE source = 'admin' OR source IS NULL ORDER BY invited_at DESC"
    ).all();
    return json({ invitees: results || [] });
  } catch {
    await env.DB.prepare(
      "CREATE TABLE IF NOT EXISTS team_invites (id TEXT PRIMARY KEY, email TEXT NOT NULL, name TEXT, role TEXT DEFAULT 'member', token TEXT, invited_by TEXT, invited_at TEXT, status TEXT DEFAULT 'pending', source TEXT DEFAULT 'admin')"
    ).run();
    return json({ invitees: [] });
  }
}

// PUBLIC — intentionally no auth (used by invite landing page to validate token before sign-in).
async function handleValidateToken(request, env, url) {
  const token = url.searchParams.get("token") || "";
  if (!token) return err(400, "token required");

  try {
    const row = await env.DB.prepare(
      "SELECT id, email, name, role FROM team_invites WHERE token = ?"
    ).bind(token).first();
    if (!row) return json({ valid: false });
    return json({ valid: true, email: row.email, name: row.name, role: row.role });
  } catch {
    return json({ valid: false });
  }
}

async function handleDeleteInvite(request, env, inviteId) {
  const { error: authErr, sess } = await requireAuth(request, env);
  if (authErr) return authErr;
  if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");

  console.log(`[admin-action] role=${sess.role} user=${sess.user_id} action=delete_invite target=${inviteId}`);
  return revokeInviteById(env, inviteId);
}

// POST /api/admin/invite/revoke — frontend revoke button (id-in-body shape).
// Hard delete: matches existing DELETE-by-id behavior. Token unrecoverable post-revoke.
async function handleRevokeInvite(request, env) {
  const { error: authErr, sess } = await requireAuth(request, env);
  if (authErr) return authErr;
  if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");

  const body = await request.json();
  const id = body.id;
  if (id === undefined || id === null || id === "") return err(400, "id required");
  console.log(`[admin-action] role=${sess.role} user=${sess.user_id} action=revoke_invite target=${id}`);
  return revokeInviteById(env, id);
}

// ---------- Main Export ----------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    const origin = request.headers.get("origin") || "";

    // CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    let response;
    try {
      // Health check
      if (path === "/health") {
        response = json({ status: "ok", service: "admin-api", ts: new Date().toISOString() });

      // --- Public: AI name uniqueness check (no auth required) ---
      } else if (method === "GET" && path === "/api/check-name") {
        response = await handleCheckName(env, url);

      // --- Client endpoints ---
      } else if (method === "GET" && path === "/api/admin/clients") {
        response = await handleGetClients(request, env, url);

      } else if (method === "POST" && path === "/api/admin/clients/update") {
        response = await handleUpdateClient(request, env);

      } else if (method === "PATCH" && path.startsWith("/api/admin/clients/by-email/")) {
        const clientEmail = decodeURIComponent(
          path.slice("/api/admin/clients/by-email/".length)
        );
        response = await handleUpdateClientByEmail(request, env, clientEmail);

      } else if (method === "PATCH" && path.startsWith("/api/admin/clients/")) {
        const clientId = path.slice("/api/admin/clients/".length);
        response = await handleUpdateClientById(request, env, clientId);

      // --- Invite endpoints ---
      } else if (method === "POST" && path === "/api/admin/invite") {
        response = await handleCreateInvite(request, env);

      } else if (method === "POST" && path === "/api/admin/invite/revoke") {
        response = await handleRevokeInvite(request, env);

      } else if (method === "GET" && path === "/api/admin/invites") {
        response = await handleGetInvites(request, env);

      } else if (method === "DELETE" && path.startsWith("/api/admin/invites/")) {
        const inviteId = path.slice("/api/admin/invites/".length);
        response = await handleDeleteInvite(request, env, inviteId);

      } else if (method === "GET" && path === "/api/admin/validate-token") {
        response = await handleValidateToken(request, env, url);

      } else {
        response = err(404, "not found");
      }
    } catch (e) {
      response = err(
        500,
        "internal: " + (e.message || String(e)).slice(0, 200)
      );
    }

    // Attach CORS to every response
    const headers = new Headers(response.headers);
    const cors = corsHeaders(origin);
    for (const [k, v] of Object.entries(cors)) headers.set(k, v);
    return new Response(response.body, { status: response.status, headers });
  },
};
