/**
 * 777 Command Center — Bidirectional Edit API
 * Vercel Serverless Function
 *
 * Accepts a UI edit, validates it, and queues it in pending-edits.json
 * for the next 60-second cron sync back to Google Sheets.
 *
 * Security:
 *  - POST only
 *  - Password gate matches dashboard ("777grind")
 *  - Per-IP rate limiting: 10 edits / minute (in-memory, resets on cold start)
 *  - All required fields validated before write
 *  - No file traversal — writes to a fixed path only
 *
 * Request body (JSON):
 *  { password, table, key, field, value }
 *
 * Response (200 OK):
 *  { ok: true, queued: true, edit_id: <number> }
 *
 * Error responses:
 *  { ok: false, error: "..." }  with appropriate HTTP status
 *
 * NOTE: pending-edits.json is file-based for now. D1 migration path:
 *  Replace readEdits/writeEdits with D1 INSERT INTO pending_edits.
 *
 * Author: PTT full-stack-developer
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve } from 'path';

// ---------------------------------------------------------------------------
// CONFIG
// ---------------------------------------------------------------------------
const DASHBOARD_PASSWORD = '777grind';

const RATE_LIMIT_WINDOW_MS = 60 * 1000;  // 1 minute
const RATE_LIMIT_MAX = 10;               // edits per minute per IP

// Allowed table names (whitelist — prevents injection of arbitrary table names)
const ALLOWED_TABLES = new Set([
  'daily_scores',
  'seven_fs',
  'goals',
  'proof_wall',
]);

// Allowed fields per table (prevents writing to unexpected columns)
const ALLOWED_FIELDS = {
  daily_scores: new Set(['score', ...Array.from({length: 20}, (_, i) => String(i))]),
  seven_fs:     new Set(['family', 'career', 'fitness', 'faith', 'finance', 'fellowship', 'fun']),
  goals:        new Set(['text', 'progress']),
  proof_wall:   new Set(['task']),
};

// In-memory rate limit store (resets on cold start — acceptable for serverless)
const rateLimitStore = new Map();

// ---------------------------------------------------------------------------
// PENDING EDITS FILE PATH
// The file lives at the root of the 777 deployment.
// In Vercel, /var/task is the function root — resolve relative to __dirname.
// ---------------------------------------------------------------------------
function getPendingEditsPath() {
  // Resolve path relative to this file: ../pending-edits.json
  return resolve(__dirname, '..', 'pending-edits.json');
}

// ---------------------------------------------------------------------------
// PENDING EDITS IO
// ---------------------------------------------------------------------------
function readEdits() {
  const path = getPendingEditsPath();
  if (!existsSync(path)) {
    return { edits: [] };
  }
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return { edits: [] };
  }
}

function writeEdits(data) {
  const path = getPendingEditsPath();
  writeFileSync(path, JSON.stringify(data, null, 2), 'utf8');
}

// ---------------------------------------------------------------------------
// RATE LIMIT
// ---------------------------------------------------------------------------
function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimitStore.get(ip);

  if (!entry || now - entry.windowStart > RATE_LIMIT_WINDOW_MS) {
    rateLimitStore.set(ip, { windowStart: now, count: 1 });
    return true;
  }

  entry.count++;
  return entry.count <= RATE_LIMIT_MAX;
}

// ---------------------------------------------------------------------------
// VALIDATION
// ---------------------------------------------------------------------------
function validateBody(body) {
  if (!body || typeof body !== 'object') {
    return 'Request body must be a JSON object.';
  }

  const { password, table, key, field, value } = body;

  if (!password || typeof password !== 'string') {
    return 'password is required.';
  }
  if (password !== DASHBOARD_PASSWORD) {
    return 'Invalid password.';
  }
  if (!table || typeof table !== 'string') {
    return 'table is required.';
  }
  if (!ALLOWED_TABLES.has(table)) {
    return `Invalid table. Allowed: ${[...ALLOWED_TABLES].join(', ')}`;
  }
  if (!key || typeof key !== 'string' || key.length > 100) {
    return 'key is required (max 100 chars).';
  }
  if (!field || typeof field !== 'string') {
    return 'field is required.';
  }
  if (!ALLOWED_FIELDS[table]?.has(field)) {
    return `Invalid field "${field}" for table "${table}". Allowed: ${[...ALLOWED_FIELDS[table] || []].join(', ')}`;
  }
  if (value === undefined || value === null) {
    return 'value is required.';
  }
  // Coerce to string for storage, limit length
  const valueStr = String(value);
  if (valueStr.length > 2000) {
    return 'value too long (max 2000 chars).';
  }

  return null; // no error
}

// ---------------------------------------------------------------------------
// CORS — match chat.js for consistency
// ---------------------------------------------------------------------------
const ALLOWED_ORIGINS = [
  'https://777-command-center.vercel.app',
  'https://777.purebrain.ai',
];

function isAllowedOrigin(origin) {
  if (!origin) return false;
  return ALLOWED_ORIGINS.includes(origin);
}

function corsHeaders(origin) {
  const allowed = isAllowedOrigin(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

// ---------------------------------------------------------------------------
// MAIN HANDLER
// ---------------------------------------------------------------------------
export default async function handler(req, res) {
  const origin = req.headers['origin'] || '';
  const cors = corsHeaders(origin);

  // Preflight
  if (req.method === 'OPTIONS') {
    return res.status(204).set(cors).end();
  }

  // POST only
  if (req.method !== 'POST') {
    return res.status(405).set(cors).json({ ok: false, error: 'Method not allowed. POST only.' });
  }

  // Origin check — reject cross-origin requests from unknown origins
  if (origin && !isAllowedOrigin(origin)) {
    return res.status(403).set(cors).json({ ok: false, error: 'Forbidden origin.' });
  }

  // Rate limit
  const ip =
    req.headers['x-real-ip'] ||
    req.headers['x-forwarded-for']?.split(',')[0]?.trim() ||
    req.socket?.remoteAddress ||
    'unknown';

  if (!checkRateLimit(ip)) {
    return res.status(429).set(cors).json({
      ok: false,
      error: 'Rate limit exceeded: max 10 edits per minute.',
    });
  }

  // Parse body
  let body;
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
  } catch {
    return res.status(400).set(cors).json({ ok: false, error: 'Invalid JSON body.' });
  }

  // Validate
  const validationError = validateBody(body);
  if (validationError) {
    // Return 401 for auth failure, 400 for all other validation errors
    const status = validationError === 'Invalid password.' ? 401 : 400;
    return res.status(status).set(cors).json({ ok: false, error: validationError });
  }

  const { table, key, field, value } = body;
  const valueStr = String(value);

  // Read current edits
  let store;
  try {
    store = readEdits();
  } catch (err) {
    console.error('[edit.js] readEdits error:', err);
    return res.status(500).set(cors).json({ ok: false, error: 'Could not read pending edits file.' });
  }

  // Build new edit record
  const newId = (store.edits.length > 0
    ? Math.max(...store.edits.map(e => e.id || 0)) + 1
    : 1);

  const editRecord = {
    id:         newId,
    table_name: table,
    record_key: key,
    field:      field,
    new_value:  valueStr,
    created_at: new Date().toISOString(),
    synced_at:  null,
  };

  store.edits.push(editRecord);

  // Write back
  try {
    writeEdits(store);
  } catch (err) {
    console.error('[edit.js] writeEdits error:', err);
    return res.status(500).set(cors).json({ ok: false, error: 'Could not write pending edits file.' });
  }

  console.log(`[edit.js] Edit queued: id=${newId} table=${table} key=${key} field=${field}`);

  return res.status(200).set(cors).json({
    ok:      true,
    queued:  true,
    edit_id: newId,
  });
}
