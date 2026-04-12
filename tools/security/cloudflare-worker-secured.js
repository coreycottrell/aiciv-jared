/**
 * PureBrain Claude API Proxy - Cloudflare Worker (SECURED)
 *
 * Security layers (defense in depth):
 *   1. Origin whitelist  - only purebrain.ai / puremarketing.ai
 *   2. Secret token      - X-PB-Token header must match PB_AUTH_TOKEN env var
 *   3. Per-IP rate limit - max 30 requests / minute via Cloudflare KV
 *   4. Rejection logging - all blocked requests written to console
 *
 * Required environment variables (set in Cloudflare dashboard as encrypted):
 *   ANTHROPIC_API_KEY  - Your Anthropic API key  (sk-ant-...)
 *   PB_AUTH_TOKEN      - Your 32-char secret      (generate with: openssl rand -base64 24)
 *
 * Required KV namespace (bind in dashboard as):
 *   RATE_LIMIT_KV
 *
 * See CLOUDFLARE-WORKER-DEPLOY.md for full setup instructions.
 */

// ---------------------------------------------------------------------------
// 1. ORIGIN WHITELIST
// ---------------------------------------------------------------------------
const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://puremarketing.ai',
  'https://www.puremarketing.ai',
];

// ---------------------------------------------------------------------------
// 2. RATE LIMIT CONFIG
// ---------------------------------------------------------------------------
const RATE_LIMIT_MAX_REQUESTS = 30;   // max requests
const RATE_LIMIT_WINDOW_SECONDS = 60; // per minute
const RATE_LIMIT_KV_TTL = RATE_LIMIT_WINDOW_SECONDS + 5; // KV expiry (seconds)

// ---------------------------------------------------------------------------
// HELPERS
// ---------------------------------------------------------------------------

/**
 * Build CORS headers.
 * If origin is allowed, echo it back (required for credentialed requests).
 * If origin is NOT in the whitelist, we will have already rejected the
 * request before this function matters - but we still return a safe
 * default so no browser receives a wildcard.
 */
function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-PB-Token',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

/**
 * Constant-time string comparison.
 * Prevents timing attacks on the secret token check.
 */
function timingSafeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  const encoder = new TextEncoder();
  const aBytes = encoder.encode(a);
  const bBytes = encoder.encode(b);
  if (aBytes.length !== bBytes.length) {
    // Still iterate over a to avoid length-based timing leak
    let result = 1;
    for (let i = 0; i < aBytes.length; i++) result |= aBytes[i] ^ (bBytes[i % bBytes.length] || 0);
    return false;
  }
  let diff = 0;
  for (let i = 0; i < aBytes.length; i++) {
    diff |= aBytes[i] ^ bBytes[i];
  }
  return diff === 0;
}

/**
 * Extract a stable client identifier.
 * Cloudflare provides the connecting IP in CF-Connecting-IP.
 * Fall back to a generic key so rate limiting still applies.
 */
function getClientIP(request) {
  return request.headers.get('CF-Connecting-IP') || 'unknown';
}

/**
 * Per-IP rate limiting backed by Cloudflare KV.
 * KV is eventually consistent but good enough for abuse prevention.
 *
 * @param {KVNamespace} kv  - Bound KV namespace (RATE_LIMIT_KV)
 * @param {string} ip       - Client IP address
 * @returns {Promise<{allowed: boolean, remaining: number}>}
 */
async function checkRateLimit(kv, ip) {
  // KV key is scoped to the current 60-second window so it auto-resets
  const window = Math.floor(Date.now() / (RATE_LIMIT_WINDOW_SECONDS * 1000));
  const key = `rl:${ip}:${window}`;

  let count = 0;
  try {
    const stored = await kv.get(key);
    count = stored ? parseInt(stored, 10) : 0;
  } catch (_) {
    // KV read error - fail open (allow) to avoid blocking legitimate users
    // on infra issues, but log it
    console.warn(`[RATE_LIMIT] KV read error for key ${key}`);
    return { allowed: true, remaining: RATE_LIMIT_MAX_REQUESTS };
  }

  if (count >= RATE_LIMIT_MAX_REQUESTS) {
    return { allowed: false, remaining: 0 };
  }

  // Increment counter (fire-and-forget - don't await to keep latency low)
  kv.put(key, String(count + 1), { expirationTtl: RATE_LIMIT_KV_TTL }).catch(() => {});

  return { allowed: true, remaining: RATE_LIMIT_MAX_REQUESTS - count - 1 };
}

/**
 * Structured rejection log.
 * All rejected requests are written to console so they appear in the
 * Cloudflare dashboard under Workers > Logs.
 */
function logRejection(reason, ip, origin, extra = {}) {
  console.log(JSON.stringify({
    event: 'rejected',
    reason,
    ip,
    origin: origin || '(none)',
    ts: new Date().toISOString(),
    ...extra,
  }));
}

// ---------------------------------------------------------------------------
// MAIN HANDLER
// ---------------------------------------------------------------------------
export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin') || '';
    const ip     = getClientIP(request);
    const cors   = corsHeaders(origin);

    // -----------------------------------------------------------------------
    // PREFLIGHT
    // Browser sends OPTIONS before the real POST - must respond correctly
    // for credentialed cross-origin requests.
    // -----------------------------------------------------------------------
    if (request.method === 'OPTIONS') {
      // Only respond to allowed origins - browser will block disallowed ones
      // regardless, but rejecting here reduces noise and leaks no info.
      if (!ALLOWED_ORIGINS.includes(origin)) {
        logRejection('origin_not_allowed_preflight', ip, origin);
        return new Response(null, { status: 403 });
      }
      return new Response(null, { status: 204, headers: cors });
    }

    // -----------------------------------------------------------------------
    // METHOD CHECK
    // -----------------------------------------------------------------------
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    // -----------------------------------------------------------------------
    // LAYER 1: ORIGIN CHECK
    // Must be a known purebrain.ai / puremarketing.ai origin.
    // Direct API calls (no Origin header) are also rejected.
    // -----------------------------------------------------------------------
    if (!ALLOWED_ORIGINS.includes(origin)) {
      logRejection('origin_not_allowed', ip, origin);
      return new Response(JSON.stringify({ error: 'Forbidden' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // -----------------------------------------------------------------------
    // LAYER 2: SECRET TOKEN CHECK
    // Client must send X-PB-Token header matching the PB_AUTH_TOKEN env var.
    // Compared with constant-time equality to prevent timing attacks.
    // -----------------------------------------------------------------------
    if (!env.PB_AUTH_TOKEN) {
      // Misconfiguration - don't expose details to caller
      console.error('[CONFIG] PB_AUTH_TOKEN env var is not set');
      return new Response(JSON.stringify({ error: 'Service unavailable' }), {
        status: 503,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    const clientToken = request.headers.get('X-PB-Token') || '';
    if (!timingSafeEqual(clientToken, env.PB_AUTH_TOKEN)) {
      logRejection('invalid_token', ip, origin);
      return new Response(JSON.stringify({ error: 'Forbidden' }), {
        status: 403,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    // -----------------------------------------------------------------------
    // LAYER 3: RATE LIMITING
    // 30 requests per IP per 60-second window.
    // Requires RATE_LIMIT_KV namespace binding.
    // -----------------------------------------------------------------------
    if (env.RATE_LIMIT_KV) {
      const { allowed, remaining } = await checkRateLimit(env.RATE_LIMIT_KV, ip);
      if (!allowed) {
        logRejection('rate_limit_exceeded', ip, origin);
        return new Response(JSON.stringify({ error: 'Too many requests' }), {
          status: 429,
          headers: {
            ...cors,
            'Content-Type': 'application/json',
            'Retry-After': String(RATE_LIMIT_WINDOW_SECONDS),
            'X-RateLimit-Limit': String(RATE_LIMIT_MAX_REQUESTS),
            'X-RateLimit-Remaining': '0',
          },
        });
      }
    } else {
      // KV not configured - log warning but do not block (fail open)
      // This ensures the proxy works even before KV is set up,
      // but operators should configure KV immediately.
      console.warn('[CONFIG] RATE_LIMIT_KV not bound - rate limiting disabled');
    }

    // -----------------------------------------------------------------------
    // LAYER 4: ANTHROPIC API KEY
    // -----------------------------------------------------------------------
    if (!env.ANTHROPIC_API_KEY) {
      console.error('[CONFIG] ANTHROPIC_API_KEY env var is not set');
      return new Response(JSON.stringify({ error: 'Service unavailable' }), {
        status: 503,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    // -----------------------------------------------------------------------
    // PROXY TO ANTHROPIC
    // Forward the request body as-is - no mutation of the payload.
    // -----------------------------------------------------------------------
    let body;
    try {
      body = await request.json();
    } catch (_) {
      return new Response(JSON.stringify({ error: 'Invalid JSON body' }), {
        status: 400,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    try {
      const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify(body),
      });

      const data = await anthropicResponse.json();

      return new Response(JSON.stringify(data), {
        status: anthropicResponse.status,
        headers: {
          ...cors,
          'Content-Type': 'application/json',
        },
      });

    } catch (error) {
      console.error('[PROXY] Upstream error:', error.message);
      return new Response(JSON.stringify({ error: 'Upstream error' }), {
        status: 502,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }
  },
};
