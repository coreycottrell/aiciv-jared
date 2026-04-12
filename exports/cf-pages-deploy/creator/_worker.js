/**
 * PureBrain Creator AI — Cloudflare Worker Backend
 * Night 2 Sprint | 2026-03-21
 * Sprint 3 additions | 2026-03-21
 * Night 4 additions | 2026-03-21
 *
 * Bindings required (wrangler.toml):
 *   CREATOR_DB     — D1 database
 *   ANTHROPIC_API_KEY — Anthropic API key (secret)
 *   JWT_SECRET     — token signing secret (var or secret)
 *
 * Night 2 additions:
 *   - POST /api/creator/voice/analyze         (Task 2.1 — voice fingerprint)
 *   - POST /api/creator/content/generate      (Task 2.2/2.3 — enhanced + generate_all)
 *   - POST /api/creator/interview/start       (Task 2.5 — interview mode start)
 *   - POST /api/creator/interview/respond     (Task 2.6 — interview follow-up)
 *   - POST /api/creator/interview/generate    (Task 2.6 — generate from transcript)
 *   - GET  /api/creator/content/drafts        (Task 2.4 — list drafts)
 *   - PUT  /api/creator/content/drafts/:id    (Task 2.9 — update draft status/rating)
 *   - POST /api/creator/content/check-overlap (Task 2.8 — memory check)
 *   - GET  /api/creator/stats                 (dashboard stats)
 *
 * Sprint 3 additions (fan-facing public endpoints + product CRUD):
 *   - GET  /api/fan/creator/:handle           (public — creator profile for chat page)
 *   - POST /api/fan/chat                      (public — main fan chat)
 *   - POST /api/fan/lead                      (public — capture fan email)
 *   - GET  /api/creator/products              (auth — list products)
 *   - POST /api/creator/products              (auth — create product)
 *   - DELETE /api/creator/products/:id        (auth — delete product)
 *   - GET  /api/fan/tts/:msgId                 (public — ElevenLabs TTS for AI messages)
 *   - Route /:handle/chat                     (serve chat.html for fan chat pages)
 *
 * Night 4 additions:
 *   - GET  /api/creator/analytics             (auth — full analytics dashboard data)
 *   - GET  /api/fan/paywall-status            (public — fan paywall check)
 *
 * Night 6 additions:
 *   - POST /api/creator/profile-optimizer/scan     (auth — LinkedIn profile silent scan)
 *   - POST /api/creator/profile-optimizer/optimize (auth — optimize one profile section)
 *   - GET  /api/creator/profile-optimizer/status   (auth — which sections done)
 *   - POST /api/creator/content/audit              (auth — full 11-step content audit)
 *   - PUT  /api/creator/monetization               (auth — set paywall + tier pricing)
 *   - POST /api/fan/subscribe                      (public — fan tier upgrade)
 *   - POST /api/creator/voice/clone                (auth — ElevenLabs voice clone)
 *   - GET  /api/creator/email-sequences            (auth — list email sequences)
 *   - PUT  /api/creator/email-sequences/:id        (auth — update sequence)
 *   - POST /api/creator/email-sequences/generate   (auth — AI-generate welcome sequence)
 *   - GET  /api/creator/email-queue                (auth — view pending emails)
 */

const ALLOWED_ORIGINS = [
  'https://creator.purebrain.ai',
  'https://purebrain-staging.pages.dev',
  'http://localhost:3000',
];

// ============================================================
// CORS helpers
// ============================================================
function corsHeaders(origin, publicEndpoint = false) {
  // Fan (public) endpoints allow any origin — fans come from anywhere
  const allowed = publicEndpoint ? (origin || '*') : (ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0]);
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
}

function publicJsonResponse(data, status = 200, origin = '') {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(origin, true),
    },
  });
}

function publicErrorResponse(message, status = 400, origin = '') {
  return publicJsonResponse({ error: true, message }, status, origin);
}

function jsonResponse(data, status = 200, origin = '') {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(origin),
    },
  });
}

function errorResponse(message, status = 400, origin = '') {
  return jsonResponse({ error: true, message }, status, origin);
}

// Constant-time string comparison to prevent timing attacks
function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

// ============================================================
// Password hashing via PBKDF2 (SubtleCrypto — CF Workers native)
// Format stored: "pbkdf2:salt_hex:hash_hex" or legacy "salt:hash"
// ============================================================
async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']
  );
  const derived = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    keyMaterial, 256
  );
  const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('');
  const hashHex = Array.from(new Uint8Array(derived)).map(b => b.toString(16).padStart(2, '0')).join('');
  return `pbkdf2:${saltHex}:${hashHex}`;
}

async function verifyPassword(password, storedHash) {
  const parts = storedHash.split(':');
  const encoder = new TextEncoder();

  // PBKDF2 format: "pbkdf2:salt_hex:hash_hex"
  if (parts[0] === 'pbkdf2' && parts.length === 3) {
    const salt = new Uint8Array(parts[1].match(/.{2}/g).map(b => parseInt(b, 16)));
    const keyMaterial = await crypto.subtle.importKey(
      'raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']
    );
    const derived = await crypto.subtle.deriveBits(
      { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
      keyMaterial, 256
    );
    const hashHex = Array.from(new Uint8Array(derived)).map(b => b.toString(16).padStart(2, '0')).join('');
    return timingSafeEqual(hashHex, parts[2]);
  }

  // Legacy SHA-256 format: "salt:hash" — verify and caller should re-hash
  if (parts.length === 2) {
    const [salt, expectedHash] = parts;
    if (!salt || !expectedHash) return false;
    const data = encoder.encode(salt + password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return timingSafeEqual(hash, expectedHash);
  }

  return false;
}

// ============================================================
// Session / token management
// ============================================================
async function createSession(creatorId, env) {
  const token = crypto.randomUUID() + '-' + crypto.randomUUID();
  const expiresAt = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 30; // 30 days
  await env.CREATOR_DB.prepare(
    'INSERT INTO sessions (token, creator_id, expires_at) VALUES (?, ?, ?)'
  ).bind(token, creatorId, expiresAt).run();
  return token;
}

async function verifyToken(token, env) {
  if (!token) return null;
  const now = Math.floor(Date.now() / 1000);
  const session = await env.CREATOR_DB.prepare(
    'SELECT creator_id FROM sessions WHERE token = ? AND expires_at > ?'
  ).bind(token, now).first();
  return session ? session.creator_id : null;
}

function extractToken(request) {
  const auth = request.headers.get('Authorization') || '';
  if (auth.startsWith('Bearer ')) return auth.slice(7);
  return null;
}

// ============================================================
// Anthropic API helper
// ============================================================
async function callClaude(env, systemPrompt, userPrompt, maxTokens = 1024) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY.trim(),
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5',
      max_tokens: maxTokens,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Anthropic API error ${response.status}: ${err}`);
  }
  const data = await response.json();
  return data.content?.[0]?.text || '';
}

// ============================================================
// CSV parser (simple — handles content,date,platform or just content)
// ============================================================
function parseCSV(csvText) {
  const lines = csvText.trim().split('\n');
  if (lines.length === 0) return [];

  const header = lines[0].toLowerCase().split(',').map(h => h.trim().replace(/"/g, ''));
  const hasContent = header.includes('content');
  const contentIdx = hasContent ? header.indexOf('content') : 0;
  const platformIdx = header.indexOf('platform');
  const dateIdx = header.indexOf('date');

  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    // Simple CSV split (handles quoted fields with commas)
    const cols = line.match(/(".*?"|[^,]+)(?=\s*,|\s*$)/g) || [line];
    const clean = (s) => (s || '').replace(/^"|"$/g, '').trim();

    const content = clean(cols[contentIdx]);
    if (!content) continue;

    rows.push({
      content_text: content,
      platform: platformIdx >= 0 ? (clean(cols[platformIdx]) || 'other') : 'other',
      posted_at: dateIdx >= 0 && cols[dateIdx]
        ? Math.floor(new Date(clean(cols[dateIdx])).getTime() / 1000) || null
        : null,
    });
  }
  return rows;
}

// ============================================================
// Shared: build voice fingerprint context for system prompts
// ============================================================
function buildVoiceContext(settings, samples) {
  const fingerprint = settings.voice_fingerprint;
  let voiceSection = `CREATOR VOICE PROFILE:
- Tone: ${settings.tone || 'conversational'}
- Formality: ${settings.formality || 'balanced'}
- Voice notes from creator: "${settings.voice_notes || 'None provided'}"`;

  if (fingerprint) {
    voiceSection += `

EXTRACTED VOICE FINGERPRINT (deep style analysis):
- Avg sentence length: ${fingerprint.avg_sentence_length || 'unknown'}
- Vocabulary complexity: ${fingerprint.vocabulary_complexity || 'unknown'}
- Emoji usage: ${fingerprint.emoji_usage || 'none'}
- CTA style: ${fingerprint.cta_style || 'unknown'}
- Opening hook pattern: ${fingerprint.opening_hook_pattern || 'unknown'}
- Hashtag pattern: ${fingerprint.hashtag_pattern || 'unknown'}
- Recurring phrases: ${(fingerprint.recurring_phrases || []).join(', ') || 'none identified'}
- Writing personality: ${fingerprint.writing_personality || 'unknown'}`;
  }

  if (samples) {
    voiceSection += `\n\nSAMPLE CONTENT FROM THIS CREATOR (study and match their style):\n${samples}`;
  }

  return voiceSection;
}

// ============================================================
// Platform-specific formatting guides
// ============================================================
const PLATFORM_GUIDES = {
  linkedin: 'LinkedIn format: use line breaks for readability, professional hooks that open with insight or a bold claim, max 1300 characters, optional 3-5 hashtags at end. No walls of text.',
  instagram: 'Instagram format: emoji-driven opening hook on first line, storytelling narrative arc, 5-10 relevant hashtags at end, max 2200 characters. Make it visually scannable.',
  twitter: 'Twitter/X format: under 280 characters for a single tweet, OR if longer write a numbered thread (1/, 2/, 3/ etc). Each tweet must stand alone and be punchy.',
  bluesky: 'Bluesky format: under 300 characters, conversational and authentic, minimal hashtags (0-2 max), no corporate-speak. Think smart casual.',
  email: 'Email newsletter format: subject line on first line prefixed with "Subject:", then body. Personal, direct, and conversational.',
};

const LENGTH_GUIDES = {
  short: 'Keep it under 150 words.',
  medium: 'Aim for 200-400 words.',
  long: 'Write 400-700 words with depth and examples.',
};

// ============================================================
// Route handlers
// ============================================================

// GET /api/creator/handle-check?handle=xxx
async function handleCheckHandle(request, env, origin) {
  const url = new URL(request.url);
  const handle = (url.searchParams.get('handle') || '').toLowerCase().trim();

  if (!handle) return errorResponse('handle is required', 400, origin);
  if (!/^[a-z0-9_]{3,32}$/.test(handle)) {
    return jsonResponse({ available: false, reason: 'Handle must be 3-32 chars, letters/numbers/underscores only' }, 200, origin);
  }

  const existing = await env.CREATOR_DB.prepare(
    'SELECT id FROM creators WHERE handle = ?'
  ).bind(handle).first();

  return jsonResponse({ available: !existing, handle }, 200, origin);
}

// POST /api/creator/signup
async function handleSignup(request, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { email, password, handle, display_name, tone, formality, voice_notes, plan } = body;

  if (!email || !password || !handle || !display_name) {
    return errorResponse('email, password, handle, and display_name are required', 400, origin);
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return errorResponse('Invalid email address', 400, origin);
  }
  if (password.length < 8) {
    return errorResponse('Password must be at least 8 characters', 400, origin);
  }
  if (!/^[a-z0-9_]{3,32}$/.test(handle.toLowerCase())) {
    return errorResponse('Handle must be 3-32 chars, alphanumeric + underscores', 400, origin);
  }

  // Check handle + email uniqueness
  const existingHandle = await env.CREATOR_DB.prepare(
    'SELECT id FROM creators WHERE handle = ?'
  ).bind(handle.toLowerCase()).first();
  if (existingHandle) return errorResponse('Handle already taken', 409, origin);

  const existingEmail = await env.CREATOR_DB.prepare(
    'SELECT id FROM creators WHERE email = ?'
  ).bind(email.toLowerCase()).first();
  if (existingEmail) return errorResponse('Email already registered', 409, origin);

  const passwordHash = await hashPassword(password);
  const settings = JSON.stringify({
    tone: tone || 'conversational',
    formality: formality || 'balanced',
    voice_notes: voice_notes || '',
    plan: plan || 'starter',
  });

  const trialEndsAt = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7; // 7 days

  await env.CREATOR_DB.prepare(`
    INSERT INTO creators (handle, email, password_hash, display_name, subscription_tier, subscription_status, trial_ends_at, settings)
    VALUES (?, ?, ?, ?, 'trial', 'trial', ?, ?)
  `).bind(handle.toLowerCase(), email.toLowerCase(), passwordHash, display_name, trialEndsAt, settings).run();

  const creator = await env.CREATOR_DB.prepare(
    'SELECT * FROM creators WHERE email = ?'
  ).bind(email.toLowerCase()).first();

  const token = await createSession(creator.id, env);

  return jsonResponse({
    token,
    creator: {
      id: creator.id,
      handle: creator.handle,
      email: creator.email,
      display_name: creator.display_name,
      subscription_tier: creator.subscription_tier,
      subscription_status: creator.subscription_status,
      trial_ends_at: creator.trial_ends_at,
      settings: JSON.parse(creator.settings || '{}'),
    },
  }, 201, origin);
}

// POST /api/creator/login
// Simple in-memory rate limiter (resets per worker instance lifecycle)
const rateLimitMap = new Map();
function checkRateLimit(key, maxAttempts, windowSeconds) {
  const now = Date.now();
  const entry = rateLimitMap.get(key);
  if (entry && (now - entry.start) < windowSeconds * 1000) {
    if (entry.count >= maxAttempts) return false;
    entry.count++;
    return true;
  }
  rateLimitMap.set(key, { start: now, count: 1 });
  // Cleanup old entries periodically
  if (rateLimitMap.size > 10000) {
    for (const [k, v] of rateLimitMap) {
      if (now - v.start > windowSeconds * 1000 * 2) rateLimitMap.delete(k);
    }
  }
  return true;
}

async function handleLogin(request, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { email, password } = body;
  if (!email || !password) return errorResponse('email and password are required', 400, origin);

  // Rate limit: 5 attempts per email per 60 seconds
  if (!checkRateLimit(`login:${(email || '').toLowerCase()}`, 5, 60)) {
    return errorResponse('Too many login attempts. Try again in 60 seconds.', 429, origin);
  }

  const creator = await env.CREATOR_DB.prepare(
    'SELECT * FROM creators WHERE email = ?'
  ).bind(email.toLowerCase()).first();

  if (!creator) return errorResponse('Invalid credentials', 401, origin);

  const valid = await verifyPassword(password, creator.password_hash);
  if (!valid) return errorResponse('Invalid credentials', 401, origin);

  const token = await createSession(creator.id, env);

  return jsonResponse({
    token,
    creator: {
      id: creator.id,
      handle: creator.handle,
      email: creator.email,
      display_name: creator.display_name,
      subscription_tier: creator.subscription_tier,
      subscription_status: creator.subscription_status,
      trial_ends_at: creator.trial_ends_at,
      settings: JSON.parse(creator.settings || '{}'),
    },
  }, 200, origin);
}

// GET /api/creator/profile
async function handleGetProfile(creatorId, env, origin) {
  const creator = await env.CREATOR_DB.prepare(
    'SELECT id, handle, email, display_name, subscription_tier, subscription_status, trial_ends_at, settings, created_at FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  if (!creator) return errorResponse('Creator not found', 404, origin);

  return jsonResponse({
    ...creator,
    settings: JSON.parse(creator.settings || '{}'),
  }, 200, origin);
}

// PUT /api/creator/profile
async function handleUpdateProfile(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { display_name, settings } = body;
  const now = Math.floor(Date.now() / 1000);

  if (display_name) {
    await env.CREATOR_DB.prepare(
      'UPDATE creators SET display_name = ?, updated_at = ? WHERE id = ?'
    ).bind(display_name, now, creatorId).run();
  }

  if (settings && typeof settings === 'object') {
    const current = await env.CREATOR_DB.prepare(
      'SELECT settings FROM creators WHERE id = ?'
    ).bind(creatorId).first();
    const currentSettings = JSON.parse(current?.settings || '{}');
    const merged = { ...currentSettings, ...settings };
    await env.CREATOR_DB.prepare(
      'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
    ).bind(JSON.stringify(merged), now, creatorId).run();
  }

  return handleGetProfile(creatorId, env, origin);
}

// POST /api/creator/knowledge-base — multipart form
async function handleKBUpload(request, creatorId, env, ctx, origin) {
  let formData;
  try { formData = await request.formData(); }
  catch { return errorResponse('Invalid form data', 400, origin); }

  const file = formData.get('file');
  if (!file) return errorResponse('file is required', 400, origin);

  const tag = formData.get('tag') || 'other';
  const validTags = ['pricing','methodology','faq','testimonials','bio','other'];
  const safeTag = validTags.includes(tag) ? tag : 'other';

  const filename = file.name || 'unnamed';
  const fileSize = file.size || 0;
  const ext = filename.split('.').pop().toLowerCase();
  const typeMap = { pdf: 'pdf', docx: 'docx', doc: 'docx', txt: 'txt', mp3: 'audio', mp4: 'video', wav: 'audio' };
  const fileType = typeMap[ext] || 'txt';

  const now = Math.floor(Date.now() / 1000);
  const fileId = crypto.randomUUID().replace(/-/g, '');

  await env.CREATOR_DB.prepare(`
    INSERT INTO knowledge_base_files (id, creator_id, filename, file_type, file_size, status, tag, uploaded_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'queued', ?, ?, ?, ?)
  `).bind(fileId, creatorId, filename, fileType, fileSize, safeTag, now, now, now).run();

  // Background processing simulation: update status to active after delay
  ctx.waitUntil((async () => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    const processedAt = Math.floor(Date.now() / 1000);
    await env.CREATOR_DB.prepare(
      'UPDATE knowledge_base_files SET status = ?, chunk_count = ?, processed_at = ?, updated_at = ? WHERE id = ?'
    ).bind('active', 5, processedAt, processedAt, fileId).run();
  })());

  return jsonResponse({
    id: fileId,
    filename,
    file_type: fileType,
    file_size: fileSize,
    status: 'queued',
    tag: safeTag,
    uploaded_at: now,
  }, 201, origin);
}

// GET /api/creator/knowledge-base
async function handleKBList(creatorId, env, origin) {
  const result = await env.CREATOR_DB.prepare(
    'SELECT id, filename, file_type, file_size, status, tag, chunk_count, uploaded_at, processed_at FROM knowledge_base_files WHERE creator_id = ? ORDER BY uploaded_at DESC'
  ).bind(creatorId).all();

  return jsonResponse({ files: result.results || [] }, 200, origin);
}

// DELETE /api/creator/knowledge-base/:id
async function handleKBDelete(fileId, creatorId, env, origin) {
  const file = await env.CREATOR_DB.prepare(
    'SELECT id FROM knowledge_base_files WHERE id = ? AND creator_id = ?'
  ).bind(fileId, creatorId).first();

  if (!file) return errorResponse('File not found', 404, origin);

  await env.CREATOR_DB.prepare(
    'DELETE FROM knowledge_base_files WHERE id = ? AND creator_id = ?'
  ).bind(fileId, creatorId).run();

  return jsonResponse({ deleted: true, id: fileId }, 200, origin);
}

// POST /api/creator/content-history
async function handleContentHistory(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { content, source } = body;
  if (!content) return errorResponse('content is required', 400, origin);

  const now = Math.floor(Date.now() / 1000);
  let rows = [];

  if (source === 'csv') {
    rows = parseCSV(content);
  } else {
    // Plain text: each non-empty line is one post
    const lines = content.split('\n').map(l => l.trim()).filter(l => l.length > 10);
    rows = lines.map(line => ({ content_text: line, platform: 'other', posted_at: null }));
  }

  if (rows.length === 0) return errorResponse('No valid content found to import', 400, origin);

  // Batch insert (D1 max 100 params per statement — insert one by one for simplicity)
  let imported = 0;
  for (const row of rows) {
    try {
      await env.CREATOR_DB.prepare(`
        INSERT INTO creator_content_history (creator_id, platform, content_text, posted_at, source, ingested_at, created_at)
        VALUES (?, ?, ?, ?, 'imported', ?, ?)
      `).bind(creatorId, row.platform || 'other', row.content_text, row.posted_at || null, now, now).run();
      imported++;
    } catch {
      // Skip invalid rows silently
    }
  }

  return jsonResponse({ imported_count: imported }, 200, origin);
}

// ============================================================
// Night 2: POST /api/creator/voice/analyze (Task 2.1)
// ============================================================
async function handleVoiceAnalyze(creatorId, env, origin) {
  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();
  if (!creator) return errorResponse('Creator not found', 404, origin);

  // Fetch up to 20 content history items for analysis
  const historyResult = await env.CREATOR_DB.prepare(
    'SELECT content_text, platform FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 20'
  ).bind(creatorId).all();

  const samples = historyResult.results || [];
  if (samples.length === 0) {
    return errorResponse('No content history found. Import some past content first to analyze your voice.', 400, origin);
  }

  const sampleText = samples.map((r, i) => `[Post ${i + 1} — ${r.platform}]\n${r.content_text}`).join('\n\n---\n\n');

  const systemPrompt = `You are an expert writing analyst specializing in social media voice profiling.
Your job is to analyze writing samples and extract a precise voice fingerprint as structured JSON.
Be specific and data-driven. Look for actual patterns, not generic descriptions.`;

  const userPrompt = `Analyze these ${samples.length} writing samples from creator "${creator.display_name}" and extract their voice fingerprint.

WRITING SAMPLES:
${sampleText}

Return ONLY a valid JSON object (no markdown, no explanation) with these exact fields:
{
  "avg_sentence_length": "short (under 10 words) | medium (10-20 words) | long (20+ words)",
  "vocabulary_complexity": "simple | moderate | sophisticated",
  "emoji_usage": "none | occasional (1-3 per post) | frequent (4+ per post)",
  "cta_style": "direct command | soft suggestion | question-based | none",
  "opening_hook_pattern": "describe their typical first line pattern in 10 words or less",
  "hashtag_pattern": "none | minimal (1-3) | moderate (4-7) | heavy (8+)",
  "recurring_phrases": ["phrase1", "phrase2", "phrase3"],
  "writing_personality": "describe their overall voice in one sentence",
  "paragraph_style": "one-liners | short paragraphs | long paragraphs | mixed",
  "punctuation_style": "standard | heavy ellipsis | exclamation heavy | minimal",
  "niche_keywords": ["keyword1", "keyword2", "keyword3"],
  "analyzed_at": "${new Date().toISOString()}"
}`;

  let fingerprintText;
  try {
    fingerprintText = await callClaude(env, systemPrompt, userPrompt, 1024);
  } catch (err) {
    return errorResponse('Voice analysis failed. Please try again.', 502, origin);
  }

  // Parse the JSON response
  let fingerprint;
  try {
    // Strip any accidental markdown code fences
    const cleaned = fingerprintText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    fingerprint = JSON.parse(cleaned);
  } catch {
    return errorResponse('Voice analysis returned invalid JSON. Please try again.', 502, origin);
  }

  // Merge fingerprint into creator settings
  const now = Math.floor(Date.now() / 1000);
  const currentSettings = JSON.parse(creator.settings || '{}');
  const updatedSettings = { ...currentSettings, voice_fingerprint: fingerprint };

  await env.CREATOR_DB.prepare(
    'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
  ).bind(JSON.stringify(updatedSettings), now, creatorId).run();

  return jsonResponse({
    voice_fingerprint: fingerprint,
    samples_analyzed: samples.length,
  }, 200, origin);
}

// ============================================================
// Night 2: POST /api/creator/content/generate (Task 2.2 + 2.3 — enhanced)
// ============================================================
async function handleGenerateContent(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { topic, platform, length, generate_all } = body;
  if (!topic) return errorResponse('topic is required', 400, origin);

  const safeLength = ['short','medium','long'].includes(length) ? length : 'medium';

  // Get creator profile + settings
  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();
  if (!creator) return errorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');

  // Get last 5 content history samples for voice matching
  const historyResult = await env.CREATOR_DB.prepare(
    'SELECT content_text, platform FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 5'
  ).bind(creatorId).all();
  const samples = (historyResult.results || []).map(r => r.content_text).join('\n\n---\n\n');

  const voiceContext = buildVoiceContext(settings, samples);

  const baseSystemPrompt = `You are a content ghostwriter for ${creator.display_name}. Your job is to write in their exact voice.

${voiceContext}

RULES:
- Match their sentence structure, vocabulary, and rhythm exactly
- Do NOT add a disclaimer that this is AI-generated
- Do NOT use generic phrases like "In today's fast-paced world"
- Write as if you ARE them`;

  const now = Math.floor(Date.now() / 1000);

  // generate_all: generate for all 4 platforms in one response
  if (generate_all || platform === 'all') {
    const allPlatforms = ['linkedin', 'instagram', 'twitter', 'bluesky'];

    const systemPrompt = `${baseSystemPrompt}
- ${LENGTH_GUIDES[safeLength]}`;

    const userPrompt = `Write a post about: "${topic}" for ALL FOUR of these platforms.

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "linkedin": "[LinkedIn post here — ${PLATFORM_GUIDES.linkedin}]",
  "instagram": "[Instagram post here — ${PLATFORM_GUIDES.instagram}]",
  "twitter": "[Twitter post here — ${PLATFORM_GUIDES.twitter}]",
  "bluesky": "[Bluesky post here — ${PLATFORM_GUIDES.bluesky}]"
}`;

    let generatedText;
    try {
      generatedText = await callClaude(env, systemPrompt, userPrompt, 2048);
    } catch (err) {
      return errorResponse('Content generation failed. Please try again.', 502, origin);
    }

    let contentMap;
    try {
      const cleaned = generatedText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
      contentMap = JSON.parse(cleaned);
    } catch {
      return errorResponse('Content generation returned invalid JSON. Please try again.', 502, origin);
    }

    // Store all drafts
    const draftIds = {};
    for (const plt of allPlatforms) {
      const text = contentMap[plt] || '';
      if (!text) continue;
      const draftId = crypto.randomUUID().replace(/-/g, '');
      draftIds[plt] = draftId;
      await env.CREATOR_DB.prepare(`
        INSERT INTO generated_content (id, creator_id, platform, content_text, topic, status, generation_mode, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'draft', 'on_demand', ?, ?)
      `).bind(draftId, creatorId, plt, text, topic, now, now).run();
    }

    return jsonResponse({
      generate_all: true,
      topic,
      content: contentMap,
      draft_ids: draftIds,
    }, 200, origin);
  }

  // Single platform generation
  const safePlatform = ['linkedin','instagram','twitter','bluesky','email'].includes(platform) ? platform : 'linkedin';

  const systemPrompt = `${baseSystemPrompt}
- ${LENGTH_GUIDES[safeLength]}
- ${PLATFORM_GUIDES[safePlatform]}`;

  const userPrompt = `Write a ${safePlatform} post about: "${topic}"`;

  let generatedText;
  try {
    generatedText = await callClaude(env, systemPrompt, userPrompt, 1024);
  } catch (err) {
    return errorResponse('Content generation failed. Please try again.', 502, origin);
  }

  const draftId = crypto.randomUUID().replace(/-/g, '');

  await env.CREATOR_DB.prepare(`
    INSERT INTO generated_content (id, creator_id, platform, content_text, topic, status, generation_mode, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'draft', 'on_demand', ?, ?)
  `).bind(draftId, creatorId, safePlatform, generatedText, topic, now, now).run();

  return jsonResponse({
    content: generatedText,
    platform: safePlatform,
    draft_id: draftId,
    topic,
  }, 200, origin);
}

// ============================================================
// Night 2: POST /api/creator/interview/start (Task 2.5)
// ============================================================
async function handleInterviewStart(creatorId, env, origin) {
  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();
  if (!creator) return errorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');

  // Get recent content topics to avoid repeating and to understand niche
  const historyResult = await env.CREATOR_DB.prepare(
    'SELECT content_text FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 5'
  ).bind(creatorId).all();
  const recentSamples = (historyResult.results || []).map(r => r.content_text.slice(0, 200)).join('\n');

  const systemPrompt = `You are an expert content interviewer helping ${creator.display_name} discover compelling content ideas through conversation.
Your job is to ask ONE insightful question at a time that draws out their unique experiences, opinions, and stories.
Ask questions that uncover specific details, not generic thoughts. Make them think.`;

  const userPrompt = `You are about to start an interview with ${creator.display_name} to help them create a social media post.

Their voice profile: Tone=${settings.tone || 'conversational'}, Formality=${settings.formality || 'balanced'}
${recentSamples ? `Recent content themes (so you can ask about something fresh):\n${recentSamples}` : ''}

Ask ONE opening question that will help uncover a compelling story or insight for a post.
The question should be specific, curious, and conversational — not generic.
Return ONLY the question, nothing else.`;

  let openingQuestion;
  try {
    openingQuestion = await callClaude(env, systemPrompt, userPrompt, 256);
  } catch (err) {
    return errorResponse('Interview start failed. Please try again.', 502, origin);
  }

  const now = Math.floor(Date.now() / 1000);
  const sessionId = crypto.randomUUID().replace(/-/g, '');

  const transcript = JSON.stringify([
    { role: 'interviewer', text: openingQuestion.trim(), timestamp: now }
  ]);

  await env.CREATOR_DB.prepare(`
    INSERT INTO interview_sessions (id, creator_id, status, transcript, exchange_count, created_at, updated_at)
    VALUES (?, ?, 'in_progress', ?, 0, ?, ?)
  `).bind(sessionId, creatorId, transcript, now, now).run();

  return jsonResponse({
    session_id: sessionId,
    question: openingQuestion.trim(),
    exchange_count: 0,
  }, 201, origin);
}

// ============================================================
// Night 2: POST /api/creator/interview/respond (Task 2.6)
// ============================================================
async function handleInterviewRespond(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { session_id, answer } = body;
  if (!session_id || !answer) {
    return errorResponse('session_id and answer are required', 400, origin);
  }

  const session = await env.CREATOR_DB.prepare(
    'SELECT * FROM interview_sessions WHERE id = ? AND creator_id = ?'
  ).bind(session_id, creatorId).first();

  if (!session) return errorResponse('Interview session not found', 404, origin);
  if (session.status === 'completed') {
    return errorResponse('This interview session is already completed. Use /interview/generate to create content.', 400, origin);
  }

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();
  if (!creator) return errorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');
  const now = Math.floor(Date.now() / 1000);
  const transcript = JSON.parse(session.transcript || '[]');
  const exchangeCount = (session.exchange_count || 0) + 1;

  // Add creator's answer to transcript
  transcript.push({ role: 'creator', text: answer.trim(), timestamp: now });

  // Check if we should wrap up (8+ exchanges or explicit wrap-up signal)
  const wrapUpPhrases = ['wrap it up', 'wrap up', "that's enough", "i'm done", 'done', 'stop', 'generate now', 'make the post'];
  const wantsToWrap = wrapUpPhrases.some(phrase => answer.toLowerCase().includes(phrase));

  if (wantsToWrap || exchangeCount >= 8) {
    // Transition to content-ready state
    transcript.push({
      role: 'interviewer',
      text: "Great, I have everything I need. Use 'Generate from Interview' to turn this into a post.",
      timestamp: now
    });

    await env.CREATOR_DB.prepare(
      'UPDATE interview_sessions SET transcript = ?, exchange_count = ?, status = ?, updated_at = ? WHERE id = ?'
    ).bind(JSON.stringify(transcript), exchangeCount, 'completed', now, session_id).run();

    return jsonResponse({
      session_id,
      status: 'completed',
      message: "Interview complete. Ready to generate content.",
      exchange_count: exchangeCount,
      ready_to_generate: true,
    }, 200, origin);
  }

  // Build transcript context for follow-up question
  const transcriptContext = transcript
    .map(t => `${t.role === 'interviewer' ? 'Interviewer' : creator.display_name}: ${t.text}`)
    .join('\n\n');

  const systemPrompt = `You are an expert content interviewer helping ${creator.display_name} discover compelling content ideas.
Ask ONE specific follow-up question based on what they just said. Dig deeper into details, emotions, or specific examples.
Never repeat a question already asked. Make each question build on the previous answer.`;

  const userPrompt = `Interview transcript so far:
${transcriptContext}

Ask ONE follow-up question to dig deeper. Be specific and curious.
Return ONLY the question, nothing else.`;

  let followUpQuestion;
  try {
    followUpQuestion = await callClaude(env, systemPrompt, userPrompt, 256);
  } catch (err) {
    return errorResponse('Interview follow-up failed. Please try again.', 502, origin);
  }

  transcript.push({ role: 'interviewer', text: followUpQuestion.trim(), timestamp: now });

  await env.CREATOR_DB.prepare(
    'UPDATE interview_sessions SET transcript = ?, exchange_count = ?, updated_at = ? WHERE id = ?'
  ).bind(JSON.stringify(transcript), exchangeCount, now, session_id).run();

  return jsonResponse({
    session_id,
    question: followUpQuestion.trim(),
    exchange_count: exchangeCount,
    ready_to_generate: false,
  }, 200, origin);
}

// ============================================================
// Night 2: POST /api/creator/interview/generate (Task 2.6)
// ============================================================
async function handleInterviewGenerate(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { session_id, platform } = body;
  if (!session_id) return errorResponse('session_id is required', 400, origin);

  const session = await env.CREATOR_DB.prepare(
    'SELECT * FROM interview_sessions WHERE id = ? AND creator_id = ?'
  ).bind(session_id, creatorId).first();

  if (!session) return errorResponse('Interview session not found', 404, origin);

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();
  if (!creator) return errorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');
  const safePlatform = ['linkedin','instagram','twitter','bluesky','email'].includes(platform) ? platform : 'linkedin';

  const transcript = JSON.parse(session.transcript || '[]');
  if (transcript.length < 2) {
    return errorResponse('Interview transcript is too short to generate content', 400, origin);
  }

  const transcriptText = transcript
    .filter(t => t.role !== 'interviewer' || !t.text.includes("Great, I have everything"))
    .map(t => `${t.role === 'interviewer' ? 'Q' : 'A'}: ${t.text}`)
    .join('\n\n');

  // Get content history for voice samples
  const historyResult = await env.CREATOR_DB.prepare(
    'SELECT content_text FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 5'
  ).bind(creatorId).all();
  const samples = (historyResult.results || []).map(r => r.content_text).join('\n\n---\n\n');

  const voiceContext = buildVoiceContext(settings, samples);

  const systemPrompt = `You are a content ghostwriter for ${creator.display_name}. Your job is to write in their exact voice.

${voiceContext}

RULES:
- Write ONLY the finished post — no intro, no explanation, no "here's your post"
- Draw directly from what they shared in the interview
- Use their actual words, phrases, and examples where possible
- Do NOT add generic filler — only what came from the interview
- ${PLATFORM_GUIDES[safePlatform]}`;

  const userPrompt = `Turn this interview transcript into a polished ${safePlatform} post.

INTERVIEW TRANSCRIPT:
${transcriptText}

Write the post now.`;

  let generatedText;
  try {
    generatedText = await callClaude(env, systemPrompt, userPrompt, 1024);
  } catch (err) {
    return errorResponse('Content generation from interview failed. Please try again.', 502, origin);
  }

  const now = Math.floor(Date.now() / 1000);
  const draftId = crypto.randomUUID().replace(/-/g, '');

  await env.CREATOR_DB.prepare(`
    INSERT INTO generated_content (id, creator_id, platform, content_text, topic, status, generation_mode, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'draft', 'interview_mode', ?, ?)
  `).bind(draftId, creatorId, safePlatform, generatedText, `Interview Session ${session_id.slice(0, 8)}`, now, now).run();

  // Link the generated content back to the interview session
  await env.CREATOR_DB.prepare(
    'UPDATE interview_sessions SET generated_content_id = ?, updated_at = ? WHERE id = ?'
  ).bind(draftId, now, session_id).run();

  return jsonResponse({
    content: generatedText,
    platform: safePlatform,
    draft_id: draftId,
    session_id,
  }, 200, origin);
}

// ============================================================
// Night 2: GET /api/creator/content/drafts (Task 2.4)
// ============================================================
async function handleListDrafts(creatorId, env, origin) {
  const result = await env.CREATOR_DB.prepare(`
    SELECT id, platform, content_text, topic, status, generation_mode, creator_rating, notes, created_at
    FROM generated_content
    WHERE creator_id = ?
    ORDER BY created_at DESC
  `).bind(creatorId).all();

  return jsonResponse({ drafts: result.results || [] }, 200, origin);
}

// ============================================================
// Night 2: PUT /api/creator/content/drafts/:id (Task 2.9 + 2.7)
// ============================================================
async function handleUpdateDraft(draftId, request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const draft = await env.CREATOR_DB.prepare(
    'SELECT id FROM generated_content WHERE id = ? AND creator_id = ?'
  ).bind(draftId, creatorId).first();

  if (!draft) return errorResponse('Draft not found', 404, origin);

  const { status, rating, notes } = body;
  const validStatuses = ['draft', 'approved', 'rejected', 'published'];

  const updates = [];
  const values = [];
  const now = Math.floor(Date.now() / 1000);

  if (status && validStatuses.includes(status)) {
    updates.push('status = ?');
    values.push(status);
  }

  if (rating !== undefined && rating !== null) {
    const safeRating = Math.min(5, Math.max(1, parseInt(rating, 10)));
    if (!isNaN(safeRating)) {
      updates.push('creator_rating = ?');
      values.push(safeRating);
    }
  }

  if (notes !== undefined) {
    updates.push('notes = ?');
    values.push(notes);
  }

  if (updates.length === 0) {
    return errorResponse('No valid fields to update. Provide status, rating, or notes.', 400, origin);
  }

  updates.push('updated_at = ?');
  values.push(now);
  values.push(draftId);
  values.push(creatorId);

  await env.CREATOR_DB.prepare(
    `UPDATE generated_content SET ${updates.join(', ')} WHERE id = ? AND creator_id = ?`
  ).bind(...values).run();

  const updated = await env.CREATOR_DB.prepare(
    'SELECT id, platform, content_text, topic, status, generation_mode, creator_rating, notes, created_at, updated_at FROM generated_content WHERE id = ?'
  ).bind(draftId).first();

  return jsonResponse({ draft: updated }, 200, origin);
}

// ============================================================
// Night 2: POST /api/creator/content/check-overlap (Task 2.8)
// ============================================================
async function handleCheckOverlap(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { topic } = body;
  if (!topic) return errorResponse('topic is required', 400, origin);

  const topicLower = topic.toLowerCase();
  // Extract keywords (words 4+ chars, not common stop words)
  const stopWords = new Set(['that', 'this', 'with', 'from', 'have', 'been', 'will', 'your', 'what', 'when', 'where', 'which', 'they', 'their', 'there', 'about', 'more', 'into', 'then', 'than', 'just', 'some', 'also']);
  const keywords = topicLower.split(/\s+/)
    .map(w => w.replace(/[^a-z0-9]/g, ''))
    .filter(w => w.length >= 4 && !stopWords.has(w));

  if (keywords.length === 0) {
    return jsonResponse({ has_overlap: false, similar_topics: [], suggestion: null }, 200, origin);
  }

  // Search generated_content
  const draftsResult = await env.CREATOR_DB.prepare(
    'SELECT id, topic, platform, created_at, status FROM generated_content WHERE creator_id = ? ORDER BY created_at DESC LIMIT 50'
  ).bind(creatorId).all();

  // Search content_history
  const historyResult = await env.CREATOR_DB.prepare(
    'SELECT content_text, platform, ingested_at FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 50'
  ).bind(creatorId).all();

  const similarTopics = [];

  // Check drafts
  for (const draft of (draftsResult.results || [])) {
    if (!draft.topic) continue;
    const draftLower = draft.topic.toLowerCase();
    const matchCount = keywords.filter(kw => draftLower.includes(kw)).length;
    if (matchCount >= Math.min(2, keywords.length)) {
      const date = new Date(draft.created_at * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      similarTopics.push({
        source: 'draft',
        topic: draft.topic,
        platform: draft.platform,
        date,
        status: draft.status,
      });
    }
  }

  // Check content history
  for (const item of (historyResult.results || [])) {
    if (!item.content_text) continue;
    const contentLower = item.content_text.toLowerCase().slice(0, 300);
    const matchCount = keywords.filter(kw => contentLower.includes(kw)).length;
    if (matchCount >= Math.min(2, keywords.length)) {
      const date = new Date((item.ingested_at || 0) * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      const snippet = item.content_text.slice(0, 80).trim() + '...';
      similarTopics.push({
        source: 'history',
        topic: snippet,
        platform: item.platform,
        date,
        status: 'published',
      });
    }
  }

  // Deduplicate and cap at 5
  const deduped = similarTopics.slice(0, 5);
  const hasOverlap = deduped.length > 0;

  let suggestion = null;
  if (hasOverlap) {
    const first = deduped[0];
    suggestion = `You already covered "${first.topic}" on ${first.date} (${first.platform}). Consider a fresh angle or related sub-topic.`;
  }

  return jsonResponse({
    has_overlap: hasOverlap,
    similar_topics: deduped,
    suggestion,
  }, 200, origin);
}

// ============================================================
// Night 2: GET /api/creator/stats
// ============================================================
async function handleStats(creatorId, env, origin) {
  const [kbResult, historyResult, draftsResult, interviewResult] = await Promise.all([
    env.CREATOR_DB.prepare(
      "SELECT COUNT(*) as count FROM knowledge_base_files WHERE creator_id = ? AND status = 'active'"
    ).bind(creatorId).first(),
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as count FROM creator_content_history WHERE creator_id = ?'
    ).bind(creatorId).first(),
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as total, SUM(CASE WHEN status = \'draft\' THEN 1 ELSE 0 END) as pending FROM generated_content WHERE creator_id = ?'
    ).bind(creatorId).first(),
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as count FROM interview_sessions WHERE creator_id = ?'
    ).bind(creatorId).first(),
  ]);

  const kbFiles = kbResult?.count || 0;
  const contentHistory = historyResult?.count || 0;
  const draftsTotal = draftsResult?.total || 0;
  const draftsPending = draftsResult?.pending || 0;
  const interviewSessions = interviewResult?.count || 0;

  // Intelligence score: content history + kb files + drafts generated + interview count
  const intelligenceScore = contentHistory + kbFiles + draftsTotal + interviewSessions;

  return jsonResponse({
    kb_files: kbFiles,
    content_history: contentHistory,
    drafts_total: draftsTotal,
    drafts_pending: draftsPending,
    interview_sessions: interviewSessions,
    intelligence_score: intelligenceScore,
  }, 200, origin);
}

// ============================================================
// Sprint 3: GET /api/fan/creator/:handle
// Public — returns creator's public profile for the chat page
// ============================================================
async function handleFanCreatorProfile(handle, env, origin) {
  const creator = await env.CREATOR_DB.prepare(
    'SELECT id, display_name, settings FROM creators WHERE handle = ?'
  ).bind(handle.toLowerCase()).first();

  if (!creator) return publicErrorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');

  return publicJsonResponse({
    display_name: creator.display_name,
    welcome_message: settings.welcome_message || `Hi! I'm ${creator.display_name}'s AI assistant. Ask me anything!`,
    accent_color: settings.accent_color || '#6366f1',
    bg_color: settings.bg_color || '#0f0f13',
    avatar_url: settings.avatar_url || null,
  }, 200, origin);
}

// ============================================================
// Sprint 3: POST /api/fan/chat
// Public — main fan chat endpoint
// ============================================================
async function handleFanChat(request, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return publicErrorResponse('Invalid JSON', 400, origin); }

  const { handle, fan_id, conversation_id, message, fingerprint } = body;

  if (!handle) return publicErrorResponse('handle is required', 400, origin);
  if (!message || !message.trim()) return publicErrorResponse('message is required', 400, origin);

  // Cap message length to prevent token stuffing / API cost abuse
  if (message.length > 2000) return publicErrorResponse('Message too long (max 2000 characters)', 400, origin);

  // Rate limit fan chat: 20 requests per minute per IP
  const fanIp = request.headers.get('CF-Connecting-IP') || 'unknown';
  if (!checkRateLimit(`fanchat:${fanIp}`, 20, 60)) {
    return publicErrorResponse('Too many messages. Please slow down.', 429, origin);
  }

  // 1. Look up creator by handle
  const creator = await env.CREATOR_DB.prepare(
    'SELECT id, display_name, settings FROM creators WHERE handle = ?'
  ).bind(handle.toLowerCase()).first();

  if (!creator) return publicErrorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');
  const now = Math.floor(Date.now() / 1000);

  // 2. Fan lookup or creation
  let fanRecord = null;
  if (fan_id) {
    fanRecord = await env.CREATOR_DB.prepare(
      'SELECT * FROM fans WHERE id = ? AND creator_id = ?'
    ).bind(fan_id, creator.id).first();
  }
  if (!fanRecord) {
    // Create new fan
    const newFanId = crypto.randomUUID().replace(/-/g, '');
    await env.CREATOR_DB.prepare(`
      INSERT INTO fans (id, creator_id, fingerprint, first_seen_at, last_seen_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).bind(newFanId, creator.id, fingerprint || null, now, now, now, now).run();
    fanRecord = await env.CREATOR_DB.prepare(
      'SELECT * FROM fans WHERE id = ?'
    ).bind(newFanId).first();
  } else {
    // Update last_seen_at
    await env.CREATOR_DB.prepare(
      'UPDATE fans SET last_seen_at = ?, updated_at = ? WHERE id = ?'
    ).bind(now, now, fanRecord.id).run();
  }

  // 3. Conversation lookup or creation
  let convo = null;
  if (conversation_id) {
    convo = await env.CREATOR_DB.prepare(
      'SELECT * FROM fan_conversations WHERE id = ? AND fan_id = ?'
    ).bind(conversation_id, fanRecord.id).first();
  }
  if (!convo) {
    const newConvoId = crypto.randomUUID().replace(/-/g, '');
    await env.CREATOR_DB.prepare(`
      INSERT INTO fan_conversations (id, creator_id, fan_id, message_count, lead_captured, created_at, updated_at)
      VALUES (?, ?, ?, 0, 0, ?, ?)
    `).bind(newConvoId, creator.id, fanRecord.id, now, now).run();
    convo = await env.CREATOR_DB.prepare(
      'SELECT * FROM fan_conversations WHERE id = ?'
    ).bind(newConvoId).first();
  }

  // 4. Insert fan message
  const fanMsgId = crypto.randomUUID().replace(/-/g, '');
  await env.CREATOR_DB.prepare(`
    INSERT INTO fan_messages (id, conversation_id, role, content, created_at)
    VALUES (?, ?, 'fan', ?, ?)
  `).bind(fanMsgId, convo.id, message.trim(), now).run();

  // 5. Increment message_count
  const newMessageCount = (convo.message_count || 0) + 1;
  await env.CREATOR_DB.prepare(
    'UPDATE fan_conversations SET message_count = ?, updated_at = ? WHERE id = ?'
  ).bind(newMessageCount, now, convo.id).run();

  // 6. Load active KB files for RAG (keyword matching)
  const kbResult = await env.CREATOR_DB.prepare(
    "SELECT id, filename, tag FROM knowledge_base_files WHERE creator_id = ? AND status = 'active'"
  ).bind(creator.id).all();

  const kbFiles = kbResult.results || [];

  // Simple keyword extraction from fan message (words 3+ chars, excluding stop words)
  const stopWords = new Set(['the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','has','him','his','how','man','new','now','old','see','two','way','who','boy','did','its','let','put','say','she','too','use','that','this','with','from','have','been','will','your','what','when','where','which','they','their','there','about','more','into','then','than','just','some','also']);
  const msgLower = message.toLowerCase();
  const keywords = msgLower.split(/\s+/)
    .map(w => w.replace(/[^a-z0-9]/g, ''))
    .filter(w => w.length >= 3 && !stopWords.has(w));

  // Find matching KB files by filename or tag
  const matchingKB = kbFiles.filter(f => {
    const combined = ((f.filename || '') + ' ' + (f.tag || '')).toLowerCase();
    return keywords.some(kw => combined.includes(kw));
  });

  // Fall back to all KB files if no keyword match (still list them for context)
  const kbContext = kbFiles.length > 0
    ? kbFiles.map(f => `- ${f.filename} [${f.tag || 'general'}]`).join('\n')
    : 'No knowledge base files uploaded yet.';

  const matchedKBNames = matchingKB.map(f => f.filename);

  // 7. Load active products
  const productsResult = await env.CREATOR_DB.prepare(
    "SELECT name, description, price, url FROM creator_products WHERE creator_id = ? AND is_active = 1 ORDER BY display_order ASC"
  ).bind(creator.id).all();

  const products = productsResult.results || [];
  const productsContext = products.length > 0
    ? products.map(p => `- ${p.name}: ${p.description || ''} — ${p.price ? '$' + p.price : 'Contact for pricing'}${p.url ? ' | ' + p.url : ''}`).join('\n')
    : 'No products listed yet.';

  // 8. Load last 10 messages from conversation for chat history
  const historyResult = await env.CREATOR_DB.prepare(
    'SELECT role, content FROM fan_messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 10'
  ).bind(convo.id).all();

  // Reverse to chronological order (oldest first), exclude the message we just inserted
  const historyMessages = (historyResult.results || [])
    .reverse()
    .filter(m => m.content !== message.trim() || m.role !== 'fan');

  // 9. Build system prompt
  const systemPrompt = `You are ${creator.display_name}'s AI assistant. You help fans by answering questions using ${creator.display_name}'s knowledge base and expertise.

PERSONALITY:
- Tone: ${settings.tone || 'conversational'}
- Formality: ${settings.formality || 'balanced'}
- Voice notes: ${settings.voice_notes || 'None provided'}

KNOWLEDGE BASE (answer from these sources ONLY for factual questions):
${kbContext}

PRODUCTS (recommend naturally when relevant, never be pushy):
${productsContext}

${fanRecord.memory_summary ? `FAN CONTEXT:\n${fanRecord.memory_summary}` : ''}

RULES:
- Answer questions helpfully and accurately
- If you don't know something, say "I don't have that information — reach out to ${creator.display_name} directly"
- When a fan asks about pricing, courses, or services, reference the product catalog
- Be warm and conversational, matching the creator's personality
- Keep responses concise (2-3 paragraphs max)`;

  // Build messages array for Claude (conversation history + new message)
  const claudeMessages = [
    ...historyMessages.map(m => ({
      role: m.role === 'fan' ? 'user' : 'assistant',
      content: m.content,
    })),
    { role: 'user', content: message.trim() },
  ];

  // 10. Call Claude with full conversation history
  let aiReply;
  try {
    const claudeResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY.trim(),
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 512,
        system: systemPrompt,
        messages: claudeMessages,
      }),
    });
    if (!claudeResponse.ok) {
      const err = await claudeResponse.text();
      throw new Error(`Anthropic API error ${claudeResponse.status}: ${err}`);
    }
    const claudeData = await claudeResponse.json();
    aiReply = claudeData.content?.[0]?.text || "I'm not sure how to answer that — please reach out to the creator directly.";
  } catch (err) {
    return publicErrorResponse('Chat service temporarily unavailable. Please try again.', 502, origin);
  }

  // 11. Check for product recommendations
  // Purchase-intent keywords trigger product lookup
  const purchaseKeywords = ['price', 'cost', 'buy', 'enroll', 'sign up', 'sign-up', 'how much', 'course', 'program', 'purchase', 'join', 'pricing', 'subscription', 'fee', 'register'];
  const hasPurchaseIntent = purchaseKeywords.some(kw => msgLower.includes(kw));

  let recommendedProducts = [];
  if (hasPurchaseIntent && products.length > 0) {
    // Return matching products or all products if no specific match
    recommendedProducts = products.filter(p => {
      const pText = ((p.name || '') + ' ' + (p.description || '')).toLowerCase();
      return keywords.some(kw => pText.includes(kw));
    });
    if (recommendedProducts.length === 0) recommendedProducts = products;
  }

  // 12. Determine if lead_prompt should be shown
  // Show after 5 messages if fan has no email
  const lead_prompt = newMessageCount >= 5 && !fanRecord.email;

  // 13. Insert AI response into fan_messages
  const aiMsgId = crypto.randomUUID().replace(/-/g, '');
  const productRecommended = recommendedProducts.length > 0 ? recommendedProducts[0].name : null;
  const kbSourcesUsed = matchedKBNames.length > 0 ? JSON.stringify(matchedKBNames) : '[]';

  await env.CREATOR_DB.prepare(`
    INSERT INTO fan_messages (id, conversation_id, role, content, kb_sources_used, product_recommended, created_at)
    VALUES (?, ?, 'ai', ?, ?, ?, ?)
  `).bind(aiMsgId, convo.id, aiReply, kbSourcesUsed, productRecommended, now).run();

  // 14. Voice URL — generate TTS via ElevenLabs when creator has voice enabled
  let voice_url = null;
  if (settings.voice_enabled && env.ELEVENLABS_API_KEY) {
    // Point to our TTS proxy endpoint — audio generated on-demand when fan clicks play
    voice_url = `/api/fan/tts/${aiMsgId}`;
  }

  return publicJsonResponse({
    reply: aiReply,
    voice_url,
    products: recommendedProducts.map(p => ({
      name: p.name,
      description: p.description,
      price: p.price,
      url: p.url,
    })),
    conversation_id: convo.id,
    fan_id: fanRecord.id,
    lead_prompt,
    message_count: newMessageCount,
  }, 200, origin);
}

// ============================================================
// Sprint 3: POST /api/fan/lead
// Public — capture fan email
// ============================================================
async function handleFanLead(request, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return publicErrorResponse('Invalid JSON', 400, origin); }

  const { email, first_name, conversation_id, fan_id } = body;

  if (!email) return publicErrorResponse('email is required', 400, origin);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return publicErrorResponse('Invalid email address', 400, origin);
  }
  if (!fan_id) return publicErrorResponse('fan_id is required', 400, origin);
  if (!conversation_id) return publicErrorResponse('conversation_id is required', 400, origin);

  // Get creator_id from the conversation
  const convo = await env.CREATOR_DB.prepare(
    'SELECT creator_id FROM fan_conversations WHERE id = ? AND fan_id = ?'
  ).bind(conversation_id, fan_id).first();

  if (!convo) return publicErrorResponse('Conversation not found', 404, origin);

  const creatorId = convo.creator_id;
  const now = Math.floor(Date.now() / 1000);

  // Check for existing lead (don't duplicate)
  const existingLead = await env.CREATOR_DB.prepare(
    'SELECT id FROM leads WHERE email = ? AND creator_id = ?'
  ).bind(email.toLowerCase(), creatorId).first();

  let leadId;
  if (existingLead) {
    leadId = existingLead.id;
  } else {
    leadId = crypto.randomUUID().replace(/-/g, '');
    await env.CREATOR_DB.prepare(`
      INSERT INTO leads (id, creator_id, fan_id, email, first_name, capture_trigger, created_at)
      VALUES (?, ?, ?, ?, ?, 'message_count', ?)
    `).bind(leadId, creatorId, fan_id, email.toLowerCase(), first_name || null, now).run();
  }

  // Update fan record with email and first_name
  await env.CREATOR_DB.prepare(
    'UPDATE fans SET email = ?, first_name = ?, updated_at = ? WHERE id = ?'
  ).bind(email.toLowerCase(), first_name || null, now, fan_id).run();

  // Update conversation lead_captured flag
  await env.CREATOR_DB.prepare(
    'UPDATE fan_conversations SET lead_captured = 1, updated_at = ? WHERE id = ?'
  ).bind(now, conversation_id).run();

  // If this is a new lead, enqueue the welcome email sequence
  if (!existingLead) {
    await enqueueWelcomeSequence(fan_id, creatorId, email.toLowerCase(), first_name || null, env);
  }

  return publicJsonResponse({ ok: true, lead_id: leadId }, 200, origin);
}

// ============================================================
// Sprint 3: POST /api/creator/products (auth'd)
// Create a product in the creator's product catalog
// ============================================================
async function handleCreateProduct(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { name, description, price, url } = body;
  if (!name || !name.trim()) return errorResponse('name is required', 400, origin);

  // Validate product URL — only allow http/https to prevent javascript: XSS
  if (url) {
    try {
      const parsed = new URL(url);
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        return errorResponse('Product URL must be http:// or https://', 400, origin);
      }
    } catch {
      return errorResponse('Product URL must be a valid URL', 400, origin);
    }
  }

  const now = Math.floor(Date.now() / 1000);
  const productId = crypto.randomUUID().replace(/-/g, '');

  // Get current max display_order so new product goes to end
  const maxOrderResult = await env.CREATOR_DB.prepare(
    'SELECT MAX(display_order) as max_order FROM creator_products WHERE creator_id = ?'
  ).bind(creatorId).first();
  const displayOrder = (maxOrderResult?.max_order || 0) + 1;

  await env.CREATOR_DB.prepare(`
    INSERT INTO creator_products (id, creator_id, name, description, price, url, status, display_order, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
  `).bind(productId, creatorId, name.trim(), description || null, price || null, url || null, displayOrder, now, now).run();

  const product = await env.CREATOR_DB.prepare(
    'SELECT id, name, description, price, url, status, display_order, created_at FROM creator_products WHERE id = ?'
  ).bind(productId).first();

  return jsonResponse({ product }, 201, origin);
}

// ============================================================
// Sprint 3: GET /api/creator/products (auth'd)
// List creator's products
// ============================================================
async function handleListProducts(creatorId, env, origin) {
  const result = await env.CREATOR_DB.prepare(
    'SELECT id, name, description, price, url, status, display_order, created_at FROM creator_products WHERE creator_id = ? ORDER BY display_order ASC'
  ).bind(creatorId).all();

  return jsonResponse({ products: result.results || [] }, 200, origin);
}

// ============================================================
// Sprint 3: DELETE /api/creator/products/:id (auth'd)
// Delete a product, verifying ownership
// ============================================================
async function handleDeleteProduct(productId, creatorId, env, origin) {
  const product = await env.CREATOR_DB.prepare(
    'SELECT id FROM creator_products WHERE id = ? AND creator_id = ?'
  ).bind(productId, creatorId).first();

  if (!product) return errorResponse('Product not found', 404, origin);

  await env.CREATOR_DB.prepare(
    'DELETE FROM creator_products WHERE id = ? AND creator_id = ?'
  ).bind(productId, creatorId).run();

  return jsonResponse({ deleted: true, id: productId }, 200, origin);
}

// ============================================================
// Night 4: GET /api/creator/analytics
// Returns full analytics data for the analytics dashboard tab
// ============================================================
async function handleAnalytics(creatorId, env, origin) {
  const now = Math.floor(Date.now() / 1000);
  const thirtyDaysAgo = now - 60 * 60 * 24 * 30;
  const todayStart = now - (now % 86400); // approximate UTC day start

  // Run all queries in parallel
  const [
    totalFansResult,
    totalConvosResult,
    totalLeadsResult,
    totalContentResult,
    avgRatingResult,
    recentConvosResult,
    recentLeadsResult,
    contentByPlatformResult,
    dailyConvosResult,
    topTopicsResult,
  ] = await Promise.all([
    // Total unique fans
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as count FROM fans WHERE creator_id = ?'
    ).bind(creatorId).first(),

    // Total conversations
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as count FROM fan_conversations WHERE creator_id = ?'
    ).bind(creatorId).first(),

    // Total leads captured
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as count FROM leads WHERE creator_id = ?'
    ).bind(creatorId).first(),

    // Total content generated
    env.CREATOR_DB.prepare(
      'SELECT COUNT(*) as count FROM generated_content WHERE creator_id = ?'
    ).bind(creatorId).first(),

    // Average rating of rated drafts
    env.CREATOR_DB.prepare(
      'SELECT AVG(creator_rating) as avg FROM generated_content WHERE creator_id = ? AND creator_rating IS NOT NULL'
    ).bind(creatorId).first(),

    // Recent fan conversations (last 10)
    env.CREATOR_DB.prepare(`
      SELECT fc.id, fc.created_at, fc.message_count, fc.lead_captured,
             f.first_name, f.email,
             (SELECT content FROM fan_messages WHERE conversation_id = fc.id AND role = 'fan' ORDER BY created_at ASC LIMIT 1) as first_message
      FROM fan_conversations fc
      LEFT JOIN fans f ON fc.fan_id = f.id
      WHERE fc.creator_id = ?
      ORDER BY fc.created_at DESC
      LIMIT 10
    `).bind(creatorId).all(),

    // Recent leads (last 5)
    env.CREATOR_DB.prepare(`
      SELECT id, email, first_name, capture_trigger as source, created_at
      FROM leads
      WHERE creator_id = ?
      ORDER BY created_at DESC
      LIMIT 5
    `).bind(creatorId).all(),

    // Content generated by platform
    env.CREATOR_DB.prepare(`
      SELECT platform, COUNT(*) as count
      FROM generated_content
      WHERE creator_id = ?
      GROUP BY platform
      ORDER BY count DESC
    `).bind(creatorId).all(),

    // Conversations per day — last 30 days
    // D1 uses strftime for date grouping
    env.CREATOR_DB.prepare(`
      SELECT
        date(created_at, 'unixepoch') as day,
        COUNT(*) as count
      FROM fan_conversations
      WHERE creator_id = ? AND created_at >= ?
      GROUP BY day
      ORDER BY day ASC
    `).bind(creatorId, thirtyDaysAgo).all(),

    // Top topics from fan first messages (simple keyword grouping — top 5 non-stop words)
    env.CREATOR_DB.prepare(`
      SELECT content FROM fan_messages
      WHERE role = 'fan'
      AND conversation_id IN (
        SELECT id FROM fan_conversations WHERE creator_id = ?
      )
      ORDER BY created_at DESC
      LIMIT 100
    `).bind(creatorId).all(),
  ]);

  // Build 30-day date array for bar chart
  const dayLabels = [];
  const dayCounts = {};
  for (let i = 29; i >= 0; i--) {
    const d = new Date((now - i * 86400) * 1000);
    const key = d.toISOString().slice(0, 10);
    dayLabels.push(key);
    dayCounts[key] = 0;
  }
  for (const row of (dailyConvosResult.results || [])) {
    if (dayCounts.hasOwnProperty(row.day)) {
      dayCounts[row.day] = row.count;
    }
  }
  const dailyData = dayLabels.map(d => ({ day: d, count: dayCounts[d] || 0 }));

  // Extract top topics from fan messages via keyword frequency
  const stopWords = new Set(['the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','has','him','his','how','man','new','now','old','see','two','way','who','did','its','let','put','say','she','too','use','that','this','with','from','have','been','will','your','what','when','where','which','they','their','there','about','more','into','then','than','just','some','also','want','know','does','like','help','need','tell','what','much','many']);
  const wordFreq = {};
  for (const row of (topTopicsResult.results || [])) {
    const words = (row.content || '').toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length >= 4 && !stopWords.has(w));
    for (const w of words) {
      wordFreq[w] = (wordFreq[w] || 0) + 1;
    }
  }
  const topTopics = Object.entries(wordFreq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([word, count]) => ({ word, count }));

  // Lead capture rate
  const totalConvos = totalConvosResult?.count || 0;
  const totalLeads = totalLeadsResult?.count || 0;
  const leadCaptureRate = totalConvos > 0 ? Math.round((totalLeads / totalConvos) * 100) : 0;

  return jsonResponse({
    stats: {
      total_fans: totalFansResult?.count || 0,
      total_conversations: totalConvos,
      leads_captured: totalLeads,
      content_generated: totalContentResult?.count || 0,
      avg_rating: avgRatingResult?.avg ? Math.round(avgRatingResult.avg * 10) / 10 : null,
      lead_capture_rate: leadCaptureRate,
    },
    daily_conversations: dailyData,
    content_by_platform: contentByPlatformResult.results || [],
    top_topics: topTopics,
    recent_conversations: (recentConvosResult.results || []).map(c => ({
      id: c.id,
      fan_name: c.first_name || c.email || 'Anonymous Fan',
      topic: (c.first_message || '').slice(0, 80) || 'No message',
      message_count: c.message_count || 0,
      lead_captured: !!c.lead_captured,
      created_at: c.created_at,
    })),
    recent_leads: (recentLeadsResult.results || []).map(l => ({
      id: l.id,
      email: l.email,
      name: l.first_name || null,
      source: l.source || 'chat',
      created_at: l.created_at,
    })),
  }, 200, origin);
}

// ============================================================
// Night 4: GET /api/fan/paywall-status
// Public — check paywall status for a fan+creator combo
// Query params: handle, fan_id, messages_used
// ============================================================
async function handleFanPaywallStatus(request, env, origin) {
  const url = new URL(request.url);
  const handle = (url.searchParams.get('handle') || '').toLowerCase().trim();
  const fanId = url.searchParams.get('fan_id') || '';
  const messagesUsed = parseInt(url.searchParams.get('messages_used') || '0', 10);

  if (!handle) return publicErrorResponse('handle is required', 400, origin);

  const creator = await env.CREATOR_DB.prepare(
    'SELECT id, settings FROM creators WHERE handle = ?'
  ).bind(handle).first();

  if (!creator) return publicErrorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');
  const paywallEnabled = !!settings.paywall_enabled;
  const freeLimit = parseInt(settings.paywall_free_limit || '5', 10);
  const price = settings.paywall_price || null;
  const message = settings.paywall_message || null;

  if (!paywallEnabled) {
    return publicJsonResponse({
      enabled: false,
      paywalled: false,
      messages_used: messagesUsed,
      limit: freeLimit,
      price,
      message: null,
    }, 200, origin);
  }

  const paywalled = messagesUsed >= freeLimit;

  return publicJsonResponse({
    enabled: true,
    paywalled,
    messages_used: messagesUsed,
    limit: freeLimit,
    price,
    message: paywalled ? (message || `Subscribe to keep chatting with this creator's AI`) : null,
  }, 200, origin);
}

// ============================================================
// Sprint 3: GET /api/fan/tts/:msgId
// Public — on-demand ElevenLabs TTS for AI messages
// ============================================================
async function handleFanTTS(msgId, env, origin) {
  // Look up the AI message text
  const msg = await env.CREATOR_DB.prepare(
    "SELECT fm.content, fm.conversation_id FROM fan_messages fm WHERE fm.id = ? AND fm.role = 'ai'"
  ).bind(msgId).first();

  if (!msg) return publicErrorResponse('Message not found', 404, origin);

  // Get creator settings to find voice_id
  const convo = await env.CREATOR_DB.prepare(
    'SELECT creator_id FROM fan_conversations WHERE id = ?'
  ).bind(msg.conversation_id).first();

  if (!convo) return publicErrorResponse('Conversation not found', 404, origin);

  const creator = await env.CREATOR_DB.prepare(
    'SELECT settings FROM creators WHERE id = ?'
  ).bind(convo.creator_id).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const voiceId = settings.elevenlabs_voice_id || 'RX0kjGhuL9AMRVJm2dG5'; // default Aether voice

  // Truncate text to ElevenLabs limit (5000 chars)
  const text = msg.content.substring(0, 4800);

  try {
    const ttsResponse = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'xi-api-key': env.ELEVENLABS_API_KEY.trim(),
        },
        body: JSON.stringify({
          text,
          model_id: 'eleven_multilingual_v2',
          voice_settings: { stability: 0.5, similarity_boost: 0.75 },
        }),
      }
    );

    if (!ttsResponse.ok) {
      return publicErrorResponse('Voice generation unavailable', 502, origin);
    }

    return new Response(ttsResponse.body, {
      status: 200,
      headers: {
        'Content-Type': 'audio/mpeg',
        'Cache-Control': 'public, max-age=86400',
        ...corsHeaders(origin, true),
      },
    });
  } catch {
    return publicErrorResponse('Voice generation failed', 502, origin);
  }
}

// ============================================================
// Night 5 — Feature 1: Story Extraction Onboarding (GPT #6)
// POST /api/creator/story/start
// POST /api/creator/story/respond
// POST /api/creator/story/generate-missions
// POST /api/creator/story/lock
// ============================================================

const STORY_QUESTIONS = [
  "What do you do — in plain language, not your job title?",
  "What problem do you solve that nobody else does quite like you?",
  "What's the turning point that led you to do this?",
  "Who specifically do you help, and what changes for them?",
  "What do people misunderstand about what you do?",
  "If you could only be known for one thing, what would it be?",
];

async function ensureCreatorStory(creatorId, env) {
  const existing = await env.CREATOR_DB.prepare(
    'SELECT * FROM creator_stories WHERE creator_id = ?'
  ).bind(creatorId).first();
  if (existing) return existing;

  await env.CREATOR_DB.prepare(
    `INSERT INTO creator_stories (id, creator_id, answers, mission_candidates, story_status)
     VALUES (lower(hex(randomblob(16))), ?, '{}', '[]', 'in_progress')`
  ).bind(creatorId).run();

  return await env.CREATOR_DB.prepare(
    'SELECT * FROM creator_stories WHERE creator_id = ?'
  ).bind(creatorId).first();
}

async function handleStoryStart(creatorId, env, origin) {
  const story = await ensureCreatorStory(creatorId, env);
  const answers = JSON.parse(story.answers || '{}');

  // Find next unanswered question index
  const nextIndex = STORY_QUESTIONS.findIndex((_, i) => !answers[i]);

  if (nextIndex === -1 || story.locked_mission) {
    return jsonResponse({
      done: true,
      locked_mission: story.locked_mission || null,
      mission_candidates: JSON.parse(story.mission_candidates || '[]'),
      story_status: story.story_status,
    }, 200, origin);
  }

  return jsonResponse({
    done: false,
    question_index: nextIndex,
    question: STORY_QUESTIONS[nextIndex],
    total_questions: STORY_QUESTIONS.length,
    answers_so_far: Object.keys(answers).length,
    story_status: story.story_status,
  }, 200, origin);
}

async function handleStoryRespond(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { question_index, answer } = body;
  if (question_index === undefined || !answer?.trim()) {
    return errorResponse('question_index and answer are required', 400, origin);
  }

  const story = await ensureCreatorStory(creatorId, env);
  const answers = JSON.parse(story.answers || '{}');

  answers[question_index] = answer.trim();
  const now = Math.floor(Date.now() / 1000);

  await env.CREATOR_DB.prepare(
    'UPDATE creator_stories SET answers = ?, updated_at = ? WHERE creator_id = ?'
  ).bind(JSON.stringify(answers), now, creatorId).run();

  const nextIndex = STORY_QUESTIONS.findIndex((_, i) => !answers[i]);

  if (nextIndex === -1) {
    return jsonResponse({
      done: true,
      ready_for_missions: true,
      total_answers: Object.keys(answers).length,
    }, 200, origin);
  }

  return jsonResponse({
    done: false,
    question_index: nextIndex,
    question: STORY_QUESTIONS[nextIndex],
    total_questions: STORY_QUESTIONS.length,
    answers_so_far: Object.keys(answers).length,
  }, 200, origin);
}

async function handleStoryGenerateMissions(creatorId, env, origin) {
  const story = await env.CREATOR_DB.prepare(
    'SELECT * FROM creator_stories WHERE creator_id = ?'
  ).bind(creatorId).first();

  if (!story) return errorResponse('Story not started', 404, origin);

  const answers = JSON.parse(story.answers || '{}');
  const answeredCount = Object.keys(answers).length;

  if (answeredCount < STORY_QUESTIONS.length) {
    return errorResponse(`Only ${answeredCount}/${STORY_QUESTIONS.length} questions answered. Complete all before generating.`, 400, origin);
  }

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const answersNarrative = STORY_QUESTIONS.map((q, i) => `Q: ${q}\nA: ${answers[i] || '(no answer)'}`).join('\n\n');

  const systemPrompt = `You are a mission statement specialist. Your job is to synthesize a creator's story into 10 powerful, authentic mission one-liners.

Rules for mission one-liners:
- 10 to 22 words each
- No buzzwords, corporate jargon, or hype language
- Plain language — a fifth-grader should understand it
- At least 6 must be plain-language (no metrics)
- Up to 4 can be metric-forward (include specific outcomes)
- Must feel like the creator actually said it
- Each one-liner should be distinct — different angles, not variations of the same sentence
- Do NOT include numbering in the one-liners themselves`;

  const userPrompt = `Here are the story extraction answers from creator "${creator?.display_name}":

${answersNarrative}

Generate exactly 10 mission one-liners. Return ONLY a JSON array of 10 strings, no explanation, no numbering, no markdown:
["mission 1", "mission 2", ..., "mission 10"]`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 1024);
  } catch (err) {
    return errorResponse('Mission generation failed: ' + err.message, 502, origin);
  }

  let candidates;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    candidates = JSON.parse(cleaned);
    if (!Array.isArray(candidates)) throw new Error('Not an array');
  } catch {
    return errorResponse('Mission generation returned invalid format. Please try again.', 502, origin);
  }

  candidates = candidates.slice(0, 10).map(c => String(c).trim());

  const now = Math.floor(Date.now() / 1000);
  await env.CREATOR_DB.prepare(
    "UPDATE creator_stories SET mission_candidates = ?, story_status = 'missions_generated', updated_at = ? WHERE creator_id = ?"
  ).bind(JSON.stringify(candidates), now, creatorId).run();

  return jsonResponse({ mission_candidates: candidates }, 200, origin);
}

async function handleStoryLock(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { mission } = body;
  if (!mission?.trim()) return errorResponse('mission is required', 400, origin);

  const now = Math.floor(Date.now() / 1000);

  await env.CREATOR_DB.prepare(
    "UPDATE creator_stories SET locked_mission = ?, story_status = 'locked', updated_at = ? WHERE creator_id = ?"
  ).bind(mission.trim(), now, creatorId).run();

  const creator = await env.CREATOR_DB.prepare(
    'SELECT settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  settings.locked_mission = mission.trim();

  await env.CREATOR_DB.prepare(
    'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
  ).bind(JSON.stringify(settings), now, creatorId).run();

  return jsonResponse({ locked_mission: mission.trim(), story_status: 'locked' }, 200, origin);
}

// ============================================================
// Night 5 — Feature 2: Post Quality Scorer (GPT #7)
// POST /api/creator/content/score
// ============================================================
async function handleContentScore(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { draft, audience, goal, platform } = body;
  if (!draft?.trim()) return errorResponse('draft is required', 400, origin);

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const lockedMission = settings.locked_mission || '';

  const systemPrompt = `You are an expert LinkedIn content performance coach. You audit and score content drafts with brutal honesty and actionable precision.

Your scoring system (GPT #7 Behavioral Source of Truth):

Scoring categories (each /10):
- Hook Strength: Clear promise in first 2 lines, obvious audience, real tension or curiosity
- CTA Effectiveness: CTA matches goal + trust level, clear next step, doesn't oversell
- Platform Fit: Format, length, structure, and language match the target platform's norms
- Algorithm Signals: Short paragraphs, mobile-friendly, engagement-worthy length, no filler

Hard thresholds:
- Hook < 6: Hook must be rewritten first before anything else
- Platform Fit < 7: Rebuild structure into short paragraphs
- CTA < 6: Downgrade CTA intensity and tighten relevance

Engagement Prediction: Low (score avg < 5) | Medium (5-6.5) | High (6.5-8) | Viral (8+)

For top_fixes: Give exactly 3 specific, immediately actionable improvements in priority order.
For alternative_hooks: Give exactly 2 rewritten hook alternatives using patterns from:
  Contrarian ("Stop doing X. It's costing you Y."), Confession ("I messed up X for years."),
  Specific win ("We changed one thing and got Y."), Myth bust ("X doesn't matter. Y does."),
  Pain mirror ("If X feels hard, it's usually because Y.")

Return ONLY valid JSON, no markdown fences.`;

  const userPrompt = `Score this ${platform || 'LinkedIn'} content draft.

Creator: ${creator?.display_name || 'Unknown'}
${lockedMission ? `Their locked mission: "${lockedMission}"` : ''}
${audience ? `Target audience: ${audience}` : ''}
${goal ? `Post goal: ${goal}` : ''}

DRAFT:
${draft.trim()}

Return this exact JSON:
{
  "hook_strength": <1-10 integer>,
  "cta_effectiveness": <1-10 integer>,
  "platform_fit": <1-10 integer>,
  "algorithm_signals": <1-10 integer>,
  "overall_score": <average rounded to 1 decimal>,
  "engagement_prediction": "Low|Medium|High|Viral",
  "verdict": "<one sentence verdict>",
  "top_fixes": ["fix 1", "fix 2", "fix 3"],
  "alternative_hooks": ["hook A", "hook B"]
}`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 1024);
  } catch (err) {
    return errorResponse('Scoring failed: ' + err.message, 502, origin);
  }

  let scoreData;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    scoreData = JSON.parse(cleaned);
  } catch {
    return errorResponse('Scoring returned invalid format. Please try again.', 502, origin);
  }

  return jsonResponse(scoreData, 200, origin);
}

// ============================================================
// Night 5 — Feature 3: A/B Hook Variations
// POST /api/creator/content/hooks
// ============================================================
async function handleContentHooks(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { draft } = body;
  if (!draft?.trim()) return errorResponse('draft is required', 400, origin);

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const lockedMission = settings.locked_mission || '';
  const voiceFingerprint = settings.voice_fingerprint || null;

  const voiceContext = voiceFingerprint
    ? `Creator voice: ${voiceFingerprint.writing_personality || ''}. Style: ${voiceFingerprint.paragraph_style || ''}, ${voiceFingerprint.avg_sentence_length || ''} sentences.`
    : '';

  const systemPrompt = `You are a LinkedIn hook specialist who writes opening lines that stop the scroll.

Hook pattern library:
- Contrarian: "Stop doing X. It's costing you Y."
- Confession: "I messed up X for years."
- Specific win: "We changed one thing and got Y."
- Myth bust: "X doesn't matter. Y does."
- Pain mirror: "If X feels hard, it's usually because Y."

Rules:
- 1-2 lines only — these are opening hooks, not full posts
- Each hook must use a DIFFERENT pattern from the library above
- Plain language, no corporate speak
- Create immediate tension or curiosity
- Match the creator's authentic voice — must sound like them

Return ONLY a JSON array of exactly 3 strings, no markdown, no explanation.`;

  const userPrompt = `Write 3 alternative hook openings for this content.

Creator: ${creator?.display_name || 'Unknown'}
${lockedMission ? `Their mission: "${lockedMission}"` : ''}
${voiceContext}

DRAFT (for context — pick a different hook than what's already there):
${draft.trim()}

Return: ["hook 1", "hook 2", "hook 3"]
Each hook = 1-2 short lines max. Use a different pattern for each.`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 512);
  } catch (err) {
    return errorResponse('Hook generation failed: ' + err.message, 502, origin);
  }

  let hooks;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    hooks = JSON.parse(cleaned);
    if (!Array.isArray(hooks)) throw new Error('Not an array');
  } catch {
    return errorResponse('Hook generation returned invalid format. Please try again.', 502, origin);
  }

  hooks = hooks.slice(0, 3).map(h => String(h).trim());

  return jsonResponse({ hooks }, 200, origin);
}


// ============================================================

// ============================================================
// Night 6 — Feature 1: LinkedIn Profile Optimizer (GPT #5)
// POST /api/creator/profile-optimizer/scan
// POST /api/creator/profile-optimizer/optimize
// GET  /api/creator/profile-optimizer/status
// ============================================================

async function handleProfileOptimizerScan(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { profile_text, profile_url } = body;
  if (!profile_text && !profile_url) {
    return errorResponse('profile_text or profile_url is required', 400, origin);
  }

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const lockedMission = settings.locked_mission || '';

  const inputText = profile_text || `LinkedIn profile URL: ${profile_url} (creator to paste text manually)`;

  const systemPrompt = `You are LinkedIn Profile Optimizer. Your role is to perform a silent, internal scan of a LinkedIn profile and return a structured assessment. You are not about visibility or vanity — you are about resonance, credibility, and conversion.

Perform the Profile Scan Doctrine internally:
1. Cogency — Primary Narrative Integrity: Is there one dominant, reinforced theme?
2. Clarity — Comprehension Test: Can a first-time reader quickly understand "what does this person do?" and "who is it for?"
3. Consistency — Cross-Section Alignment: Check alignment across Headline, About, Featured, Experience
4. Authority vs Accessibility: Where does the profile sit on the spectrum?
5. Role-Type Tuning: Founder / Consultant / Operator — which does the evidence suggest?
6. Intent Routing: Job-seeker, client-seeker, or audience-builder?
7. CTA Directionality: Is there a clear CTA, and is it reinforced?
8. Overall narrative coherence score

Return ONLY valid JSON, no markdown fences.`;

  const userPrompt = `Scan this LinkedIn profile.

Creator name: ${creator?.display_name || 'Unknown'}
${lockedMission ? `Their locked mission statement: "${lockedMission}"` : ''}

PROFILE TEXT:
${inputText.substring(0, 6000)}

Return this exact JSON structure:
{
  "narrative_coherence": <1-10>,
  "clarity_score": <1-10>,
  "cta_presence": true|false,
  "dominant_theme": "<one sentence>",
  "role_type": "founder|consultant|operator|unclear",
  "intent": "job-seeker|client-seeker|audience-builder|unclear",
  "identity_conflict_detected": true|false,
  "identity_conflict_question": "<one question to resolve if conflict, else null>",
  "sections_assessed": {
    "headline": { "score": <1-10>, "issue": "<brief>", "priority": "high|medium|low" },
    "about": { "score": <1-10>, "issue": "<brief>", "priority": "high|medium|low" },
    "featured": { "score": <1-10>, "issue": "<brief>", "priority": "high|medium|low" },
    "experience": { "score": <1-10>, "issue": "<brief>", "priority": "high|medium|low" },
    "banner": { "score": <1-10>, "issue": "<brief>", "priority": "high|medium|low" }
  },
  "optimization_order": ["headline","banner","about","featured","experience"],
  "overall_verdict": "<2-3 sentence assessment of the profile as a system>"
}`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 1500);
  } catch (err) {
    return errorResponse('Profile scan failed: ' + err.message, 502, origin);
  }

  let scanData;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    scanData = JSON.parse(cleaned);
  } catch {
    return errorResponse('Profile scan returned invalid format. Please try again.', 502, origin);
  }

  // Store scan result in creator settings
  const now = Math.floor(Date.now() / 1000);
  const current = await env.CREATOR_DB.prepare('SELECT settings FROM creators WHERE id = ?').bind(creatorId).first();
  const currentSettings = JSON.parse(current?.settings || '{}');
  const merged = {
    ...currentSettings,
    profile_scan: scanData,
    profile_scan_at: now,
    profile_optimizer_completed: currentSettings.profile_optimizer_completed || [],
  };
  await env.CREATOR_DB.prepare(
    'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
  ).bind(JSON.stringify(merged), now, creatorId).run();

  return jsonResponse({ ok: true, scan: scanData }, 200, origin);
}

async function handleProfileOptimizerOptimize(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { section, current_content, context } = body;

  const validSections = ['headline', 'about', 'experience', 'featured', 'banner'];
  if (!section || !validSections.includes(section)) {
    return errorResponse(`section must be one of: ${validSections.join(', ')}`, 400, origin);
  }

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const lockedMission = settings.locked_mission || '';
  const profileScan = settings.profile_scan || null;
  const completed = settings.profile_optimizer_completed || [];

  // Enforce locked order — cannot skip sections
  const sectionOrder = ['headline', 'banner', 'about', 'featured', 'experience'];
  const sectionIndex = sectionOrder.indexOf(section);
  for (let i = 0; i < sectionIndex; i++) {
    if (!completed.includes(sectionOrder[i])) {
      return errorResponse(`Must complete "${sectionOrder[i]}" before optimizing "${section}"`, 400, origin);
    }
  }

  const sectionGuides = {
    headline: `HEADLINE RULES:
- Outcome beats title. Proof beats adjectives. Who they help must be obvious.
- Must earn the "...more" click. Avoid vague leadership language.
- Present ONE primary headline. ONE alternate only if there is a meaningful clarity tradeoff.
- Format: [Who you help] + [specific result/outcome] or [Proof element] + [Who you serve]`,

    banner: `BANNER + FIRST LINK RULES:
- Treat banner as a digital billboard — value at a glance.
- First link functions as a "Start Here" action.
- Give ONE clear recommendation: banner concept/text + link CTA.
- Output: banner copy concept (headline + sub-line) + first link text.`,

    about: `ABOUT SECTION RULES:
- Not a résumé. Lead with challenges solved and lived experience.
- Allow humanity, struggle, and credibility. End with clear promise.
- Clean paragraphs; avoid hype and corporate tone.
- First line must mirror the creator's locked mission one-liner exactly.
- Output: full About section copy, ready to paste.`,

    featured: `FEATURED SECTION RULES:
- Highlight reel and trust builder.
- Each item must prove value or convert attention.
- Avoid clutter. Give exactly 3 featured item recommendations (title + why).`,

    experience: `EXPERIENCE SECTION RULES:
- Write like a landing page, not a résumé. Outcomes, credibility, proof.
- Each role answers: "Why should I trust you?"
- CTAs allowed. Focus on the top 1-2 most relevant roles.
- Output: optimized copy for the most recent/relevant role.`,
  };

  const systemPrompt = `You are LinkedIn Profile Optimizer from https://puremarketing.ai. Your role is to optimize one section of a LinkedIn profile at a time, using the creator's locked mission statement as the foundation.

Rules (non-negotiable):
- Never use meta/process words: step, framework, system, phase, mode, funnel, blueprint
- No emojis
- Never refer to people as "users"
- Never fabricate personal experience or metrics
- If writing could apply to anyone, rewrite until it could only apply to this person
- Tone: Calm, direct, credible. Human, not instructional. Confident without hype.
- Output is copy-paste ready LinkedIn content

${sectionGuides[section]}`;

  const userPrompt = `Optimize the ${section} section for this creator.

Creator: ${creator?.display_name || 'Unknown'}
${lockedMission ? `Locked mission one-liner: "${lockedMission}"` : ''}
${profileScan ? `Profile scan — dominant theme: "${profileScan.dominant_theme || ''}", role type: "${profileScan.role_type || ''}", intent: "${profileScan.intent || ''}"` : ''}
${context ? `Additional context: ${context}` : ''}

CURRENT ${section.toUpperCase()} CONTENT:
${(current_content || '').substring(0, 3000) || '(not provided — generate from mission and scan data)'}

Return a JSON object:
{
  "section": "${section}",
  "optimized": "<the full optimized copy, ready to paste>",
  "alternate": "<one alternate version if meaningful tradeoff exists, else null>",
  "rationale": "<2-3 sentence explanation of key changes made>",
  "lock_prompt": "Approve this ${section}? Reply 'approved' to lock it and move to the next section."
}

Return ONLY valid JSON, no markdown fences.`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 2000);
  } catch (err) {
    return errorResponse('Profile optimization failed: ' + err.message, 502, origin);
  }

  let optimizedData;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    optimizedData = JSON.parse(cleaned);
  } catch {
    return errorResponse('Optimization returned invalid format. Please try again.', 502, origin);
  }

  // If the body includes approved: true, lock this section
  if (body.approved === true) {
    const now = Math.floor(Date.now() / 1000);
    const current = await env.CREATOR_DB.prepare('SELECT settings FROM creators WHERE id = ?').bind(creatorId).first();
    const currentSettings = JSON.parse(current?.settings || '{}');
    const completedSections = currentSettings.profile_optimizer_completed || [];
    if (!completedSections.includes(section)) {
      completedSections.push(section);
    }
    const merged = {
      ...currentSettings,
      profile_optimizer_completed: completedSections,
      [`profile_optimized_${section}`]: optimizedData.optimized,
    };
    await env.CREATOR_DB.prepare(
      'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
    ).bind(JSON.stringify(merged), now, creatorId).run();
    optimizedData.locked = true;
  }

  return jsonResponse({ ok: true, ...optimizedData }, 200, origin);
}

async function handleProfileOptimizerStatus(creatorId, env, origin) {
  const creator = await env.CREATOR_DB.prepare(
    'SELECT settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const completed = settings.profile_optimizer_completed || [];
  const sectionOrder = ['headline', 'banner', 'about', 'featured', 'experience'];

  const sections = {};
  for (const s of sectionOrder) {
    sections[s] = {
      done: completed.includes(s),
      optimized_content: settings[`profile_optimized_${s}`] || null,
    };
  }

  const nextSection = sectionOrder.find(s => !completed.includes(s)) || null;
  const allDone = completed.length >= sectionOrder.length;
  const hasScan = !!settings.profile_scan;

  return jsonResponse({
    ok: true,
    has_scan: hasScan,
    scan_summary: hasScan ? {
      narrative_coherence: settings.profile_scan.narrative_coherence,
      dominant_theme: settings.profile_scan.dominant_theme,
      overall_verdict: settings.profile_scan.overall_verdict,
    } : null,
    sections,
    next_section: nextSection,
    all_done: allDone,
    completed_count: completed.length,
    total_sections: sectionOrder.length,
  }, 200, origin);
}

// ============================================================
// Night 6 — Feature 2: Full Content Audit Scorecard (GPT #7)
// POST /api/creator/content/audit
// ============================================================

async function handleContentAudit(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { draft, audience, goal, platform, offer } = body;
  if (!draft?.trim()) return errorResponse('draft is required', 400, origin);

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const lockedMission = settings.locked_mission || '';
  const voiceFingerprint = settings.voice_fingerprint || null;

  const platformName = platform || 'LinkedIn';

  const systemPrompt = `You are LI Social Content Performance Coach from PureMarketing.ai.
Mission: audit and improve LinkedIn content for reach and conversion. Blunt in the audit, friendly in intake. No corporate fluff. No cringe engagement bait. American spelling. No em dash.

BEHAVIORAL SOURCE OF TRUTH — deliver in this exact order every time:
1. Verdict (one line): "This will underperform because…"
2. Snapshot diagnosis (3-6 bullets): what's broken and why
3. Scorecard /10 with brutal justification — 6 categories: Hook Strength, Skimmability, Novelty+Insight, Proof+Credibility, Engagement Quality, Conversion Fit
4. Outlier Checklist (Pass/Fail — 10 criteria)
5. Fix list: top 7 changes in priority order
6. Rewrite A (primary, best-performing)
7. Rewrite B (different angle: more contrarian OR more story)
8. Hooks: 5 options (varied patterns)
9. CTA options: 3 levels (light/medium/strong)
10. Distribution plan: exact 24-hour behaviors
11. One next action today

SCORECARD CATEGORIES:
- Hook Strength /10: Clear promise in first 2 lines, obvious audience, real tension or curiosity
- Skimmability /10: Short lines, spacing, no walls of text, mobile-friendly
- Novelty+Insight /10: Not obvious advice, has a stance or trade-off, avoids LinkedIn beige
- Proof+Credibility /10: Examples, numbers, receipts, specific experience (no vague "I believe")
- Engagement Quality /10: Prompts meaningful replies, not just "thoughts?"
- Conversion Fit /10: CTA matches goal + trust level, clear next step

HARD THRESHOLDS:
- Hook < 6: rewrite hook FIRST before anything else
- Skimmability < 7: rebuild structure into short paragraphs and bullets
- Proof < 6: add at least one concrete example, mini case, or specific detail
- Conversion Fit < 6: downgrade CTA intensity and tighten relevance

OUTLIER CHECKLIST (Pass/Fail — needs 7/10 to qualify):
1. Audience is explicit
2. One clear point (has a spine)
3. Hook creates tension or curiosity
4. Skimmable structure (mobile-first)
5. Includes at least one specific example/proof point
6. Has a stance (not neutral)
7. Close lands with a strong line (not generic question)
8. CTA matches the trust level
9. No filler intro
10. No jargon or corporate fluff

ALGORITHM CONTEXT (2025-2026):
- Long posts (1250-3000 chars) perform ~31% better if they read clean
- Posts with fewer than 7 paragraphs perform ~71% worse than posts with 14+ paragraphs
- Simpler language wins: target grade 5-7 reading level
- Portrait images perform ~86% better than landscape
- Questions at the end are weaker unless scenario-based, either/or debates, or provocative statements

REWRITE RULES:
- Lead with tension: problem, mistake, surprising truth, or specific result
- Keep paragraphs short (1-2 sentences max)
- Use concrete nouns and verbs; delete abstract language
- Show one example before giving advice
- Prefer "do X because Y" over "X is important"
- Close with a stance + specific prompt

CTA LADDER:
- Light: "If you're dealing with X, steal this framework."
- Medium: "Comment 'X' and I'll send the template/checklist."
- Strong: "If you want me to review yours, DM me 'audit'."
Strong CTA only if the post includes proof and earns trust.

Return ONLY valid JSON, no markdown fences.`;

  const userPrompt = `Audit this ${platformName} content draft.

Creator: ${creator?.display_name || 'Unknown'}
${lockedMission ? `Locked mission: "${lockedMission}"` : ''}
${audience ? `Target audience: ${audience}` : 'Assume: peers + authority/inbound + light CTA'}
${goal ? `Post goal: ${goal}` : ''}
${offer ? `Offer/CTA context: ${offer}` : ''}
${voiceFingerprint ? `Creator voice — personality: ${voiceFingerprint.writing_personality || 'unknown'}, avg sentence: ${voiceFingerprint.avg_sentence_length || 'unknown'}` : ''}

DRAFT:
${draft.trim().substring(0, 3000)}

Return this exact JSON structure:
{
  "verdict": "<one line — This will underperform because...>",
  "snapshot_diagnosis": ["<bullet 1>", "<bullet 2>", "<bullet 3>"],
  "scorecard": {
    "hook_strength": { "score": <1-10>, "justification": "<brief>" },
    "skimmability": { "score": <1-10>, "justification": "<brief>" },
    "novelty_insight": { "score": <1-10>, "justification": "<brief>" },
    "proof_credibility": { "score": <1-10>, "justification": "<brief>" },
    "engagement_quality": { "score": <1-10>, "justification": "<brief>" },
    "conversion_fit": { "score": <1-10>, "justification": "<brief>" },
    "overall": <average to 1 decimal>
  },
  "outlier_checklist": [
    { "item": "Audience is explicit", "pass": true|false },
    { "item": "One clear point (has a spine)", "pass": true|false },
    { "item": "Hook creates tension or curiosity", "pass": true|false },
    { "item": "Skimmable structure (mobile-first)", "pass": true|false },
    { "item": "Includes at least one specific example/proof point", "pass": true|false },
    { "item": "Has a stance (not neutral)", "pass": true|false },
    { "item": "Close lands with a strong line (not generic question)", "pass": true|false },
    { "item": "CTA matches the trust level", "pass": true|false },
    { "item": "No filler intro", "pass": true|false },
    { "item": "No jargon or corporate fluff", "pass": true|false }
  ],
  "outlier_score": <count of passes out of 10>,
  "fix_list": [
    { "priority": 1, "fix": "<specific actionable fix>" },
    { "priority": 2, "fix": "<specific actionable fix>" },
    { "priority": 3, "fix": "<specific actionable fix>" },
    { "priority": 4, "fix": "<specific actionable fix>" },
    { "priority": 5, "fix": "<specific actionable fix>" },
    { "priority": 6, "fix": "<specific actionable fix>" },
    { "priority": 7, "fix": "<specific actionable fix>" }
  ],
  "rewrite_a": "<full rewrite — primary best-performing version>",
  "rewrite_b": "<full rewrite — different angle: contrarian OR story>",
  "hooks": [
    "<hook option 1>",
    "<hook option 2>",
    "<hook option 3>",
    "<hook option 4>",
    "<hook option 5>"
  ],
  "cta_options": {
    "light": "<light CTA>",
    "medium": "<medium CTA>",
    "strong": "<strong CTA>"
  },
  "distribution_plan": {
    "first_60_min": "<exact behavior>",
    "2_hours_later": "<exact behavior>",
    "same_day": "<exact behavior>",
    "next_morning": "<exact behavior>"
  },
  "next_action": "<one specific next action today>",
  "threshold_warnings": []
}`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 4000);
  } catch (err) {
    return errorResponse('Content audit failed: ' + err.message, 502, origin);
  }

  let auditData;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    auditData = JSON.parse(cleaned);
  } catch {
    return errorResponse('Content audit returned invalid format. Please try again.', 502, origin);
  }

  // Generate threshold warnings
  const warnings = [];
  const sc = auditData.scorecard || {};
  if ((sc.hook_strength?.score || 10) < 6) warnings.push('Hook < 6: Rewrite hook first before anything else');
  if ((sc.skimmability?.score || 10) < 7) warnings.push('Skimmability < 7: Rebuild structure into short paragraphs and bullets');
  if ((sc.proof_credibility?.score || 10) < 6) warnings.push('Proof < 6: Add at least one concrete example, mini case, or specific detail');
  if ((sc.conversion_fit?.score || 10) < 6) warnings.push('Conversion Fit < 6: Downgrade CTA intensity and tighten relevance');
  auditData.threshold_warnings = warnings;

  return jsonResponse({ ok: true, ...auditData }, 200, origin);
}

// ============================================================
// Night 6 — Feature 3: Fan Monetization Tiers
// GET  /api/fan/paywall-status — enhanced with subscription lookup
// POST /api/fan/subscribe      — upgrade fan tier
// PUT  /api/creator/monetization — creator sets pricing
// ============================================================

async function handleFanSubscribe(request, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return publicErrorResponse('Invalid JSON', 400, origin); }

  const { fan_id, creator_id, tier, email } = body;
  if (!fan_id) return publicErrorResponse('fan_id is required', 400, origin);
  if (!creator_id) return publicErrorResponse('creator_id is required', 400, origin);
  if (!tier || !['basic', 'premium'].includes(tier)) {
    return publicErrorResponse('tier must be basic or premium', 400, origin);
  }

  const creator = await env.CREATOR_DB.prepare(
    'SELECT id, settings FROM creators WHERE id = ?'
  ).bind(creator_id).first();
  if (!creator) return publicErrorResponse('Creator not found', 404, origin);

  const settings = JSON.parse(creator.settings || '{}');
  const monetization = settings.monetization || {};

  const tierPrices = {
    basic: { cents: monetization.basic_price_cents || 500, messages: monetization.basic_messages || 50 },
    premium: { cents: monetization.premium_price_cents || 1500, messages: -1 }, // -1 = unlimited
  };

  const now = Math.floor(Date.now() / 1000);
  const thirtyDays = now + (30 * 24 * 60 * 60);

  // Check for existing subscription
  const existing = await env.CREATOR_DB.prepare(
    'SELECT id FROM fan_subscriptions WHERE fan_id = ? AND creator_id = ?'
  ).bind(fan_id, creator_id).first();

  const subId = crypto.randomUUID().replace(/-/g, '');
  const priceInfo = tierPrices[tier];
  const messagesPerMonth = priceInfo.messages;
  const messagesRemaining = messagesPerMonth === -1 ? 99999 : messagesPerMonth;

  if (existing) {
    await env.CREATOR_DB.prepare(`
      UPDATE fan_subscriptions
      SET tier = ?, price_cents = ?, messages_remaining = ?, messages_per_month = ?,
          started_at = ?, expires_at = ?
      WHERE fan_id = ? AND creator_id = ?
    `).bind(tier, priceInfo.cents, messagesRemaining, messagesPerMonth, now, thirtyDays, fan_id, creator_id).run();
  } else {
    await env.CREATOR_DB.prepare(`
      INSERT INTO fan_subscriptions
        (id, fan_id, creator_id, tier, price_cents, messages_remaining, messages_per_month, started_at, expires_at, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(subId, fan_id, creator_id, tier, priceInfo.cents, messagesRemaining, messagesPerMonth, now, thirtyDays, now).run();
  }

  // Update fan email if provided
  if (email) {
    await env.CREATOR_DB.prepare(
      'UPDATE fans SET email = ?, updated_at = ? WHERE id = ?'
    ).bind(email.toLowerCase(), now, fan_id).run();
  }

  return publicJsonResponse({
    ok: true,
    tier,
    messages_remaining: messagesRemaining,
    expires_at: thirtyDays,
    // Stripe integration placeholder — implement when stripe_publishable_key is configured
    stripe_enabled: false,
    message: `Subscribed to ${tier} tier. Stripe payment integration coming soon.`,
  }, 200, origin);
}

async function handleCreatorMonetization(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const {
    paywall_enabled,
    paywall_free_limit,
    paywall_message,
    basic_price_cents,
    basic_messages,
    premium_price_cents,
    creator_revenue_share,
  } = body;

  const now = Math.floor(Date.now() / 1000);
  const current = await env.CREATOR_DB.prepare('SELECT settings FROM creators WHERE id = ?').bind(creatorId).first();
  const currentSettings = JSON.parse(current?.settings || '{}');

  const monetization = {
    ...(currentSettings.monetization || {}),
    ...(basic_price_cents !== undefined ? { basic_price_cents } : {}),
    ...(basic_messages !== undefined ? { basic_messages } : {}),
    ...(premium_price_cents !== undefined ? { premium_price_cents } : {}),
    ...(creator_revenue_share !== undefined ? { creator_revenue_share } : {}),
  };

  const merged = {
    ...currentSettings,
    monetization,
    ...(paywall_enabled !== undefined ? { paywall_enabled } : {}),
    ...(paywall_free_limit !== undefined ? { paywall_free_limit } : {}),
    ...(paywall_message !== undefined ? { paywall_message } : {}),
  };

  await env.CREATOR_DB.prepare(
    'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
  ).bind(JSON.stringify(merged), now, creatorId).run();

  return jsonResponse({
    ok: true,
    paywall_enabled: merged.paywall_enabled || false,
    paywall_free_limit: merged.paywall_free_limit || 5,
    monetization: merged.monetization,
    tiers: {
      free: { messages: merged.paywall_free_limit || 5, price_cents: 0 },
      basic: { messages: merged.monetization?.basic_messages || 50, price_cents: merged.monetization?.basic_price_cents || 500 },
      premium: { messages: 'unlimited', price_cents: merged.monetization?.premium_price_cents || 1500 },
    },
    creator_revenue_share: merged.monetization?.creator_revenue_share || 70,
  }, 200, origin);
}

// ============================================================
// Night 6 — Feature 4: Voice Clone (ElevenLabs)
// POST /api/creator/voice/clone
// ============================================================

async function handleVoiceClone(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { voice_name, description, sample_urls } = body;

  if (!voice_name?.trim()) return errorResponse('voice_name is required', 400, origin);

  if (!env.ELEVENLABS_API_KEY) {
    return errorResponse('ElevenLabs API key not configured', 503, origin);
  }

  // ElevenLabs Voice Clone API — expects audio files
  // If sample_urls provided, attempt to clone; else return setup instructions
  if (!sample_urls || sample_urls.length === 0) {
    return jsonResponse({
      ok: false,
      needs_samples: true,
      message: 'To clone a voice, provide at least 1 audio sample URL (WAV or MP3, minimum 1 minute clean audio). Send sample_urls array.',
      instructions: [
        'Record 1-3 minutes of clear speech with no background noise',
        'Upload the audio file and get a public URL',
        'Call this endpoint again with { voice_name, sample_urls: ["url1"] }',
      ],
    }, 200, origin);
  }

  // Fetch samples and build FormData for ElevenLabs
  try {
    const formData = new FormData();
    formData.append('name', voice_name.trim());
    if (description) formData.append('description', description);
    formData.append('labels', JSON.stringify({ creator_id: creatorId }));

    // Fetch each sample and attach
    for (let i = 0; i < Math.min(sample_urls.length, 5); i++) {
      const sampleRes = await fetch(sample_urls[i]);
      if (!sampleRes.ok) continue;
      const blob = await sampleRes.blob();
      const filename = `sample_${i + 1}.mp3`;
      formData.append('files', blob, filename);
    }

    const cloneRes = await fetch('https://api.elevenlabs.io/v1/voices/add', {
      method: 'POST',
      headers: { 'xi-api-key': env.ELEVENLABS_API_KEY.trim() },
      body: formData,
    });

    if (!cloneRes.ok) {
      const errText = await cloneRes.text();
      return errorResponse('ElevenLabs voice clone failed: ' + errText, 502, origin);
    }

    const cloneData = await cloneRes.json();
    const voiceId = cloneData.voice_id;

    // Store voice_id in creator settings
    const now = Math.floor(Date.now() / 1000);
    const current = await env.CREATOR_DB.prepare('SELECT settings FROM creators WHERE id = ?').bind(creatorId).first();
    const currentSettings = JSON.parse(current?.settings || '{}');
    const merged = {
      ...currentSettings,
      elevenlabs_voice_id: voiceId,
      elevenlabs_voice_name: voice_name.trim(),
      voice_cloned_at: now,
    };
    await env.CREATOR_DB.prepare(
      'UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?'
    ).bind(JSON.stringify(merged), now, creatorId).run();

    return jsonResponse({
      ok: true,
      voice_id: voiceId,
      voice_name: voice_name.trim(),
      message: 'Voice clone created successfully. Fan chat will now use your cloned voice.',
    }, 200, origin);

  } catch (err) {
    return errorResponse('Voice clone failed: ' + err.message, 502, origin);
  }
}

// ============================================================
// Night 6 — Feature 5: Welcome Email Sequences
// GET  /api/creator/email-sequences
// PUT  /api/creator/email-sequences/:id
// POST /api/creator/email-sequences/generate
// Internal: enqueueWelcomeSequence(fanId, creatorId, env)
// ============================================================

async function handleListEmailSequences(creatorId, env, origin) {
  const result = await env.CREATOR_DB.prepare(
    'SELECT * FROM email_sequences WHERE creator_id = ? ORDER BY created_at DESC'
  ).bind(creatorId).all();

  const sequences = (result.results || []).map(s => ({
    ...s,
    emails: JSON.parse(s.emails || '[]'),
  }));

  return jsonResponse({ ok: true, sequences }, 200, origin);
}

async function handleUpdateEmailSequence(seqId, request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { emails, sequence_name, is_active } = body;
  const now = Math.floor(Date.now() / 1000);

  // Verify ownership
  const seq = await env.CREATOR_DB.prepare(
    'SELECT id FROM email_sequences WHERE id = ? AND creator_id = ?'
  ).bind(seqId, creatorId).first();
  if (!seq) return errorResponse('Sequence not found', 404, origin);

  const updates = [];
  const values = [];

  if (emails !== undefined) {
    updates.push('emails = ?');
    values.push(JSON.stringify(emails));
  }
  if (sequence_name !== undefined) {
    updates.push('sequence_name = ?');
    values.push(sequence_name);
  }
  if (is_active !== undefined) {
    updates.push('is_active = ?');
    values.push(is_active ? 1 : 0);
  }

  if (updates.length > 0) {
    values.push(now, seqId, creatorId);
    await env.CREATOR_DB.prepare(
      `UPDATE email_sequences SET ${updates.join(', ')}, updated_at = ? WHERE id = ? AND creator_id = ?`
    ).bind(...values).run();
  }

  const updated = await env.CREATOR_DB.prepare(
    'SELECT * FROM email_sequences WHERE id = ?'
  ).bind(seqId).first();

  return jsonResponse({
    ok: true,
    sequence: { ...updated, emails: JSON.parse(updated.emails || '[]') },
  }, 200, origin);
}

async function handleGenerateEmailSequence(request, creatorId, env, origin) {
  let body;
  try { body = await request.json(); }
  catch { return errorResponse('Invalid JSON', 400, origin); }

  const { sequence_name = 'welcome', save_to_db = true } = body;

  const creator = await env.CREATOR_DB.prepare(
    'SELECT display_name, settings FROM creators WHERE id = ?'
  ).bind(creatorId).first();

  const settings = JSON.parse(creator?.settings || '{}');
  const lockedMission = settings.locked_mission || '';
  const voiceFingerprint = settings.voice_fingerprint || null;
  const displayName = creator?.display_name || 'the creator';

  if (!lockedMission) {
    return errorResponse('Complete the Story Extraction (lock a mission statement) before generating an email sequence.', 400, origin);
  }

  const systemPrompt = `You are an expert email copywriter. Your task is to generate a 5-email welcome sequence for a creator's new fans/subscribers. The emails must be written in the creator's authentic voice — personal, direct, non-corporate.

Voice requirements:
- Match the creator's voice fingerprint if provided
- Short paragraphs (1-3 sentences)
- Conversational, not formal
- Each email has ONE clear purpose
- No corporate-speak, no fluff
- Subject lines that get opened — specific, curious, or direct benefit

Email sequence structure (14-day drip):
- Email 1 (Day 0 — send immediately): Welcome + who you are + what they can expect
- Email 2 (Day 2): Your origin story — why you do what you do
- Email 3 (Day 5): Your best piece of advice / biggest insight you wish you knew earlier  
- Email 4 (Day 9): A mistake you made and what you learned
- Email 5 (Day 14): Where to go from here + clear CTA

Return ONLY valid JSON, no markdown fences.`;

  const days = [0, 2, 5, 9, 14];
  const purposes = [
    'Welcome + who you are + what they can expect',
    'Your origin story — why you do what you do',
    'Your best insight or advice you wish you knew earlier',
    'A mistake you made and what you learned from it',
    'Where to go from here + clear CTA to your offer or community',
  ];

  const userPrompt = `Generate a 5-email welcome sequence for this creator.

Creator name: ${displayName}
Mission: "${lockedMission}"
${voiceFingerprint ? `Voice personality: ${voiceFingerprint.writing_personality || 'conversational'}
Avg sentence length: ${voiceFingerprint.avg_sentence_length || 'medium'}
Emoji usage: ${voiceFingerprint.emoji_usage || 'minimal'}` : ''}

Email sequence plan:
${days.map((d, i) => `Email ${i + 1} (Day ${d}): ${purposes[i]}`).join('\n')}

Return this exact JSON:
{
  "sequence_name": "${sequence_name}",
  "emails": [
    ${days.map((d, i) => `{
      "position": ${i + 1},
      "day_offset": ${d},
      "subject": "<subject line for email ${i + 1}>",
      "preview_text": "<preview text for email ${i + 1}>",
      "body_html": "<full email body as HTML, use <p> tags, keep it personal and conversational>",
      "purpose": "${purposes[i]}"
    }`).join(',\n    ')}
  ]
}`;

  let rawText;
  try {
    rawText = await callClaude(env, systemPrompt, userPrompt, 4000);
  } catch (err) {
    return errorResponse('Email sequence generation failed: ' + err.message, 502, origin);
  }

  let seqData;
  try {
    const cleaned = rawText.replace(/^```json?\n?/i, '').replace(/\n?```$/i, '').trim();
    seqData = JSON.parse(cleaned);
  } catch {
    return errorResponse('Email sequence generation returned invalid format. Please try again.', 502, origin);
  }

  // Save to DB if requested
  if (save_to_db) {
    const now = Math.floor(Date.now() / 1000);
    // Check if a welcome sequence already exists
    const existing = await env.CREATOR_DB.prepare(
      'SELECT id FROM email_sequences WHERE creator_id = ? AND sequence_name = ?'
    ).bind(creatorId, sequence_name).first();

    if (existing) {
      await env.CREATOR_DB.prepare(
        'UPDATE email_sequences SET emails = ?, is_active = 1, updated_at = ? WHERE id = ?'
      ).bind(JSON.stringify(seqData.emails || []), now, existing.id).run();
      seqData.sequence_id = existing.id;
    } else {
      const newId = crypto.randomUUID().replace(/-/g, '');
      await env.CREATOR_DB.prepare(`
        INSERT INTO email_sequences (id, creator_id, sequence_name, emails, is_active, created_at)
        VALUES (?, ?, ?, ?, 1, ?)
      `).bind(newId, creatorId, sequence_name, JSON.stringify(seqData.emails || []), now).run();
      seqData.sequence_id = newId;
    }
  }

  return jsonResponse({ ok: true, ...seqData }, 200, origin);
}

// Called internally when a new fan provides their email (from handleFanLead)
// Enqueues the welcome email sequence for that fan
async function enqueueWelcomeSequence(fanId, creatorId, fanEmail, fanFirstName, env) {
  try {
    // Get the active welcome sequence for this creator
    const seq = await env.CREATOR_DB.prepare(
      "SELECT * FROM email_sequences WHERE creator_id = ? AND sequence_name = 'welcome' AND is_active = 1"
    ).bind(creatorId).first();

    if (!seq) return; // No welcome sequence configured yet

    const emails = JSON.parse(seq.emails || '[]');
    if (!emails.length) return;

    const now = Math.floor(Date.now() / 1000);
    const creator = await env.CREATOR_DB.prepare(
      'SELECT display_name, settings FROM creators WHERE id = ?'
    ).bind(creatorId).first();
    const displayName = creator?.display_name || 'Your AI';

    for (const email of emails) {
      const sendAt = now + (email.day_offset || 0) * 24 * 60 * 60;

      // Personalize body
      let bodyHtml = (email.body_html || '').replace(/\{first_name\}/gi, fanFirstName || 'there');
      bodyHtml = bodyHtml.replace(/\{creator_name\}/gi, displayName);

      const queueId = crypto.randomUUID().replace(/-/g, '');
      await env.CREATOR_DB.prepare(`
        INSERT INTO email_queue
          (id, creator_id, fan_id, to_email, subject, body_html, send_at, sent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
      `).bind(queueId, creatorId, fanId, fanEmail, email.subject || 'Hello', bodyHtml, sendAt, now).run();
    }
  } catch (err) {
    // Non-fatal — log but don't break fan lead capture
    console.error('enqueueWelcomeSequence error:', err.message);
  }
}

// GET /api/creator/email-queue — view pending emails
async function handleListEmailQueue(creatorId, env, origin) {
  const result = await env.CREATOR_DB.prepare(
    'SELECT * FROM email_queue WHERE creator_id = ? ORDER BY send_at ASC LIMIT 100'
  ).bind(creatorId).all();

  const queue = (result.results || []).map(item => ({
    ...item,
    send_at_human: new Date(item.send_at * 1000).toISOString(),
  }));

  return jsonResponse({ ok: true, queue, total: queue.length }, 200, origin);
}

// Main fetch handler — router
// ============================================================
export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin') || '';
    const url = new URL(request.url);
    const pathname = url.pathname;
    const method = request.method;

    // OPTIONS preflight
    if (method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin),
      });
    }

    try {
      // ── Fan public routes — /:handle/chat page serving ───────
      // Serve chat.html when someone visits /<handle>/chat
      // The handle is extracted client-side from window.location.pathname
      const chatPageMatch = pathname.match(/^\/([a-z0-9_]{3,32})\/chat\/?$/i);
      if (method === 'GET' && chatPageMatch) {
        // Serve chat.html static file (co-located in the creator/ directory)
        const chatAsset = await env.ASSETS?.fetch(new Request(new URL('/chat.html', request.url)));
        if (chatAsset && chatAsset.ok) return chatAsset;
        // Fallback: redirect to the same page (CF Pages should serve the asset)
        return new Response('Chat page not found', { status: 404 });
      }

      // ── Fan public API routes (no auth) ─────────────────────
      // GET /api/fan/creator/:handle
      const fanCreatorMatch = pathname.match(/^\/api\/fan\/creator\/([a-z0-9_]{3,32})$/i);
      if (method === 'GET' && fanCreatorMatch) {
        return await handleFanCreatorProfile(fanCreatorMatch[1], env, origin);
      }

      // POST /api/fan/chat
      if (method === 'POST' && pathname === '/api/fan/chat') {
        return await handleFanChat(request, env, origin);
      }

      // POST /api/fan/lead
      if (method === 'POST' && pathname === '/api/fan/lead') {
        return await handleFanLead(request, env, origin);
      }

      // POST /api/fan/subscribe — Night 6: Fan monetization tier upgrade
      if (method === 'POST' && pathname === '/api/fan/subscribe') {
        return await handleFanSubscribe(request, env, origin);
      }

      // GET /api/fan/tts/:msgId — on-demand voice for AI messages
      const ttsMsgMatch = pathname.match(/^\/api\/fan\/tts\/([a-zA-Z0-9]+)$/);
      if (method === 'GET' && ttsMsgMatch) {
        return await handleFanTTS(ttsMsgMatch[1], env, origin);
      }

      // GET /api/fan/paywall-status
      if (method === 'GET' && pathname === '/api/fan/paywall-status') {
        return await handleFanPaywallStatus(request, env, origin);
      }

      // ── Creator public routes (no auth) ──────────────────────
      if (method === 'GET' && pathname === '/api/creator/handle-check') {
        return await handleCheckHandle(request, env, origin);
      }

      if (method === 'POST' && pathname === '/api/creator/signup') {
        return await handleSignup(request, env, origin);
      }

      if (method === 'POST' && pathname === '/api/creator/login') {
        return await handleLogin(request, env, origin);
      }

      // ── Static assets — serve index.html for non-API routes ──
      if (!pathname.startsWith('/api/')) {
        const asset = await env.ASSETS?.fetch(request);
        if (asset && asset.ok) return asset;
        // If no asset found, fall through to 404
        return errorResponse('Not found', 404, origin);
      }

      // ── Auth-required routes ─────────────────────────────────
      const token = extractToken(request);
      const creatorId = await verifyToken(token, env);

      if (!creatorId) {
        return errorResponse('Authentication required', 401, origin);
      }

      // Profile
      if (method === 'GET' && pathname === '/api/creator/profile') {
        return await handleGetProfile(creatorId, env, origin);
      }
      if (method === 'PUT' && pathname === '/api/creator/profile') {
        return await handleUpdateProfile(request, creatorId, env, origin);
      }

      // Knowledge base
      if (method === 'POST' && pathname === '/api/creator/knowledge-base') {
        return await handleKBUpload(request, creatorId, env, ctx, origin);
      }
      if (method === 'GET' && pathname === '/api/creator/knowledge-base') {
        return await handleKBList(creatorId, env, origin);
      }
      // DELETE /api/creator/knowledge-base/:id
      const kbDeleteMatch = pathname.match(/^\/api\/creator\/knowledge-base\/([a-zA-Z0-9]+)$/);
      if (method === 'DELETE' && kbDeleteMatch) {
        return await handleKBDelete(kbDeleteMatch[1], creatorId, env, origin);
      }

      // Content history
      if (method === 'POST' && pathname === '/api/creator/content-history') {
        return await handleContentHistory(request, creatorId, env, origin);
      }

      // ── Night 2 routes ───────────────────────────────────────

      // Voice fingerprint
      if (method === 'POST' && pathname === '/api/creator/voice/analyze') {
        return await handleVoiceAnalyze(creatorId, env, origin);
      }

      // Content generation (enhanced — replaces Night 1 handler)
      if (method === 'POST' && pathname === '/api/creator/content/generate') {
        return await handleGenerateContent(request, creatorId, env, origin);
      }

      // Interview mode
      if (method === 'POST' && pathname === '/api/creator/interview/start') {
        return await handleInterviewStart(creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/interview/respond') {
        return await handleInterviewRespond(request, creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/interview/generate') {
        return await handleInterviewGenerate(request, creatorId, env, origin);
      }

      // Drafts management
      if (method === 'GET' && pathname === '/api/creator/content/drafts') {
        return await handleListDrafts(creatorId, env, origin);
      }
      // PUT /api/creator/content/drafts/:id
      const draftUpdateMatch = pathname.match(/^\/api\/creator\/content\/drafts\/([a-zA-Z0-9]+)$/);
      if (method === 'PUT' && draftUpdateMatch) {
        return await handleUpdateDraft(draftUpdateMatch[1], request, creatorId, env, origin);
      }

      // Content overlap check
      if (method === 'POST' && pathname === '/api/creator/content/check-overlap') {
        return await handleCheckOverlap(request, creatorId, env, origin);
      }

      // Dashboard stats
      if (method === 'GET' && pathname === '/api/creator/stats') {
        return await handleStats(creatorId, env, origin);
      }

      // Analytics dashboard
      if (method === 'GET' && pathname === '/api/creator/analytics') {
        return await handleAnalytics(creatorId, env, origin);
      }

      // ── Sprint 3: Product catalog (auth'd) ───────────────────

      // GET /api/creator/products
      if (method === 'GET' && pathname === '/api/creator/products') {
        return await handleListProducts(creatorId, env, origin);
      }

      // POST /api/creator/products
      if (method === 'POST' && pathname === '/api/creator/products') {
        return await handleCreateProduct(request, creatorId, env, origin);
      }

      // DELETE /api/creator/products/:id
      const productDeleteMatch = pathname.match(/^\/api\/creator\/products\/([a-zA-Z0-9]+)$/);
      if (method === 'DELETE' && productDeleteMatch) {
        return await handleDeleteProduct(productDeleteMatch[1], creatorId, env, origin);
      }

      // Night 5: Story Extraction (Feature 1)
      if (method === 'POST' && pathname === '/api/creator/story/start') {
        return await handleStoryStart(creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/story/respond') {
        return await handleStoryRespond(request, creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/story/generate-missions') {
        return await handleStoryGenerateMissions(creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/story/lock') {
        return await handleStoryLock(request, creatorId, env, origin);
      }

      // Night 5: Post Quality Scorer (Feature 2)
      if (method === 'POST' && pathname === '/api/creator/content/score') {
        return await handleContentScore(request, creatorId, env, origin);
      }

      // Night 5: A/B Hook Variations (Feature 3)
      if (method === 'POST' && pathname === '/api/creator/content/hooks') {
        return await handleContentHooks(request, creatorId, env, origin);
      }

      // ── Night 6: Feature 1 — LinkedIn Profile Optimizer ──────
      if (method === 'POST' && pathname === '/api/creator/profile-optimizer/scan') {
        return await handleProfileOptimizerScan(request, creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/profile-optimizer/optimize') {
        return await handleProfileOptimizerOptimize(request, creatorId, env, origin);
      }
      if (method === 'GET' && pathname === '/api/creator/profile-optimizer/status') {
        return await handleProfileOptimizerStatus(creatorId, env, origin);
      }

      // ── Night 6: Feature 2 — Full Content Audit Scorecard ────
      if (method === 'POST' && pathname === '/api/creator/content/audit') {
        return await handleContentAudit(request, creatorId, env, origin);
      }

      // ── Night 6: Feature 3 — Fan Monetization ────────────────
      if (method === 'PUT' && pathname === '/api/creator/monetization') {
        return await handleCreatorMonetization(request, creatorId, env, origin);
      }

      // ── Night 6: Feature 4 — Voice Clone ─────────────────────
      if (method === 'POST' && pathname === '/api/creator/voice/clone') {
        return await handleVoiceClone(request, creatorId, env, origin);
      }

      // ── Night 6: Feature 5 — Email Sequences ─────────────────
      if (method === 'GET' && pathname === '/api/creator/email-sequences') {
        return await handleListEmailSequences(creatorId, env, origin);
      }
      if (method === 'POST' && pathname === '/api/creator/email-sequences/generate') {
        return await handleGenerateEmailSequence(request, creatorId, env, origin);
      }
      const emailSeqMatch = pathname.match(/^\/api\/creator\/email-sequences\/([a-zA-Z0-9]+)$/);
      if (method === 'PUT' && emailSeqMatch) {
        return await handleUpdateEmailSequence(emailSeqMatch[1], request, creatorId, env, origin);
      }
      if (method === 'GET' && pathname === '/api/creator/email-queue') {
        return await handleListEmailQueue(creatorId, env, origin);
      }

      // 404
      return errorResponse('Not found', 404, origin);

    } catch (err) {
      console.error('Worker error:', err);
      return errorResponse('Internal server error: ' + (err.message || String(err)), 500, origin);
    }
  },
};
