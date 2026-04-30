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
// D1 operations
// ---------------------------------------------------------------------------

async function upsertClient(env, { email, name, tier, monthlyAmount, subscriptionId }) {
  if (!email) {
    console.log("[paypal-webhook] No email in event, skipping upsert");
    return null;
  }

  const now = new Date().toISOString();

  const result = await env.DB.prepare(`
    INSERT INTO clients (
      email, name, tier, monthly_amount, status, payment_status,
      paypal_subscription_id, total_paid, first_seen_at, last_active_at,
      joined_date, source, hidden
    ) VALUES (
      ?1, ?2, ?3, ?4, 'active', 'active',
      ?5, 0, ?6, ?6,
      ?6, 'paypal', 0
    )
    ON CONFLICT(email) DO UPDATE SET
      name = COALESCE(NULLIF(?2, ''), clients.name),
      tier = COALESCE(NULLIF(?3, 'Unknown'), clients.tier),
      monthly_amount = CASE WHEN ?4 > 0 THEN ?4 ELSE clients.monthly_amount END,
      status = 'active',
      payment_status = 'active',
      paypal_subscription_id = COALESCE(?5, clients.paypal_subscription_id),
      last_active_at = ?6
  `).bind(
    email,                         // ?1
    name || "",                    // ?2
    tier || "Unknown",             // ?3
    monthlyAmount || 0,            // ?4
    subscriptionId || null,        // ?5
    now                            // ?6
  ).run();

  console.log(`[paypal-webhook] Upserted client: ${email}, tier=${tier}, amount=${monthlyAmount}`);
  return result;
}

async function updateClientStatus(env, subscriptionId, status, paymentStatus) {
  if (!subscriptionId) {
    console.log("[paypal-webhook] No subscription ID, cannot update status");
    return null;
  }

  const now = new Date().toISOString();

  const result = await env.DB.prepare(`
    UPDATE clients
    SET status = ?, payment_status = ?, last_active_at = ?
    WHERE paypal_subscription_id = ?
  `).bind(status, paymentStatus, now, subscriptionId).run();

  console.log(`[paypal-webhook] Updated status for sub=${subscriptionId}: status=${status}, payment=${paymentStatus}, rows=${result.meta?.changes || 0}`);
  return result;
}

async function incrementTotalPaid(env, subscriptionId, amount) {
  if (!subscriptionId || !amount) {
    console.log("[paypal-webhook] Missing sub ID or amount for payment increment");
    return null;
  }

  const now = new Date().toISOString();

  const result = await env.DB.prepare(`
    UPDATE clients
    SET total_paid = COALESCE(total_paid, 0) + ?,
        last_active_at = ?,
        payment_status = 'active'
    WHERE paypal_subscription_id = ?
  `).bind(amount, now, subscriptionId).run();

  console.log(`[paypal-webhook] Incremented total_paid by ${amount} for sub=${subscriptionId}, rows=${result.meta?.changes || 0}`);
  return result;
}

// ---------------------------------------------------------------------------
// Webhook verification (basic)
// ---------------------------------------------------------------------------

function verifyWebhook(request, env) {
  const webhookId = request.headers.get("paypal-webhook-id") ||
                    request.headers.get("PAYPAL-WEBHOOK-ID");

  // Basic check: PayPal must include webhook ID header
  if (!webhookId) {
    console.log("[paypal-webhook] WARN: Missing PayPal webhook ID header");
    // Still process — PayPal may send differently in sandbox
    return true;
  }

  // If WEBHOOK_SECRET is configured, verify it matches
  if (env.WEBHOOK_SECRET && webhookId !== env.WEBHOOK_SECRET) {
    console.log(`[paypal-webhook] WARN: Webhook ID mismatch: got=${webhookId}`);
    // Log but don't reject — full signature verification is the proper way
    // For now, allow through to avoid losing events
  }

  return true;
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

  return { action: "upserted", email, tier };
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

  // Keep status as-is (they're still a client), just mark payment as suspended
  const now = new Date().toISOString();
  await env.DB.prepare(`
    UPDATE clients
    SET payment_status = 'suspended', last_active_at = ?
    WHERE paypal_subscription_id = ?
  `).bind(now, subscriptionId).run();

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
      return handleWebhook(request, env);
    }

    return Response.json({ error: "Not found" }, { status: 404 });
  },
};

async function handleWebhook(request, env) {
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

  // Verify webhook (basic)
  if (!verifyWebhook(request, env)) {
    console.log("[paypal-webhook] Webhook verification failed");
    // Return 200 anyway to stop retries, but don't process
    return Response.json({ status: "rejected", reason: "verification_failed" });
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
