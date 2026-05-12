/**
 * Referrals API Worker — full CRUD facade over D1 `purebrain-referrals`.
 *
 * Replaces ALL container/SQLite dependencies. D1 is the single source of truth.
 *
 * Endpoints (all JSON responses):
 *
 *   --- Public / VPS-scoped ---
 *   GET  /health
 *   GET  /referrers?code=PB-XXXX             — full referrer row (minus password_hash)
 *   GET  /referrers?email=foo@bar             — full referrer row
 *   GET  /referrals?referrer_id=N             — list referrals (joined with commission sums)
 *   GET  /commission_payments?referral_id=N
 *   GET  /dashboard?code=PB-XXXX             — aggregated shape with partner_tier + tier_rate
 *   GET  /leaderboard                         — ranked affiliates
 *
 *   --- Public Application & Payout (partner-self) ---
 *   POST /partners/apply                      — partner application (creates partner_applications row)
 *   POST /referrals/complete                  — payment-page onApprove POST (idempotent pending row)
 *   POST /payouts/request                     — partner-self payout request ($50 min)
 *
 *   --- Admin (X-Admin-Token required) ---
 *   GET  /admin/emails                        — lightweight (email, code) pairs
 *   GET  /admin/affiliates                    — full admin view (incl. partner_tier + split_config)
 *   GET  /admin/payouts                       — list payout requests (legacy + v2 merged)
 *   GET  /admin/applications                  — list partner applications (?status= filter)
 *   GET  /admin/stats                         — overview stats (totals)
 *   POST /referrers/upsert                    — auto-provision referral code (default tier=silver)
 *   POST /partners/signup                     — direct admin signup (default tier=silver)
 *   POST /commission_payments                 — record commission (writes tier_at_write + Support Tier detect)
 *   POST /admin/payout/mark-paid              — mark a payout request as paid
 *   POST /admin/referral/assign               — manually assign a client to a referrer
 *   POST /admin/applications/:id/approve      — approve partner application
 *   POST /admin/applications/:id/reject       — reject partner application (CTO Edit #8)
 *   POST /admin/recalc-tier                   — retroactive rate recalc (chunked, idempotent)
 *   POST /referrals/complete (admin mode)     — mark existing row completed by id
 *   PUT  /admin/affiliate/update              — update affiliate (incl. partner_tier, split_config)
 *   PUT  /admin/referral/update               — update a referral record
 *   DELETE /admin/affiliate/delete            — delete affiliate + cascade
 *
 * Auth model:
 *   - /admin/* and admin write endpoints require X-Admin-Token header or
 *     ?admin_token= query param matching ADMIN_TOKENS secret (comma-separated).
 *   - /partners/apply, /referrals/complete (public mode), /payouts/request are
 *     PUBLIC — called from website frontend. Idempotency from UNIQUE INDEX
 *     and identity gate (paypal_email match) prevent abuse.
 *
 * D1 binding: env.DB
 *
 * Env vars (wrangler.toml + secrets):
 *   ADMIN_TOKENS           — comma-separated admin tokens (secret, REQUIRED)
 *   SUPPORT_TIER_PLAN_IDS  — comma-separated PayPal Plan IDs that map to Support
 *                            Tier 25% (SPEC E1 / CTO Q2). Empty default = no plans.
 *
 * Constitutional notes:
 *   - Commission formula = paymentAmount * rate. NO $35 deduction in Worker
 *     ($35 ops fee comes off in tools/paypal_auto_split.py per CTO Edit #1).
 *   - Every commission_payments INSERT MUST set tier_at_write (CTO Edit #2)
 *     for safe retroactive recalc (CTO §1.3).
 *   - $50 min payout enforced by DB CHECK on payout_requests_v2.
 *   - (pb_ref, payment_id) UNIQUE INDEX makes /referrals/complete idempotent.
 */

const REFERRER_PUBLIC_COLS = [
  "id", "user_name", "user_email", "referral_code",
  "paypal_email", "created_at", "partner_tier", "total_sales", "split_config"
  // Note: password_hash intentionally excluded.
];

/* ---------- tier rate lookup (CTO Edit #2 + SPEC C1/C3) ---------- */

// Authoritative tier→rate map. Source of truth for commission calculations.
// 'silver' is the new default for /partners/signup (was 'standard' 5%).
// 'elite' kept for legacy partners (e.g., founder-tier); admin-only.
const TIER_RATES = Object.freeze({
  standard: 0.05,   // legacy — 5% — DO NOT assign to new partners
  silver:   0.15,   // default for new signups (CTO Edit #2 / SPEC C1)
  gold:     0.17,   // 100+ referrals milestone (SPEC C3)
  platinum: 0.20,   // 1000+ referrals milestone (SPEC C3)
  elite:    0.25,   // legacy founder-tier; matches Support Tier numerically
});

const SUPPORT_TIER_RATE = 0.25; // SPEC E1

function rateForTier(tier) {
  const t = String(tier || "silver").toLowerCase();
  return TIER_RATES[t] !== undefined ? TIER_RATES[t] : TIER_RATES.silver;
}

// Milestone thresholds (SPEC C3)
function milestoneTier(totalSales) {
  const n = Number(totalSales) || 0;
  if (n >= 1000) return "platinum";
  if (n >= 100)  return "gold";
  return null; // no milestone reached
}

// SPEC E1: detect Support Tier subscription via PayPal Plan ID allowlist
function isSupportTierPlan(planId, env) {
  if (!planId) return false;
  const allow = (env.SUPPORT_TIER_PLAN_IDS || "")
    .split(",").map(s => s.trim()).filter(Boolean);
  return allow.includes(String(planId).trim());
}

/**
 * Constitutional commission formula (SPEC A3 / CTO Edit #1):
 *   commission = paymentAmount * rate
 *
 * NO $35 deduction in Worker — the $35 ops fee is taken in
 * tools/paypal_auto_split.py at payout time, NOT here.
 *
 * SPEC E1: if planId matches SUPPORT_TIER_PLAN_IDS, override to 25%.
 *
 * Returns { value, rate, source } where source ∈ {'standard','support_tier'}.
 */
function computeCommission({ paymentAmount, partnerTier, planId, env }) {
  const amt = Number(paymentAmount) || 0;
  if (isSupportTierPlan(planId, env)) {
    return {
      value: Math.round(amt * SUPPORT_TIER_RATE * 100) / 100,
      rate:  SUPPORT_TIER_RATE,
      source: "support_tier",
    };
  }
  const rate = rateForTier(partnerTier);
  return {
    value: Math.round(amt * rate * 100) / 100,
    rate,
    source: "standard",
  };
}

/* ---------- helpers ---------- */

function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
      "access-control-allow-headers": "x-admin-token, content-type, authorization",
      ...(init.headers || {}),
    },
  });
}

function err(status, message) {
  return json({ error: message }, { status });
}

async function requireAdmin(request, env) {
  const hdr = request.headers.get("x-admin-token") || "";
  const url = new URL(request.url);
  const qp  = url.searchParams.get("admin_token") || "";
  const token = (hdr || qp).trim();
  if (!token) return false;
  const allow = (env.ADMIN_TOKENS || "").split(",").map(s => s.trim()).filter(Boolean);
  return allow.includes(token);
}

/* ---------- session-based admin auth (CTO 2026-05-12 unified login) ---------- */

/**
 * 60-second in-memory cache for validate-session results.
 * Mirrors the social-api pattern (line 3707) — acceptable lag per CTO brief.
 * Keys: bearer token string. Values: { session, expires_ms } or { ok: false, expires_ms }.
 */
const _SESSION_CACHE = new Map();
const SESSION_CACHE_TTL_MS = 60_000;

function _cacheGet(key) {
  const v = _SESSION_CACHE.get(key);
  if (!v) return null;
  if (Date.now() > v.expires_ms) {
    _SESSION_CACHE.delete(key);
    return null;
  }
  return v;
}

function _cacheSet(key, value) {
  _SESSION_CACHE.set(key, { ...value, expires_ms: Date.now() + SESSION_CACHE_TTL_MS });
}

const ADMIN_ROLES = new Set(["owner", "admin", "leader", "system"]);

/**
 * Validate a session token by calling social-api via Service Binding.
 *
 * Token sourced from (in priority order):
 *   1. Authorization: Bearer <token>
 *   2. social_session cookie
 *
 * Returns { ok: true, session: {user_id, email, name, team_id, role, billing_tier, expires_at} }
 * Returns { ok: false, status: 401|403 } on failure.
 *
 * 60s in-memory cache to mirror social-api pattern.
 *
 * Requires:
 *   - env.SOCIAL_API service binding
 *   - env.INTERNAL_BINDING_SECRET — must match the 6-Worker family value
 *     (per feedback_secret_rotation_must_include_portal_proxy.md)
 */
async function requireAdminViaSession(request, env) {
  // Extract token from Bearer header or cookie
  let token = "";
  const auth = (request.headers.get("authorization") || "").trim();
  if (auth.toLowerCase().startsWith("bearer ")) {
    token = auth.slice(7).trim();
  }
  if (!token) {
    const cookie = request.headers.get("cookie") || "";
    const m = cookie.match(/(?:^|;\s*)social_session=([^;]+)/);
    if (m) token = decodeURIComponent(m[1]).trim();
  }
  if (!token) return { ok: false, status: 401 };

  // Check cache
  const cached = _cacheGet(token);
  if (cached) {
    if (cached.session) {
      return { ok: true, session: cached.session };
    }
    return { ok: false, status: cached.status || 401 };
  }

  // Service Binding required
  if (!env.SOCIAL_API || typeof env.SOCIAL_API.fetch !== "function") {
    return { ok: false, status: 503 };
  }
  const secret = (env.INTERNAL_BINDING_SECRET || "").trim();
  if (!secret) return { ok: false, status: 503 };

  try {
    const req = new Request("https://social-api/internal/validate-session", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding-secret": secret,
      },
      body: JSON.stringify({ token }),
    });
    const resp = await env.SOCIAL_API.fetch(req);
    if (!resp.ok) {
      _cacheSet(token, { ok: false, status: resp.status });
      return { ok: false, status: resp.status };
    }
    const data = await resp.json().catch(() => ({}));
    if (!data || data.valid !== true) {
      _cacheSet(token, { ok: false, status: 401 });
      return { ok: false, status: 401 };
    }
    const role = String(data.role || "").toLowerCase();
    if (!ADMIN_ROLES.has(role)) {
      _cacheSet(token, { ok: false, status: 403 });
      return { ok: false, status: 403 };
    }
    const session = {
      user_id: data.user_id,
      email: data.email,
      name: data.name,
      team_id: data.team_id,
      role,
      billing_tier: data.billing_tier,
      expires_at: data.expires_at,
    };
    _cacheSet(token, { session });
    return { ok: true, session };
  } catch (e) {
    return { ok: false, status: 503 };
  }
}

/**
 * Unified admin gate — session-first, X-Admin-Token fallback.
 *
 * Fallback is behind LEGACY_ADMIN_TOKEN_ENABLED env var (default "true" for
 * 1-week rollback window per CTO brief; flip to "false" after stability, then
 * remove the entire fallback branch in v2).
 *
 * Returns { ok: true, source: 'session'|'token', user: {email, user_id?} } on success.
 * Returns { ok: false, status } on failure.
 *
 * Caller convention (for sweep-replace):
 *   const gate = await requireAdminUnified(request, env);
 *   if (!gate.ok) return err(gate.status || 401, "unauthorized");
 *   // gate.user.email available for audit logging
 */
async function requireAdminUnified(request, env) {
  // Session-first (new path)
  const viaSession = await requireAdminViaSession(request, env);
  if (viaSession.ok) {
    // Audit log: attribute action to real user (Worker tail-accessible)
    try {
      const url = new URL(request.url);
      console.log(JSON.stringify({
        event: "admin_action",
        source: "session",
        user_id: viaSession.session.user_id,
        email: viaSession.session.email,
        role: viaSession.session.role,
        method: request.method,
        path: url.pathname,
        ts: new Date().toISOString(),
      }));
    } catch (_e) { /* logging best-effort */ }
    return { ok: true, source: "session", user: viaSession.session };
  }
  // 503 means service-binding unavailable — don't degrade silently; surface
  if (viaSession.status === 503) {
    // fall through to token if enabled (rollback path)
  } else if (viaSession.status === 403) {
    // Valid session but insufficient role — do NOT fall through to token
    // (otherwise viewer-with-token could escalate).
    return { ok: false, status: 403 };
  }
  // X-Admin-Token fallback (legacy, gated by feature flag)
  const legacyEnabled = String(env.LEGACY_ADMIN_TOKEN_ENABLED || "true").toLowerCase() === "true";
  if (legacyEnabled && (await requireAdmin(request, env))) {
    try {
      const url = new URL(request.url);
      console.log(JSON.stringify({
        event: "admin_action",
        source: "token",
        user_id: null,
        email: "legacy-token-user",
        method: request.method,
        path: url.pathname,
        ts: new Date().toISOString(),
      }));
    } catch (_e) {}
    return { ok: true, source: "token", user: { email: "legacy-token-user" } };
  }
  return { ok: false, status: viaSession.status || 401 };
}

/**
 * Auth gate for /internal/* endpoints (CTO 2026-05-12 Track E).
 *
 * Service Binding traffic between Workers is in-CF and never reaches the
 * public internet, but per `feedback_purebrain_social_never_touches_referral_or_clients.md`
 * defense-in-depth rigor: gate every internal hop with a shared secret.
 *
 * NEW SECRET (referrals-api isolation boundary):
 *   env.REFERRALS_INTERNAL_SECRET — separate from the 6-Worker
 *   `INTERNAL_BINDING_SECRET` used by clients-api ↔ social/admin/agentmail/paypal.
 *   Keeping a distinct value here means the referrals trust boundary is
 *   independent — rotation of one secret doesn't force coordinated 6-Worker
 *   redeploy + risks. Aligns with constitutional rule
 *   `feedback_purebrain_social_never_touches_referral_or_clients.md`
 *   (referrals domain is isolated).
 *
 * Backward-compat: also accepts env.INTERNAL_BINDING_SECRET so that if the
 * paypal-webhook propagation hasn't completed yet, the legacy 6-Worker secret
 * still authenticates the binding call. Either value MUST match for true.
 *
 * Headers accepted (any one matches):
 *   - x-internal-binding-secret  (matches paypal-webhook + clients-api convention)
 *   - x-internal-secret           (legacy alias)
 *   - authorization: Bearer <secret>
 *
 * Returns true on match. False if neither secret configured (fail-closed).
 */
function checkInternalBinding(request, env) {
  const primary = (env.REFERRALS_INTERNAL_SECRET || "").trim();
  const legacy  = (env.INTERNAL_BINDING_SECRET   || "").trim();
  if (!primary && !legacy) return false; // fail-closed

  const candidates = [];
  const h1 = (request.headers.get("x-internal-binding-secret") || "").trim();
  if (h1) candidates.push(h1);
  const h2 = (request.headers.get("x-internal-secret") || "").trim();
  if (h2) candidates.push(h2);
  const auth = (request.headers.get("authorization") || "").trim();
  if (auth.toLowerCase().startsWith("bearer ")) {
    candidates.push(auth.slice(7).trim());
  }
  for (const c of candidates) {
    if (primary && c === primary) return true;
    if (legacy  && c === legacy)  return true;
  }
  return false;
}

function pick(row, cols) {
  const out = {};
  for (const c of cols) out[c] = row[c];
  return out;
}

async function parseBody(request) {
  try { return await request.json(); }
  catch (_e) { return null; }
}

/* ---------- affiliate auth helpers (PTT# Fix B, 2026-05-12) ----------
 *
 * Ported from purebrain-site/functions/api/referral/_shared.js (dead CF Pages
 * Functions). Reason: CF Pages `_worker.js` override has dropped the entire
 * functions/ directory from prod routing — affiliate login broke for all 66
 * affiliates. Owner per `feedback_aether_chy_domain_boundaries.md`: Aether.
 *
 * CONSTITUTIONAL CONSTRAINTS:
 *   - PBKDF2-SHA256 @ 100k iterations ONLY. NO bcrypt introduction.
 *   - NO logging of email, password, password_hash, token, or IP.
 *   - NO Resend / NO email send paths (per Jared 2026-05-12 + feedback_no_resend_ever.md).
 *     forgot-password / reset-password DEFERRED — manual D1 reset via support
 *     for affiliates who forget their password.
 *
 * Session token model: opaque 32-byte random hex, server-side validated by
 * lookup in `affiliate_sessions` D1 table. NOT a JWT. 7-day TTL. Server-side
 * revocable via DELETE.
 */

const AFFILIATE_SESSION_TTL_SECS = 86400 * 7;       // 7 days
const AFFILIATE_LOGIN_MAX_ATTEMPTS = 10;            // per 15-min window
const AFFILIATE_LOGIN_WINDOW_SECS = 900;            // 15 minutes
const AFFILIATE_REGISTER_MAX_ATTEMPTS = 5;          // per hour (CTO Q6 add)
const AFFILIATE_REGISTER_WINDOW_SECS = 3600;        // 1 hour
const PBKDF2_ITERATIONS = 100000;
const REFERRAL_CODE_PREFIX = "PB-";
const REFERRAL_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
const REFERRAL_CODE_LENGTH = 4;

function _bufToHex(buf) {
  return Array.from(buf).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function _hexToBuf(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}

async function affiliateHashPassword(password) {
  const salt = new Uint8Array(16);
  crypto.getRandomValues(salt);
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const derivedBits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
    keyMaterial,
    256
  );
  return `pbkdf2:${PBKDF2_ITERATIONS}:${_bufToHex(salt)}:${_bufToHex(new Uint8Array(derivedBits))}`;
}

/**
 * Verifies password against stored hash. Supports 5 formats:
 *   1. PBKDF2 (`pbkdf2:iterations:salt_hex:hash_hex`) — current standard.
 *   2. Legacy bcrypt (`$2b$...` / `$2a$...`) — returns false (Workers cannot
 *      verify bcrypt). Caller MUST detect this and force a reset flow.
 *   3. Legacy SHA-256 colon format (`salt:hexdigest`, hash = sha256(`salt:password`))
 *      — accepted then auto-migrated to PBKDF2 by caller on successful login.
 *   4. Legacy SHA-256 dollar format (`salt_hex$digest_hex`, 81-char) — same data
 *      shape as #3 but with `$` separator. Tries multiple hash-input shapes for
 *      compatibility (legacy data was hand-migrated, exact recipe is uncertain).
 *      Auto-migrated to PBKDF2 by caller on successful login.
 *   5. Raw SHA-256 (64-hex, no separator) — assumed unsalted `sha256(password)`.
 *      Auto-migrated to PBKDF2 by caller on successful login.
 *
 * 2026-05-12 hash format coverage extension (Path A patch):
 *   - JAREDSB0 and 5 other affiliates use format #4 (`salt$digest`)
 *   - 6 affiliates use format #5 (raw 64-hex)
 *   - Original `_shared.js` only handled #3 — these rows were never verifiable.
 */
async function affiliateVerifyPassword(password, storedHash) {
  if (!storedHash) return false;

  // Case 1: PBKDF2 — current standard
  if (storedHash.startsWith("pbkdf2:")) {
    const parts = storedHash.split(":");
    if (parts.length !== 4) return false;
    const iterations = parseInt(parts[1], 10);
    const salt = _hexToBuf(parts[2]);
    const expectedHash = parts[3];
    const keyMaterial = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(password),
      "PBKDF2",
      false,
      ["deriveBits"]
    );
    const derivedBits = await crypto.subtle.deriveBits(
      { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
      keyMaterial,
      256
    );
    return _bufToHex(new Uint8Array(derivedBits)) === expectedHash;
  }

  // Case 2: bcrypt — Workers cannot verify natively
  if (storedHash.startsWith("$2b$") || storedHash.startsWith("$2a$")) {
    return false; // caller must force reset
  }

  // Case 3: Legacy SHA-256 with `:` separator (salt:digest)
  // Hash input = `${salt}:${password}` per portal_server.py:3674
  if (storedHash.includes(":") && !storedHash.startsWith("pbkdf2:")) {
    const idx = storedHash.indexOf(":");
    const saltVal = storedHash.substring(0, idx);
    const expectedHex = storedHash.substring(idx + 1);
    const data = new TextEncoder().encode(`${saltVal}:${password}`);
    const digest = await crypto.subtle.digest("SHA-256", data);
    return _bufToHex(new Uint8Array(digest)) === expectedHex;
  }

  // Case 4 (NEW 2026-05-12): Legacy SHA-256 with `$` separator (salt$digest, 81-char)
  // Origin uncertain (no source code emits this shape). Try multiple input recipes
  // for back-compat. First match wins. Guard against bcrypt $2a$/$2b$ prefix.
  if (storedHash.includes("$") && !storedHash.startsWith("$2")) {
    const idx = storedHash.indexOf("$");
    const saltVal = storedHash.substring(0, idx);
    const expectedHex = storedHash.substring(idx + 1).toLowerCase();
    const candidates = [
      `${saltVal}$${password}`,  // sister format to #3 with `$` separator
      `${saltVal}:${password}`,  // colon-style input despite `$` separator
      `${saltVal}${password}`,   // brief's recommended shape (no separator in input)
      `${password}${saltVal}`,   // reverse concat
      password,                  // unsalted fallback (treat salt as cosmetic prefix)
    ];
    for (const candidate of candidates) {
      const data = new TextEncoder().encode(candidate);
      const digest = await crypto.subtle.digest("SHA-256", data);
      if (_bufToHex(new Uint8Array(digest)) === expectedHex) return true;
    }
    return false;
  }

  // Case 5 (NEW 2026-05-12): Raw 64-hex SHA-256 (no separator, no salt)
  if (/^[0-9a-f]{64}$/i.test(storedHash)) {
    const data = new TextEncoder().encode(password);
    const digest = await crypto.subtle.digest("SHA-256", data);
    return _bufToHex(new Uint8Array(digest)) === storedHash.toLowerCase();
  }

  return false;
}

async function affiliateCreateSession(db, referralCode) {
  const arr = new Uint8Array(32);
  crypto.getRandomValues(arr);
  const token = _bufToHex(arr);
  const now = Math.floor(Date.now() / 1000);
  const expiresAt = now + AFFILIATE_SESSION_TTL_SECS;
  await db
    .prepare("INSERT INTO affiliate_sessions (token, referral_code, expires_at) VALUES (?, ?, ?)")
    .bind(token, referralCode.toUpperCase(), expiresAt)
    .run();
  return token;
}

function affiliateGetClientIP(request) {
  return request.headers.get("CF-Connecting-IP")
      || request.headers.get("X-Forwarded-For")
      || "0.0.0.0";
}

async function affiliateHashIP(ip) {
  const data = new TextEncoder().encode(ip);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return _bufToHex(new Uint8Array(digest)).substring(0, 16);
}

/**
 * D1-backed rate limiter. Same algorithm as _shared.js:isRateLimited.
 * Key namespaces (constitutional, must not cross-pollinate):
 *   "login:<ip_hash>"     → /referrals/session
 *   "register:<ip_hash>"  → /referrals/register
 */
async function affiliateIsRateLimited(db, key, maxPerWindow, windowSecs) {
  const now = Math.floor(Date.now() / 1000);
  const row = await db
    .prepare("SELECT count, window_start FROM rate_limits WHERE key = ?")
    .bind(key)
    .first();
  if (!row) {
    await db
      .prepare("INSERT OR REPLACE INTO rate_limits (key, count, window_start) VALUES (?, 1, ?)")
      .bind(key, now).run();
    return false;
  }
  if (now - row.window_start > windowSecs) {
    await db
      .prepare("UPDATE rate_limits SET count = 1, window_start = ? WHERE key = ?")
      .bind(now, key).run();
    return false;
  }
  if (row.count >= maxPerWindow) return true;
  await db
    .prepare("UPDATE rate_limits SET count = count + 1 WHERE key = ?")
    .bind(key).run();
  return false;
}

function _generateReferralCode() {
  const arr = new Uint8Array(REFERRAL_CODE_LENGTH);
  crypto.getRandomValues(arr);
  let suffix = "";
  for (let i = 0; i < REFERRAL_CODE_LENGTH; i++) {
    suffix += REFERRAL_CODE_CHARS[arr[i] % REFERRAL_CODE_CHARS.length];
  }
  return `${REFERRAL_CODE_PREFIX}${suffix}`;
}

async function affiliateGenerateUniqueCode(db) {
  for (let i = 0; i < 50; i++) {
    const code = _generateReferralCode();
    const existing = await db
      .prepare("SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE")
      .bind(code).first();
    if (!existing) return code;
  }
  throw new Error("could not generate unique referral code after 50 attempts");
}

function affiliateReferralLink(code) {
  return `https://purebrain.ai/?ref=${code}`;
}

/* ---------- retroactive backfill helper (CTO 2026-05-12 Bug 2) ---------- */

/**
 * Backfill commission_payments rows for past payments by a client who was
 * just manually assigned to a referrer.
 *
 * Called from POST /admin/referral/assign immediately after the referrals row
 * INSERT succeeds. Also reachable directly via POST /admin/referral/:id/retro-backfill
 * (companion retry endpoint).
 *
 * Strategy (CTO Edit, locked):
 *   1. Look up the new referrer's CURRENT partner_tier — that becomes
 *      tier_at_write for every retro commission row. Matches the
 *      "tier_at_write doctrine" locked 2026-05-07.
 *   2. Call CLIENTS_API.fetch("/internal/client-payments?email=...") for
 *      historical payment events for this email.
 *   3. For each payment with a positive amount and a stable order_id:
 *      INSERT into commission_payments with commission_source='retroactive_assign'.
 *      Idempotent via (referral_id, order_id) check-then-insert (no DB UNIQUE).
 *   4. Return summary { ok, commissions_written, skipped, total_dollars,
 *      payments_seen, tier_at_write, commission_rate }.
 *
 * Graceful degradation:
 *   - CLIENTS_API binding missing → ok:false, error:"clients_api_binding_missing".
 *   - CLIENTS_API returns 404 (endpoint not shipped yet) →
 *     ok:true, commissions_written:0, error:"endpoint_pending". This lets Bug 1
 *     ship standalone while the clients-api side catches up.
 *   - Any non-404 non-2xx → ok:false, error:"clients_api_<status>".
 *   - Per-row INSERT failure (UNIQUE conflict, CHECK failure) → skip + continue.
 *   - Empty payments list → ok:true, commissions_written:0.
 *
 * Constitutional:
 *   - paymentAmount * rate (NO $35 deduction here; ops fee handled at payout).
 *   - tier_at_write set on EVERY commission_payments INSERT (CTO Edit #2).
 *   - Service Binding only — no HTTP+token cross-Worker call.
 */
async function backfillRetroactiveCommissions(env, { referral_id, referrer_id, referred_email }) {
  // Step 1: load referrer's current tier + rate.
  const referrer = await env.DB.prepare(
    `SELECT id, partner_tier FROM referrers WHERE id = ?`
  ).bind(referrer_id).first();
  if (!referrer) return { ok: false, error: "referrer_not_found", commissions_written: 0 };

  const partner_tier = String(referrer.partner_tier || "silver").toLowerCase();
  const commission_rate = TIER_RATES[partner_tier];
  if (!commission_rate) {
    return { ok: false, error: `invalid_tier:${partner_tier}`, commissions_written: 0 };
  }

  // Step 2: fetch historical payments via Service Binding.
  if (!env.CLIENTS_API) {
    return { ok: false, error: "clients_api_binding_missing", commissions_written: 0 };
  }
  if (!env.INTERNAL_BINDING_SECRET) {
    return { ok: false, error: "internal_binding_secret_missing", commissions_written: 0 };
  }

  const url = `https://clients-api/internal/client-payments?email=${encodeURIComponent(referred_email)}`;
  let resp;
  try {
    resp = await env.CLIENTS_API.fetch(new Request(url, {
      method: "GET",
      headers: {
        "x-internal-binding": "clients-api",
        "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
      },
    }));
  } catch (e) {
    return { ok: false, error: `clients_api_throw:${String(e && e.message || e).slice(0, 80)}`, commissions_written: 0 };
  }

  if (resp.status === 404) {
    // Endpoint not yet shipped on clients-api. Graceful degradation per Bug 2 plan.
    return {
      ok: true,
      commissions_written: 0,
      skipped: 0,
      total_dollars: 0,
      payments_seen: 0,
      tier_at_write: partner_tier,
      commission_rate,
      error: "endpoint_pending",
      message: "clients-api /internal/client-payments not yet shipped. Retry via POST /admin/referral/:id/retro-backfill once available.",
    };
  }
  if (!resp.ok) {
    return { ok: false, error: `clients_api_${resp.status}`, commissions_written: 0 };
  }

  let data;
  try { data = await resp.json(); }
  catch (_e) { return { ok: false, error: "clients_api_bad_json", commissions_written: 0 }; }

  const payments = Array.isArray(data && data.payments) ? data.payments : [];
  if (payments.length === 0) {
    return { ok: true, commissions_written: 0, skipped: 0, total_dollars: 0, payments_seen: 0, tier_at_write: partner_tier, commission_rate };
  }

  // Step 3: write commission rows.
  let written = 0;
  let skipped = 0;
  let total_dollars = 0;
  const now = new Date().toISOString();

  for (const p of payments) {
    const payment_amount = Number(p && p.amount);
    if (!(payment_amount > 0)) { skipped++; continue; }

    const commission_value = Math.round(payment_amount * commission_rate * 100) / 100;
    const order_id = String((p && (p.payment_id || p.order_id || p.id)) || "").trim();
    if (!order_id) { skipped++; continue; }

    // Idempotency: skip if a commission row for this referral + order_id already exists.
    const dup = await env.DB.prepare(
      `SELECT id FROM commission_payments WHERE referral_id = ? AND order_id = ? LIMIT 1`
    ).bind(referral_id, order_id).first();
    if (dup) { skipped++; continue; }

    try {
      await env.DB.prepare(
        `INSERT INTO commission_payments
           (referrer_id, referral_id, payer_email, order_id,
            payment_amount, commission_rate, commission_value,
            tier, tier_at_write, commission_source, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(
        referrer_id,
        referral_id,
        referred_email,
        order_id,
        payment_amount,
        commission_rate,
        commission_value,
        partner_tier,            // legacy `tier` col mirrors tier_at_write
        partner_tier,            // tier_at_write — CTO Edit #2 constitutional
        "retroactive_assign",    // commission_source (CHECK extended in migration 0003)
        now
      ).run();
      written++;
      total_dollars += commission_value;
    } catch (_e) {
      // UNIQUE / CHECK / FK failure — skip and continue.
      skipped++;
    }
  }

  return {
    ok: true,
    commissions_written: written,
    skipped,
    total_dollars: Math.round(total_dollars * 100) / 100,
    payments_seen: payments.length,
    tier_at_write: partner_tier,
    commission_rate,
  };
}

/* ---------- route handler ---------- */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    let path = url.pathname.replace(/\/+$/, "") || "/";
    const method = request.method.toUpperCase();

    // Path aliases (CTO 2026-05-12 Track B.1)
    // /admin/partners is a frontend-friendly alias for /admin/affiliates.
    // Rewriting here is DRY and ensures all auth + caching behavior is identical.
    if (path === "/admin/partners") path = "/admin/affiliates";

    // CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
          "access-control-allow-headers": "x-admin-token, content-type, authorization",
          "access-control-max-age": "86400",
        },
      });
    }

    try {
      // ─────────────────────────────────────────────
      // POST /referrals/session — affiliate login (PTT# Fix B, 2026-05-12)
      //
      // Ported from purebrain-site/functions/api/referral/session.js (dead CF
      // Pages Function — _worker.js override stripped functions/ routing).
      //
      // Body: { email? | referral_code?, password }
      // Returns: { ok, session_token, referral_code, expires_in }
      //
      // First-login flow: if password_hash is empty, the first POST CLAIMS
      // the password (sets it for that referrer). This is intentional — all
      // 66 legacy affiliates have empty hashes until they log in once. No
      // affiliate-comms blast required to "set" a password; they choose it
      // on first login.
      //
      // Rate limit: 10 attempts / 15 min per IP hash.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/referrals/session") {
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const code = String(body.referral_code || "").trim().toUpperCase();
        const email = String(body.email || "").trim().toLowerCase();
        const password = String(body.password || "").trim();

        if (!password) return err(400, "password required");
        if (!code && !email) return err(400, "referral_code or email required");

        const ipHash = await affiliateHashIP(affiliateGetClientIP(request));
        const limited = await affiliateIsRateLimited(
          env.DB,
          `login:${ipHash}`,
          AFFILIATE_LOGIN_MAX_ATTEMPTS,
          AFFILIATE_LOGIN_WINDOW_SECS
        );
        if (limited) {
          return err(429, "too many login attempts. Please wait 15 minutes.");
        }

        let row;
        if (code) {
          row = await env.DB
            .prepare("SELECT referral_code, password_hash FROM referrers WHERE referral_code = ? COLLATE NOCASE")
            .bind(code).first();
        } else {
          row = await env.DB
            .prepare("SELECT referral_code, password_hash FROM referrers WHERE user_email = ? COLLATE NOCASE")
            .bind(email).first();
        }
        if (!row) return err(404, "account not found");

        const storedHash = row.password_hash;

        if (!storedHash) {
          // First login — claim the password
          const newHash = await affiliateHashPassword(password);
          await env.DB
            .prepare("UPDATE referrers SET password_hash = ? WHERE referral_code = ? COLLATE NOCASE")
            .bind(newHash, row.referral_code).run();
          // Audit log — code is NOT PII; never log email/password/token/IP.
          console.log(`[SECURITY] First-login password claim for affiliate code ${row.referral_code}`);
        } else {
          const valid = await affiliateVerifyPassword(password, storedHash);
          if (!valid) {
            // Legacy bcrypt rows cannot be verified in Workers — direct user
            // to forgot-password flow. (forgot/reset endpoints DEFERRED per
            // 2026-05-12 constitutional ruling: no Resend. Interim: manual
            // D1 reset via support — admin sets password_hash='' for the
            // affiliate, then they re-claim on next login.)
            if (storedHash.startsWith("$2b$") || storedHash.startsWith("$2a$")) {
              return err(401, "Your account requires a password reset. Contact support.");
            }
            return err(401, "incorrect password");
          }
          // Auto-migrate legacy SHA-256 hashes to PBKDF2 on successful login.
          if (!storedHash.startsWith("pbkdf2:")) {
            const migratedHash = await affiliateHashPassword(password);
            await env.DB
              .prepare("UPDATE referrers SET password_hash = ? WHERE referral_code = ? COLLATE NOCASE")
              .bind(migratedHash, row.referral_code).run();
          }
        }

        const sessionToken = await affiliateCreateSession(env.DB, row.referral_code);
        return json({
          ok: true,
          session_token: sessionToken,
          referral_code: row.referral_code,
          expires_in: AFFILIATE_SESSION_TTL_SECS,
        });
      }

      // ─────────────────────────────────────────────
      // POST /referrals/register — new affiliate signup (PTT# Fix B, 2026-05-12)
      //
      // Ported from purebrain-site/functions/api/referral/register.js (dead).
      // Body: { name, email, password?, paypal_email? }
      // Returns: { ok, referral_code, referral_link, existing }
      //
      // Idempotent on email: existing referrer returned with existing:true.
      // Auto-generates a random password if caller doesn't supply one (or
      // supplies <6 chars). Password_hash stored, raw password discarded.
      //
      // Rate limit: 5 attempts / hour per IP hash (CTO Q6 add — not in source).
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/referrals/register") {
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const name = String(body.name || "").trim();
        const email = String(body.email || "").trim().toLowerCase();
        const password = String(body.password || "").trim();
        const paypalEmail = String(body.paypal_email || "").trim();

        if (!email || !email.includes("@") || !email.split("@").pop().includes(".")) {
          return err(400, "invalid email");
        }

        const ipHash = await affiliateHashIP(affiliateGetClientIP(request));
        const limited = await affiliateIsRateLimited(
          env.DB,
          `register:${ipHash}`,
          AFFILIATE_REGISTER_MAX_ATTEMPTS,
          AFFILIATE_REGISTER_WINDOW_SECS
        );
        if (limited) {
          return err(429, "too many registration attempts. Please wait an hour.");
        }

        // Auto-generate a password if not provided or too short.
        let pw = password;
        if (!pw || pw.length < 6) {
          const arr = new Uint8Array(16);
          crypto.getRandomValues(arr);
          pw = Array.from(arr).map((b) => b.toString(36)).join("").substring(0, 20);
        }
        const pwHash = await affiliateHashPassword(pw);

        // Idempotent: existing referrer → return existing code, do NOT overwrite hash.
        const existing = await env.DB
          .prepare("SELECT id, referral_code FROM referrers WHERE user_email = ? COLLATE NOCASE")
          .bind(email).first();
        if (existing) {
          return json({
            ok: true,
            referral_code: existing.referral_code,
            referral_link: affiliateReferralLink(existing.referral_code),
            existing: true,
            message: "You are already registered. Here is your existing referral link.",
          });
        }

        const code = await affiliateGenerateUniqueCode(env.DB);
        const now = new Date().toISOString();
        // Default partner_tier='silver' (15%) matches /partners/signup convention.
        await env.DB.prepare(
          `INSERT INTO referrers (user_name, user_email, referral_code, password_hash, paypal_email, created_at, partner_tier, total_sales)
           VALUES (?, ?, ?, ?, ?, ?, 'silver', 0)`
        ).bind(name, email, code, pwHash, paypalEmail, now).run();

        return json({
          ok: true,
          referral_code: code,
          referral_link: affiliateReferralLink(code),
          existing: false,
          message: "Registration successful!",
        });
      }

      // ─────────────────────────────────────────────
      // POST endpoints
      // ─────────────────────────────────────────────

      if (method === "POST" && path === "/referrers/upsert") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email        = String(body.email || "").trim().toLowerCase();
        const name         = String(body.name || "").trim();
        const code         = String(body.code || "").trim().toUpperCase();
        const paypal_email = String(body.paypal_email || "").trim();
        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!code) return err(400, "code required");

        const now = new Date().toISOString();
        try {
          // SPEC C1: NEW upsert rows default to partner_tier='silver' (15%)
          // Existing rows preserve their partner_tier on conflict.
          const res = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at, partner_tier, total_sales)
             VALUES (?, ?, ?, ?, '', ?, 'silver', 0)
             ON CONFLICT(user_email) DO UPDATE SET
               user_name    = CASE WHEN referrers.user_name = '' THEN excluded.user_name ELSE referrers.user_name END,
               paypal_email = CASE WHEN referrers.paypal_email = '' THEN excluded.paypal_email ELSE referrers.paypal_email END
             RETURNING id, user_email, referral_code, user_name, paypal_email, created_at, partner_tier, total_sales`
          ).bind(name, email, code, paypal_email, now).all();
          const row = res.results && res.results[0];
          return json({ ok: true, referrer: row, provisioned: !!row });
        } catch (e) {
          return json({ error: "upsert_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /partners/apply — public partner application (SPEC C2)
      //
      // Replaces Brevo-only flow. Creates partner_applications row with
      // status='pending'. Admin reviews via GET /admin/applications and
      // approves/rejects via /admin/applications/:id/approve|reject.
      //
      // 30-day-use enforcement (CTO Q3): clients table currently lives in
      // purebrain-social D1 (held under domain-isolation rule, May 7).
      // For v1, applications default to 'pending' and admin verifies
      // 30d-use manually during review. Admin can stamp 'needs_30d_use'
      // status with reviewer_override_reason when overriding for partners
      // who paid via different email.
      //
      // Idempotent on email — UNIQUE constraint returns 409 if applied before.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/partners/apply") {
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email = String(body.email || "").trim().toLowerCase();
        const full_name = String(body.full_name || body.name || "").trim();
        const audience_size = Number.isFinite(Number(body.audience_size))
          ? Math.max(0, Math.floor(Number(body.audience_size)))
          : null;
        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!full_name) return err(400, "full_name required");

        // 30-day-use check: deferred to admin review queue (clients table
        // lives in purebrain-social D1, held under domain-isolation rule).
        // Future: extract clients to purebrain-clients D1 and add real lookup
        // that auto-stamps 'needs_30d_use' when applicant lacks 30d client history.
        const status = "pending";

        const application_data = JSON.stringify({
          source: body.source || "partners-page",
          referral_url: body.referral_url || null,
          notes: body.notes || null,
          submitted_user_agent: request.headers.get("user-agent") || null,
        });

        const now = Math.floor(Date.now() / 1000);
        try {
          const res = await env.DB.prepare(
            `INSERT INTO partner_applications (email, full_name, audience_size, application_data, status, applied_at)
             VALUES (?, ?, ?, ?, ?, ?)
             RETURNING id, email, full_name, status, applied_at`
          ).bind(email, full_name, audience_size, application_data, status, now).all();
          const row = res.results && res.results[0];
          return json({ ok: true, application: row });
        } catch (e) {
          // UNIQUE constraint on email → already applied
          const msg = String(e && e.message || e);
          if (msg.includes("UNIQUE")) {
            return err(409, "application_exists");
          }
          return json({ error: "apply_failed", detail: msg }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /admin/applications/:id/approve  (SPEC C2)
      // POST /admin/applications/:id/reject   (CTO Edit #8 — companion route)
      //
      // approve body: { code, paypal_email?, partner_tier?, reviewed_by?, reviewer_override_reason? }
      // reject body:  { rejection_reason, reviewed_by? }
      //
      // approve: creates active referrer row at chosen tier (default 'silver'),
      //          stamps application status='approved' with reviewed_at/by.
      // reject:  stamps application status='rejected' with rejection_reason.
      //
      // Both routes use existing X-Admin-Token auth pattern.
      // ─────────────────────────────────────────────
      const applicationActionMatch = path.match(/^\/admin\/applications\/(\d+)\/(approve|reject)$/);
      if (method === "POST" && applicationActionMatch) {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const appId = Number(applicationActionMatch[1]);
        const action = applicationActionMatch[2];
        const body = (await parseBody(request)) || {};

        const reviewed_by = String(body.reviewed_by || "admin").trim();
        const now = Math.floor(Date.now() / 1000);

        // Load application
        const appRow = await env.DB.prepare(
          `SELECT * FROM partner_applications WHERE id = ?`
        ).bind(appId).first();
        if (!appRow) return err(404, "application not found");
        if (appRow.status !== "pending" && appRow.status !== "needs_30d_use") {
          return err(409, `application already ${appRow.status}`);
        }

        if (action === "reject") {
          const rejection_reason = String(body.rejection_reason || "no reason given").slice(0, 500);
          await env.DB.prepare(
            `UPDATE partner_applications
                SET status = 'rejected', reviewed_at = ?, reviewed_by = ?, rejection_reason = ?
              WHERE id = ?`
          ).bind(now, reviewed_by, rejection_reason, appId).run();
          return json({ ok: true, action: "rejected", id: appId, rejection_reason });
        }

        // approve: create active referrer row, mark application approved
        const code = String(body.code || "").trim().toUpperCase();
        const paypal_email = String(body.paypal_email || appRow.email).trim();
        const partner_tier = String(body.partner_tier || "silver").toLowerCase();
        const reviewer_override_reason = body.reviewer_override_reason
          ? String(body.reviewer_override_reason).slice(0, 500)
          : null;
        if (!code) return err(400, "code required for approval");
        if (!TIER_RATES[partner_tier]) {
          return err(400, `invalid partner_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
        }

        const isoNow = new Date().toISOString();
        try {
          // Create referrer at chosen tier
          const refRes = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at, partner_tier, total_sales)
             VALUES (?, ?, ?, ?, '', ?, ?, 0)
             RETURNING id, user_email, referral_code, user_name, partner_tier`
          ).bind(appRow.full_name, appRow.email, code, paypal_email, isoNow, partner_tier).all();
          const referrer = refRes.results && refRes.results[0];

          // Mark application approved
          await env.DB.prepare(
            `UPDATE partner_applications
                SET status = 'approved', reviewed_at = ?, reviewed_by = ?, reviewer_override_reason = ?
              WHERE id = ?`
          ).bind(now, reviewed_by, reviewer_override_reason, appId).run();

          return json({
            ok: true,
            action: "approved",
            id: appId,
            referrer,
            tier_rate: rateForTier(partner_tier),
          });
        } catch (e) {
          return json({ error: "approve_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /partners/signup — direct admin signup (SPEC C1)
      // Default partner_tier='silver' (15%), explicit alternative tiers allowed.
      // (Public application path is /partners/apply; this is admin-direct provisioning.)
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/partners/signup") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email        = String(body.email || "").trim().toLowerCase();
        const name         = String(body.name || "").trim();
        const code         = String(body.code || "").trim().toUpperCase();
        const paypal_email = String(body.paypal_email || "").trim();
        // SPEC C1: default 'silver' (15%); admin can override
        const partner_tier = String(body.partner_tier || "silver").toLowerCase();

        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!code) return err(400, "code required");
        if (!TIER_RATES[partner_tier]) {
          return err(400, `invalid partner_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
        }

        const now = new Date().toISOString();
        try {
          const res = await env.DB.prepare(
            `INSERT INTO referrers (user_name, user_email, referral_code, paypal_email, password_hash, created_at, partner_tier, total_sales)
             VALUES (?, ?, ?, ?, '', ?, ?, 0)
             RETURNING id, user_email, referral_code, user_name, paypal_email, created_at, partner_tier, total_sales`
          ).bind(name, email, code, paypal_email, now, partner_tier).all();
          const row = res.results && res.results[0];
          return json({
            ok: true,
            referrer: row,
            tier_rate: rateForTier(partner_tier),
          });
        } catch (e) {
          return json({ error: "signup_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // ─────────────────────────────────────────────
      // POST /referrals/complete (SPEC B2 + CTO Q1)
      //
      // Two modes:
      //   1) Admin mode (legacy): { referral_id } → mark existing referral completed.
      //   2) Public mode (B2):    { pb_ref, payment_id, customer_email, ... }
      //      → INSERT OR IGNORE pending row (idempotent via UNIQUE INDEX
      //        uniq_referrals_pbref_payment on (pb_ref, payment_id)).
      //      Called from PayPal onApprove handlers on /awakened/, /insiders/,
      //      /partnered/, /unified/, homepage, home-test variants.
      //      No admin token required — idempotency from UNIQUE INDEX prevents abuse.
      //
      // Per CTO Q1: pending row created here (at payment-page onApprove time),
      // NOT at click-track time. Keeps referral_clicks separate from paid intent.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/referrals/complete") {
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        // Mode 1: admin legacy path — mark existing referral completed by id
        if (body.referral_id !== undefined && !body.pb_ref) {
          { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
          const referral_id = body.referral_id;
          const now = new Date().toISOString();
          const res = await env.DB.prepare(
            `UPDATE referrals SET status = 'completed', completed_at = ? WHERE id = ? RETURNING *`
          ).bind(now, referral_id).all();
          const row = res.results && res.results[0];
          if (!row) return err(404, "referral not found");
          return json({ ok: true, referral: row, mode: "admin_complete" });
        }

        // Mode 2: public payment-page POST — INSERT OR IGNORE pending row
        const pb_ref = String(body.pb_ref || body.referral_code || "").trim().toUpperCase();
        const payment_id = String(body.payment_id || body.order_id || "").trim();
        const customer_email = String(body.customer_email || body.email || "").trim().toLowerCase();
        const referred_name = String(body.referred_name || body.name || customer_email).trim();

        if (!pb_ref) return err(400, "pb_ref required");
        if (!payment_id) return err(400, "payment_id required");
        if (!customer_email || !customer_email.includes("@")) return err(400, "customer_email required");

        // Look up referrer by code (must exist for attribution)
        const referrer = await env.DB.prepare(
          `SELECT id, referral_code, partner_tier FROM referrers WHERE referral_code = ? COLLATE NOCASE`
        ).bind(pb_ref).first();
        if (!referrer) {
          // Unknown ref code — webhook can still attribute via customer_email separately.
          return json({ ok: false, error: "unknown_referral_code", pb_ref }, { status: 404 });
        }

        const now = new Date().toISOString();

        // INSERT OR IGNORE: UNIQUE INDEX uniq_referrals_pbref_payment makes this idempotent.
        // CTO Edit #4 / SPEC §3: page reload, network retry, double-click all collapse to 1 row.
        try {
          const insertRes = await env.DB.prepare(
            `INSERT OR IGNORE INTO referrals
                (referrer_id, referred_email, referred_name, status, created_at, pb_ref, payment_id)
             VALUES (?, ?, ?, 'pending', ?, ?, ?)
             RETURNING *`
          ).bind(
            referrer.id, customer_email, referred_name, now, pb_ref, payment_id
          ).all();
          const row = insertRes.results && insertRes.results[0];

          if (row) {
            return json({ ok: true, referral: row, idempotent: false, mode: "pending_create" });
          }

          // INSERT IGNORED → row already exists for (pb_ref, payment_id)
          const existing = await env.DB.prepare(
            `SELECT * FROM referrals WHERE pb_ref = ? AND payment_id = ? LIMIT 1`
          ).bind(pb_ref, payment_id).first();
          return json({ ok: true, referral: existing, idempotent: true, mode: "pending_create" });
        } catch (e) {
          return json({ error: "complete_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      if (method === "POST" && path === "/commission_payments") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const {
          referrer_id, referral_id, payer_email, order_id,
          payment_amount,
          // Legacy: caller can pass pre-computed values (paypal-webhook backwards-compat)
          commission_rate: legacyRate, commission_value: legacyValue, tier: legacyTier,
          // New: caller passes plan_id; Worker computes rate via TIER_RATES + Support Tier
          plan_id,
        } = body;
        if (!referrer_id || !referral_id) return err(400, "referrer_id and referral_id required");

        // Look up partner_tier for tier_at_write audit + rate computation
        const refRow = await env.DB.prepare(
          `SELECT partner_tier FROM referrers WHERE id = ?`
        ).bind(referrer_id).first();
        const partner_tier = (refRow && refRow.partner_tier) || legacyTier || "silver";

        // SPEC A3 (CTO Edit #1): commission = paymentAmount * rate. NO $35 deduction here.
        // The $35 ops fee is taken in tools/paypal_auto_split.py at payout time.
        // SPEC E1: if plan_id is in SUPPORT_TIER_PLAN_IDS, override to 25%.
        let commission_value, commission_rate, commission_source;
        if (legacyValue !== undefined && legacyRate !== undefined) {
          // Legacy path: caller pre-computed (paypal-webhook with custom logic)
          commission_value = Number(legacyValue);
          commission_rate  = Number(legacyRate);
          commission_source = isSupportTierPlan(plan_id, env) ? "support_tier" : "standard";
        } else {
          // New path: Worker computes from payment_amount + partner_tier (+ plan_id)
          const computed = computeCommission({
            paymentAmount: payment_amount,
            partnerTier: partner_tier,
            planId: plan_id,
            env,
          });
          commission_value = computed.value;
          commission_rate  = computed.rate;
          commission_source = computed.source;
        }

        // CTO Edit #2: tier_at_write MUST be set on every commission_payments INSERT
        // for safe idempotent retroactive recalc.
        const tier_at_write = String(partner_tier);

        const now = new Date().toISOString();
        const res = await env.DB.prepare(
          `INSERT INTO commission_payments
             (referrer_id, referral_id, payer_email, order_id,
              payment_amount, commission_rate, commission_value, tier,
              tier_at_write, commission_source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           RETURNING *`
        ).bind(
          referrer_id, referral_id,
          payer_email || "", order_id || "",
          Number(payment_amount) || 0,
          commission_rate, commission_value,
          tier_at_write, // legacy `tier` col mirrors tier_at_write for backwards compat
          tier_at_write,
          commission_source,
          now
        ).all();
        const row = res.results && res.results[0];
        return json({ ok: true, payment: row });
      }

      // ─────────────────────────────────────────────
      // POST /admin/payments/manual — admin records a commission that didn't auto-attribute
      // (CTO 2026-05-12 Track B.3)
      //
      // Body: { referral_id, payment_id, payment_amount, commission_rate?, note?, tier_at_write? }
      //
      // Behavior:
      //   - Looks up referral → referrer → partner_tier.
      //   - commission_value = payment_amount * rate (server-authoritative).
      //   - Idempotent via check-then-insert on (referral_id, order_id) — no DB UNIQUE.
      //   - Stores admin payment_id in order_id column (which is the closest
      //     existing identifier on commission_payments per current schema).
      //   - Returns existing row if duplicate detected (idempotent_skip=true).
      //   - Marks referrals.status='completed' if currently 'pending'.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/admin/payments/manual") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const referral_id     = Number(body.referral_id);
        const payment_id      = String(body.payment_id || "").trim();
        const payment_amount  = Number(body.payment_amount);
        const note            = String(body.note || "").trim().slice(0, 500);
        const overrideTierRaw = body.tier_at_write ? String(body.tier_at_write).toLowerCase().trim() : "";
        const overrideRate    = body.commission_rate !== undefined ? Number(body.commission_rate) : null;

        if (!Number.isFinite(referral_id) || referral_id <= 0) return err(400, "invalid referral_id");
        if (!payment_id) return err(400, "payment_id required");
        if (!Number.isFinite(payment_amount) || payment_amount < 0) return err(400, "invalid payment_amount");

        // Look up referral + referrer
        const refRow = await env.DB.prepare(
          `SELECT r.referrer_id, r.status AS referral_status, r.referred_email,
                  rr.partner_tier
             FROM referrals r
             LEFT JOIN referrers rr ON rr.id = r.referrer_id
            WHERE r.id = ?`
        ).bind(referral_id).first();
        if (!refRow) return err(404, "referral not found");

        const referrer_id = refRow.referrer_id;
        const partner_tier = overrideTierRaw || refRow.partner_tier || "silver";
        const tier_at_write = String(partner_tier);

        // Server-authoritative rate (allow admin override; default to tier rate)
        const commission_rate = Number.isFinite(overrideRate) && overrideRate > 0
          ? overrideRate
          : rateForTier(partner_tier);
        const commission_value = Math.round((payment_amount * commission_rate) * 100) / 100;

        // Idempotency check: (referral_id, order_id) where order_id = payment_id.
        // commission_payments has no UNIQUE on (referral_id, order_id) in current
        // schema, so check-then-insert is the safest path.
        const existing = await env.DB.prepare(
          `SELECT * FROM commission_payments
            WHERE referral_id = ? AND order_id = ?
            LIMIT 1`
        ).bind(referral_id, payment_id).first();
        if (existing) {
          return json({
            ok: true,
            payment: existing,
            idempotent_skip: true,
            message: "duplicate (referral_id, payment_id) — returning existing row",
          });
        }

        const now = new Date().toISOString();
        const audit_payer = (refRow.referred_email || "").trim();
        const audit_order = payment_id + (note ? ` | note:${note}` : "");

        const res = await env.DB.prepare(
          `INSERT INTO commission_payments
             (referrer_id, referral_id, payer_email, order_id,
              payment_amount, commission_rate, commission_value, tier,
              tier_at_write, commission_source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           RETURNING *`
        ).bind(
          referrer_id, referral_id,
          audit_payer, audit_order,
          Number(payment_amount) || 0,
          commission_rate, commission_value,
          tier_at_write,
          tier_at_write,
          "standard",
          now
        ).all();

        // Mark referral completed if currently pending
        if (refRow.referral_status === "pending") {
          try {
            await env.DB.prepare(
              `UPDATE referrals SET status='completed' WHERE id = ? AND status='pending'`
            ).bind(referral_id).run();
          } catch (_e) { /* non-fatal */ }
        }

        const row = res.results && res.results[0];
        console.log(`[referrals-api] manual payment recorded: referral_id=${referral_id} payment_id=${payment_id} value=${commission_value}`);
        return json({ ok: true, payment: row, idempotent_skip: false });
      }

      // ─────────────────────────────────────────────
      // POST /internal/complete-by-email — paypal-webhook Service Binding attribution
      // (CTO 2026-05-12 Track E.1)
      //
      // Auth: INTERNAL_BINDING_SECRET header (defense-in-depth even though
      // Service Binding traffic is in-CF). Per
      // feedback_purebrain_social_never_touches_referral_or_clients.md
      // rigor — secret-gate every internal hop.
      //
      // Body: { customer_email | email, subscription_id, payment_amount, plan_id?, event_id?, event_time? }
      //
      // Behavior:
      //   1. Find latest pending referral by referred_email.
      //   2. If found → write commission via same logic as POST /commission_payments
      //      (respects tier_at_write + Support Tier detect), mark referral completed.
      //   3. If not found → return 200 with {matched: false} (no retry storm).
      //   4. Idempotent: dedupe on (referral_id, order_id=subscription_id).
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/internal/complete-by-email") {
        if (!checkInternalBinding(request, env)) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const email = String(body.customer_email || body.email || "").trim().toLowerCase();
        const subscription_id = String(body.subscription_id || body.payment_id || "").trim();
        const payment_amount = Number(body.payment_amount) || 0;
        const plan_id = body.plan_id ? String(body.plan_id) : null;
        const event_id = body.event_id ? String(body.event_id) : null;
        const event_time = body.event_time ? String(body.event_time) : null;

        if (!email || !email.includes("@")) return err(400, "invalid email");
        if (!subscription_id) return err(400, "subscription_id (or payment_id) required");

        // Find the latest pending referral for this email.
        // Excludes synthetic 'paypal_*@pending' rejected placeholders.
        const refRow = await env.DB.prepare(
          `SELECT r.id, r.referrer_id, rr.partner_tier
             FROM referrals r
             LEFT JOIN referrers rr ON rr.id = r.referrer_id
            WHERE LOWER(r.referred_email) = ?
              AND r.status = 'pending'
              AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
            ORDER BY r.created_at DESC
            LIMIT 1`
        ).bind(email).first();

        if (!refRow) {
          console.log(`[referrals-api] /internal/complete-by-email no pending referral for ${email}`);
          return json({ matched: false, email, message: "no pending referral" });
        }

        const partner_tier = refRow.partner_tier || "silver";
        const tier_at_write = String(partner_tier);

        // Idempotency: detect prior commission for this (referral_id, subscription_id)
        const existing = await env.DB.prepare(
          `SELECT * FROM commission_payments
            WHERE referral_id = ? AND order_id = ?
            LIMIT 1`
        ).bind(refRow.id, subscription_id).first();
        if (existing) {
          // Already attributed — still mark referral completed if needed.
          try {
            await env.DB.prepare(
              `UPDATE referrals SET status='completed' WHERE id = ? AND status='pending'`
            ).bind(refRow.id).run();
          } catch (_e) { /* non-fatal */ }
          return json({
            matched: true, idempotent_skip: true,
            referral_id: refRow.id, payment: existing,
          });
        }

        // Compute commission (handles Support Tier override via plan_id)
        const computed = computeCommission({
          paymentAmount: payment_amount,
          partnerTier: partner_tier,
          planId: plan_id,
          env,
        });

        const now = (event_time && /^\d{4}-\d{2}-\d{2}T/.test(event_time))
          ? event_time
          : new Date().toISOString();
        const order_id_audit = subscription_id + (event_id ? `|evt:${event_id}` : "");

        const res = await env.DB.prepare(
          `INSERT INTO commission_payments
             (referrer_id, referral_id, payer_email, order_id,
              payment_amount, commission_rate, commission_value, tier,
              tier_at_write, commission_source, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           RETURNING *`
        ).bind(
          refRow.referrer_id, refRow.id,
          email, order_id_audit,
          payment_amount,
          computed.rate, computed.value,
          tier_at_write,
          tier_at_write,
          computed.source,
          now
        ).all();

        // Mark referral completed
        try {
          await env.DB.prepare(
            `UPDATE referrals SET status='completed' WHERE id = ? AND status='pending'`
          ).bind(refRow.id).run();
        } catch (_e) { /* non-fatal */ }

        const row = res.results && res.results[0];
        console.log(`[referrals-api] /internal/complete-by-email attribution: email=${email} referral_id=${refRow.id} subscription_id=${subscription_id} value=${computed.value}`);
        return json({
          matched: true,
          idempotent_skip: false,
          referral_id: refRow.id,
          referrer_id: refRow.referrer_id,
          payment: row,
        });
      }

      // ─────────────────────────────────────────────
      // POST /internal/recalc-subscription — paypal-webhook commission recalc on plan change/refund
      // (CTO 2026-05-12 Track E.2)
      //
      // Body: { subscription_id, event_type?, old_amount?, new_amount?, payment_amount?, event_id?, changed_at? }
      //
      // Behavior:
      //   - Looks up commission_payments rows where order_id contains subscription_id.
      //     (No paypal_subscription_id column in current schema — match via order_id prefix.)
      //   - For RENEWED / new payment event_type → write a NEW commission row using
      //     current referrer tier (separate row per renewal).
      //   - For REFUNDED → mark existing rows' commission_source='refunded' (note: this
      //     uses commission_source CHECK constraint which does NOT include 'refunded' —
      //     so we instead record a NEGATIVE commission row as the audit trail and let
      //     admin reconcile via /admin/payments/manual). Safe, no schema migration.
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/internal/recalc-subscription") {
        if (!checkInternalBinding(request, env)) return err(401, "unauthorized");
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const subscription_id = String(body.subscription_id || "").trim();
        const event_type = String(body.event_type || "BILLING.SUBSCRIPTION.UPDATED").trim();
        const payment_amount = Number(body.payment_amount || body.new_amount || 0);
        const old_amount = Number(body.old_amount || 0);
        const event_id = body.event_id ? String(body.event_id) : null;

        if (!subscription_id) return err(400, "subscription_id required");

        // Find commission rows matching this subscription_id via order_id pattern.
        // order_id was written as "<subscription_id>|evt:<eid>" by /internal/complete-by-email.
        const { results: priorRows } = await env.DB.prepare(
          `SELECT cp.*, r.partner_tier AS current_tier
             FROM commission_payments cp
             LEFT JOIN referrers r ON r.id = cp.referrer_id
            WHERE cp.order_id = ? OR cp.order_id LIKE ?
            ORDER BY cp.created_at DESC`
        ).bind(subscription_id, subscription_id + "|%").all();

        if (!priorRows || priorRows.length === 0) {
          console.log(`[referrals-api] /internal/recalc-subscription no prior commissions for ${subscription_id}`);
          return json({ updated: 0, matched: false, subscription_id });
        }

        const isRefund = /REFUND/i.test(event_type);
        const isRenewal = /PAYMENT\.COMPLETED|RENEW|RECURRING/i.test(event_type)
                         || (payment_amount > 0 && !isRefund);

        const referrer_id = priorRows[0].referrer_id;
        const referral_id = priorRows[0].referral_id;
        const partner_tier = priorRows[0].current_tier || priorRows[0].tier_at_write || "silver";
        const tier_at_write = String(partner_tier);
        const now = new Date().toISOString();

        if (isRefund) {
          // Negative audit row (commission_source='standard' to satisfy CHECK).
          // Admin reconciles via /admin/payments/manual or direct D1 for full clawback.
          const refundAmount = -Math.abs(payment_amount || priorRows[0].payment_amount || 0);
          const refundCommission = -Math.abs(priorRows[0].commission_value || 0);
          const order_id_audit = subscription_id + (event_id ? `|refund:${event_id}` : "|refund");
          const res = await env.DB.prepare(
            `INSERT INTO commission_payments
               (referrer_id, referral_id, payer_email, order_id,
                payment_amount, commission_rate, commission_value, tier,
                tier_at_write, commission_source, created_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             RETURNING *`
          ).bind(
            referrer_id, referral_id,
            priorRows[0].payer_email || "",
            order_id_audit,
            refundAmount,
            priorRows[0].commission_rate || 0,
            refundCommission,
            tier_at_write, tier_at_write,
            "standard", now
          ).all();
          console.log(`[referrals-api] /internal/recalc-subscription refund recorded: subscription_id=${subscription_id} amount=${refundCommission}`);
          return json({
            updated: 1, action: "refund_recorded",
            subscription_id, payment: (res.results && res.results[0]) || null,
          });
        }

        if (isRenewal && payment_amount > 0) {
          // Idempotency: skip if we already wrote a renewal for this event_id
          if (event_id) {
            const dup = await env.DB.prepare(
              `SELECT * FROM commission_payments
                WHERE referral_id = ? AND order_id LIKE ?
                LIMIT 1`
            ).bind(referral_id, `%|evt:${event_id}%`).first();
            if (dup) {
              return json({
                updated: 0, action: "idempotent_skip",
                subscription_id, payment: dup,
              });
            }
          }
          const computed = computeCommission({
            paymentAmount: payment_amount,
            partnerTier: partner_tier,
            planId: null,
            env,
          });
          const order_id_audit = subscription_id + (event_id ? `|evt:${event_id}` : `|renewal:${Date.now()}`);
          const res = await env.DB.prepare(
            `INSERT INTO commission_payments
               (referrer_id, referral_id, payer_email, order_id,
                payment_amount, commission_rate, commission_value, tier,
                tier_at_write, commission_source, created_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             RETURNING *`
          ).bind(
            referrer_id, referral_id,
            priorRows[0].payer_email || "",
            order_id_audit,
            payment_amount,
            computed.rate, computed.value,
            tier_at_write, tier_at_write,
            computed.source, now
          ).all();
          console.log(`[referrals-api] /internal/recalc-subscription renewal recorded: subscription_id=${subscription_id} value=${computed.value}`);
          return json({
            updated: 1, action: "renewal_recorded",
            subscription_id, payment: (res.results && res.results[0]) || null,
          });
        }

        // Plan change with no immediate payment: just log; future PAYMENT.COMPLETED
        // event will trigger the renewal write path above.
        console.log(`[referrals-api] /internal/recalc-subscription plan_change_acknowledged: subscription_id=${subscription_id} old=${old_amount} new=${payment_amount}`);
        return json({
          updated: 0, action: "plan_change_acknowledged",
          subscription_id, old_amount, new_amount: payment_amount,
        });
      }

      // ─────────────────────────────────────────────
      // POST /payouts/request — partner-self payout request (SPEC C4)
      //
      // PUBLIC endpoint. Identity gate: { partner_id, paypal_email }
      //   — must match referrers.referral_code + referrers.paypal_email.
      //
      // Body: { partner_id, amount, paypal_email }
      //
      // Constraints:
      //   - amount >= 50 (DB CHECK on payout_requests_v2 enforces this)
      //   - amount must not exceed (sum of commissions earned) - (sum of approved/paid payouts)
      //   - partner_id (referral_code) must exist
      //   - paypal_email must match referrer record (no spoofing)
      //
      // Admin approval (manual, via /admin/payout/mark-paid + paypal_auto_split.py)
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/payouts/request") {
        // Public — identity verified by partner_id + paypal_email match
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const partner_id = String(body.partner_id || body.referral_code || "").trim().toUpperCase();
        const amount = Number(body.amount || 0);
        const paypal_email = String(body.paypal_email || "").trim();

        if (!partner_id) return err(400, "partner_id required");
        if (!paypal_email || !paypal_email.includes("@")) return err(400, "paypal_email required");
        if (!Number.isFinite(amount) || amount < 50) {
          return err(400, "amount must be >= 50");
        }

        // Identity gate: partner exists + paypal_email matches
        const referrer = await env.DB.prepare(
          `SELECT id, referral_code, paypal_email FROM referrers WHERE referral_code = ? COLLATE NOCASE`
        ).bind(partner_id).first();
        if (!referrer) return err(404, "partner not found");
        if (referrer.paypal_email && referrer.paypal_email.toLowerCase() !== paypal_email.toLowerCase()) {
          return err(403, "paypal_email_mismatch");
        }

        // Verify partner has at least `amount` in unpaid commission earnings
        const earningsRow = await env.DB.prepare(
          `SELECT COALESCE(SUM(commission_value), 0) AS earned
             FROM commission_payments
            WHERE referrer_id = ?`
        ).bind(referrer.id).first();
        const paidRow = await env.DB.prepare(
          `SELECT COALESCE(SUM(amount), 0) AS paid
             FROM payout_requests_v2
            WHERE partner_id = ? COLLATE NOCASE
              AND status IN ('approved', 'paid')`
        ).bind(partner_id).first();
        const available = Math.round(((earningsRow.earned || 0) - (paidRow.paid || 0)) * 100) / 100;
        if (amount > available) {
          return err(400, `requested amount ${amount} exceeds available ${available.toFixed(2)}`);
        }

        const now = Math.floor(Date.now() / 1000);
        try {
          // DB CHECK constraint amount >= 50 enforces $50 min
          // CHECK payout_method = 'paypal' enforces v1 PayPal-only
          const res = await env.DB.prepare(
            `INSERT INTO payout_requests_v2
               (partner_id, amount, payout_method, paypal_email, status, requested_at)
             VALUES (?, ?, 'paypal', ?, 'requested', ?)
             RETURNING *`
          ).bind(partner_id, amount, paypal_email, now).all();
          const row = res.results && res.results[0];
          return json({
            ok: true,
            payout_request: row,
            available_after: Math.round((available - amount) * 100) / 100,
          });
        } catch (e) {
          return json({ error: "payout_request_failed", detail: String(e && e.message || e) }, { status: 500 });
        }
      }

      // POST /admin/payout/mark-paid — mark a payout request as paid
      if (method === "POST" && path === "/admin/payout/mark-paid") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { payout_id, notes } = body;
        if (!payout_id) return err(400, "payout_id required");

        const now = new Date().toISOString();
        const res = await env.DB.prepare(
          `UPDATE payout_requests SET status = 'paid', paid_at = ?, notes = COALESCE(?, notes) WHERE id = ? RETURNING *`
        ).bind(now, notes || null, payout_id).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "payout request not found");
        return json({ ok: true, payout: row });
      }

      // ─────────────────────────────────────────────
      // POST /admin/recalc-tier — retroactive rate recalc (SPEC C3 / CTO Q4)
      //
      // Strategy: idempotent recalc using tier_at_write column.
      // Only rows where tier_at_write != target_tier get updated → safe
      // to call repeatedly; converges to consistent state.
      //
      // Body: {
      //   partner_id: "PB-XXXX",        — referral_code (required)
      //   trigger_event: "100_referrals" | "1000_referrals" | "manual"  (default "manual")
      //   force_tier:    "silver"|"gold"|"platinum"|"elite"  (optional override of milestone derivation)
      // }
      //
      // Behavior:
      //   - Computes target tier (force_tier > milestoneTier(total_sales) > current)
      //   - Updates referrers.partner_tier
      //   - Recalculates commission_payments rows where tier_at_write != target_tier
      //     AND commission_source != 'support_tier' (Support Tier locked at 25%)
      //   - Chunked at LIMIT 200 per call (CF Worker 30s CPU limit)
      //   - Returns more=true if rows still need recalc → caller re-invokes
      //   - Logs to rate_adjustments only on chunks that actually recalculated rows
      // ─────────────────────────────────────────────
      if (method === "POST" && path === "/admin/recalc-tier") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const partner_id = String(body.partner_id || "").trim().toUpperCase();
        const force_tier = body.force_tier ? String(body.force_tier).toLowerCase() : null;
        const trigger = String(body.trigger_event || "manual");

        if (!partner_id) return err(400, "partner_id required");
        if (!["100_referrals", "1000_referrals", "manual"].includes(trigger)) {
          return err(400, "invalid trigger_event");
        }
        if (force_tier && !TIER_RATES[force_tier]) {
          return err(400, `invalid force_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
        }

        // Load current partner state
        const referrer = await env.DB.prepare(
          `SELECT id, referral_code, partner_tier, total_sales FROM referrers WHERE referral_code = ? COLLATE NOCASE`
        ).bind(partner_id).first();
        if (!referrer) return err(404, "partner not found");

        const oldTier = String(referrer.partner_tier || "silver").toLowerCase();
        const computedTier = milestoneTier(referrer.total_sales);
        const newTier = String(force_tier || computedTier || oldTier).toLowerCase();
        if (!TIER_RATES[newTier]) return err(400, `invalid tier ${newTier}`);

        const oldRate = rateForTier(oldTier);
        const newRate = rateForTier(newTier);

        // No-op if tier unchanged AND no rows need recalc
        if (newTier === oldTier) {
          // Still check if any rows have stale tier_at_write
          const staleRow = await env.DB.prepare(
            `SELECT COUNT(*) AS c FROM commission_payments
              WHERE referrer_id = ?
                AND (tier_at_write IS NULL OR tier_at_write != ?)
                AND (commission_source IS NULL OR commission_source != 'support_tier')`
          ).bind(referrer.id, newTier).first();
          if ((staleRow.c || 0) === 0) {
            return json({ ok: true, no_change: true, tier: newTier, rate: newRate });
          }
        }

        // Update partner_tier on referrer (idempotent — same value if no change)
        await env.DB.prepare(
          `UPDATE referrers SET partner_tier = ? WHERE id = ?`
        ).bind(newTier, referrer.id).run();

        // Chunked recalc: only rows where tier_at_write != newTier
        // CTO §1.3: tier_at_write is source of truth for safe idempotent recalc.
        // Skip support_tier rows — those are locked at 25% regardless of partner tier.
        const CHUNK = 200;
        const { results: rows } = await env.DB.prepare(
          `SELECT id, payment_amount, commission_value, tier_at_write
             FROM commission_payments
            WHERE referrer_id = ?
              AND (tier_at_write IS NULL OR tier_at_write != ?)
              AND (commission_source IS NULL OR commission_source != 'support_tier')
            ORDER BY id ASC
            LIMIT ?`
        ).bind(referrer.id, newTier, CHUNK).all();

        let recalculated = 0;
        let dollarDelta = 0;
        for (const r of rows || []) {
          const amt = Number(r.payment_amount) || 0;
          const oldVal = Number(r.commission_value) || 0;
          const newVal = Math.round(amt * newRate * 100) / 100;
          await env.DB.prepare(
            `UPDATE commission_payments
                SET commission_value  = ?,
                    commission_rate   = ?,
                    tier              = ?,
                    tier_at_write     = ?,
                    commission_source = 'milestone_recalc'
              WHERE id = ?`
          ).bind(newVal, newRate, newTier, newTier, r.id).run();
          recalculated += 1;
          dollarDelta += (newVal - oldVal);
        }

        // Check whether more rows remain
        const moreRow = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM commission_payments
            WHERE referrer_id = ?
              AND (tier_at_write IS NULL OR tier_at_write != ?)
              AND (commission_source IS NULL OR commission_source != 'support_tier')`
        ).bind(referrer.id, newTier).first();
        const more = (moreRow.c || 0) > 0;

        // Audit log: rate_adjustments (logged per chunk that recalculated)
        const dollarsRecalculated = Math.round(Math.abs(dollarDelta) * 100) / 100;
        if (recalculated > 0) {
          await env.DB.prepare(
            `INSERT INTO rate_adjustments
               (partner_id, old_rate, new_rate, trigger_event, affected_commission_count, total_dollars_recalculated, created_at)
             VALUES (?, ?, ?, ?, ?, ?, ?)`
          ).bind(
            partner_id, oldRate, newRate, trigger,
            recalculated, dollarsRecalculated,
            Math.floor(Date.now() / 1000)
          ).run();
        }

        return json({
          ok: true,
          partner_id,
          old_tier: oldTier, new_tier: newTier,
          old_rate: oldRate, new_rate: newRate,
          recalculated,
          dollar_delta: Math.round(dollarDelta * 100) / 100,
          chunk_size: CHUNK,
          more,
        });
      }

      // POST /admin/referral/assign — manually assign a client to a referrer
      // CONSTITUTIONAL: one referred_email = one referral, ever (Jared rule, CTO 2026-05-12).
      // Structurally enforced by UNIQUE INDEX uniq_referrals_referred_email (migration 0003).
      // Reassignment to a different referrer is BLOCKED. Splits handled separately in
      // elite settings.
      //
      // Accepts both naming conventions:
      //   { referrer_id, referred_email, referred_name }           — original
      //   { referral_code, client_email, client_name }             — admin/referrals frontend
      //
      // On successful new INSERT, triggers retroactive commission backfill via
      // CLIENTS_API for any past payments by this client. Backfill failure does
      // NOT block the assignment; surfaces in response.retroactive for retry via
      // POST /admin/referral/:id/retro-backfill.
      if (method === "POST" && path === "/admin/referral/assign") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        let referrer_id = body.referrer_id;
        const referral_code = body.referral_code;
        const referred_email_raw = body.referred_email || body.client_email;
        const referred_name = body.referred_name || body.client_name;

        if (!referred_email_raw) return err(400, "referred_email or client_email required");
        const referred_email = String(referred_email_raw).trim().toLowerCase();

        // Resolve referral_code → referrer_id when only the human-readable code is supplied
        if (!referrer_id && referral_code) {
          const lookup = await env.DB
            .prepare("SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE")
            .bind(String(referral_code).trim()).first();
          if (!lookup) return err(404, "referrer not found for code: " + referral_code);
          referrer_id = lookup.id;
        }
        if (!referrer_id) return err(400, "referrer_id or referral_code required");

        // Pre-INSERT idempotency check — friendly 409 BEFORE relying on UNIQUE INDEX.
        // The UNIQUE INDEX (migration 0003) is the structural guarantee; this query
        // surfaces a clear error message with existing referrer info.
        const existing = await env.DB.prepare(
          `SELECT r.id, r.referrer_id, r.status, r.created_at,
                  rr.user_name AS existing_referrer_name,
                  rr.referral_code AS existing_referrer_code
             FROM referrals r
             LEFT JOIN referrers rr ON rr.id = r.referrer_id
            WHERE LOWER(r.referred_email) = ?
              AND r.referred_email NOT LIKE 'paypal_%@pending'
            LIMIT 1`
        ).bind(referred_email).first();

        if (existing) {
          return json({
            ok: false,
            error: "already_assigned",
            message: "This client is already assigned and cannot be reassigned. Splits are handled separately in elite settings.",
            existing_referral_id: existing.id,
            existing_referrer_id: existing.referrer_id,
            existing_referrer_code: existing.existing_referrer_code,
            existing_referrer_name: existing.existing_referrer_name,
            existing_status: existing.status,
            existing_created_at: existing.created_at,
          }, { status: 409 });
        }

        const now = new Date().toISOString();
        let row;
        try {
          const res = await env.DB.prepare(
            `INSERT INTO referrals (referrer_id, referred_email, referred_name, status, created_at)
             VALUES (?, ?, ?, 'pending', ?)
             RETURNING *`
          ).bind(referrer_id, referred_email, String(referred_name || "").trim(), now).all();
          row = res.results && res.results[0];
        } catch (e) {
          // Belt-and-suspenders: pre-check race-loses to UNIQUE INDEX → SQLite returns
          // "UNIQUE constraint failed" → map to 409.
          const msg = String(e && e.message || e);
          if (/UNIQUE constraint failed.*referred_email/i.test(msg)) {
            return json({
              ok: false,
              error: "already_assigned",
              message: "Race-condition duplicate blocked by UNIQUE INDEX. Refresh and retry.",
            }, { status: 409 });
          }
          throw e;
        }

        // Retroactive commission backfill (Bug 2). MUST NOT block assignment.
        let retro_summary;
        try {
          retro_summary = await backfillRetroactiveCommissions(env, {
            referral_id: row.id,
            referrer_id,
            referred_email,
          });
        } catch (e) {
          retro_summary = {
            ok: false,
            error: `backfill_throw:${String(e && e.message || e).slice(0, 80)}`,
            commissions_written: 0,
          };
        }

        return json({ ok: true, referral: row, retroactive: retro_summary });
      }

      // POST /admin/referral/:id/retro-backfill — retry retroactive commission backfill.
      // CTO 2026-05-12 Bug 2 companion endpoint. Idempotent: existing commission rows
      // (matched by referral_id, order_id) are skipped. Useful when CLIENTS_API was
      // briefly unavailable during the original assign call, OR when clients-api ships
      // /internal/client-payments AFTER the assign happened.
      {
        const retroMatch = path.match(/^\/admin\/referral\/(\d+)\/retro-backfill$/);
        if (method === "POST" && retroMatch) {
          { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
          const referral_id = Number(retroMatch[1]);
          if (!Number.isFinite(referral_id) || referral_id <= 0) return err(400, "invalid referral_id");

          const refRow = await env.DB.prepare(
            `SELECT id, referrer_id, referred_email FROM referrals WHERE id = ?`
          ).bind(referral_id).first();
          if (!refRow) return err(404, "referral not found");
          if (!refRow.referred_email) return err(400, "referral has no referred_email");

          let retro_summary;
          try {
            retro_summary = await backfillRetroactiveCommissions(env, {
              referral_id: refRow.id,
              referrer_id: refRow.referrer_id,
              referred_email: refRow.referred_email,
            });
          } catch (e) {
            retro_summary = {
              ok: false,
              error: `backfill_throw:${String(e && e.message || e).slice(0, 80)}`,
              commissions_written: 0,
            };
          }
          return json({ ok: true, referral_id, retroactive: retro_summary });
        }
      }

      // Bug 3 (CTO 2026-05-12): splits-save 404 routing fix.
      // Frontend (admin/referrals/index.html line 1940-1951) tries:
      //   PATCH /api/admin/partners/{id}/splits
      //   PUT   /api/admin/partners/{id}/splits
      //   PUT   /api/admin/partners/{id}    (with split_config in body)
      // Portal-proxy strips /api/admin → /admin so we receive:
      //   PATCH /admin/partners/{id}/splits
      //   PUT   /admin/partners/{id}/splits
      //   PUT   /admin/partners/{id}
      // All three are forwarded here to the existing PUT /admin/affiliate/update
      // logic, but constrained to split_config-only updates (no tier mutation
      // via this path — keeps the surface narrow).
      {
        const splitsMatch = path.match(/^\/admin\/partners\/(\d+)(\/splits)?$/);
        if (splitsMatch && (method === "PATCH" || method === "PUT")) {
          { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
          const referrer_id = Number(splitsMatch[1]);
          if (!Number.isFinite(referrer_id) || referrer_id <= 0) return err(400, "invalid partner id");

          const body = await parseBody(request);
          if (!body) return err(400, "invalid json");
          if (body.split_config === undefined) return err(400, "split_config required");

          // Normalize: accept array OR pre-stringified JSON, mirroring /admin/affiliate/update line 1858.
          const sc = typeof body.split_config === "string" ? body.split_config : JSON.stringify(body.split_config);

          // Validate it parses to an array (cheap sanity check — prevents storing garbage).
          try {
            const parsed = JSON.parse(sc);
            if (!Array.isArray(parsed)) return err(400, "split_config must be an array");
          } catch (_e) {
            return err(400, "split_config invalid JSON");
          }

          const res = await env.DB.prepare(
            `UPDATE referrers SET split_config = ? WHERE id = ? RETURNING *`
          ).bind(sc, referrer_id).all();
          const row = res.results && res.results[0];
          if (!row) return err(404, "partner not found");

          // Inline parseSplit — accept array, pre-stringified JSON, or null/empty → []
          // (function-scoped parseSplit exists elsewhere; safer to inline here).
          let savedSplits = [];
          if (Array.isArray(row.split_config)) savedSplits = row.split_config;
          else if (row.split_config) {
            try { savedSplits = JSON.parse(row.split_config); } catch (_e) { savedSplits = []; }
          }

          // Return shape compatible with frontend handleSaveSuccess() in admin/referrals/index.html:
          //   resp.partner.split_config OR resp.split_config — both supported here.
          return json({
            ok: true,
            partner: pick(row, REFERRER_PUBLIC_COLS),
            split_config: savedSplits,
          });
        }
      }

      // ─────────────────────────────────────────────
      // PUT endpoints
      // ─────────────────────────────────────────────

      if (method === "PUT" && path === "/admin/affiliate/update") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referrer_id, user_name, user_email, paypal_email, partner_tier, split_config } = body;
        if (!referrer_id) return err(400, "referrer_id required");

        // Build dynamic SET clause for only provided fields
        const sets = [];
        const binds = [];
        if (user_name !== undefined) { sets.push("user_name = ?"); binds.push(user_name); }
        if (user_email !== undefined) { sets.push("user_email = ?"); binds.push(user_email.trim().toLowerCase()); }
        if (paypal_email !== undefined) { sets.push("paypal_email = ?"); binds.push(paypal_email.trim()); }
        // SPEC C1: admin can change partner_tier (validated against TIER_RATES)
        if (partner_tier !== undefined) {
          const t = String(partner_tier).toLowerCase();
          if (!TIER_RATES[t]) return err(400, `invalid partner_tier (allowed: ${Object.keys(TIER_RATES).join(", ")})`);
          sets.push("partner_tier = ?"); binds.push(t);
        }
        // SPEC D2: admin can update split_config (accepts array or pre-stringified JSON)
        if (split_config !== undefined) {
          const sc = typeof split_config === "string" ? split_config : JSON.stringify(split_config);
          sets.push("split_config = ?"); binds.push(sc);
        }

        if (sets.length === 0) return err(400, "no fields to update");

        binds.push(referrer_id);
        const res = await env.DB.prepare(
          `UPDATE referrers SET ${sets.join(", ")} WHERE id = ? RETURNING *`
        ).bind(...binds).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "referrer not found");
        return json({ ok: true, referrer: pick(row, REFERRER_PUBLIC_COLS) });
      }

      if (method === "PUT" && path === "/admin/referral/update") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referral_id, referred_email, referred_name, status } = body;
        if (!referral_id) return err(400, "referral_id required");

        const sets = [];
        const binds = [];
        if (referred_email !== undefined) { sets.push("referred_email = ?"); binds.push(referred_email.trim().toLowerCase()); }
        if (referred_name !== undefined) { sets.push("referred_name = ?"); binds.push(referred_name.trim()); }
        if (status !== undefined) {
          sets.push("status = ?"); binds.push(status);
          if (status === "completed") {
            sets.push("completed_at = ?"); binds.push(new Date().toISOString());
          }
        }

        if (sets.length === 0) return err(400, "no fields to update");

        binds.push(referral_id);
        const res = await env.DB.prepare(
          `UPDATE referrals SET ${sets.join(", ")} WHERE id = ? RETURNING *`
        ).bind(...binds).all();
        const row = res.results && res.results[0];
        if (!row) return err(404, "referral not found");
        return json({ ok: true, referral: row });
      }

      // ─────────────────────────────────────────────
      // DELETE endpoints
      // ─────────────────────────────────────────────

      if (method === "DELETE" && path === "/admin/affiliate/delete") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const body = await parseBody(request);
        if (!body) return err(400, "invalid json");

        const { referrer_id } = body;
        if (!referrer_id) return err(400, "referrer_id required");

        // Cascade: delete commission_payments for this referrer's referrals, then referrals, then referrer
        // Also clean up payout_requests, rewards, referral_clicks
        await env.DB.prepare(
          `DELETE FROM commission_payments WHERE referrer_id = ?`
        ).bind(referrer_id).run();
        await env.DB.prepare(
          `DELETE FROM rewards WHERE referrer_id = ?`
        ).bind(referrer_id).run();
        await env.DB.prepare(
          `DELETE FROM payout_requests WHERE referrer_id = ?`
        ).bind(referrer_id).run();

        // Get referral_code before deleting referrer (for click cleanup)
        const ref = await env.DB.prepare(
          `SELECT referral_code FROM referrers WHERE id = ?`
        ).bind(referrer_id).first();

        await env.DB.prepare(
          `DELETE FROM referrals WHERE referrer_id = ?`
        ).bind(referrer_id).run();

        if (ref && ref.referral_code) {
          await env.DB.prepare(
            `DELETE FROM referral_clicks WHERE referral_code = ? COLLATE NOCASE`
          ).bind(ref.referral_code).run();
          // C4: also clean v2 payouts (partner_id = referral_code)
          await env.DB.prepare(
            `DELETE FROM payout_requests_v2 WHERE partner_id = ? COLLATE NOCASE`
          ).bind(ref.referral_code).run();
        }

        const del = await env.DB.prepare(
          `DELETE FROM referrers WHERE id = ?`
        ).bind(referrer_id).run();

        return json({ ok: true, deleted: del.meta?.changes > 0 });
      }

      // ─────────────────────────────────────────────
      // GET endpoints
      // ─────────────────────────────────────────────

      if (method !== "GET" && method !== "POST" && method !== "PUT" && method !== "DELETE") {
        return err(405, "method not allowed");
      }
      if (method !== "GET") return err(404, "not found");

      // GET /health
      if (path === "/health") {
        return json({ ok: true, db: "purebrain-referrals", ts: new Date().toISOString() });
      }

      // GET /referrers
      if (path === "/referrers") {
        const code  = (url.searchParams.get("code")  || "").trim();
        const email = (url.searchParams.get("email") || "").trim();
        if (!code && !email) return err(400, "missing code or email");
        const sql = code
          ? `SELECT * FROM referrers WHERE referral_code = ? COLLATE NOCASE`
          : `SELECT * FROM referrers WHERE user_email = ? COLLATE NOCASE`;
        const { results } = await env.DB.prepare(sql).bind(code || email).all();
        if (!results || results.length === 0) return err(404, "referrer not found");
        return json({ referrer: pick(results[0], REFERRER_PUBLIC_COLS) });
      }

      // GET /referrals
      if (path === "/referrals") {
        const refId = (url.searchParams.get("referrer_id") || "").trim();
        if (!refId) return err(400, "missing referrer_id");
        const { results } = await env.DB.prepare(
          `SELECT r.id, r.referred_name, r.referred_email, r.status, r.created_at,
                  r.completed_at,
                  COALESCE(SUM(cp.commission_value), 0) AS earnings,
                  COUNT(cp.id) AS payment_count
             FROM referrals r
             LEFT JOIN commission_payments cp ON cp.referral_id = r.id
            WHERE r.referrer_id = ?
              AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
         GROUP BY r.id
         ORDER BY r.created_at DESC`
        ).bind(refId).all();
        return json({ referrals: results || [] });
      }

      // GET /commission_payments
      if (path === "/commission_payments") {
        const referralId = (url.searchParams.get("referral_id") || "").trim();
        if (!referralId) return err(400, "missing referral_id");
        const { results } = await env.DB.prepare(
          `SELECT id, referrer_id, referral_id, payer_email, order_id,
                  payment_amount, commission_rate, commission_value, tier,
                  tier_at_write, commission_source, created_at
             FROM commission_payments
            WHERE referral_id = ?
         ORDER BY created_at DESC`
        ).bind(referralId).all();
        return json({ payments: results || [] });
      }

      // GET /dashboard
      if (path === "/dashboard") {
        const code  = (url.searchParams.get("code")  || "").trim().toUpperCase();
        const email = (url.searchParams.get("email") || "").trim().toLowerCase();
        if (!code && !email) return err(400, "missing code or email");

        const refRes = await env.DB.prepare(
          code
            ? `SELECT * FROM referrers WHERE referral_code = ? COLLATE NOCASE`
            : `SELECT * FROM referrers WHERE user_email = ? COLLATE NOCASE`
        ).bind(code || email).all();
        const referrer = refRes.results && refRes.results[0];
        if (!referrer) return err(404, "referrer not found");

        const rid   = referrer.id;
        const rcode = referrer.referral_code;

        const totalQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ?
             AND NOT (status = 'rejected' AND referred_email LIKE 'paypal_%@pending')`
        ).bind(rid).first();
        const completedQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ? AND status = 'completed'`
        ).bind(rid).first();
        const pendingQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ? AND status = 'pending'`
        ).bind(rid).first();
        const earningsQ = await env.DB.prepare(
          `SELECT COALESCE(SUM(reward_value), 0) AS s FROM rewards WHERE referrer_id = ?`
        ).bind(rid).first();
        const clicksQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referral_clicks WHERE referral_code = ? COLLATE NOCASE`
        ).bind(rcode).first();

        const histQ = await env.DB.prepare(
          `SELECT r.referred_name, r.referred_email, r.status, r.created_at,
                  COALESCE(SUM(cp.commission_value), 0) AS earnings,
                  COUNT(cp.id) AS payment_count
             FROM referrals r
             LEFT JOIN commission_payments cp ON cp.referral_id = r.id
            WHERE r.referrer_id = ?
              AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
         GROUP BY r.id
         ORDER BY r.created_at DESC`
        ).bind(rid).all();

        return json({
          referrer_id: rid,
          referral_code: rcode,
          email: referrer.user_email,
          name: referrer.user_name,
          paypal_email: referrer.paypal_email,
          // C1/D2: surface tier + rate for partner dashboard
          partner_tier: referrer.partner_tier || "silver",
          tier_rate: rateForTier(referrer.partner_tier),
          total_sales: referrer.total_sales || 0,
          total_referrals: totalQ.c,
          completed: completedQ.c,
          pending: pendingQ.c,
          earnings: Math.round((earningsQ.s || 0) * 100) / 100,
          total_clicks: clicksQ.c,
          history: histQ.results || [],
        });
      }

      // GET /leaderboard — public, ranked affiliates
      if (path === "/leaderboard") {
        const { results } = await env.DB.prepare(
          `SELECT
             ref.id,
             ref.user_name AS name,
             ref.referral_code AS code,
             COUNT(DISTINCT CASE WHEN r.status = 'completed' THEN r.id END) AS completed,
             COUNT(DISTINCT CASE WHEN r.status = 'pending' THEN r.id END) AS pending,
             COUNT(DISTINCT r.id) AS total_referrals,
             COALESCE(SUM(cp.commission_value), 0) AS total_earned
           FROM referrers ref
           LEFT JOIN referrals r ON r.referrer_id = ref.id
             AND NOT (r.status = 'rejected' AND r.referred_email LIKE 'paypal_%@pending')
           LEFT JOIN commission_payments cp ON cp.referral_id = r.id
           GROUP BY ref.id
           ORDER BY completed DESC, total_earned DESC`
        ).all();
        return json({ leaderboard: results || [] });
      }

      // GET /admin/emails
      if (path === "/admin/emails") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const { results } = await env.DB.prepare(
          `SELECT user_email, referral_code FROM referrers`
        ).all();
        return json({ count: (results || []).length, referrers: results || [] });
      }

      // GET /admin/affiliates
      if (path === "/admin/affiliates") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }

        // Single aggregated query instead of N+1 per-referrer
        const { results: referrers } = await env.DB.prepare(
          `SELECT r.*,
                  COALESCE(rc.click_count, 0) AS clicks,
                  COALESCE(ref_stats.total, 0) AS total,
                  COALESCE(ref_stats.completed, 0) AS completed,
                  COALESCE(ref_stats.pending, 0) AS pending,
                  COALESCE(rew.earnings, 0) AS earnings
           FROM referrers r
           LEFT JOIN (SELECT referral_code, COUNT(*) AS click_count FROM referral_clicks GROUP BY referral_code) rc
             ON LOWER(rc.referral_code) = LOWER(r.referral_code)
           LEFT JOIN (SELECT referrer_id,
                             COUNT(*) AS total,
                             SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed,
                             SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending
                      FROM referrals GROUP BY referrer_id) ref_stats
             ON ref_stats.referrer_id = r.id
           LEFT JOIN (SELECT referrer_id, COALESCE(SUM(reward_value), 0) AS earnings FROM rewards GROUP BY referrer_id) rew
             ON rew.referrer_id = r.id
           ORDER BY r.created_at DESC`
        ).all();

        // Get referral history in one query
        const { results: allHistory } = await env.DB.prepare(
          `SELECT ref.referrer_id, ref.id, ref.referred_name, ref.referred_email, ref.status, ref.created_at,
                  COALESCE(SUM(cp.commission_value), 0) AS earnings,
                  COUNT(cp.id) AS payment_count
           FROM referrals ref
           LEFT JOIN commission_payments cp ON cp.referral_id = ref.id
           GROUP BY ref.id
           ORDER BY ref.created_at DESC`
        ).all();

        // Group history by referrer
        const histMap = {};
        for (const h of allHistory || []) {
          if (!histMap[h.referrer_id]) histMap[h.referrer_id] = [];
          histMap[h.referrer_id].push({
            id: h.id, referred_name: h.referred_name, referred_email: h.referred_email,
            status: h.status, created_at: h.created_at, earnings: h.earnings, payment_count: h.payment_count
          });
        }

        // SPEC D2: parse split_config JSON for frontend renderSplitRows().
        // Accept array, pre-stringified JSON, or null/empty → []
        function parseSplit(s) {
          if (!s) return [];
          if (Array.isArray(s)) return s;
          try { return JSON.parse(s); } catch (_e) { return []; }
        }

        const affiliates = (referrers || []).map(r => ({
          id: r.id, name: r.user_name, email: r.user_email, code: r.referral_code,
          paypal_email: r.paypal_email || "", clicks: r.clicks || 0,
          total: r.total || 0, completed: r.completed || 0, pending: r.pending || 0,
          earnings: r.earnings || 0, joined: r.created_at,
          // SPEC D2 + C1: include partner_tier + split_config in response
          // so frontend renderSplitRows() can populate split rows.
          partner_tier: r.partner_tier || "silver",
          tier_rate: rateForTier(r.partner_tier),
          total_sales: r.total_sales || 0,
          split_config: parseSplit(r.split_config),
          history: histMap[r.id] || []
        }));

        return json({ affiliates, count: affiliates.length });
      }

      // GET /admin/payouts — list all payout requests (legacy + v2 merged)
      // SPEC C4: v2 table payout_requests_v2 holds partner-self requests with
      // $50 min CHECK. Legacy payout_requests retained for historical records.
      if (path === "/admin/payouts") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const legacyP = env.DB.prepare(
          `SELECT 'legacy' AS source, p.*, ref.user_name AS referrer_name, ref.user_email AS referrer_email,
                  ref.paypal_email AS referrer_paypal
           FROM payout_requests p
           LEFT JOIN referrers ref ON ref.id = p.referrer_id
           ORDER BY p.created_at DESC`
        ).all();
        const v2P = env.DB.prepare(
          `SELECT 'v2' AS source, p2.id, p2.partner_id, p2.amount, p2.payout_method, p2.paypal_email,
                  p2.status, p2.requested_at, p2.paid_at, p2.paid_via_split_id,
                  ref.user_name AS referrer_name, ref.user_email AS referrer_email,
                  ref.paypal_email AS referrer_paypal
           FROM payout_requests_v2 p2
           LEFT JOIN referrers ref ON ref.referral_code = p2.partner_id COLLATE NOCASE
           ORDER BY p2.requested_at DESC`
        ).all();
        const [legacy, v2] = await Promise.all([legacyP, v2P]);
        const merged = [...(legacy.results || []), ...(v2.results || [])];
        return json({ payouts: merged, count: merged.length });
      }

      // GET /admin/applications — list partner applications (SPEC C2)
      // Optional query: ?status=pending|approved|rejected|needs_30d_use
      if (path === "/admin/applications") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }
        const status = (url.searchParams.get("status") || "").trim();
        const stmt = status
          ? env.DB.prepare(
              `SELECT * FROM partner_applications WHERE status = ? ORDER BY applied_at DESC`
            ).bind(status)
          : env.DB.prepare(
              `SELECT * FROM partner_applications ORDER BY applied_at DESC`
            );
        const { results } = await stmt.all();
        return json({ applications: results || [], count: (results || []).length });
      }

      // GET /admin/commission-report — grouped commissions per referrer (CTO 2026-05-12 Track B.2)
      // Query: ?start=YYYY-MM-DD&end=YYYY-MM-DD&referrer_id=N (all optional)
      // Default window: current calendar month UTC.
      // Returns { report: [...], totals: {gross,paid,pending,count}, period: {start,end} }
      if (path === "/admin/commission-report") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }

        const isoDateRe = /^\d{4}-\d{2}-\d{2}$/;
        const now = new Date();
        const monthStart = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1))
          .toISOString().slice(0, 10);
        const nextMonth = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 1))
          .toISOString().slice(0, 10);

        let start = (url.searchParams.get("start") || "").trim();
        let end   = (url.searchParams.get("end")   || "").trim();
        const referrer_id_raw = (url.searchParams.get("referrer_id") || "").trim();

        if (start && !isoDateRe.test(start)) return err(400, "invalid start (YYYY-MM-DD)");
        if (end   && !isoDateRe.test(end))   return err(400, "invalid end (YYYY-MM-DD)");
        if (!start) start = monthStart;
        if (!end)   end   = nextMonth; // exclusive upper bound

        const referrer_id = referrer_id_raw ? Number(referrer_id_raw) : null;
        if (referrer_id_raw && !Number.isFinite(referrer_id)) return err(400, "invalid referrer_id");

        // D1 TEXT date columns sort lexicographically when format is consistent.
        // commission_payments.created_at is ISO-8601 UTC, prefix matches YYYY-MM-DD.
        const { results } = await env.DB.prepare(
          `SELECT
              r.id AS referrer_id,
              r.user_name AS referrer_name,
              r.user_email AS referrer_email,
              r.referral_code,
              r.partner_tier,
              COUNT(cp.id) AS commission_count,
              COALESCE(SUM(cp.commission_value), 0) AS gross_commissions,
              SUM(CASE WHEN cp.commission_source = 'support_tier' THEN 1 ELSE 0 END) AS support_tier_count
           FROM referrers r
           LEFT JOIN commission_payments cp
             ON cp.referrer_id = r.id
             AND cp.created_at >= ?
             AND cp.created_at < ?
           WHERE (? IS NULL OR r.id = ?)
           GROUP BY r.id
           HAVING COUNT(cp.id) > 0
           ORDER BY gross_commissions DESC
           LIMIT 1000`
        ).bind(start, end, referrer_id, referrer_id).all();

        const report = (results || []).map(row => ({
          referrer_id: row.referrer_id,
          referrer_name: row.referrer_name,
          referrer_email: row.referrer_email,
          referral_code: row.referral_code,
          partner_tier: row.partner_tier || "silver",
          tier_rate: rateForTier(row.partner_tier),
          commission_count: row.commission_count || 0,
          gross_commissions: Math.round((row.gross_commissions || 0) * 100) / 100,
          support_tier_count: row.support_tier_count || 0,
        }));

        const totals = report.reduce((acc, r) => {
          acc.count += r.commission_count;
          acc.gross += r.gross_commissions;
          return acc;
        }, { count: 0, gross: 0 });
        totals.gross = Math.round(totals.gross * 100) / 100;

        return json({
          report,
          totals,
          period: { start, end },
        });
      }

      // GET /admin/stats — overview stats
      if (path === "/admin/stats") {
        { const gate = await requireAdminUnified(request, env); if (!gate.ok) return err(gate.status || 401, "unauthorized"); }

        const affiliatesQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrers`
        ).first();
        const clicksQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referral_clicks`
        ).first();
        const referralsQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals`
        ).first();
        const completedQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE status = 'completed'`
        ).first();
        const pendingQ = await env.DB.prepare(
          `SELECT COUNT(*) AS c FROM referrals WHERE status = 'pending'`
        ).first();
        const earningsQ = await env.DB.prepare(
          `SELECT COALESCE(SUM(commission_value), 0) AS total FROM commission_payments`
        ).first();
        const rewardsQ = await env.DB.prepare(
          `SELECT COALESCE(SUM(reward_value), 0) AS total FROM rewards`
        ).first();

        return json({
          total_affiliates: affiliatesQ.c,
          total_clicks: clicksQ.c,
          total_referrals: referralsQ.c,
          completed_referrals: completedQ.c,
          pending_referrals: pendingQ.c,
          total_commissions: Math.round((earningsQ.total || 0) * 100) / 100,
          total_rewards: Math.round((rewardsQ.total || 0) * 100) / 100,
        });
      }

      return err(404, "not found");
    } catch (e) {
      return json({ error: "worker_error", detail: String(e && e.message || e) }, { status: 500 });
    }
  },
};
