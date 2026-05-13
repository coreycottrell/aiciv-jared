/**
 * onboarding-capture-proxy — Cloudflare Worker
 *
 * Server-side proxy for A-C-Gee's Fork Awakening conversation-capture API.
 * Holds ACGEE_API_KEY as a wrangler secret so the key is never browser-readable.
 *
 * Created: 2026-05-13 by security-engineer-tech.
 * Replaces direct-from-browser fetch to sageandweaver-network.netlify.app
 * that leaked the ACGEE_API_KEY in /purebrain-3/index.html
 * (os3ctWW0CAQSVPnM-WeNZr75SKTlrvliGTTvkdanYbc — removed same change).
 *
 * Endpoint: POST /api/capture
 *   body: same shape as the upstream capture-proxy payload (source, messages,
 *         aiName, session_uuid, metadata, session_id).
 *   returns: pass-through of upstream response (or 502 if upstream fails).
 *
 * Auth: Origin-bound (CORS). No API key needed in browser.
 *
 * Privacy note: this proxy forwards conversation transcripts during the
 * pre-payment onboarding/naming flow. Per /privacy-policy/, this analytics
 * service is operated directly by Pure Technology (sageandweaver-network is
 * our infrastructure for AI quality improvement). Disclosed in privacy policy.
 */

// ---------- CORS ----------

function parseAllowedOrigins(env) {
  return new Set((env.ALLOWED_ORIGINS || 'https://purebrain.ai').split(',').map(s => s.trim()));
}

function resolveAllowedOrigin(request, env) {
  const allowed = parseAllowedOrigins(env);
  const origin = request.headers.get('Origin') || '';
  if (allowed.has(origin)) return origin;
  return null;
}

function corsHeaders(request, env) {
  const origin = resolveAllowedOrigin(request, env);
  const headers = {
    'Vary': 'Origin',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
  if (origin) headers['Access-Control-Allow-Origin'] = origin;
  return headers;
}

function jsonResponse(body, status, request, env) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(request, env),
    },
  });
}

// ---------- Payload size guard (anti-DoS) ----------
// Conversation transcripts are bounded — we cap to 256KB.
const MAX_BODY_BYTES = 256 * 1024;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    }

    if (path === '/health') {
      return jsonResponse(
        { status: 'ok', service: 'onboarding-capture-proxy', ts: new Date().toISOString() },
        200, request, env
      );
    }

    const allowedOrigin = resolveAllowedOrigin(request, env);
    if (!allowedOrigin) {
      return jsonResponse({ error: 'origin not allowed' }, 403, request, env);
    }

    if (path === '/api/capture' && request.method === 'POST') {
      if (!env.ACGEE_API_KEY) {
        console.error('ACGEE_API_KEY secret not set on worker');
        return jsonResponse({ error: 'server misconfigured' }, 500, request, env);
      }
      if (!env.UPSTREAM_URL) {
        return jsonResponse({ error: 'server misconfigured' }, 500, request, env);
      }

      // Read body as text first so we can enforce size + re-emit.
      let rawBody;
      try {
        rawBody = await request.text();
      } catch {
        return jsonResponse({ error: 'failed to read body' }, 400, request, env);
      }
      if (rawBody.length > MAX_BODY_BYTES) {
        return jsonResponse({ error: 'payload too large' }, 413, request, env);
      }

      // Sanity-check JSON shape (do NOT mutate — pass-through to A-C-Gee).
      let parsed;
      try {
        parsed = rawBody ? JSON.parse(rawBody) : null;
      } catch {
        return jsonResponse({ error: 'invalid JSON' }, 400, request, env);
      }
      if (!parsed || typeof parsed !== 'object') {
        return jsonResponse({ error: 'payload must be an object' }, 400, request, env);
      }

      try {
        const upstream = await fetch(env.UPSTREAM_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': env.ACGEE_API_KEY,
          },
          body: rawBody,
        });
        const text = await upstream.text();
        // Best-effort JSON pass-through; if upstream returns non-JSON, wrap it.
        let upstreamBody;
        try { upstreamBody = text ? JSON.parse(text) : {}; }
        catch { upstreamBody = { raw: text }; }
        if (!upstream.ok) {
          console.error('Upstream capture failed', upstream.status, upstreamBody);
          return jsonResponse(
            { error: 'upstream failed', upstream_status: upstream.status, body: upstreamBody },
            502, request, env
          );
        }
        return jsonResponse({ ok: true, upstream: upstreamBody }, 200, request, env);
      } catch (err) {
        console.error('onboarding-capture-proxy fetch error', err);
        return jsonResponse({ error: 'upstream unreachable' }, 502, request, env);
      }
    }

    return jsonResponse({ error: 'not found' }, 404, request, env);
  },
};
