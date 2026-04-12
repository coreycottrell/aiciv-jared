/**
 * POST /api/referral/payout-request — User requests a payout.
 *
 * Body: { referral_code, paypal_email, amount, session_token? }
 * Auth: portal bearer OR valid affiliate session
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  checkPortalAuth,
  verifyAffiliateSession,
  getSessionToken,
  PAYOUT_MIN_AMOUNT,
  PAYOUT_COOLDOWN_DAYS,
  PAYOUT_AUTO_APPROVE_LIMIT,
} from './_shared.js';

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

  const portalAuthed = checkPortalAuth(request, env);
  let sessionCode = null;

  if (!portalAuthed) {
    const sessionToken = getSessionToken(request, body);
    sessionCode = await verifyAffiliateSession(db, sessionToken);
    if (!sessionCode) {
      return jsonResponse({ error: 'authentication required' }, 401, request);
    }
  }

  const paypalEmail = String(body.paypal_email || '').trim().toLowerCase();
  const referralCode = String(body.referral_code || '').trim();
  let amount;
  try {
    amount = parseFloat(body.amount || 0);
  } catch {
    return jsonResponse({ error: 'invalid amount' }, 400, request);
  }

  if (!paypalEmail || !paypalEmail.includes('@') || !paypalEmail.split('@').pop().includes('.')) {
    return jsonResponse({ error: 'invalid paypal_email' }, 400, request);
  }
  if (!referralCode) {
    return jsonResponse({ error: 'missing referral_code' }, 400, request);
  }

  // IDOR fix: affiliate sessions can only request payouts for their own code
  if (!portalAuthed && sessionCode && sessionCode.toUpperCase() !== referralCode.toUpperCase()) {
    return jsonResponse({ error: 'access denied' }, 403, request);
  }

  if (amount < PAYOUT_MIN_AMOUNT) {
    return jsonResponse({ error: `minimum payout is $${PAYOUT_MIN_AMOUNT}` }, 400, request);
  }

  const nowTs = Math.floor(Date.now() / 1000);
  const cooldownSecs = PAYOUT_COOLDOWN_DAYS * 86400;

  // Check for existing pending payout within cooldown
  const pendingPayout = await db
    .prepare(
      "SELECT created_at_ts FROM payout_requests WHERE referral_code = ? AND status IN ('pending', 'processing') ORDER BY created_at_ts DESC LIMIT 1"
    )
    .bind(referralCode)
    .first();

  if (pendingPayout && (nowTs - pendingPayout.created_at_ts) < cooldownSecs) {
    const daysLeft = Math.ceil((cooldownSecs - (nowTs - pendingPayout.created_at_ts)) / 86400);
    return jsonResponse({ error: `payout already requested. Please wait ${daysLeft} more day(s).` }, 429, request);
  }

  // Check balance
  const balanceRow = await db
    .prepare(
      `SELECT COALESCE(SUM(rw.reward_value), 0) as total
       FROM rewards rw
       JOIN referrers r ON r.id = rw.referrer_id
       WHERE r.referral_code = ? COLLATE NOCASE`
    )
    .bind(referralCode)
    .first();

  const actualEarnings = balanceRow ? parseFloat(balanceRow.total) : 0;

  if (amount > actualEarnings) {
    return jsonResponse(
      { error: `requested amount $${amount.toFixed(2)} exceeds available balance $${actualEarnings.toFixed(2)}` },
      400,
      request
    );
  }

  const requestId = `payout-${referralCode}-${nowTs}`;
  const now = new Date().toISOString();

  // Store payout request in D1
  await db
    .prepare(
      `INSERT INTO payout_requests (request_id, referral_code, paypal_email, amount, status, created_at, created_at_ts, notes)
       VALUES (?, ?, ?, ?, 'pending', ?, ?, '')`
    )
    .bind(requestId, referralCode, paypalEmail, Math.round(amount * 100) / 100, now, nowTs)
    .run();

  // For now, all payouts are manual (no PayPal API in Workers).
  // The admin will be notified via logs and can approve manually.
  const message =
    amount > PAYOUT_AUTO_APPROVE_LIMIT
      ? 'Payout request submitted. We will process within 2 business days.'
      : 'Payout request submitted. Processing will begin shortly.';

  console.log(
    `[referral] PAYOUT REQUEST: ${referralCode} requesting $${amount.toFixed(2)} to ${paypalEmail} (request: ${requestId})`
  );

  return jsonResponse(
    {
      ok: true,
      request_id: requestId,
      message,
      amount: Math.round(amount * 100) / 100,
      paypal_email: paypalEmail,
    },
    200,
    request
  );
}
