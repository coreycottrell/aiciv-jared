/**
 * POST /api/referral/track — Log a referral link click.
 *
 * Body: { referral_code }
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  isRateLimited,
  getClientIP,
  hashIP,
  TRACK_MAX_PER_WINDOW,
  TRACK_WINDOW_SECS,
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

  const code = String(body.referral_code || '').trim().toUpperCase();
  if (!code) {
    return jsonResponse({ error: 'missing referral_code' }, 400, request);
  }

  // Hash IP for privacy
  const clientIP = getClientIP(request);
  const ipHash = await hashIP(clientIP);

  // Rate limit click tracking
  const limited = await isRateLimited(db, `track:${ipHash}`, TRACK_MAX_PER_WINDOW, TRACK_WINDOW_SECS);
  if (limited) {
    return jsonResponse({ error: 'rate limited' }, 429, request);
  }

  // Verify code exists
  const referrer = await db
    .prepare('SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE')
    .bind(code)
    .first();

  if (!referrer) {
    return jsonResponse({ error: 'invalid referral code' }, 404, request);
  }

  const now = new Date().toISOString();
  await db
    .prepare('INSERT INTO referral_clicks (referral_code, ip_hash, clicked_at) VALUES (?, ?, ?)')
    .bind(code, ipHash, now)
    .run();

  return jsonResponse({ ok: true }, 200, request);
}
