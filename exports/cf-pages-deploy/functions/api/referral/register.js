/**
 * POST /api/referral/register — Register as a referrer, get unique code back.
 *
 * Body: { name, email, password?, paypal_email? }
 * D1 binding: REFERRAL_DB
 */
import {
  corsResponse,
  jsonResponse,
  checkPortalAuth,
  hashPassword,
  generateUniqueCode,
  referralLink,
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

  const name = String(body.name || '').trim();
  const email = String(body.email || '').trim().toLowerCase();
  const password = String(body.password || '').trim();
  const paypalEmail = String(body.paypal_email || '').trim();

  if (!email || !email.includes('@') || !email.split('@').pop().includes('.')) {
    return jsonResponse({ error: 'invalid email' }, 400, request);
  }

  // Auto-generate password if not provided
  let pw = password;
  if (!pw || pw.length < 6) {
    const arr = new Uint8Array(16);
    crypto.getRandomValues(arr);
    pw = Array.from(arr)
      .map((b) => b.toString(36))
      .join('')
      .substring(0, 20);
  }

  const pwHash = await hashPassword(pw);

  // Check if already registered
  const existing = await db
    .prepare('SELECT id, referral_code FROM referrers WHERE user_email = ? COLLATE NOCASE')
    .bind(email)
    .first();

  if (existing) {
    return jsonResponse(
      {
        ok: true,
        referral_code: existing.referral_code,
        referral_link: referralLink(existing.referral_code),
        existing: true,
        message: 'You are already registered. Here is your existing referral link.',
      },
      200,
      request
    );
  }

  const code = await generateUniqueCode(db);
  const now = new Date().toISOString();

  await db
    .prepare(
      'INSERT INTO referrers (user_name, user_email, referral_code, password_hash, paypal_email, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    )
    .bind(name, email, code, pwHash, paypalEmail, now)
    .run();

  return jsonResponse(
    {
      ok: true,
      referral_code: code,
      referral_link: referralLink(code),
      existing: false,
      message: 'Registration successful!',
    },
    200,
    request
  );
}
