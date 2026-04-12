/**
 * PureBrain CF Pages Worker (_worker.js)
 *
 * Handles API routes that require server-side execution.
 * When this file is present, /functions/ directory is ignored by CF Pages.
 *
 * Routes:
 *   POST /api/subscribe   — Brevo Neural Feed subscription proxy
 *   OPTIONS *             — CORS preflight
 *   *                     — Fall through to static assets via ASSETS binding
 *
 * Environment variables (set in CF Pages dashboard):
 *   BREVO_API_KEY       — Brevo API key (xkeysib-... format)
 *
 * Note: The /functions/ directory is kept for reference but is NOT executed.
 * All function logic lives here in _worker.js.
 */

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://purebrain-staging.pages.dev',
  'https://voice.purebrain.ai',
];

const BREVO_LIST_ID = 3;

function getCorsHeaders(origin) {
  const corsOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': corsOrigin,
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

function json(body, status, cors) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method.toUpperCase();
    const path = url.pathname;
    const origin = request.headers.get('Origin') || '';
    const cors = getCorsHeaders(origin);

    // CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: { ...cors, 'Access-Control-Max-Age': '86400' },
      });
    }

    // POST /api/subscribe
    if (method === 'POST' && path === '/api/subscribe') {
      // Parse body
      let body;
      try { body = await request.json(); } catch {
        return json({ ok: false, message: 'Invalid JSON' }, 400, cors);
      }

      const { email } = body;
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return json({ ok: false, message: 'Valid email required' }, 400, cors);
      }

      const apiKey = (env.BREVO_API_KEY || '').trim().replace(/[\r\n]/g, '');
      if (!apiKey) {
        return json({ ok: false, message: 'Server configuration error' }, 200, cors);
      }

      // Call Brevo API
      let brevoStatus = 0;
      let brevoDetail = '';
      try {
        const brevoResp = await fetch('https://api.brevo.com/v3/contacts', {
          method: 'POST',
          headers: {
            'api-key': apiKey,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            email,
            listIds: [BREVO_LIST_ID],
            updateEnabled: true,
            attributes: { SOURCE: 'purebrain-blog' },
          }),
        });
        brevoStatus = brevoResp.status;
        try { const d = await brevoResp.json(); brevoDetail = d.message || ''; } catch {}
      } catch (fetchErr) {
        return json({ ok: false, message: 'Network error' }, 200, cors);
      }

      if (brevoStatus === 201) {
        return json({ ok: true, message: 'subscribed' }, 200, cors);
      }
      if (brevoStatus === 204) {
        return json({ ok: true, message: 'already_subscribed' }, 200, cors);
      }
      return json({ ok: false, message: brevoDetail || 'Subscription failed' }, 200, cors);
    }

    // voice.purebrain.ai → serve /voice-manager/ content
    const hostname = new URL(request.url).hostname;
    if (hostname === 'voice.purebrain.ai') {
      const url = new URL(request.url);
      const path = url.pathname === '/' ? '/voice-manager/index.html' : '/voice-manager' + url.pathname;
      const rewritten = new Request(new URL(path, url.origin), request);
      return env.ASSETS.fetch(rewritten);
    }

    // All other requests: serve static assets
    return env.ASSETS.fetch(request);
  },
};
