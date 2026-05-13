/**
 * contact-form-api — Cloudflare Worker
 *
 * Receives contact form submissions from purebrain.ai/contact-us/ and forwards
 * them to Brevo transactional API server-side. Holds BREVO_API_KEY as a wrangler
 * secret so it's never exposed in browser-readable HTML.
 *
 * Created: 2026-05-13 by security-engineer-tech.
 * Replaces direct-from-browser fetch to api.brevo.com that leaked the Brevo
 * API key in /contact-us/index.html (xkeysib-9f445c4c3a44763f... — removed
 * same change).
 *
 * Endpoint: POST /api/contact
 *   body: { name, email, phone, company?, service?, message? }
 *   returns: { ok: true } on success, { error } on failure (4xx/5xx).
 *
 * Auth: Origin-bound (CORS). No API key in client. Defense-in-depth via:
 *   - origin allowlist
 *   - required-field validation
 *   - email format check
 *   - basic length caps (anti-DoS)
 */

const BREVO_SEND_URL = 'https://api.brevo.com/v3/smtp/email';

// Field length caps — anti-DoS, anti-spam
const LIMITS = {
  name: 200,
  email: 320, // RFC 5321 max
  phone: 50,
  company: 200,
  service: 200,
  message: 5000,
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ---------- CORS ----------

function parseAllowedOrigins(env) {
  return new Set((env.ALLOWED_ORIGINS || 'https://purebrain.ai').split(',').map(s => s.trim()));
}

function resolveAllowedOrigin(request, env) {
  const allowed = parseAllowedOrigins(env);
  const origin = request.headers.get('Origin') || '';
  if (allowed.has(origin)) return origin;
  // Reject everything else (returns false-y for caller).
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

// ---------- HTML escape (server-side, defense-in-depth) ----------

function escHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ---------- Validation ----------

function validate(body) {
  const errors = [];
  if (!body || typeof body !== 'object') return ['invalid payload'];

  const required = ['name', 'email', 'phone'];
  for (const k of required) {
    if (!body[k] || typeof body[k] !== 'string' || !body[k].trim()) {
      errors.push(`${k} is required`);
    }
  }
  if (errors.length) return errors;

  for (const [k, limit] of Object.entries(LIMITS)) {
    if (body[k] && typeof body[k] === 'string' && body[k].length > limit) {
      errors.push(`${k} exceeds ${limit} chars`);
    }
  }
  if (!EMAIL_RE.test(body.email)) errors.push('invalid email format');

  return errors;
}

// ---------- Brevo send ----------

async function sendViaBrevo(env, body) {
  const name = String(body.name || '').trim();
  const email = String(body.email || '').trim();
  const phone = String(body.phone || '').trim();
  const company = String(body.company || '').trim();
  const service = String(body.service || '').trim();
  const message = String(body.message || '').trim();

  const htmlContent =
    '<h2>New Contact Form Submission</h2>' +
    '<table style="border-collapse:collapse;width:100%;max-width:600px;">' +
    `<tr><td style="padding:8px 12px;border:1px solid #ddd;font-weight:bold;">Name</td><td style="padding:8px 12px;border:1px solid #ddd;">${escHtml(name)}</td></tr>` +
    `<tr><td style="padding:8px 12px;border:1px solid #ddd;font-weight:bold;">Email</td><td style="padding:8px 12px;border:1px solid #ddd;"><a href="mailto:${escHtml(email)}">${escHtml(email)}</a></td></tr>` +
    `<tr><td style="padding:8px 12px;border:1px solid #ddd;font-weight:bold;">Phone</td><td style="padding:8px 12px;border:1px solid #ddd;">${escHtml(phone)}</td></tr>` +
    `<tr><td style="padding:8px 12px;border:1px solid #ddd;font-weight:bold;">Company</td><td style="padding:8px 12px;border:1px solid #ddd;">${escHtml(company || 'N/A')}</td></tr>` +
    `<tr><td style="padding:8px 12px;border:1px solid #ddd;font-weight:bold;">Service Interest</td><td style="padding:8px 12px;border:1px solid #ddd;">${escHtml(service || 'Not specified')}</td></tr>` +
    `<tr><td style="padding:8px 12px;border:1px solid #ddd;font-weight:bold;">Message</td><td style="padding:8px 12px;border:1px solid #ddd;">${escHtml(message || 'No message provided')}</td></tr>` +
    '</table>' +
    `<p style="margin-top:16px;color:#666;font-size:13px;">Submitted from purebrain.ai/contact-us/ at ${new Date().toISOString()}</p>`;

  const payload = {
    sender: { name: env.SENDER_NAME || 'PureBrain Contact Form', email: env.SENDER_EMAIL || 'purebrain@puremarketing.ai' },
    to: [{ email: env.TO_EMAIL || 'support@puremarketing.ai', name: 'Jared Sanborn' }],
    subject: 'New Contact Form Submission from ' + name,
    htmlContent,
    replyTo: { email, name },
  };

  const res = await fetch(BREVO_SEND_URL, {
    method: 'POST',
    headers: {
      'accept': 'application/json',
      'api-key': env.BREVO_API_KEY,
      'content-type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  let parsed;
  try { parsed = text ? JSON.parse(text) : {}; } catch { parsed = { raw: text }; }
  return { ok: res.ok, status: res.status, body: parsed };
}

// ---------- Router ----------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    }

    // Health (no auth — always returns 200)
    if (path === '/health') {
      return jsonResponse({ status: 'ok', service: 'contact-form-api', ts: new Date().toISOString() }, 200, request, env);
    }

    // Reject any request whose Origin isn't whitelisted (browser callers).
    // Server-to-server callers (no Origin) are NOT supported on this worker — it's
    // exclusively a browser-form proxy.
    const allowedOrigin = resolveAllowedOrigin(request, env);
    if (!allowedOrigin) {
      return jsonResponse({ error: 'origin not allowed' }, 403, request, env);
    }

    if (path === '/api/contact' && request.method === 'POST') {
      if (!env.BREVO_API_KEY) {
        console.error('BREVO_API_KEY secret not set on worker');
        return jsonResponse({ error: 'server misconfigured' }, 500, request, env);
      }

      let body;
      try {
        body = await request.json();
      } catch {
        return jsonResponse({ error: 'invalid JSON' }, 400, request, env);
      }

      const errors = validate(body);
      if (errors.length) {
        return jsonResponse({ error: 'validation failed', details: errors }, 400, request, env);
      }

      try {
        const result = await sendViaBrevo(env, body);
        if (!result.ok) {
          console.error('Brevo send failed', result.status, result.body);
          return jsonResponse({ error: result.body?.message || 'send failed' }, 502, request, env);
        }
        return jsonResponse({ ok: true, messageId: result.body?.messageId || null }, 200, request, env);
      } catch (err) {
        console.error('contact-form-api error', err);
        return jsonResponse({ error: 'internal error' }, 500, request, env);
      }
    }

    return jsonResponse({ error: 'not found' }, 404, request, env);
  },
};
