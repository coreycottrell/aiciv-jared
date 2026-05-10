/**
 * paypal-webhook Worker
 *
 * Receives PayPal subscription webhook events and auto-syncs client data
 * to the purebrain-social D1 database (clients table).
 *
 * D1 binding: env.DB = purebrain-social
 *
 * Endpoints:
 *   GET  /health              — health check
 *   POST /paypal/webhook      — PayPal webhook receiver
 *
 * Handled events:
 *   BILLING.SUBSCRIPTION.ACTIVATED    — new subscriber
 *   BILLING.SUBSCRIPTION.CANCELLED    — cancelled
 *   BILLING.SUBSCRIPTION.SUSPENDED    — payment failed
 *   BILLING.SUBSCRIPTION.RE-ACTIVATED — reactivated
 *   PAYMENT.SALE.COMPLETED            — recurring payment received
 */

// ---------------------------------------------------------------------------
// Plan -> Tier mapping
// ---------------------------------------------------------------------------

function resolveTier(planName, amount) {
  const name = (planName || "").toLowerCase();

  if (name.includes("insider") || amount === 74.5) return "Insiders";
  if (name.includes("awakened") || name.includes("purebrain ai") || amount === 149) return "Awakened";
  if (amount === 499) return "Partnered";
  if (amount === 999) return "Unified";

  // Fallback: guess from amount ranges
  if (amount > 0 && amount <= 100) return "Insiders";
  if (amount > 100 && amount <= 200) return "Awakened";
  if (amount > 200 && amount <= 600) return "Partnered";
  if (amount > 600) return "Unified";

  return "Unknown";
}

// ---------------------------------------------------------------------------
// Helpers: extract data from PayPal event payloads
// ---------------------------------------------------------------------------

function extractSubscriptionData(resource) {
  const subscriber = resource.subscriber || {};
  const name_obj = subscriber.name || {};
  const fullName = [name_obj.given_name, name_obj.surname].filter(Boolean).join(" ");
  const email = (subscriber.email_address || "").toLowerCase().trim();
  const subscriptionId = resource.id || null;
  const planName = (resource.plan_id || resource.plan?.name || "");

  // Amount: check billing_info or plan
  let amount = 0;
  if (resource.billing_info?.last_payment?.amount?.value) {
    amount = parseFloat(resource.billing_info.last_payment.amount.value);
  } else if (resource.plan?.billing_cycles) {
    const cycle = resource.plan.billing_cycles.find(c => c.tenure_type === "REGULAR");
    if (cycle?.pricing_scheme?.fixed_price?.value) {
      amount = parseFloat(cycle.pricing_scheme.fixed_price.value);
    }
  } else if (resource.shipping_amount?.value) {
    // fallback
    amount = parseFloat(resource.shipping_amount.value);
  }

  return { fullName, email, subscriptionId, planName, amount };
}

function extractSaleData(resource) {
  const amount = resource.amount?.total ? parseFloat(resource.amount.total) : 0;
  const subscriptionId = resource.billing_agreement_id || null;
  // Sale events don't always carry subscriber email directly
  // We use the billing_agreement_id to look up the existing client
  return { amount, subscriptionId };
}

// ---------------------------------------------------------------------------
// Client mutations — Service Binding to clients-api (P1.5)
// ---------------------------------------------------------------------------
//
// Constitutional: ALL writes to the `clients` table go through clients-api
// via Service Binding. No direct env.DB.prepare(...UPDATE clients...) here.
// (cf-service-binding-pattern skill, 2026-05-07; CTO P1.5 brief 2026-05-10.)
//
// The DB binding (env.DB → purebrain-social) remains for paypal_webhook_log
// and no_referral_log only. clients-table writes have been redirected to
// clients-api (env.CLIENTS_API → purebrain-clients DB).
//
// Error handling per CTO brief (Option C — hard-fail): on non-2xx from
// clients-api we throw. The webhook handler returns 500, and PayPal retries
// on its 24h exponential schedule. Better than silent loss.

async function callClientsApi(env, path, { method = "POST", body = null } = {}) {
  if (!env.CLIENTS_API) {
    throw new Error("CLIENTS_API service binding not configured");
  }
  if (!env.INTERNAL_BINDING_SECRET) {
    throw new Error("INTERNAL_BINDING_SECRET not configured");
  }

  const init = {
    method,
    headers: {
      "content-type": "application/json",
      "x-internal-binding": "clients-api",
      "x-internal-binding-secret": env.INTERNAL_BINDING_SECRET,
    },
  };
  if (body !== null) init.body = JSON.stringify(body);

  const req = new Request(`https://clients-api${path}`, init);
  const resp = await env.CLIENTS_API.fetch(req);

  if (!resp.ok) {
    const errText = await resp.text().catch(() => "");
    throw new Error(`clients-api ${path} failed: ${resp.status} ${errText}`);
  }

  const json = await resp.json().catch(() => ({}));
  if (json && json.ok === false) {
    throw new Error(`clients-api ${path} returned ok=false: ${JSON.stringify(json.error || json)}`);
  }
  return json;
}

async function upsertClient(env, { email, name, tier, monthlyAmount, subscriptionId }) {
  if (!email) {
    console.log("[paypal-webhook] No email in event, skipping upsert");
    return null;
  }

  const result = await callClientsApi(env, "/internal/clients/upsert", {
    method: "POST",
    body: {
      email,
      name: name || "",
      tier: tier || "Unknown",
      monthly_amount: monthlyAmount || 0,
      paypal_subscription_id: subscriptionId || null,
      source: "paypal",
    },
  });

  console.log(`[paypal-webhook] Upserted client via clients-api: ${email}, tier=${tier}, amount=${monthlyAmount}`);
  return result;
}

async function updateClientStatus(env, subscriptionId, status, paymentStatus) {
  if (!subscriptionId) {
    console.log("[paypal-webhook] No subscription ID, cannot update status");
    return null;
  }

  const result = await callClientsApi(env, "/internal/clients/update-status", {
    method: "POST",
    body: {
      paypal_subscription_id: subscriptionId,
      status,
      payment_status: paymentStatus,
    },
  });

  console.log(`[paypal-webhook] Updated status via clients-api for sub=${subscriptionId}: status=${status}, payment=${paymentStatus}, changes=${result?.data?.changes ?? 0}`);
  return result;
}

async function incrementTotalPaid(env, subscriptionId, amount) {
  if (!subscriptionId || !amount) {
    console.log("[paypal-webhook] Missing sub ID or amount for payment increment");
    return null;
  }

  const result = await callClientsApi(env, "/internal/clients/increment-paid", {
    method: "POST",
    body: {
      paypal_subscription_id: subscriptionId,
      amount,
    },
  });

  console.log(`[paypal-webhook] Incremented total_paid via clients-api by ${amount} for sub=${subscriptionId}, changes=${result?.data?.changes ?? 0}`);
  return result;
}

// ---------------------------------------------------------------------------
// Webhook verification (PayPal signature verification)
// ---------------------------------------------------------------------------

// OAuth token cache (in-memory, per isolate)
let cachedAccessToken = null;
let tokenExpiry = 0;

async function getPayPalAccessToken(env) {
  const now = Date.now();

  // Return cached token if still valid (5min TTL)
  if (cachedAccessToken && now < tokenExpiry) {
    return cachedAccessToken;
  }

  const clientId = env.PAYPAL_CLIENT_ID;
  const clientSecret = env.PAYPAL_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error("PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be configured");
  }

  const auth = btoa(`${clientId}:${clientSecret}`);
  const tokenUrl = env.PAYPAL_MODE === "live"
    ? "https://api-m.paypal.com/v1/oauth2/token"
    : "https://api-m.sandbox.paypal.com/v1/oauth2/token";

  const response = await fetch(tokenUrl, {
    method: "POST",
    headers: {
      "Authorization": `Basic ${auth}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`PayPal OAuth failed: ${error}`);
  }

  const data = await response.json();
  cachedAccessToken = data.access_token;
  tokenExpiry = now + (5 * 60 * 1000); // 5 min TTL

  return cachedAccessToken;
}

async function verifyWebhook(request, env, body) {
  const webhookId = env.WEBHOOK_ID;

  if (!webhookId) {
    console.log("[paypal-webhook] WARN: WEBHOOK_ID not configured, skipping verification");
    return true;
  }

  // Extract signature headers
  const transmissionId = request.headers.get("paypal-transmission-id");
  const transmissionTime = request.headers.get("paypal-transmission-time");
  const transmissionSig = request.headers.get("paypal-transmission-sig");
  const certUrl = request.headers.get("paypal-cert-url");
  const authAlgo = request.headers.get("paypal-auth-algo") || "SHA256withRSA";

  if (!transmissionId || !transmissionTime || !transmissionSig || !certUrl) {
    console.log("[paypal-webhook] ERROR: Missing required signature headers");
    return false;
  }

  try {
    const accessToken = await getPayPalAccessToken(env);
    const verifyUrl = env.PAYPAL_MODE === "live"
      ? "https://api-m.paypal.com/v1/notifications/verify-webhook-signature"
      : "https://api-m.sandbox.paypal.com/v1/notifications/verify-webhook-signature";

    const verifyPayload = {
      auth_algo: authAlgo,
      cert_url: certUrl,
      transmission_id: transmissionId,
      transmission_sig: transmissionSig,
      transmission_time: transmissionTime,
      webhook_id: webhookId,
      webhook_event: body, // Full event body
    };

    const verifyResponse = await fetch(verifyUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(verifyPayload),
    });

    if (!verifyResponse.ok) {
      const error = await verifyResponse.text();
      console.log(`[paypal-webhook] Signature verification failed: ${error}`);
      return false;
    }

    const verifyData = await verifyResponse.json();
    const isValid = verifyData.verification_status === "SUCCESS";

    console.log(`[paypal-webhook] Signature verification: ${isValid ? "VALID" : "INVALID"}`);
    return isValid;

  } catch (error) {
    console.error(`[paypal-webhook] Signature verification error: ${error.message}`);
    return false;
  }
}

// ---------------------------------------------------------------------------
// Idempotency: deduplicate by transmission ID (in-memory per isolate + D1)
// ---------------------------------------------------------------------------

// In-memory cache (per-isolate, cleared on cold start — that's fine, D1 is the
// durable store). Keeps last 500 transmission IDs.
const seenTransmissions = new Set();
const SEEN_MAX = 500;

async function isDuplicate(env, transmissionId) {
  if (!transmissionId) return false;

  // Fast path: in-memory check
  if (seenTransmissions.has(transmissionId)) {
    console.log(`[paypal-webhook] Duplicate (in-memory): ${transmissionId}`);
    return true;
  }

  // Slow path: D1 check
  try {
    const row = await env.DB.prepare(
      "SELECT 1 FROM paypal_webhook_log WHERE transmission_id = ?"
    ).bind(transmissionId).first();
    if (row) {
      seenTransmissions.add(transmissionId);
      console.log(`[paypal-webhook] Duplicate (D1): ${transmissionId}`);
      return true;
    }
  } catch (e) {
    // Table may not exist yet — that's OK, not a duplicate
    if (!e.message?.includes("no such table")) {
      console.log(`[paypal-webhook] D1 dedup check error: ${e.message}`);
    }
  }

  return false;
}

async function recordTransmission(env, transmissionId, eventType, status) {
  if (!transmissionId) return;

  // In-memory
  seenTransmissions.add(transmissionId);
  if (seenTransmissions.size > SEEN_MAX) {
    const first = seenTransmissions.values().next().value;
    seenTransmissions.delete(first);
  }

  // D1 (best effort — create table if needed)
  try {
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS paypal_webhook_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transmission_id TEXT UNIQUE NOT NULL,
        event_type TEXT,
        status TEXT DEFAULT 'processed',
        received_at TEXT DEFAULT (datetime('now'))
      )
    `).run();

    await env.DB.prepare(
      "INSERT OR IGNORE INTO paypal_webhook_log (transmission_id, event_type, status) VALUES (?, ?, ?)"
    ).bind(transmissionId, eventType, status).run();
  } catch (e) {
    console.log(`[paypal-webhook] D1 dedup write error: ${e.message}`);
  }
}

// ---------------------------------------------------------------------------
// Event handlers
// ---------------------------------------------------------------------------

async function handleSubscriptionActivated(env, resource) {
  const { fullName, email, subscriptionId, planName, amount } = extractSubscriptionData(resource);
  const tier = resolveTier(planName, amount);

  console.log(`[paypal-webhook] SUBSCRIPTION.ACTIVATED: email=${email}, name=${fullName}, tier=${tier}, amount=${amount}, sub=${subscriptionId}`);

  await upsertClient(env, {
    email,
    name: fullName,
    tier,
    monthlyAmount: amount,
    subscriptionId,
  });

  // Check for referral attribution via Service Binding
  // (with 60-second retry if pending row doesn't exist yet)
  await checkReferralAttribution(env, { email, subscriptionId, amount }, 0);

  return { action: "upserted", email, tier };
}

async function checkReferralAttribution(env, data, retryCount) {
  if (!env.REFERRALS_API) {
    console.log("[paypal-webhook] REFERRALS_API binding not available, skipping attribution");
    return;
  }

  const { email, subscriptionId, amount } = data;

  try {
    // Call referrals-api to complete attribution
    const attributionRequest = new Request("https://referrals-api/internal/complete-by-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_email: email,
        subscription_id: subscriptionId,
        payment_amount: amount,
      }),
    });

    const attributionResponse = await env.REFERRALS_API.fetch(attributionRequest);

    if (attributionResponse.status === 404) {
      // No referral found — retry once after 60 seconds
      if (retryCount === 0) {
        console.log(`[paypal-webhook] No referral found for ${email}, scheduling retry in 60s`);

        // Schedule a Durable Object alarm or use waitUntil + setTimeout
        // For now, use waitUntil with a Promise that resolves after 60s
        env.ctx?.waitUntil(
          new Promise(resolve => setTimeout(resolve, 60000)).then(async () => {
            console.log(`[paypal-webhook] Retry: checking referral attribution for ${email}`);
            await checkReferralAttribution(env, data, retryCount + 1);
          })
        );
      } else {
        console.log(`[paypal-webhook] No referral found for ${email} after retry`);
        // Write to no_referral_log for manual reconciliation
        await env.DB.prepare(`
          INSERT INTO paypal_webhook_log (transmission_id, event_type, status)
          VALUES (?, 'no_referral_after_retry', ?)
        `).bind(`${email}-${subscriptionId}`, JSON.stringify(data)).run();
      }
    } else if (!attributionResponse.ok) {
      const error = await attributionResponse.text();
      console.log(`[paypal-webhook] Attribution error: ${error}`);
    } else {
      const result = await attributionResponse.json();
      console.log(`[paypal-webhook] Referral attribution completed: ${JSON.stringify(result)}`);
    }
  } catch (error) {
    console.error(`[paypal-webhook] Service binding error (attribution): ${error.message}`);
  }
}

async function handleSubscriptionCancelled(env, resource) {
  const subscriptionId = resource.id;
  console.log(`[paypal-webhook] SUBSCRIPTION.CANCELLED: sub=${subscriptionId}`);

  await updateClientStatus(env, subscriptionId, "cancelled", "cancelled");
  return { action: "cancelled", subscriptionId };
}

async function handleSubscriptionSuspended(env, resource) {
  const subscriptionId = resource.id;
  console.log(`[paypal-webhook] SUBSCRIPTION.SUSPENDED: sub=${subscriptionId}`);

  // Keep status as-is (they're still a client), just mark payment as suspended.
  // Routed to clients-api per P1.5 (no direct env.DB write to clients).
  const result = await callClientsApi(env, "/internal/clients/suspend", {
    method: "POST",
    body: { paypal_subscription_id: subscriptionId },
  });

  console.log(`[paypal-webhook] Suspended via clients-api for sub=${subscriptionId}, changes=${result?.data?.changes ?? 0}`);
  return { action: "suspended", subscriptionId };
}

async function handleSubscriptionReactivated(env, resource) {
  const subscriptionId = resource.id;
  console.log(`[paypal-webhook] SUBSCRIPTION.RE-ACTIVATED: sub=${subscriptionId}`);

  await updateClientStatus(env, subscriptionId, "active", "active");
  return { action: "reactivated", subscriptionId };
}

async function handlePaymentCompleted(env, resource) {
  const { amount, subscriptionId } = extractSaleData(resource);
  console.log(`[paypal-webhook] PAYMENT.SALE.COMPLETED: sub=${subscriptionId}, amount=${amount}`);

  if (subscriptionId && amount > 0) {
    await incrementTotalPaid(env, subscriptionId, amount);
    return { action: "payment_recorded", subscriptionId, amount };
  }

  return { action: "payment_skipped", reason: "missing sub_id or zero amount" };
}

async function handleSubscriptionUpdated(env, resource) {
  const subscriptionId = resource.id;
  const planName = resource.plan_id || resource.plan?.name || "";

  // Extract old and new amounts to detect plan changes
  let oldAmount = 0;
  let newAmount = 0;

  // Current amount from billing_info
  if (resource.billing_info?.last_payment?.amount?.value) {
    newAmount = parseFloat(resource.billing_info.last_payment.amount.value);
  } else if (resource.plan?.billing_cycles) {
    const cycle = resource.plan.billing_cycles.find(c => c.tenure_type === "REGULAR");
    if (cycle?.pricing_scheme?.fixed_price?.value) {
      newAmount = parseFloat(cycle.pricing_scheme.fixed_price.value);
    }
  }

  // Look up previous amount from clients table — via clients-api (P1.5).
  // P1.4.1 extension: get-amount accepts ?paypal_subscription_id= as alternative
  // to ?email= and returns { monthly_amount, previous_monthly_amount, ... }.
  try {
    const lookup = await callClientsApi(
      env,
      `/internal/clients/get-amount?paypal_subscription_id=${encodeURIComponent(subscriptionId)}`,
      { method: "GET" }
    );
    const data = lookup?.data || {};
    oldAmount = data.monthly_amount || 0;
  } catch (e) {
    // If lookup fails (404/500), proceed with oldAmount=0 — the plan-change
    // branch below requires both > 0, so this naturally falls through to
    // upsert (which is idempotent). Log loudly for monitoring.
    console.log(`[paypal-webhook] get-amount lookup failed for sub=${subscriptionId}: ${e.message}`);
  }

  console.log(`[paypal-webhook] SUBSCRIPTION.UPDATED: sub=${subscriptionId}, old=${oldAmount}, new=${newAmount}`);

  // Detect plan change (amount differs)
  if (newAmount > 0 && oldAmount > 0 && newAmount !== oldAmount) {
    // Store previous amount for audit trail — via clients-api (P1.5).
    // update-amount endpoint handles previous_monthly_amount, monthly_amount,
    // plan_changed_at, last_active_at atomically.
    const now = new Date().toISOString();
    await callClientsApi(env, "/internal/clients/update-amount", {
      method: "POST",
      body: {
        paypal_subscription_id: subscriptionId,
        new_amount: newAmount,
        old_amount: oldAmount,
      },
    });

    // Trigger commission recalculation via Service Binding to referrals-api
    // (if subscription has referral attribution)
    try {
      if (env.REFERRALS_API) {
        const recalcRequest = new Request("https://referrals-api/internal/recalc-subscription", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            subscription_id: subscriptionId,
            old_amount: oldAmount,
            new_amount: newAmount,
            changed_at: now,
          }),
        });

        const recalcResponse = await env.REFERRALS_API.fetch(recalcRequest);
        if (!recalcResponse.ok) {
          const error = await recalcResponse.text();
          console.log(`[paypal-webhook] Commission recalc warning: ${error}`);
        } else {
          const result = await recalcResponse.json();
          console.log(`[paypal-webhook] Commission recalc triggered: ${JSON.stringify(result)}`);
        }
      }
    } catch (error) {
      console.error(`[paypal-webhook] Service binding error (recalc): ${error.message}`);
      // Don't fail the webhook if recalc fails — can be fixed manually
    }

    return { action: "plan_changed", subscriptionId, oldAmount, newAmount };
  }

  // No amount change, just update metadata
  const tier = resolveTier(planName, newAmount || oldAmount);
  await upsertClient(env, {
    email: null, // Keep existing
    name: null,
    tier,
    monthlyAmount: newAmount || oldAmount,
    subscriptionId,
  });

  return { action: "subscription_updated", subscriptionId, tier };
}

// ---------------------------------------------------------------------------
// Main router
// ---------------------------------------------------------------------------

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method;
    const path = url.pathname;

    // CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }

    // Health check
    if (method === "GET" && (path === "/health" || path === "/paypal/webhook/health")) {
      return Response.json({
        status: "ok",
        worker: "paypal-webhook",
        timestamp: new Date().toISOString(),
      });
    }

    // PayPal webhook endpoint
    if (method === "POST" && (path === "/paypal/webhook" || path === "/")) {
      return handleWebhook(request, env, ctx);
    }

    return Response.json({ error: "Not found" }, { status: 404 });
  },
};

async function handleWebhook(request, env, ctx) {
  // Store ctx in env for use in handlers
  env.ctx = ctx;

  let body;
  try {
    body = await request.json();
  } catch (e) {
    console.log(`[paypal-webhook] Invalid JSON body: ${e.message}`);
    return Response.json({ status: "error", message: "Invalid JSON" }, { status: 400 });
  }

  const eventType = body.event_type || "UNKNOWN";
  const transmissionId = request.headers.get("paypal-transmission-id") ||
                         request.headers.get("PAYPAL-TRANSMISSION-ID") ||
                         body.id || "";

  console.log(`[paypal-webhook] Received: event=${eventType}, transmission_id=${transmissionId}, id=${body.id}`);

  // Verify webhook signature
  if (!await verifyWebhook(request, env, body)) {
    console.log("[paypal-webhook] Webhook signature verification failed");
    return Response.json({ status: "rejected", reason: "invalid_signature" }, { status: 401 });
  }

  // Idempotency check
  if (await isDuplicate(env, transmissionId)) {
    return Response.json({ status: "duplicate_skipped", transmission_id: transmissionId });
  }

  // Record transmission immediately (optimistic lock)
  await recordTransmission(env, transmissionId, eventType, "processing");

  const resource = body.resource || {};
  let result;

  try {
    switch (eventType) {
      case "BILLING.SUBSCRIPTION.ACTIVATED":
        result = await handleSubscriptionActivated(env, resource);
        break;

      case "BILLING.SUBSCRIPTION.CANCELLED":
        result = await handleSubscriptionCancelled(env, resource);
        break;

      case "BILLING.SUBSCRIPTION.SUSPENDED":
        result = await handleSubscriptionSuspended(env, resource);
        break;

      case "BILLING.SUBSCRIPTION.RE-ACTIVATED":
        result = await handleSubscriptionReactivated(env, resource);
        break;

      case "BILLING.SUBSCRIPTION.UPDATED":
        result = await handleSubscriptionUpdated(env, resource);
        break;

      case "PAYMENT.SALE.COMPLETED":
        result = await handlePaymentCompleted(env, resource);
        break;

      default:
        console.log(`[paypal-webhook] Unhandled event type: ${eventType}`);
        result = { action: "ignored", reason: `unhandled_event: ${eventType}` };
    }

    // Update transmission log to 'processed'
    await recordTransmission(env, transmissionId, eventType, "processed");

  } catch (e) {
    console.error(`[paypal-webhook] Error processing ${eventType}: ${e.message}`, e.stack);
    // Update transmission log to 'error'
    await recordTransmission(env, transmissionId, eventType, `error: ${e.message}`);
    // Still return 200 to PayPal to prevent infinite retries
    return Response.json({
      status: "error",
      event_type: eventType,
      message: e.message,
    });
  }

  return Response.json({
    status: "ok",
    event_type: eventType,
    result,
  });
}
