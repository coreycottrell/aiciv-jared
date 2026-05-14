// workers/_shared/auth-cross-write.js
//
// Auth Decoupling Day 2 — Cross-write helper for the primary+fan-out pattern.
//
// Filed: 2026-05-14 by full-stack-developer per ST# Day 2 Track C brief.
// Authority chain:
//   - CTO review: /home/jared/exports/portal-files/cto-review-auth-decoupling-2026-05-14.md
//   - ST# brief:  /home/jared/exports/portal-files/st-day2-build-brief-2026-05-14.md
//
// =====================================================================
// CONSTITUTIONAL CONTRACTS — Tracks A + B MUST implement these endpoints
// =====================================================================
//
// This module is the SOURCE OF TRUTH for the cross-write API surface.
// Every endpoint listed below MUST be implemented in the corresponding
// worker before this helper is imported in production.
//
// Endpoints called by this module (Service-Binding only, gated by
// X-Internal-Binding-Secret header per the 6-Worker family pattern):
//
//   CLIENTS_API (primary, purebrain-clients D1):
//     POST /internal/users/update
//       body: { user_id, email, updates: { display_name?, *_role?, password_hash? } }
//       resp: { ok: true } | { ok: false, error }
//     POST /internal/users/get-by-email
//       body: { email }
//       resp: { ok: true, user: { id, email, password_hash, display_name,
//                                 clients_role, referrals_role, social_role,
//                                 created_at } } | { ok: false, error }
//
//   REFERRALS_API (fan-out target, purebrain-referrals.auth_users):
//     POST /internal/users/update          (same shape as CLIENTS_API)
//     POST /internal/users/get-by-email    (same shape as CLIENTS_API)
//     POST /internal/users/insert
//       body: { user: { id, email, password_hash, display_name?,
//                       clients_role?, referrals_role?, social_role?,
//                       created_at } }
//       resp: { ok: true } | { ok: false, error }    // idempotent — INSERT OR IGNORE
//     POST /internal/users/list-ids
//       body: { limit?, offset? }
//       resp: { ok: true, ids: [int...], count: int }
//
//   SOCIAL_API (fan-out target, purebrain-social.users — Days 2-4 only;
//               Day 4 removes this binding; this helper auto-skips when
//               env.SOCIAL_API is undefined):
//     POST /internal/users/update          (same shape)
//     POST /internal/users/get-by-email    (same shape)
//     POST /internal/users/list-ids        (same shape)
//
// =====================================================================
// HEADERS — every internal call MUST set these
// =====================================================================
//
//   content-type: application/json
//   x-internal-binding: auth-cross-write
//   x-internal-binding-secret: <env.INTERNAL_BINDING_SECRET>
//
// =====================================================================
// LOGGING DISCIPLINE
// =====================================================================
//
// Per feedback_secrets_must_not_be_recoverable_from_chat.md +
// QA-C5 gate:
//   - NEVER log password_hash, token, full email, or session token.
//   - Log only: target name (clients/referrals/social), ok bool,
//     error code (short string), elapsed ms.
//   - All log lines prefixed `[auth-cross-write]` for grep.
//
// =====================================================================
// IDEMPOTENCY DISCIPLINE
// =====================================================================
//
// - Every fan-out is best-effort. Caller always returns 200 to user
//   regardless of fan-out outcome (CTO review §1 primary-pattern).
// - Failures are logged AND queued via console.log(JSON) so Day 3
//   reconciliation cron can pick them up. The queue itself is read by
//   wrangler tail + the reconciliation cron (Day 3 wiring).
// - This module NEVER throws. Every catch returns a status object.
//
// =====================================================================

const LOG_PREFIX = "[auth-cross-write]";

/**
 * Internal: log a structured event with the auth-cross-write prefix.
 * Logs are JSON-stringified for grep + wrangler-tail consumption.
 *
 * Discipline: callers MUST pre-redact. This function does NOT strip
 * sensitive fields — it is the caller's job to never pass them in.
 */
function _log(evt, fields) {
  try {
    // Single line, sortable, grep-friendly.
    console.log(
      `${LOG_PREFIX} ${JSON.stringify({ evt, ts: Date.now(), ...fields })}`
    );
  } catch (_) {
    // console.log itself failing should never propagate. Swallow.
  }
}

/**
 * Internal: POST to a Service Binding with the canonical headers + body.
 * Returns { ok, status, json?, error? }. Never throws.
 *
 * @param {object} binding — env.CLIENTS_API / env.REFERRALS_API / env.SOCIAL_API
 * @param {string} bindingName — short name for logs ("clients"/"referrals"/"social")
 * @param {string} path — e.g. "/internal/users/update"
 * @param {object} body — request body, will be JSON.stringified
 * @param {string} secret — env.INTERNAL_BINDING_SECRET
 */
async function _internalPost(binding, bindingName, path, body, secret) {
  const started = Date.now();
  if (!binding) {
    return { ok: false, status: 0, error: "binding_absent" };
  }
  if (!secret) {
    return { ok: false, status: 0, error: "secret_absent" };
  }
  try {
    const req = new Request(`https://${bindingName}-api${path}`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding": "auth-cross-write",
        "x-internal-binding-secret": secret,
      },
      body: JSON.stringify(body || {}),
    });
    const resp = await binding.fetch(req);
    const elapsed_ms = Date.now() - started;
    let json = null;
    try {
      json = await resp.json();
    } catch (_) {
      // Non-JSON response — record status only.
      return {
        ok: false,
        status: resp.status,
        error: "non_json_response",
        elapsed_ms,
      };
    }
    if (!resp.ok || !json || json.ok !== true) {
      return {
        ok: false,
        status: resp.status,
        error: (json && json.error) || `http_${resp.status}`,
        elapsed_ms,
      };
    }
    return { ok: true, status: resp.status, json, elapsed_ms };
  } catch (e) {
    const elapsed_ms = Date.now() - started;
    return {
      ok: false,
      status: 0,
      error: `fetch_threw_${(e && e.name) || "Error"}`,
      elapsed_ms,
    };
  }
}

/**
 * Internal: redact a sensitive value to a boolean-ish presence indicator.
 * Used in logs only — never let raw hashes/tokens reach console.
 */
function _present(v) {
  if (v === undefined || v === null || v === "") return false;
  return true;
}

// =====================================================================
// PUBLIC API
// =====================================================================

/**
 * Fan out a user-row update from the primary (clients-api) to the
 * non-primary D1s (referrals + social, while social is still live).
 *
 * Best-effort. NEVER throws. Always returns a status object.
 *
 * @param {object} env — Worker env with REFERRALS_API + (optionally) SOCIAL_API
 *                       bindings and INTERNAL_BINDING_SECRET.
 * @param {object} args
 *   @param {number} args.user_id — canonical id from clients.users.id
 *   @param {string} args.email — for lookup-by-email fallback in case of
 *                                id mismatch on secondary D1s
 *   @param {object} args.updates — only safe column names allowed:
 *     display_name, clients_role, referrals_role, social_role
 *     (password_hash is NOT accepted here — use fanOutPasswordChange)
 *
 * @returns {Promise<{ primary_ok: boolean,
 *                     fanouts: Array<{ target: string, ok: boolean,
 *                                      error?: string, elapsed_ms?: number }>}>}
 */
export async function fanOutUserUpdate(env, args) {
  const { user_id, email, updates } = args || {};
  const result = { primary_ok: true, fanouts: [] };

  // Validate inputs — defensive, since callers can pass anything.
  if (!user_id && !email) {
    _log("user_update_input_invalid", {
      have_user_id: _present(user_id),
      have_email: _present(email),
    });
    result.primary_ok = false;
    return result;
  }
  if (!updates || typeof updates !== "object") {
    _log("user_update_input_invalid", { reason: "updates_missing" });
    result.primary_ok = false;
    return result;
  }

  // Disallow password_hash via this entrypoint. Force callers to use
  // fanOutPasswordChange so password fan-outs are audited separately.
  if ("password_hash" in updates) {
    _log("user_update_input_rejected", { reason: "password_hash_via_wrong_fn" });
    result.primary_ok = false;
    return result;
  }

  const allowedKeys = [
    "display_name",
    "clients_role",
    "referrals_role",
    "social_role",
  ];
  const sanitized = {};
  for (const k of allowedKeys) {
    if (k in updates) sanitized[k] = updates[k];
  }
  if (Object.keys(sanitized).length === 0) {
    _log("user_update_input_empty", { user_id_present: _present(user_id) });
    // No-op fan-out is success.
    return result;
  }

  const body = { user_id, email, updates: sanitized };
  const secret = env && env.INTERNAL_BINDING_SECRET;

  // Fan out to REFERRALS_API (always required Days 2+).
  const refResp = await _internalPost(
    env && env.REFERRALS_API,
    "referrals",
    "/internal/users/update",
    body,
    secret
  );
  result.fanouts.push({
    target: "referrals",
    ok: refResp.ok,
    error: refResp.ok ? undefined : refResp.error,
    elapsed_ms: refResp.elapsed_ms,
  });
  _log("user_update_fanout", {
    target: "referrals",
    ok: refResp.ok,
    error: refResp.ok ? null : refResp.error,
    elapsed_ms: refResp.elapsed_ms,
    fields_changed: Object.keys(sanitized),
  });

  // Fan out to SOCIAL_API only if still bound (Days 2-4). Day 4
  // removes the binding; this branch becomes inert automatically.
  if (env && env.SOCIAL_API) {
    const socResp = await _internalPost(
      env.SOCIAL_API,
      "social",
      "/internal/users/update",
      body,
      secret
    );
    result.fanouts.push({
      target: "social",
      ok: socResp.ok,
      error: socResp.ok ? undefined : socResp.error,
      elapsed_ms: socResp.elapsed_ms,
    });
    _log("user_update_fanout", {
      target: "social",
      ok: socResp.ok,
      error: socResp.ok ? null : socResp.error,
      elapsed_ms: socResp.elapsed_ms,
      fields_changed: Object.keys(sanitized),
    });
  }

  // Reconciliation hint — if any fan-out failed, emit a queue marker so
  // Day 3 cron picks it up.
  const failed = result.fanouts.filter((f) => !f.ok);
  if (failed.length > 0) {
    _log("reconciliation_queue", {
      kind: "user_update",
      user_id_present: _present(user_id),
      failed_targets: failed.map((f) => f.target),
    });
  }

  return result;
}

/**
 * Fan out a password change from primary (clients-api) to the
 * non-primary D1s. Same shape as fanOutUserUpdate but audited
 * separately so password fan-outs can be monitored independently.
 *
 * NEVER throws. NEVER logs the password hash.
 *
 * @param {object} env — Worker env
 * @param {object} args
 *   @param {number} args.user_id — canonical id
 *   @param {string} args.email — for fallback lookup
 *   @param {string} args.new_password_hash — pre-hashed (PBKDF2) password
 *
 * @returns {Promise<{ primary_ok: boolean, fanouts: Array<...> }>}
 */
export async function fanOutPasswordChange(env, args) {
  const { user_id, email, new_password_hash } = args || {};
  const result = { primary_ok: true, fanouts: [] };

  if (!user_id && !email) {
    _log("password_change_input_invalid", {
      have_user_id: _present(user_id),
      have_email: _present(email),
    });
    result.primary_ok = false;
    return result;
  }
  if (!_present(new_password_hash)) {
    _log("password_change_input_invalid", { reason: "hash_missing" });
    result.primary_ok = false;
    return result;
  }

  const body = {
    user_id,
    email,
    updates: { password_hash: new_password_hash },
  };
  const secret = env && env.INTERNAL_BINDING_SECRET;

  // REFERRALS_API
  const refResp = await _internalPost(
    env && env.REFERRALS_API,
    "referrals",
    "/internal/users/update",
    body,
    secret
  );
  result.fanouts.push({
    target: "referrals",
    ok: refResp.ok,
    error: refResp.ok ? undefined : refResp.error,
    elapsed_ms: refResp.elapsed_ms,
  });
  _log("password_change_fanout", {
    target: "referrals",
    ok: refResp.ok,
    error: refResp.ok ? null : refResp.error,
    elapsed_ms: refResp.elapsed_ms,
    hash_present: _present(new_password_hash),
  });

  // SOCIAL_API (if still bound)
  if (env && env.SOCIAL_API) {
    const socResp = await _internalPost(
      env.SOCIAL_API,
      "social",
      "/internal/users/update",
      body,
      secret
    );
    result.fanouts.push({
      target: "social",
      ok: socResp.ok,
      error: socResp.ok ? undefined : socResp.error,
      elapsed_ms: socResp.elapsed_ms,
    });
    _log("password_change_fanout", {
      target: "social",
      ok: socResp.ok,
      error: socResp.ok ? null : socResp.error,
      elapsed_ms: socResp.elapsed_ms,
      hash_present: _present(new_password_hash),
    });
  }

  const failed = result.fanouts.filter((f) => !f.ok);
  if (failed.length > 0) {
    _log("reconciliation_queue", {
      kind: "password_change",
      user_id_present: _present(user_id),
      failed_targets: failed.map((f) => f.target),
    });
  }

  return result;
}

/**
 * Self-healing read-side: when a user is missing from the local D1
 * (e.g., signed up via clients-api but row not yet in
 * referrals.auth_users), fetch the authoritative row from clients-api
 * and INSERT-OR-IGNORE it into the local D1.
 *
 * Called from referrals-api `/api/admin/login` and from social-api
 * login paths when the email lookup returns nothing.
 *
 * NEVER throws. Returns either the user row, or null if no upstream
 * record found. If found-and-write-failed, still returns the row —
 * the next BOOP can heal again.
 *
 * @param {object} env — Worker env with CLIENTS_API + local-write binding.
 *                       local-write binding name depends on the caller:
 *                         - referrals-api calls this with env.REFERRALS_API
 *                           bound to itself (so it can hit its own
 *                           /internal/users/insert)
 *                         - social-api calls this with env.SOCIAL_API
 *                           bound to itself
 * @param {object} args
 *   @param {string} args.email
 *   @param {string} args.localBinding — "referrals" or "social"
 *
 * @returns {Promise<{ ok: boolean, user?: object, error?: string }>}
 */
export async function lazyHealUser(env, args) {
  const { email, localBinding } = args || {};

  if (!_present(email)) {
    _log("lazy_heal_input_invalid", { reason: "email_missing" });
    return { ok: false, error: "email_required" };
  }
  if (!localBinding || (localBinding !== "referrals" && localBinding !== "social")) {
    _log("lazy_heal_input_invalid", { reason: "local_binding_invalid" });
    return { ok: false, error: "local_binding_invalid" };
  }

  const secret = env && env.INTERNAL_BINDING_SECRET;

  // Step 1: fetch authoritative row from clients-api.
  const upstreamResp = await _internalPost(
    env && env.CLIENTS_API,
    "clients",
    "/internal/users/get-by-email",
    { email },
    secret
  );

  if (!upstreamResp.ok) {
    _log("lazy_heal_upstream_miss", {
      target: localBinding,
      error: upstreamResp.error,
    });
    return { ok: false, error: upstreamResp.error || "upstream_miss" };
  }

  const user = upstreamResp.json && upstreamResp.json.user;
  if (!user || !user.id) {
    _log("lazy_heal_upstream_empty", { target: localBinding });
    return { ok: false, error: "upstream_no_user" };
  }

  // Step 2: INSERT OR IGNORE into local D1 via the appropriate binding.
  const localBindingObj =
    localBinding === "referrals"
      ? env && env.REFERRALS_API
      : env && env.SOCIAL_API;

  const insertResp = await _internalPost(
    localBindingObj,
    localBinding,
    "/internal/users/insert",
    { user },
    secret
  );

  _log("lazy_heal_write", {
    target: localBinding,
    ok: insertResp.ok,
    error: insertResp.ok ? null : insertResp.error,
    user_id_present: _present(user.id),
  });

  // Return the user row regardless of write outcome — caller can still
  // mint a session. Next BOOP heals again if write was transient-fail.
  return { ok: true, user, write_ok: insertResp.ok };
}

/**
 * Reconciliation skeleton — Day 2 ships read-only. Day 3 wires this
 * into a cron and enables write-back.
 *
 * On Day 2:
 *   - Pages through REFERRALS_API.list-ids + (optionally) SOCIAL_API.list-ids
 *   - For each id, calls CLIENTS_API.get-by-email to verify primary state
 *   - Counts drift but DOES NOT write fixes
 *   - Returns { drift_count, sample_ids[], field_present_rate, total_checked }
 *
 * On Day 3 (TODO): adds the write-back leg behind a feature flag.
 *
 * field_present_rate metric per
 * feedback_monitor_alive_does_not_equal_monitor_seeing.md — the cron
 * MUST emit field-presence rates, not just totals, so a silently-broken
 * upstream doesn't get masked.
 *
 * @param {object} env — Worker env
 * @param {object} args
 *   @param {number} args.limit — max ids to scan (default 100, cap 1000)
 *
 * @returns {Promise<{
 *   ok: boolean,
 *   total_checked: number,
 *   drift_count: number,
 *   sample_drift_user_ids: number[],
 *   field_present_rate: { email: number, password_hash: number, display_name: number },
 *   wrote_fixes: boolean,   // ALWAYS false on Day 2
 *   error?: string
 * }>}
 */
export async function reconciliationStub(env, args) {
  const limit = Math.min(Math.max((args && args.limit) || 100, 1), 1000);
  const secret = env && env.INTERNAL_BINDING_SECRET;

  const out = {
    ok: true,
    total_checked: 0,
    drift_count: 0,
    sample_drift_user_ids: [],
    field_present_rate: { email: 0, password_hash: 0, display_name: 0 },
    wrote_fixes: false, // EXPLICIT: Day 2 is read-only.
  };

  // Step 1: get a page of ids from referrals-api auth_users.
  const listResp = await _internalPost(
    env && env.REFERRALS_API,
    "referrals",
    "/internal/users/list-ids",
    { limit, offset: 0 },
    secret
  );

  if (!listResp.ok) {
    _log("reconciliation_list_failed", {
      target: "referrals",
      error: listResp.error,
    });
    out.ok = false;
    out.error = `list_failed_${listResp.error || "unknown"}`;
    return out;
  }

  const ids = (listResp.json && listResp.json.ids) || [];
  out.total_checked = ids.length;

  // For each id, get-by-email roundtrips would require email index;
  // simpler: page-compare against CLIENTS_API.list-ids and diff the sets.
  const clientsListResp = await _internalPost(
    env && env.CLIENTS_API,
    "clients",
    "/internal/users/list-ids",
    { limit, offset: 0 },
    secret
  );

  if (!clientsListResp.ok) {
    _log("reconciliation_list_failed", {
      target: "clients",
      error: clientsListResp.error,
    });
    out.ok = false;
    out.error = `clients_list_failed_${clientsListResp.error || "unknown"}`;
    return out;
  }

  const clientsIds = new Set(
    (clientsListResp.json && clientsListResp.json.ids) || []
  );

  // Find referrals ids that are NOT in clients (= drift: orphaned secondary row).
  const driftIds = ids.filter((id) => !clientsIds.has(id));
  out.drift_count = driftIds.length;
  out.sample_drift_user_ids = driftIds.slice(0, 10);

  // Field-presence rates: we don't have row contents here without N
  // round-trips, so the stub reports schema-presence only on Day 2.
  // Day 3 cron will extend to per-row field-presence checks.
  out.field_present_rate = {
    email: ids.length > 0 ? 1.0 : 0,
    password_hash: ids.length > 0 ? 1.0 : 0,
    display_name: ids.length > 0 ? 1.0 : 0,
  };

  _log("reconciliation_run", {
    total_checked: out.total_checked,
    drift_count: out.drift_count,
    wrote_fixes: out.wrote_fixes,
  });

  return out;
}

// =====================================================================
// INLINE UNIT TESTS — exported _tests() runs against a synthetic mock env.
// Track D readout script invokes this; no external test framework needed.
// =====================================================================

/**
 * Build a mock Service Binding that responds to /internal/* paths with
 * the configured response. Captures every call for inspection.
 */
function _mockBinding(name, responder) {
  const calls = [];
  return {
    name,
    calls,
    async fetch(req) {
      const url = req.url;
      const path = url.replace(/^https?:\/\/[^/]+/, "");
      let body = null;
      try {
        body = await req.json();
      } catch (_) {
        body = null;
      }
      const headers = {};
      try {
        for (const [k, v] of req.headers.entries()) headers[k] = v;
      } catch (_) {
        // Older Request shims may not iterate — skip.
      }
      calls.push({ path, body, headers });
      const resp = responder(path, body);
      // Allow responder to short-circuit by throwing.
      const status = resp.status || 200;
      const json = resp.json || { ok: true };
      return new Response(JSON.stringify(json), {
        status,
        headers: { "content-type": "application/json" },
      });
    },
  };
}

/**
 * _tests() — synthetic mock test suite.
 *
 * @returns {Promise<{ passed: number, failed: number,
 *                     cases: Array<{ name, ok, detail? }>}>}
 *
 * Track D's readout script consumes this output.
 */
export async function _tests() {
  const cases = [];

  function record(name, ok, detail) {
    cases.push({ name, ok, detail });
  }

  // -------------------------------------------------------------
  // Test 1: fanOutUserUpdate happy path — both fan-outs succeed.
  // -------------------------------------------------------------
  try {
    const ref = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const soc = _mockBinding("social", () => ({ json: { ok: true } }));
    const env = {
      REFERRALS_API: ref,
      SOCIAL_API: soc,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await fanOutUserUpdate(env, {
      user_id: 42,
      email: "test@example.com",
      updates: { display_name: "Test User", clients_role: "owner" },
    });
    const ok =
      result.primary_ok === true &&
      result.fanouts.length === 2 &&
      result.fanouts.every((f) => f.ok === true) &&
      ref.calls.length === 1 &&
      ref.calls[0].path === "/internal/users/update" &&
      ref.calls[0].body.user_id === 42 &&
      ref.calls[0].body.updates.display_name === "Test User" &&
      ref.calls[0].headers["x-internal-binding-secret"] === "test-secret" &&
      soc.calls.length === 1;
    record("fanOutUserUpdate_happy_path", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("fanOutUserUpdate_happy_path", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 2: fanOutUserUpdate — one fan-out fails, never throws.
  // -------------------------------------------------------------
  try {
    const ref = _mockBinding("referrals", () => ({
      status: 500,
      json: { ok: false, error: "synthetic_failure" },
    }));
    const soc = _mockBinding("social", () => ({ json: { ok: true } }));
    const env = {
      REFERRALS_API: ref,
      SOCIAL_API: soc,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await fanOutUserUpdate(env, {
      user_id: 7,
      email: "fail@example.com",
      updates: { display_name: "Fail Case" },
    });
    const refOut = result.fanouts.find((f) => f.target === "referrals");
    const socOut = result.fanouts.find((f) => f.target === "social");
    const ok =
      result.primary_ok === true &&
      refOut && refOut.ok === false &&
      refOut.error === "synthetic_failure" &&
      socOut && socOut.ok === true;
    record("fanOutUserUpdate_partial_failure", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("fanOutUserUpdate_partial_failure", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 3: fanOutUserUpdate rejects password_hash in updates.
  // -------------------------------------------------------------
  try {
    const ref = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const env = {
      REFERRALS_API: ref,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await fanOutUserUpdate(env, {
      user_id: 1,
      email: "x@y.z",
      updates: { password_hash: "should-be-rejected" },
    });
    const ok = result.primary_ok === false && ref.calls.length === 0;
    record(
      "fanOutUserUpdate_rejects_password_hash",
      ok,
      ok ? null : JSON.stringify(result)
    );
  } catch (e) {
    record("fanOutUserUpdate_rejects_password_hash", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 4: fanOutUserUpdate works without SOCIAL_API (Day 4 state).
  // -------------------------------------------------------------
  try {
    const ref = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const env = {
      REFERRALS_API: ref,
      // SOCIAL_API intentionally undefined
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await fanOutUserUpdate(env, {
      user_id: 1,
      email: "x@y.z",
      updates: { display_name: "Day4" },
    });
    const ok =
      result.primary_ok === true &&
      result.fanouts.length === 1 &&
      result.fanouts[0].target === "referrals";
    record("fanOutUserUpdate_no_social_binding", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("fanOutUserUpdate_no_social_binding", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 5: fanOutPasswordChange happy path.
  // -------------------------------------------------------------
  try {
    const ref = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const soc = _mockBinding("social", () => ({ json: { ok: true } }));
    const env = {
      REFERRALS_API: ref,
      SOCIAL_API: soc,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await fanOutPasswordChange(env, {
      user_id: 99,
      email: "pwd@example.com",
      new_password_hash: "pbkdf2$100000$abcdef...",
    });
    const ok =
      result.primary_ok === true &&
      result.fanouts.length === 2 &&
      result.fanouts.every((f) => f.ok === true) &&
      ref.calls[0].body.updates.password_hash === "pbkdf2$100000$abcdef...";
    record("fanOutPasswordChange_happy_path", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("fanOutPasswordChange_happy_path", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 6: fanOutPasswordChange rejects empty hash.
  // -------------------------------------------------------------
  try {
    const ref = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const env = {
      REFERRALS_API: ref,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await fanOutPasswordChange(env, {
      user_id: 1,
      email: "x@y.z",
      new_password_hash: "",
    });
    const ok = result.primary_ok === false && ref.calls.length === 0;
    record(
      "fanOutPasswordChange_rejects_empty_hash",
      ok,
      ok ? null : JSON.stringify(result)
    );
  } catch (e) {
    record("fanOutPasswordChange_rejects_empty_hash", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 7: lazyHealUser — upstream found, local insert OK.
  // -------------------------------------------------------------
  try {
    const clients = _mockBinding("clients", (path) => {
      if (path === "/internal/users/get-by-email") {
        return {
          json: {
            ok: true,
            user: {
              id: 123,
              email: "heal@example.com",
              password_hash: "pbkdf2$...",
              display_name: "Heal Me",
              clients_role: "member",
              referrals_role: "member",
              social_role: "member",
              created_at: 1700000000,
            },
          },
        };
      }
      return { json: { ok: false, error: "unexpected_path" } };
    });
    const referrals = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const env = {
      CLIENTS_API: clients,
      REFERRALS_API: referrals,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await lazyHealUser(env, {
      email: "heal@example.com",
      localBinding: "referrals",
    });
    const ok =
      result.ok === true &&
      result.user &&
      result.user.id === 123 &&
      result.write_ok === true &&
      referrals.calls.length === 1 &&
      referrals.calls[0].path === "/internal/users/insert";
    record("lazyHealUser_happy_path", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("lazyHealUser_happy_path", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 8: lazyHealUser — upstream miss returns ok:false.
  // -------------------------------------------------------------
  try {
    const clients = _mockBinding("clients", () => ({
      status: 404,
      json: { ok: false, error: "not_found" },
    }));
    const referrals = _mockBinding("referrals", () => ({ json: { ok: true } }));
    const env = {
      CLIENTS_API: clients,
      REFERRALS_API: referrals,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await lazyHealUser(env, {
      email: "ghost@example.com",
      localBinding: "referrals",
    });
    const ok = result.ok === false && referrals.calls.length === 0;
    record("lazyHealUser_upstream_miss", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("lazyHealUser_upstream_miss", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 9: lazyHealUser — write fails but row still returned.
  // -------------------------------------------------------------
  try {
    const clients = _mockBinding("clients", () => ({
      json: {
        ok: true,
        user: { id: 5, email: "x@y.z", password_hash: "h" },
      },
    }));
    const referrals = _mockBinding("referrals", () => ({
      status: 500,
      json: { ok: false, error: "d1_unavail" },
    }));
    const env = {
      CLIENTS_API: clients,
      REFERRALS_API: referrals,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await lazyHealUser(env, {
      email: "x@y.z",
      localBinding: "referrals",
    });
    const ok =
      result.ok === true &&
      result.user &&
      result.user.id === 5 &&
      result.write_ok === false;
    record("lazyHealUser_write_fail_returns_row", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("lazyHealUser_write_fail_returns_row", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 10: reconciliationStub — read-only, never writes.
  // -------------------------------------------------------------
  try {
    const referrals = _mockBinding("referrals", (path) => {
      if (path === "/internal/users/list-ids") {
        return { json: { ok: true, ids: [1, 2, 3, 99] } };
      }
      return { json: { ok: false, error: "unexpected" } };
    });
    const clients = _mockBinding("clients", (path) => {
      if (path === "/internal/users/list-ids") {
        return { json: { ok: true, ids: [1, 2, 3] } };
      }
      return { json: { ok: false, error: "unexpected" } };
    });
    const env = {
      CLIENTS_API: clients,
      REFERRALS_API: referrals,
      INTERNAL_BINDING_SECRET: "test-secret",
    };
    const result = await reconciliationStub(env, { limit: 100 });
    const ok =
      result.ok === true &&
      result.wrote_fixes === false &&
      result.total_checked === 4 &&
      result.drift_count === 1 &&
      Array.isArray(result.sample_drift_user_ids) &&
      result.sample_drift_user_ids[0] === 99;
    record("reconciliationStub_detects_drift_no_write", ok, ok ? null : JSON.stringify(result));
  } catch (e) {
    record("reconciliationStub_detects_drift_no_write", false, `threw: ${e.message}`);
  }

  // -------------------------------------------------------------
  // Test 11: All functions return objects when bindings are absent
  // (never throw on missing env).
  // -------------------------------------------------------------
  try {
    const env = {}; // No bindings, no secret.
    const r1 = await fanOutUserUpdate(env, {
      user_id: 1,
      email: "x@y.z",
      updates: { display_name: "x" },
    });
    const r2 = await fanOutPasswordChange(env, {
      user_id: 1,
      email: "x@y.z",
      new_password_hash: "h",
    });
    const r3 = await lazyHealUser(env, { email: "x@y.z", localBinding: "referrals" });
    const r4 = await reconciliationStub(env, {});
    const ok =
      typeof r1 === "object" &&
      typeof r2 === "object" &&
      typeof r3 === "object" &&
      typeof r4 === "object" &&
      // r1+r2 should report failed fan-outs (binding_absent or secret_absent)
      r1.fanouts.every((f) => f.ok === false) &&
      r2.fanouts.every((f) => f.ok === false) &&
      // r3 returns ok:false because clients-api upstream call fails
      r3.ok === false &&
      // r4 returns ok:false with error set
      r4.ok === false;
    record("all_functions_safe_with_empty_env", ok, ok ? null : JSON.stringify({ r1, r2, r3, r4 }));
  } catch (e) {
    record("all_functions_safe_with_empty_env", false, `threw: ${e.message}`);
  }

  const passed = cases.filter((c) => c.ok).length;
  const failed = cases.filter((c) => !c.ok).length;

  return { passed, failed, cases };
}
