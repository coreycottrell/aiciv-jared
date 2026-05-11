/**
 * ce-sme-api Worker — PureBrain SME Operations Platform
 *
 * CF Worker + D1 backend for ce.purebrain.ai
 * Modules: Proposals (AI-generated), Operations (SOPs/Tasks/Vendors/Compliance), Project Control
 *
 * D1 binding: env.DB = ce-sme-db
 * Secrets: ANTHROPIC_API_KEY (for AI proposal generation)
 *
 * Auth: email/password with session tokens stored in D1
 * Multi-tenant: all queries scoped by user_id
 */

// ─── Helpers ─────────────────────────────────────────────

function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      "x-frame-options": "DENY",
      "strict-transport-security": "max-age=31536000; includeSubDomains",
      "referrer-policy": "strict-origin-when-cross-origin",
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

function corsHeaders(origin, env) {
  const allowed = (env.CORS_ORIGINS || "https://ce.purebrain.ai").split(",").map(s => s.trim());
  const allowOrigin = allowed.includes(origin) ? origin : allowed[0];
  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "access-control-allow-headers": "authorization, content-type",
    "vary": "origin",
  };
}

function applyCors(response, origin, env) {
  const cors = corsHeaders(origin, env);
  const newHeaders = new Headers(response.headers);
  for (const [k, v] of Object.entries(cors)) newHeaders.set(k, v);
  return new Response(response.body, { status: response.status, headers: newHeaders });
}

// ─── Input Validation ───────────────────────────────────

function validateLength(value, maxLen, fieldName) {
  if (typeof value === "string" && value.length > maxLen) {
    return `${fieldName} exceeds maximum length of ${maxLen} characters`;
  }
  return null;
}

function validateEmail(email) {
  if (!email || typeof email !== "string") return "Email is required";
  if (email.length > 254) return "Email exceeds maximum length";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Invalid email format";
  return null;
}

function validateTextInputs(body, rules) {
  for (const [field, maxLen] of Object.entries(rules)) {
    if (body[field] !== undefined && body[field] !== null) {
      const error = validateLength(String(body[field]), maxLen, field);
      if (error) return error;
    }
  }
  return null;
}

// ─── Status Enums ───────────────────────────────────────

const STATUS_ENUMS = {
  proposals: ['draft', 'sent', 'won', 'lost'],
  tasks: ['pending', 'in_progress', 'completed'],
  projects: ['planning', 'active', 'on_hold', 'completed', 'cancelled'],
  invoices: ['draft', 'sent', 'paid', 'overdue'],
  jobs: ['open', 'closed', 'filled'],
  candidates: ['applied', 'screening', 'interview', 'offer', 'hired', 'rejected'],
  content_calendar: ['idea', 'draft', 'review', 'scheduled', 'published'],
  onboarding: ['pending', 'in_progress', 'completed'],
};

function validateStatus(entityType, status) {
  const allowed = STATUS_ENUMS[entityType];
  if (!allowed) return null;
  if (!allowed.includes(status)) return `Invalid status '${status}'. Allowed: ${allowed.join(', ')}`;
  return null;
}

// ─── Rate Limiting ──────────────────────────────────────

async function checkRateLimit(env, key, maxRequests, windowSeconds) {
  try {
    const now = new Date();
    const row = await env.DB.prepare(
      "SELECT count, window_start FROM rate_limits WHERE key = ?"
    ).bind(key).first();

    if (row) {
      const windowStart = new Date(row.window_start);
      const elapsed = (now - windowStart) / 1000;
      if (elapsed < windowSeconds) {
        if (row.count >= maxRequests) {
          return false; // rate limited
        }
        await env.DB.prepare(
          "UPDATE rate_limits SET count = count + 1 WHERE key = ?"
        ).bind(key).run();
        return true;
      }
      // Window expired, reset
      await env.DB.prepare(
        "UPDATE rate_limits SET count = 1, window_start = datetime('now') WHERE key = ?"
      ).bind(key).run();
      return true;
    }

    // No record, create one
    await env.DB.prepare(
      "INSERT INTO rate_limits (key, count, window_start) VALUES (?, 1, datetime('now'))"
    ).bind(key).run();
    return true;
  } catch {
    // If rate limit check fails, allow the request (fail open for availability)
    return true;
  }
}

function getClientIP(request) {
  return request.headers.get("cf-connecting-ip") || request.headers.get("x-forwarded-for") || "unknown";
}

// ─── Auth ────────────────────────────────────────────────

async function hashPassword(password, existingSalt) {
  const salt = existingSalt || crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]
  );
  const hash = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
    keyMaterial, 256
  );
  const saltB64 = btoa(String.fromCharCode(...salt));
  const hashB64 = btoa(String.fromCharCode(...new Uint8Array(hash)));
  return saltB64 + ':' + hashB64;
}

async function verifyPassword(password, storedHash) {
  const [saltB64, hashB64] = storedHash.split(':');
  if (!saltB64 || !hashB64) {
    // Legacy unsalted hash -- verify with old method, then caller should re-hash
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hash = await crypto.subtle.digest("SHA-256", data);
    const legacyHash = btoa(String.fromCharCode(...new Uint8Array(hash)));
    return { valid: legacyHash === storedHash, legacy: true };
  }
  const salt = new Uint8Array([...atob(saltB64)].map(c => c.charCodeAt(0)));
  const newHash = await hashPassword(password, salt);
  // Constant-time comparison
  const a = new TextEncoder().encode(newHash);
  const b = new TextEncoder().encode(saltB64 + ':' + hashB64);
  if (a.length !== b.length) return { valid: false, legacy: false };
  let result = 0;
  for (let i = 0; i < a.length; i++) result |= a[i] ^ b[i];
  return { valid: result === 0, legacy: false };
}

async function getSession(request, env) {
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/ce_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return null;

  try {
    const row = await env.DB.prepare(
      "SELECT s.user_id, s.expires_at, u.email, u.company_name, u.industry FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?"
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
  if (!sess) return { error: err(401, "Unauthorized"), sess: null };
  return { error: null, sess };
}

async function logActivity(env, userId, action, entityType, entityId) {
  try {
    await env.DB.prepare(
      "INSERT INTO activity_log (user_id, action, entity_type, entity_id) VALUES (?, ?, ?, ?)"
    ).bind(userId, action, entityType, entityId).run();
  } catch { /* non-critical */ }
}

// ─── Auth Routes ─────────────────────────────────────────

async function handleRegister(request, env) {
  // Rate limit: 3 registrations per IP per hour
  const ip = getClientIP(request);
  if (!await checkRateLimit(env, `reg:${ip}`, 3, 3600)) {
    return err(429, "Too many registration attempts. Try again later.");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { email, password, company_name, industry } = body;
  if (!email || !password) return err(400, "Email and password required");
  if (password.length < 6) return err(400, "Password must be at least 6 characters");

  // Input validation
  const emailErr = validateEmail(email);
  if (emailErr) return err(400, emailErr);
  const lengthErr = validateTextInputs(body, { company_name: 200, industry: 200 });
  if (lengthErr) return err(400, lengthErr);

  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email.toLowerCase().trim()).first();
  if (existing) return err(409, "Email already registered");

  const passwordHash = await hashPassword(password);
  const result = await env.DB.prepare(
    "INSERT INTO users (email, password_hash, company_name, industry) VALUES (?, ?, ?, ?)"
  ).bind(email.toLowerCase().trim(), passwordHash, company_name || "", industry || "").run();

  const userId = result.meta.last_row_id;
  const token = generateToken();
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours

  await env.DB.prepare(
    "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)"
  ).bind(userId, token, expiresAt).run();

  await logActivity(env, userId, "register", "user", userId);

  return json({ ok: true, token, user: { id: userId, email: email.toLowerCase().trim(), company_name: company_name || "", industry: industry || "" } }, { status: 201 });
}

async function handleLogin(request, env) {
  // Rate limit: 5 login attempts per IP per minute
  const ip = getClientIP(request);
  if (!await checkRateLimit(env, `login:${ip}`, 5, 60)) {
    return err(429, "Too many login attempts. Try again later.");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { email, password } = body;
  if (!email || !password) return err(400, "Email and password required");

  const user = await env.DB.prepare(
    "SELECT id, email, password_hash, company_name, industry FROM users WHERE email = ?"
  ).bind(email.toLowerCase().trim()).first();
  if (!user) return err(401, "Invalid credentials");

  const { valid, legacy } = await verifyPassword(password, user.password_hash);
  if (!valid) return err(401, "Invalid credentials");

  // Upgrade legacy SHA-256 hash to PBKDF2 on successful login
  if (legacy) {
    const newHash = await hashPassword(password);
    await env.DB.prepare("UPDATE users SET password_hash = ? WHERE id = ?").bind(newHash, user.id).run();
  }

  const token = generateToken();
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours

  await env.DB.prepare(
    "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)"
  ).bind(user.id, token, expiresAt).run();

  return json({ ok: true, token, user: { id: user.id, email: user.email, company_name: user.company_name, industry: user.industry } });
}

async function handleLogout(request, env) {
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/ce_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return err(401, "Unauthorized");

  await env.DB.prepare("DELETE FROM sessions WHERE token = ?").bind(token).run();
  return json({ ok: true, message: "Logged out" });
}

// ─── Proposals Routes ────────────────────────────────────

async function handleCreateProposal(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { client_name, project_type, scope, pricing, brief, items } = body;

  // Input validation
  const lengthErr = validateTextInputs(body, { client_name: 200, project_type: 200, scope: 50000, brief: 50000 });
  if (lengthErr) return err(400, lengthErr);

  const result = await env.DB.prepare(
    "INSERT INTO proposals (user_id, client_name, project_type, scope, pricing, brief) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, client_name || "", project_type || "", scope || "", pricing || 0, brief || "").run();

  const proposalId = result.meta.last_row_id;

  if (items && Array.isArray(items)) {
    for (const item of items) {
      const amount = (item.quantity || 1) * (item.rate || 0);
      await env.DB.prepare(
        "INSERT INTO proposal_items (proposal_id, description, quantity, rate, amount) VALUES (?, ?, ?, ?, ?)"
      ).bind(proposalId, item.description || "", item.quantity || 1, item.rate || 0, amount).run();
    }
  }

  await logActivity(env, sess.user_id, "create", "proposal", proposalId);
  return json({ ok: true, id: proposalId }, { status: 201 });
}

async function handleListProposals(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM proposals WHERE user_id = ? ORDER BY created_at DESC"
  ).bind(sess.user_id).all();
  return json({ proposals: rows.results });
}

async function handleGetProposal(env, sess, id) {
  const proposal = await env.DB.prepare(
    "SELECT * FROM proposals WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!proposal) return err(404, "Proposal not found");

  const items = await env.DB.prepare(
    "SELECT pi.* FROM proposal_items pi JOIN proposals p ON pi.proposal_id = p.id WHERE pi.proposal_id = ? AND p.user_id = ?"
  ).bind(id, sess.user_id).all();

  return json({ ...proposal, items: items.results });
}

async function handleUpdateProposal(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM proposals WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Proposal not found");

  const fields = [];
  const values = [];
  if (body.status !== undefined) {
    const statusErr = validateStatus('proposals', body.status);
    if (statusErr) return err(400, statusErr);
  }

  for (const key of ["client_name", "project_type", "scope", "pricing", "status", "ai_draft", "pdf_url", "brief"]) {
    if (body[key] !== undefined) {
      fields.push(`${key} = ?`);
      values.push(body[key]);
    }
  }
  if (fields.length === 0) return err(400, "No fields to update");

  fields.push("updated_at = datetime('now')");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE proposals SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "proposal", id);
  return json({ ok: true });
}

async function handleGenerateProposal(request, env, sess, id) {
  // Rate limit: 20 AI generations per user per hour
  if (!await checkRateLimit(env, `ai:${sess.user_id}`, 20, 3600)) {
    return err(429, "AI generation rate limit exceeded. Try again later.");
  }

  const proposal = await env.DB.prepare(
    "SELECT * FROM proposals WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!proposal) return err(404, "Proposal not found");

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) return err(503, "AI generation not configured");

  const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(sess.user_id).first();

  const systemPrompt = `${TIE_SYSTEM_CONTEXT}

You are a professional proposal writer for small and medium businesses.
The user's company is "${user.company_name || "a professional services firm"}" in the "${user.industry || "general"}" industry.
Generate a complete, professional business proposal based on the brief provided.
Include: Executive Summary, Scope of Work, Timeline, Deliverables, Pricing Breakdown (in CAD), Terms & Conditions.
Format in clean markdown. Be specific, professional, and persuasive.`;

  const userPrompt = `Create a proposal for:
Client: ${proposal.client_name}
Project Type: ${proposal.project_type}
Brief: ${proposal.brief || proposal.scope || "General project proposal"}
Budget Range: $${proposal.pricing || "TBD"}`;

  try {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      }),
    });

    if (!resp.ok) {
      console.error(`AI generation failed: ${resp.status}`);
      return err(502, "AI generation failed");
    }

    const result = await resp.json();
    const aiDraft = result.content?.[0]?.text || "";

    await env.DB.prepare(
      "UPDATE proposals SET ai_draft = ?, updated_at = datetime('now') WHERE id = ? AND user_id = ?"
    ).bind(aiDraft, id, sess.user_id).run();

    await logActivity(env, sess.user_id, "ai_generate", "proposal", id);
    return json({ ok: true, ai_draft: aiDraft });
  } catch (e) {
    console.error("AI generation error:", e.message);
    return err(502, "AI generation failed");
  }
}

async function handleProposalPdf(request, env, sess, id) {
  // PDF generation placeholder — in production this would use a PDF library or external service
  const proposal = await env.DB.prepare(
    "SELECT * FROM proposals WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!proposal) return err(404, "Proposal not found");

  const items = await env.DB.prepare(
    "SELECT pi.* FROM proposal_items pi JOIN proposals p ON pi.proposal_id = p.id WHERE pi.proposal_id = ? AND p.user_id = ?"
  ).bind(id, sess.user_id).all();

  // Return structured data that the frontend can render as PDF via browser print
  return json({
    ok: true,
    pdf_data: {
      proposal,
      items: items.results,
      generated_at: new Date().toISOString(),
      note: "Use browser print (Ctrl+P) to save as PDF. Server-side PDF generation available in Phase 2.",
    },
  });
}

async function handleProposalStats(env, sess) {
  const stats = await env.DB.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as drafts,
      SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
      SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
      SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as lost,
      SUM(CASE WHEN status = 'won' THEN pricing ELSE 0 END) as won_revenue,
      SUM(CASE WHEN status IN ('draft','sent') THEN pricing ELSE 0 END) as pipeline_value
    FROM proposals WHERE user_id = ?
  `).bind(sess.user_id).first();
  return json({ stats });
}

// ─── SOPs Routes ─────────────────────────────────────────

async function handleCreateSop(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { title, content, category } = body;
  if (!title) return err(400, "Title required");

  // Input validation
  const lengthErr = validateTextInputs(body, { title: 200, content: 50000, category: 200 });
  if (lengthErr) return err(400, lengthErr);

  const result = await env.DB.prepare(
    "INSERT INTO sops (user_id, title, content, category) VALUES (?, ?, ?, ?)"
  ).bind(sess.user_id, title, content || "", category || "general").run();

  await logActivity(env, sess.user_id, "create", "sop", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListSops(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM sops WHERE user_id = ? ORDER BY updated_at DESC"
  ).bind(sess.user_id).all();
  return json({ sops: rows.results });
}

async function handleUpdateSop(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM sops WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "SOP not found");

  const fields = [];
  const values = [];
  for (const key of ["title", "content", "category"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  fields.push("updated_at = datetime('now')");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE sops SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "sop", id);
  return json({ ok: true });
}

// ─── Tasks Routes ────────────────────────────────────────

async function handleCreateTask(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { title, description, due_date, recurrence, priority } = body;
  if (!title) return err(400, "Title required");

  // Input validation
  const lengthErr = validateTextInputs(body, { title: 200, description: 50000 });
  if (lengthErr) return err(400, lengthErr);

  const result = await env.DB.prepare(
    "INSERT INTO tasks (user_id, title, description, due_date, recurrence, priority) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, title, description || "", due_date || "", recurrence || "none", priority || "medium").run();

  await logActivity(env, sess.user_id, "create", "task", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListTasks(env, sess, url) {
  const status = url.searchParams.get("status");
  let query = "SELECT * FROM tasks WHERE user_id = ?";
  const params = [sess.user_id];
  if (status) { query += " AND status = ?"; params.push(status); }
  query += " ORDER BY due_date ASC, priority DESC";

  const rows = await env.DB.prepare(query).bind(...params).all();
  return json({ tasks: rows.results });
}

async function handleUpdateTask(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM tasks WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Task not found");

  const fields = [];
  const values = [];
  if (body.status !== undefined) {
    const statusErr = validateStatus('tasks', body.status);
    if (statusErr) return err(400, statusErr);
  }

  for (const key of ["title", "description", "due_date", "recurrence", "status", "priority"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE tasks SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "task", id);
  return json({ ok: true });
}

// ─── Vendors Routes ──────────────────────────────────────

async function handleCreateVendor(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { name, contact_email, phone, contract_end, notes } = body;
  if (!name) return err(400, "Vendor name required");

  // Input validation
  const lengthErr = validateTextInputs(body, { name: 200, contact_email: 254, phone: 50, notes: 50000 });
  if (lengthErr) return err(400, lengthErr);
  if (contact_email) {
    const emailErr = validateEmail(contact_email);
    if (emailErr) return err(400, emailErr);
  }

  const result = await env.DB.prepare(
    "INSERT INTO vendors (user_id, name, contact_email, phone, contract_end, notes) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, name, contact_email || "", phone || "", contract_end || "", notes || "").run();

  await logActivity(env, sess.user_id, "create", "vendor", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListVendors(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM vendors WHERE user_id = ? ORDER BY name ASC"
  ).bind(sess.user_id).all();
  return json({ vendors: rows.results });
}

// ─── Compliance Routes ───────────────────────────────────

async function handleCreateCompliance(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { title, deadline, category, reminder_days } = body;
  if (!title) return err(400, "Title required");
  if (!deadline) return err(400, "Deadline required");

  // Input validation
  const lengthErr = validateTextInputs(body, { title: 200, category: 200 });
  if (lengthErr) return err(400, lengthErr);

  const result = await env.DB.prepare(
    "INSERT INTO compliance_items (user_id, title, deadline, category, status, reminder_days) VALUES (?, ?, ?, ?, 'active', ?)"
  ).bind(sess.user_id, title, deadline, category || "Regulatory", reminder_days || 30).run();

  await logActivity(env, sess.user_id, "create", "compliance", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListCompliance(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM compliance_items WHERE user_id = ? ORDER BY deadline ASC"
  ).bind(sess.user_id).all();
  return json({ compliance: rows.results });
}

// ─── Projects Routes ─────────────────────────────────────

async function handleCreateProject(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { name, client_name, proposal_id, budget, start_date, end_date } = body;
  if (!name) return err(400, "Project name required");

  // Input validation
  const lengthErr = validateTextInputs(body, { name: 200, client_name: 200 });
  if (lengthErr) return err(400, lengthErr);

  // Validate proposal_id belongs to user
  if (proposal_id) {
    const pCheck = await env.DB.prepare("SELECT id FROM proposals WHERE id = ? AND user_id = ?").bind(proposal_id, sess.user_id).first();
    if (!pCheck) return err(403, "Proposal not found");
  }

  const result = await env.DB.prepare(
    "INSERT INTO projects (user_id, proposal_id, name, client_name, budget, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, proposal_id || null, name, client_name || "", budget || 0, start_date || "", end_date || "").run();

  await logActivity(env, sess.user_id, "create", "project", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListProjects(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC"
  ).bind(sess.user_id).all();
  return json({ projects: rows.results });
}

async function handleGetProject(env, sess, id) {
  const project = await env.DB.prepare(
    "SELECT * FROM projects WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!project) return err(404, "Project not found");

  const milestones = await env.DB.prepare(
    "SELECT m.* FROM milestones m JOIN projects p ON m.project_id = p.id WHERE m.project_id = ? AND p.user_id = ? ORDER BY m.due_date ASC"
  ).bind(id, sess.user_id).all();

  return json({ ...project, milestones: milestones.results });
}

async function handleCreateMilestone(request, env, sess, projectId) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const project = await env.DB.prepare(
    "SELECT id FROM projects WHERE id = ? AND user_id = ?"
  ).bind(projectId, sess.user_id).first();
  if (!project) return err(404, "Project not found");

  const { title, due_date, notes } = body;
  if (!title) return err(400, "Milestone title required");

  const result = await env.DB.prepare(
    "INSERT INTO milestones (project_id, title, due_date, notes) VALUES (?, ?, ?, ?)"
  ).bind(projectId, title, due_date || "", notes || "").run();

  await logActivity(env, sess.user_id, "create", "milestone", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleUpdateMilestone(request, env, sess, projectId, milestoneId) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const project = await env.DB.prepare(
    "SELECT id FROM projects WHERE id = ? AND user_id = ?"
  ).bind(projectId, sess.user_id).first();
  if (!project) return err(404, "Project not found");

  const fields = [];
  const values = [];
  for (const key of ["title", "due_date", "status", "notes"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  values.push(milestoneId, projectId);

  await env.DB.prepare(
    `UPDATE milestones SET ${fields.join(", ")} WHERE id = ? AND project_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "milestone", milestoneId);
  return json({ ok: true });
}

async function handleProjectBudget(env, sess, id) {
  const project = await env.DB.prepare(
    "SELECT id, name, budget, actual_spend FROM projects WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!project) return err(404, "Project not found");

  const variance = project.budget - project.actual_spend;
  const percentUsed = project.budget > 0 ? ((project.actual_spend / project.budget) * 100).toFixed(1) : 0;

  return json({
    project_id: project.id,
    name: project.name,
    budget: project.budget,
    actual_spend: project.actual_spend,
    variance,
    percent_used: parseFloat(percentUsed),
    status: variance < 0 ? "over_budget" : variance < project.budget * 0.1 ? "at_risk" : "on_track",
  });
}

async function handleProjectStatusUpdate(request, env, sess, id) {
  const project = await env.DB.prepare(
    "SELECT * FROM projects WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!project) return err(404, "Project not found");

  const milestones = await env.DB.prepare(
    "SELECT m.* FROM milestones m JOIN projects p ON m.project_id = p.id WHERE m.project_id = ? AND p.user_id = ? ORDER BY m.due_date ASC"
  ).bind(id, sess.user_id).all();

  const completed = milestones.results.filter(m => m.status === "completed").length;
  const total = milestones.results.length;
  const budgetUsed = project.budget > 0 ? ((project.actual_spend / project.budget) * 100).toFixed(0) : 0;

  const statusEmail = `Subject: Project Update — ${project.name}

Hi ${project.client_name || "Team"},

Here is your project status update for ${project.name}:

Progress: ${completed}/${total} milestones completed (${total > 0 ? ((completed/total)*100).toFixed(0) : 0}%)
Budget: $${project.actual_spend.toLocaleString()} of $${project.budget.toLocaleString()} used (${budgetUsed}%)
Status: ${project.status}

Upcoming milestones:
${milestones.results.filter(m => m.status !== "completed").map(m => `  - ${m.title} (due: ${m.due_date || "TBD"})`).join("\n") || "  None remaining"}

Please let me know if you have any questions.

Best regards`;

  return json({ ok: true, status_email: statusEmail });
}

// ─── Invoices Routes ────────────────────────────────────

async function handleCreateInvoice(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { client_name, project_id, milestone_id, amount, due_date, notes } = body;
  if (!client_name || !amount) return err(400, "Client name and amount required");

  const result = await env.DB.prepare(
    "INSERT INTO invoices (user_id, project_id, milestone_id, client_name, amount, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, project_id || null, milestone_id || null, client_name, amount, due_date || null, notes || "").run();

  await logActivity(env, sess.user_id, "create", "invoice", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListInvoices(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM invoices WHERE user_id = ? ORDER BY created_at DESC"
  ).bind(sess.user_id).all();
  return json({ invoices: rows.results });
}

async function handleUpdateInvoice(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM invoices WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Invoice not found");

  const fields = [];
  const values = [];
  if (body.status !== undefined) {
    const statusErr = validateStatus('invoices', body.status);
    if (statusErr) return err(400, statusErr);
  }

  for (const key of ["client_name", "project_id", "milestone_id", "amount", "status", "due_date", "paid_date", "notes"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE invoices SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "invoice", id);
  return json({ ok: true });
}

async function handleSendInvoice(request, env, sess, id) {
  const existing = await env.DB.prepare(
    "SELECT id, status FROM invoices WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Invoice not found");

  await env.DB.prepare(
    "UPDATE invoices SET status = 'sent' WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).run();

  await logActivity(env, sess.user_id, "send", "invoice", id);
  return json({ ok: true, message: "Invoice marked as sent" });
}

// ─── Expenses Routes ────────────────────────────────────

async function handleCreateExpense(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { category, amount, description, receipt_url, expense_date } = body;
  if (!category || !amount) return err(400, "Category and amount required");

  const result = await env.DB.prepare(
    "INSERT INTO expenses (user_id, category, amount, description, receipt_url, expense_date) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, category, amount, description || "", receipt_url || "", expense_date || "").run();

  await logActivity(env, sess.user_id, "create", "expense", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListExpenses(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM expenses WHERE user_id = ? ORDER BY expense_date DESC, created_at DESC"
  ).bind(sess.user_id).all();
  return json({ expenses: rows.results });
}

// ─── Cash Flow Route ────────────────────────────────────

async function handleCashFlow(env, sess) {
  const now = new Date();
  const monthStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;

  const [owed, incoming, overdue, paidThisMonth, expensesThisMonth] = await Promise.all([
    env.DB.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM invoices WHERE user_id = ? AND status IN ('draft','sent')").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM invoices WHERE user_id = ? AND status = 'sent'").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM invoices WHERE user_id = ? AND status IN ('sent','overdue') AND due_date < date('now')").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM invoices WHERE user_id = ? AND status = 'paid' AND paid_date >= ?").bind(sess.user_id, monthStart).first(),
    env.DB.prepare("SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ? AND expense_date >= ?").bind(sess.user_id, monthStart).first(),
  ]);

  return json({
    total_owed: owed.total,
    incoming: incoming.total,
    overdue: overdue.total,
    paid_this_month: paidThisMonth.total,
    expenses_this_month: expensesThisMonth.total,
    net_this_month: paidThisMonth.total - expensesThisMonth.total,
  });
}

// ─── Jobs Routes ────────────────────────────────────────

async function handleCreateJob(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { title, description, requirements, salary_range } = body;
  if (!title) return err(400, "Job title required");

  // Input validation
  const lengthErr = validateTextInputs(body, { title: 200, description: 50000, requirements: 50000, salary_range: 200 });
  if (lengthErr) return err(400, lengthErr);

  const result = await env.DB.prepare(
    "INSERT INTO jobs (user_id, title, description, requirements, salary_range) VALUES (?, ?, ?, ?, ?)"
  ).bind(sess.user_id, title, description || "", requirements || "", salary_range || "").run();

  await logActivity(env, sess.user_id, "create", "job", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListJobs(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT j.*, (SELECT COUNT(*) FROM candidates c WHERE c.job_id = j.id) as candidate_count FROM jobs j WHERE j.user_id = ? ORDER BY j.created_at DESC"
  ).bind(sess.user_id).all();
  return json({ jobs: rows.results });
}

async function handleUpdateJob(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM jobs WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Job not found");

  const fields = [];
  const values = [];
  if (body.status !== undefined) {
    const statusErr = validateStatus('jobs', body.status);
    if (statusErr) return err(400, statusErr);
  }

  for (const key of ["title", "description", "requirements", "salary_range", "status"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE jobs SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "job", id);
  return json({ ok: true });
}

// ─── Candidates Routes ──────────────────────────────────

async function handleCreateCandidate(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { job_id, name, email, phone, resume_text, notes } = body;
  if (!job_id || !name) return err(400, "Job ID and candidate name required");

  // Input validation
  const lengthErr = validateTextInputs(body, { name: 200, email: 254, phone: 50, resume_text: 50000, notes: 50000 });
  if (lengthErr) return err(400, lengthErr);
  if (email) {
    const emailErr = validateEmail(email);
    if (emailErr) return err(400, emailErr);
  }

  // Verify job belongs to user
  const job = await env.DB.prepare("SELECT id FROM jobs WHERE id = ? AND user_id = ?").bind(job_id, sess.user_id).first();
  if (!job) return err(404, "Job not found");

  const result = await env.DB.prepare(
    "INSERT INTO candidates (user_id, job_id, name, email, phone, resume_text, notes) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, job_id, name, email || "", phone || "", resume_text || "", notes || "").run();

  await logActivity(env, sess.user_id, "create", "candidate", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListCandidates(env, sess, url) {
  const jobId = url.searchParams.get("job_id");
  let query = "SELECT * FROM candidates WHERE user_id = ?";
  const params = [sess.user_id];
  if (jobId) { query += " AND job_id = ?"; params.push(jobId); }
  query += " ORDER BY created_at DESC";

  const rows = await env.DB.prepare(query).bind(...params).all();
  return json({ candidates: rows.results });
}

async function handleUpdateCandidate(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM candidates WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Candidate not found");

  const fields = [];
  const values = [];
  if (body.status !== undefined) {
    const statusErr = validateStatus('candidates', body.status);
    if (statusErr) return err(400, statusErr);
  }

  for (const key of ["name", "email", "phone", "resume_text", "status", "rating", "notes", "ai_screening"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE candidates SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "candidate", id);
  return json({ ok: true });
}

async function handleScreenCandidate(request, env, sess, id) {
  // Rate limit: 20 AI screenings per user per hour
  if (!await checkRateLimit(env, `ai:${sess.user_id}`, 20, 3600)) {
    return err(429, "AI screening rate limit exceeded. Try again later.");
  }

  const candidate = await env.DB.prepare(
    "SELECT c.*, j.title as job_title, j.description as job_description, j.requirements as job_requirements FROM candidates c JOIN jobs j ON c.job_id = j.id WHERE c.id = ? AND c.user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!candidate) return err(404, "Candidate not found");

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) return err(503, "AI screening not configured");

  const systemPrompt = `${TIE_SYSTEM_CONTEXT}

You are an HR screening assistant for a Canadian business. Evaluate the candidate against the job requirements.
Consider Canadian employment standards and labour law context where relevant.
Provide:
1. Overall Match Score (1-10)
2. Key Strengths (matching requirements)
3. Gaps/Concerns
4. Recommended Interview Questions (3-5)
5. Hiring Recommendation (Strong Yes / Yes / Maybe / No)
Be objective, specific, and concise.`;

  const userPrompt = `Job: ${candidate.job_title}
Description: ${candidate.job_description || 'N/A'}
Requirements: ${candidate.job_requirements || 'N/A'}

Candidate: ${candidate.name}
Resume/Background: ${candidate.resume_text || 'No resume provided'}
Notes: ${candidate.notes || 'None'}`;

  try {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 2048,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      }),
    });

    if (!resp.ok) {
      console.error(`AI screening failed: ${resp.status}`);
      return err(502, "AI screening failed");
    }

    const result = await resp.json();
    const screening = result.content?.[0]?.text || "";

    await env.DB.prepare(
      "UPDATE candidates SET ai_screening = ? WHERE id = ? AND user_id = ?"
    ).bind(screening, id, sess.user_id).run();

    await logActivity(env, sess.user_id, "ai_screen", "candidate", id);
    return json({ ok: true, ai_screening: screening });
  } catch (e) {
    console.error("AI screening error:", e.message);
    return err(502, "AI screening failed");
  }
}

// ─── Onboarding Routes ──────────────────────────────────

async function handleCreateOnboarding(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { candidate_id, employee_name, position, start_date, checklist } = body;
  if (!employee_name) return err(400, "Employee name required");

  const checklistStr = checklist || JSON.stringify([
    { task: "Set up email and accounts", done: false },
    { task: "Equipment provisioning", done: false },
    { task: "Welcome meeting with team", done: false },
    { task: "Review company policies", done: false },
    { task: "Complete tax/payroll forms", done: false },
    { task: "First week training plan", done: false },
  ]);

  const result = await env.DB.prepare(
    "INSERT INTO onboarding (user_id, candidate_id, employee_name, position, start_date, checklist) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, candidate_id || null, employee_name, position || "", start_date || "", checklistStr).run();

  await logActivity(env, sess.user_id, "create", "onboarding", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleGetOnboarding(env, sess, id) {
  const row = await env.DB.prepare(
    "SELECT * FROM onboarding WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!row) return err(404, "Onboarding record not found");

  let checklist = [];
  try { checklist = JSON.parse(row.checklist || "[]"); } catch { checklist = []; }

  return json({ ...row, checklist_parsed: checklist });
}

async function handleListOnboarding(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM onboarding WHERE user_id = ? ORDER BY created_at DESC"
  ).bind(sess.user_id).all();
  return json({ onboarding: rows.results });
}

// ─── Reviews Routes ─────────────────────────────────────

async function handleCreateReview(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { employee_name, position, review_period, rating, strengths, improvements, goals, generate_ai } = body;
  if (!employee_name) return err(400, "Employee name required");

  // Input validation
  const lengthErr = validateTextInputs(body, { employee_name: 200, position: 200, review_period: 200, strengths: 50000, improvements: 50000, goals: 50000 });
  if (lengthErr) return err(400, lengthErr);

  // Rate limit AI if requested
  if (generate_ai) {
    if (!await checkRateLimit(env, `ai:${sess.user_id}`, 20, 3600)) {
      return err(429, "AI generation rate limit exceeded. Try again later.");
    }
  }

  let aiDraft = "";
  if (generate_ai && env.ANTHROPIC_API_KEY) {
    try {
      const resp = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 2048,
          system: `${TIE_SYSTEM_CONTEXT}\n\nYou are an HR professional writing a performance review for a Canadian business. Be constructive, specific, and balanced. Reference Canadian employment standards where appropriate. Format in clean markdown.`,
          messages: [{ role: "user", content: `Write a performance review for:
Employee: ${employee_name}
Position: ${position || 'N/A'}
Review Period: ${review_period || 'Current period'}
Rating: ${rating || 'N/A'}/5
Strengths noted: ${strengths || 'N/A'}
Areas for improvement: ${improvements || 'N/A'}
Goals: ${goals || 'N/A'}` }],
        }),
      });
      if (resp.ok) {
        const result = await resp.json();
        aiDraft = result.content?.[0]?.text || "";
      }
    } catch { /* non-critical */ }
  }

  const result = await env.DB.prepare(
    "INSERT INTO reviews (user_id, employee_name, position, review_period, rating, strengths, improvements, goals, ai_draft) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, employee_name, position || "", review_period || "", rating || null, strengths || "", improvements || "", goals || "", aiDraft).run();

  await logActivity(env, sess.user_id, "create", "review", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id, ai_draft: aiDraft }, { status: 201 });
}

async function handleListReviews(env, sess) {
  const rows = await env.DB.prepare(
    "SELECT * FROM reviews WHERE user_id = ? ORDER BY created_at DESC"
  ).bind(sess.user_id).all();
  return json({ reviews: rows.results });
}

// ─── Canadian TIE System Prompt ─────────────────────────

const TIE_SYSTEM_CONTEXT = `You are TIE (The Intelligence Engine), an AI assistant for Canadian small and medium businesses.
Context: The user operates a business in Canada. Apply Canadian business norms including:
- Canadian tax references (GST/HST, CRA, T4, T2, provincial tax rates)
- Canadian employment standards (ESA, provincial labour codes)
- Canadian regulatory environment (PIPEDA for privacy, provincial regulations)
- Canadian spelling conventions (colour, honour, licence, centre)
- Canadian currency (CAD $) unless specified otherwise
- Canadian market context (BDC funding, IRAP, SR&ED tax credits)`;

// ─── Content Calendar Routes ────────────────────────────

async function handleCreateContent(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { type, title, topic, audience, brand_voice, scheduled_date, channel } = body;
  if (!title) return err(400, "Title required");

  // Input validation
  const lengthErr = validateTextInputs(body, { type: 200, title: 200, topic: 50000, audience: 200, brand_voice: 200, channel: 200 });
  if (lengthErr) return err(400, lengthErr);

  const result = await env.DB.prepare(
    "INSERT INTO content_calendar (user_id, type, title, topic, audience, brand_voice, scheduled_date, channel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(sess.user_id, type || "blog", title, topic || "", audience || "", brand_voice || "", scheduled_date || "", channel || "").run();

  await logActivity(env, sess.user_id, "create", "content", result.meta.last_row_id);
  return json({ ok: true, id: result.meta.last_row_id }, { status: 201 });
}

async function handleListContent(env, sess, url) {
  const month = url.searchParams.get("month"); // format: YYYY-MM
  const type = url.searchParams.get("type");
  let query = "SELECT * FROM content_calendar WHERE user_id = ?";
  const params = [sess.user_id];

  if (month) {
    query += " AND scheduled_date LIKE ?";
    params.push(month + "%");
  }
  if (type) {
    query += " AND type = ?";
    params.push(type);
  }
  query += " ORDER BY scheduled_date ASC, created_at DESC";

  const rows = await env.DB.prepare(query).bind(...params).all();
  return json({ content: rows.results });
}

async function handleGetContent(env, sess, id) {
  const row = await env.DB.prepare(
    "SELECT * FROM content_calendar WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!row) return err(404, "Content entry not found");
  return json(row);
}

async function handleUpdateContent(request, env, sess, id) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const existing = await env.DB.prepare(
    "SELECT id FROM content_calendar WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Content entry not found");

  const fields = [];
  const values = [];
  if (body.status !== undefined) {
    const statusErr = validateStatus('content_calendar', body.status);
    if (statusErr) return err(400, statusErr);
  }

  for (const key of ["type", "title", "topic", "audience", "brand_voice", "ai_draft", "status", "scheduled_date", "published_date", "channel"]) {
    if (body[key] !== undefined) { fields.push(`${key} = ?`); values.push(body[key]); }
  }
  if (fields.length === 0) return err(400, "No fields to update");
  values.push(id, sess.user_id);

  await env.DB.prepare(
    `UPDATE content_calendar SET ${fields.join(", ")} WHERE id = ? AND user_id = ?`
  ).bind(...values).run();

  await logActivity(env, sess.user_id, "update", "content", id);
  return json({ ok: true });
}

async function handleGenerateContent(request, env, sess) {
  // Rate limit: 20 AI generations per user per hour
  if (!await checkRateLimit(env, `ai:${sess.user_id}`, 20, 3600)) {
    return err(429, "AI generation rate limit exceeded. Try again later.");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { type, topic, brand_voice, audience } = body;
  if (!topic) return err(400, "Topic required");

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) return err(503, "AI generation not configured");

  const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(sess.user_id).first();

  const systemPrompt = `${TIE_SYSTEM_CONTEXT}

You are a content creation specialist. The user's company is "${user.company_name || "a Canadian business"}" in the "${user.industry || "general"}" industry.
Generate high-quality ${type || "blog"} content based on the topic provided.
${brand_voice ? `Brand voice: ${brand_voice}` : "Use a professional, approachable tone."}
${audience ? `Target audience: ${audience}` : ""}

For blog posts: Include title, introduction, 3-5 sections with subheadings, and a conclusion with CTA.
For social media: Keep it concise, engaging, with relevant hashtags.
For email: Include subject line, preview text, body with clear CTA.
For newsletter: Include headline, 2-3 featured stories/tips, and sign-off.
Format in clean markdown.`;

  const userPrompt = `Create ${type || "blog"} content about: ${topic}`;

  try {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      }),
    });

    if (!resp.ok) {
      console.error(`AI content generation failed: ${resp.status}`);
      return err(502, "AI generation failed");
    }

    const result = await resp.json();
    const aiDraft = result.content?.[0]?.text || "";

    await logActivity(env, sess.user_id, "ai_generate", "content", 0);
    return json({ ok: true, ai_draft: aiDraft });
  } catch (e) {
    console.error("AI content generation error:", e.message);
    return err(502, "AI generation failed");
  }
}

async function handlePublishContent(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { id } = body;
  if (!id) return err(400, "Content ID required");

  const existing = await env.DB.prepare(
    "SELECT id FROM content_calendar WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Content entry not found");

  const publishedDate = new Date().toISOString().split("T")[0];
  await env.DB.prepare(
    "UPDATE content_calendar SET status = 'published', published_date = ? WHERE id = ? AND user_id = ?"
  ).bind(publishedDate, id, sess.user_id).run();

  await logActivity(env, sess.user_id, "publish", "content", id);
  return json({ ok: true, message: "Content marked as published" });
}

async function handleContentStats(env, sess) {
  const now = new Date();
  const monthStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;

  const stats = await env.DB.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status = 'published' AND published_date LIKE ? THEN 1 ELSE 0 END) as published_this_month,
      SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
      SUM(CASE WHEN status IN ('idea','draft') THEN 1 ELSE 0 END) as drafts_pending,
      SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as in_review
    FROM content_calendar WHERE user_id = ?
  `).bind(monthStart + "%", sess.user_id).first();

  return json({ stats });
}

// ─── Delete Handlers ────────────────────────────────────

async function handleDelete(env, sess, table, id) {
  const existing = await env.DB.prepare(
    `SELECT id FROM ${table} WHERE id = ? AND user_id = ?`
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Not found");

  await env.DB.prepare(
    `DELETE FROM ${table} WHERE id = ? AND user_id = ?`
  ).bind(id, sess.user_id).run();

  await logActivity(env, sess.user_id, "delete", table, id);
  return json({ ok: true, deleted: id });
}

async function handleDeleteJob(env, sess, id) {
  const existing = await env.DB.prepare(
    "SELECT id FROM jobs WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Not found");

  // Delete associated candidates first
  await env.DB.prepare(
    "DELETE FROM candidates WHERE job_id = ? AND user_id = ?"
  ).bind(id, sess.user_id).run();

  await env.DB.prepare(
    "DELETE FROM jobs WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).run();

  await logActivity(env, sess.user_id, "delete", "jobs", id);
  return json({ ok: true, deleted: id });
}

async function handleDeleteContentCalendar(env, sess, id) {
  const existing = await env.DB.prepare(
    "SELECT id FROM content_calendar WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!existing) return err(404, "Not found");

  await env.DB.prepare(
    "DELETE FROM content_calendar WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).run();

  await logActivity(env, sess.user_id, "delete", "content_calendar", id);
  return json({ ok: true, deleted: id });
}

// ─── Demo Seed ──────────────────────────────────────────

async function handleDemoSeed(env, sess) {
  const uid = sess.user_id;
  const now = new Date();
  const today = now.toISOString().split('T')[0];
  const inDays = (d) => {
    const dt = new Date(now);
    dt.setDate(dt.getDate() + d);
    return dt.toISOString().split('T')[0];
  };

  // 3 proposals
  await env.DB.prepare(
    "INSERT INTO proposals (user_id, client_name, project_type, scope, pricing, status, brief, ai_draft) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Maple Ridge Construction", "Consulting", "Complete IT infrastructure review and recommendations for new office build-out. Includes network architecture, security assessment, and vendor evaluation.", 12500, "won", "IT infrastructure consulting for new office construction", "# IT Infrastructure Proposal\n\n## Executive Summary\nWe propose a comprehensive IT infrastructure review for Maple Ridge Construction's new office build-out...\n\n## Scope of Work\n- Network architecture design\n- Security assessment\n- Vendor evaluation and selection\n- Implementation timeline\n\n## Timeline\n6 weeks from project start\n\n## Investment\n$12,500 CAD + HST").run();

  await env.DB.prepare(
    "INSERT INTO proposals (user_id, client_name, project_type, scope, pricing, status, brief) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Northern Lights Dental", "Marketing", "Digital marketing strategy including website redesign, SEO audit, and social media content plan for Q3-Q4 2026.", 8000, "sent", "Full digital marketing overhaul for dental practice").run();

  await env.DB.prepare(
    "INSERT INTO proposals (user_id, client_name, project_type, scope, pricing, status, brief) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Ottawa Valley Brewing Co.", "Development", "E-commerce platform development with inventory management, online ordering, and delivery zone mapping.", 22000, "draft", "Custom e-commerce platform for craft brewery").run();

  // 2 projects (1 from won proposal, 1 standalone)
  const proposalRow = await env.DB.prepare(
    "SELECT id FROM proposals WHERE user_id = ? AND client_name = 'Maple Ridge Construction'"
  ).bind(uid).first();

  await env.DB.prepare(
    "INSERT INTO projects (user_id, proposal_id, name, client_name, budget, actual_spend, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, proposalRow?.id || null, "Maple Ridge IT Build-Out", "Maple Ridge Construction", 12500, 4200, inDays(-14), inDays(28), "active").run();

  const proj1 = await env.DB.prepare("SELECT id FROM projects WHERE user_id = ? AND name = 'Maple Ridge IT Build-Out'").bind(uid).first();

  await env.DB.prepare(
    "INSERT INTO projects (user_id, name, client_name, budget, actual_spend, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Office Automation Upgrade", "Internal", 5000, 1800, inDays(-7), inDays(45), "active").run();

  // Milestones for project 1
  if (proj1) {
    await env.DB.prepare(
      "INSERT INTO milestones (project_id, title, due_date, status, notes) VALUES (?, ?, ?, ?, ?)"
    ).bind(proj1.id, "Network Assessment Complete", inDays(-7), "completed", "Site survey and current infrastructure audit done").run();

    await env.DB.prepare(
      "INSERT INTO milestones (project_id, title, due_date, status, notes) VALUES (?, ?, ?, ?, ?)"
    ).bind(proj1.id, "Security Review", inDays(7), "in_progress", "Penetration testing and vulnerability scan").run();

    await env.DB.prepare(
      "INSERT INTO milestones (project_id, title, due_date, status, notes) VALUES (?, ?, ?, ?, ?)"
    ).bind(proj1.id, "Vendor Selection", inDays(21), "pending", "Evaluate and select hardware/software vendors").run();

    await env.DB.prepare(
      "INSERT INTO milestones (project_id, title, due_date, status, notes) VALUES (?, ?, ?, ?, ?)"
    ).bind(proj1.id, "Final Report & Handoff", inDays(28), "pending", "Deliver final documentation and recommendations").run();
  }

  // 5 tasks
  await env.DB.prepare(
    "INSERT INTO tasks (user_id, title, description, due_date, priority, status, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Follow up with Northern Lights Dental", "Check on proposal status, schedule call if needed", inDays(2), "high", "pending", "none").run();

  await env.DB.prepare(
    "INSERT INTO tasks (user_id, title, description, due_date, priority, status, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Review monthly financials", "Pull P&L, check AR/AP, update cash flow forecast", inDays(5), "medium", "pending", "monthly").run();

  await env.DB.prepare(
    "INSERT INTO tasks (user_id, title, description, due_date, priority, status, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Update company website", "Add new case studies and client testimonials", inDays(10), "low", "pending", "none").run();

  await env.DB.prepare(
    "INSERT INTO tasks (user_id, title, description, due_date, priority, status, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Submit GST/HST filing", "Quarterly GST/HST return due to CRA", inDays(-3), "high", "pending", "quarterly").run();

  await env.DB.prepare(
    "INSERT INTO tasks (user_id, title, description, due_date, priority, status, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Team standup prep", "Prepare agenda for weekly team sync", inDays(1), "medium", "in_progress", "weekly").run();

  // 2 SOPs
  await env.DB.prepare(
    "INSERT INTO sops (user_id, title, content, category) VALUES (?, ?, ?, ?)"
  ).bind(uid, "Office Opening & Closing Procedure", "## Daily Opening\n1. Disarm security system (code: see manager)\n2. Turn on lights and HVAC\n3. Check phone messages and email\n4. Review daily calendar for meetings\n5. Unlock front entrance at 8:30 AM\n\n## Daily Closing\n1. Lock front entrance\n2. Shut down shared workstations\n3. Turn off lights (leave emergency lighting)\n4. Arm security system\n5. Lock deadbolt on exit", "operations").run();

  await env.DB.prepare(
    "INSERT INTO sops (user_id, title, content, category) VALUES (?, ?, ?, ?)"
  ).bind(uid, "New Client Onboarding Checklist", "## Before First Meeting\n- [ ] Send welcome email with company overview\n- [ ] Create client folder in file system\n- [ ] Set up project in management tool\n\n## First Meeting\n- [ ] Review scope of work together\n- [ ] Confirm billing terms and payment schedule\n- [ ] Establish communication preferences\n- [ ] Introduce key team members\n\n## After Meeting\n- [ ] Send meeting notes within 24 hours\n- [ ] Create initial project timeline\n- [ ] Set up recurring check-in meetings\n- [ ] Add to newsletter/update distribution list", "customer-service").run();

  // 2 vendors
  await env.DB.prepare(
    "INSERT INTO vendors (user_id, name, contact_email, phone, contract_end, notes) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Bennett & Associates CPA", "sarah@bennettcpa.ca", "613-555-0142", inDays(180), "Annual retainer for bookkeeping and tax prep. Renewal in Q4.").run();

  await env.DB.prepare(
    "INSERT INTO vendors (user_id, name, contact_email, phone, contract_end, notes) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Staples Business Advantage", "orders@staplesba.ca", "1-800-668-4200", inDays(90), "Office supplies and equipment. Volume discount agreement.").run();

  // 3 compliance items
  await env.DB.prepare(
    "INSERT INTO compliance_items (user_id, title, deadline, category, status, reminder_days) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Business Licence Renewal", inDays(45), "Regulatory", "active", 30).run();

  await env.DB.prepare(
    "INSERT INTO compliance_items (user_id, title, deadline, category, status, reminder_days) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Commercial General Liability Insurance", inDays(120), "Insurance", "active", 60).run();

  await env.DB.prepare(
    "INSERT INTO compliance_items (user_id, title, deadline, category, status, reminder_days) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "T2 Corporate Tax Filing", inDays(75), "Financial", "active", 45).run();

  // 2 invoices
  await env.DB.prepare(
    "INSERT INTO invoices (user_id, client_name, amount, due_date, status, paid_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Maple Ridge Construction", 6250, inDays(-5), "paid", inDays(-3), "First milestone payment - Network Assessment").run();

  await env.DB.prepare(
    "INSERT INTO invoices (user_id, client_name, amount, due_date, status, notes) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Maple Ridge Construction", 6250, inDays(14), "sent", "Second milestone payment - Security Review & Final Report").run();

  // 1 job posting + 2 candidates
  await env.DB.prepare(
    "INSERT INTO jobs (user_id, title, description, requirements, salary_range, status) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(uid, "Junior IT Consultant", "Join our growing team to help deliver IT consulting projects for SME clients across Eastern Ontario. Mix of on-site and remote work.", "- 1-3 years IT experience\n- CompTIA A+ or equivalent\n- Strong communication skills\n- Valid driver's licence\n- Experience with networking and security a plus", "$45,000 - $55,000", "open").run();

  const jobRow = await env.DB.prepare(
    "SELECT id FROM jobs WHERE user_id = ? AND title = 'Junior IT Consultant'"
  ).bind(uid).first();

  if (jobRow) {
    await env.DB.prepare(
      "INSERT INTO candidates (user_id, job_id, name, email, phone, resume_text, status, rating, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    ).bind(uid, jobRow.id, "Alex Chen", "alex.chen@email.com", "613-555-0198", "B.Sc. Computer Science, Carleton University 2024. 2 years helpdesk experience at local MSP. CompTIA A+ certified. Familiar with Cisco networking.", "screening", 4, "Strong technical background, good culture fit from phone screen").run();

    await env.DB.prepare(
      "INSERT INTO candidates (user_id, job_id, name, email, phone, resume_text, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    ).bind(uid, jobRow.id, "Priya Sharma", "priya.sharma@email.com", "343-555-0267", "Algonquin College IT diploma 2023. 1 year co-op at federal government IT department. Strong documentation skills.", "applied", "Just applied, needs initial review").run();
  }

  // 3 content calendar entries
  await env.DB.prepare(
    "INSERT INTO content_calendar (user_id, type, title, topic, audience, brand_voice, scheduled_date, channel, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "blog", "5 IT Security Mistakes Canadian SMEs Make", "Common security vulnerabilities in small businesses and how to fix them", "Small business owners, IT managers", "professional", inDays(7), "Website", "draft").run();

  await env.DB.prepare(
    "INSERT INTO content_calendar (user_id, type, title, topic, audience, brand_voice, scheduled_date, channel, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "social", "Client Success Story: Maple Ridge", "Highlight the IT infrastructure project win and early results", "LinkedIn connections, potential clients", "friendly", inDays(3), "LinkedIn", "scheduled").run();

  await env.DB.prepare(
    "INSERT INTO content_calendar (user_id, type, title, topic, audience, brand_voice, scheduled_date, channel, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(uid, "newsletter", "Q2 2026 Business Tech Roundup", "Quarterly newsletter with industry trends, tips, and company updates", "Email subscribers, existing clients", "conversational", inDays(14), "Email list", "idea").run();

  await logActivity(env, uid, "demo_seed", "system", 0);

  return json({
    ok: true,
    message: "Demo data seeded successfully",
    seeded: {
      proposals: 3, projects: 2, milestones: 4, tasks: 5,
      sops: 2, vendors: 2, compliance: 3, invoices: 2,
      jobs: 1, candidates: 2, content: 3,
    },
  });
}

// ─── Dashboard ───────────────────────────────────────────

async function handleDashboard(env, sess) {
  const [proposalStats, projectStats, taskStats, revenueStats] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN status IN ('draft','sent') THEN 1 ELSE 0 END) as active FROM proposals WHERE user_id = ?").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active FROM projects WHERE user_id = ?").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending, SUM(CASE WHEN due_date <= date('now','+7 days') AND status = 'pending' THEN 1 ELSE 0 END) as due_soon, SUM(CASE WHEN due_date < date('now') AND status = 'pending' THEN 1 ELSE 0 END) as overdue FROM tasks WHERE user_id = ?").bind(sess.user_id).first(),
    env.DB.prepare("SELECT SUM(CASE WHEN status = 'won' THEN pricing ELSE 0 END) as won_revenue, SUM(CASE WHEN status IN ('draft','sent') THEN pricing ELSE 0 END) as pipeline FROM proposals WHERE user_id = ?").bind(sess.user_id).first(),
  ]);

  const recentActivity = await env.DB.prepare(
    "SELECT * FROM activity_log WHERE user_id = ? ORDER BY created_at DESC LIMIT 10"
  ).bind(sess.user_id).all();

  return json({
    proposals: proposalStats,
    projects: projectStats,
    tasks: taskStats,
    revenue: revenueStats,
    recent_activity: recentActivity.results,
  });
}

// ─── Router ──────────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    const origin = request.headers.get("origin") || "";

    // CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin, env) });
    }

    let response;

    try {
      // Health
      if (path === "/health" && method === "GET") {
        response = json({ status: "ok", service: "ce-sme-api", timestamp: new Date().toISOString() });
      }

      // Auth (no session required)
      else if (path === "/api/auth/register" && method === "POST") {
        response = await handleRegister(request, env);
      }
      else if (path === "/api/auth/login" && method === "POST") {
        response = await handleLogin(request, env);
      }
      else if (path === "/api/auth/logout" && method === "POST") {
        response = await handleLogout(request, env);
      }

      // All routes below require auth
      else if (path.startsWith("/api/")) {
        const { error: authErr, sess } = await requireAuth(request, env);
        if (authErr) { response = authErr; }

        // Dashboard
        else if (path === "/api/dashboard" && method === "GET") {
          response = await handleDashboard(env, sess);
        }

        // Proposals
        else if (path === "/api/proposals/stats" && method === "GET") {
          response = await handleProposalStats(env, sess);
        }
        else if (path === "/api/proposals" && method === "POST") {
          response = await handleCreateProposal(request, env, sess);
        }
        else if (path === "/api/proposals" && method === "GET") {
          response = await handleListProposals(env, sess);
        }
        else if (/^\/api\/proposals\/(\d+)\/generate$/.test(path) && method === "POST") {
          const id = parseInt(path.match(/\/api\/proposals\/(\d+)\/generate/)[1]);
          response = await handleGenerateProposal(request, env, sess, id);
        }
        else if (/^\/api\/proposals\/(\d+)\/pdf$/.test(path) && method === "POST") {
          const id = parseInt(path.match(/\/api\/proposals\/(\d+)\/pdf/)[1]);
          response = await handleProposalPdf(request, env, sess, id);
        }
        else if (/^\/api\/proposals\/(\d+)$/.test(path) && method === "GET") {
          const id = parseInt(path.match(/\/api\/proposals\/(\d+)/)[1]);
          response = await handleGetProposal(env, sess, id);
        }
        else if (/^\/api\/proposals\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/proposals\/(\d+)/)[1]);
          response = await handleUpdateProposal(request, env, sess, id);
        }

        // SOPs
        else if (path === "/api/sops" && method === "POST") {
          response = await handleCreateSop(request, env, sess);
        }
        else if (path === "/api/sops" && method === "GET") {
          response = await handleListSops(env, sess);
        }
        else if (/^\/api\/sops\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/sops\/(\d+)/)[1]);
          response = await handleUpdateSop(request, env, sess, id);
        }

        // Tasks
        else if (path === "/api/tasks" && method === "POST") {
          response = await handleCreateTask(request, env, sess);
        }
        else if (path === "/api/tasks" && method === "GET") {
          response = await handleListTasks(env, sess, url);
        }
        else if (/^\/api\/tasks\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/tasks\/(\d+)/)[1]);
          response = await handleUpdateTask(request, env, sess, id);
        }

        // Vendors
        else if (path === "/api/vendors" && method === "POST") {
          response = await handleCreateVendor(request, env, sess);
        }
        else if (path === "/api/vendors" && method === "GET") {
          response = await handleListVendors(env, sess);
        }

        // Compliance
        else if (path === "/api/compliance" && method === "POST") {
          response = await handleCreateCompliance(request, env, sess);
        }
        else if (path === "/api/compliance" && method === "GET") {
          response = await handleListCompliance(env, sess);
        }

        // Invoices
        else if (path === "/api/invoices" && method === "POST") {
          response = await handleCreateInvoice(request, env, sess);
        }
        else if (path === "/api/invoices" && method === "GET") {
          response = await handleListInvoices(env, sess);
        }
        else if (/^\/api\/invoices\/(\d+)\/send$/.test(path) && method === "POST") {
          const id = parseInt(path.match(/\/api\/invoices\/(\d+)\/send/)[1]);
          response = await handleSendInvoice(request, env, sess, id);
        }
        else if (/^\/api\/invoices\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/invoices\/(\d+)/)[1]);
          response = await handleUpdateInvoice(request, env, sess, id);
        }

        // Expenses
        else if (path === "/api/expenses" && method === "POST") {
          response = await handleCreateExpense(request, env, sess);
        }
        else if (path === "/api/expenses" && method === "GET") {
          response = await handleListExpenses(env, sess);
        }

        // Cash Flow
        else if (path === "/api/cashflow" && method === "GET") {
          response = await handleCashFlow(env, sess);
        }

        // Jobs
        else if (path === "/api/jobs" && method === "POST") {
          response = await handleCreateJob(request, env, sess);
        }
        else if (path === "/api/jobs" && method === "GET") {
          response = await handleListJobs(env, sess);
        }
        else if (/^\/api\/jobs\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/jobs\/(\d+)/)[1]);
          response = await handleUpdateJob(request, env, sess, id);
        }

        // Candidates
        else if (path === "/api/candidates" && method === "POST") {
          response = await handleCreateCandidate(request, env, sess);
        }
        else if (path === "/api/candidates" && method === "GET") {
          response = await handleListCandidates(env, sess, url);
        }
        else if (/^\/api\/candidates\/(\d+)\/screen$/.test(path) && method === "POST") {
          const id = parseInt(path.match(/\/api\/candidates\/(\d+)\/screen/)[1]);
          response = await handleScreenCandidate(request, env, sess, id);
        }
        else if (/^\/api\/candidates\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/candidates\/(\d+)/)[1]);
          response = await handleUpdateCandidate(request, env, sess, id);
        }

        // Onboarding
        else if (path === "/api/onboarding" && method === "POST") {
          response = await handleCreateOnboarding(request, env, sess);
        }
        else if (path === "/api/onboarding" && method === "GET") {
          response = await handleListOnboarding(env, sess);
        }
        else if (/^\/api\/onboarding\/(\d+)$/.test(path) && method === "GET") {
          const id = parseInt(path.match(/\/api\/onboarding\/(\d+)/)[1]);
          response = await handleGetOnboarding(env, sess, id);
        }

        // Reviews
        else if (path === "/api/reviews" && method === "POST") {
          response = await handleCreateReview(request, env, sess);
        }
        else if (path === "/api/reviews" && method === "GET") {
          response = await handleListReviews(env, sess);
        }

        // Content Calendar
        else if (path === "/api/content/calendar" && method === "POST") {
          response = await handleCreateContent(request, env, sess);
        }
        else if (path === "/api/content/calendar" && method === "GET") {
          response = await handleListContent(env, sess, url);
        }
        else if (path === "/api/content/stats" && method === "GET") {
          response = await handleContentStats(env, sess);
        }
        else if (path === "/api/content/generate" && method === "POST") {
          response = await handleGenerateContent(request, env, sess);
        }
        else if (path === "/api/content/publish" && method === "POST") {
          response = await handlePublishContent(request, env, sess);
        }
        else if (/^\/api\/content\/calendar\/(\d+)$/.test(path) && method === "GET") {
          const id = parseInt(path.match(/\/api\/content\/calendar\/(\d+)/)[1]);
          response = await handleGetContent(env, sess, id);
        }
        else if (/^\/api\/content\/calendar\/(\d+)$/.test(path) && method === "PUT") {
          const id = parseInt(path.match(/\/api\/content\/calendar\/(\d+)/)[1]);
          response = await handleUpdateContent(request, env, sess, id);
        }

        // Demo Seed
        else if (path === "/api/demo/seed" && method === "POST") {
          response = await handleDemoSeed(env, sess);
        }

        // Delete endpoints
        else if (/^\/api\/proposals\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/proposals\/(\d+)/)[1]);
          response = await handleDelete(env, sess, "proposals", id);
        }
        else if (/^\/api\/tasks\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/tasks\/(\d+)/)[1]);
          response = await handleDelete(env, sess, "tasks", id);
        }
        else if (/^\/api\/sops\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/sops\/(\d+)/)[1]);
          response = await handleDelete(env, sess, "sops", id);
        }
        else if (/^\/api\/vendors\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/vendors\/(\d+)/)[1]);
          response = await handleDelete(env, sess, "vendors", id);
        }
        else if (/^\/api\/invoices\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/invoices\/(\d+)/)[1]);
          response = await handleDelete(env, sess, "invoices", id);
        }
        else if (/^\/api\/expenses\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/expenses\/(\d+)/)[1]);
          response = await handleDelete(env, sess, "expenses", id);
        }
        else if (/^\/api\/jobs\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/jobs\/(\d+)/)[1]);
          response = await handleDeleteJob(env, sess, id);
        }
        else if (/^\/api\/content\/calendar\/(\d+)$/.test(path) && method === "DELETE") {
          const id = parseInt(path.match(/\/api\/content\/calendar\/(\d+)/)[1]);
          response = await handleDeleteContentCalendar(env, sess, id);
        }

        // Projects
        else if (path === "/api/projects" && method === "POST") {
          response = await handleCreateProject(request, env, sess);
        }
        else if (path === "/api/projects" && method === "GET") {
          response = await handleListProjects(env, sess);
        }
        else if (/^\/api\/projects\/(\d+)\/milestones\/(\d+)$/.test(path) && method === "PUT") {
          const m = path.match(/\/api\/projects\/(\d+)\/milestones\/(\d+)/);
          response = await handleUpdateMilestone(request, env, sess, parseInt(m[1]), parseInt(m[2]));
        }
        else if (/^\/api\/projects\/(\d+)\/milestones$/.test(path) && method === "POST") {
          const id = parseInt(path.match(/\/api\/projects\/(\d+)\/milestones/)[1]);
          response = await handleCreateMilestone(request, env, sess, id);
        }
        else if (/^\/api\/projects\/(\d+)\/budget$/.test(path) && method === "GET") {
          const id = parseInt(path.match(/\/api\/projects\/(\d+)\/budget/)[1]);
          response = await handleProjectBudget(env, sess, id);
        }
        else if (/^\/api\/projects\/(\d+)\/status-update$/.test(path) && method === "POST") {
          const id = parseInt(path.match(/\/api\/projects\/(\d+)\/status-update/)[1]);
          response = await handleProjectStatusUpdate(request, env, sess, id);
        }
        else if (/^\/api\/projects\/(\d+)$/.test(path) && method === "GET") {
          const id = parseInt(path.match(/\/api\/projects\/(\d+)/)[1]);
          response = await handleGetProject(env, sess, id);
        }

        else {
          response = err(404, "Not found");
        }
      }
      else {
        response = err(404, "Not found");
      }
    } catch (e) {
      console.error("Internal error:", e.message);
      response = err(500, "Internal server error");
    }

    return applyCors(response, origin, env);
  },
};
