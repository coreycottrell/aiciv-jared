/**
 * POST /api/referral/complete — Mark a referral as completed and record it.
 *
 * This endpoint is intentionally PUBLIC (no auth required).
 * Called from browser JS on payment pages after PayPal payment.
 * The referral_code itself acts as the credential.
 *
 * Body: { referral_code, referred_email, referred_name?, order_id? }
 * D1 binding: REFERRAL_DB
 */
import { corsResponse, jsonResponse } from './_shared.js';

export async function onRequestOptions(context) {
  return corsResponse(context.request);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const db = env.REFERRAL_DB;

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'invalid json' }, 400, request);
  }

  let referralCode = String(body.referral_code || '').trim().toUpperCase();
  let referredEmail = String(body.referred_email || '').trim().toLowerCase();
  const referredName = String(body.referred_name || '').trim();
  const orderId = String(body.order_id || '').trim();

  if (!referralCode) {
    return jsonResponse({ error: 'missing referral_code' }, 400, request);
  }

  // referred_email is optional for subscription payments where PayPal doesn't
  // provide payer email. Use placeholder derived from order_id.
  if (!referredEmail || !referredEmail.includes('@')) {
    if (orderId) {
      referredEmail = `paypal_${orderId.toLowerCase()}@pending`;
    } else {
      return jsonResponse({ error: 'invalid referred_email' }, 400, request);
    }
  }

  const now = new Date().toISOString();

  // Verify referral code
  const referrer = await db
    .prepare('SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE')
    .bind(referralCode)
    .first();

  if (!referrer) {
    return jsonResponse({ error: 'invalid referral code' }, 404, request);
  }

  const referrerId = referrer.id;

  // Single-referrer enforcement: remove existing completed referrals for this
  // email under DIFFERENT referrers (skip for placeholder emails)
  if (!referredEmail.includes('@pending')) {
    await db
      .prepare(
        "DELETE FROM referrals WHERE referred_email = ? COLLATE NOCASE AND referrer_id != ?"
      )
      .bind(referredEmail, referrerId)
      .run();
  }

  // Check for existing referral under this referrer
  let existing = null;
  if (!referredEmail.includes('@pending')) {
    existing = await db
      .prepare(
        'SELECT id, status FROM referrals WHERE referrer_id = ? AND referred_email = ? COLLATE NOCASE'
      )
      .bind(referrerId, referredEmail)
      .first();
  }

  if (existing) {
    if (existing.status === 'completed') {
      return jsonResponse({ ok: true, message: 'already completed' }, 200, request);
    }
    // Update existing pending row
    await db
      .prepare("UPDATE referrals SET status = 'completed', completed_at = ?, referred_name = ? WHERE id = ?")
      .bind(now, referredName || '', existing.id)
      .run();
  } else {
    await db
      .prepare(
        "INSERT INTO referrals (referrer_id, referred_email, referred_name, status, created_at, completed_at) VALUES (?, ?, ?, 'completed', ?, ?)"
      )
      .bind(referrerId, referredEmail, referredName, now, now)
      .run();
  }

  console.log(`[referral] complete: ${referralCode} -> ${referredEmail}`);

  return jsonResponse(
    { ok: true, message: 'Referral recorded. You will earn 5% of every payment this member makes.' },
    200,
    request
  );
}
