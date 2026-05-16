/**
 * meetings-api Worker — PureBrain meetings backend
 *
 * Separated from admin-api so meeting deploys NEVER affect
 * admin dashboard or social content.
 *
 * D1 binding: env.DB = purebrain-social (shared, read/write for meeting tables)
 *
 * Endpoints:
 *   GET    /health
 *   POST   /api/login                      — login (returns session token)
 *   GET    /api/meetings/assignments       — list meeting assignments (public)
 *   PUT    /api/meetings/assignments       — save meeting assignments (auth required)
 *   POST   /api/meetings/form-response     — submit form response (public)
 *   GET    /api/meetings/responses/:id     — list form responses for meeting (public)
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
    "access-control-allow-methods": "GET, POST, PUT, OPTIONS",
    "access-control-allow-headers": "authorization, content-type, x-admin-token",
    "vary": "origin",
  };
}

function nowIso() { return new Date().toISOString(); }

// ---------- Auth ----------

async function getSession(request, env) {
  // 1. Check X-Admin-Token header (set by portal proxy)
  const adminToken = request.headers.get("x-admin-token") || "";
  if (env.ADMIN_TOKEN && adminToken && adminToken === env.ADMIN_TOKEN) {
    return {
      user_id: "admin",
      email: "admin@system",
      role: "leader",
      display_name: "Admin",
    };
  }

  // 2. Check Bearer token / session cookie against D1 sessions table
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return null;

  // System API key passthrough
  if (env.ROUTER_API_KEY && token === env.ROUTER_API_KEY) {
    return {
      user_id: "system",
      email: "router@system",
      role: "system",
      display_name: "System",
    };
  }

  try {
    const row = await env.DB.prepare(
      "SELECT s.user_id, s.expires_at, u.email, u.role, u.name FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?"
    ).bind(token).first();
    if (!row) return null;
    if (new Date(row.expires_at) < new Date()) return null;
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

// ---------- Login Handler ----------

async function handleLogin(request, env) {
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const email = (body.email || "").trim().toLowerCase();
  const password = body.password || "";
  if (!email || !password) return err(400, "email and password required");

  const user = await env.DB.prepare(
    "SELECT id, email, name, role, password_hash FROM users WHERE LOWER(email) = ?"
  ).bind(email).first();
  if (!user) return err(401, "invalid credentials");

  const [saltHex, hashHex] = (user.password_hash || "").split(":");
  if (!saltHex || !hashHex) return err(401, "invalid credentials");

  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]);
  const salt = new Uint8Array(saltHex.match(/.{2}/g).map(b => parseInt(b, 16)));
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
    keyMaterial, 256
  );
  const rehash = Array.from(new Uint8Array(bits)).map(b => b.toString(16).padStart(2, "0")).join("");
  if (rehash !== hashHex) return err(401, "invalid credentials");

  const token = crypto.randomUUID() + crypto.randomUUID().slice(0, 8);
  const expiresAt = new Date(Date.now() + 12 * 3600 * 1000).toISOString();
  await env.DB.prepare(
    "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)"
  ).bind(token, user.id, expiresAt).run();

  await env.DB.prepare(
    "UPDATE users SET last_login_at = ? WHERE id = ?"
  ).bind(nowIso(), user.id).run();

  return json({
    token,
    user: { id: user.id, email: user.email, name: user.name, role: user.role }
  });
}

// ---------- Meeting Handlers ----------

async function handleGetMeetingAssignments(request, env) {
  const { results: assignments } = await env.DB.prepare(
    "SELECT * FROM meeting_assignments"
  ).all();
  const { results: custom } = await env.DB.prepare(
    "SELECT * FROM custom_meetings ORDER BY created_at"
  ).all();
  return json({ assignments: assignments || [], custom_meetings: custom || [] });
}

async function handleSaveMeetingAssignments(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const assignments = body.assignments || [];
  const now = nowIso();

  for (const a of assignments) {
    if (!a.meeting_id) continue;
    await env.DB.prepare(
      `INSERT INTO meeting_assignments (meeting_id, required_ids, optional_ids, zoom_link, zoom_meeting_id, updated_by, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(meeting_id) DO UPDATE SET
         required_ids = excluded.required_ids,
         optional_ids = excluded.optional_ids,
         zoom_link = COALESCE(excluded.zoom_link, meeting_assignments.zoom_link),
         zoom_meeting_id = COALESCE(excluded.zoom_meeting_id, meeting_assignments.zoom_meeting_id),
         updated_by = excluded.updated_by,
         updated_at = excluded.updated_at`
    ).bind(
      a.meeting_id,
      JSON.stringify(a.required || []),
      JSON.stringify(a.optional || []),
      a.zoom_link || null,
      a.zoom_meeting_id || null,
      sess.user_id,
      now
    ).run();
  }

  const customMeetings = body.custom_meetings || [];
  for (const cm of customMeetings) {
    if (!cm.id || !cm.name) continue;
    await env.DB.prepare(
      `INSERT INTO custom_meetings (id, name, full_name, color, schedule, duration, led_by, hook, description, domain, format, facilitator, created_by, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
         name = excluded.name, full_name = excluded.full_name, color = excluded.color,
         schedule = excluded.schedule, duration = excluded.duration, led_by = excluded.led_by,
         hook = excluded.hook, description = excluded.description, domain = excluded.domain,
         format = excluded.format, facilitator = excluded.facilitator, updated_at = excluded.updated_at`
    ).bind(
      cm.id, cm.name, cm.full_name || cm.name, cm.color || '#3b82f6',
      cm.schedule || '', cm.duration || '', cm.led_by || '',
      cm.hook || '', cm.description || '', cm.domain || 'Custom',
      JSON.stringify(cm.format || []), cm.facilitator || '',
      sess.user_id, now
    ).run();
  }

  return json({ saved: assignments.length, custom_saved: customMeetings.length });
}

async function handleSubmitFormResponse(request, env) {
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const meeting_id = body.meeting_id;
  const name = body.name || body.respondent_name;
  const email = body.email || body.respondent_email;
  const responses = body.responses;
  const respondent_type = body.respondent_type;
  if (!meeting_id || !name || !responses) return err(400, "meeting_id, name, and responses required");
  const id = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT INTO meeting_form_responses (id, meeting_id, respondent_name, respondent_email, respondent_type, responses) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(id, meeting_id, name, email || null, respondent_type || "human", JSON.stringify(responses)).run();
  return json({ id, status: "submitted" }, { status: 201 });
}

async function handleGetFormResponses(request, env) {
  const url = new URL(request.url);
  const meetingId = url.pathname.split("/").pop();
  const { results } = await env.DB.prepare(
    "SELECT * FROM meeting_form_responses WHERE meeting_id = ? ORDER BY submitted_at DESC"
  ).bind(meetingId).all();
  const parsed = (results || []).map(r => ({
    ...r,
    responses: (() => { try { return JSON.parse(r.responses); } catch { return r.responses; } })()
  }));
  return json({ responses: parsed, count: parsed.length });
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
        response = json({ ok: true, service: "meetings-api", ts: nowIso() });

      // --- Login (both paths for flexibility) ---
      } else if (method === "POST" && (path === "/api/login" || path === "/api/meetings/login")) {
        response = await handleLogin(request, env);

      // --- Meeting endpoints ---
      } else if (method === "GET" && path === "/api/meetings/assignments") {
        response = await handleGetMeetingAssignments(request, env);

      } else if (method === "PUT" && path === "/api/meetings/assignments") {
        response = await handleSaveMeetingAssignments(request, env);

      } else if (method === "POST" && path === "/api/meetings/form-response") {
        response = await handleSubmitFormResponse(request, env);

      } else if (method === "GET" && path.startsWith("/api/meetings/responses/")) {
        response = await handleGetFormResponses(request, env);

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
