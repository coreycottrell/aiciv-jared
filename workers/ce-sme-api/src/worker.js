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

// ─── Auth ────────────────────────────────────────────────

async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return btoa(String.fromCharCode(...new Uint8Array(hash)));
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
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { email, password, company_name, industry } = body;
  if (!email || !password) return err(400, "Email and password required");
  if (password.length < 6) return err(400, "Password must be at least 6 characters");

  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email.toLowerCase().trim()).first();
  if (existing) return err(409, "Email already registered");

  const passwordHash = await hashPassword(password);
  const result = await env.DB.prepare(
    "INSERT INTO users (email, password_hash, company_name, industry) VALUES (?, ?, ?, ?)"
  ).bind(email.toLowerCase().trim(), passwordHash, company_name || "", industry || "").run();

  const userId = result.meta.last_row_id;
  const token = generateToken();
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(); // 30 days

  await env.DB.prepare(
    "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)"
  ).bind(userId, token, expiresAt).run();

  await logActivity(env, userId, "register", "user", userId);

  return json({ ok: true, token, user: { id: userId, email: email.toLowerCase().trim(), company_name: company_name || "", industry: industry || "" } }, { status: 201 });
}

async function handleLogin(request, env) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { email, password } = body;
  if (!email || !password) return err(400, "Email and password required");

  const user = await env.DB.prepare(
    "SELECT id, email, password_hash, company_name, industry FROM users WHERE email = ?"
  ).bind(email.toLowerCase().trim()).first();
  if (!user) return err(401, "Invalid credentials");

  const passwordHash = await hashPassword(password);
  if (passwordHash !== user.password_hash) return err(401, "Invalid credentials");

  const token = generateToken();
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

  await env.DB.prepare(
    "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)"
  ).bind(user.id, token, expiresAt).run();

  return json({ ok: true, token, user: { id: user.id, email: user.email, company_name: user.company_name, industry: user.industry } });
}

// ─── Proposals Routes ────────────────────────────────────

async function handleCreateProposal(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { client_name, project_type, scope, pricing, brief, items } = body;
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
    "SELECT * FROM proposal_items WHERE proposal_id = ?"
  ).bind(id).all();

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
  const proposal = await env.DB.prepare(
    "SELECT * FROM proposals WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!proposal) return err(404, "Proposal not found");

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) return err(503, "AI generation not configured");

  const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(sess.user_id).first();

  const systemPrompt = `You are a professional proposal writer for small and medium businesses.
The user's company is "${user.company_name || "a professional services firm"}" in the "${user.industry || "general"}" industry.
Generate a complete, professional business proposal based on the brief provided.
Include: Executive Summary, Scope of Work, Timeline, Deliverables, Pricing Breakdown, Terms & Conditions.
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
      const errBody = await resp.text();
      return err(502, `AI generation failed: ${resp.status}`);
    }

    const result = await resp.json();
    const aiDraft = result.content?.[0]?.text || "";

    await env.DB.prepare(
      "UPDATE proposals SET ai_draft = ?, updated_at = datetime('now') WHERE id = ? AND user_id = ?"
    ).bind(aiDraft, id, sess.user_id).run();

    await logActivity(env, sess.user_id, "ai_generate", "proposal", id);
    return json({ ok: true, ai_draft: aiDraft });
  } catch (e) {
    return err(502, `AI generation error: ${e.message}`);
  }
}

async function handleProposalPdf(request, env, sess, id) {
  // PDF generation placeholder — in production this would use a PDF library or external service
  const proposal = await env.DB.prepare(
    "SELECT * FROM proposals WHERE id = ? AND user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!proposal) return err(404, "Proposal not found");

  const items = await env.DB.prepare(
    "SELECT * FROM proposal_items WHERE proposal_id = ?"
  ).bind(id).all();

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
    "SELECT * FROM milestones WHERE project_id = ? ORDER BY due_date ASC"
  ).bind(id).all();

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
    "SELECT * FROM milestones WHERE project_id = ? ORDER BY due_date ASC"
  ).bind(id).all();

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
  const candidate = await env.DB.prepare(
    "SELECT c.*, j.title as job_title, j.description as job_description, j.requirements as job_requirements FROM candidates c JOIN jobs j ON c.job_id = j.id WHERE c.id = ? AND c.user_id = ?"
  ).bind(id, sess.user_id).first();
  if (!candidate) return err(404, "Candidate not found");

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) return err(503, "AI screening not configured");

  const systemPrompt = `You are an HR screening assistant. Evaluate the candidate against the job requirements.
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

    if (!resp.ok) return err(502, `AI screening failed: ${resp.status}`);

    const result = await resp.json();
    const screening = result.content?.[0]?.text || "";

    await env.DB.prepare(
      "UPDATE candidates SET ai_screening = ? WHERE id = ? AND user_id = ?"
    ).bind(screening, id, sess.user_id).run();

    await logActivity(env, sess.user_id, "ai_screen", "candidate", id);
    return json({ ok: true, ai_screening: screening });
  } catch (e) {
    return err(502, `AI screening error: ${e.message}`);
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

// ─── Reviews Routes ─────────────────────────────────────

async function handleCreateReview(request, env, sess) {
  let body;
  try { body = await request.json(); } catch { return err(400, "Invalid JSON"); }

  const { employee_name, position, review_period, rating, strengths, improvements, goals, generate_ai } = body;
  if (!employee_name) return err(400, "Employee name required");

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
          system: "You are an HR professional writing a performance review. Be constructive, specific, and balanced. Format in clean markdown.",
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

// ─── Dashboard ───────────────────────────────────────────

async function handleDashboard(env, sess) {
  const [proposalStats, projectStats, taskStats, revenueStats] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN status IN ('draft','sent') THEN 1 ELSE 0 END) as active FROM proposals WHERE user_id = ?").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active FROM projects WHERE user_id = ?").bind(sess.user_id).first(),
    env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending, SUM(CASE WHEN due_date <= date('now','+7 days') AND status = 'pending' THEN 1 ELSE 0 END) as due_soon FROM tasks WHERE user_id = ?").bind(sess.user_id).first(),
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
      response = err(500, `Internal error: ${e.message}`);
    }

    return applyCors(response, origin, env);
  },
};
