/**
 * PureBrain Portal Proxy Worker
 * ==============================
 * Routes *.purebrain.ai portal subdomains to Witness containers at 37.27.237.109.
 *
 * Request flow:
 *   {subdomain}.purebrain.ai/*
 *     → Check if portal subdomain (not a known system subdomain)
 *     → If portal: proxy to https://{subdomain}.ai-civ.com on Witness (37.27.237.109)
 *     → If system subdomain: pass through to Cloudflare (tunnel handles it)
 *
 * P-2 FIX (2026-04-15): The prior version had a special-case for
 *   `app.purebrain.ai/api/referral/*` that proxied to `chy-jared.ai-civ.com`.
 *   That container's D1-backed handler returned HTTP 200 success bodies
 *   without writing to the authoritative SQLite store on the VPS, silently
 *   dropping every referral attribution since at least 2026-04-14.
 *
 *   Fix: removed the special-case. `app` is already a SYSTEM_SUBDOMAIN, so it
 *   now falls through to Cloudflare routing, which hands off to the cloudflared
 *   tunnel → nginx → portal_server.py:8097 (SQLite authoritative). Root cause
 *   + audit in:
 *     /home/jared/exports/portal-files/referral-attribution-flow-2026-04-15.md
 *     .claude/memory/agent-learnings/security-engineer-tech/2026-04-15--p2-referral-attribution-ghost-endpoint.md
 *
 * Deploy:
 *   Worker name:  purebrain-portal-proxy
 *   Route:        *.purebrain.ai/*  (already configured on zone)
 *   Zone:         purebrain.ai (ID: 49400cad1527af716705f6cb8c22bb65)
 *
 * Witness server: 37.27.237.109
 * Container URL format: https://{subdomain}.ai-civ.com
 */

// Known system subdomains — pass these through to Cloudflare/tunnel unchanged.
// These have explicit DNS records (CNAME → cloudflared tunnel) that handle routing.
const SYSTEM_SUBDOMAINS = new Set([
  'app',
  'www',
  'portal',
  'api',
  'video',
  'cc',
  'comms',
  'mail',
  'staging',
  'blog',
  'status',
  'cdn',
  'static',
  'assets',
  'media',
  'social',         // social.purebrain.ai → social-api CF Worker
  'social-api',     // social-api.purebrain.ai → social-api CF Worker
  'voice',          // voice.purebrain.ai → proxy worker handles routing
  'tts',            // tts.purebrain.ai → Argo Tunnel to Chatterbox TTS
  'keenjared',     // Legacy test portal — still in DNS, routed via nginx
  'testariatest',  // Legacy test portal — still in DNS, routed via nginx
]);

// Witness server IP — all container traffic routes here
const WITNESS_IP = '37.27.237.109';

// ai-civ.com: the actual hostname namespace for portal containers
const CONTAINER_DOMAIN = 'ai-civ.com';

/**
 * Determine if this subdomain is a portal subdomain.
 * Returns true if it should be proxied to Witness.
 * Returns false if it's a known system subdomain.
 */
function isPortalSubdomain(subdomain) {
  if (!subdomain) return false;
  if (SYSTEM_SUBDOMAINS.has(subdomain.toLowerCase())) return false;
  return /^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/.test(subdomain.toLowerCase());
}

/**
 * Extract the subdomain from a Host header value.
 * e.g. "greg-lucas-neuteufel.purebrain.ai" → "greg-lucas-neuteufel"
 * e.g. "purebrain.ai" → "" (no subdomain = apex domain)
 */
function extractSubdomain(host) {
  const hostname = host.split(':')[0];
  const parts = hostname.split('.');
  if (parts.length <= 2) return '';
  return parts.slice(0, parts.length - 2).join('.');
}

/**
 * Proxy a request to a specific container on Witness.
 */
async function proxyToContainer(request, targetHost, originalHost) {
  const url = new URL(request.url);
  const targetUrl = `https://${targetHost}${url.pathname}${url.search}`;

  const proxyHeaders = new Headers(request.headers);
  proxyHeaders.set('Host', targetHost);
  proxyHeaders.set('X-Forwarded-Host', originalHost);
  proxyHeaders.set('X-Forwarded-Proto', url.protocol.replace(':', ''));
  proxyHeaders.set('X-Real-IP', request.headers.get('CF-Connecting-IP') || '');

  const proxyRequest = new Request(targetUrl, {
    method: request.method,
    headers: proxyHeaders,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
    redirect: 'manual',
  });

  const response = await fetch(proxyRequest, {
    cf: { resolveOverride: WITNESS_IP },
  });

  const responseHeaders = new Headers(response.headers);
  const location = responseHeaders.get('Location');
  if (location && location.includes(`.${CONTAINER_DOMAIN}`)) {
    const rewritten = location.replace(
      new RegExp(`([a-z0-9-]+)\\.${CONTAINER_DOMAIN.replace('.', '\\.')}`, 'g'),
      `$1.purebrain.ai`
    );
    responseHeaders.set('Location', rewritten);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

/**
 * Validate the caller has a valid `leader` session before allowing the bridge
 * to inject `X-Admin-Token` into admin-api forwards.
 *
 * Source: 2026-05-09 CTO pre-build spec. Closes the bug where anonymous
 * `curl https://portal.purebrain.ai/api/admin/invites` received a server-injected
 * admin token + full invitee list (including role:leader grants).
 *
 * Reuses the existing `/internal/validate-session` Service Binding contract on
 * `social-api` (the new auth authority per CTO spec UL-SEC-003, 2026-05-12).
 * Previously routed to clients-api; swapped to social-api which shipped its
 * own /internal/validate-session at Chy commit f7d0428.
 *
 * Failure modes (fail CLOSED — security gate):
 *   - missing token        → 401 unauthorized
 *   - missing binding/secret → 503 auth_unavailable
 *   - bridge non-success   → 401 unauthorized
 *   - role !== "leader"    → 403 forbidden
 *   - bridge throw         → 503 auth_unavailable
 *
 * Token sources accepted (matches admin-api getSession order):
 *   1. Authorization: Bearer <token>      (preferred, used by admin frontend localStorage)
 *   2. Cookie social_session=<token>      (fallback, set by /api/login → social-api)
 */
async function validateLeaderSession(request, env) {
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return { ok: false, status: 401 };

  if (!env.SOCIAL_API || !env.INTERNAL_BINDING_SECRET) {
    // Fail CLOSED — emergency security gate. Better 503 than bypass.
    return { ok: false, status: 503 };
  }

  try {
    // 2026-05-12: Swapped CLIENTS_API → SOCIAL_API per CTO spec UL-SEC-003.
    // Chy shipped /internal/validate-session on social-api at commit f7d0428;
    // social-api is now the canonical auth authority. Verified LIVE:
    //   POST https://social-api.in0v8.workers.dev/internal/validate-session → 403
    //   (route exists, secret-gated). Aether-local source mirror is STALE
    //   for Chy's domain — verified via live probe per
    //   feedback_architectural_truth_first.md.
    const req = new Request("https://social-api/internal/validate-session", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding": "social-api",
        "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
      },
      body: JSON.stringify({ token }),
    });
    const resp = await env.SOCIAL_API.fetch(req);
    if (!resp.ok) return { ok: false, status: 401 };
    const j = await resp.json();
    if (!j || j.valid !== true) return { ok: false, status: 401 };
    // Expanded role list per CTO spec UL-SEC-003 (owner/admin/leader/system).
    if (!["owner","admin","leader","system"].includes(j.role)) return { ok: false, status: 403 };
    return { ok: true, session: j };
  } catch {
    // Bridge unreachable — fail CLOSED for security routes.
    return { ok: false, status: 503 };
  }
}

// =====================================================================
// Day 2 Track D — Shadow-auth instrumentation
// =====================================================================
//
// Wraps validateLeaderSession() so we can dual-call BOTH the legacy
// social-api path AND the new per-dashboard validate-session paths
// (clients-api for /admin/clients/*, referrals-api for /admin/referral/*).
//
// LEGACY ALWAYS WINS. The shadow call is fire-and-forget — its result
// never feeds the auth decision. Zero behavior change Day 2.
//
// Authority chain:
//   - ST# brief: /home/jared/exports/portal-files/st-day2-build-brief-2026-05-14.md §Track D
//   - CTO review: /home/jared/exports/portal-files/cto-review-auth-decoupling-2026-05-14.md
//   - Compressed shadow window (1-2h) per CTO amendment #1 (not 24h)
//
// PII discipline (per feedback_secrets_must_not_be_recoverable_from_chat.md +
// monitor-alive-≠-monitor-seeing): logs emit only boolean field-presence
// indicators (have_user_id, have_email). NO password_hash, NO session
// tokens, NO full email values.
//
// Readout: tail-based via scripts/shadow-auth-readout.sh (the canonical
// mechanism per ST# brief D.4) PLUS a live in-isolate snapshot at
// GET /admin/shadow-auth-readout (admin-gated; same auth as the wrapped
// validator).
// =====================================================================

const SHADOW_LOG_EVT = "shadow_auth";

// In-isolate ring buffer of recent shadow-auth samples. Workers isolates are
// not persistent and not shared across edge locations — this is best-effort
// for live debugging via /admin/shadow-auth-readout. Authoritative readout
// is wrangler tail (see scripts/shadow-auth-readout.sh).
const SHADOW_RING_MAX = 512;
const SHADOW_RING = []; // newest at end; older entries shifted off the front

function _shadowRingPush(entry) {
  try {
    SHADOW_RING.push(entry);
    if (SHADOW_RING.length > SHADOW_RING_MAX) {
      SHADOW_RING.splice(0, SHADOW_RING.length - SHADOW_RING_MAX);
    }
  } catch {
    // never throw from the shadow log path
  }
}

function _present(v) {
  // Sensitive-value redaction: convert any value to a presence indicator only.
  // Same pattern as workers/_shared/auth-cross-write.js (Track C).
  return v !== undefined && v !== null && v !== "" && v !== false;
}

/**
 * Detect which "new" dashboard validate-session path should be shadowed
 * for this request. Returns one of: "clients" | "referrals" | "unknown".
 *
 * The detection is based on URL pathname because admin frontends issue
 * requests with a stable path family per dashboard:
 *   - /api/admin/clients/*  + /api/admin/invite* → clients dashboard
 *   - /api/admin/referral/* + /api/admin/affiliat* + /api/admin/partners*
 *     + /api/admin/payout* + /api/admin/applications* + /api/admin/payments/manual*
 *     + /api/admin/commission-report + /api/admin/stats → referrals dashboard
 *
 * Other paths (e.g. /api/admin/validate-token, which is intentionally
 * unauthenticated) → "unknown" → shadow side becomes a no-op.
 */
function shadowDashboardTarget(pathname) {
  if (!pathname) return "unknown";
  if (
    pathname.startsWith("/api/admin/clients") ||
    pathname.startsWith("/api/admin/invite") ||
    pathname.startsWith("/api/admin/invites")
  ) {
    return "clients";
  }
  if (
    pathname.startsWith("/api/admin/affiliat") ||
    pathname.startsWith("/api/admin/payout") ||
    pathname.startsWith("/api/admin/referral/") ||
    pathname === "/api/admin/stats" ||
    pathname === "/api/admin/partners" ||
    pathname.startsWith("/api/admin/partners/") ||
    pathname === "/api/admin/commission-report" ||
    pathname.startsWith("/api/admin/payments/manual") ||
    pathname.startsWith("/api/admin/applications")
  ) {
    return "referrals";
  }
  return "unknown";
}

/**
 * Extract the same token validateLeaderSession() uses. Kept as a pure
 * helper so the shadow path can replay the same token without re-parsing
 * headers in three places.
 */
function _extractSessionToken(request) {
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) return auth.slice(7);
  const cookies = request.headers.get("cookie") || "";
  const m = cookies.match(/social_session=([^;]+)/);
  if (m) return m[1];
  return "";
}

/**
 * Call the new per-dashboard /internal/validate-session and return its
 * parsed JSON. NEVER throws. NEVER affects the wrapping caller's path.
 *
 * Targets:
 *   - "clients"   → env.CLIENTS_API   (binding already present in wrangler.toml)
 *   - "referrals" → env.REFERRALS_API (binding added by Day 2 Track D wrangler.toml diff)
 *
 * Returns shape:
 *   { ok: true, status: 200, json: { ok, session?: {user_id, email, role?, ...} } }
 *   { ok: false, status: <int>, error: <str> }
 */
async function _shadowValidateNewPath(target, token, env) {
  let binding = null;
  let bindingName = null;
  if (target === "clients") {
    binding = env.CLIENTS_API || null;
    bindingName = "clients-api";
  } else if (target === "referrals") {
    binding = env.REFERRALS_API || null;
    bindingName = "referrals-api";
  } else {
    return { ok: false, status: 0, error: "target_unknown" };
  }
  if (!binding) return { ok: false, status: 0, error: "binding_missing" };
  if (!env.INTERNAL_BINDING_SECRET) {
    return { ok: false, status: 0, error: "secret_missing" };
  }
  if (!token) return { ok: false, status: 401, error: "no_token" };

  try {
    const req = new Request(`https://${bindingName}/internal/validate-session`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding": bindingName,
        "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
      },
      body: JSON.stringify({ token }),
    });
    const resp = await binding.fetch(req);
    let json = null;
    try {
      json = await resp.json();
    } catch {
      json = null;
    }
    return { ok: resp.ok, status: resp.status, json };
  } catch (e) {
    return { ok: false, status: 0, error: "fetch_failed", detail: (e && e.message) || "unknown" };
  }
}

/**
 * Compare a legacy validateLeaderSession() result with a shadow
 * _shadowValidateNewPath() result. Returns a comparison record with
 * presence-only fields (PII-safe).
 *
 * Inputs:
 *   legacy — return value of validateLeaderSession(): {ok, status?, session?}
 *   shadow — return value of _shadowValidateNewPath(): {ok, status, json?, error?}
 *
 * The shadow JSON shape depends on which worker answered:
 *   - clients-api: { ok: true, session: { user_id, email, role?, client_id? } }
 *   - referrals-api: { ok: true, session: { user_id, email, referrals_role? } }
 * We normalize both to {user_id, email, role}.
 */
function _compareAuthResults(legacy, shadow) {
  const legacyUserId = legacy && legacy.session && legacy.session.user_id;
  const legacyEmail = legacy && legacy.session && legacy.session.email;
  const legacyRole = legacy && legacy.session && legacy.session.role;

  const sj = shadow && shadow.json && (shadow.json.session || shadow.json) || null;
  const shadowUserId = sj && sj.user_id;
  const shadowEmail = sj && sj.email;
  // role may live under different column names; normalize for comparison
  const shadowRole = sj && (sj.role || sj.referrals_role || sj.clients_role || sj.social_role);

  const user_id_match = legacyUserId === shadowUserId;
  const email_match = legacyEmail === shadowEmail;
  // role match is informational only — different dashboards may legitimately
  // have different roles for the same user (clients_role vs referrals_role).
  const role_match = legacyRole === shadowRole;

  // Divergence definition for Day-3 greenlight gate: user_id MUST match when
  // BOTH sides successfully validated. If only one side succeeded, that's a
  // divergence in itself.
  const both_ok = !!(legacy && legacy.ok) && !!(shadow && shadow.ok);
  const neither_ok = !(legacy && legacy.ok) && !(shadow && shadow.ok);
  const divergent = both_ok ? !user_id_match : !neither_ok;

  return {
    legacy_ok: !!(legacy && legacy.ok),
    shadow_ok: !!(shadow && shadow.ok),
    legacy_status: (legacy && legacy.status) || (legacy && legacy.ok ? 200 : 0),
    shadow_status: (shadow && shadow.status) || 0,
    shadow_error: (shadow && shadow.error) || null,
    user_id_match,
    email_match,
    role_match,
    field_present: {
      legacy_user_id: _present(legacyUserId),
      legacy_email: _present(legacyEmail),
      legacy_role: _present(legacyRole),
      shadow_user_id: _present(shadowUserId),
      shadow_email: _present(shadowEmail),
      shadow_role: _present(shadowRole),
    },
    divergent,
  };
}

/**
 * Drop-in wrapper for validateLeaderSession() that ALSO runs the new
 * per-dashboard validator in parallel, compares, and logs. Returns the
 * LEGACY result verbatim — auth decision is unchanged.
 *
 * Caller pattern:
 *   const gate = await validateLeaderSessionShadow(request, env);
 *   if (!gate.ok) { ...same as before... }
 *
 * If shadow side fails for any reason (binding missing, fetch error,
 * exception), the shadow leg is logged with the error and the legacy
 * result is still returned cleanly.
 */
async function validateLeaderSessionShadow(request, env) {
  const url = new URL(request.url);
  const target = shadowDashboardTarget(url.pathname);
  const token = _extractSessionToken(request);

  // Run BOTH in parallel. We always await legacy because that's the
  // auth decision; we await shadow only so we can log the comparison
  // before returning (preserves linear timing semantics for callers).
  const legacyPromise = validateLeaderSession(request, env);
  const shadowPromise = _shadowValidateNewPath(target, token, env);

  // settle both; never let shadow's settlement affect legacy's return value
  let legacy, shadow;
  try {
    [legacy, shadow] = await Promise.all([
      legacyPromise.catch((e) => ({ ok: false, status: 503, error: "legacy_threw", detail: (e && e.message) || "unknown" })),
      shadowPromise.catch((e) => ({ ok: false, status: 0, error: "shadow_threw", detail: (e && e.message) || "unknown" })),
    ]);
  } catch (e) {
    // Defensive — Promise.all itself should not throw given the .catch above,
    // but if it does, fall back to a fresh legacy call so we never leave the
    // caller without a verdict.
    try {
      legacy = await validateLeaderSession(request, env);
    } catch {
      legacy = { ok: false, status: 503 };
    }
    shadow = { ok: false, status: 0, error: "promise_all_threw" };
  }

  const cmp = _compareAuthResults(legacy, shadow);
  const entry = {
    evt: SHADOW_LOG_EVT,
    ts: Date.now(),
    target,
    path: url.pathname,
    method: request.method,
    have_token: _present(token),
    ...cmp,
  };
  try {
    // structured JSON line — wrangler tail will capture it
    console.log(JSON.stringify(entry));
  } catch {
    // never throw from the log path
  }
  _shadowRingPush(entry);

  // ALWAYS honor legacy — zero behavior change Day 2
  return legacy;
}

/**
 * GET /admin/shadow-auth-readout
 *
 * Admin-gated live snapshot of the in-isolate shadow-auth ring buffer.
 * Returns aggregated stats + a sample of recent comparisons (PII-safe,
 * presence flags only — no tokens, no emails, no raw IDs).
 *
 * Verdict semantics (matches scripts/shadow-auth-readout.sh):
 *   - GREENLIGHT: ≥100 samples AND 0 divergences AND all field_present_rates = 1.0
 *   - YELLOW:    ≥100 samples AND divergence rate ≤ 1%
 *   - BLOCK:     anything else (insufficient samples OR divergence > 1%)
 *
 * NOTE: this endpoint reflects ONE isolate. For a fleet-wide readout,
 * use the wrangler-tail script. This is a live convenience for the
 * operator to spot-check from an admin browser.
 *
 * Auth: same gate as the wrapped paths — requires owner/admin/leader/system
 * session via validateLeaderSession (legacy, fail-closed).
 */
async function shadowAuthReadout(request, env) {
  const gate = await validateLeaderSession(request, env);
  if (!gate.ok) {
    const errBody = gate.status === 403
      ? '{"error":"forbidden"}'
      : (gate.status === 503 ? '{"error":"auth_unavailable"}' : '{"error":"unauthorized"}');
    return new Response(errBody, {
      status: gate.status,
      headers: { "content-type": "application/json" },
    });
  }

  const url = new URL(request.url);
  // Optional ?hours= filter; default = all entries in the isolate ring buffer.
  const hoursParam = parseFloat(url.searchParams.get("hours") || "0");
  const cutoff = hoursParam > 0 ? Date.now() - hoursParam * 3600 * 1000 : 0;
  const entries = SHADOW_RING.filter((e) => e.ts >= cutoff);
  const total = entries.length;

  let divergent = 0;
  let both_ok = 0;
  let neither_ok = 0;
  let legacy_only_ok = 0;
  let shadow_only_ok = 0;
  const by_target = { clients: 0, referrals: 0, unknown: 0 };
  const field_present_sums = {
    legacy_user_id: 0, legacy_email: 0, legacy_role: 0,
    shadow_user_id: 0, shadow_email: 0, shadow_role: 0,
  };

  for (const e of entries) {
    if (e.divergent) divergent++;
    if (e.legacy_ok && e.shadow_ok) both_ok++;
    else if (!e.legacy_ok && !e.shadow_ok) neither_ok++;
    else if (e.legacy_ok && !e.shadow_ok) legacy_only_ok++;
    else if (!e.legacy_ok && e.shadow_ok) shadow_only_ok++;

    if (by_target[e.target] !== undefined) by_target[e.target]++;

    if (e.field_present) {
      for (const k of Object.keys(field_present_sums)) {
        if (e.field_present[k]) field_present_sums[k]++;
      }
    }
  }

  const field_present_rate = {};
  for (const k of Object.keys(field_present_sums)) {
    field_present_rate[k] = total > 0 ? field_present_sums[k] / total : null;
  }

  const divergence_rate = total > 0 ? divergent / total : null;

  let verdict;
  if (total < 100) {
    verdict = "BLOCK"; // insufficient samples — never greenlight on low N
  } else if (divergent === 0 && field_present_rate.legacy_user_id === 1.0 && field_present_rate.shadow_user_id === 1.0) {
    verdict = "GREENLIGHT";
  } else if (divergence_rate <= 0.01) {
    verdict = "YELLOW";
  } else {
    verdict = "BLOCK";
  }

  // PII-safe sample: last 10 entries with ONLY presence + status + matches
  const sampleSize = Math.min(10, entries.length);
  const sample = entries.slice(-sampleSize).map((e) => ({
    ts: e.ts,
    target: e.target,
    path: e.path,
    method: e.method,
    legacy_ok: e.legacy_ok,
    shadow_ok: e.shadow_ok,
    legacy_status: e.legacy_status,
    shadow_status: e.shadow_status,
    shadow_error: e.shadow_error,
    user_id_match: e.user_id_match,
    email_match: e.email_match,
    role_match: e.role_match,
    divergent: e.divergent,
    field_present: e.field_present,
  }));

  return new Response(JSON.stringify({
    ok: true,
    source: "in-isolate-ring-buffer",
    note: "Single-isolate snapshot. For fleet-wide readout use scripts/shadow-auth-readout.sh",
    window_hours: hoursParam || null,
    ring_max: SHADOW_RING_MAX,
    total,
    divergent,
    divergence_rate,
    both_ok,
    neither_ok,
    legacy_only_ok,
    shadow_only_ok,
    by_target,
    field_present_rate,
    verdict,
    sample,
    generated_at: Date.now(),
  }, null, 2), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const host = request.headers.get('Host') || url.host;
    const subdomain = extractSubdomain(host);

    // No subdomain = apex domain (purebrain.ai itself).
    if (!subdomain) {
      return fetch(request);
    }

    // NOTE: the prior `app + /api/referral/*` special-case was REMOVED
    // (P-2 fix 2026-04-15). `app` is a SYSTEM_SUBDOMAIN and now falls through
    // to the tunnel → nginx → portal_server.py, which is the authoritative
    // SQLite write path.

    // portal.purebrain.ai routing
    if (subdomain === 'portal') {
      // Admin HTML pages → CF Pages (git, NOT container)
      if (url.pathname.startsWith('/admin/clients') || url.pathname.startsWith('/admin/referrals')) {
        const pagesPath = url.pathname.endsWith('/') ? url.pathname + 'index.html' : url.pathname + '/index.html';
        const resp = await fetch(`https://purebrain.ai${pagesPath}`);
        return new Response(resp.body, { status: resp.status, headers: resp.headers });
      }
      // Admin + Referral API → D1 Workers
      // Login API → social-api Worker (for email/password auth).
      //
      // Phase 7c (2026-05-11): switched from outbound fetch() to Service
      // Binding to preserve cf-connecting-ip across the Worker→Worker hop.
      // Prior outbound fetch() caused social-api to see a shared edge IP
      // (or null → "unknown") for ALL portal logins globally, saturating
      // the LOGIN_TOTAL_LIMIT=20/60min bucket within minutes and 429ing
      // every subsequent login. Service binding hands the receiving
      // Worker the same Request object — cf-connecting-ip is the real
      // client IP. Constitutional pattern: feedback_cf_service_binding_pattern.md
      if (url.pathname === '/api/login') {
        if (!env.SOCIAL_API) {
          // Defensive: should be impossible if wrangler.toml is correct,
          // but fail CLOSED if binding is missing (matches the
          // CLIENTS_API fail-closed pattern at line 163-166).
          return new Response(
            JSON.stringify({ error: 'login service binding unavailable' }),
            { status: 503, headers: { 'content-type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
          );
        }
        const resp = await env.SOCIAL_API.fetch(request);
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Referral API → referrals-api Worker (D1)
      // B1 (referral-v1): path mismatch fix.
      //   payment-page POSTs to /api/referral/complete must forward to
      //   referrals-api /referrals/complete (the actual handler path) — not
      //   the bare /complete that the previous prefix-strip produced.
      //   Map: /api/referral/<rest> → /referrals/<rest>
      //   Special: /api/referral or /api/referral/ → /referrals
      if (url.pathname.startsWith('/api/referral/') || url.pathname === '/api/referral') {
        const tail = url.pathname === '/api/referral'
          ? ''
          : url.pathname.slice('/api/referral'.length); // includes leading '/'
        // 2026-05-12 PTT# leaderboard routing fix:
        //   /api/referral/leaderboard is a PUBLIC endpoint exposed at root path
        //   /leaderboard on the referrals-api worker — NOT under /referrals/*.
        //   Map it directly. All other /api/referral/* paths still rewrite to
        //   /referrals/<tail> (e.g. /referrals/complete, /referrals/track).
        //   Live probe confirmed: GET /leaderboard?limit=20 returns 200 with
        //   {leaderboard: [...]}; GET /referrals/leaderboard returns 404.
        //
        // 2026-05-12 PTT# dashboard routing fix (same bug class):
        //   /api/referral/dashboard was 404ing because portal-proxy mapped it
        //   to /referrals/dashboard, but referrals-api exposes /dashboard at
        //   ROOT (worker.js:1999). Live probe:
        //     GET /dashboard?code=JAREDSB0 → 200 {referrer_id, earnings, history,...}
        //     GET /referrals/dashboard?code=JAREDSB0 → 404
        //   Converted leaderboard exception into a set-based allowlist so future
        //   root-level public endpoints can be added in one line instead of
        //   whack-a-mole'ing this every time.
        //   Audit of referrals-api root-level routes (grep `path === "/...`):
        //     /health, /referrers, /referrals, /commission_payments, /dashboard,
        //     /leaderboard, /admin/* (separate handler block below).
        //   Of these, only /dashboard and /leaderboard are called from the
        //   public refer/ UI via /api/referral/* — others are admin/internal.
        const ROOT_LEVEL_REFERRAL_PATHS = new Set(['/leaderboard', '/dashboard']);
        const workerPath = ROOT_LEVEL_REFERRAL_PATHS.has(tail)
          ? tail
          : '/referrals' + tail; // e.g. /referrals/complete, /referrals/track
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const resp = await fetch(new Request(workerUrl, {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin referral endpoints → referrals-api Worker (D1 purebrain-referrals)
      //
      // SECURITY (2026-05-09 V-11 regression on referral-v1): X-Admin-Token now sourced from
      // env.ADMIN_TOKEN secret. Hardcoded literal `purebrain-admin-2026` was retired on `main`
      // by commit 1fe0a3e (2026-05-07) but branch divergence left it live on referral-v1 until
      // this commit. Token rotated and bound via wrangler secret put on both portal-proxy and
      // admin-api workers concurrent with this change.
      //
      // EXPANDED 2026-05-12 (CTO Track B/C cutover): added /partners, /commission-report,
      // /payments/manual, /applications. Old duplicate dead-code block below this one
      // removed in same commit per Blocker #6. Single block now handles all admin
      // referral paths routed to referrals-api.
      if (
        url.pathname.startsWith('/api/admin/affiliat') ||
        url.pathname.startsWith('/api/admin/payout') ||
        url.pathname.startsWith('/api/admin/referral/') ||
        url.pathname === '/api/admin/stats' ||
        url.pathname === '/api/admin/partners' ||
        url.pathname.startsWith('/api/admin/partners/') ||
        url.pathname === '/api/admin/commission-report' ||
        url.pathname.startsWith('/api/admin/payments/manual') ||
        url.pathname.startsWith('/api/admin/applications')
      ) {
        // CTO 2026-05-12 unified login (Commit C):
        //   Stop injecting X-Admin-Token for referrals admin routes. referrals-api
        //   now validates the user session via Service Binding to social-api
        //   (requireAdminViaSession). Forward Authorization + Cookie headers
        //   UNTOUCHED so the worker can extract Bearer/social_session.
        //
        //   LEGACY_ADMIN_TOKEN_ENABLED=true on referrals-api keeps the X-Admin-Token
        //   fallback alive for 1-week rollback window, BUT we no longer mint it
        //   here — the only callers using it now are deliberate (out-of-band ops
        //   scripts, etc.), which is the desired pruning.
        //
        //   The X-Admin-Token injection for /api/admin/clients/* below is
        //   UNCHANGED (different path family, different worker).
        // Day 2 Track D: fire-and-forget shadow probe for referrals dashboard.
        // The actual auth check is done downstream by referrals-api itself
        // (requireAdminViaSession via Service Binding to social-api). We probe
        // BOTH legacy (social-api) AND new (referrals-api/internal/validate-session
        // — landing on Day 3 from Track B's held branch) so the comparison
        // dataset includes referrals-target traffic.
        //
        // ctx.waitUntil keeps the probe alive past response without blocking.
        // If ctx is unavailable (e.g. internal call shapes), we still await
        // briefly via .catch-to-ignore to avoid losing the sample.
        try {
          const shadowFn = validateLeaderSessionShadow(request, env);
          if (ctx && typeof ctx.waitUntil === 'function') {
            ctx.waitUntil(shadowFn.catch(() => {}));
          } else {
            // best-effort: don't block the proxy hop
            shadowFn.catch(() => {});
          }
        } catch { /* never throw from shadow path */ }

        const workerPath = url.pathname.replace('/api/admin', '/admin');
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const proxyHeaders = new Headers(request.headers);
        // No X-Admin-Token injection. Authorization + Cookie pass through.
        const resp = await fetch(new Request(workerUrl, {
          method: request.method, headers: proxyHeaders,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin clients + invites endpoints → admin-api Worker (D1 purebrain-social shared)
      // Apr 23 split (commit 8474bc8) added admin-api routes but never wired the proxy.
      // This routes the six P0 endpoints (PATCH client, invite CRUD) that were 404ing.
      // CONSTRAINT: throwaway bridge code — Tier 3 Phase 9 deletes this whole admin block.
      // CTO pre-build approved 2026-05-08: HTTP+token (NOT Service Bindings — admin-api deletion ~2 weeks).
      //
      // SECURITY GATE (2026-05-09 CTO spec, post-V11-rotation finding):
      //   Before injecting env.ADMIN_TOKEN, validate the caller has a leader
      //   session via the CLIENTS_API Service Binding. Closes the anonymous
      //   data-exposure bug where curl with no auth received the full invitee
      //   list (including role:leader invite tokens). PUBLIC EXCEPTION:
      //   /api/admin/validate-token is intentionally unauthenticated (powers
      //   invite-landing before sign-in — admin-api worker.js:404).
      // Day 2 Track D: shadow-auth live readout (admin-gated).
      // Returns aggregated stats from the in-isolate ring buffer.
      // For fleet-wide readout use scripts/shadow-auth-readout.sh (wrangler tail).
      if (url.pathname === '/admin/shadow-auth-readout') {
        return shadowAuthReadout(request, env);
      }
      if (
        url.pathname.startsWith('/api/admin/clients') ||
        url.pathname.startsWith('/api/admin/invite') ||
        url.pathname.startsWith('/api/admin/invites') ||
        url.pathname === '/api/admin/validate-token'
      ) {
        if (url.pathname !== '/api/admin/validate-token') {
          // Day 2 Track D: shadow-wrap the validator. Legacy still wins.
          // The shadow leg calls clients-api/internal/validate-session
          // and logs the comparison. Zero behavior change.
          const gate = await validateLeaderSessionShadow(request, env);
          if (!gate.ok) {
            const errBody = gate.status === 403
              ? '{"error":"forbidden"}'
              : (gate.status === 503 ? '{"error":"auth_unavailable"}' : '{"error":"unauthorized"}');
            return new Response(errBody, {
              status: gate.status,
              headers: {
                'content-type': 'application/json',
                'Access-Control-Allow-Origin': '*',
              },
            });
          }
        }
        const workerUrl = `https://admin-api.in0v8.workers.dev${url.pathname}${url.search}`;
        const proxyHeaders = new Headers(request.headers);
        if (env.ADMIN_TOKEN) {
          proxyHeaders.set('X-Admin-Token', env.ADMIN_TOKEN);
        }
        const resp = await fetch(new Request(workerUrl, {
          method: request.method,
          headers: proxyHeaders,
          body: (request.method !== 'GET' && request.method !== 'HEAD' && request.method !== 'OPTIONS') ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin client endpoints → social-api Worker (D1)
      if (url.pathname.startsWith('/api/admin/')) {
        const workerUrl = `https://social-api.in0v8.workers.dev${url.pathname}${url.search}`;
        const resp = await fetch(new Request(workerUrl, {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
    }

    // voice.purebrain.ai routing:
    //   /tts/* and /health → proxy to Hetzner VPS port 8950 (SSH-forwarded to Vast.ai GPU)
    //   everything else → CF Pages voice-manager UI
    if (subdomain === 'voice') {
      if (url.pathname.startsWith('/tts') || url.pathname === '/health') {
        if (request.method === 'OPTIONS') {
          return new Response(null, { status: 204, headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400',
          }});
        }
        // Route TTS API calls through tts.purebrain.ai (Argo Tunnel → Hetzner → Vast.ai GPU)
        const ttsUrl = `https://tts.purebrain.ai${url.pathname}${url.search}`;
        const ttsReq = new Request(ttsUrl, {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        });
        const resp = await fetch(ttsReq);
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        respHeaders.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        respHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Voice manager UI
      const voicePath = url.pathname === '/' ? '/voice-manager/' : '/voice-manager' + url.pathname;
      const rewrittenUrl = new URL(voicePath, 'https://purebrain.ai');
      rewrittenUrl.search = url.search;
      const newReq = new Request(rewrittenUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
      });
      return fetch(newReq);
    }

    // System subdomain — pass through to Cloudflare routing (tunnel handles these).
    if (!isPortalSubdomain(subdomain)) {
      return fetch(request);
    }

    // Portal subdomain — proxy to {subdomain}.ai-civ.com on Witness.
    const targetHost = `${subdomain}.${CONTAINER_DOMAIN}`;

    try {
      return await proxyToContainer(request, targetHost, host);
    } catch (err) {
      return new Response(
        `Portal unavailable. Your portal "${subdomain}" may still be initializing. ` +
          `Please try again in a few minutes. (Error: ${err.message})`,
        {
          status: 502,
          headers: { 'Content-Type': 'text/plain' },
        }
      );
    }
  },
};
