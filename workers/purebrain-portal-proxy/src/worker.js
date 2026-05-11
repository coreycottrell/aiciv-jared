/**
 * PureBrain Portal Proxy Worker
 * ==============================
 * Routes *.purebrain.ai portal subdomains to Witness containers at 37.27.237.109.
 *
 * Request flow:
 *   {subdomain}.purebrain.ai/*
 *     → Check if portal subdomain (not a known system subdomain)
 *     → If portal: proxy to https://{subdomain}.ai-civ.com on Witness (37.27.237.109)
 *     → If system subdomain: pass through to Cloudflare (tunnel handles it)
 *
 * P-2 FIX (2026-04-15): The prior version had a special-case for
 *   `app.purebrain.ai/api/referral/*` that proxied to `chy-jared.ai-civ.com`.
 *   That container's D1-backed handler returned HTTP 200 success bodies
 *   without writing to the authoritative SQLite store on the VPS, silently
 *   dropping every referral attribution since at least 2026-04-14.
 *
 *   Fix: removed the special-case. `app` is already a SYSTEM_SUBDOMAIN, so it
 *   now falls through to Cloudflare routing, which hands off to the cloudflared
 *   tunnel → nginx → portal_server.py:8097 (SQLite authoritative). Root cause
 *   + audit in:
 *     /home/jared/exports/portal-files/referral-attribution-flow-2026-04-15.md
 *     .claude/memory/agent-learnings/security-engineer-tech/2026-04-15--p2-referral-attribution-ghost-endpoint.md
 *
 * Deploy:
 *   Worker name:  purebrain-portal-proxy
 *   Route:        *.purebrain.ai/*  (already configured on zone)
 *   Zone:         purebrain.ai (ID: 49400cad1527af716705f6cb8c22bb65)
 *
 * Witness server: 37.27.237.109
 * Container URL format: https://{subdomain}.ai-civ.com
 */

// Known system subdomains — pass these through to Cloudflare/tunnel unchanged.
// These have explicit DNS records (CNAME → cloudflared tunnel) that handle routing.
const SYSTEM_SUBDOMAINS = new Set([
  'app',
  'www',
  'portal',
  'api',
  'video',
  'cc',
  'comms',
  'mail',
  'staging',
  'blog',
  'status',
  'cdn',
  'static',
  'assets',
  'media',
  'social',         // social.purebrain.ai → social-api CF Worker
  'social-api',     // social-api.purebrain.ai → social-api CF Worker
  'voice',          // voice.purebrain.ai → proxy worker handles routing
  'tts',            // tts.purebrain.ai → Argo Tunnel to Chatterbox TTS
  'keenjared',     // Legacy test portal — still in DNS, routed via nginx
  'testariatest',  // Legacy test portal — still in DNS, routed via nginx
]);

// Witness server IP — all container traffic routes here
const WITNESS_IP = '37.27.237.109';

// ai-civ.com: the actual hostname namespace for portal containers
const CONTAINER_DOMAIN = 'ai-civ.com';

/**
 * Determine if this subdomain is a portal subdomain.
 * Returns true if it should be proxied to Witness.
 * Returns false if it's a known system subdomain.
 */
function isPortalSubdomain(subdomain) {
  if (!subdomain) return false;
  if (SYSTEM_SUBDOMAINS.has(subdomain.toLowerCase())) return false;
  return /^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/.test(subdomain.toLowerCase());
}

/**
 * Extract the subdomain from a Host header value.
 * e.g. "greg-lucas-neuteufel.purebrain.ai" → "greg-lucas-neuteufel"
 * e.g. "purebrain.ai" → "" (no subdomain = apex domain)
 */
function extractSubdomain(host) {
  const hostname = host.split(':')[0];
  const parts = hostname.split('.');
  if (parts.length <= 2) return '';
  return parts.slice(0, parts.length - 2).join('.');
}

/**
 * Proxy a request to a specific container on Witness.
 */
async function proxyToContainer(request, targetHost, originalHost) {
  const url = new URL(request.url);
  const targetUrl = `https://${targetHost}${url.pathname}${url.search}`;

  const proxyHeaders = new Headers(request.headers);
  proxyHeaders.set('Host', targetHost);
  proxyHeaders.set('X-Forwarded-Host', originalHost);
  proxyHeaders.set('X-Forwarded-Proto', url.protocol.replace(':', ''));
  proxyHeaders.set('X-Real-IP', request.headers.get('CF-Connecting-IP') || '');

  const proxyRequest = new Request(targetUrl, {
    method: request.method,
    headers: proxyHeaders,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
    redirect: 'manual',
  });

  const response = await fetch(proxyRequest, {
    cf: { resolveOverride: WITNESS_IP },
  });

  const responseHeaders = new Headers(response.headers);
  const location = responseHeaders.get('Location');
  if (location && location.includes(`.${CONTAINER_DOMAIN}`)) {
    const rewritten = location.replace(
      new RegExp(`([a-z0-9-]+)\\.${CONTAINER_DOMAIN.replace('.', '\\.')}`, 'g'),
      `$1.purebrain.ai`
    );
    responseHeaders.set('Location', rewritten);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

/**
 * Validate the caller has a valid `leader` session before allowing the bridge
 * to inject `X-Admin-Token` into admin-api forwards.
 *
 * Source: 2026-05-09 CTO pre-build spec. Closes the bug where anonymous
 * `curl https://portal.purebrain.ai/api/admin/invites` received a server-injected
 * admin token + full invitee list (including role:leader grants).
 *
 * Reuses the existing `/internal/validate-session` Service Binding contract on
 * `clients-api` (already production-hardened by admin-api + social-api callers).
 *
 * Failure modes (fail CLOSED — security gate):
 *   - missing token        → 401 unauthorized
 *   - missing binding/secret → 503 auth_unavailable
 *   - bridge non-success   → 401 unauthorized
 *   - role !== "leader"    → 403 forbidden
 *   - bridge throw         → 503 auth_unavailable
 *
 * Token sources accepted (matches admin-api getSession order):
 *   1. Authorization: Bearer <token>      (preferred, used by admin frontend localStorage)
 *   2. Cookie social_session=<token>      (fallback, set by /api/login → social-api)
 */
async function validateLeaderSession(request, env) {
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return { ok: false, status: 401 };

  if (!env.CLIENTS_API || !env.INTERNAL_BINDING_SECRET) {
    // Fail CLOSED — emergency security gate. Better 503 than bypass.
    return { ok: false, status: 503 };
  }

  try {
    const req = new Request("https://clients-api/internal/validate-session", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-binding": "clients-api",
        "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
      },
      body: JSON.stringify({ token }),
    });
    const resp = await env.CLIENTS_API.fetch(req);
    if (!resp.ok) return { ok: false, status: 401 };
    const j = await resp.json();
    if (!j || j.valid !== true) return { ok: false, status: 401 };
    if (!["leader","owner"].includes(j.role)) return { ok: false, status: 403 };
    return { ok: true, session: j };
  } catch {
    // Bridge unreachable — fail CLOSED for security routes.
    return { ok: false, status: 503 };
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const host = request.headers.get('Host') || url.host;
    const subdomain = extractSubdomain(host);

    // No subdomain = apex domain (purebrain.ai itself).
    if (!subdomain) {
      return fetch(request);
    }

    // NOTE: the prior `app + /api/referral/*` special-case was REMOVED
    // (P-2 fix 2026-04-15). `app` is a SYSTEM_SUBDOMAIN and now falls through
    // to the tunnel → nginx → portal_server.py, which is the authoritative
    // SQLite write path.

    // portal.purebrain.ai routing
    if (subdomain === 'portal') {
      // Admin HTML pages → CF Pages (git, NOT container)
      if (url.pathname.startsWith('/admin/clients') || url.pathname.startsWith('/admin/referrals')) {
        const pagesPath = url.pathname.endsWith('/') ? url.pathname + 'index.html' : url.pathname + '/index.html';
        const resp = await fetch(`https://purebrain.ai${pagesPath}`);
        return new Response(resp.body, { status: resp.status, headers: resp.headers });
      }
      // Admin + Referral API → D1 Workers
      // Login API → social-api Worker (for email/password auth).
      //
      // Phase 7c (2026-05-11): switched from outbound fetch() to Service
      // Binding to preserve cf-connecting-ip across the Worker→Worker hop.
      // Prior outbound fetch() caused social-api to see a shared edge IP
      // (or null → "unknown") for ALL portal logins globally, saturating
      // the LOGIN_TOTAL_LIMIT=20/60min bucket within minutes and 429ing
      // every subsequent login. Service binding hands the receiving
      // Worker the same Request object — cf-connecting-ip is the real
      // client IP. Constitutional pattern: feedback_cf_service_binding_pattern.md
      if (url.pathname === '/api/login') {
        if (!env.SOCIAL_API) {
          // Defensive: should be impossible if wrangler.toml is correct,
          // but fail CLOSED if binding is missing (matches the
          // CLIENTS_API fail-closed pattern at line 163-166).
          return new Response(
            JSON.stringify({ error: 'login service binding unavailable' }),
            { status: 503, headers: { 'content-type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
          );
        }
        const resp = await env.SOCIAL_API.fetch(request);
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Referral API → referrals-api Worker (D1)
      // B1 (referral-v1): path mismatch fix.
      //   payment-page POSTs to /api/referral/complete must forward to
      //   referrals-api /referrals/complete (the actual handler path) — not
      //   the bare /complete that the previous prefix-strip produced.
      //   Map: /api/referral/<rest> → /referrals/<rest>
      //   Special: /api/referral or /api/referral/ → /referrals
      if (url.pathname.startsWith('/api/referral/') || url.pathname === '/api/referral') {
        const tail = url.pathname === '/api/referral'
          ? ''
          : url.pathname.slice('/api/referral'.length); // includes leading '/'
        const workerPath = '/referrals' + tail; // e.g. /referrals/complete, /referrals/track
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const resp = await fetch(new Request(workerUrl, {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin referral endpoints → referrals-api Worker (D1)
      // SECURITY (2026-05-09 V-11 regression on referral-v1): X-Admin-Token now sourced from
      // env.ADMIN_TOKEN secret. Hardcoded literal `purebrain-admin-2026` was retired on `main`
      // by commit 1fe0a3e (2026-05-07) but branch divergence left it live on referral-v1 until
      // this commit. Token rotated and bound via wrangler secret put on both portal-proxy and
      // admin-api workers concurrent with this change.
      if (url.pathname.startsWith('/api/admin/affiliat') || url.pathname.startsWith('/api/admin/payout') || url.pathname.startsWith('/api/admin/referral/') || url.pathname === '/api/admin/stats') {
        const workerPath = url.pathname.replace('/api/admin', '/admin');
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const proxyHeaders = new Headers(request.headers);
        if (env.ADMIN_TOKEN) proxyHeaders.set('X-Admin-Token', env.ADMIN_TOKEN);
        const resp = await fetch(new Request(workerUrl, {
          method: request.method, headers: proxyHeaders,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin referral endpoints → referrals-api Worker (D1)
      // NOTE: duplicate dead-code block of the above (identical `if` always matches first block).
      // Left in place per dispatch scope; token literal patched defensively so any future code
      // shuffle cannot reintroduce the leak. Separate cleanup will remove the dead block.
      if (url.pathname.startsWith('/api/admin/affiliat') || url.pathname.startsWith('/api/admin/payout') || url.pathname.startsWith('/api/admin/referral/') || url.pathname === '/api/admin/stats') {
        const workerPath = url.pathname.replace('/api/admin', '/admin');
        const proxyHeaders = new Headers(request.headers);
        if (env.ADMIN_TOKEN) proxyHeaders.set('X-Admin-Token', env.ADMIN_TOKEN);
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const resp = await fetch(new Request(workerUrl, {
          method: request.method, headers: proxyHeaders,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin clients + invites endpoints → admin-api Worker (D1 purebrain-social shared)
      // Apr 23 split (commit 8474bc8) added admin-api routes but never wired the proxy.
      // This routes the six P0 endpoints (PATCH client, invite CRUD) that were 404ing.
      // CONSTRAINT: throwaway bridge code — Tier 3 Phase 9 deletes this whole admin block.
      // CTO pre-build approved 2026-05-08: HTTP+token (NOT Service Bindings — admin-api deletion ~2 weeks).
      //
      // SECURITY GATE (2026-05-09 CTO spec, post-V11-rotation finding):
      //   Before injecting env.ADMIN_TOKEN, validate the caller has a leader
      //   session via the CLIENTS_API Service Binding. Closes the anonymous
      //   data-exposure bug where curl with no auth received the full invitee
      //   list (including role:leader invite tokens). PUBLIC EXCEPTION:
      //   /api/admin/validate-token is intentionally unauthenticated (powers
      //   invite-landing before sign-in — admin-api worker.js:404).
      if (
        url.pathname.startsWith('/api/admin/clients') ||
        url.pathname.startsWith('/api/admin/invite') ||
        url.pathname.startsWith('/api/admin/invites') ||
        url.pathname === '/api/admin/validate-token'
      ) {
        if (url.pathname !== '/api/admin/validate-token') {
          const gate = await validateLeaderSession(request, env);
          if (!gate.ok) {
            const errBody = gate.status === 403
              ? '{"error":"forbidden"}'
              : (gate.status === 503 ? '{"error":"auth_unavailable"}' : '{"error":"unauthorized"}');
            return new Response(errBody, {
              status: gate.status,
              headers: {
                'content-type': 'application/json',
                'Access-Control-Allow-Origin': '*',
              },
            });
          }
        }
        const workerUrl = `https://admin-api.in0v8.workers.dev${url.pathname}${url.search}`;
        const proxyHeaders = new Headers(request.headers);
        if (env.ADMIN_TOKEN) {
          proxyHeaders.set('X-Admin-Token', env.ADMIN_TOKEN);
        }
        const resp = await fetch(new Request(workerUrl, {
          method: request.method,
          headers: proxyHeaders,
          body: (request.method !== 'GET' && request.method !== 'HEAD' && request.method !== 'OPTIONS') ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin client endpoints → social-api Worker (D1)
      if (url.pathname.startsWith('/api/admin/')) {
        const workerUrl = `https://social-api.in0v8.workers.dev${url.pathname}${url.search}`;
        const resp = await fetch(new Request(workerUrl, {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
    }

    // voice.purebrain.ai routing:
    //   /tts/* and /health → proxy to Hetzner VPS port 8950 (SSH-forwarded to Vast.ai GPU)
    //   everything else → CF Pages voice-manager UI
    if (subdomain === 'voice') {
      if (url.pathname.startsWith('/tts') || url.pathname === '/health') {
        if (request.method === 'OPTIONS') {
          return new Response(null, { status: 204, headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400',
          }});
        }
        // Route TTS API calls through tts.purebrain.ai (Argo Tunnel → Hetzner → Vast.ai GPU)
        const ttsUrl = `https://tts.purebrain.ai${url.pathname}${url.search}`;
        const ttsReq = new Request(ttsUrl, {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        });
        const resp = await fetch(ttsReq);
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        respHeaders.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        respHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Voice manager UI
      const voicePath = url.pathname === '/' ? '/voice-manager/' : '/voice-manager' + url.pathname;
      const rewrittenUrl = new URL(voicePath, 'https://purebrain.ai');
      rewrittenUrl.search = url.search;
      const newReq = new Request(rewrittenUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
      });
      return fetch(newReq);
    }

    // System subdomain — pass through to Cloudflare routing (tunnel handles these).
    if (!isPortalSubdomain(subdomain)) {
      return fetch(request);
    }

    // Portal subdomain — proxy to {subdomain}.ai-civ.com on Witness.
    const targetHost = `${subdomain}.${CONTAINER_DOMAIN}`;

    try {
      return await proxyToContainer(request, targetHost, host);
    } catch (err) {
      return new Response(
        `Portal unavailable. Your portal "${subdomain}" may still be initializing. ` +
          `Please try again in a few minutes. (Error: ${err.message})`,
        {
          status: 502,
          headers: { 'Content-Type': 'text/plain' },
        }
      );
    }
  },
};
