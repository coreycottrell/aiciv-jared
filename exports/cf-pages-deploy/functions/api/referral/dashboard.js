/**
 * GET /api/referral/dashboard?code=PB-XXXX — Referrer stats and history.
 *
 * Auth: portal bearer, affiliate session token, or password query param.
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  checkPortalAuth,
  verifyAffiliateSession,
  verifyPassword,
  referralLink,
  REFERRAL_COMMISSION_RATE,
} from './_shared.js';

export async function onRequestOptions(context) {
  return corsResponse(context.request);
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const db = env.REFERRAL_DB;
  const url = new URL(request.url);

  const code = (url.searchParams.get('code') || '').trim().toUpperCase();
  const email = (url.searchParams.get('email') || '').trim().toLowerCase();
  const passwordParam = (url.searchParams.get('password') || '').trim();

  const portalAuthed = checkPortalAuth(request, env);

  if (!code && !email) {
    return jsonResponse({ error: 'missing code or email' }, 400, request);
  }

  // Look up referrer
  let referrer;
  if (code) {
    referrer = await db
      .prepare('SELECT * FROM referrers WHERE referral_code = ? COLLATE NOCASE')
      .bind(code)
      .first();
  } else {
    referrer = await db
      .prepare('SELECT * FROM referrers WHERE user_email = ? COLLATE NOCASE')
      .bind(email)
      .first();
  }

  if (!referrer) {
    return jsonResponse({ error: 'referrer not found' }, 404, request);
  }

  // Auth check
  if (!portalAuthed) {
    const sessionToken = (
      url.searchParams.get('session') ||
      request.headers.get('X-Affiliate-Session') ||
      ''
    ).trim();

    const sessionCode = await verifyAffiliateSession(db, sessionToken);

    if (sessionCode) {
      if (sessionCode.toUpperCase() !== referrer.referral_code.toUpperCase()) {
        return jsonResponse({ error: 'session token does not match this account' }, 403, request);
      }
    } else if (passwordParam) {
      if (!referrer.password_hash) {
        return jsonResponse(
          { error: 'no password set for this account. Please login via the referral portal to set one.' },
          401,
          request
        );
      }
      const validPw = await verifyPassword(passwordParam, referrer.password_hash);
      if (!validPw) {
        return jsonResponse({ error: 'incorrect password' }, 401, request);
      }
    } else {
      return jsonResponse({ error: 'authentication required. Please login at purebrain.ai/refer/' }, 401, request);
    }
  }

  const referrerId = referrer.id;
  const referralCode = referrer.referral_code;

  // Counts
  const totalReferrals = (
    await db
      .prepare('SELECT COUNT(*) as c FROM referrals WHERE referrer_id = ?')
      .bind(referrerId)
      .first()
  ).c;

  const completed = (
    await db
      .prepare("SELECT COUNT(*) as c FROM referrals WHERE referrer_id = ? AND status = 'completed'")
      .bind(referrerId)
      .first()
  ).c;

  const pending = (
    await db
      .prepare("SELECT COUNT(*) as c FROM referrals WHERE referrer_id = ? AND status = 'pending'")
      .bind(referrerId)
      .first()
  ).c;

  // Total earnings
  const earningsRow = await db
    .prepare('SELECT COALESCE(SUM(reward_value), 0) as total FROM rewards WHERE referrer_id = ?')
    .bind(referrerId)
    .first();
  const earnings = earningsRow ? parseFloat(earningsRow.total) : 0;

  // Click count
  const clicksRow = await db
    .prepare('SELECT COUNT(*) as c FROM referral_clicks WHERE referral_code = ? COLLATE NOCASE')
    .bind(referralCode)
    .first();
  const totalClicks = clicksRow ? clicksRow.c : 0;

  // Referral history with commissions
  const historyRows = await db
    .prepare(
      `SELECT r.referred_name, r.referred_email, r.status, r.created_at,
              COALESCE(SUM(cp.commission_value), 0) AS earnings,
              COUNT(cp.id) AS payment_count
       FROM referrals r
       LEFT JOIN commission_payments cp ON cp.referral_id = r.id
       WHERE r.referrer_id = ?
       GROUP BY r.id
       ORDER BY r.created_at DESC`
    )
    .bind(referrerId)
    .all();

  const history = (historyRows.results || []).map((row) => ({
    referred_name: row.referred_name,
    referred_email: row.referred_email,
    status: row.status,
    created_at: row.created_at,
    earnings: row.earnings,
    payment_count: row.payment_count,
  }));

  const rewardTiers = [
    { label: 'Commission Rate', reward: `${REFERRAL_COMMISSION_RATE * 100}% of every payment` },
    { label: 'Frequency', reward: 'Every month, for as long as they are a member' },
    { label: 'Awakened ($197/mo)', reward: '$9.85/month per referral' },
    { label: 'Partnered ($579/mo)', reward: '$28.95/month per referral' },
    { label: 'Unified ($1,089/mo)', reward: '$54.45/month per referral' },
    { label: 'Enterprise (Custom)', reward: '5% of custom monthly rate' },
  ];

  return jsonResponse(
    {
      referral_code: referralCode,
      referral_link: referralLink(referralCode),
      email: referrer.user_email,
      name: referrer.user_name,
      paypal_email: referrer.paypal_email,
      total_referrals: totalReferrals,
      completed,
      pending,
      earnings: Math.round(earnings * 100) / 100,
      total_clicks: totalClicks,
      history,
      reward_tiers: rewardTiers,
      commission_rate: REFERRAL_COMMISSION_RATE,
      commission_rate_pct: `${REFERRAL_COMMISSION_RATE * 100}%`,
      model: 'recurring',
    },
    200,
    request
  );
}
