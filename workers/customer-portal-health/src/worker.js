/**
 * customer-portal-health Worker
 *
 * Spec: specs/customer-portal-recovery-2026-05-15.md
 * CTO review: specs/cto-review-4-specs-2026-05-15.md (verdict: AMEND)
 * Jared greenlight: 2026-05-15 22:40 UTC — Whitehurst canary, silent recovery + audit log.
 *
 * Three responsibilities:
 *   1. Cron (every 5 min) — list customers, probe recovery-agent /health per host,
 *      log every sample to customer_portal_recovery_log (action='health_check').
 *   2. POST /admin/restart — admin-auth-gated. Calls recovery-agent's Tunnel URL
 *      with HMAC(nonce+ts), then writes the outcome row to D1.
 *   3. GET  /admin/recovery-log?customer=X&hours=N — readout for ops.
 *
 * Recovery-agent endpoint shape (must match recovery_agent.py):
 *   POST /restart with headers x-nonce, x-timestamp, x-signature
 *   body: { container_name, reason, request_id }
 *
 * NOTE: this worker NEVER restarts customers in cron — only the admin button
 * triggers a restart in Phase 1. Cron is observation-only.
 */

const TS_WINDOW_SECONDS = 30;

/* ----------------------------- helpers --------------------------------- */

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

function err(status, message) {
  return json({ error: message }, status);
}

async function hmacHex(key, message) {
  const enc = new TextEncoder();
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(key),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sigBuf = await crypto.subtle.sign("HMAC", cryptoKey, enc.encode(message));
  return [...new Uint8Array(sigBuf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function randHex(bytes = 16) {
  const buf = new Uint8Array(bytes);
  crypto.getRandomValues(buf);
  return [...buf].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function adminAuthOk(req, env) {
  const auth = req.headers.get("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;
  return Boolean(env.ADMIN_TOKEN && token === env.ADMIN_TOKEN);
}

function parseTunnelMap(env) {
  try {
    return JSON.parse(env.RECOVERY_AGENT_TUNNEL_URL || "{}");
  } catch {
    return {};
  }
}

/* ------------------------- D1 helpers ---------------------------------- */

/**
 * Append a row to customer_portal_recovery_log. Action is one of
 * 'health_check' | 'restart' | 'inner_relaunch' | 'escalate'.
 */
async function logRecovery(env, row) {
  const stmt = env.DB.prepare(`
    INSERT INTO customer_portal_recovery_log
      (ts, customer_slug, hetzner_host, action,
       ai_alive_before, ai_alive_after,
       thread_count_before, thread_count_after,
       pid_count_before, pid_count_after,
       duration_ms, outcome, error_message,
       triggered_by, request_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    row.ts,
    row.customer_slug,
    row.hetzner_host,
    row.action,
    row.ai_alive_before == null ? null : (row.ai_alive_before ? 1 : 0),
    row.ai_alive_after == null ? null : (row.ai_alive_after ? 1 : 0),
    row.thread_count_before ?? null,
    row.thread_count_after ?? null,
    row.pid_count_before ?? null,
    row.pid_count_after ?? null,
    row.duration_ms ?? null,
    row.outcome ?? null,
    row.error_message ?? null,
    row.triggered_by ?? null,
    row.request_id ?? null,
  );
  return stmt.run();
}

/* ------------------------- recovery-agent call ------------------------- */

/**
 * Call recovery-agent /restart over Cloudflare Tunnel. Returns parsed JSON.
 * Throws on non-2xx (caller logs failed outcome).
 */
async function callRecoveryAgentRestart(env, tunnelUrl, payload) {
  const body = JSON.stringify(payload);
  const nonce = randHex(16);
  const ts = Math.floor(Date.now() / 1000);
  const message = `${body}|${nonce}|${ts}`;
  const sig = await hmacHex(env.RECOVERY_AGENT_HMAC_KEY, message);

  const resp = await fetch(`${tunnelUrl.replace(/\/+$/, "")}/restart`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-nonce": nonce,
      "x-timestamp": String(ts),
      "x-signature": sig,
    },
    body,
  });
  const text = await resp.text();
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    parsed = { ok: false, error: "bad json from agent", raw: text.slice(0, 400) };
  }
  return { status: resp.status, body: parsed };
}

async function probeRecoveryAgentHealth(tunnelUrl, timeoutMs = 5000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const resp = await fetch(`${tunnelUrl.replace(/\/+$/, "")}/health`, {
      method: "GET", signal: ctrl.signal,
    });
    const text = await resp.text();
    let body;
    try { body = JSON.parse(text); } catch { body = { ok: false }; }
    return { ok: resp.ok, status: resp.status, body };
  } catch (e) {
    return { ok: false, status: 0, body: { error: String(e) } };
  } finally {
    clearTimeout(t);
  }
}

/* ------------------------------ routes --------------------------------- */

async function handleAdminRestart(req, env) {
  if (!adminAuthOk(req, env)) return err(401, "unauthorized");
  if (req.method !== "POST") return err(405, "method not allowed");

  let body;
  try {
    body = await req.json();
  } catch {
    return err(400, "bad json");
  }
  const customer = body.customer_slug;
  const reason = body.reason || "admin_button";
  const triggeredBy = body.triggered_by === "manual" ? "manual" : "admin_button";

  if (typeof customer !== "string" || !/^[a-z0-9_-]{1,64}$/.test(customer)) {
    return err(400, "missing or bad customer_slug");
  }

  const tunnels = parseTunnelMap(env);
  const tunnelUrl = tunnels[customer];
  if (!tunnelUrl) {
    return err(400, `no tunnel URL configured for customer: ${customer}`);
  }

  // hetzner_host is derived from the tunnel URL's hostname for the audit row.
  let hetznerHost = "unknown";
  try { hetznerHost = new URL(tunnelUrl).hostname; } catch { /* keep default */ }

  const requestId = body.request_id || randHex(8);
  const start = Date.now();
  let agentResp;
  let agentErr = null;
  try {
    agentResp = await callRecoveryAgentRestart(env, tunnelUrl, {
      container_name: customer,
      reason,
      request_id: requestId,
    });
  } catch (e) {
    agentErr = String(e);
  }
  const durationMs = Date.now() - start;

  let outcome = "failed";
  let errorMessage = agentErr;
  let pidBefore = null, pidAfter = null, thrBefore = null, thrAfter = null;
  if (agentResp) {
    if (agentResp.status === 200 && agentResp.body?.ok) outcome = "success";
    else if (agentResp.status === 429 && agentResp.body?.loop_detected) {
      outcome = "failed";
      errorMessage = "loop_detected";
    } else {
      outcome = "failed";
      errorMessage = agentResp.body?.error || `agent http ${agentResp.status}`;
    }
    pidBefore = agentResp.body?.pid_count_before ?? null;
    pidAfter = agentResp.body?.pid_count_after ?? null;
    thrBefore = agentResp.body?.thread_count_before ?? null;
    thrAfter = agentResp.body?.thread_count_after ?? null;
  }

  await logRecovery(env, {
    ts: Math.floor(Date.now() / 1000),
    customer_slug: customer,
    hetzner_host: hetznerHost,
    action: "restart",
    ai_alive_before: null,
    ai_alive_after: agentResp?.body?.ai_alive_after ?? null,
    thread_count_before: thrBefore,
    thread_count_after: thrAfter,
    pid_count_before: pidBefore,
    pid_count_after: pidAfter,
    duration_ms: durationMs,
    outcome,
    error_message: errorMessage,
    triggered_by: triggeredBy,
    request_id: requestId,
  });

  return json({
    ok: outcome === "success",
    outcome,
    customer_slug: customer,
    request_id: requestId,
    duration_ms: durationMs,
    agent_status: agentResp?.status ?? null,
    agent_body: agentResp?.body ?? null,
    error: errorMessage,
  }, outcome === "success" ? 200 : (agentResp?.status === 429 ? 429 : 502));
}

async function handleRecoveryLog(req, env) {
  if (!adminAuthOk(req, env)) return err(401, "unauthorized");
  const url = new URL(req.url);
  const customer = url.searchParams.get("customer");
  if (!customer || !/^[a-z0-9_-]{1,64}$/.test(customer)) {
    return err(400, "bad customer query param");
  }
  const hours = Math.min(Math.max(parseInt(url.searchParams.get("hours") || "24", 10), 1), 168);
  const since = Math.floor(Date.now() / 1000) - hours * 3600;
  const rs = await env.DB.prepare(`
    SELECT id, ts, customer_slug, hetzner_host, action,
           ai_alive_before, ai_alive_after,
           thread_count_before, thread_count_after,
           pid_count_before, pid_count_after,
           duration_ms, outcome, error_message, triggered_by, request_id
      FROM customer_portal_recovery_log
     WHERE customer_slug = ? AND ts >= ?
     ORDER BY ts DESC
     LIMIT 500
  `).bind(customer, since).all();
  return json({ customer_slug: customer, hours, rows: rs.results || [] });
}

/* -------------------------- cron handler ------------------------------- */

/**
 * Phase 1 cron: probe recovery-agent /health for each customer in the tunnel map.
 * Every sample is logged to D1 (action='health_check'). No restart decisions.
 *
 * Aether-side TODO (Phase 2): swap probeRecoveryAgentHealth() for a richer
 * container-aware probe that calls health_probe.py via recovery-agent and
 * yields ai_alive. This worker is wired so that swap is a one-function change.
 */
async function handleCron(env, ctx) {
  const tunnels = parseTunnelMap(env);
  const customers = Object.keys(tunnels);
  if (customers.length === 0) {
    console.log("[customer-portal-health] cron: no customers configured");
    return;
  }
  const tasks = customers.map(async (slug) => {
    const tunnelUrl = tunnels[slug];
    let host = "unknown";
    try { host = new URL(tunnelUrl).hostname; } catch { /* default */ }
    const start = Date.now();
    const probe = await probeRecoveryAgentHealth(tunnelUrl);
    const durationMs = Date.now() - start;
    try {
      await logRecovery(env, {
        ts: Math.floor(Date.now() / 1000),
        customer_slug: slug,
        hetzner_host: host,
        action: "health_check",
        ai_alive_before: probe.ok ? true : null,    // Phase 1 = daemon-alive only
        ai_alive_after: null,
        thread_count_before: null,
        thread_count_after: null,
        pid_count_before: null,
        pid_count_after: null,
        duration_ms: durationMs,
        outcome: probe.ok ? "success" : "failed",
        error_message: probe.ok ? null : (probe.body?.error || `http ${probe.status}`),
        triggered_by: "cron",
        request_id: null,
      });
    } catch (e) {
      console.error(`[customer-portal-health] D1 write failed for ${slug}: ${e}`);
    }
  });
  await Promise.allSettled(tasks);
}

/* ----------------------------- entry ----------------------------------- */

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname;

    if (path === "/health" && req.method === "GET") {
      return json({ ok: true, worker: "customer-portal-health" });
    }
    if (path === "/admin/restart") {
      return handleAdminRestart(req, env);
    }
    if (path === "/admin/recovery-log" && req.method === "GET") {
      return handleRecoveryLog(req, env);
    }
    return err(404, "not found");
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(handleCron(env, ctx));
  },
};
