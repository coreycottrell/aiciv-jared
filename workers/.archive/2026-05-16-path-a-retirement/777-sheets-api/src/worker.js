/**
 * 777 Sheets API Worker
 * Cloudflare Worker that proxies Google Sheets API requests
 * using service account authentication (JWT/OAuth2).
 *
 * Endpoints:
 *   GET  /api/sheets/read?range=...         — Read a range
 *   POST /api/sheets/update  {range, values} — Update specific cells
 *   POST /api/sheets/append  {range, values} — Append rows
 *   GET  /api/sheets/meta                    — Spreadsheet metadata (sheet names)
 *   GET  /health                             — Health check
 */

// ---------- crypto helpers (Web Crypto API) ----------

function arrayBufToBase64Url(buf) {
  const bytes = new Uint8Array(buf);
  let binary = '';
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function strToBase64Url(str) {
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function pemToArrayBuffer(pem) {
  const b64 = pem
    .replace(/-----BEGIN [A-Z ]+-----/, '')
    .replace(/-----END [A-Z ]+-----/, '')
    .replace(/\s/g, '');
  const binary = atob(b64);
  const buf = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) buf[i] = binary.charCodeAt(i);
  return buf.buffer;
}

async function importPrivateKey(pem) {
  const keyData = pemToArrayBuffer(pem);
  return crypto.subtle.importKey(
    'pkcs8',
    keyData,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['sign']
  );
}

// ---------- Google OAuth2 via service account JWT ----------

let cachedToken = null;
let tokenExpiry = 0;

async function getAccessToken(env) {
  const now = Math.floor(Date.now() / 1000);
  if (cachedToken && now < tokenExpiry - 60) return cachedToken;

  const header = strToBase64Url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const claims = {
    iss: env.SERVICE_ACCOUNT_EMAIL,
    scope: 'https://www.googleapis.com/auth/spreadsheets',
    aud: 'https://oauth2.googleapis.com/token',
    iat: now,
    exp: now + 3600,
  };
  const payload = strToBase64Url(JSON.stringify(claims));

  const signingInput = new TextEncoder().encode(`${header}.${payload}`);
  const key = await importPrivateKey(env.SERVICE_ACCOUNT_PRIVATE_KEY);
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, signingInput);
  const signature = arrayBufToBase64Url(sig);

  const jwt = `${header}.${payload}.${signature}`;

  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + jwt,
  });

  if (!tokenRes.ok) {
    const errBody = await tokenRes.text();
    throw new Error(`Token exchange failed: ${tokenRes.status} - ${errBody}`);
  }

  const tokenData = await tokenRes.json();
  cachedToken = tokenData.access_token;
  tokenExpiry = now + (tokenData.expires_in || 3600);
  return cachedToken;
}

// ---------- CORS ----------

function corsHeaders(env) {
  return {
    'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
    'Access-Control-Max-Age': '86400',
  };
}

function corsResponse(env, body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(env),
    },
  });
}

// ---------- Sheets API helpers ----------

const SHEETS_BASE = 'https://sheets.googleapis.com/v4/spreadsheets';

// Allowed spreadsheet IDs (whitelist for security)
const ALLOWED_SPREADSHEETS = new Set([
  '1BaMup71ObVneuEBn-VWwGgU2vPpg9IZX9lFui_qTO8c', // Personal OS planner
  '1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs', // TOS Dashboard
  '1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E', // Team Whitelist
]);

function getSpreadsheetId(env, requestSpreadsheetId) {
  if (requestSpreadsheetId && ALLOWED_SPREADSHEETS.has(requestSpreadsheetId)) {
    return requestSpreadsheetId;
  }
  return env.SPREADSHEET_ID; // default to personal planner
}

async function sheetsRead(env, range, spreadsheetId) {
  const token = await getAccessToken(env);
  const ssId = spreadsheetId || env.SPREADSHEET_ID;
  const url = `${SHEETS_BASE}/${ssId}/values/${encodeURIComponent(range)}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Sheets read error ${res.status}: ${err}`);
  }
  return res.json();
}

async function sheetsUpdate(env, range, values, spreadsheetId) {
  const token = await getAccessToken(env);
  const ssId = spreadsheetId || env.SPREADSHEET_ID;
  const url = `${SHEETS_BASE}/${ssId}/values/${encodeURIComponent(range)}?valueInputOption=USER_ENTERED`;
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ range, values }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Sheets update error ${res.status}: ${err}`);
  }
  return res.json();
}

async function sheetsAppend(env, range, values, spreadsheetId) {
  const token = await getAccessToken(env);
  const ssId = spreadsheetId || env.SPREADSHEET_ID;
  const url = `${SHEETS_BASE}/${ssId}/values/${encodeURIComponent(range)}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ values }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Sheets append error ${res.status}: ${err}`);
  }
  return res.json();
}

async function sheetsMeta(env) {
  const token = await getAccessToken(env);
  const url = `${SHEETS_BASE}/${env.SPREADSHEET_ID}?fields=properties.title,sheets.properties.title`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Sheets meta error ${res.status}: ${err}`);
  }
  return res.json();
}

// ---------- Auth middleware ----------

function authenticate(request, env) {
  // Simple API key auth - the dashboard sends this
  const apiKey = request.headers.get('X-API-Key');
  if (apiKey && apiKey === env.WORKER_API_KEY) return true;

  // Also accept from the allowed origin (CORS already restricts)
  const origin = request.headers.get('Origin') || '';
  if (origin === env.ALLOWED_ORIGIN) return true;

  // Allow localhost for dev
  if (origin.includes('localhost') || origin.includes('127.0.0.1')) return true;

  return false;
}

// ---------- Router ----------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(env) });
    }

    // Health check
    if (path === '/health') {
      return corsResponse(env, {
        status: 'ok',
        timestamp: new Date().toISOString(),
        spreadsheet: env.SPREADSHEET_ID,
      });
    }

    // Auth check for all /api routes
    if (path.startsWith('/api/') && !authenticate(request, env)) {
      return corsResponse(env, { error: 'Unauthorized' }, 401);
    }

    try {
      // GET /api/sheets/read?range=...&spreadsheetId=...
      // GET /api/sheet?range=...  (alias — used by Conductor BOOPs, dashboard, reference docs)
      if ((path === '/api/sheets/read' || path === '/api/sheet') && request.method === 'GET') {
        const range = url.searchParams.get('range');
        if (!range) return corsResponse(env, { error: 'Missing range parameter' }, 400);
        const ssId = getSpreadsheetId(env, url.searchParams.get('spreadsheetId'));
        const data = await sheetsRead(env, range, ssId);
        return corsResponse(env, data);
      }

      // POST /api/sheets/update  {range, values, spreadsheetId?}
      if (path === '/api/sheets/update' && request.method === 'POST') {
        const body = await request.json();
        if (!body.range || !body.values) {
          return corsResponse(env, { error: 'Missing range or values' }, 400);
        }
        const ssId = getSpreadsheetId(env, body.spreadsheetId);
        const result = await sheetsUpdate(env, body.range, body.values, ssId);
        return corsResponse(env, result);
      }

      // POST /api/sheets/append  {range, values, spreadsheetId?}
      if (path === '/api/sheets/append' && request.method === 'POST') {
        const body = await request.json();
        if (!body.range || !body.values) {
          return corsResponse(env, { error: 'Missing range or values' }, 400);
        }
        const ssId = getSpreadsheetId(env, body.spreadsheetId);
        const result = await sheetsAppend(env, body.range, body.values, ssId);
        return corsResponse(env, result);
      }

      // GET /api/sheets/meta
      if (path === '/api/sheets/meta' && request.method === 'GET') {
        const data = await sheetsMeta(env);
        return corsResponse(env, data);
      }

      return corsResponse(env, { error: 'Not found' }, 404);
    } catch (err) {
      console.error('Worker error:', err);
      return corsResponse(env, { error: err.message }, 500);
    }
  },
};
