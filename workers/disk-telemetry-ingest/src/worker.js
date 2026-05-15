/**
 * disk-telemetry-ingest Worker
 *
 * Ingestion endpoint for fleet disk telemetry. Authenticated via HMAC-SHA256
 * over (body + nonce + timestamp), keyed by INGEST_TOKEN. Replay-resistant
 * via nonce LRU + 30s timestamp window.
 *
 * Spec: specs/disk-safety-telemetry-2026-05-15.md
 * CTO amendments folded in:
 *   #1 HMAC nonce + timestamp window (30s)
 *   #3 INGEST_TOKEN_PREVIOUS rolling-rotation support
 *   #4 source_ip column stamped from cf-connecting-ip
 *
 * Endpoints:
 *   POST /ingest                    — daemon submits telemetry row
 *   GET  /health                    — Worker self-health (no auth)
 *   GET  /civs/<civ>/recent?hours=N — admin-auth-gated forensics read
 *
 * D1 binding: env.DB = disk-telemetry
 * Secrets:    env.INGEST_TOKEN (current), env.INGEST_TOKEN_PREVIOUS (rotation window), env.ADMIN_TOKEN
 */

// In-memory nonce LRU (best-effort; Workers may rotate isolates).
// Replay defense is primarily timestamp window; nonce LRU is belt-and-suspenders.
const NONCE_LRU = new Map();
const NONCE_LRU_MAX = 2048;
const TS_WINDOW_SECONDS = 30;

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

function err(status, message) {
  return json({ error: message }, status);
}

function rememberNonce(nonce) {
  if (NONCE_LRU.has(nonce)) return false; // already seen — replay
  NONCE_LRU.set(nonce, Date.now());
  if (NONCE_LRU.size > NONCE_LRU_MAX) {
    // drop oldest entries
    const drop = NONCE_LRU.size - NONCE_LRU_MAX;
    let i = 0;
    for (const k of NONCE_LRU.keys()) {
      if (i++ >= drop) break;
      NONCE_LRU.delete(k);
    }
  }
  return true;
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

function constantTimeEqualHex(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

async function verifyHmac(rawBody, nonce, ts, sig, env) {
  const message = `${rawBody}|${nonce}|${ts}`;
  const candidates = [env.INGEST_TOKEN, env.INGEST_TOKEN_PREVIOUS].filter(Boolean);
  for (const tok of candidates) {
    const expected = await hmacHex(tok, message);
    if (constantTimeEqualHex(expected, sig)) return true;
  }
  return false;
}

async function handleIngest(req, env) {
  if (req.method !== "POST") return err(405, "method not allowed");

  const nonce = req.headers.get("x-nonce");
  const tsHeader = req.headers.get("x-timestamp");
  const sig = req.headers.get("x-signature");
  if (!nonce || !tsHeader || !sig) return err(401, "missing auth headers");

  const ts = Number(tsHeader);
  if (!Number.isFinite(ts)) return err(401, "bad timestamp");
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - ts) > TS_WINDOW_SECONDS) return err(401, "timestamp out of window");

  if (!rememberNonce(nonce)) return err(401, "nonce replay");

  const rawBody = await req.text();
  const ok = await verifyHmac(rawBody, nonce, ts, sig, env);
  if (!ok) return err(401, "bad signature");

  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return err(400, "bad json");
  }

  // Minimal schema validation
  const required = [
    "civ_name", "hostname", "disk_root_used_pct", "disk_root_free_mb",
    "tmp_size_mb", "tmp_large_files_count",
  ];
  for (const k of required) {
    if (payload[k] === undefined || payload[k] === null) return err(400, `missing field: ${k}`);
  }
  if (typeof payload.civ_name !== "string" || payload.civ_name.length > 64) return err(400, "bad civ_name");
  if (typeof payload.hostname !== "string" || payload.hostname.length > 128) return err(400, "bad hostname");
  const pct = Number(payload.disk_root_used_pct);
  if (!Number.isFinite(pct) || pct < 0 || pct > 100) return err(400, "bad disk_root_used_pct");

  const sourceIp = req.headers.get("cf-connecting-ip") || null;
  const insertTs = Math.floor(Date.now() / 1000);

  const stmt = env.DB.prepare(`
    INSERT INTO disk_telemetry
      (ts, civ_name, hostname, source_ip,
       disk_root_used_pct, disk_root_free_mb, tmp_size_mb,
       tmp_large_files_count, working_tree_large_files_count,
       alert_tier, raw_top5_tmp_files, daemon_version)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    insertTs,
    payload.civ_name,
    payload.hostname,
    sourceIp,
    Math.round(pct),
    Math.round(Number(payload.disk_root_free_mb) || 0),
    Math.round(Number(payload.tmp_size_mb) || 0),
    Math.round(Number(payload.tmp_large_files_count) || 0),
    payload.working_tree_large_files_count == null
      ? null
      : Math.round(Number(payload.working_tree_large_files_count)),
    payload.alert_tier || null,
    payload.raw_top5_tmp_files
      ? JSON.stringify(payload.raw_top5_tmp_files).slice(0, 4000)
      : null,
    payload.daemon_version || null,
  );

  const result = await stmt.run();
  return json({ ok: true, id: result.meta?.last_row_id ?? null, ts: insertTs });
}

async function handleRecent(req, env, civName) {
  const auth = req.headers.get("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) return err(401, "unauthorized");
  if (!/^[A-Za-z0-9_-]{1,64}$/.test(civName)) return err(400, "bad civ_name");

  const url = new URL(req.url);
  const hours = Math.min(Math.max(parseInt(url.searchParams.get("hours") || "6", 10), 1), 168);
  const since = Math.floor(Date.now() / 1000) - hours * 3600;

  const rs = await env.DB.prepare(`
    SELECT id, ts, civ_name, hostname, source_ip,
           disk_root_used_pct, disk_root_free_mb, tmp_size_mb,
           tmp_large_files_count, working_tree_large_files_count,
           alert_tier, daemon_version
      FROM disk_telemetry
     WHERE civ_name = ? AND ts >= ?
     ORDER BY ts DESC
     LIMIT 500
  `).bind(civName, since).all();

  return json({ civ_name: civName, hours, rows: rs.results || [] });
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname;

    if (path === "/health" && req.method === "GET") {
      return json({ ok: true, worker: "disk-telemetry-ingest" });
    }
    if (path === "/ingest") {
      return handleIngest(req, env);
    }
    const m = path.match(/^\/civs\/([^/]+)\/recent$/);
    if (m && req.method === "GET") {
      return handleRecent(req, env, m[1]);
    }
    return err(404, "not found");
  },
};
