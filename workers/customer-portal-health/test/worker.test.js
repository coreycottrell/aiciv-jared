/**
 * Tests for customer-portal-health Worker.
 *
 * Pure node:test — no wrangler/miniflare needed. We import the worker
 * module and call its fetch()/scheduled() with mocked env (D1 + fetch).
 *
 * Coverage:
 *   - admin auth gates /admin/restart and /admin/recovery-log
 *   - cron writes one D1 row per configured customer
 *   - admin/restart signs HMAC with nonce+ts and writes audit row
 *   - admin/recovery-log returns rows from D1
 */

import { describe, it, beforeEach } from "node:test";
import { strict as assert } from "node:assert";
import workerMod from "../src/worker.js";

/* ----------------------------- mocks ----------------------------------- */

function makeD1() {
  const calls = [];
  const rows = [];
  const prepare = (sql) => {
    return {
      sql,
      _bound: null,
      bind(...args) {
        this._bound = args;
        return this;
      },
      async run() {
        calls.push({ sql, args: this._bound });
        if (sql.trim().toUpperCase().startsWith("INSERT")) {
          // Mimic D1 row insert.
          rows.push({ sql, args: this._bound });
        }
        return { success: true, meta: { last_row_id: rows.length } };
      },
      async all() {
        calls.push({ sql, args: this._bound });
        return { results: rows.map((r, i) => ({ id: i + 1, sql: r.sql })) };
      },
    };
  };
  return { prepare, _calls: calls, _rows: rows };
}

function makeEnv({ tunnelMap = { whitehurst: "https://recovery-pb3.example/" },
                   adminToken = "test-admin",
                   hmacKey = "test-hmac" } = {}) {
  return {
    DB: makeD1(),
    ADMIN_TOKEN: adminToken,
    RECOVERY_AGENT_HMAC_KEY: hmacKey,
    RECOVERY_AGENT_TUNNEL_URL: JSON.stringify(tunnelMap),
  };
}

/**
 * Patch global fetch with a programmable mock.
 * Returns { restore, calls }.
 */
function mockFetch(handler) {
  const orig = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init });
    return handler(String(url), init);
  };
  return {
    restore() { globalThis.fetch = orig; },
    calls,
  };
}

/* ------------------------------ tests ---------------------------------- */

describe("customer-portal-health worker", () => {
  let env;
  beforeEach(() => { env = makeEnv(); });

  it("GET /health returns 200", async () => {
    const resp = await workerMod.fetch(new Request("https://w/health"), env);
    assert.equal(resp.status, 200);
    const body = await resp.json();
    assert.equal(body.ok, true);
    assert.equal(body.worker, "customer-portal-health");
  });

  it("POST /admin/restart without auth -> 401", async () => {
    const req = new Request("https://w/admin/restart", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ customer_slug: "whitehurst" }),
    });
    const resp = await workerMod.fetch(req, env);
    assert.equal(resp.status, 401);
  });

  it("POST /admin/restart with bad customer_slug -> 400", async () => {
    const req = new Request("https://w/admin/restart", {
      method: "POST",
      headers: { "content-type": "application/json", authorization: "Bearer test-admin" },
      body: JSON.stringify({ customer_slug: "WHITEHURST/../etc/passwd" }),
    });
    const resp = await workerMod.fetch(req, env);
    assert.equal(resp.status, 400);
  });

  it("POST /admin/restart unknown customer -> 400", async () => {
    const req = new Request("https://w/admin/restart", {
      method: "POST",
      headers: { "content-type": "application/json", authorization: "Bearer test-admin" },
      body: JSON.stringify({ customer_slug: "gary" }),
    });
    const resp = await workerMod.fetch(req, env);
    assert.equal(resp.status, 400);
    const body = await resp.json();
    assert.match(body.error, /no tunnel URL/);
  });

  it("POST /admin/restart calls recovery-agent with HMAC headers and writes audit row", async () => {
    const fetchMock = mockFetch(async (url, init) => {
      assert.match(url, /\/restart$/);
      const h = new Headers(init.headers);
      assert.ok(h.get("x-nonce"), "nonce header present");
      assert.ok(h.get("x-timestamp"), "timestamp header present");
      assert.ok(h.get("x-signature"), "signature header present");
      const body = JSON.parse(init.body);
      assert.equal(body.container_name, "whitehurst");
      assert.ok(body.request_id);
      return new Response(JSON.stringify({
        ok: true,
        restart_id: body.request_id,
        duration_ms: 1234,
        pid_count_before: 5,
        pid_count_after: 6,
        thread_count_before: 40,
        thread_count_after: 42,
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    try {
      const req = new Request("https://w/admin/restart", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: "Bearer test-admin" },
        body: JSON.stringify({ customer_slug: "whitehurst", reason: "test" }),
      });
      const resp = await workerMod.fetch(req, env);
      assert.equal(resp.status, 200);
      const body = await resp.json();
      assert.equal(body.ok, true);
      assert.equal(body.outcome, "success");
      // Exactly one INSERT into customer_portal_recovery_log.
      const inserts = env.DB._calls.filter((c) => c.sql.trim().toUpperCase().startsWith("INSERT"));
      assert.equal(inserts.length, 1);
      // action column = 'restart'
      const args = inserts[0].args;
      // args order from worker.js: ts, customer_slug, hetzner_host, action, ai_before, ai_after, thr_b, thr_a, pid_b, pid_a, dur, outcome, err, triggered, req_id
      assert.equal(args[1], "whitehurst");
      assert.equal(args[3], "restart");
      assert.equal(args[11], "success");
      assert.equal(args[13], "admin_button");
    } finally {
      fetchMock.restore();
    }
  });

  it("POST /admin/restart with loop_detected response writes 'failed' outcome", async () => {
    const fetchMock = mockFetch(async () => new Response(JSON.stringify({
      ok: false, loop_detected: true, error: "loop_detected",
    }), { status: 429 }));
    try {
      const req = new Request("https://w/admin/restart", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: "Bearer test-admin" },
        body: JSON.stringify({ customer_slug: "whitehurst" }),
      });
      const resp = await workerMod.fetch(req, env);
      assert.equal(resp.status, 429);
      const body = await resp.json();
      assert.equal(body.outcome, "failed");
      assert.equal(body.error, "loop_detected");
      const inserts = env.DB._calls.filter((c) => c.sql.trim().toUpperCase().startsWith("INSERT"));
      assert.equal(inserts.length, 1);
      assert.equal(inserts[0].args[11], "failed");
      assert.equal(inserts[0].args[12], "loop_detected");
    } finally {
      fetchMock.restore();
    }
  });

  it("GET /admin/recovery-log requires auth and validates customer", async () => {
    const r1 = await workerMod.fetch(new Request("https://w/admin/recovery-log?customer=whitehurst"), env);
    assert.equal(r1.status, 401);

    const r2 = await workerMod.fetch(new Request("https://w/admin/recovery-log?customer=bad..slug", {
      headers: { authorization: "Bearer test-admin" },
    }), env);
    assert.equal(r2.status, 400);

    const r3 = await workerMod.fetch(new Request("https://w/admin/recovery-log?customer=whitehurst", {
      headers: { authorization: "Bearer test-admin" },
    }), env);
    assert.equal(r3.status, 200);
    const body = await r3.json();
    assert.equal(body.customer_slug, "whitehurst");
    assert.ok(Array.isArray(body.rows));
  });

  it("scheduled() writes one health_check row per configured customer", async () => {
    const fetchMock = mockFetch(async () => new Response(JSON.stringify({
      ok: true, daemon: "recovery-agent", ts: 1,
    }), { status: 200 }));
    try {
      const ctx = { waitUntil: (p) => p };
      // Two customers configured.
      env = makeEnv({ tunnelMap: {
        whitehurst: "https://recovery-pb3.example",
        canary2: "https://recovery-pb4.example",
      } });
      await workerMod.scheduled({ scheduledTime: Date.now() }, env, ctx);
      // Allow Promise.allSettled to resolve.
      await new Promise((r) => setTimeout(r, 10));
      const inserts = env.DB._calls.filter((c) => c.sql.trim().toUpperCase().startsWith("INSERT"));
      assert.equal(inserts.length, 2);
      for (const ins of inserts) {
        assert.equal(ins.args[3], "health_check");
        assert.equal(ins.args[11], "success");
        assert.equal(ins.args[13], "cron");
      }
    } finally {
      fetchMock.restore();
    }
  });

  it("scheduled() with no tunnel map is a no-op (no D1 writes)", async () => {
    env = makeEnv({ tunnelMap: {} });
    const ctx = { waitUntil: (p) => p };
    await workerMod.scheduled({ scheduledTime: Date.now() }, env, ctx);
    const inserts = env.DB._calls.filter((c) => c.sql.trim().toUpperCase().startsWith("INSERT"));
    assert.equal(inserts.length, 0);
  });
});
