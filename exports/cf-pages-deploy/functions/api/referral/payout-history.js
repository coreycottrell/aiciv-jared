/**
 * GET /api/referral/payout-history?referral_code=XXX&session=TOKEN
 *
 * Auth: portal bearer OR affiliate session
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  checkPortalAuth,
  verifyAffiliateSession,
  PAYOUT_COOLDOWN_DAYS,
} from './_shared.js';

export async function onRequestOptions(context) {
  return corsResponse(context.request);
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const db = env.REFERRAL_DB;
  const url = new URL(request.url);

  const portalAuthed = checkPortalAuth(request, env);
  let sessionCode = null;

  if (!portalAuthed) {
    const sessionToken = (
      url.searchParams.get('session') ||
      request.headers.get('X-Affiliate-Session') ||
      ''
    ).trim();
    sessionCode = await verifyAffiliateSession(db, sessionToken);
    if (!sessionCode) {
      return jsonResponse({ error: 'authentication required' }, 401, request);
    }
  }

  const referralCode = (url.searchParams.get('referral_code') || '').trim();
  if (!referralCode) {
    return jsonResponse({ error: 'missing referral_code' }, 400, request);
  }

  // IDOR fix: affiliate sessions can only view their own payout history
  if (!portalAuthed && sessionCode && sessionCode.toUpperCase() !== referralCode.toUpperCase()) {
    return jsonResponse({ error: 'access denied' }, 403, request);
  }

  // Fetch payout requests from D1
  const result = await db
    .prepare(
      'SELECT * FROM payout_requests WHERE referral_code = ? ORDER BY created_at_ts DESC'
    )
    .bind(referralCode)
    .all();

  const requests = (result.results || []).map((r) => ({
    request_id: r.request_id,
    referral_code: r.referral_code,
    paypal_email: r.paypal_email,
    amount: r.amount,
    status: r.status,
    created_at: r.created_at,
    paid_at: r.paid_at || null,
    notes: r.notes || '',
  }));

  const nowTs = Math.floor(Date.now() / 1000);
  const cooldownSecs = PAYOUT_COOLDOWN_DAYS * 86400;
  let hasPending = false;
  let daysUntilEligible = 0;

  for (const req of requests) {
    if (req.status === 'pending' || req.status === 'processing') {
      hasPending = true;
      // Find the row with created_at_ts
      const original = (result.results || []).find((r) => r.request_id === req.request_id);
      if (original) {
        const elapsed = nowTs - original.created_at_ts;
        if (elapsed < cooldownSecs) {
          daysUntilEligible = Math.ceil((cooldownSecs - elapsed) / 86400);
        }
      }
      break;
    }
  }

  return jsonResponse(
    {
      requests,
      has_pending: hasPending,
      days_until_eligible: daysUntilEligible,
      cooldown_days: PAYOUT_COOLDOWN_DAYS,
    },
    200,
    request
  );
}
