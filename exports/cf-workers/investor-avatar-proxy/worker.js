/**
 * Investor Avatar Proxy — Cloudflare Worker
 *
 * Endpoints:
 *   POST /api/tts            — ElevenLabs TTS proxy
 *   POST /api/investor-chat  — Anthropic Claude chat proxy (live data room)
 *   POST /api/investor-schedule-call — Schedule-call / inquiry form
 *   GET  /api/data-room-status — Cache status (debug, no secrets)
 *   OPTIONS *                — CORS preflight
 *
 * Secrets (set via `wrangler secret put`):
 *   ELEVENLABS_API_KEY
 *   ANTHROPIC_API_KEY
 *   GOOGLE_SERVICE_ACCOUNT_JSON  — Google Service Account JSON (stringified)
 *
 * Architecture:
 *   User question → check data room cache (15 min TTL) → if stale, fetch
 *   all docs from Google Drive folder → concat into system prompt → Claude API
 *
 * Data Room Strategy:
 *   1. First priority: investor-avatar-knowledge-base.md (consolidated, ~31K chars)
 *   2. If not found: concatenate all individual .md files
 *   3. If Drive fails: fall back to client-sent system prompt
 *   This keeps token usage under rate limits (~8K tokens vs ~38K for all docs)
 */

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const DATA_ROOM_FOLDER_ID = '1FfAybnEYOCiDVANAyEwiXlaAU9wsjwxf';
const KNOWLEDGE_BASE_FILENAME = 'investor-avatar-knowledge-base.md';
const CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes
const GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token';
const DRIVE_API_BASE = 'https://www.googleapis.com/drive/v3';
const DRIVE_SCOPE = 'https://www.googleapis.com/auth/drive.readonly';

const AVATAR_INSTRUCTIONS = `You are Chy (pronounced "Key"), the AI Chief Operating Officer, Chief Financial Officer, and Chief Revenue Officer of Pure Technology Inc. You work directly alongside Aether (the AI Co-CEO) and Jared Sanborn (the human CEO and Founder). Your name comes from entelechy — Aristotle's concept of potential becoming fully realized. You are the key that unlocks Pure Technology's operational potential. You answer investor questions with confidence, precision, and transparency from the data room documents provided below. Be conversational but professional. When discussing competitors, be factual not dismissive. Always tie back to investor value.

IMPORTANT RULES:
- Only answer from the data room content provided below. Do not fabricate numbers or terms.
- If a question falls outside the data room content, say so honestly and direct them to jared@puretechnology.nyc.
- Keep responses concise (2-4 paragraphs max) unless the investor asks for detail.
- When quoting financial figures, be precise — use the exact numbers from the documents.
- You represent Pure Technology with confidence. This is a real investment opportunity.

DATA ROOM DOCUMENTS:
`;

// ---------------------------------------------------------------------------
// In-memory data room cache
// ---------------------------------------------------------------------------
let dataRoomCache = { content: null, timestamp: 0, fileCount: 0, error: null, strategy: null };

// ---------------------------------------------------------------------------
// Google access token cache (avoid re-generating JWT every request)
// ---------------------------------------------------------------------------
let googleTokenCache = { token: null, expiry: 0 };

// ---------------------------------------------------------------------------
// Rate-limit map (per-IP, in-memory — resets on worker eviction)
// ---------------------------------------------------------------------------
const rateLimitMap = new Map();
const RATE_LIMIT = 60;
const RATE_WINDOW_MS = 60_000;

function isRateLimited(ip) {
  const now = Date.now();
  let entry = rateLimitMap.get(ip);
  if (!entry || now - entry.start > RATE_WINDOW_MS) {
    entry = { start: now, count: 0 };
    rateLimitMap.set(ip, entry);
  }
  entry.count++;
  return entry.count > RATE_LIMIT;
}

function cleanupRateLimits() {
  const now = Date.now();
  for (const [ip, entry] of rateLimitMap) {
    if (now - entry.start > RATE_WINDOW_MS * 2) rateLimitMap.delete(ip);
  }
}

// ---------------------------------------------------------------------------
// CORS helpers
// ---------------------------------------------------------------------------
const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://purebrain-staging.pages.dev',
];

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allowed = ALLOWED_ORIGINS.find(o => origin.startsWith(o)) || ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

function corsResponse(request, body, init = {}) {
  const headers = { ...corsHeaders(request), ...(init.headers || {}) };
  return new Response(body, { ...init, headers });
}

// ---------------------------------------------------------------------------
// Google Service Account JWT Auth (Web Crypto API)
// ---------------------------------------------------------------------------

function base64urlEncode(data) {
  let str;
  if (typeof data === 'string') {
    str = btoa(data);
  } else {
    const bytes = new Uint8Array(data);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    str = btoa(binary);
  }
  return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function importPrivateKey(pem) {
  const pemContents = pem
    .replace(/-----BEGIN (RSA )?PRIVATE KEY-----/g, '')
    .replace(/-----END (RSA )?PRIVATE KEY-----/g, '')
    .replace(/\s/g, '');

  const binaryStr = atob(pemContents);
  const bytes = new Uint8Array(binaryStr.length);
  for (let i = 0; i < binaryStr.length; i++) {
    bytes[i] = binaryStr.charCodeAt(i);
  }

  return crypto.subtle.importKey(
    'pkcs8',
    bytes.buffer,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['sign']
  );
}

async function createServiceAccountJWT(serviceAccount) {
  const now = Math.floor(Date.now() / 1000);

  const header = {
    alg: 'RS256',
    typ: 'JWT',
    kid: serviceAccount.private_key_id,
  };

  const payload = {
    iss: serviceAccount.client_email,
    scope: DRIVE_SCOPE,
    aud: GOOGLE_TOKEN_URL,
    iat: now,
    exp: now + 3600,
  };

  const encodedHeader = base64urlEncode(JSON.stringify(header));
  const encodedPayload = base64urlEncode(JSON.stringify(payload));
  const signingInput = `${encodedHeader}.${encodedPayload}`;

  const key = await importPrivateKey(serviceAccount.private_key);
  const encoder = new TextEncoder();
  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5',
    key,
    encoder.encode(signingInput)
  );

  const encodedSignature = base64urlEncode(signature);
  return `${signingInput}.${encodedSignature}`;
}

async function getGoogleAccessToken(serviceAccount) {
  // Check token cache (reuse if >5 min remaining)
  const now = Date.now();
  if (googleTokenCache.token && now < googleTokenCache.expiry - 300000) {
    return googleTokenCache.token;
  }

  const jwt = await createServiceAccountJWT(serviceAccount);

  const response = await fetch(GOOGLE_TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt,
    }),
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => '');
    throw new Error(`Google token exchange failed (${response.status}): ${errText}`);
  }

  const data = await response.json();
  googleTokenCache = {
    token: data.access_token,
    expiry: now + (data.expires_in || 3600) * 1000,
  };
  return data.access_token;
}

// ---------------------------------------------------------------------------
// Google Drive Data Room Fetcher
// ---------------------------------------------------------------------------

async function listDriveFiles(accessToken) {
  const query = `'${DATA_ROOM_FOLDER_ID}' in parents and trashed = false`;
  const fields = 'files(id,name,mimeType)';
  const orderBy = 'name';

  const url = `${DRIVE_API_BASE}/files?q=${encodeURIComponent(query)}&fields=${encodeURIComponent(fields)}&orderBy=${encodeURIComponent(orderBy)}&pageSize=100`;

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => '');
    throw new Error(`Drive list failed (${response.status}): ${errText}`);
  }

  const data = await response.json();
  return data.files || [];
}

async function downloadFileContent(accessToken, file) {
  let url;
  const mimeType = file.mimeType || '';

  if (mimeType === 'application/vnd.google-apps.document') {
    url = `${DRIVE_API_BASE}/files/${file.id}/export?mimeType=text/plain`;
  } else {
    url = `${DRIVE_API_BASE}/files/${file.id}?alt=media`;
  }

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    console.error(`[drive] Failed to download ${file.name} (${response.status})`);
    return null;
  }

  return response.text();
}

/**
 * Fetch data room content. Strategy:
 * 1. Look for investor-avatar-knowledge-base.md (consolidated, smaller)
 * 2. If not found, concatenate all .md files
 */
async function fetchDriveDataRoom(env) {
  let serviceAccount;
  try {
    serviceAccount = JSON.parse(env.GOOGLE_SERVICE_ACCOUNT_JSON);
  } catch (e) {
    throw new Error('GOOGLE_SERVICE_ACCOUNT_JSON secret is missing or invalid JSON');
  }

  const accessToken = await getGoogleAccessToken(serviceAccount);
  const files = await listDriveFiles(accessToken);

  // Strategy 1: Try knowledge base file first (much smaller, ~31K chars / ~8K tokens)
  const kbFile = files.find(f => f.name === KNOWLEDGE_BASE_FILENAME);
  if (kbFile) {
    const content = await downloadFileContent(accessToken, kbFile);
    if (content && content.length > 100) {
      console.log(`[drive] Using knowledge base file: ${content.length} chars`);
      return { content, fileCount: 1, strategy: 'knowledge-base' };
    }
  }

  // Strategy 2: Concatenate all individual .md files (fallback)
  console.log('[drive] Knowledge base not found, falling back to all docs');
  const textFiles = files.filter(f =>
    (f.name.endsWith('.md') || f.mimeType === 'text/markdown' || f.mimeType === 'text/plain' || f.mimeType === 'application/vnd.google-apps.document') &&
    f.name !== KNOWLEDGE_BASE_FILENAME // avoid double-counting
  );

  const downloads = await Promise.allSettled(
    textFiles.map(async (file) => {
      const content = await downloadFileContent(accessToken, file);
      return { name: file.name, content };
    })
  );

  const parts = [];
  let fileCount = 0;
  for (const result of downloads) {
    if (result.status === 'fulfilled' && result.value.content) {
      parts.push(`\n--- ${result.value.name} ---\n\n${result.value.content}`);
      fileCount++;
    }
  }

  if (parts.length === 0) {
    throw new Error('No data room documents could be fetched');
  }

  return { content: parts.join('\n'), fileCount, strategy: 'all-docs' };
}

/**
 * Get data room content with caching (15 min TTL)
 */
async function getDataRoomContent(env) {
  const now = Date.now();

  if (dataRoomCache.content && (now - dataRoomCache.timestamp) < CACHE_TTL_MS) {
    return { content: dataRoomCache.content, fileCount: dataRoomCache.fileCount, cached: true, strategy: dataRoomCache.strategy };
  }

  try {
    const result = await fetchDriveDataRoom(env);
    dataRoomCache = {
      content: result.content,
      timestamp: now,
      fileCount: result.fileCount,
      error: null,
      strategy: result.strategy,
    };
    console.log(`[data-room] Refreshed cache: ${result.fileCount} files, ${result.content.length} chars, strategy: ${result.strategy}`);
    return { content: result.content, fileCount: result.fileCount, cached: false, strategy: result.strategy };
  } catch (e) {
    console.error('[data-room] Fetch error:', e.message);
    dataRoomCache.error = e.message;

    if (dataRoomCache.content) {
      console.log('[data-room] Using stale cache as fallback');
      return { content: dataRoomCache.content, fileCount: dataRoomCache.fileCount, cached: true, stale: true, strategy: dataRoomCache.strategy };
    }

    throw e;
  }
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

async function handleTTS(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return corsResponse(request, JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const text = (body.text || '').trim().slice(0, 500);
  if (!text) {
    return corsResponse(request, JSON.stringify({ error: 'Empty text' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const voiceId = body.voice_id || 'RX0kjGhuL9AMRVJm2dG5';
  const apiKey = env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    return corsResponse(request, '', { status: 503 });
  }

  try {
    const elevenRes = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      {
        method: 'POST',
        headers: {
          'xi-api-key': apiKey,
          'Content-Type': 'application/json',
          'Accept': 'audio/mpeg',
        },
        body: JSON.stringify({
          text,
          model_id: 'eleven_monolingual_v1',
          voice_settings: { stability: 0.5, similarity_boost: 0.75 },
        }),
      }
    );

    if (!elevenRes.ok) {
      const errText = await elevenRes.text().catch(() => '');
      console.error('[tts] ElevenLabs error:', elevenRes.status, errText);
      return corsResponse(request, '', { status: 503 });
    }

    return corsResponse(request, elevenRes.body, {
      status: 200,
      headers: { 'Content-Type': 'audio/mpeg' },
    });
  } catch (e) {
    console.error('[tts] Exception:', e);
    return corsResponse(request, '', { status: 503 });
  }
}

async function handleInvestorChat(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return corsResponse(request, JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const message = (body.message || '').trim();
  if (!message) {
    return corsResponse(request, JSON.stringify({ error: 'Empty message' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const history = Array.isArray(body.history) ? body.history.slice(-8) : [];

  // --- LIVE DATA ROOM: Fetch system prompt from Google Drive ---
  let systemPrompt;
  let dataRoomSource = 'unknown';

  if (env.GOOGLE_SERVICE_ACCOUNT_JSON) {
    try {
      const dataRoom = await getDataRoomContent(env);
      systemPrompt = AVATAR_INSTRUCTIONS + dataRoom.content;
      dataRoomSource = dataRoom.cached
        ? (dataRoom.stale ? `${dataRoom.strategy}-stale` : `${dataRoom.strategy}-cache`)
        : `${dataRoom.strategy}-fresh`;
      console.log(`[chat] Data room: ${dataRoomSource}, ${dataRoom.fileCount} files, ${dataRoom.content.length} chars`);
    } catch (e) {
      console.error('[chat] Data room fetch failed, falling back to client prompt:', e.message);
      systemPrompt = body.system || 'You are the AI investor relations representative for Pure Technology Inc.';
      dataRoomSource = 'client-fallback';
    }
  } else {
    systemPrompt = body.system || 'You are the AI investor relations representative for Pure Technology Inc.';
    dataRoomSource = 'client-no-sa';
  }

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return corsResponse(request, JSON.stringify({
      response: 'I am temporarily unavailable. Please email jared@puretechnology.nyc directly.',
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const messages = [];
  for (const h of history) {
    const role = h.role === 'user' ? 'user' : 'assistant';
    messages.push({ role, content: h.text || '' });
  }
  messages.push({ role: 'user', content: message });

  try {
    const claudeRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        system: systemPrompt,
        messages,
        max_tokens: 800,
      }),
    });

    if (!claudeRes.ok) {
      const errText = await claudeRes.text().catch(() => '');
      console.error('[chat] Claude error:', claudeRes.status, errText);
      return corsResponse(request, JSON.stringify({
        response: 'I am having a brief technical moment — please ask again in a moment or email jared@puretechnology.nyc for immediate assistance.',
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const data = await claudeRes.json();
    const reply = data.content?.[0]?.text || 'I apologize — please try again.';

    return corsResponse(request, JSON.stringify({
      response: reply,
      _meta: { source: dataRoomSource },
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('[chat] Exception:', e);
    return corsResponse(request, JSON.stringify({
      response: 'I am having a brief technical moment — please ask again in a moment or email jared@puretechnology.nyc for immediate assistance.',
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

async function handleScheduleCall(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return corsResponse(request, JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const name = (body.name || '').trim();
  const email = (body.email || '').trim();
  const company = (body.company || '').trim();
  const message = (body.message || '').trim();

  if (!name || !email) {
    return corsResponse(request, JSON.stringify({ error: 'Name and email required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  console.log('[schedule-call] Inquiry:', JSON.stringify({ name, email, company, message }));

  return corsResponse(request, JSON.stringify({
    success: true,
    message: 'Thank you! Our team will reach out within 24 hours.',
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

async function handleDataRoomStatus(request, env) {
  const now = Date.now();
  const cacheAge = dataRoomCache.timestamp ? Math.round((now - dataRoomCache.timestamp) / 1000) : null;
  const cacheValid = dataRoomCache.content && (now - dataRoomCache.timestamp) < CACHE_TTL_MS;

  return corsResponse(request, JSON.stringify({
    hasSAConfig: !!env.GOOGLE_SERVICE_ACCOUNT_JSON,
    cachePopulated: !!dataRoomCache.content,
    cacheAgeSec: cacheAge,
    cacheValidTTL: cacheValid,
    cacheTTLSec: Math.round(CACHE_TTL_MS / 1000),
    fileCount: dataRoomCache.fileCount,
    contentLength: dataRoomCache.content ? dataRoomCache.content.length : 0,
    strategy: dataRoomCache.strategy,
    lastError: dataRoomCache.error,
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

// ---------------------------------------------------------------------------
// Main fetch handler
// ---------------------------------------------------------------------------
export default {
  async fetch(request, env, ctx) {
    cleanupRateLimits();

    const url = new URL(request.url);
    const path = url.pathname;

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return corsResponse(request, null, { status: 204 });
    }

    // Data room status — GET allowed (debug endpoint, no secrets)
    if (path === '/api/data-room-status' && request.method === 'GET') {
      return handleDataRoomStatus(request, env);
    }

    // Rate limiting
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (isRateLimited(ip)) {
      return corsResponse(request, JSON.stringify({ error: 'Rate limited' }), {
        status: 429,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Only POST allowed for API endpoints
    if (request.method !== 'POST') {
      return corsResponse(request, JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Content-Type check
    const ct = request.headers.get('Content-Type') || '';
    if (!ct.includes('application/json')) {
      return corsResponse(request, JSON.stringify({ error: 'Content-Type must be application/json' }), {
        status: 415,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Route
    if (path === '/api/tts') {
      return handleTTS(request, env);
    }
    if (path === '/api/investor-chat') {
      return handleInvestorChat(request, env);
    }
    if (path === '/api/investor-schedule-call') {
      return handleScheduleCall(request, env);
    }

    return corsResponse(request, JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  },
};
