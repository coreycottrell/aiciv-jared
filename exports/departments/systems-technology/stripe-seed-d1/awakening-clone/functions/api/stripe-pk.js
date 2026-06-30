// Cloudflare Pages Function: GET /api/stripe-pk
// Returns ONLY the Stripe PUBLISHABLE key (pk_*) for the frontend to init
// loadStripe(). The publishable key is, by Stripe design, safe to expose
// client-side. The secret key (sk_*) is NEVER served here.
//
// Configure via wrangler env: STRIPE_PUBLISHABLE_KEY (test pk for staging) with
// a STRIPE_PUBLISHABLE_KEY_LIVE fallback.
// ---- CORS (cross-origin money-path call) ----
// The standalone pricing pages live on https://purebrain.ai (apex) and
// https://www.purebrain.ai (www) but the Stripe endpoints are served from this
// awakening-clone CF Pages project, so the "Checkout with Stripe" fetch is
// cross-origin. The browser BLOCKS the response (hiding even the error body)
// unless Access-Control-Allow-Origin echoes the caller's Origin. We reflect a
// FIXED ALLOWLIST only (never "*", never credentials) — these endpoints
// intentionally serve the public purebrain.ai site and nothing else.
const CORS_ALLOWLIST = new Set([
  "https://purebrain.ai",
  "https://www.purebrain.ai",
]);

function corsHeaders(request, methods) {
  const origin = request.headers.get("Origin") || "";
  const h = {
    "Access-Control-Allow-Methods": methods,
    "Access-Control-Allow-Headers": "Content-Type, Accept",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
  // Echo the Origin ONLY when it is in the allowlist (so apex + www both work),
  // otherwise omit ACAO entirely and the browser blocks the cross-origin read.
  if (CORS_ALLOWLIST.has(origin)) {
    h["Access-Control-Allow-Origin"] = origin;
  }
  return h;
}

function json(body, status, request) {
  const headers = { "Content-Type": "application/json", "Cache-Control": "no-store" };
  if (request) Object.assign(headers, corsHeaders(request, "GET, OPTIONS"));
  return new Response(JSON.stringify(body), { status: status || 200, headers });
}

export async function onRequestOptions(context) {
  // Preflight: 204 + CORS headers (no body). Without this, OPTIONS hit the
  // method-not-allowed path and returned 405, failing the browser preflight.
  return new Response(null, { status: 204, headers: corsHeaders(context.request, "GET, OPTIONS") });
}

export async function onRequestGet(context) {
  const { env, request } = context;
  const pk = env.STRIPE_PUBLISHABLE_KEY || env.STRIPE_PUBLISHABLE_KEY_LIVE;
  if (!pk) {
    return json({ error: "Publishable key not configured." }, 500, request);
  }
  // Defensive: refuse to ever emit a secret key from this route.
  if (/^sk_/.test(pk)) {
    return json({ error: "Misconfigured: secret key in publishable slot." }, 500, request);
  }
  return json({ pk }, 200, request);
}

export async function onRequest(context) {
  if (context.request.method === "OPTIONS") return onRequestOptions(context);
  if (context.request.method === "GET") return onRequestGet(context);
  return json({ error: "Method not allowed. Use GET." }, 405, context.request);
}
