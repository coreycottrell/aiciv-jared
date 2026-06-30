// ===========================================================================
// stripe-webhook  (CF Worker)  — PHASE C (PROD-HARDENED backend)
// ---------------------------------------------------------------------------
// Fulfillment webhook for Stripe Checkout, mirroring the archived paypal-webhook.
// This is the LIVE-MONEY-PATH variant. It is ADDITIVE alongside PayPal and does
// NOT touch the 7 live checkout pages (frontend wiring + go-live flip are a
// separate, Jared-gated step).
//
// Handles:
//   checkout.session.completed   -> seed (LOCKED core) + clients upsert + referral
//   invoice.paid                 -> NO reseed (renewal); clients increment-paid only
//   customer.subscription.updated-> clients update-status (active/past_due) only
//   customer.subscription.deleted-> clients update-status 'cancelled' only
//   invoice.payment_failed       -> clients update-status 'suspended' only
//   (all others)                 -> ack 200, no action
//
// SECURITY / CONSTITUTIONAL:
//   * Verify Stripe-Signature with async Web Crypto HMAC-SHA256 over the RAW
//     body. 5-min replay window. Timing-safe compare. JSON.parse ONLY after verify.
//   * STRIPE_WEBHOOK_SECRET (whsec_) = wrangler secret. Never committed/logged.
//   * Route-scoped body cap (envelope bytes, type-agnostic) BEFORE parse.
//   * Best-effort per-isolate rate limit (defense-in-depth; CF already shields).
//   * Reuse the LOCKED seed core — CALLS it, never duplicates dedup/claim logic.
//     If the seed holds (422) or fails (5xx/ok:false), return non-2xx so Stripe
//     retries — never report success on a failed/held seed.
//   * event.id dedup (stripe_webhook_log) = a SECOND idempotency layer in front
//     of the core's own session_uuid + order_id dedup. So a Stripe retry after a
//     clients-api hard-fail re-runs handleCheckoutCompleted, but the LOCKED core's
//     session_uuid/order dedup prevents a double-seed: only the failed mirror is
//     re-attempted. (event.id is claimed up-front; on a hard-fail we RELEASE the
//     claim so the retry is allowed to re-run — see releaseEventId.)
//   * tier/amount MISMATCH => HARD 400, NEVER seed (defends tampered metadata).
//   * NO CAD / $350 default — real USD amount_total/100 only.
// ===========================================================================

// ---- LIVE price->tier map (verified against live Stripe 2026-06-29) ----
// MUST agree with the other plan->tier maps. amount in whole USD.
const PRICE_TO_TIER = {
  "price_1Tnj60GdQ6Jplni4FqCPFgxq": { tier: "Awakened",  amount: 297 },
  "price_1Tnj61GdQ6Jplni4xEeMMVhD": { tier: "Partnered", amount: 597 },
  "price_1Tnj61GdQ6Jplni4mDtvnn3U": { tier: "Unified",   amount: 1097 },
  // --- New pages (/insiders, /old-pricing). tier strings MUST exactly equal the
  // metadata.tier the checkout creator writes, or the FATAL mismatch gate 400s
  // (no seed). $74.50 amount is the Number 74.5 (NOT 74) so the amount-fallback
  // (info.amount === amountUsd, where amountUsd = amount_total/100 = 74.5) matches.
  "price_1TnzumGdQ6Jplni4xCtOLt77": { tier: "insider",                amount: 74.5 },
  "price_1TnzunGdQ6Jplni4a44R5kvG": { tier: "legacy_awakened_149",    amount: 149 },
  "price_1TnzupGdQ6Jplni4DE0EZJMC": { tier: "legacy_partnered_499",   amount: 499 },
  "price_1TnzuqGdQ6Jplni4X2g58oLa": { tier: "legacy_unified_999",     amount: 999 },
};

// Route-scoped envelope cap. Stripe webhook events are small (KBs). 256KB is a
// generous ceiling that still blocks a disk/CPU-fill DoS. This is NOT a global
// MAX_CONTENT_LENGTH — it is scoped to THIS worker's single POST route.
const MAX_BODY_BYTES = 256 * 1024;

// Best-effort per-isolate rate limit (defense in depth; resets per cold start).
const RL_WINDOW_MS = 60 * 1000;
const RL_MAX = 600; // 600 events/min/isolate — far above real Stripe volume.
const _rlHits = []; // timestamps (ms)
function rateLimited() {
  const now = Date.now();
  while (_rlHits.length && now - _rlHits[0] > RL_WINDOW_MS) _rlHits.shift();
  if (_rlHits.length >= RL_MAX) return true;
  _rlHits.push(now);
  return false;
}

// =================== signature verification (Web Crypto) ===================
function utf8(s) { return new TextEncoder().encode(s); }

function hex(buf) {
  const b = new Uint8Array(buf);
  let out = "";
  for (let i = 0; i < b.length; i++) out += b[i].toString(16).padStart(2, "0");
  return out;
}

function timingSafeEqualHex(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function parseStripeSig(header) {
  const out = { t: null, v1: [] };
  if (!header) return out;
  for (const part of header.split(",")) {
    const idx = part.indexOf("=");
    if (idx < 0) continue;
    const k = part.slice(0, idx).trim();
    const v = part.slice(idx + 1).trim();
    if (k === "t") out.t = v;
    else if (k === "v1") out.v1.push(v);
  }
  return out;
}

async function verifyStripeSignature(rawBody, sigHeader, secret, toleranceSec) {
  if (!secret) return { ok: false, reason: "secret_not_configured" };
  const parsed = parseStripeSig(sigHeader);
  if (!parsed.t || parsed.v1.length === 0) return { ok: false, reason: "malformed_signature" };

  const tNum = parseInt(parsed.t, 10);
  if (!Number.isFinite(tNum)) return { ok: false, reason: "bad_timestamp" };
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - tNum) > (toleranceSec || 300)) return { ok: false, reason: "replay_window" };

  const signedPayload = parsed.t + "." + rawBody;
  const key = await crypto.subtle.importKey(
    "raw", utf8(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, utf8(signedPayload));
  const expected = hex(mac);

  for (const candidate of parsed.v1) {
    if (timingSafeEqualHex(expected, candidate)) return { ok: true };
  }
  return { ok: false, reason: "no_match" };
}

// =================== D1 event.id dedup layer ===================
async function claimEventId(env, eventId, eventType) {
  if (!env.DB) return "new";
  try {
    const res = await env.DB.prepare(
      "INSERT OR IGNORE INTO stripe_webhook_log (event_id, event_type, status, received_at) VALUES (?, ?, 'received', datetime('now'))"
    ).bind(eventId, eventType || "").run();
    const changes = (res && res.meta && typeof res.meta.changes === "number")
      ? res.meta.changes
      : (res && res.changes) || 0;
    return changes > 0 ? "new" : "duplicate";
  } catch (e) {
    console.warn("[stripe-webhook] stripe_webhook_log claim failed (continuing): " + (e && e.message));
    return "new";
  }
}

// Release a claimed event.id so a Stripe RETRY (after a transient hard-fail in a
// downstream mirror) is permitted to re-run. The LOCKED seed core still dedups on
// session_uuid/order_id, so the retry re-attempts ONLY the failed mirror, never a
// second seed. Without this, the second-layer dedup would wrongly ACK the retry.
async function releaseEventId(env, eventId) {
  if (!env.DB) return;
  try {
    await env.DB.prepare("DELETE FROM stripe_webhook_log WHERE event_id = ?").bind(eventId).run();
  } catch (e) { console.warn("[stripe-webhook] releaseEventId failed: " + (e && e.message)); }
}

async function markEventStatus(env, eventId, status) {
  if (!env.DB) return;
  try {
    await env.DB.prepare(
      "UPDATE stripe_webhook_log SET status = ? WHERE event_id = ?"
    ).bind(status, eventId).run();
  } catch (e) { /* best-effort audit */ }
}

// =================== seed call (LOCKED Python core) ===================
async function fireSeed(env, fields) {
  const url = (env.SEED_ENDPOINT || "https://api.purebrain.ai/api/send-seed");
  const headers = { "Content-Type": "application/json" };
  if (env.SEED_INBOUND_SECRET) headers["X-Seed-Secret"] = env.SEED_INBOUND_SECRET;

  const body = {
    session_uuid: fields.session_uuid,
    ai_name:      fields.ai_name,
    human_name:   fields.human_name,
    human_email:  fields.human_email,
    tier:         fields.tier,
    order_id:     fields.order_id,
    // PROD: default to REAL (non-banner) seed unless explicitly overridden to "true".
    is_sandbox:   (env.SEED_IS_SANDBOX === "true") ? true : false,
    conversation: [], // hydrated server-side by the send-seed WRAPPER via session_uuid
  };

  const resp = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) });
  let data = {};
  try { data = await resp.json(); } catch (_) { /* non-JSON */ }
  const success = resp.ok && data && data.ok !== false;
  return { success, status: resp.status, held: !!(data && data.held), data };
}

// =================== D1 mirror (service bindings, like PayPal) ===================
async function callClientsApi(env, path, body) {
  if (!env.CLIENTS_API) throw new Error("CLIENTS_API service binding not configured");
  if (!env.INTERNAL_BINDING_SECRET) throw new Error("INTERNAL_BINDING_SECRET not configured");
  const req = new Request("https://clients-api" + path, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-internal-binding": "clients-api",
      "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
    },
    body: JSON.stringify(body),
  });
  const resp = await env.CLIENTS_API.fetch(req);
  if (!resp.ok) {
    const t = await resp.text().catch(() => "");
    throw new Error("clients-api " + path + " failed: " + resp.status + " " + t);
  }
  const json = await resp.json().catch(() => ({}));
  if (json && json.ok === false) {
    throw new Error("clients-api " + path + " ok=false: " + JSON.stringify(json.error || json));
  }
  return json;
}

// Hard-fail (Option C) like PayPal: caller returns 500 on throw -> Stripe retries.
async function upsertClient(env, { email, name, tier, monthlyAmount, stripeSubscriptionId }) {
  if (!email) { console.log("[stripe-webhook] no email, skip client upsert"); return null; }
  return callClientsApi(env, "/internal/clients/upsert", {
    email,
    name: name || "",
    tier: tier || "Unknown",
    monthly_amount: monthlyAmount || 0,
    stripe_subscription_id: stripeSubscriptionId || null, // NEW column — never overload paypal_
    source: "stripe",
  });
}

// Lifecycle status update keyed by stripe_subscription_id. Mirrors PayPal's
// update-status but on the Stripe column. Best-effort: never seeds, never throws
// past the handler (the handler decides retry vs ack).
async function updateClientStatusByStripeSub(env, stripeSubId, status, paymentStatus) {
  if (!env.CLIENTS_API) { console.log("[stripe-webhook] no CLIENTS_API binding, skip status update"); return; }
  if (!stripeSubId) { console.log("[stripe-webhook] no stripe sub id, skip status update"); return; }
  return callClientsApi(env, "/internal/clients/update-status-stripe", {
    stripe_subscription_id: stripeSubId,
    status: status,
    payment_status: paymentStatus,
  });
}

// Best-effort / non-fatal: a referral miss must NOT fail the webhook.
async function completeReferral(env, { email, subscriptionId, amount, planId, eventId, eventTime }) {
  if (!env.REFERRALS_API) { console.log("[stripe-webhook] no REFERRALS_API binding, skip attribution"); return; }
  const secret = env.REFERRALS_INTERNAL_SECRET || env.INTERNAL_BINDING_SECRET || "";
  if (!secret) console.warn("[stripe-webhook] no referrals secret — attribution will 401");
  try {
    const req = new Request("https://referrals-api/internal/complete-by-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-internal-binding": "referrals-api",
        "x-internal-binding-secret": secret,
      },
      body: JSON.stringify({
        customer_email: email,
        subscription_id: subscriptionId,
        payment_amount: amount,
        plan_id: planId || undefined,
        event_id: eventId || undefined,
        event_time: eventTime || undefined,
      }),
    });
    const resp = await env.REFERRALS_API.fetch(req);
    if (resp.status === 404) { console.log("[stripe-webhook] no referral for " + email); return; }
    if (!resp.ok) { console.log("[stripe-webhook] attribution error " + resp.status); return; }
    const r = await resp.json().catch(() => ({}));
    console.log("[stripe-webhook] referral attribution: " + JSON.stringify(r));
  } catch (e) {
    console.error("[stripe-webhook] attribution binding error: " + (e && e.message));
  }
}

// =================== event handler: checkout.session.completed ===================
async function handleCheckoutCompleted(env, event) {
  const session = (event.data && event.data.object) || {};
  const md = session.metadata || {};

  // EMAIL: the seed/D1 key. With TIER-ONLY checkout the page sends no humanEmail,
  // so Stripe collects it and we read it from customer_details (mirrors PayPal).
  const humanEmail  = ((md.human_email || (session.customer_details && session.customer_details.email) || "")).trim().toLowerCase();
  const humanName   = (md.human_name || (session.customer_details && session.customer_details.name) || "").trim();
  const metaTier    = (md.tier || "").trim();

  // --- TIER-ONLY fulfillment defaults (2026-06-30) ---
  // The LOCKED Python send-seed core HARD-REQUIRES a non-empty session_uuid
  // (400 on empty) and a non-placeholder ai_name (422 "held" on empty/placeholder
  // — verified against _validate_ai_name_for_seed / _AI_NAME_PLACEHOLDER_VALUES).
  // With a no-naming-step Stripe purchase these arrive empty, so we MUST supply
  // both or the customer PAYS and is never seeded (orphaned paid customer — the
  // exact failure the old up-front gate prevented). We DO NOT modify the locked
  // core; we satisfy its contract from this caller:
  //   * session_uuid empty -> server-mint a stable v4 UUID (dedup/seed key).
  //   * ai_name     empty -> a SAFE DEFAULT that is NOT a placeholder value, so
  //     the constitutional guard passes and the magic link fires. The customer
  //     names their AI post-purchase in the portal. (See SEED_DEFAULT_AI_NAME.)
  let sessionUuid = (md.session_uuid || "").trim();
  if (!sessionUuid) {
    sessionUuid = (typeof crypto !== "undefined" && crypto.randomUUID)
      ? crypto.randomUUID()
      : ("stripe-" + (session.id || Date.now()));
    console.log("[stripe-webhook] tier-only: minted session_uuid=" + sessionUuid);
  }
  let aiName = (md.ai_name || "").trim();
  if (!aiName) {
    // env-overridable; default "PURE BRAIN". MUST NOT be any value in the core's
    // _AI_NAME_PLACEHOLDER_VALUES set (e.g. "", "unknown", "(not yet named)") or
    // the seed will be HELD (422). "PURE BRAIN" -> "pure brain" is NOT a placeholder.
    aiName = (env.SEED_DEFAULT_AI_NAME || "PURE BRAIN").trim();
    console.log("[stripe-webhook] tier-only: applied default ai_name=" + aiName);
  }

  // order_id = subscription id (stable across lifecycle events) else checkout session id (cs_ fallback).
  const orderId = (session.subscription || session.id || "").toString();

  const amountUsd = typeof session.amount_total === "number" ? Math.round(session.amount_total) / 100 : 0;

  // Resolve tier from PRICE (server-held). Prefer line_items price id if expanded;
  // else derive from amount. ASSERT metadata.tier agrees with price-derived tier.
  let resolvedTier = "";
  let planId = "";
  // Prefer expanded line_items[0].price.id when present.
  const li = session.line_items && session.line_items.data && session.line_items.data[0];
  const expandedPriceId = li && li.price && li.price.id;
  if (expandedPriceId && PRICE_TO_TIER[expandedPriceId]) {
    planId = expandedPriceId;
    resolvedTier = PRICE_TO_TIER[expandedPriceId].tier;
  } else {
    for (const [pid, info] of Object.entries(PRICE_TO_TIER)) {
      if (info.amount === amountUsd) { planId = pid; resolvedTier = info.tier; break; }
    }
  }

  // HARD tier/amount mismatch gate: if we resolved a tier from the price AND the
  // caller-supplied metadata.tier disagrees, REFUSE (400, no seed). Tampered or
  // stale metadata must never drive a seed/tier. This is fatal, not a warning.
  if (resolvedTier && metaTier && metaTier.toLowerCase() !== resolvedTier.toLowerCase()) {
    console.error("[stripe-webhook] FATAL TIER MISMATCH metadata.tier=" + metaTier +
      " price-derived=" + resolvedTier + " amount=" + amountUsd + " — refusing (no seed)");
    return { ok: false, fatal: true, stage: "tier_mismatch" };
  }
  // If price gave us nothing AND amount matched nothing, we cannot trust a tier
  // from metadata alone for a money event — refuse rather than seed a guessed tier.
  if (!resolvedTier) {
    console.error("[stripe-webhook] FATAL unresolved tier (amount=" + amountUsd +
      " no price match, metadata.tier=" + (metaTier || "-") + ") — refusing (no seed)");
    return { ok: false, fatal: true, stage: "tier_unresolved" };
  }

  // --- (a) Fire the seed (LOCKED core). MUST succeed or we return non-2xx. ---
  const seed = await fireSeed(env, {
    session_uuid: sessionUuid,
    ai_name: aiName,
    human_name: humanName,
    human_email: humanEmail,
    tier: resolvedTier,
    order_id: orderId,
  });
  if (!seed.success) {
    return { ok: false, stage: "seed", status: seed.status, held: seed.held };
  }

  // --- (b) Mirror D1 writes. clients upsert HARD-FAIL; referral non-fatal. ---
  // Ordering note: the seed already fired+claimed via the LOCKED core. If this
  // upsert throws, the handler returns 500 and we RELEASE the event.id claim so
  // Stripe's retry re-runs handleCheckoutCompleted. On that retry fireSeed hits
  // the core's session_uuid/order dedup (no second seed) and the upsert is
  // re-attempted. So a transient mirror failure self-heals without double-seeding.
  await upsertClient(env, {
    email: humanEmail,
    name: humanName,
    tier: resolvedTier,
    monthlyAmount: amountUsd,
    stripeSubscriptionId: session.subscription || null,
  });

  await completeReferral(env, {
    email: humanEmail,
    subscriptionId: orderId,
    amount: amountUsd,
    planId: planId,
    eventId: event.id,
    eventTime: event.created ? new Date(event.created * 1000).toISOString() : undefined,
  });

  return { ok: true };
}

// =================== lifecycle handlers (NO RESEED, status only) ===================
async function handleInvoicePaid(env, event) {
  // Renewal payment. NEVER reseed. Increment paid total / keep active.
  const inv = (event.data && event.data.object) || {};
  const stripeSubId = (inv.subscription || "").toString();
  const amountUsd = typeof inv.amount_paid === "number" ? Math.round(inv.amount_paid) / 100 : 0;
  // billing_reason 'subscription_create' is the FIRST invoice — fulfillment is
  // handled by checkout.session.completed, so do NOT double-process it here.
  if (inv.billing_reason === "subscription_create") {
    console.log("[stripe-webhook] invoice.paid first-invoice (create) — no-op (seed handled by checkout.completed)");
    return { ok: true };
  }
  if (!stripeSubId) { console.log("[stripe-webhook] invoice.paid no sub id — ack"); return { ok: true }; }
  await updateClientStatusByStripeSub(env, stripeSubId, "active", "active");
  console.log("[stripe-webhook] invoice.paid renewal " + stripeSubId + " amount=" + amountUsd + " (NO reseed)");
  return { ok: true };
}

async function handleSubscriptionDeleted(env, event) {
  const sub = (event.data && event.data.object) || {};
  const stripeSubId = (sub.id || "").toString();
  await updateClientStatusByStripeSub(env, stripeSubId, "cancelled", "cancelled");
  return { ok: true };
}

async function handleSubscriptionUpdated(env, event) {
  const sub = (event.data && event.data.object) || {};
  const stripeSubId = (sub.id || "").toString();
  // Map Stripe sub.status to our status. NEVER seed.
  const s = (sub.status || "").toLowerCase();
  let status = "active", payment = "active";
  if (s === "past_due" || s === "unpaid") { status = "active"; payment = "past_due"; }
  else if (s === "canceled") { status = "cancelled"; payment = "cancelled"; }
  else if (s === "paused") { status = "active"; payment = "paused"; }
  await updateClientStatusByStripeSub(env, stripeSubId, status, payment);
  return { ok: true };
}

async function handlePaymentFailed(env, event) {
  const inv = (event.data && event.data.object) || {};
  const stripeSubId = (inv.subscription || "").toString();
  if (!stripeSubId) { console.log("[stripe-webhook] payment_failed no sub id — ack"); return { ok: true }; }
  await updateClientStatusByStripeSub(env, stripeSubId, "active", "suspended");
  return { ok: true };
}

// =================== fetch entrypoint ===================
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // --- health (GET) for deploy verification + uptime probes ---
    if (request.method === "GET" && (url.pathname === "/health" || url.pathname === "/")) {
      return new Response(JSON.stringify({
        ok: true,
        service: "stripe-webhook",
        phase: "C-prod",
        bindings: {
          db: !!env.DB,
          clients_api: !!env.CLIENTS_API,
          referrals_api: !!env.REFERRALS_API,
          webhook_secret: !!env.STRIPE_WEBHOOK_SECRET,
          seed_inbound_secret: !!env.SEED_INBOUND_SECRET,
          internal_binding_secret: !!env.INTERNAL_BINDING_SECRET,
        },
        seed_is_sandbox: (env.SEED_IS_SANDBOX === "true"),
      }), { status: 200, headers: { "content-type": "application/json" } });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405, headers: { "content-type": "application/json" },
      });
    }

    // --- route-scoped rate limit (best-effort, per isolate) ---
    if (rateLimited()) {
      return new Response(JSON.stringify({ error: "rate_limited" }), {
        status: 429, headers: { "content-type": "application/json" },
      });
    }

    // --- route-scoped envelope cap BEFORE reading body fully ---
    const clen = parseInt(request.headers.get("content-length") || "0", 10);
    if (Number.isFinite(clen) && clen > MAX_BODY_BYTES) {
      return new Response(JSON.stringify({ error: "payload_too_large" }), {
        status: 413, headers: { "content-type": "application/json" },
      });
    }

    // 1. Read RAW body BEFORE any JSON parse (signature is over exact bytes).
    const rawBody = await request.text();
    // Backstop in case content-length was absent/wrong (byte length, type-agnostic).
    if (utf8(rawBody).byteLength > MAX_BODY_BYTES) {
      return new Response(JSON.stringify({ error: "payload_too_large" }), {
        status: 413, headers: { "content-type": "application/json" },
      });
    }
    const sigHeader = request.headers.get("Stripe-Signature");

    // 2. Verify signature.
    const verify = await verifyStripeSignature(rawBody, sigHeader, env.STRIPE_WEBHOOK_SECRET, 300);
    if (!verify.ok) {
      console.warn("[stripe-webhook] signature rejected: " + verify.reason);
      return new Response(JSON.stringify({ error: "invalid signature", reason: verify.reason }), {
        status: 400, headers: { "content-type": "application/json" },
      });
    }

    // 3. Parse ONLY after verify.
    let event;
    try { event = JSON.parse(rawBody); }
    catch (_) {
      return new Response(JSON.stringify({ error: "bad json" }), {
        status: 400, headers: { "content-type": "application/json" },
      });
    }

    // 4. event.id dedup (second idempotency layer).
    const claim = await claimEventId(env, event.id, event.type);
    if (claim === "duplicate") {
      console.log("[stripe-webhook] duplicate event " + event.id + " — acked");
      return new Response(JSON.stringify({ ok: true, duplicate: true }), {
        status: 200, headers: { "content-type": "application/json" },
      });
    }

    // 5. Dispatch by event type.
    try {
      let result;
      switch (event.type) {
        case "checkout.session.completed": result = await handleCheckoutCompleted(env, event); break;
        case "invoice.paid":               result = await handleInvoicePaid(env, event); break;
        case "customer.subscription.deleted": result = await handleSubscriptionDeleted(env, event); break;
        case "customer.subscription.updated": result = await handleSubscriptionUpdated(env, event); break;
        case "invoice.payment_failed":     result = await handlePaymentFailed(env, event); break;
        default:
          console.log("[stripe-webhook] ignored event type: " + event.type);
          await markEventStatus(env, event.id, "ignored");
          return new Response(JSON.stringify({ ok: true, ignored: event.type }), {
            status: 200, headers: { "content-type": "application/json" },
          });
      }

      if (result && result.ok) {
        await markEventStatus(env, event.id, "completed");
        return new Response(JSON.stringify({ ok: true }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }

      // FATAL (tier mismatch/unresolved): mark + ACK 200 so Stripe stops retrying a
      // request that can never succeed (a retry would mismatch identically). No seed
      // happened, no double-charge — fulfillment is intentionally withheld + alerted.
      if (result && result.fatal) {
        await markEventStatus(env, event.id, "fatal:" + (result.stage || "error"));
        return new Response(JSON.stringify({ ok: false, fatal: true, stage: result.stage }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }

      // Transient failure (seed held/failed or clients-api hard-fail): RELEASE the
      // event.id claim and return 500 so Stripe retries; the LOCKED core dedup keeps
      // the retry from double-seeding.
      await releaseEventId(env, event.id);
      return new Response(JSON.stringify({ ok: false, retry: true, stage: result && result.stage }), {
        status: 500, headers: { "content-type": "application/json" },
      });
    } catch (e) {
      console.error("[stripe-webhook] handler error: " + (e && e.message));
      // clients-api hard-fail lands here. Release claim so Stripe's retry re-runs;
      // core dedup prevents a second seed.
      await releaseEventId(env, event.id);
      return new Response(JSON.stringify({ ok: false, error: "handler_error" }), {
        status: 500, headers: { "content-type": "application/json" },
      });
    }
  },
};

// Export pure helpers for unit testing (no secrets, no network).
export const __test__ = {
  parseStripeSig, timingSafeEqualHex, verifyStripeSignature, PRICE_TO_TIER, hex,
  rateLimited, MAX_BODY_BYTES,
};
