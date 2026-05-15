/**
 * Shape tests for disk-telemetry-ingest Worker.
 *
 * These tests construct fetch requests and invoke the worker's default export.
 * Run:
 *   node tests/test_disk_telemetry_ingest_worker.js
 *
 * They use a mock D1 binding (prepare/bind/run/all) to verify the worker logic
 * without touching real Cloudflare infrastructure.
 */

const path = require('path');

// Polyfill crypto.subtle for older Node? Node 18+ has it native.
// We import the worker as a module via dynamic import.

async function loadWorker() {
  const workerPath = path.join(
    __dirname,
    '..',
    'workers',
    'disk-telemetry-ingest',
    'src',
    'worker.js',
  );
  return (await import(workerPath)).default;
}

function makeMockDB(rowsToReturn = []) {
  const calls = { prepares: [], runs: 0, alls: 0, lastBind: null };
  const stmt = {
    bind(...args) {
      calls.lastBind = args;
      return this;
    },
    async run() {
      calls.runs++;
      return { meta: { last_row_id: 42 } };
    },
    async all() {
      calls.alls++;
      return { results: rowsToReturn };
    },
  };
  return {
    prepare(sql) {
      calls.prepares.push(sql);
      return stmt;
    },
    _calls: calls,
  };
}

async function hmacHex(key, message) {
  const enc = new TextEncoder();
  const k = await crypto.subtle.importKey(
    'raw',
    enc.encode(key),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', k, enc.encode(message));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function signedRequest(url, body, token, opts = {}) {
  const ts = opts.ts ?? Math.floor(Date.now() / 1000);
  const nonce = opts.nonce ?? `nonce-${Math.random().toString(36).slice(2)}`;
  const rawBody = JSON.stringify(body);
  const sig = await hmacHex(token, `${rawBody}|${nonce}|${ts}`);
  return new Request(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-nonce': nonce,
      'x-timestamp': String(ts),
      'x-signature': opts.sig ?? sig,
      ...(opts.extraHeaders || {}),
    },
    body: rawBody,
  });
}

const tests = [];
function test(name, fn) {
  tests.push({ name, fn });
}

test('health endpoint returns 200', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB() };
  const resp = await worker.fetch(new Request('https://x/health'), env);
  assertEq(resp.status, 200);
  const body = await resp.json();
  assertEq(body.ok, true);
});

test('ingest rejects missing auth headers', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB(), INGEST_TOKEN: 'tok' };
  const req = new Request('https://x/ingest', {
    method: 'POST',
    body: '{}',
    headers: { 'content-type': 'application/json' },
  });
  const resp = await worker.fetch(req, env);
  assertEq(resp.status, 401);
});

test('ingest rejects old timestamp', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB(), INGEST_TOKEN: 'tok' };
  const req = await signedRequest('https://x/ingest', { civ_name: 'a' }, 'tok', {
    ts: Math.floor(Date.now() / 1000) - 120,
  });
  const resp = await worker.fetch(req, env);
  assertEq(resp.status, 401);
});

test('ingest rejects bad signature', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB(), INGEST_TOKEN: 'tok' };
  const req = await signedRequest('https://x/ingest', { civ_name: 'a' }, 'tok', {
    sig: 'deadbeef',
  });
  const resp = await worker.fetch(req, env);
  assertEq(resp.status, 401);
});

test('ingest rejects replayed nonce', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB(), INGEST_TOKEN: 'tok' };
  const body = {
    civ_name: 'aether',
    hostname: 'host1',
    disk_root_used_pct: 50,
    disk_root_free_mb: 1024,
    tmp_size_mb: 100,
    tmp_large_files_count: 0,
  };
  const req1 = await signedRequest('https://x/ingest', body, 'tok', { nonce: 'fixed-nonce-1' });
  const resp1 = await worker.fetch(req1, env);
  assertEq(resp1.status, 200);

  const req2 = await signedRequest('https://x/ingest', body, 'tok', { nonce: 'fixed-nonce-1' });
  const resp2 = await worker.fetch(req2, env);
  assertEq(resp2.status, 401);
});

test('ingest accepts valid signed request and writes row', async () => {
  const worker = await loadWorker();
  const db = makeMockDB();
  const env = { DB: db, INGEST_TOKEN: 'tok' };
  const body = {
    civ_name: 'aether',
    hostname: 'purebrain-3',
    disk_root_used_pct: 42,
    disk_root_free_mb: 2048,
    tmp_size_mb: 150,
    tmp_large_files_count: 1,
    working_tree_large_files_count: 0,
    alert_tier: 'info',
    daemon_version: '1.0.0',
  };
  const req = await signedRequest('https://x/ingest', body, 'tok', { nonce: 'nA' });
  const resp = await worker.fetch(req, env);
  assertEq(resp.status, 200);
  const json = await resp.json();
  assertEq(json.ok, true);
  assertEq(json.id, 42);
  assertEq(db._calls.runs, 1);
  assertEq(db._calls.lastBind[1], 'aether'); // civ_name positional
});

test('ingest rejects bad pct (>100)', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB(), INGEST_TOKEN: 'tok' };
  const body = {
    civ_name: 'a', hostname: 'h',
    disk_root_used_pct: 250, disk_root_free_mb: 1, tmp_size_mb: 1, tmp_large_files_count: 0,
  };
  const req = await signedRequest('https://x/ingest', body, 'tok', { nonce: 'badpct' });
  const resp = await worker.fetch(req, env);
  assertEq(resp.status, 400);
});

test('ingest accepts previous token during rotation', async () => {
  const worker = await loadWorker();
  const env = {
    DB: makeMockDB(),
    INGEST_TOKEN: 'new-token',
    INGEST_TOKEN_PREVIOUS: 'old-token',
  };
  const body = {
    civ_name: 'a', hostname: 'h',
    disk_root_used_pct: 10, disk_root_free_mb: 1, tmp_size_mb: 1, tmp_large_files_count: 0,
  };
  // Daemon still using OLD token during rolling rotation
  const req = await signedRequest('https://x/ingest', body, 'old-token', { nonce: 'rot1' });
  const resp = await worker.fetch(req, env);
  assertEq(resp.status, 200);
});

test('/civs/<name>/recent requires admin bearer', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB([]), ADMIN_TOKEN: 'admin-secret' };
  const r1 = await worker.fetch(new Request('https://x/civs/aether/recent?hours=1'), env);
  assertEq(r1.status, 401);
  const r2 = await worker.fetch(
    new Request('https://x/civs/aether/recent?hours=1', {
      headers: { authorization: 'Bearer admin-secret' },
    }),
    env,
  );
  assertEq(r2.status, 200);
});

test('unknown path returns 404', async () => {
  const worker = await loadWorker();
  const env = { DB: makeMockDB() };
  const resp = await worker.fetch(new Request('https://x/unknown'), env);
  assertEq(resp.status, 404);
});

// ----------------------------- runner ----------------------------------------

function assertEq(actual, expected) {
  if (actual !== expected) {
    throw new Error(`expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

(async function main() {
  let passed = 0;
  let failed = 0;
  for (const { name, fn } of tests) {
    try {
      await fn();
      console.log(`  PASS  ${name}`);
      passed++;
    } catch (e) {
      console.error(`  FAIL  ${name}: ${e.message}`);
      failed++;
    }
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed === 0 ? 0 : 1);
})();
