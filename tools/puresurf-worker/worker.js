/**
 * PureSurf API Proxy Worker
 *
 * Proxies HTTPS requests from purebrain.ai/api/surf/* to the BaaS server
 * at http://157.180.69.225:8901/* — solving the mixed-content block.
 *
 * Route: purebrain.ai/api/surf/*
 * Example: /api/surf/health -> http://157.180.69.225:8901/health
 */

// Use DNS hostname instead of raw IP — CF Workers block direct IP fetch
const BACKEND = 'http://baas-origin.purebrain.ai:8901';

const ALLOWED_ORIGINS = [
  'https://purebrain.ai',
  'https://www.purebrain.ai',
  'https://puretechnology.nyc',
  'https://www.puretechnology.nyc',
  'https://surf.purebrain.ai',
];

function getCorsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-API-Key, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

export default {
  async fetch(request) {
    const CORS_HEADERS = getCorsHeaders(request);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    try {
      const url = new URL(request.url);

      // Strip /api/surf prefix to get the backend path
      // e.g. /api/surf/sessions/abc123/navigate -> /sessions/abc123/navigate
      const backendPath = url.pathname.replace(/^\/api\/surf/, '') || '/';
      const backendUrl = BACKEND + backendPath + url.search;

      // Build forwarded headers — pass through everything relevant
      const headers = new Headers();
      for (const [key, value] of request.headers) {
        // Skip hop-by-hop and CF-specific headers
        if (['host', 'cf-connecting-ip', 'cf-ray', 'cf-visitor', 'cf-worker',
             'cf-ipcountry', 'cdn-loop', 'x-forwarded-proto'].includes(key.toLowerCase())) {
          continue;
        }
        headers.set(key, value);
      }

      // Forward the client IP for logging on the backend
      headers.set('X-Forwarded-For', request.headers.get('cf-connecting-ip') || '');
      headers.set('X-Forwarded-Proto', 'https');

      // Build fetch options
      const fetchOpts = {
        method: request.method,
        headers,
      };

      // Forward body for methods that have one
      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
        fetchOpts.body = request.body;
      }

      // Proxy the request to the backend
      const response = await fetch(backendUrl, fetchOpts);

      // Build response with CORS headers
      const responseHeaders = new Headers(response.headers);
      for (const [key, value] of Object.entries(CORS_HEADERS)) {
        responseHeaders.set(key, value);
      }

      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });

    } catch (err) {
      return new Response(JSON.stringify({
        error: 'Proxy error',
        message: err.message,
      }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          ...CORS_HEADERS,
        },
      });
    }
  },
};
