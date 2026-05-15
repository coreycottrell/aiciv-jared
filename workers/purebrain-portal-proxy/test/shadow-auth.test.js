// workers/purebrain-portal-proxy/test/shadow-auth.test.js
//
// Day 2 Track D — Synthetic test that proves the shadow-auth wrapper
//   1. calls BOTH legacy AND new paths
//   2. compares the two results with PII-safe presence flags only
//   3. ALWAYS returns the legacy result unchanged
//   4. NEVER throws into the caller
//   5. logs structured JSON with evt=shadow_auth that the readout
//      script can parse
//
// Runs without a test framework — node --test or `node shadow-auth.test.js`.
//
// IMPORTANT: this is a behavioral test that exercises the wrapper as if
// it lived in a real Worker. We import the worker module's helper
// functions by reading the worker.js source, extracting the relevant
// exports as new Function bindings. The wrapper functions in worker.js
// are NOT exported (Workers entry is `default { fetch }`), so we
// tunnel-test by attaching them to globalThis via a controlled eval
// shim. This keeps the production code free of test-only exports.

import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const WORKER_PATH = resolve(__dirname, "..", "src", "worker.js");

// Pull the worker source and extract the named helper functions by
// rewriting them into a CommonJS-style module we can `await import`.
// We rewrite `export default { ... }` to a no-op and tack on
// `globalThis.__shadowAuthTestHandle = { ... }` for the helpers we need.
const src = readFileSync(WORKER_PATH, "utf-8");

const TEST_EXPORT_BLOCK = `
globalThis.__shadowAuthTestHandle = {
  shadowDashboardTarget,
  validateLeaderSession,
  validateLeaderSessionShadow,
  shadowAuthReadout,
  _present,
};
`;

// We need to run the worker.js source so that the helper functions become
// available. Strip the `export default` block (the fetch handler is for
// runtime, not for tests) and append the test export block.
const cleaned = src.replace(/export default \{[\s\S]*?\};\s*$/m, "");
const program = cleaned + "\n" + TEST_EXPORT_BLOCK;

// Use a fresh Function with our augmented source. This avoids polluting
// the host module scope with worker globals.
const wrap = new Function(program);
wrap.call({}); // executes the worker.js helpers + sets globalThis handle

const handle = globalThis.__shadowAuthTestHandle;
assert.ok(handle, "expected test handle to be installed");
const {
  shadowDashboardTarget,
  validateLeaderSession,
  validateLeaderSessionShadow,
  shadowAuthReadout,
  _present,
} = handle;

// ---------------------------------------------------------------------
// Mock helpers
// ---------------------------------------------------------------------

function makeRequest({ pathname = "/api/admin/clients", headers = {}, method = "GET" } = {}) {
  const url = `https://portal.purebrain.ai${pathname}`;
  return new Request(url, { method, headers });
}

function makeServiceBinding(name, handler) {
  // Service Binding shape: a `fetch` method that the worker calls.
  const calls = [];
  return {
    name,
    calls,
    fetch: async (req) => {
      const body = await req.text().catch(() => "");
      let parsed = null;
      try { parsed = JSON.parse(body); } catch { /* leave null */ }
      calls.push({ url: req.url, method: req.method, body: parsed, headers: Object.fromEntries(req.headers) });
      const out = await handler(req, parsed);
      if (out instanceof Response) return out;
      return new Response(JSON.stringify(out.body ?? {}), {
        status: out.status ?? 200,
        headers: { "content-type": "application/json" },
      });
    },
  };
}

function captureConsoleLog() {
  const original = console.log;
  const lines = [];
  console.log = (...args) => { lines.push(args.join(" ")); };
  return {
    lines,
    restore() { console.log = original; },
  };
}

// ---------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------

let passed = 0;
let failed = 0;
async function t(name, fn) {
  try {
    await fn();
    console.log(`PASS ${name}`);
    passed++;
  } catch (e) {
    console.log(`FAIL ${name}: ${e && e.message}`);
    if (e && e.stack) console.log(e.stack);
    failed++;
  }
}

await t("T1: shadowDashboardTarget routes paths correctly", async () => {
  assert.equal(shadowDashboardTarget("/api/admin/clients"), "clients");
  assert.equal(shadowDashboardTarget("/api/admin/clients/42"), "clients");
  assert.equal(shadowDashboardTarget("/api/admin/invites"), "clients");
  assert.equal(shadowDashboardTarget("/api/admin/invite/xyz"), "clients");

  assert.equal(shadowDashboardTarget("/api/admin/affiliates"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/payouts/x"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/referral/list"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/stats"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/partners"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/partners/42"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/commission-report"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/payments/manual"), "referrals");
  assert.equal(shadowDashboardTarget("/api/admin/applications/12"), "referrals");

  assert.equal(shadowDashboardTarget("/api/admin/validate-token"), "unknown");
  assert.equal(shadowDashboardTarget("/admin/shadow-auth-readout"), "unknown");
  assert.equal(shadowDashboardTarget("/"), "unknown");
});

await t("T2: legacy result is returned verbatim — shadow never wins", async () => {
  let legacyCalls = 0;
  let shadowCalls = 0;
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => {
      legacyCalls++;
      return { status: 200, body: { valid: true, role: "leader", user_id: 42, email: "leader@example.com" } };
    }),
    CLIENTS_API: makeServiceBinding("clients-api", () => {
      shadowCalls++;
      // shadow legitimately differs in shape — use session envelope
      return { status: 200, body: { ok: true, session: { user_id: 999, email: "different@example.com" } } };
    }),
  };
  const req = makeRequest({ headers: { authorization: "Bearer tok-aaaa" } });

  const cap = captureConsoleLog();
  let result;
  try {
    result = await validateLeaderSessionShadow(req, env);
  } finally { cap.restore(); }

  assert.equal(result.ok, true, "legacy ok=true wins");
  assert.deepEqual(result.session, { valid: true, role: "leader", user_id: 42, email: "leader@example.com" });
  assert.equal(legacyCalls, 1, "legacy called exactly once");
  assert.equal(shadowCalls, 1, "shadow called exactly once");

  const logLine = cap.lines.find((l) => l.includes("shadow_auth"));
  assert.ok(logLine, "expected a shadow_auth log line");
  const log = JSON.parse(logLine);
  assert.equal(log.evt, "shadow_auth");
  assert.equal(log.legacy_ok, true);
  assert.equal(log.shadow_ok, true);
  assert.equal(log.user_id_match, false, "user_id mismatch detected");
  assert.equal(log.email_match, false, "email mismatch detected");
  assert.equal(log.divergent, true, "divergence flagged when both ok but user_ids differ");
  // PII safety: presence flags only
  assert.equal(typeof log.field_present.legacy_user_id, "boolean");
  assert.equal(typeof log.field_present.shadow_email, "boolean");
});

await t("T3: shadow exception NEVER propagates — legacy still returned", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "owner", user_id: 1, email: "a@x" },
    })),
    CLIENTS_API: {
      name: "clients-api",
      fetch: async () => { throw new Error("boom"); },
    },
  };
  const req = makeRequest({ headers: { authorization: "Bearer tok-bbbb" } });

  const cap = captureConsoleLog();
  let result;
  try {
    result = await validateLeaderSessionShadow(req, env);
  } finally { cap.restore(); }

  assert.equal(result.ok, true, "legacy still wins when shadow throws");
  const log = JSON.parse(cap.lines.find((l) => l.includes("shadow_auth")));
  assert.equal(log.shadow_ok, false);
  assert.equal(log.shadow_error, "fetch_failed");
});

await t("T4: both sides agree (clean match) — no divergence", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 7, email: "ok@x" },
    })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({
      status: 200, body: { ok: true, session: { user_id: 7, email: "ok@x" } },
    })),
  };
  const req = makeRequest({ headers: { cookie: "social_session=tok-cccc" } });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  const log = JSON.parse(cap.lines.find((l) => l.includes("shadow_auth")));
  assert.equal(log.user_id_match, true);
  assert.equal(log.email_match, true);
  assert.equal(log.divergent, false);
  assert.equal(result.ok, true);
});

await t("T5: missing token — both fail, neither_ok branch, NO divergence", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({ status: 200, body: { valid: true } })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({ status: 200, body: { ok: true } })),
  };
  const req = makeRequest(); // no auth headers
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, false);
  assert.equal(result.status, 401);
  const log = JSON.parse(cap.lines.find((l) => l.includes("shadow_auth")));
  assert.equal(log.legacy_ok, false);
  assert.equal(log.shadow_ok, false);
  assert.equal(log.divergent, false, "neither_ok is NOT a divergence");
  assert.equal(log.have_token, false);
});

await t("T6: missing REFERRALS_API binding — shadow leg logs binding_missing, legacy still wins", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "owner", user_id: 5, email: "z@x" },
    })),
    // REFERRALS_API not bound at all (Day 2 mid-state)
  };
  const req = makeRequest({
    pathname: "/api/admin/referral/list",
    headers: { authorization: "Bearer tok-dddd" },
  });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, true);
  const log = JSON.parse(cap.lines.find((l) => l.includes("shadow_auth")));
  assert.equal(log.target, "referrals");
  assert.equal(log.shadow_ok, false);
  assert.equal(log.shadow_error, "binding_missing");
});

await t("T7: PII discipline — log has NO raw email/token/hash values", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 99, email: "sensitive@example.com" },
    })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({
      status: 200, body: { ok: true, session: { user_id: 99, email: "sensitive@example.com", password_hash: "should-never-appear" } },
    })),
  };
  const req = makeRequest({
    headers: { authorization: "Bearer SENSITIVE-TOKEN-9999" },
  });
  const cap = captureConsoleLog();
  await validateLeaderSessionShadow(req, env);
  cap.restore();
  const logLine = cap.lines.find((l) => l.includes("shadow_auth"));
  assert.ok(logLine, "shadow_auth log exists");
  // Hard PII assertions: no raw email, no token, no hash
  assert.ok(!logLine.includes("sensitive@example.com"), "no raw email in log");
  assert.ok(!logLine.includes("SENSITIVE-TOKEN-9999"), "no raw token in log");
  assert.ok(!logLine.includes("password_hash"), "no password_hash key in log");
  assert.ok(!logLine.includes("should-never-appear"), "no hash value in log");
});

await t("T8: readout endpoint produces verdict + PII-safe sample", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 11, email: "rdo@x" },
    })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({
      status: 200, body: { ok: true, session: { user_id: 11, email: "rdo@x" } },
    })),
  };

  // Seed the ring buffer with 3 samples
  const cap = captureConsoleLog();
  for (let i = 0; i < 3; i++) {
    const r = makeRequest({ headers: { authorization: `Bearer tok-${i}` } });
    await validateLeaderSessionShadow(r, env);
  }
  cap.restore();

  // Now call the readout (which requires its own auth gate)
  const readoutReq = makeRequest({
    pathname: "/admin/shadow-auth-readout",
    headers: { authorization: "Bearer tok-readout" },
  });
  const resp = await shadowAuthReadout(readoutReq, env);
  assert.equal(resp.status, 200);
  const body = await resp.json();
  assert.equal(body.ok, true);
  assert.ok(body.total >= 3, `expected >=3 samples in ring, got ${body.total}`);
  // <100 samples → BLOCK verdict
  assert.equal(body.verdict, "BLOCK");
  assert.ok(body.verdict || body.verdict === null);
  // Sample is PII-safe
  for (const s of body.sample) {
    assert.equal(typeof s.legacy_ok, "boolean");
    assert.equal(typeof s.user_id_match, "boolean");
    assert.ok(!("email" in s), "sample must not contain email");
    assert.ok(!("token" in s), "sample must not contain token");
  }
});

await t("T9: readout endpoint rejects unauth requests with 401", async () => {
  const env = {
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({ status: 200, body: { valid: false } })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({ status: 200, body: { ok: false } })),
  };
  // No auth headers
  const req = makeRequest({ pathname: "/admin/shadow-auth-readout" });
  const resp = await shadowAuthReadout(req, env);
  assert.equal(resp.status, 401, "no token → 401");
});

await t("T10: _present is the only redaction primitive used in logs", async () => {
  assert.equal(_present(null), false);
  assert.equal(_present(undefined), false);
  assert.equal(_present(""), false);
  assert.equal(_present(false), false);
  assert.equal(_present(0), true); // 0 is a legitimate user_id... wait no, _present treats 0 as truthy because v !== "" + v !== false + v !== undefined + v !== null
  // Actually _present returns true for 0; user_ids are positive so this is fine.
  // The behavior we care about is: NEVER expose the raw value.
  assert.equal(_present("foo"), true);
  assert.equal(_present(42), true);
});

// =====================================================================
// Day 3 cutover gate — SHADOW_AUTH_ENABLED env flag
// =====================================================================

await t("T11: SHADOW_AUTH_ENABLED=true + clients target + shadow ok → shadow wins", async () => {
  const env = {
    SHADOW_AUTH_ENABLED: "true",
    INTERNAL_BINDING_SECRET: "test-secret",
    // Legacy returns a DIFFERENT user — proves shadow result is authoritative
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 1, email: "legacy@x" },
    })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({
      status: 200, body: { ok: true, session: { user_id: 99, email: "shadow@x", role: "leader" } },
    })),
  };
  const req = makeRequest({
    pathname: "/api/admin/clients/42",
    headers: { authorization: "Bearer tok-d3-1" },
  });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, true, "shadow ok bubbles up");
  assert.equal(result.session.user_id, 99, "user_id from SHADOW not legacy");
  assert.equal(result.session.email, "shadow@x", "email from SHADOW not legacy");
  assert.equal(result.source, "shadow", "tagged source=shadow");
  assert.equal(result.target, "clients", "tagged target=clients");
});

await t("T12: SHADOW_AUTH_ENABLED=true + shadow role NOT in leader-set → 403 from shadow", async () => {
  const env = {
    SHADOW_AUTH_ENABLED: "true",
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 1, email: "legacy@x" },
    })),
    REFERRALS_API: makeServiceBinding("referrals-api", () => ({
      status: 200, body: { ok: true, session: { user_id: 7, email: "x@y", referrals_role: "viewer" } },
    })),
  };
  const req = makeRequest({
    pathname: "/api/admin/referral/list",
    headers: { authorization: "Bearer tok-d3-2" },
  });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, false, "viewer role rejected even when shadow ok");
  assert.equal(result.status, 403);
  assert.equal(result.source, "shadow");
});

await t("T13: SHADOW_AUTH_ENABLED unset (default) → legacy wins (Day 2 behavior preserved)", async () => {
  const env = {
    // SHADOW_AUTH_ENABLED intentionally absent
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 1, email: "legacy@x" },
    })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({
      status: 200, body: { ok: true, session: { user_id: 99, email: "shadow@x", role: "leader" } },
    })),
  };
  const req = makeRequest({
    pathname: "/api/admin/clients",
    headers: { authorization: "Bearer tok-d3-3" },
  });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, true);
  assert.equal(result.session.user_id, 1, "user_id from LEGACY (flag off)");
  assert.equal(result.source, undefined, "no source tag when legacy wins");
});

await t("T14: SHADOW_AUTH_ENABLED=true + unknown target → legacy still wins (gate is scoped)", async () => {
  const env = {
    SHADOW_AUTH_ENABLED: "true",
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 1, email: "legacy@x" },
    })),
  };
  const req = makeRequest({
    pathname: "/api/admin/validate-token", // explicitly "unknown" target
    headers: { authorization: "Bearer tok-d3-4" },
  });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, true);
  assert.equal(result.session.user_id, 1, "legacy wins for unknown targets");
});

await t("T15: SHADOW_AUTH_ENABLED=true + shadow FAILS → legacy wins (kill-switch safe)", async () => {
  const env = {
    SHADOW_AUTH_ENABLED: "true",
    INTERNAL_BINDING_SECRET: "test-secret",
    SOCIAL_API: makeServiceBinding("social-api", () => ({
      status: 200, body: { valid: true, role: "leader", user_id: 1, email: "legacy@x" },
    })),
    CLIENTS_API: makeServiceBinding("clients-api", () => ({
      status: 401, body: { ok: false, error: "expired" },
    })),
  };
  const req = makeRequest({
    pathname: "/api/admin/clients",
    headers: { authorization: "Bearer tok-d3-5" },
  });
  const cap = captureConsoleLog();
  const result = await validateLeaderSessionShadow(req, env);
  cap.restore();
  assert.equal(result.ok, true, "legacy still wins when shadow fails");
  assert.equal(result.session.user_id, 1);
});

console.log(`\n=== ${passed} passed, ${failed} failed ===`);
process.exit(failed === 0 ? 0 : 1);
