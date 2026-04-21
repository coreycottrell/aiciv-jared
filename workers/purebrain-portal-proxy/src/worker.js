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
      // Login API → social-api Worker (for email/password auth)
      if (url.pathname === '/api/login') {
        const resp = await fetch(new Request('https://social-api.in0v8.workers.dev/api/login', {
          method: request.method, headers: request.headers,
          body: request.method !== 'GET' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Referral API → referrals-api Worker (D1)
      if (url.pathname.startsWith('/api/referral/') || url.pathname === '/api/referral') {
        const workerPath = url.pathname.replace('/api/referral', '') || '/';
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
      if (url.pathname.startsWith('/api/admin/affiliat') || url.pathname.startsWith('/api/admin/payout') || url.pathname.startsWith('/api/admin/referral/') || url.pathname === '/api/admin/stats') {
        const workerPath = url.pathname.replace('/api/admin', '/admin');
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const proxyHeaders = new Headers(request.headers);
        proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');
        const resp = await fetch(new Request(workerUrl, {
          method: request.method, headers: proxyHeaders,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
        }));
        const respHeaders = new Headers(resp.headers);
        respHeaders.set('Access-Control-Allow-Origin', '*');
        return new Response(resp.body, { status: resp.status, headers: respHeaders });
      }
      // Admin referral endpoints → referrals-api Worker (D1)
      if (url.pathname.startsWith('/api/admin/affiliat') || url.pathname.startsWith('/api/admin/payout') || url.pathname.startsWith('/api/admin/referral/') || url.pathname === '/api/admin/stats') {
        const workerPath = url.pathname.replace('/api/admin', '/admin');
        const proxyHeaders = new Headers(request.headers);
        proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');
        const workerUrl = `https://referrals-api.in0v8.workers.dev${workerPath}${url.search}`;
        const resp = await fetch(new Request(workerUrl, {
          method: request.method, headers: proxyHeaders,
          body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
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
