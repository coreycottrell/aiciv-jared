/**
 * POST /api/referral/commission — Record a 5% recurring commission payment.
 *
 * Called by purebrain_log_server when a payment is verified.
 * Requires bearer token authentication.
 *
 * Body: { payer_email, order_id, amount, tier }
 * D1 binding: REFERRAL_DB
 */
import { corsResponse, jsonResponse, checkPortalAuth, REFERRAL_COMMISSION_RATE } from './_shared.js';

export async function onRequestOptions(context) {
  return corsResponse(context.request);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const db = env.REFERRAL_DB;

  if (!checkPortalAuth(request, env)) {
    return jsonResponse({ error: 'unauthorized' }, 401, request);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'invalid json' }, 400, request);
  }

  const payerEmail = String(body.payer_email || '').trim().toLowerCase();
  const orderId = String(body.order_id || '').trim();
  let amount;
  try {
    amount = parseFloat(body.amount || 0);
  } catch {
    amount = 0;
  }
  const tier = String(body.tier || '').trim();

  if (!payerEmail || !payerEmail.includes('@')) {
    return jsonResponse({ error: 'missing valid payer_email' }, 400, request);
  }
  if (!orderId) {
    return jsonResponse({ error: 'missing order_id' }, 400, request);
  }
  if (amount <= 0) {
    return jsonResponse({ ok: true, skipped: 'zero amount, no commission' }, 200, request);
  }

  const now = new Date().toISOString();
  const commissionValue = Math.round(amount * REFERRAL_COMMISSION_RATE * 100) / 100;

  // Find completed referral for this payer
  const referral = await db
    .prepare(
      "SELECT id, referrer_id FROM referrals WHERE referred_email = ? COLLATE NOCASE AND status = 'completed' LIMIT 1"
    )
    .bind(payerEmail)
    .first();

  if (!referral) {
    return jsonResponse({ ok: true, skipped: 'payer not in referrals' }, 200, request);
  }

  // Prevent duplicate commission for same order_id
  const dupe = await db
    .prepare('SELECT id FROM commission_payments WHERE order_id = ?')
    .bind(orderId)
    .first();

  if (dupe) {
    return jsonResponse({ ok: true, skipped: 'duplicate order_id' }, 200, request);
  }

  // Record commission
  await db
    .prepare(
      `INSERT INTO commission_payments
       (referrer_id, referral_id, payer_email, order_id, payment_amount,
        commission_rate, commission_value, tier, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .bind(
      referral.referrer_id,
      referral.id,
      payerEmail,
      orderId,
      amount,
      REFERRAL_COMMISSION_RATE,
      commissionValue,
      tier,
      now
    )
    .run();

  // Also insert into rewards table for balance consistency
  await db
    .prepare(
      "INSERT INTO rewards (referrer_id, referral_id, reward_type, reward_value, issued_at) VALUES (?, ?, 'commission', ?, ?)"
    )
    .bind(referral.referrer_id, referral.id, commissionValue, now)
    .run();

  // Fetch referrer info
  const referrer = await db
    .prepare('SELECT user_name, user_email FROM referrers WHERE id = ?')
    .bind(referral.referrer_id)
    .first();

  console.log(
    `[referral] Commission recorded: $${commissionValue.toFixed(2)} for ${referrer?.user_email || 'unknown'} (order ${orderId})`
  );

  return jsonResponse(
    {
      ok: true,
      commission_value: commissionValue,
      referrer_email: referrer?.user_email || '',
      referrer_name: referrer?.user_name || '',
      payer_email: payerEmail,
      order_id: orderId,
      payment_amount: amount,
      tier,
    },
    200,
    request
  );
}
