// Cloudflare Pages Function: POST /api/create-checkout-session
// ---------------------------------------------------------------------------
// Phase A (STAGING). Creates a Stripe Checkout Session in EMBEDDED ui_mode and
// returns { client_secret } so the frontend can mount Stripe Embedded Checkout
// in a modal/container over the awakening page (matches the PayPal modal UX).
//
// SECURITY:
//   * sk lives ONLY in env (a wrangler secret). NEVER returned to the client,
//     NEVER logged. Only the publishable key (pk_*) + the session client_secret
//     go client-side, and pk is served from a separate /api/stripe-pk route.
//   * price is SERVER-HELD (allowlist) — the client never sends an amount.
//
// IDENTITY METADATA (so the webhook can seed + write D1 with no page JS at
// fulfillment time) is written to BOTH session.metadata AND
// subscription_data.metadata. We VALIDATE the required identity fields here so a
// payable subscription can never be created that the webhook cannot seed.
// ---------------------------------------------------------------------------

// Existing LIVE prices (mirror of PayPal tiers). For STAGING you may override
// each via env (STRIPE_PRICE_AWAKENED / _PARTNERED / _UNIFIED) with TEST price
// ids; the literals below are the documented LIVE fallback.
function priceByTier(env) {
  return {
    awakened:  env.STRIPE_PRICE_AWAKENED  || "price_1Tnj60GdQ6Jplni4FqCPFgxq", // $297
    partnered: env.STRIPE_PRICE_PARTNERED || "price_1Tnj61GdQ6Jplni4xEeMMVhD", // $597
    unified:   env.STRIPE_PRICE_UNIFIED   || "price_1Tnj61GdQ6Jplni4mDtvnn3U", // $1097
    // LIVE $1/month test tier (prod_UnNikRLpUBBtuz). Created 2026-06-29 to drive
    // a real-money $1 charge end-to-end through the SAME embedded checkout ->
    // checkout.session.completed webhook -> seed -> Witness -> magic link ->
    // /thank-you/ -> clients D1 (source=stripe) -> admin chain. metadata[tier]=test
    // flows through to the session + subscription metadata unchanged.
    test:      env.STRIPE_PRICE_TEST       || "price_1TnmxKGdQ6Jplni4LEVwWtc2", // $1
    // --- New pages (/insiders, /old-pricing). The tier KEY here is what the
    // frontend sends as body.tier (lowercased) AND what is written verbatim to
    // metadata[tier]; it MUST exactly equal the PRICE_TO_TIER.tier string in the
    // webhook so the FATAL mismatch gate passes. env-override pattern matches the
    // existing entries; LIVE literal fallback documented inline.
    insider:               env.STRIPE_PRICE_INSIDER          || "price_1TnzumGdQ6Jplni4xCtOLt77", // $74.50
    legacy_awakened_149:   env.STRIPE_PRICE_LEGACY_AWAKENED  || "price_1TnzunGdQ6Jplni4a44R5kvG", // $149
    legacy_partnered_499:  env.STRIPE_PRICE_LEGACY_PARTNERED || "price_1TnzupGdQ6Jplni4DE0EZJMC", // $499
    legacy_unified_999:    env.STRIPE_PRICE_LEGACY_UNIFIED   || "price_1TnzuqGdQ6Jplni4X2g58oLa", // $999
  };
}

// ---- CORS (cross-origin money-path call) ----
// The standalone pricing pages live on https://purebrain.ai (apex) and
// https://www.purebrain.ai (www) but this endpoint is served from the
// awakening-clone CF Pages project, so the "Checkout with Stripe" POST is
// cross-origin. The browser BLOCKS the response (hiding even the error body the
// page reads) unless Access-Control-Allow-Origin echoes the caller's Origin. We
// reflect a FIXED ALLOWLIST only (never "*", never credentials) — this endpoint
// intentionally serves the public purebrain.ai site.
const CORS_ALLOWLIST = new Set([
  "https://purebrain.ai",
  "https://www.purebrain.ai",
]);

function corsHeaders(request, methods) {
  const origin = (request && request.headers.get("Origin")) || "";
  const h = {
    "Access-Control-Allow-Methods": methods,
    "Access-Control-Allow-Headers": "Content-Type, Accept",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
  if (CORS_ALLOWLIST.has(origin)) {
    h["Access-Control-Allow-Origin"] = origin;
  }
  return h;
}

function json(body, status, request) {
  const headers = { "Content-Type": "application/json", "Cache-Control": "no-store" };
  if (request) Object.assign(headers, corsHeaders(request, "POST, OPTIONS"));
  return new Response(JSON.stringify(body), { status: status || 200, headers });
}

export async function onRequestOptions(context) {
  // Preflight: 204 + CORS headers (no body). Without this, OPTIONS fell through
  // to method-not-allowed (405) and failed the browser preflight before the POST.
  return new Response(null, { status: 204, headers: corsHeaders(context.request, "POST, OPTIONS") });
}

function isEmail(s) {
  return typeof s === "string" && s.includes("@") && s.length <= 320;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  // sk is read from STRIPE_SECRET_KEY (test) with a documented live fallback.
  // For STAGING use a TEST key; if a live key is needed for embedded session
  // creation, STRIPE_SECRET_KEY_LIVE is the fallback and the seed must be fired
  // with is_sandbox:true (see webhook).
  const sk = env.STRIPE_SECRET_KEY || env.STRIPE_SECRET_KEY_LIVE;
  if (!sk) {
    return json({ error: "Server not configured (missing Stripe secret)." }, 500, request);
  }

  let body;
  try {
    const ct = request.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      return json({ error: "Content-Type must be application/json" }, 400, request);
    }
    body = await request.json();
  } catch (_) {
    return json({ error: "Invalid JSON" }, 400, request);
  }

  // ---- TIER-ONLY checkout (cold-load card button) ----
  // 2026-06-30: Relaxed to mirror the PayPal cold-load path. A bare {tier} now
  // mints a session so "Checkout with Stripe" works on first paint with NO
  // pre-form / naming step / identity fields. The ONLY hard requirement is a
  // tier in the server-held allowlist (price is never client-supplied).
  //
  // Stripe's hosted/embedded checkout collects the customer email itself; we do
  // NOT pre-set customer_email (it would require the now-optional humanEmail).
  // The webhook reads the email from session.customer_details.email at
  // fulfillment, exactly like PayPal reads the PayPal-collected email.
  //
  // aiName / humanEmail / sessionUuid are now OPTIONAL pass-throughs: the
  // existing embedded *awakening* flow that DOES collect them still threads them
  // into metadata, but their absence no longer 400s the cold-load tier-only call.
  const tier      = String(body.tier || "").toLowerCase().trim();
  const aiName    = String(body.aiName || "").trim();
  const humanName = String(body.humanName || "").trim();
  const humanEmail = String(body.humanEmail || "").trim();
  const sessionUuid = String(body.sessionUuid || "").trim();
  // ref_code optional; pass through uppercased or empty.
  const refCode   = String(body.refCode || "").trim().toUpperCase();

  const PRICE_BY_TIER = priceByTier(env);
  const price = PRICE_BY_TIER[tier];
  if (!price) {
    // KEPT: unknown/missing tier is still a hard 400 (security-critical — the
    // tier drives the price + the webhook's FATAL tier/amount mismatch gate).
    return json({ error: "Unknown or missing tier." }, 400, request);
  }

  // Return URL = thank-you contract (exact param names confirmed in
  // thank-you/index.html). In STAGING this may point at a staging clone; the
  // {CHECKOUT_SESSION_ID} placeholder is filled by Stripe.
  const returnBase = env.THANK_YOU_BASE || "https://purebrain.ai/thank-you/";
  const sep = returnBase.includes("?") ? "&" : "?";
  const returnUrl =
    returnBase + sep +
    "aiName=" + encodeURIComponent(aiName) +
    "&name=" + encodeURIComponent(humanName) +
    "&email=" + encodeURIComponent(humanEmail) +
    "&tier=" + encodeURIComponent(tier) +
    "&session_id={CHECKOUT_SESSION_ID}";

  // ---- Build the Stripe Checkout Session (embedded ui_mode) ----
  // NOTE (2026-06-29, E2E): the account's current Stripe API version renamed the
  // embedded ui_mode value from "embedded" to "embedded_page". The JS
  // s.initEmbeddedCheckout({clientSecret}) mount is the embedded-page method and
  // pairs with this value. Stripe returned an explicit error on "embedded".
  const form = new URLSearchParams();
  form.set("ui_mode", "embedded_page");
  form.set("mode", "subscription");
  form.set("line_items[0][price]", price);
  form.set("line_items[0][quantity]", "1");
  form.set("return_url", returnUrl);
  form.set("billing_address_collection", "auto");
  // EMAIL COLLECTION: do NOT force customer_email here. With tier-only cold load
  // there is no humanEmail to pre-set; pre-setting "" would suppress Stripe's own
  // email field. Letting Stripe's hosted/embedded checkout collect the email is
  // exactly how PayPal works (we read it from session.customer_details.email in
  // the webhook). Only pre-fill when an email WAS supplied by the awakening flow.
  if (isEmail(humanEmail)) {
    form.set("customer_email", humanEmail);
  }

  // Identity metadata on the SESSION (read by checkout.session.completed).
  // source + tier are ALWAYS written (tier is required by the webhook's FATAL
  // tier/amount mismatch gate). The remaining identity fields are written ONLY
  // when present, so the embedded awakening flow that DOES collect them keeps
  // working, while the tier-only cold-load path simply omits them (the webhook
  // server-mints a session_uuid + applies a safe default ai_name on empty).
  const md = { source: "stripe", tier: tier };
  if (aiName)      md.ai_name = aiName;
  if (humanName)   md.human_name = humanName;
  if (isEmail(humanEmail)) md.human_email = humanEmail;
  if (sessionUuid) md.session_uuid = sessionUuid;
  if (refCode)     md.ref_code = refCode;
  for (const [k, v] of Object.entries(md)) {
    form.set("metadata[" + k + "]", v);
    // ... and ALSO on the subscription so lifecycle events carry it (Phase B).
    form.set("subscription_data[metadata][" + k + "]", v);
  }

  let resp, data;
  try {
    resp = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + sk,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: form.toString(),
    });
    data = await resp.json();
  } catch (e) {
    return json({ error: "Stripe request failed." }, 502, request);
  }

  if (!resp.ok) {
    const msg = (data && data.error && data.error.message) || "Stripe error";
    return json({ error: msg }, resp.status, request);
  }

  // Embedded mode returns client_secret (NOT a redirect url).
  if (!data.client_secret) {
    return json({ error: "Stripe did not return a client_secret." }, 502, request);
  }

  // client_secret + id are client-facing redirect/mount tokens (safe). sk never
  // appears in this response.
  return json({ client_secret: data.client_secret, id: data.id }, 200, request);
}

export async function onRequest(context) {
  if (context.request.method === "OPTIONS") return onRequestOptions(context);
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ error: "Method not allowed. Use POST." }, 405, context.request);
}
